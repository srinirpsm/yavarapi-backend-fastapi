from fastapi import FastAPI
import models
from database import engine
from routes import auth,tasks    # Import the new router
from fastapi.middleware.cors import CORSMiddleware

# Run database migrations
models.Base.metadata.create_all(bind=engine)

# Initialize the FastAPI app
app = FastAPI()

# Allow requests from your frontend (React)
origins = [
    "http://localhost:3000",  # Your React app
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow only this origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include authentication routes
app.include_router(auth.router)
app.include_router(tasks.router)
