# Todo Web Application – Phase II Implementation

This is a full-stack Todo web application implementing the Phase II specifications using modern web technologies with secure authentication, database integration, and RESTful API handling.

## 🌐 Live Demo

👉 https://hackathon2-phase2-two.vercel.app/

---

## 🛠 Tech Stack

- **Frontend**: Next.js 14+, TypeScript, Tailwind CSS
- **Backend**: Python FastAPI
- **ORM**: SQLModel
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: Better Auth with JWT Tokens

---

## ✨ Features Implemented

### 🔐 Authentication System
- Email/password authentication (no email verification)
- JWT token issued on successful login
- Frontend sends JWT with every request using  
  `Authorization: Bearer <token>`
- Backend verifies JWT and extracts `user_id`
- All protected endpoints return `401 Unauthorized` if token is invalid

---

### 📌 Todo API Endpoints (FastAPI)

- `GET /api/{user_id}/tasks` → List all tasks
- `POST /api/{user_id}/tasks` → Create a new task
- `GET /api/{user_id}/tasks/{id}` → Retrieve a specific task
- `PUT /api/{user_id}/tasks/{id}` → Update a task
- `DELETE /api/{user_id}/tasks/{id}` → Delete a task
- `PATCH /api/{user_id}/tasks/{id}/complete` → Toggle task completion

✅ All responses are valid JSON  
✅ Tasks are strictly filtered by authenticated `user_id`

---

### 🗄 Database Schema

- `users` table managed by Better Auth
- `tasks` table with required fields
- Indexed columns:
  - `tasks.user_id`
  - `tasks.completed`

---

### 🎨 Frontend Architecture

- Reusable API client located at `/lib/api.ts`
- Centralized request handling for:
  - Authentication
  - Task CRUD operations
  - Task completion toggle

---

## ⚙️ Environment Variables

### Frontend (`.env.local`)
```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_BETTER_AUTH_SECRET=your_better_auth_secret_here
```
### Backend (.env)
DATABASE_URL=your_postgresql_connection_string
BETTER_AUTH_SECRET=your_better_auth_secret_here
SECRET_KEY=your_jwt_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

## 🚀 Running the Application

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```
## Frontend Setup
cd frontend
npm install
npm run dev

### 📦 API Client Usage

Reusable API client is available at:

## frontend/lib/api.ts


#### Available Functions

- `signUp(email, password)`
- `signIn(email, password)`
- `getTasks(userId)`
- `createTask(userId, title, description)`
- `updateTask(userId, id, title, description)`
- `deleteTask(userId, id)`
- `toggleComplete(userId, id)`

---

### 📌 Notes

This project was built following **production-grade best practices**, with a focus on:

- Clean architecture
- Secure authentication
- Scalable backend design
- Modern frontend stack



