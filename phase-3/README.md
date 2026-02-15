# Full-Stack ToDo Application with Chatbot (Phase 3)

## Description
This is a full-stack ToDo application designed to demonstrate modern web development practices with added AI integration. It features a robust backend built with FastAPI and a dynamic frontend powered by Next.js. Users can manage their tasks efficiently and interact with an AI chatbot for task management assistance, providing a seamless and intuitive experience.

## Live Application
You can access the deployed application at: [https://hackathon-2phase3.vercel.app/](https://hackathon-2phase3.vercel.app/)

## Technologies Used

### Frontend
*   **Next.js:** A React framework for building server-side rendered and static web applications.
*   **React:** A JavaScript library for building user interfaces.
*   **Tailwind CSS:** A utility-first CSS framework for rapidly building custom designs.
*   **Axios:** Promise-based HTTP client for the browser and Node.js.
*   **Zod:** TypeScript-first schema declaration and validation library.

### Backend
*   **FastAPI:** A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.
*   **Uvicorn:** An ASGI server for FastAPI, providing asynchronous capabilities.
*   **SQLModel:** A library for interacting with SQL databases from Python code, with Python objects. It's designed to be simple, intuitive, and robust, and is based on Pydantic and SQLAlchemy.
*   **PostgreSQL:** A powerful, open-source object-relational database system.
*   **python-dotenv:** For managing environment variables.
*   **python-jose:** For JSON Web Token (JWT) handling.
*   **passlib:** For password hashing.
*   **better-auth:** Authentication library for secure user management.
*   **OpenAI API:** For AI-powered chatbot functionality.

## Key Features
*   User authentication and authorization
*   Full CRUD operations for todo tasks
*   Interactive AI chatbot for task management
*   Responsive UI design
*   Secure session management

## Setup Instructions

Follow these steps to get the project up and running on your local machine.

### Prerequisites

Before you begin, ensure you have the following installed:

*   **Node.js** (LTS version recommended)
*   **npm** (comes with Node.js)
*   **Python 3.9+**
*   **pip** (comes with Python)
*   **PostgreSQL** database server running

### 1. Clone the Repository

```bash
git clone <repository_url>
cd hackathon-2phase3 # or your project root directory
```

### 2. Backend Setup

Navigate to the `backend` directory, set up a virtual environment, install dependencies, and configure your environment variables.

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

**Environment Variables for Backend:**

Create a `.env` file in the `backend` directory with the following content:

```env
DATABASE_URL="postgresql://user:password@host:port/database_name"
SECRET_KEY="your-super-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
GEMINI_API_KEY="your-gemini-api-key"
```
*   Replace `user`, `password`, `host`, `port`, and `database_name` with your PostgreSQL database credentials.
*   Generate a strong `SECRET_KEY` for JWT.
*   Add your OpenAI API key for chatbot functionality.

### 3. Frontend Setup

Navigate to the `frontend` directory, install dependencies, and configure your environment variables.

```bash
cd ../frontend
npm install
```

**Environment Variables for Frontend:**

Create a `.env.local` file in the `frontend` directory with the following content:

```env
NEXT_PUBLIC_API_URL="http://localhost:8000" # Or wherever your backend is running
```
*   Ensure `NEXT_PUBLIC_API_URL` points to your running backend API.

## How to Run the Application

Once both the backend and frontend are set up, you can start them independently.

### 1. Start the Backend Server

```bash
cd backend
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```
The backend will be accessible at `http://localhost:8000`.

### 2. Start the Frontend Development Server

```bash
cd frontend
npm run dev
```
The frontend application will be accessible at `http://localhost:3000` (or another port if 3000 is occupied).

Open your web browser and navigate to `http://localhost:3000` to access the ToDo application.

## Project Structure Overview

```
hackathon-2phase3/
├── backend/                  # FastAPI backend application
│   ├── src/                  # Backend source code
│   │   ├── api/              # API routes and middleware
│   │   │   ├── routes/       # Individual route files (auth, todos, chat)
│   │   ├── database/         # Database connection and tables
│   │   ├── models/           # SQLModel models
│   │   ├── mcp/              # MCP server and tools
│   │   └── services/         # Business logic and services
│   ├── requirements.txt      # Python dependencies
│   └── ...
├── frontend/                 # Next.js frontend application
│   ├── src/                  # Frontend source code
│   │   ├── components/       # Reusable UI components
│   │   │   ├── chat/         # Chat interface components
│   │   │   ├── common/       # Common UI elements
│   │   │   └── layout/       # Layout components
│   │   ├── hooks/            # React hooks
│   │   ├── pages/            # Next.js pages (routes)
│   │   ├── services/         # API interaction services
│   │   └── styles/           # Global styles
│   ├── package.json          # Node.js dependencies
│   └── ...
└── README.md                 # Project documentation
```

## Testing

### Backend Testing

Navigate to the `backend` directory and run pytest:
```bash
cd backend
source venv/bin/activate # On Windows: .\venv\Scripts\activate
pytest
```

### Frontend Testing

Frontend tests are typically run with a command like:
```bash
cd frontend
npm test
```

## AI Chatbot Integration
The application includes an AI chatbot that can assist with:
*   Creating new tasks via natural language
*   Updating existing tasks
*   Checking task status
*   Providing suggestions for task management