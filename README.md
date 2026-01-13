# Task Management System - Kanban Board

A full-stack task management application with user authentication and a Kanban-style task board. Built as part of the OZi Technologies SDE Intern Assignment.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [API Documentation](#api-documentation)
- [Screenshots](#screenshots)
- [Assignment Requirements](#assignment-requirements)

---

## 🎯 Overview

This is a full-stack Task Management System that allows users to:
- Create and manage personal accounts
- Create, read, update, and delete tasks
- Organize tasks using a Kanban board with drag-and-drop functionality
- Track task status across three stages: Pending, In Progress, and Completed
- Set due dates for tasks
- Manage user profiles

## ✨ Features

### Authentication & User Management
- **User Registration**: Sign up with username, email, and password
- **User Login**: Secure JWT-based authentication
- **User Logout**: Properly handles session termination
- **Profile Management**: Update user information (username, email, full name, password)
- **Account Deletion**: Delete account with all associated tasks

### Task Management
- **Create Tasks**: Add new tasks with title, description, status, and due date
- **View Tasks**: See all personal tasks organized by status
- **Update Tasks**: Edit task details and status
- **Delete Tasks**: Remove tasks permanently
- **Filter Tasks**: API supports filtering tasks by status (pending/in-progress/completed)

### Kanban Board
- **Three Columns**: Pending, In Progress, Completed
- **Drag & Drop**: Move tasks between columns with smooth animations
- **Real-time Updates**: Status changes persist immediately to the database
- **Task Cards**: Display task title, description, and due date
- **Task Count**: Shows number of tasks in each column

### UI/UX
- **Mobile Responsive**: Fully responsive design that works on all devices
- **Modern Design**: Clean interface using Tailwind CSS
- **Error Handling**: User-friendly error messages
- **Loading States**: Visual feedback during API calls
- **Form Validation**: Client and server-side validation

---

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: MongoDB (with Motor async driver)
- **Authentication**: JWT (JSON Web Tokens) with bcrypt password hashing
- **Validation**: Pydantic models
- **CORS**: Enabled for cross-origin requests

### Frontend
- **Framework**: React 19
- **Routing**: React Router DOM
- **Styling**: Tailwind CSS
- **Drag & Drop**: react-beautiful-dnd
- **HTTP Client**: Axios
- **Date Handling**: date-fns
- **UI Components**: Custom components with Radix UI primitives

### Development Tools
- **Process Management**: Supervisor
- **Package Manager**: Yarn (Frontend), pip (Backend)
- **Code Quality**: ESLint, Prettier

---

## 📁 Project Structure

```
/app/
├── backend/                    # FastAPI backend
│   ├── server.py              # Main FastAPI application
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables
│
├── frontend/                  # React frontend
│   ├── public/               # Static assets
│   ├── src/
│   │   ├── api/              # API client functions
│   │   │   └── tasks.js      # Task API calls
│   │   ├── components/       # Reusable components
│   │   │   ├── TaskModal.js  # Task create/edit modal
│   │   │   ├── PrivateRoute.js # Auth guard component
│   │   │   └── ui/           # UI primitives
│   │   ├── contexts/         # React contexts
│   │   │   └── AuthContext.js # Authentication context
│   │   ├── pages/            # Page components
│   │   │   ├── Login.js      # Login page
│   │   │   ├── Signup.js     # Registration page
│   │   │   ├── Dashboard.js  # Kanban board
│   │   │   └── Profile.js    # User profile
│   │   ├── App.js            # Main app component
│   │   ├── App.css           # App styles
│   │   ├── index.js          # Entry point
│   │   └── index.css         # Global styles
│   ├── package.json          # Node.js dependencies
│   ├── tailwind.config.js    # Tailwind configuration
│   └── .env                  # Environment variables
│
├── tests/                    # Test files
├── README.md                 # This file
└── .gitignore               # Git ignore rules

```

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 14+ and Yarn
- MongoDB

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd /app/backend
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   Create a `.env` file in the backend directory:
   ```env
   MONGO_URL=mongodb://localhost:27017
   DB_NAME=task_management
   CORS_ORIGINS=*
   JWT_SECRET_KEY=your-secret-key-change-in-production
   ```

4. **Start the backend server:**
   ```bash
   uvicorn server:app --host 0.0.0.0 --port 8001 --reload
   ```

   The backend will be available at `http://localhost:8001`

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd /app/frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   yarn install
   ```

3. **Configure environment variables:**
   Create a `.env` file in the frontend directory:
   ```env
   REACT_APP_BACKEND_URL=http://localhost:8001
   ```

4. **Start the frontend development server:**
   ```bash
   yarn start
   ```

   The frontend will be available at `http://localhost:3000`

### Using Supervisor (Recommended for Production)

The project is configured to run with Supervisor for process management:

```bash
# Start all services
sudo supervisorctl start all

# Restart backend
sudo supervisorctl restart backend

# Restart frontend
sudo supervisorctl restart frontend

# Check status
sudo supervisorctl status
```

---

## 📚 API Documentation

### Base URL
```
http://localhost:8001/api
```

### Authentication Endpoints

#### POST /auth/signup
Register a new user.

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "password123",
  "full_name": "John Doe"  // optional
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "username": "johndoe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "created_at": "2026-01-13T05:23:04.993398Z"
  }
}
```

#### POST /auth/login
Authenticate an existing user.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

**Response:** Same as signup

#### POST /auth/logout
Logout current user (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

#### GET /auth/me
Get current user information (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

### User Profile Endpoints

#### GET /user/profile
Get current user's profile (requires authentication).

#### PUT /user/profile
Update user profile (requires authentication).

**Request Body:**
```json
{
  "username": "newusername",  // optional
  "email": "newemail@example.com",  // optional
  "full_name": "New Name",  // optional
  "password": "newpassword"  // optional
}
```

#### DELETE /user/profile
Delete user account and all associated tasks (requires authentication).

### Task Endpoints

#### POST /tasks
Create a new task (requires authentication).

**Request Body:**
```json
{
  "title": "Complete Project",
  "description": "Finish the task management system",
  "status": "pending",  // pending | in-progress | completed
  "due_date": "2026-01-20T10:00:00Z"  // optional
}
```

#### GET /tasks
Get all tasks for the current user (requires authentication).

**Query Parameters:**
- `status_filter` (optional): Filter by status (pending, in-progress, completed)

**Example:**
```
GET /tasks?status_filter=pending
```

#### GET /tasks/{task_id}
Get a specific task by ID (requires authentication).

#### PUT /tasks/{task_id}
Update a task (requires authentication).

**Request Body:**
```json
{
  "title": "Updated Title",  // optional
  "description": "Updated description",  // optional
  "status": "in-progress",  // optional
  "due_date": "2026-01-25T10:00:00Z"  // optional
}
```

#### DELETE /tasks/{task_id}
Delete a task (requires authentication).

---

## 📸 Screenshots

### Login Page
Clean and simple login interface with form validation.

### Signup Page
User registration with username, email, password, and optional full name.

### Kanban Dashboard
Three-column layout with drag-and-drop functionality:
- Pending tasks
- In Progress tasks
- Completed tasks

### Task Modal
Create or edit tasks with:
- Title (required)
- Description (optional)
- Status selection
- Due date picker

### Profile Page
View and edit user information:
- Username
- Email
- Full name
- Password
- Account deletion option

---

## ✅ Assignment Requirements

This project fulfills all the requirements specified in the OZi Technologies SDE Intern Assignment:

### Backend Requirements ✓
- ✅ RESTful API built with Python (FastAPI)
- ✅ User authentication (Sign Up, Login, Logout)
- ✅ User profile management (Update & Delete)
- ✅ Full CRUD operations for tasks
- ✅ Task fields: title, description, status, due_date, created_at
- ✅ User-specific tasks
- ✅ API filtering by status
- ✅ Proper API routing and folder structure
- ✅ Input validation with meaningful error responses
- ✅ Comprehensive README with setup instructions

### Frontend Requirements ✓
- ✅ User can edit profile details
- ✅ Login and logout functionality
- ✅ Kanban board with three columns (Pending, In Progress, Completed)
- ✅ Task cards display title, description, and due date
- ✅ Tasks fetched from backend and organized by status
- ✅ Drag & drop functionality between columns
- ✅ Status updates persist via backend API
- ✅ Clean, minimal styling with Tailwind CSS
- ✅ Mobile responsive design

### Submission Guidelines ✓
- ✅ Single Git repository with frontend and backend
- ✅ Meaningful commit messages
- ✅ No unnecessary files (node_modules, .env excluded)
- ✅ Comprehensive README.md
- ✅ Environment variables properly configured
- ✅ MongoDB database (flexible choice)
- ✅ Protected routes with authentication
- ✅ Proper error handling with HTTP status codes
- ✅ Data-testid attributes for testing

---

## 🔒 Security Features

- **Password Hashing**: Passwords are hashed using bcrypt
- **JWT Authentication**: Secure token-based authentication
- **Protected Routes**: Frontend routes require authentication
- **Input Validation**: Both client and server-side validation
- **CORS Configuration**: Properly configured for security
- **Environment Variables**: Sensitive data stored in .env files

---

## 🧪 Testing

### Manual Testing

1. **Test User Registration:**
   ```bash
   curl -X POST http://localhost:8001/api/auth/signup \
     -H "Content-Type: application/json" \
     -d '{"username":"testuser","email":"test@example.com","password":"password123"}'
   ```

2. **Test User Login:**
   ```bash
   curl -X POST http://localhost:8001/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"password123"}'
   ```

3. **Test Create Task:**
   ```bash
   curl -X POST http://localhost:8001/api/tasks \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <your_token>" \
     -d '{"title":"Test Task","status":"pending"}'
   ```

4. **Test Get Tasks:**
   ```bash
   curl -X GET http://localhost:8001/api/tasks \
     -H "Authorization: Bearer <your_token>"
   ```

---

## 📝 License

This project was created as part of the OZi Technologies SDE Intern Assignment.

---

## 👤 Author

Created for the OZi Technologies Software Development Engineer Intern position.

---

## 🙏 Acknowledgments

- OZi Technologies for the assignment opportunity
- FastAPI for the excellent Python web framework
- React team for the powerful frontend library
- Atlassian for react-beautiful-dnd

---

## 📞 Support

For any questions or issues, please contact: hr@ozi.in
