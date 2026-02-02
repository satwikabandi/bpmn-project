import re

class Parser:
    def __init__(self):
        self.process_graph = {
            "type": "process",
            "flow": []
        }
        self.stack = [] # To handle nested blocks like If/Else

    def parse(self, tokens):
        """
        Parses tokens into a Process Graph with friendly defaults.
        """
        # Root flow
        root = []
        # Stack stores tuples: (current_list, parent_gateway_node_or_None, branch_type)
        # branch_type: 'main', 'true', 'false'
        state_stack = [(root, None, 'main')]
        current_group = None
        
        # Helper to detect if a token is a start event
        def is_start_event(lower_text):
            start_patterns = [
                "start process", "start", "begins", "process starts", 
                "the process starts", "process begins", "workflow starts",
                "ప్రారంభం", "ప్రారంభమవుతుంది", "మొదలవుతుంది"  # Telugu
            ]
            # Check if starts with or contains start patterns
            for pattern in start_patterns:
                if lower_text.startswith(pattern) or pattern in lower_text:
                    return True
            # Check for pattern like "starts when", "starts with"
            if "starts when" in lower_text or "starts with" in lower_text or "begins when" in lower_text:
                return True
            return False
        
        # Helper to detect if a token is an end event
        def is_end_event(lower_text):
            end_patterns = [
                "end process", "end", "ends", "process ends", 
                "the process ends", "workflow ends",
                "ముగింపు", "ముగుస్తుంది", "అంతమవుతుంది"  # Telugu
            ]
            for pattern in end_patterns:
                if lower_text == pattern or lower_text.startswith(pattern + " ") or lower_text.endswith(pattern):
                    return True
            if "ends when" in lower_text or "ends with" in lower_text:
                return True
            return False
        
        # 1. IMPLICIT START
        # Check if "Start" exists anywhere in the top-level tokens
        has_start = any(is_start_event(t[1]) for t in tokens)
        if not has_start:
             root.append({"type": "start", "name": "Start", "group": None})

        for original, lower in tokens:
            current_list = state_stack[-1][0]
            
            # GROUP START
            if lower.startswith("group:"):
                # "Group: User Input"
                current_group = original.split(":", 1)[1].strip()
                continue
            
            # GROUP END
            elif lower.startswith("end group"):
                current_group = None
                continue

            # START (Explicit or sentence-based)
            # English: start process, start, "The process starts when..."
            # Telugu: ప్రారంభం (Prarambham), ...ప్రారంభమవుతుంది (...starts)
            if is_start_event(lower):
                root.append({"type": "start", "name": "Start", "group": current_group})

            # END
            # English: end process, end, "The process ends"
            # Telugu: ముగింపు (Mugimpu), ...ముగుస్తుంది (...ends)
            elif is_end_event(lower):
                current_list.append({"type": "end", "name": "End", "group": current_group})

            # 3. QUESTION => IMPLICIT GATEWAY
            # If line ends with '?', assume it's a gateway (Exclusive)
            elif original.endswith("?"):
                gateway = {
                    "type": "exclusive_gateway",
                    "condition": original,
                    "true_branch": [],
                    "false_branch": [],
                    "is_implicit": True,
                    "group": current_group
                }
                current_list.append(gateway)
                state_stack.append((gateway['true_branch'], gateway, 'implicit_wait'))

            # RE-WRITING THE LOOP BODY FOR CONDITIONAL LOGIC
            
            # IF (Explicit)
            # English: if ...
            elif lower.startswith("if ") or lower.startswith("ఒకవేళ"):
                 # Clean prefix for Name/Condition
                if lower.startswith("if "):
                    condition = original[3:].replace(":", "").strip()
                else:
                    condition = original.replace("ఒకవేళ", "", 1).replace(":", "").strip()
                    
                gateway = {
                    "type": "exclusive_gateway",
                    "condition": condition,
                    "true_branch": [],
                    "false_branch": [],
                    "group": current_group
                }
                current_list.append(gateway)
                state_stack.append((gateway["true_branch"], gateway, 'true'))

            # ELSE (Explicit)
            elif lower.startswith("else") or lower.startswith("లేకపోతే"):
                if len(state_stack) > 1 and state_stack[-1][2] == 'true':
                    _, gateway, _ = state_stack.pop()
                    state_stack.append((gateway["false_branch"], gateway, 'false'))

            # END IF (Explicit)
            elif lower.startswith("end if") or lower.startswith("షరతు ముగింపు"):
                if len(state_stack) > 1:
                     state_stack.pop()

            # IMPLICIT GATEWAY: Question '?' (Redundant check removed, handled above or needs better ordering)
            # The logic above handled '?' globally. Line 100 in view_file was "elif original.endswith('?')".
            # I will ensure consistent handling. Actually, lines 55-71 were the original place for '?'.
            # I should just update the places where nodes are created.

            # IMPLICIT BRANCH: - Yes / - No
            elif re.match(r'^\W*(yes|no)[\W]*', lower):
                  
                  # Parse direction
                  match = re.match(r'^\W*(yes|no)(.*)', lower)
                  direction_str = match.group(1) # yes or no
                  
                  # Regex to find content
                  full_match = re.match(r'^\W*(yes|no)[\W]*', original, flags=re.IGNORECASE)
                  content_clean = original[full_match.end():].strip()
                  
                  # Check if we are in an implicit context
                  if len(state_stack) > 1 and 'implicit' in state_stack[-1][2]:
                      # Retrieve Gateway
                      _, gateway, state_type = state_stack[-1]
                      
                      # Identify Branch Direction
                      is_true = "yes" in direction_str
                      
                      # Pop current implicit state to switch or update
                      state_stack.pop()
                      
                      # Select new branch list
                      new_list = gateway["true_branch"] if is_true else gateway["false_branch"]
                      state_stack.append((new_list, gateway, 'implicit_active'))
                      
                      # Add the content as a task immediately
                      if content_clean:
                           new_list.append({"type": "task", "name": content_clean, "group": current_group})
                  else:
                      # Orphan Yes/No? Treat as task.
                      current_list.append({"type": "task", "name": original, "group": current_group})
            
            # DEFAULT TASK (or Implicit Close)
            else:
                 # Check if we are inside an implicit branch and need to close it?
                 if len(state_stack) > 1 and state_stack[-1][2] == 'implicit_active':
                     # The user provided a line that doesn't start with Yes/No.
                     # This implies the implicit gateway is DONE.
                     # Pop the stack to return to parent flow.
                     state_stack.pop()
                     # Update `current_list` to be the parent list (now top of stack)
                     state_stack[-1][0].append({"type": "task", "name": original, "group": current_group})
                 elif len(state_stack) > 1 and state_stack[-1][2] == 'implicit_wait':
                     # We were waiting for Yes/No after '?', but got random text.
                     # Treat '?' as just a task? or close empty gateway?
                     # Let's assume the question was just a task and pop back.
                     # OR treat this as the next step.
                     state_stack.pop()
                     state_stack[-1][0].append({"type": "task", "name": original, "group": current_group})
                 else:
                     # Normal Task in normal flow
                     current_list.append({"type": "task", "name": original, "group": current_group})
        
        def has_any_end(flow_nodes):
            for n in flow_nodes or []:
                if not isinstance(n, dict):
                    continue
                if n.get("type") == "end":
                    return True
                if n.get("type") == "exclusive_gateway":
                    if has_any_end(n.get("true_branch")) or has_any_end(n.get("false_branch")):
                        return True
            return False

        # 2. IMPLICIT END
        # Only add a global implicit end if there is no end anywhere in the process graph.
        # This prevents duplicated End events when branches already end.
        if not has_any_end(root):
            root.append({"type": "end", "name": "End"})
        
        return {"type": "process", "flow": root}
