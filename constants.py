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


OFFICE_KEYWORDS = [
    "Police", "Battalion", "Office", "Unit", "Division", "Commandant", "Commissioner", 
    "Range", "Headquarters", "HQ", "Department", "Branch", "Zone"
]

SECTION_CODES = set(["A1", "A2", "A3", "A4", "A5", "B1", "B2", "B3", "B4", "B5", 
                     "C1", "C2", "C3", "C4", "C5", "D1", "D2", "D3", "D4", "D5",
                     "E1", "E2", "E3", "E4", "E5", "E6", "F1", "F2", "F3", "F4", "F5"])

LIST_OF_RANKS = {
    "PC": "Police Constable",
    "HC": "Head Constable",
    "ASI": "Assistant Sub Inspector",
    "SI": "Sub Inspector", 
    "CI": "Circle Inspector",
    "RI": "Reserved Inspector",
    "RSI": "Reserved Sub Inspector",
    "ARSI": "Armed Reserved Sub Inspector",
    "DSP": "Deputy Superintendent of Police",
    "ACP": "Assistant Commissioner of Police",
    "ASP": "Assistant Superintendent of Police",
    "Addl. SP": "Additional Superintendent of Police",
    "SP": "Superintendent of Police",
    "DIG": "Deputy Inspector General of Police",
    "IGP": "Inspector General of Police",
    "ADGP": "Additional Director General of Police",
    "DGP": "Director General of Police"
}

LIST_OF_COYS = set([
    "A Coy",
    "B Coy",
    "C Coy",
    "D Coy",
    "E Coy",
    "F Coy",
    "HQ Coy",
    "QRT Coy",
    "RI Coy"
])

LIST_OF_UNITS_DISTRICTS = {
"1st": "Srikakulam",
"2nd": "Kurnool",
"3rd": "Kakinada",
"4th": "Rajamahendm",
"5th": "Vizianagar",
"6th": "Mangalagir",
"7th": "Ongole",
"8th": "Chittoor",
"9th": "Venkatagir",
"11th": "Kadapa",
"14th": "Ananthapur",
"16th": "Vishakapat"
}