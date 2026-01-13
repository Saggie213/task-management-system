from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production-123456789')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security
security = HTTPBearer()

# Create the main app without a prefix
app = FastAPI(title="Task Management API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# ============= Utility Functions =============

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if user is None:
        raise credentials_exception
    return user


# ============= Pydantic Models =============

# User Models
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)


class UserResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# Task Models
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: str = Field(default="pending")
    due_date: Optional[datetime] = None
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        allowed_statuses = ["pending", "in-progress", "completed"]
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return v


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[datetime] = None
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ["pending", "in-progress", "completed"]
            if v not in allowed_statuses:
                raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return v


class TaskResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    title: str
    description: Optional[str] = None
    status: str
    due_date: Optional[datetime] = None
    created_at: datetime
    user_id: str


# ============= Authentication Routes =============

@api_router.post("/auth/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one(
        {"$or": [{"email": user_data.email}, {"username": user_data.username}]}
    )
    if existing_user:
        if existing_user.get("email") == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Create new user
    user_dict = user_data.model_dump()
    user_dict["id"] = str(uuid.uuid4())
    user_dict["password"] = get_password_hash(user_data.password)
    user_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.users.insert_one(user_dict)
    
    # Create access token
    access_token = create_access_token(data={"sub": user_dict["id"]})
    
    # Remove password from response
    user_dict.pop("password")
    user_dict["created_at"] = datetime.fromisoformat(user_dict["created_at"])
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(**user_dict)
    }


@api_router.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    # Find user by email
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user["id"]})
    
    # Remove password from response
    user.pop("password")
    user["created_at"] = datetime.fromisoformat(user["created_at"])
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(**user)
    }


@api_router.post("/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    # In JWT, logout is typically handled on the client side by removing the token
    return {"message": "Successfully logged out"}


@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    current_user["created_at"] = datetime.fromisoformat(current_user["created_at"])
    return UserResponse(**current_user)


# ============= User Profile Routes =============

@api_router.get("/user/profile", response_model=UserResponse)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    current_user["created_at"] = datetime.fromisoformat(current_user["created_at"])
    return UserResponse(**current_user)


@api_router.put("/user/profile", response_model=UserResponse)
async def update_user_profile(user_update: UserUpdate, current_user: dict = Depends(get_current_user)):
    update_data = user_update.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    # Check if username or email already exists (if being updated)
    if "username" in update_data or "email" in update_data:
        query_conditions = []
        if "username" in update_data:
            query_conditions.append({"username": update_data["username"]})
        if "email" in update_data:
            query_conditions.append({"email": update_data["email"]})
        
        existing_user = await db.users.find_one(
            {"$or": query_conditions, "id": {"$ne": current_user["id"]}}
        )
        if existing_user:
            if "email" in update_data and existing_user.get("email") == update_data["email"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            if "username" in update_data and existing_user.get("username") == update_data["username"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
    
    # Hash password if being updated
    if "password" in update_data:
        update_data["password"] = get_password_hash(update_data["password"])
    
    # Update user
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": update_data}
    )
    
    # Get updated user
    updated_user = await db.users.find_one({"id": current_user["id"]}, {"_id": 0, "password": 0})
    updated_user["created_at"] = datetime.fromisoformat(updated_user["created_at"])
    
    return UserResponse(**updated_user)


@api_router.delete("/user/profile")
async def delete_user_profile(current_user: dict = Depends(get_current_user)):
    # Delete all user's tasks
    await db.tasks.delete_many({"user_id": current_user["id"]})
    
    # Delete user
    await db.users.delete_one({"id": current_user["id"]})
    
    return {"message": "User profile and all associated tasks deleted successfully"}


# ============= Task Routes =============

@api_router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate, current_user: dict = Depends(get_current_user)):
    task_dict = task_data.model_dump()
    task_dict["id"] = str(uuid.uuid4())
    task_dict["user_id"] = current_user["id"]
    task_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    
    # Convert due_date to ISO string if present
    if task_dict["due_date"]:
        task_dict["due_date"] = task_dict["due_date"].isoformat()
    
    await db.tasks.insert_one(task_dict)
    
    # Convert back to datetime for response
    task_dict["created_at"] = datetime.fromisoformat(task_dict["created_at"])
    if task_dict["due_date"]:
        task_dict["due_date"] = datetime.fromisoformat(task_dict["due_date"])
    
    return TaskResponse(**task_dict)


@api_router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(
    status_filter: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    # Build query
    query = {"user_id": current_user["id"]}
    
    if status_filter:
        allowed_statuses = ["pending", "in-progress", "completed"]
        if status_filter not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(allowed_statuses)}"
            )
        query["status"] = status_filter
    
    tasks = await db.tasks.find(query, {"_id": 0}).to_list(1000)
    
    # Convert ISO strings back to datetime objects
    for task in tasks:
        task["created_at"] = datetime.fromisoformat(task["created_at"])
        if task.get("due_date"):
            task["due_date"] = datetime.fromisoformat(task["due_date"])
    
    return tasks


@api_router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, current_user: dict = Depends(get_current_user)):
    task = await db.tasks.find_one(
        {"id": task_id, "user_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Convert ISO strings back to datetime objects
    task["created_at"] = datetime.fromisoformat(task["created_at"])
    if task.get("due_date"):
        task["due_date"] = datetime.fromisoformat(task["due_date"])
    
    return TaskResponse(**task)


@api_router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    current_user: dict = Depends(get_current_user)
):
    # Check if task exists and belongs to user
    task = await db.tasks.find_one(
        {"id": task_id, "user_id": current_user["id"]}
    )
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    update_data = task_update.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    # Convert due_date to ISO string if present
    if "due_date" in update_data and update_data["due_date"]:
        update_data["due_date"] = update_data["due_date"].isoformat()
    
    # Update task
    await db.tasks.update_one(
        {"id": task_id},
        {"$set": update_data}
    )
    
    # Get updated task
    updated_task = await db.tasks.find_one({"id": task_id}, {"_id": 0})
    
    # Convert ISO strings back to datetime objects
    updated_task["created_at"] = datetime.fromisoformat(updated_task["created_at"])
    if updated_task.get("due_date"):
        updated_task["due_date"] = datetime.fromisoformat(updated_task["due_date"])
    
    return TaskResponse(**updated_task)


@api_router.delete("/tasks/{task_id}")
async def delete_task(task_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.tasks.delete_one(
        {"id": task_id, "user_id": current_user["id"]}
    )
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return {"message": "Task deleted successfully"}


# ============= Health Check Route =============

@api_router.get("/")
async def root():
    return {"message": "Task Management API is running", "version": "1.0.0"}


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
