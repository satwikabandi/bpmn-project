# Project Technical Blueprint

## 1. Executive Summary
This project is an **AI-Powered BPMN (Business Process Model and Notation) Generator**. It bridges the gap between natural language descriptions and structured business process diagrams. By leveraging specific generative AI models for *understanding* and a deterministic compiler for *rendering*, it ensures that the generated diagrams are syntactically valid (standard BPMN 2.0) while accurately capturing the user's intent.

## 2. System Architecture

The application follows a modern decoupled architecture:
- **Frontend**: React.js (Vite)
- **Backend**: Django REST Framework (Python)
- **AI/ML Layer**: Google Gemini (GenAI) + Sentence Transformers (Hugging Face)

### Data Flow Pipeline
1.  **User Input**: User enters a process description (e.g., "Login flow where user inputs credentials...").
2.  **Normalization (AI Layer)**: The backend uses **Gemini 1.5 Flash** to convert this unstructured text into a structured pseudo-code format (Group/Start/Step/Decision).
3.  **Compilation (Rule Engine)**: A custom-built **BPMN Compiler** (Tokenizer → Parser → Builder) transforms the pseudo-code into standard BPMN 2.0 XML.
4.  **Validation (ML Layer)**: A **Semantic Similarity Model** compares the original input with the generated diagram's content to calculate an "Accuracy Score".
5.  **Rendering**: The React frontend uses `bpmn-js` to render the XML interactively.

---

## 3. Technology Stack & Rationale

| Component | Technology | Why we chose it |
| :--- | :--- | :--- |
| **Frontend Framework** | **React (Vite 7)** | Fast development (HMR), component-based architecture for the dashboard, and broad ecosystem compatibility. |
| **BPMN Rendering** | **bpmn-js** | The industry standard library for rendering BPMN 2.0 diagrams in the browser. It allows for navigation, zooming, and XML import. |
| **Styling** | **Tailwind CSS + Glassmorphism** | To create a "Premium" aesthetic (Gradients, Blur effects) as requested, moving away from standard flat enterprise designs. |
| **Backend Framework** | **Django REST Framework** | Robust, secure, and Python-native, making integration with AI/ML libraries (Torch, LangChain) seamless. |
| **Generative AI** | **Google Gemini 1.5 Flash** | Chosen for its speed and low latency. It is used *only* for logic normalization, not for direct XML generation (which helps avoid hallucinations). |
| **ML Model** | **sentence-transformers/paraphrase-xlm-r-multilingual-v1** | A lightweight, multilingual model used to compute semantic embeddings for accuracy scoring. |
| **Compiler** | **Custom Python Implementation** | Gives us 100% control over the XML structure and layout, ensuring valid file generation every time, unlike stochastic LLM outputs. |

---

## 4. Deep Dive: The BPMN Compiler

We built a custom compiler to ensure reliability. Direct LLM-to-XML generation often fails (invalid tags, broken references). Our approach is **Hybrid**: AI for logic, Code for syntax.

### Phase 1: Tokenizer (`tokenizer.py`)
- **Role**: Cleans raw input and identifies structure.
- **Logic**: Scanning for keywords (e.g., "Group:", "If", "Else"). It injects structural markers (newlines) to ensure the parser receives clean, line-by-line instructions.

### Phase 2: Parser (`parser.py`)
- **Role**: Converts tokens into a **Process Graph** (JSON).
- **Algorithm**: **Recursive Descent / Stack Machine**.
    - It maintains a `stack` to track nested contexts (e.g., inside an "If" block or a "Group").
    - **Multilingual Support**: It explicitly maps keywords in **English**, **Telugu**, and **Tamil** (e.g., "Start" = "ప్రారంభం") to standard BPMN start events.
    - **Implicit Logic**: It detects question marks (`?`) to automatically create Exclusive Gateways (Decisions).

### Phase 3: Builder (`builder.py`)
- **Role**: Layout Engine.
- **Algorithm**:
    - **Auto-Layout**: Calculates `x, y` coordinates for every node. It increments `x` for sequential tasks and branches `y` for gateways.
    - **Text Wrapping**: Calculates the pixel width/height of nodes based on text length to ensure labels fit inside boxes.
    - **BPMN DI Generation**: Generates the `<bpmndi:BPMNShape>` and `<bpmndi:BPMNEdge>` tags required for the diagram to be visible visually (not just semantically).

---

## 5. Machine Learning Algorithms

### 1. Semantic Accuracy Check (`ml_service.py`)
- **Objective**: To tell the user "confidently" how well the diagram matches their text.
- **Algorithm**: **Cosine Similarity on Embeddings**.
    1.  **Encode Input**: Convert user's description into a 768-dimensional vector using `paraphrase-xlm-r-multilingual-v1`.
    2.  **Encode Output**: Extract all `name` attributes from the generated BPMN XML and encode them into a vector.
    3.  **Compare**: Calculate the Cosine Similarity between the two vectors.
    4.  **Result**: A score (0-100%) indicating if the key concepts in the input are present in the diagram.

### 2. Logic Normalization (`gemini_service.py`)
- **Objective**: To support "Natural Language" instead of requiring users to write code.
- **Algorithm**: **Few-Shot Prompting**.
    - We provide Gemini with examples of "Messy Text" -> "Clean Pseudo-code".
    - *Example*: "User logs in, if valid go home" ->
        ```
        Start Process
        Task: User logs in
        Gateway: Is valid?
        Yes: Go home
        ```
    - This allows the deterministic parser to handle vague user inputs.

---

## 6. Frontend Minute Details

- **Custom Tree Node**: We built a recursive React component (`TreeNode`) to visualize the process structure as a hierarchical tree alongside the BPMN diagram.
- **Language Detection**: The frontend detects if the text contains Telugu or Tamil characters and adapts localized labels (e.g., showing 'వినియోగదారు ఇన్‌పుట్' for User Input).
- **Premium UI**: Uses `backdrop-filter: blur(12px)` and linear gradients to give a glass-like effect for nodes and panels.
