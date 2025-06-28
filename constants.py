import os


UPLOAD_DIR = "uploads"

# Replace with your actual MongoDB Atlas connection string
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "mydatabase")
USER_COLLECTION_NAME = os.environ.get("USER_COLLECTION_NAME", "users")
DATA_COLLECTION_NAME = os.environ.get("DATA_COLLECTION_NAME", "documents_data")

# Secret key for JWT
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REMEMBER_ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours
