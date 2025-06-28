from models import UserModel, InsertUserFileModel, FileFiltersModel
from constants import MONGODB_URI, DATABASE_NAME, USER_COLLECTION_NAME, DATA_COLLECTION_NAME
from pymongo import MongoClient
from bson.binary import Binary
from uuid import uuid4
from dotenv import load_dotenv
load_dotenv()

import os


# Replace with your actual MongoDB Atlas connection string
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "mydatabase")
USER_COLLECTION_NAME = os.environ.get("USER_COLLECTION_NAME", "users")
DATA_COLLECTION_NAME = os.environ.get("DATA_COLLECTION_NAME", "documents_data")

file_keys = set([
    "file_id",
    "upload_date",
    "filename",
    "file_path",
    "template_type",
    "extracted_text",
    "content_type"
])


def check_mongodb_connection():
    """
    Checks if the MongoDB connection is successful.
    :return: True if connection is successful, False otherwise.
    """
    try:
        with MongoClient(MONGODB_URI) as client:
            client.admin.command('ping')
        return True
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        return False



def user_exists(user_id: str) -> bool:
    with MongoClient(MONGODB_URI) as client:
        db = client[DATABASE_NAME]
        users_collection = db[USER_COLLECTION_NAME]
        user = users_collection.find_one({"user_id": user_id.strip()})
        if user:
            return True
        return False


def user_authenticate(user_name: str, password: str) -> dict:
    """
    Authenticates a user against the MongoDB collection.
    :param user_name: Username of the user.
    :param password: Password of the user.
    :return: Dictionary containing authentication status and user data if authenticated.
    """
    with MongoClient(MONGODB_URI) as client:
        db = client[DATABASE_NAME]
        users_collection = db[USER_COLLECTION_NAME]
        user = users_collection.find_one({"name": user_name.strip(), "password": password.strip()})

        if user:
            return {"status": "success", "user_data": {"user_id": user["user_id"], "name": user["name"], "email": user["email"]}}
        else:
            return {"status": "error", "message": "Invalid username or password"}


def insert_user(user_data: UserModel) -> dict:
    """
    Inserts a new user into the MongoDB collection.
    :param user_data: Dictionary containing user data to be inserted.
    :return: Dictionary containing the status of the operation and user ID if successful.
    """
    user_id = uuid4().hex  # Generate a unique user ID
    name = user_data.name
    email = user_data.email
    password = user_data.password
    phone = user_data.phone

    try:
        with MongoClient(MONGODB_URI) as client:
            db = client[DATABASE_NAME]
            users_collection = db[USER_COLLECTION_NAME]

            # Insert new user
            users_collection.insert_one({
                "user_id": user_id.strip(),
                "name": name.strip(),
                "email": email.strip(),
                "password": password.strip(),
                "phone": phone.strip()
            })
    except Exception as e:
        print(f"Error inserting user: {e}")
        return {"status": "error", "message": "Database error occurred"}
    
    return {"status": "success", "user_id": user_id}


def insert_user_file(user_data: InsertUserFileModel) -> dict:
    """
    Inserts user data into the MongoDB collection.
    :param user_data: Dictionary containing user data to be inserted.
    """
    user_id = user_data.get("user_id")
    files = user_data.get("files", [])

    try:
        with MongoClient(MONGODB_URI) as client:
            db = client[DATABASE_NAME]
            data_collection = db[DATA_COLLECTION_NAME]

            for file in files:
                file_record = {
                    "user_id": user_id,
                    **file
                }
                data_collection.insert_one(file_record)
    except Exception as e:
        print(f"Error inserting user data: {e}")
        return {"status": "error", "message": str(e)}
    
    return {
        "status": "success",
        "user_id": user_id,
        "files_inserted": len(files)
    }


def update_user_file(user_id: str, file_id: str, update_data: dict) -> dict:
    """
    Updates user data in the MongoDB collection.
    :param user_id: ID of the user whose data is to be updated.
    :param file_id: ID of the file to be updated.
    :param update_data: Dictionary containing the fields to be updated.
    :return: Dictionary containing the status of the operation.
    """
    try:
        with MongoClient(MONGODB_URI) as client:
            db = client[DATABASE_NAME]
            data_collection = db[DATA_COLLECTION_NAME]

            result = data_collection.update_one(
                {"user_id": user_id.strip(), "file_id": file_id.strip()},
                {"$set": update_data}
            )

            if result.modified_count > 0:
                return {"status": "success", "message": "Data updated successfully"}
            else:
                return {"status": "error", "message": "No matching record found or no changes made"}
    except Exception as e:
        print(f"Error updating user data: {e}")
        return {"status": "error", "message": str(e)}


def get_user_files(user_id: str, filters: FileFiltersModel = None) -> list[dict] | dict:
    """
    Retrieves files for a specific user from the MongoDB collection.
    :param user_id: ID of the user whose files are to be retrieved.
    :param filters: Optional filters to apply to the file retrieval.
    :return: List of files associated with the user.
    """
    try:
        with MongoClient(MONGODB_URI) as client:
            db = client[DATABASE_NAME]
            data_collection = db[DATA_COLLECTION_NAME]

            query = {"user_id": user_id.strip()}
            if filters:
                for filter_key in filters:
                    if filter_key in file_keys and filters[filter_key].strip():
                        query[filter_key] = filters[filter_key].strip() if isinstance(filters[filter_key], str) else filters[filter_key]

            files = list(data_collection.find(query, {"file_id": 1, "upload_date": 1, "filename": 1, "template_type":1, "_id": 0}))
            return files
    except Exception as e:
        print(f"Error retrieving user files: {e}")
        return {"status": "error", "message": str(e)}