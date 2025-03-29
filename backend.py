<<<<<<< HEAD
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
=======
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import requests
setattr
from math import radians, sin, cos, sqrt, atan2
from pydantic import BaseModel
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
>>>>>>> 8508803798fa3accb75b0b5e56c17fca8141897c
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD
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
=======
# --- Configuration ---
CSV_PATH = r"C:\Users\xoxo3\OneDrive\Desktop\New folder\bloodbank\blood_banks.csv"  
GRAPHHOPPER_KEY = os.getenv("GRAPHHOPPER_API_KEY", "9e9f9e52-ce51-4f10-b4e4-f3fd74b63123")  # Defaults to empty string if not set

# Mapping from our model fields to the CSV column headers (after stripping)
col_mapping = {
    'id': 'Sr No',
    'name': 'Blood Bank Name',
    'address': 'Address',
    'city': 'City',
    'state': 'State',
    'latitude': 'latitude',
    'longitude': 'longitude'
}

class Location(BaseModel):
    latitude: float
    longitude: float

class BloodBank(BaseModel):
    id: str
    name: str
    address: str
    city: str
    state: str
    latitude: float
    longitude: float
    distance: float = None


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371 
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = (sin(dlat/2) ** 2 +
         cos(radians(lat1)) * cos(radians(lat2)) *
         sin(dlon/2) ** 2)
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

def load_blood_banks():
    try:
        logger.info(f"Attempting to load CSV from: {CSV_PATH}")
        if not os.path.exists(CSV_PATH):
            raise FileNotFoundError(f"CSV file not found at {CSV_PATH}")
        
        
        df = pd.read_csv(CSV_PATH, encoding="windows-1252")
        df.columns = df.columns.str.strip()
        logger.info(f"Successfully loaded CSV with {len(df)} records")
        
        
        missing_cols = [col for col in col_mapping.values() if col not in df.columns]
        if missing_cols:
            raise ValueError(f"CSV missing required columns: {', '.join(missing_cols)}")
        
        
        df['Address'] = df['Address'].fillna("")
        df['City'] = df['City'].fillna("")
        
        banks = []
        for _, row in df.iterrows():
            try:
                bank = BloodBank(
                    id=str(row[col_mapping['id']]),
                    name=row[col_mapping['name']],
                    address=row[col_mapping['address']],
                    city=row[col_mapping['city']],
                    state=row[col_mapping['state']],
                    latitude=float(row[col_mapping['latitude']]),
                    longitude=float(row[col_mapping['longitude']])
                )
                banks.append(bank)
            except Exception as inner_e:
                logger.warning(f"Skipping row due to error: {inner_e}")
        return banks
    except Exception as e:
        logger.error(f"Error loading blood banks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"CSV Error: {str(e)}")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Blood Bank API!"}


@app.post("/nearby")
async def get_nearby(location: Location):
    try:
        logger.info(f"Searching nearby blood banks for location: {location.latitude}, {location.longitude}")
        banks = load_blood_banks()
        for bank in banks:
            bank.distance = haversine(
                location.latitude,
                location.longitude,
                bank.latitude,
                bank.longitude
            )
       
        return sorted(banks, key=lambda x: x.distance)[:10]
    except Exception as e:
        logger.error(f"Error in nearby endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/all-blood-banks")
async def get_all_blood_banks():
    """Return all blood banks without distance calculation"""
    try:
        logger.info("Fetching all blood banks")
        return load_blood_banks()
    except Exception as e:
        logger.error(f"Error fetching all blood banks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/route")
async def get_route(start_lat: float, start_lon: float, end_lat: float, end_lon: float):
    try:
        logger.info(f"Getting route from ({start_lat},{start_lon}) to ({end_lat},{end_lon})")
        if not GRAPHHOPPER_KEY:
            logger.warning("Graphhopper API key not set")
            raise HTTPException(status_code=500, detail="Graphhopper API key not configured")
        
        url = "https://graphhopper.com/api/1/route"
        params = {
            "point": [f"{start_lat},{start_lon}", f"{end_lat},{end_lon}"],
            "vehicle": "car",
            "key": GRAPHHOPPER_KEY,
            "points_encoded": "false"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Graphhopper API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Routing API error: {str(e)}")
    except Exception as e:
        logger.error(f"Route calculation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)
>>>>>>> 8508803798fa3accb75b0b5e56c17fca8141897c
