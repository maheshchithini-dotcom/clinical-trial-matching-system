# AI-Powered Clinical Trial Matching System

This repository contains a full-stack web application that leverages Artificial Intelligence and Natural Language Processing (specifically, a Retrieval-Augmented Generation or RAG approach) to help match patients with suitable clinical trials.

## Project Architecture

The system is composed of two main parts:

1. **Frontend**: A React application built with Vite and TailwindCSS.
2. **Backend**: A FastAPI application powered by Python, utilizing SQLAlchemy for database operations, FAISS for vector similarity search, and the Gemini API for generative AI capabilities.

## Getting Started

### Prerequisites

- Node.js (for the frontend)
- Python 3.8+ (for the backend)
- A Gemini API Key

### Backend Setup

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure the environment variables:
   - Make sure to supply your Gemini API key in the `.env` file within the `backend` folder (e.g., `GEMINI_API_KEY=your_api_key_here`).
5. Run the FastAPI dev server:
   ```bash
   # Depending on your specific script or setup, e.g.:
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install the Node modules:
   ```bash
   npm install
   ```
3. Run the Vite development server:
   ```bash
   npm run dev
   ```

### Deployment
This project includes configurations for deployment. The backend can be deployed using the configurations defined in `requirements.deploy.txt`. The frontend includes a `vercel.json` file, indicating readiness for deployment on Vercel.

## Features

- **Semantic Search**: Uses FAISS backend and embeddings for matching patient profiles with clinical trials efficiently.
- **RAG Architecture**: Combines vector database searching with advanced language models to provide accurate reasoning for trial matching.
- **Modern UI**: A responsive, fast React interface styled with Tailwind CSS.
- **Database Agnostic**: Achieved via SQLAlchemy, ensuring compatibility with standard relational databases.
