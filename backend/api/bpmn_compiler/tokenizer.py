import re

class Tokenizer:
    def __init__(self):
        pass

    def tokenize(self, text):
        """
        Converts raw text into a list of clean, significant lines.
        Handles checking for 'Sentence' structure if input is a single block.
        """
        # 1. Heuristic Parsing for Single-Line Inputs
        # If we see "Group:" or periods but few newlines, we force splits.
        processed_text = text
        
        # Inject newlines before structural keywords (Case Insensitive regex)
        # We use re.sub with lookahead/lookbehind patterns or just simple substitution
        
        # Split on sentences (Period + Space)
        processed_text = re.sub(r'\.\s+', '.\n', processed_text)
        
        # Split on Structural Keywords (force them to start new lines)
        keywords = ["Group:", "End Group", "Yes:", "No:", "Start Process", "End Process"]
        for kw in keywords:
            # Case insensitive replace
            pattern = re.compile(re.escape(kw), re.IGNORECASE)
            processed_text = pattern.sub(f'\n{kw}', processed_text)

        # 2. Standard Tokenization
        lines = processed_text.split('\n')
        tokens = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Normalize spaces
            line = ' '.join(line.split())
            
            # Clean up leading punctuation if any (like from the split leftovers)
            if line.startswith("."):
                line = line[1:].strip()

            if not line: continue
            
            # Lowercase for keyword matching (keywords will be handled by parser)
            # We keep original casing for display, but return a tuple (original, lower)
            tokens.append((line, line.lower()))
            
        return tokens
