# BPMN Project

An AI-powered BPMN (Business Process Model and Notation) tool. This project consists of a React frontend and a Django backend, utilizing generative AI capabilities.

## Prerequisites

- **Python** (3.8 or higher)
- **Node.js** (v16 or higher)
- **Git**
- **GitHub CLI** (optional, for easier repository interaction)

## Project Structure

- `backend/`: Django REST Framework application handling API requests, AI processing (LangChain, Google GenAI), and database interactions.
- `frontend/`: React application using Vite, providing the user interface for the BPMN tool.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/satwikabandi/bpmn-project.git
cd bpmn-project
```

### 2. Backend Setup

Navigate to the backend directory and set up the Python environment.

```bash
cd backend
```

**Create and activate a virtual environment:**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**Install dependencies:**

```bash
pip install -r requirements.txt
```

**Environment Variables:**

Create a `.env` file in the `backend/` directory. You will likely need API keys for the AI services (e.g., Google GenAI, Groq).
Example `.env`:
```
GOOGLE_API_KEY=your_google_api_key
# Add other necessary keys here
```

**Run Migrations:**

```bash
python manage.py migrate
```

**Start the Server:**

```bash
python manage.py runserver
```

The backend API will run at `http://localhost:8000`.

### 3. Frontend Setup

Open a new terminal and navigate to the frontend directory.

```bash
cd frontend
```

**Install Node dependencies:**

```bash
npm install
```

**Start the Development Server:**

```bash
npm run dev
```

The frontend application will typically run at `http://localhost:5173`.

## Usage

1.  Ensure both the Backend and Frontend servers are running.
2.  Open your browser and navigate to the frontend URL (e.g., `http://localhost:5173`).
3.  Use the application to generate or manage BPMN diagrams.

## Contributing

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/YourFeature`).
3.  Commit your changes (`git commit -m 'Add some feature'`).
4.  Push to the branch (`git push origin feature/YourFeature`).
5.  Open a Pull Request.
