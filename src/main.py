from datetime import datetime, timedelta
import os
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship

# ---------------- Config ----------------
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# ---------------- DB setup --------------
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    todos = relationship("Todo", back_populates="owner", cascade="all,delete")

class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    done = Column(Boolean, default=False, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="todos")

Base.metadata.create_all(bind=engine)

# ---------------- Security --------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")  # subject
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

# ---------------- Schemas ----------------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserCreate(BaseModel):
    username: str
    password: str

class TodoCreate(BaseModel):
    title: str

class TodoOut(BaseModel):
    id: int
    title: str
    done: bool
    class Config:
        orm_mode = True

# ---------------- App --------------------
app = FastAPI(title="Todo API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

# ---- Auth ----
@app.post("/auth/register", status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=409, detail="Username already taken")
    db_user = User(username=user.username, hashed_password=hash_password(user.password))
    db.add(db_user); db.commit(); db.refresh(db_user)
    return {"id": db_user.id, "username": db_user.username}

@app.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me")
def me(current: User = Depends(get_current_user)):
    return {"id": current.id, "username": current.username}

# ---- Todos ----
@app.get("/todos", response_model=List[TodoOut])
def list_todos(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Todo).filter(Todo.owner_id == current.id).order_by(Todo.id.desc()).all()

@app.post("/todos", response_model=TodoOut, status_code=201)
def create_todo(payload: TodoCreate, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    todo = Todo(title=payload.title, owner_id=current.id)
    db.add(todo); db.commit(); db.refresh(todo)
    return todo

@app.get("/todos/{todo_id}", response_model=TodoOut)
def get_todo(todo_id: int, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == current.id).first()
    if not todo: raise HTTPException(status_code=404, detail="Not found")
    return todo

@app.patch("/todos/{todo_id}", response_model=TodoOut)
def update_todo(todo_id: int, done: Optional[bool] = None, title: Optional[str] = None,
                current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == current.id).first()
    if not todo: raise HTTPException(status_code=404, detail="Not found")
    if done is not None: todo.done = done
    if title is not None: todo.title = title
    db.commit(); db.refresh(todo)
    return todo

@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == current.id).first()
    if not todo: raise HTTPException(status_code=404, detail="Not found")
    db.delete(todo); db.commit()
    return None
