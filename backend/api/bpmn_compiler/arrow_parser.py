import re

class ArrowParser:
    """
    Parses arrow-based syntax: A → B → C? → yes D / no E
    """
    
    def __init__(self):
        self.node_counter = 0
    
    def parse(self, text):
        """
        Main parsing method.
        Returns a process graph compatible with existing Builder.
        """
        # Clean up the text
        text = text.strip()
        
        # Split into lines (each line is a separate flow or continuation)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Parse all lines into a single flow
        flow = []
        for line in lines:
            parsed_line = self._parse_line(line)
            if parsed_line:
                flow.extend(parsed_line)
        
        # Add implicit start if needed
        if flow and flow[0]["type"] != "start":
            flow.insert(0, {"type": "start", "name": "Start", "group": None})
        
        return {"flow": flow}
    
    def _parse_line(self, line):
        """
        Parse a single line of arrow syntax.
        Returns a list of nodes.
        """
        # Check for parallel flows first
        if '+' in line and 'parallel' in line.lower():
            return self._parse_parallel(line)
        
        # Split by arrows
        parts = [p.strip() for p in line.split('→') if p.strip()]
        
        if not parts:
            return []
        
        nodes = []
        i = 0
        
        while i < len(parts):
            part = parts[i]
            
            # Check if this part contains a decision (?)
            if '?' in part:
                gateway_node = self._parse_decision(part, parts, i)
                if gateway_node:
                    nodes.append(gateway_node)
                    # Decision consumes the next part (branches)
                    i += 2  # Skip the question and the branch part
                else:
                    i += 1
            else:
                # Regular task
                task_node = {
                    "type": "task",
                    "name": part,
                    "group": None
                }
                nodes.append(task_node)
                i += 1
        
        return nodes
    
    def _parse_decision(self, question_part, all_parts, current_index):
        """
        Parse a decision point: 'credentials valid? → yes dashboard / no retry'
        """
        # Extract the question text (before ?)
        question_text = question_part.split('?')[0].strip()
        
        # Get the next part which should contain branches
        if current_index + 1 >= len(all_parts):
            # No branches specified, create empty gateway
            return {
                "type": "exclusive_gateway",
                "condition": question_text,
                "true_branch": [],
                "false_branch": [],
                "group": None
            }
        
        branch_part = all_parts[current_index + 1]
        
        # Parse branches: "yes dashboard / no retry"
        yes_branch, no_branch = self._parse_branches(branch_part)
        
        return {
            "type": "exclusive_gateway",
            "condition": question_text,
            "true_branch": yes_branch,
            "false_branch": no_branch,
            "group": None
        }
    
    def _parse_branches(self, branch_text):
        """
        Parse branch text: 'yes dashboard / no retry'
        Returns: (yes_nodes, no_nodes)
        """
        yes_nodes = []
        no_nodes = []
        
        # Split by / to separate yes and no branches
        if '/' in branch_text:
            parts = branch_text.split('/')
            
            for part in parts:
                part = part.strip()
                
                if part.lower().startswith('yes'):
                    # Extract text after 'yes'
                    yes_text = re.sub(r'^yes\s*', '', part, flags=re.IGNORECASE).strip()
                    if yes_text:
                        # Check if this contains another decision
                        if '?' in yes_text:
                            # Nested decision - parse recursively
                            nested_parts = [p.strip() for p in yes_text.split('→')]
                            yes_nodes.extend(self._parse_line(yes_text))
                        else:
                            yes_nodes.append({
                                "type": "task",
                                "name": yes_text,
                                "group": None
                            })
                
                elif part.lower().startswith('no'):
                    # Extract text after 'no'
                    no_text = re.sub(r'^no\s*', '', part, flags=re.IGNORECASE).strip()
                    if no_text:
                        # Check if this contains another decision
                        if '?' in no_text:
                            # Nested decision
                            no_nodes.extend(self._parse_line(no_text))
                        else:
                            no_nodes.append({
                                "type": "task",
                                "name": no_text,
                                "group": None
                            })
        else:
            # No explicit branches, might be just "yes X" or "no X"
            if branch_text.lower().startswith('yes'):
                yes_text = re.sub(r'^yes\s*', '', branch_text, flags=re.IGNORECASE).strip()
                if yes_text:
                    yes_nodes.append({"type": "task", "name": yes_text, "group": None})
            elif branch_text.lower().startswith('no'):
                no_text = re.sub(r'^no\s*', '', branch_text, flags=re.IGNORECASE).strip()
                if no_text:
                    no_nodes.append({"type": "task", "name": no_text, "group": None})
        
        return yes_nodes, no_nodes
    
    def _parse_parallel(self, line):
        """
        Parse parallel flows: 'KYC + credit check + income checks parallel'
        """
        # Remove 'parallel' keyword
        line = re.sub(r'\bparallel\b', '', line, flags=re.IGNORECASE).strip()
        
        # Split by +
        tasks = [t.strip() for t in line.split('+') if t.strip()]
        
        # Create task nodes for each
        nodes = []
        for task_text in tasks:
            # Remove arrows if any
            task_text = task_text.replace('→', '').strip()
            if task_text:
                nodes.append({
                    "type": "task",
                    "name": task_text,
                    "group": None
                })
        
        return nodes
