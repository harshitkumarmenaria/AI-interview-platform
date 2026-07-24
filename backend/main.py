from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId
import shutil
import os

# Database collections
from db import (
    users_col,
    resume_results_col,
    interview_results_col
)

# AI logic
from resume_ai import analyze_resume
from interview_ai import evaluate_interview

# Auth logic
from auth import register_user, login_user

app = FastAPI(title="AI Interview Platform")

# -------------------------
# CORS
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Models
# -------------------------
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class InterviewRequest(BaseModel):
    user_id: str
    answer: str


# -------------------------
# Health
# -------------------------
@app.get("/")
def home():
    return {"status": "Backend running successfully"}


# -------------------------
# Auth
# -------------------------
@app.post("/register")
def register(data: RegisterRequest):
    return register_user(
        name=data.name,
        email=data.email,
        password=data.password
    )


@app.post("/login")
def login(data: LoginRequest):
    return login_user(
        email=data.email,
        password=data.password
    )


# -------------------------
# Resume Upload
# -------------------------
@app.post("/upload-resume/")
async def upload_resume(
    user_id: str = Query(...),
    file: UploadFile = File(...)
):
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user_id")

        # Validate file type
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files allowed")

        temp_file_path = f"temp_{ObjectId()}.pdf"

        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        score = analyze_resume(temp_file_path)

        os.remove(temp_file_path)

        resume_results_col.insert_one({
            "user_id": ObjectId(user_id),
            "filename": file.filename,
            "score": score,
            "uploaded_at": datetime.utcnow()
        })

        return {"resume_score": score}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------
# Interview
# -------------------------
@app.post("/interview/")
def interview(data: InterviewRequest):
    try:
        if not ObjectId.is_valid(data.user_id):
            raise HTTPException(status_code=400, detail="Invalid user_id")

        score = evaluate_interview(data.answer)

        interview_results_col.insert_one({
            "user_id": ObjectId(data.user_id),
            "answer": data.answer,
            "score": score,
            "submitted_at": datetime.utcnow()
        })

        return {"interview_score": score}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------
# Dashboard
# -------------------------
@app.get("/dashboard/{user_id}")
def dashboard(user_id: str):
    try:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user_id")

        uid = ObjectId(user_id)

        # Fetch user (exclude password)
        user = users_col.find_one(
            {"_id": uid},
            {"password": 0}
        )

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Latest resume
        resume = resume_results_col.find_one(
            {"user_id": uid},
            sort=[("uploaded_at", -1)]
        )

        # Latest interview
        interview = interview_results_col.find_one(
            {"user_id": uid},
            sort=[("submitted_at", -1)]
        )

        resume_score = resume["score"] if resume else 0
        interview_score = interview["score"] if interview else 0

        final_score = int((resume_score * 0.4) + (interview_score * 0.6))

        if final_score >= 80:
            verdict = "Strong Hire"
        elif final_score >= 60:
            verdict = "Hire"
        elif final_score >= 40:
            verdict = "Needs Improvement"
        else:
            verdict = "Reject"

        return {
            "name": user["name"],
            "email": user["email"],
            "resume_score": resume_score,
            "interview_score": interview_score,
            "final_score": final_score,
            "verdict": verdict
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
