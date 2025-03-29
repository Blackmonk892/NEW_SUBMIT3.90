from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Field, SQLModel, Session, create_engine, select, Column, JSON
from typing import Optional, List
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Secret key for JWT token
SECRET_KEY = "73167eb211a19310e39d3a97cd63fe0f69e4e74f69bf6b7611e773ce137b9da3"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# SQLite DB
engine = create_engine("sqlite:///donors.db")

# -------------------------
# Database Models
# -------------------------

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    username: str
    hashed_password: str
    hearts: int = 0
    donations: int = 0
    messages: List[str] = Field(default_factory=list, sa_column=Column(JSON))

class Campaign(SQLModel):
    name: str
    location: str
    time: str
    status: str

# -------------------------
# Utility Functions
# -------------------------

def create_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user_by_username(username, session):
    return session.exec(select(User).where(User.username == username)).first()

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = get_user_by_username(username, session)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# -------------------------
# API Endpoints
# -------------------------

@app.post("/register")
def register(email: str, username: str, password: str, session: Session = Depends(get_session)):
    if get_user_by_username(username, session):
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(email=email, username=username, hashed_password=hash_password(password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "User registered"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = get_user_by_username(form_data.username, session)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/profile")
def profile(user: User = Depends(get_current_user)):
    return {
        "username": user.username,
        "email": user.email,
        "hearts": user.hearts,
        "donations": user.donations,
        "messages": user.messages,
    }

@app.post("/donate")
def donate(message: str = "Thanks for donating!", user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    user.donations += 1
    user.hearts += 1
    user.messages.append(message)
    session.add(user)
    session.commit()
    return {"message": "Donation successful! ❤️", "hearts": user.hearts}

@app.get("/leaderboard")
def leaderboard(session: Session = Depends(get_session)):
    users = session.exec(select(User).order_by(User.hearts.desc())).all()
    return [{"username": u.username, "hearts": u.hearts, "donations": u.donations} for u in users[:10]]

@app.get("/campaigns")
def campaigns():
    dummy = [
        {"name": "Blood Drive A", "location": "City Hospital", "time": "10 AM - 4 PM", "status": "Ongoing"},
        {"name": "Red Cross Event", "location": "Town Hall", "time": "Tomorrow 9 AM", "status": "Upcoming"},
    ]
    return dummy

@app.get("/rewards")
def rewards(user: User = Depends(get_current_user)):
    rewards = []
    if user.donations >= 1:
        rewards.append("🩸 First Drop Badge")
    if user.donations >= 5:
        rewards.append("☕ Starbucks Donor Badge")
    if user.donations >= 10:
        rewards.append("🎖️ Community Hero Title")
    return rewards

@app.on_event("startup")
def on_start():
    create_db()
