from sentence_transformers import SentenceTransformer, util
import torch

class MLService:
    def __init__(self):
        # Using a lightweight XLM-R model for multilingual embeddings
        self.model_name = 'sentence-transformers/paraphrase-xlm-r-multilingual-v1'
        self.model = None

    def load_model(self):
        if not self.model:
            print("Loading ML Model...")
            self.model = SentenceTransformer(self.model_name)
            print("ML Model Loaded.")

    def calculate_accuracy(self, input_text, generated_bpmn):
        """
        Calculates a semantic similarity score between the input text 
        and the content extracted from the BPMN XML.
        """
        self.load_model()
        
        # Extract meaningful text from BPMN (Labels, Names)
        bpmn_text = self._extract_text_from_bpmn(generated_bpmn)
        
        # Compute embeddings
        embeddings1 = self.model.encode(input_text, convert_to_tensor=True)
        embeddings2 = self.model.encode(bpmn_text, convert_to_tensor=True)
        
        # Compute cosine similarity
        cosine_scores = util.cos_sim(embeddings1, embeddings2)
        score = cosine_scores.item() * 100 # Convert to percentage
        
        return round(score, 2)

    def _extract_text_from_bpmn(self, bpmn_xml):
        """
        Simple extraction of 'name' attributes from BPMN XML 
        to get a textual representation of the diagram.
        """
        import re
        # Find all name="..." attributes
        matches = re.findall(r'name="([^"]+)"', bpmn_xml)
        return " ".join(matches)
