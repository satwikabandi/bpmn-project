import os
import re
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    print("Warning: google-genai library not found. AI features disabled.")

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if genai and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Gemini Client Init Error: {e}")
                self.client = None
        else:
            self.client = None

    def generate_bpmn(self, text, context=""):
        # Try API first if client exists
        if self.client:
            try:
                system_prompt = """
                You are an expert BPMN 2.0 XML generator. 
                Convert the following process description into a valid BPMN 2.0 XML file. 
                Output ONLY the XML code. No markdown backticks.
                """
                full_content = f"Process Description: {text}"
                if context:
                    full_content += f"\n\nContext:\n{context}"
                
                # Using gemini-1.5-flash-latest as a fallback for quota issues
                response = self.client.models.generate_content(
                    model="gemini-1.5-flash-latest",
                    contents=full_content,
                    config=types.GenerateContentConfig(system_instruction=system_prompt)
                )
                xml = response.text
                if xml.startswith("```"):
                   xml = xml.replace("```xml", "").replace("```", "")
                return xml.strip()
            except Exception as e:
                print(f"API Error: {e}. Falling back to Smart Mock.")

        # Fallback to Smart Mock
        return self.get_smart_mock_bpmn(text)

    def normalize_input(self, text):
        """
        Uses Gemini to convert natural language into the strict syntax expected by our Parser.
        Syntax Rules:
        - 'Start Process', 'End Process'
        - 'Group: <Name>', 'End Group'
        - Questions ending in '?' imply gateways.
        - Branches: 'Yes:' / 'No:' (indented)
        """
        if not self.client:
            return text # Passthrough if no API key

        prompt = """
        You are a BPMN Logic Normalizer. Convert the user's natural language description into a strict, indented pseudo-code format.
        
        Rules:
        1. Use "Group: <Name>" and "End Group" for logical sections.
        2. Use "Start Process" and "End Process".
        3. For decisions, end the line with "?" (e.g., "Is login valid?").
        4. For branches, use "Yes:" and "No:" on new lines, followed by indented steps.
        5. Keep step names concise (e.g. "Enter Credentials", "Check Database").
        6. Do not include markdown code blocks. Just the text.
        
        Example Input: "Users log in. It checks if valid. If yes go home, if no show error."
        Example Output:
        Start Process
        Group: Authentication
            Enter Credentials
            Is login valid?
            Yes:
               Redirect Home
               End Process
            No:
               Show Error
               End Process
        End Group
        
        User Input:
        """ + text
        
        try:
            response = self.client.models.generate_content(
                model="gemini-1.5-flash-latest",
                contents=prompt
            )
            return response.text.replace("```", "").strip()
        except Exception as e:
            print(f"Gemini Normalization Error: {e}")
            return text # Fallback to original text

    def get_smart_mock_bpmn(self, text):
        text_lower = text.lower()

        # Template 0: Login (Specific Match)
        if any(w in text_lower for w in ['login', 'sign in', 'credential', 'password', 'username', 'auth']):
            return """<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" id="Definitions_Login">
  <bpmn:process id="Process_Login" isExecutable="false">
    <bpmn:startEvent id="Start" name="User Opens Login Page"><bpmn:outgoing>F1</bpmn:outgoing></bpmn:startEvent>
    <bpmn:task id="Task1" name="Enter Username & Password"><bpmn:incoming>F1</bpmn:incoming><bpmn:outgoing>F2</bpmn:outgoing></bpmn:task>
    <bpmn:task id="Task2" name="Validate Credentials"><bpmn:incoming>F2</bpmn:incoming><bpmn:outgoing>F3</bpmn:outgoing></bpmn:task>
    <bpmn:exclusiveGateway id="Gateway" name="Valid?"><bpmn:incoming>F3</bpmn:incoming><bpmn:outgoing>F4</bpmn:outgoing><bpmn:outgoing>F5</bpmn:outgoing></bpmn:exclusiveGateway>
    <bpmn:task id="Task3" name="Show Home Page"><bpmn:incoming>F4</bpmn:incoming><bpmn:outgoing>F6</bpmn:outgoing></bpmn:task>
    <bpmn:task id="Task4" name="Show Error Message"><bpmn:incoming>F5</bpmn:incoming><bpmn:outgoing>F7</bpmn:outgoing></bpmn:task>
    <bpmn:endEvent id="End1" name="Login Successful"><bpmn:incoming>F6</bpmn:incoming></bpmn:endEvent>
    <bpmn:endEvent id="End2" name="Login Failed"><bpmn:incoming>F7</bpmn:incoming></bpmn:endEvent>
    <bpmn:sequenceFlow id="F1" sourceRef="Start" targetRef="Task1" />
    <bpmn:sequenceFlow id="F2" sourceRef="Task1" targetRef="Task2" />
    <bpmn:sequenceFlow id="F3" sourceRef="Task2" targetRef="Gateway" />
    <bpmn:sequenceFlow id="F4" sourceRef="Gateway" targetRef="Task3" name="Yes" />
    <bpmn:sequenceFlow id="F5" sourceRef="Gateway" targetRef="Task4" name="No" />
    <bpmn:sequenceFlow id="F6" sourceRef="Task3" targetRef="End1" />
    <bpmn:sequenceFlow id="F7" sourceRef="Task4" targetRef="End2" />
  </bpmn:process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_Login">
    <bpmndi:BPMNPlane id="BPMNPlane_Login" bpmnElement="Process_Login">
      <bpmndi:BPMNShape id="Start_di" bpmnElement="Start"><dc:Bounds x="150" y="100" width="36" height="36" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task1_di" bpmnElement="Task1"><dc:Bounds x="240" y="80" width="100" height="80" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task2_di" bpmnElement="Task2"><dc:Bounds x="390" y="80" width="100" height="80" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Gateway_di" bpmnElement="Gateway"><dc:Bounds x="540" y="95" width="50" height="50" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task3_di" bpmnElement="Task3"><dc:Bounds x="640" y="80" width="100" height="80" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task4_di" bpmnElement="Task4"><dc:Bounds x="640" y="200" width="100" height="80" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="End1_di" bpmnElement="End1"><dc:Bounds x="790" y="102" width="36" height="36" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="End2_di" bpmnElement="End2"><dc:Bounds x="790" y="222" width="36" height="36" /></bpmndi:BPMNShape>
      <bpmndi:BPMNEdge id="F1_di" bpmnElement="F1"><di:waypoint x="186" y="118" /><di:waypoint x="240" y="118" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="F2_di" bpmnElement="F2"><di:waypoint x="340" y="120" /><di:waypoint x="390" y="120" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="F3_di" bpmnElement="F3"><di:waypoint x="490" y="120" /><di:waypoint x="540" y="120" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="F4_di" bpmnElement="F4"><di:waypoint x="590" y="120" /><di:waypoint x="640" y="120" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="F5_di" bpmnElement="F5"><di:waypoint x="565" y="145" /><di:waypoint x="565" y="240" /><di:waypoint x="640" y="240" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="F6_di" bpmnElement="F6"><di:waypoint x="740" y="120" /><di:waypoint x="790" y="120" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="F7_di" bpmnElement="F7"><di:waypoint x="740" y="240" /><di:waypoint x="790" y="240" /></bpmndi:BPMNEdge>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>"""
        if any(w in text_lower for w in ['shop', 'buy', 'cart', 'payment', 'order', 'checkout', 'product']):
            return """<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" id="Definitions_1">
  <bpmn:process id="Process_Shop" isExecutable="false">
    <bpmn:startEvent id="Start" name="Browse Products"><bpmn:outgoing>F1</bpmn:outgoing></bpmn:startEvent>
    <bpmn:task id="Task1" name="Add to Cart"><bpmn:incoming>F1</bpmn:incoming><bpmn:outgoing>F2</bpmn:outgoing></bpmn:task>
    <bpmn:task id="Task2" name="Checkout"><bpmn:incoming>F2</bpmn:incoming><bpmn:outgoing>F3</bpmn:outgoing></bpmn:task>
    <bpmn:exclusiveGateway id="Gateway" name="Payment Success?"><bpmn:incoming>F3</bpmn:incoming><bpmn:outgoing>F4</bpmn:outgoing><bpmn:outgoing>F5</bpmn:outgoing></bpmn:exclusiveGateway>
    <bpmn:task id="Task3" name="Send Invoice"><bpmn:incoming>F4</bpmn:incoming><bpmn:outgoing>F6</bpmn:outgoing></bpmn:task>
    <bpmn:endEvent id="End1" name="Order Completed"><bpmn:incoming>F6</bpmn:incoming></bpmn:endEvent>
    <bpmn:task id="Task4" name="Show Error"><bpmn:incoming>F5</bpmn:incoming><bpmn:outgoing>F7</bpmn:outgoing></bpmn:task>
    <bpmn:endEvent id="End2" name="Payment Failed"><bpmn:incoming>F7</bpmn:incoming></bpmn:endEvent>
    <bpmn:sequenceFlow id="F1" sourceRef="Start" targetRef="Task1" />
    <bpmn:sequenceFlow id="F2" sourceRef="Task1" targetRef="Task2" />
    <bpmn:sequenceFlow id="F3" sourceRef="Task2" targetRef="Gateway" />
    <bpmn:sequenceFlow id="F4" sourceRef="Gateway" targetRef="Task3" name="Yes" />
    <bpmn:sequenceFlow id="F5" sourceRef="Gateway" targetRef="Task4" name="No" />
    <bpmn:sequenceFlow id="F6" sourceRef="Task3" targetRef="End1" />
    <bpmn:sequenceFlow id="F7" sourceRef="Task4" targetRef="End2" />
  </bpmn:process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_Shop">
      <bpmndi:BPMNShape id="Start_di" bpmnElement="Start"><dc:Bounds x="150" y="100" width="36" height="36" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task1_di" bpmnElement="Task1"><dc:Bounds x="240" y="80" width="100" height="80" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task2_di" bpmnElement="Task2"><dc:Bounds x="390" y="80" width="100" height="80" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Gateway_di" bpmnElement="Gateway"><dc:Bounds x="540" y="95" width="50" height="50" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task3_di" bpmnElement="Task3"><dc:Bounds x="640" y="80" width="100" height="80" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="End1_di" bpmnElement="End1"><dc:Bounds x="790" y="102" width="36" height="36" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task4_di" bpmnElement="Task4"><dc:Bounds x="640" y="200" width="100" height="80" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="End2_di" bpmnElement="End2"><dc:Bounds x="790" y="222" width="36" height="36" /></bpmndi:BPMNShape>
      <bpmndi:BPMNEdge id="F1_di" bpmnElement="F1"><di:waypoint x="186" y="118" /><di:waypoint x="240" y="118" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="F2_di" bpmnElement="F2"><di:waypoint x="340" y="120" /><di:waypoint x="390" y="120" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="F3_di" bpmnElement="F3"><di:waypoint x="490" y="120" /><di:waypoint x="540" y="120" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="F4_di" bpmnElement="F4"><di:waypoint x="590" y="120" /><di:waypoint x="640" y="120" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="F5_di" bpmnElement="F5"><di:waypoint x="565" y="145" /><di:waypoint x="565" y="240" /><di:waypoint x="640" y="240" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="F6_di" bpmnElement="F6"><di:waypoint x="740" y="120" /><di:waypoint x="790" y="120" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="F7_di" bpmnElement="F7"><di:waypoint x="740" y="240" /><di:waypoint x="790" y="240" /></bpmndi:BPMNEdge>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>"""

        # Template 2: HR / Hiring
        if any(w in text_lower for w in ['hire', 'interview', 'candidate', 'offer', 'employee', 'onboard']):
            return """<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" id="Definitions_HR">
  <bpmn:process id="Process_HR" isExecutable="false">
    <bpmn:startEvent id="Start" name="Receive Application"><bpmn:outgoing>F1</bpmn:outgoing></bpmn:startEvent>
    <bpmn:task id="Task1" name="Screen Resume"><bpmn:incoming>F1</bpmn:incoming><bpmn:outgoing>F2</bpmn:outgoing></bpmn:task>
    <bpmn:exclusiveGateway id="Gateway" name="Qualified?"><bpmn:incoming>F2</bpmn:incoming><bpmn:outgoing>F3</bpmn:outgoing><bpmn:outgoing>F4</bpmn:outgoing></bpmn:exclusiveGateway>
    <bpmn:task id="Task2" name="Schedule Interview"><bpmn:incoming>F3</bpmn:incoming><bpmn:outgoing>F5</bpmn:outgoing></bpmn:task>
    <bpmn:task id="Task3" name="Send Rejection"><bpmn:incoming>F4</bpmn:incoming><bpmn:outgoing>F6</bpmn:outgoing></bpmn:task>
    <bpmn:endEvent id="End1" name="Hired"><bpmn:incoming>F5</bpmn:incoming></bpmn:endEvent>
    <bpmn:endEvent id="End2" name="Rejected"><bpmn:incoming>F6</bpmn:incoming></bpmn:endEvent>
    <bpmn:sequenceFlow id="F1" sourceRef="Start" targetRef="Task1" />
    <bpmn:sequenceFlow id="F2" sourceRef="Task1" targetRef="Gateway" />
    <bpmn:sequenceFlow id="F3" sourceRef="Gateway" targetRef="Task2" name="Yes" />
    <bpmn:sequenceFlow id="F4" sourceRef="Gateway" targetRef="Task3" name="No" />
    <bpmn:sequenceFlow id="F5" sourceRef="Task2" targetRef="End1" />
    <bpmn:sequenceFlow id="F6" sourceRef="Task3" targetRef="End2" />
  </bpmn:process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_HR">
    <bpmndi:BPMNPlane id="BPMNPlane_HR" bpmnElement="Process_HR">
      <bpmndi:BPMNShape id="Start_di" bpmnElement="Start"><dc:Bounds x="150" y="100" width="36" height="36" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task1_di" bpmnElement="Task1"><dc:Bounds x="240" y="80" width="100" height="80" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Gateway_di" bpmnElement="Gateway"><dc:Bounds x="390" y="95" width="50" height="50" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task2_di" bpmnElement="Task2"><dc:Bounds x="500" y="80" width="100" height="80" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task3_di" bpmnElement="Task3"><dc:Bounds x="500" y="200" width="100" height="80" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="End1_di" bpmnElement="End1"><dc:Bounds x="650" y="102" width="36" height="36" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="End2_di" bpmnElement="End2"><dc:Bounds x="650" y="222" width="36" height="36" /></bpmndi:BPMNShape>
      <bpmndi:BPMNEdge id="F1_di" bpmnElement="F1"><di:waypoint x="186" y="118" /><di:waypoint x="240" y="118" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="F2_di" bpmnElement="F2"><di:waypoint x="340" y="120" /><di:waypoint x="390" y="120" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="F3_di" bpmnElement="F3"><di:waypoint x="440" y="120" /><di:waypoint x="500" y="120" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="F4_di" bpmnElement="F4"><di:waypoint x="415" y="145" /><di:waypoint x="415" y="240" /><di:waypoint x="500" y="240" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="F5_di" bpmnElement="F5"><di:waypoint x="600" y="120" /><di:waypoint x="650" y="120" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="F6_di" bpmnElement="F6"><di:waypoint x="600" y="240" /><di:waypoint x="650" y="240" /></bpmndi:BPMNEdge>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>"""

        # Default Template: Login / Generic
        return """<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" id="Definitions_1">
  <bpmn:process id="Process_1" isExecutable="false">
    <bpmn:startEvent id="Start" name="Start Process"><bpmn:outgoing>F1</bpmn:outgoing></bpmn:startEvent>
    <bpmn:task id="Task1" name="Execute Action"><bpmn:incoming>F1</bpmn:incoming><bpmn:outgoing>F2</bpmn:outgoing></bpmn:task>
    <bpmn:endEvent id="End" name="End Process"><bpmn:incoming>F2</bpmn:incoming></bpmn:endEvent>
    <bpmn:sequenceFlow id="F1" sourceRef="Start" targetRef="Task1" />
    <bpmn:sequenceFlow id="F2" sourceRef="Task1" targetRef="End" />
  </bpmn:process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_1">
      <bpmndi:BPMNShape id="Start_di" bpmnElement="Start"><dc:Bounds x="150" y="100" width="36" height="36" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task1_di" bpmnElement="Task1"><dc:Bounds x="240" y="80" width="100" height="80" /></bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="End_di" bpmnElement="End"><dc:Bounds x="390" y="102" width="36" height="36" /></bpmndi:BPMNShape>
      <bpmndi:BPMNEdge id="F1_di" bpmnElement="F1"><di:waypoint x="186" y="118" /><di:waypoint x="240" y="118" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="F2_di" bpmnElement="F2"><di:waypoint x="340" y="120" /><di:waypoint x="390" y="120" /></bpmndi:BPMNEdge>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>"""
