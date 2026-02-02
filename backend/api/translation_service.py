from langdetect import detect, detect_langs
from deep_translator import GoogleTranslator
import xml.etree.ElementTree as ET
import re

class TranslationService:
    def detect_language(self, text):
        try:
            if not text or len(text.strip()) < 20:
                return 'en'

            langs = detect_langs(text)
            if not langs:
                return 'en'

            top = langs[0]
            top_lang = getattr(top, 'lang', None)
            top_prob = float(getattr(top, 'prob', 0.0) or 0.0)

            # If detection confidence is low, avoid surprise translations.
            if not top_lang or top_prob < 0.90:
                return 'en'

            # Extra safety: technical/ASCII-heavy text often gets misdetected.
            ascii_ratio = sum(1 for c in text if ord(c) < 128) / max(1, len(text))
            if ascii_ratio > 0.97 and top_lang != 'en':
                lower = text.lower()
                english_signals = ('start', 'end', 'process', 'user', 'yes', 'no', 'if', 'else', 'then', '->', '→')
                if any(s in lower for s in english_signals) and top_prob < 0.97:
                    return 'en'

            return top_lang
        except Exception as e:
            print(f"Language Detection Error: {e}")
            try:
                return detect(text)
            except Exception:
                return 'en'

    def translate_text(self, text, target='en'):
        if not text:
            return ""
        try:
            return GoogleTranslator(source='auto', target=target).translate(text)
        except Exception as e:
            print(f"Translation Error: {e}")
            return text

    def translate_bpmn_xml(self, xml_string, target_lang):
        try:
            # Register namespaces to prevent ns0 prefixes
            namespaces = {
                'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
                'bpmndi': 'http://www.omg.org/spec/BPMN/20100524/DI',
                'dc': 'http://www.omg.org/spec/DD/20100524/DC',
                'di': 'http://www.omg.org/spec/DD/20100524/DI'
            }
            
            # Since ElementTree is annoying with namespaces, we can try to use basic string parsing 
            # OR regex for robustness if structure is simple. 
            # BUT ElementTree is safer. Let's try to preserve prefixes.
            
            # Actually, standard ElementTree might mess up the prefixes (ns0). 
            # A Regex approach for 'name="Content"' might be safer for maintaining strictly the byte layout 
            # if we aren't using a robust XML serializer.
            # However, I'll use ElementTree but we need to ensure we don't break the XML.
            
            # Let's use a regex approach for "name" attributes to be non-intrusive to the rest of the XML structure.
            # Pattern: name="([^"]*)"
            
            def replace_match(match):
                original_text = match.group(1)
                if not original_text.strip():
                    return f'name="{original_text}"'
                
                translated = self.translate_text(original_text, target=target_lang)
                return f'name="{translated}"'

            # Regex to find name attributes. 
            # Warning: This is a bit naive if name contains escaped quotes, but standard BPMN usuall doesn't.
            new_xml = re.sub(r'name="([^"]*)"', replace_match, xml_string)
            return new_xml

        except Exception as e:
            print(f"XML Translation Error: {e}")
            return xml_string
