from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .ml_service import MLService
from .rag_service import RAGService
from .bpmn_compiler.compiler import Compiler
import os

from .translation_service import TranslationService
from .gemini_service import GeminiService
from .groq_service import GroqService

class GenerateBPMNView(APIView):
    def post(self, request):
        text = request.data.get("text")
        use_rag = request.data.get("use_rag", False)
        force_english = request.data.get("force_english", False)
        mode = request.data.get("mode", "rule")
        
        if not text:
            return Response({"error": "Text is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        translator = TranslationService()
        
        # 1. Detect Language
        detected_lang = translator.detect_language(text)
        
        # 2. Prepare Input for Compiler (Translate to English if needed)
        input_for_compiler = text
        if detected_lang != 'en':
            input_for_compiler = translator.translate_text(text, target='en')

        # RAG Retrieval
        context = ""
        if use_rag:
            rag_service = RAGService()
            context = rag_service.retrieve_context(input_for_compiler)

        compiler = Compiler()
        ml_service = MLService()

        gemini_service = GeminiService()
        groq_service = GroqService()

        # Groq-first mode: try Groq once; if unavailable/fails, fall back to rule-based flow.
        if mode == "groq":
            groq_normalized = None
            groq_xml = None

            if getattr(groq_service, "api_key", None):
                try:
                    groq_normalized = groq_service.normalize_input(input_for_compiler)
                    groq_xml = compiler.compile(groq_normalized)
                except Exception as e:
                    print(f"Warning: Groq path failed, falling back to rule-based. Error: {e}")

            if groq_xml:
                accuracy = ml_service.calculate_accuracy(input_for_compiler, groq_xml)

                final_xml = groq_xml
                if detected_lang != 'en' and not force_english:
                    final_xml = translator.translate_bpmn_xml(groq_xml, target_lang=detected_lang)

                return Response({
                    "xml": final_xml,
                    "accuracy": accuracy,
                    "model": "Rule-Based Engine",
                    "engine": "groq",
                    "context_used": bool(context),
                    "detected_language": detected_lang,
                    "explanation": groq_normalized or input_for_compiler
                })

        candidates = []

        # Base candidate: raw (translated) input
        candidates.append({
            "engine": "rule",
            "normalized": input_for_compiler,
        })

        # Optional: Gemini normalization
        if mode in ("hybrid", "rule"):
            try:
                if gemini_service.client:
                    candidates.append({
                        "engine": "gemini",
                        "normalized": gemini_service.normalize_input(input_for_compiler),
                    })
            except Exception as e:
                print(f"Warning: Gemini Normalization failed, proceeding without it. Error: {e}")

        # Optional: Groq normalization
        if mode in ("hybrid",):
            try:
                normalized = groq_service.normalize_input(input_for_compiler)
                candidates.append({
                    "engine": "groq",
                    "normalized": normalized,
                })
            except Exception as e:
                print(f"Warning: Groq Normalization failed, proceeding without it. Error: {e}")

        # Select candidate(s) based on requested mode
        if mode == "rule":
            candidates = [c for c in candidates if c["engine"] in ("rule", "gemini")]
        elif mode == "hybrid":
            # keep all
            pass
        else:
            return Response({"error": "Invalid mode. Use rule|groq|hybrid."}, status=status.HTTP_400_BAD_REQUEST)

        best = None
        best_score = None
        best_bpmn_xml = None

        for c in candidates:
            try:
                bpmn_xml = compiler.compile(c["normalized"])
                score = ml_service.calculate_accuracy(input_for_compiler, bpmn_xml)
                if best_score is None or score > best_score:
                    best = c
                    best_score = score
                    best_bpmn_xml = bpmn_xml
            except Exception as e:
                print(f"Warning: Compilation failed for engine={c.get('engine')}. Error: {e}")

        if not best_bpmn_xml:
            return Response({"error": "Failed to generate BPMN"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        bpmn_xml = best_bpmn_xml
        selected_engine = best.get("engine") if best else "rule"
        selected_normalized = best.get("normalized") if best else input_for_compiler
        
        # 3. Handle Output Language
        final_xml = bpmn_xml
        
        # If the user spoke non-English AND did NOT explicitly ask for English output,
        # we translate the diagram labels back to their native language.
        if detected_lang != 'en' and not force_english:
            final_xml = translator.translate_bpmn_xml(bpmn_xml, target_lang=detected_lang)
            
        # Calculate Accuracy (Use English versions for comparison as the ML model is likely English trained?)
        # Or compare Translated Text vs Translated Diagram? 
        # Safest is to use the English pair for semantic check if the model is English-based (XLM-R is multilingual though).
        # Let's use the english pair for consistency.
        accuracy = best_score if best_score is not None else ml_service.calculate_accuracy(input_for_compiler, bpmn_xml)
        
        return Response({
            "xml": final_xml,
            "accuracy": accuracy,
            "model": "Rule-Based Engine",
            "engine": selected_engine,
            "context_used": bool(context),
            "detected_language": detected_lang,
            "explanation": selected_normalized
        })

class UploadFileView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.data['file']
        
        # Save temp file
        if not os.path.exists('uploads'):
            os.makedirs('uploads')
        
        file_path = os.path.join('uploads', file_obj.name)
        with open(file_path, 'wb+') as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)
        
        # Extract text content from the file
        extracted_text = ""
        try:
            if file_path.lower().endswith('.pdf'):
                # Use PyPDFLoader for PDF files
                from langchain_community.document_loaders import PyPDFLoader
                loader = PyPDFLoader(file_path)
                documents = loader.load()
                extracted_text = "\n".join([doc.page_content for doc in documents])
            elif file_path.lower().endswith('.txt'):
                # Plain text files
                with open(file_path, 'r', encoding='utf-8') as f:
                    extracted_text = f.read()
            elif file_path.lower().endswith(('.doc', '.docx')):
                # Word documents (requires python-docx)
                try:
                    import docx
                    doc = docx.Document(file_path)
                    extracted_text = "\n".join([para.text for para in doc.paragraphs])
                except ImportError:
                    extracted_text = "Word document support requires python-docx. Please install it."
        except Exception as e:
            print(f"Error extracting text: {e}")
            extracted_text = ""
        
        # Process RAG for context retrieval
        rag_service = RAGService()
        num_chunks = rag_service.process_file(file_path)
        
        return Response({
            "message": "File processed successfully", 
            "chunks": num_chunks,
            "extracted_text": extracted_text.strip()
        }, status=status.HTTP_201_CREATED)
