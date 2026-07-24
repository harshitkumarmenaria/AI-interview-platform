from passlib.context import CryptContext
from pymongo.errors import DuplicateKeyError
from datetime import datetime
from db import users_col

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

def register_user(name: str, email: str, password: str):
    try:
        name = name.strip()
        email = email.strip().lower()
        password = password.strip()

        if not name or not email or not password:
            return {"success": False, "message": "All fields required"}

        hashed_pw = hash_password(password)

        users_col.insert_one({
            "name": name,
            "email": email,
            "password": hashed_pw,
            "created_at": datetime.utcnow()
        })

        print("✅ User inserted into MongoDB")

        return {"success": True}

    except DuplicateKeyError:
        return {"success": False, "message": "User already exists"}

    except Exception as e:
        print("REGISTER ERROR:", e)
        return {"success": False, "message": "Registration failed"}

def login_user(email: str, password: str):
    try:
        email = email.strip().lower()
        password = password.strip()

        user = users_col.find_one({"email": email})

        if not user:
            return {"success": False, "message": "Invalid email or password"}

        if not verify_password(password, user["password"]):
            return {"success": False, "message": "Invalid email or password"}

        return {
            "success": True,
            "user_id": str(user["_id"]),
            "name": user["name"]
        }

    except Exception as e:
        print("LOGIN ERROR:", e)
        return {"success": False, "message": "Login failed"}
