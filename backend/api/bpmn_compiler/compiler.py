from .tokenizer import Tokenizer
from .parser import Parser
from .arrow_parser import ArrowParser
from .builder import BPMNBuilder

class Compiler:
    def __init__(self):
        self.tokenizer = Tokenizer()
        self.parser = Parser()
        self.arrow_parser = ArrowParser()
        self.builder = BPMNBuilder()

    def compile(self, text):
        try:
            # Detect syntax type
            if '→' in text or '->' in text:
                # Arrow syntax detected
                # Normalize -> to →
                text = text.replace('->', '→')
                process_graph = self.arrow_parser.parse(text)
            else:
                # Original syntax (Group:, Start, etc.)
                tokens = self.tokenizer.tokenize(text)
                process_graph = self.parser.parse(tokens)
            
            xml = self.builder.build_xml(process_graph)
            return xml
        except Exception as e:
            print(f"Compilation Error: {e}")
            import traceback
            traceback.print_exc()
            return f"<!-- Error compiling BPMN: {e} -->"
