class BPMNBuilder:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.di_shapes = []
        self.di_edges = []
        
        # Counters
        self.id_counter = 1
        
        # Layout Config - IMPROVED DEFAULTS
        self.start_x = 180  # More initial padding
        self.start_y = 150
        
        # Minimum sizes
        self.min_task_width = 160
        self.min_task_height = 80
        self.event_size = 36
        self.gateway_size = 50
        
        # Spacing
        self.horizontal_gap = 120  # Space between nodes
        self.vertical_branch_gap = 220 # Space between gateway branches
        
        self.current_x = self.start_x
        self.current_y = self.start_y
        
        self.group_bounds = {} # Map[name] -> {min_x, min_y, max_x, max_y}

    def _wrap_text_and_get_size(self, text, min_width=160, min_height=80, shape_type="rect"):
        """
        Wraps text and calculates required dimensions.
        Returns: (wrapped_text, width, height)
        """
        if not text:
            return "", min_width, min_height
            
        # Approx metrics
        char_width_avg = 7.5
        line_height = 14
        padding_x = 20
        padding_y = 20
        
        # Determine max chars per line based on min_width
        # target_width = min_width - (padding_x * 2)
        # max_chars_per_line = int(target_width / char_width_avg)
        max_chars_per_line = 25 # Start with a reasonable default wrap point
        
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            # Check if adding word exceeds logical line length
            line_str = " ".join(current_line + [word])
            if len(line_str) <= max_chars_per_line:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                # If a single word is ridiculously long, it might force a wider box/overflow
                # but standard splitting is usually enough.
                
        if current_line: lines.append(" ".join(current_line))
        
        wrapped_text = "&#10;".join(lines)
        num_lines = max(1, len(lines))
        
        # Calculate Dimensions
        longest_line_chars = max([len(l) for l in lines]) if lines else 0
        
        # Width: Base + chars * avg_width
        calculated_width = int((longest_line_chars * char_width_avg) + (padding_x * 2))
        final_width = max(min_width, calculated_width)
        
        # Height: Base + lines * height
        calculated_height = int((num_lines * line_height) + (padding_y * 2))
        
        if shape_type == "rect":
            final_height = max(min_height, calculated_height)
            return wrapped_text, final_width, final_height
            
        elif shape_type == "diamond":
            # For diamonds, textual content inside is very limited.
            # We usually expanded slightly, but not too much or it looks weird.
            # If text is too long for diamond, BPMN best practice is an annotation, 
            # but here we'll just expand the diamond.
            # Diamond internal width is roughly width/2 at center.
            
            # Simple scaling: require more size for more lines
            size_factor = max(50, (longest_line_chars * 6) + 30) # Heuristic
            size_factor = max(size_factor, (num_lines * 18) + 30)
            
            # Cap realistic size for gateway
            final_size = min(120, size_factor) 
            final_size = max(50, final_size)
            
            return wrapped_text, int(final_size), int(final_size)
            
        return text, min_width, min_height

    def get_id(self, prefix):
        self.id_counter += 1
        return f"{prefix}_{self.id_counter}"

    def build_xml(self, process_graph):
        self.process_flow(process_graph["flow"], self.current_x, self.current_y)
        
        # Generate XML
        nodes_xml = "".join(self.nodes)
        edges_xml = "".join(self.edges)
        shapes_xml = "".join(self.di_shapes)
        edges_di_xml = "".join(self.di_edges)
        
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" id="Definitions_1" targetNamespace="http://bpmn.io/schema/bpmn">
  <bpmn:process id="Process_1" isExecutable="false">
    {nodes_xml}
    {edges_xml}
    
    <!-- Groups -->
    {self._generate_group_definitions()}
  </bpmn:process>
  
  <!-- Category Definitions -->
  {self._generate_category_definitions()}

  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_1">
      {shapes_xml}
      {edges_di_xml}
      {self._generate_group_shapes()}
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>"""

    def _generate_group_definitions(self):
        xml = ""
        for name in self.group_bounds.keys():
            safe_name = "".join([c for c in name if c.isalnum()])
            cat_val_id = f"CategoryValue_{safe_name}"
            grp_id = f"Group_{safe_name}"
            xml += f'<bpmn:group id="{grp_id}" categoryValueRef="{cat_val_id}" />'
        return xml

    def _generate_category_definitions(self):
        xml = ""
        for name in self.group_bounds.keys():
            safe_name = "".join([c for c in name if c.isalnum()])
            cat_id = f"Category_{safe_name}"
            cat_val_id = f"CategoryValue_{safe_name}"
            xml += f'<bpmn:category id="{cat_id}"><bpmn:categoryValue id="{cat_val_id}" value="{name}" /></bpmn:category>'
        return xml

    def _generate_group_shapes(self):
        xml = ""
        padding = 40 # Increased padding for groups
        for name, bounds in self.group_bounds.items():
            safe_name = "".join([c for c in name if c.isalnum()])
            grp_id = f"Group_{safe_name}"
            
            x = bounds['min_x'] - padding
            y = bounds['min_y'] - padding
            w = (bounds['max_x'] - bounds['min_x']) + (padding * 2)
            h = (bounds['max_y'] - bounds['min_y']) + (padding * 2)
            
            xml += f'<bpmndi:BPMNShape id="{grp_id}_di" bpmnElement="{grp_id}"><dc:Bounds x="{x}" y="{y}" width="{w}" height="{h}" /></bpmndi:BPMNShape>'
        return xml

    def process_flow(self, flow, x, y, incoming_endpoints=None):
        cx = x
        cy = y
        last_endpoints = incoming_endpoints if incoming_endpoints else []
        
        for i, node in enumerate(flow):
            node_type = node["type"]
            node_name = node.get("name", "")
            
            # --- START Event ---
            if node_type == "start":
                node_id = "StartEvent_" + self.get_id("S")
                # Start event is fixed size
                
                self.nodes.append(f'<bpmn:startEvent id="{node_id}" name="{node_name}"><bpmn:outgoing>Flow_{node_id}</bpmn:outgoing></bpmn:startEvent>')
                self.di_shapes.append(f'<bpmndi:BPMNShape id="{node_id}_di" bpmnElement="{node_id}"><dc:Bounds x="{cx}" y="{cy}" width="{self.event_size}" height="{self.event_size}" /></bpmndi:BPMNShape>')
                
                self._update_group_bounds(node.get("group"), cx, cy, self.event_size, self.event_size)
                
                last_endpoints = [{
                    'ref': node_id,
                    'x': cx + self.event_size,
                    'y': cy + self.event_size // 2
                }]
                
                # Dynamic horizontal gap + some extra for start event
                cx += 180 

            # --- TASK ---
            elif node_type == "task":
                node_id = self.get_id("Task")
                
                # Dynamic Size Logic
                wrapped_name, task_w, task_h = self._wrap_text_and_get_size(node_name, self.min_task_width, self.min_task_height, "rect")

                # Center the task vertically relative to the incoming flow line 'y'
                # The 'cy' passed is usually the top-left 'y' or center 'y'? 
                # To align centers: top_y = center_y - height/2
                # In this simpler builder, 'cy' acts as the top-left anchor. 
                # Let's keep 'cy' as top-left for simplicity but adjust spacing.
                
                if last_endpoints:
                    for ep in last_endpoints:
                        flow_id = self.get_id("Flow")
                        label = ep.get('label', "")
                        self.edges.append(f'<bpmn:sequenceFlow id="{flow_id}" sourceRef="{ep["ref"]}" targetRef="{node_id}" name="{label}" />')
                        
                        start_x = ep['x']
                        start_y = ep['y']
                        target_x = cx
                        target_y = cy + task_h // 2
                        
                        self.di_edges.append(self.create_edge_di(flow_id, start_x, start_y, target_x, target_y))

                self.nodes.append(f'<bpmn:task id="{node_id}" name="{wrapped_name}"><bpmn:incoming>Flow_Incoming</bpmn:incoming><bpmn:outgoing>Flow_Outgoing</bpmn:outgoing></bpmn:task>')
                self.di_shapes.append(f'<bpmndi:BPMNShape id="{node_id}_di" bpmnElement="{node_id}"><dc:Bounds x="{cx}" y="{cy}" width="{task_w}" height="{task_h}" /></bpmndi:BPMNShape>')
                
                self._update_group_bounds(node.get("group"), cx, cy, task_w, task_h)
                
                last_endpoints = [{
                    'ref': node_id,
                    'x': cx + task_w,
                    'y': cy + task_h // 2
                }]
                
                # Spacing based on Task Width + Gap
                cx += task_w + self.horizontal_gap

            # --- END Event ---
            elif node_type == "end":
                node_id = self.get_id("End")
                # Wrap text for end event label? Usually shorter.
                
                if last_endpoints:
                    for ep in last_endpoints:
                        flow_id = self.get_id("Flow")
                        self.edges.append(f'<bpmn:sequenceFlow id="{flow_id}" sourceRef="{ep["ref"]}" targetRef="{node_id}" />')
                        
                        start_x = ep['x']
                        start_y = ep['y']
                        target_x = cx
                        target_y = cy + 18 # Center of 36px event
                        
                        self.di_edges.append(self.create_edge_di(flow_id, start_x, start_y, target_x, target_y))
                    
                self.nodes.append(f'<bpmn:endEvent id="{node_id}" name="{node_name}"><bpmn:incoming>Flow_Incoming</bpmn:incoming></bpmn:endEvent>')
                self.di_shapes.append(f'<bpmndi:BPMNShape id="{node_id}_di" bpmnElement="{node_id}"><dc:Bounds x="{cx}" y="{cy}" width="{self.event_size}" height="{self.event_size}" /></bpmndi:BPMNShape>')
                
                self._update_group_bounds(node.get("group"), cx, cy, self.event_size, self.event_size)
                
                last_endpoints = [{
                    'ref': node_id,
                    'x': cx + self.event_size,
                    'y': cy + self.event_size // 2
                }]
                
                cx += 100 # Padding after end

            # --- EXCLUSIVE GATEWAY ---
            elif node_type == "exclusive_gateway":
                node_id = self.get_id("Gateway")
                
                condition_text = node.get("condition", "?")
                wrapped_cond, gw_w, gw_h = self._wrap_text_and_get_size(condition_text, self.gateway_size, self.gateway_size, "diamond")
                
                if last_endpoints:
                    for ep in last_endpoints:
                        flow_id = self.get_id("Flow")
                        self.edges.append(f'<bpmn:sequenceFlow id="{flow_id}" sourceRef="{ep["ref"]}" targetRef="{node_id}" />')
                        
                        start_x = ep['x']
                        start_y = ep['y']
                        target_x = cx
                        target_y = cy + gw_h // 2
                        
                        self.di_edges.append(self.create_edge_di(flow_id, start_x, start_y, target_x, target_y))

                self.nodes.append(f'<bpmn:exclusiveGateway id="{node_id}" name="{wrapped_cond}"><bpmn:incoming>Flow_In</bpmn:incoming><bpmn:outgoing>Flow_True</bpmn:outgoing><bpmn:outgoing>Flow_False</bpmn:outgoing></bpmn:exclusiveGateway>')
                self.di_shapes.append(f'<bpmndi:BPMNShape id="{node_id}_di" bpmnElement="{node_id}"><dc:Bounds x="{cx}" y="{cy}" width="{gw_w}" height="{gw_h}" /></bpmndi:BPMNShape>')
                
                self._update_group_bounds(node.get("group"), cx, cy, gw_w, gw_h)
                
                gw_center_x = cx + gw_w // 2
                gw_center_y = cy + gw_h // 2
                
                # Branches
                true_nodes = node.get("true_branch", [])
                false_nodes = node.get("false_branch", [])
                
                collected_endpoints = []
                max_branch_x = cx + gw_w # Track furthest X
                
                # Calculate Spacing for Branches
                # Use longer initial branch connector to give space for labels
                branch_offset_x = 240
                
                # Process True Branch
                if true_nodes:
                    true_start_x = cx + branch_offset_x
                    true_start_y = cy - self.vertical_branch_gap
                    gw_endpoint = [{'ref': node_id, 'x': gw_center_x, 'y': gw_center_y, 'label': 'Yes'}]
                    
                    branch_endpoints = self.process_flow(true_nodes, true_start_x, true_start_y, incoming_endpoints=gw_endpoint)
                    collected_endpoints.extend(branch_endpoints)
                    
                    for bep in branch_endpoints:
                        max_branch_x = max(max_branch_x, bep['x'])
                else:
                    collected_endpoints.append({'ref': node_id, 'x': gw_center_x, 'y': gw_center_y, 'label': 'Yes'})
                
                # Process False Branch
                if false_nodes:
                    false_start_x = cx + branch_offset_x
                    false_start_y = cy + self.vertical_branch_gap
                    gw_endpoint = [{'ref': node_id, 'x': gw_center_x, 'y': gw_center_y, 'label': 'No'}]
                    
                    branch_endpoints = self.process_flow(false_nodes, false_start_x, false_start_y, incoming_endpoints=gw_endpoint)
                    collected_endpoints.extend(branch_endpoints)
                    
                    for bep in branch_endpoints:
                        max_branch_x = max(max_branch_x, bep['x'])
                else:
                    collected_endpoints.append({'ref': node_id, 'x': gw_center_x, 'y': gw_center_y, 'label': 'No'})

                # Converge at ends
                cx = max_branch_x + self.horizontal_gap
                last_endpoints = collected_endpoints

        return last_endpoints

    def _update_group_bounds(self, grp_name, x, y, w, h):
        if not grp_name: return
        if grp_name not in self.group_bounds:
            self.group_bounds[grp_name] = {'min_x': float('inf'), 'min_y': float('inf'), 'max_x': float('-inf'), 'max_y': float('-inf')}
        
        gb = self.group_bounds[grp_name]
        gb['min_x'] = min(gb['min_x'], x)
        gb['min_y'] = min(gb['min_y'], y)
        gb['max_x'] = max(gb['max_x'], x + w)
        gb['max_y'] = max(gb['max_y'], y + h)

    def create_edge_di(self, flow_id, x1, y1, x2, y2):
        # Improve routing: Add waypoints for right-angle connections if vertical difference fits
        # Simple Manhattan routing: x1,y1 -> x1_mid, y1 -> x1_mid, y2 -> x2, y2
        # For now, simple standard straight line to keep it stable, but let's check.
        # Direct line is usually safest for auto-layout unless we have a robust router.
        return f'<bpmndi:BPMNEdge id="{flow_id}_di" bpmnElement="{flow_id}"><di:waypoint x="{x1}" y="{y1}" /><di:waypoint x="{x2}" y="{y2}" /></bpmndi:BPMNEdge>'
