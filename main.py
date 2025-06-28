from models import UserModel, FileModel, FileFiltersModel, InsertUserFileModel
from MongoDB.database import (
    user_authenticate, 
    insert_user, 
    insert_user_file, 
    get_user_files, 
    update_user_file,
    check_mongodb_connection
)
from constants import UPLOAD_DIR, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REMEMBER_ACCESS_TOKEN_EXPIRE_MINUTES
from Validations.validate_forms import validation_functions
from Text_extraction.extract_data import document_classification, extract_json

from fastapi import FastAPI, File, UploadFile, HTTPException, status, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import JWTError, jwt

from typing import List, Optional
from datetime import datetime, timedelta
from uuid import uuid4

import hashlib
import uvicorn
import os

from dotenv import load_dotenv
load_dotenv()


os.makedirs(UPLOAD_DIR, exist_ok=True)


check_mongodb_connection()


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
api_key_header = APIKeyHeader(name="Authorization")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to ["http://localhost:8080"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# JWT Authentication
auth_header = APIKeyHeader(name="Authorization")


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT token with an expiration.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "token_type": "bearer"
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Get current user dependency
def get_current_user(token: str = Security(auth_header)) -> str:
    """
    Validates JWT from Authorization header and extracts user ID.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    print(token)
    jwt_token = token
    try:
        payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return user_id



@app.post("/login")
async def login(user_name: str, password: str, remember_me: bool) -> dict:
    hashed_password = hash_password(password)
    print(user_name, hashed_password)
    user = user_authenticate(user_name, hashed_password)
    print(user)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    data={"sub": user["user_data"]["user_id"]}
    access_token = create_access_token(data)
    if remember_me:
        access_token = create_access_token(data, timedelta(minutes=REMEMBER_ACCESS_TOKEN_EXPIRE_MINUTES))

    return {
        "status": "success",
        "user_data": {"user_id": user["user_data"]["user_id"], "name": user["user_data"]["name"], "email": user["user_data"]["email"]},
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.post("/register")
async def register(user_data: UserModel) -> dict:
    user_data.password = hash_password(user_data.password)
    return insert_user(user_data)


@app.post("/upload_files")
async def upload_files(
    user_id: str = Security(get_current_user),
    files: List[UploadFile] = File(default=[])
) -> dict:
    if not files:
        return {"error": "No files uploaded."}
    
    os.makedirs(os.path.join(UPLOAD_DIR, user_id), exist_ok=True)

    user_data = {
        "user_id": user_id,
        "files": []
    }

    try:
        for file in files:
            file_location = os.path.join(UPLOAD_DIR, user_id, file.filename)
            content = await file.read()

            with open(file_location, "wb") as f:
                f.write(content)

            # extracted_text = await get_file_content(file_location)
            document_classification_result = await document_classification(file_location)
            
            document_type = document_classification_result.get("document_type")
            print(document_type)

            if not document_type:
                # return {"status": "partial success", "error": "Document type could not be classified."}
                extracted_text = document_classification_result.get("extracted_text", "")
            else:
                extracted_text = await extract_json(
                                    file_location, 
                                    document_type
                                )
                valid = validation_functions[document_type](extracted_text)
            
                extracted_text["document_status"] = valid["document_status"]
                issues = valid["issues"]
                print(issues)


            file_data = {
                "file_id": uuid4().hex,
                "upload_date": datetime.now().strftime("%d %m %Y %H:%M:%S"),
                "filename": file.filename,
                "file_path": file_location,
                "document_type": document_type,
                "extracted_text": extracted_text if extracted_text else {},
                "content_type": file.content_type
            }
            user_data["files"].append(file_data)

        result = insert_user_file(user_data)
        return {"status": "success", "extracted_data": user_data}
    
    except Exception as e:
        print(f"Error uploading files: {e}")
        return {"status": "error", "error": "Failed to upload files."}


@app.post("/re_analyze_file")
async def re_analyze_file(file_id: str, document_type: str, user_id: str = Security(get_current_user)) -> dict:
    file_data = get_user_files(user_id, {"file_id": file_id})
    print(file_data)
    if not file_data:
        return {"error": "File not found."}

    file_path = file_data[0]["file_path"]
    extracted_text = await extract_json(file_path, document_type)
    
    valid = validation_functions[document_type](extracted_text)
            
    extracted_text["document_status"] = valid["document_status"]
    issues = valid["issues"]
    print(issues)
    if not extracted_text:
        return {"error": "Failed to extract text from the file."}
    
    response_data = FileModel(file_id=file_id, upload_date=file_data[0]["upload_date"],
                              filename=file_data[0]["filename"], file_path=file_data[0]["file_path"],
                              document_type=document_type, extracted_text=extracted_text,
                              content_type=file_data[0]["content_type"])
    
    user_data = {
        "user_id": user_id,
        "files": [response_data.model_dump()]
    }
    return {"status": "success", "extracted_data": user_data}


@app.post("/update_file_data")
async def update_file_data(file_data: InsertUserFileModel, user_id: str = Security(get_current_user)) -> dict:
    if not file_data.user_id or not file_data.files:
        return {"error": "Invalid data provided."}
    
    total_data = file_data.model_dump()
    
    result = update_user_file(user_id, total_data["files"][0]["file_id"], total_data["files"][0])
    if result:
        return {"status": "success", "message": "File data updated successfully."}
    
    return {"error": "Failed to update file data."}


@app.post("/get_files")
async def get_files(user_id: str = Security(get_current_user), filters: FileFiltersModel | None = None) -> List[dict] | dict:
    if filters:
        return get_user_files(user_id, filters.model_dump())
    
    return get_user_files(user_id)



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)