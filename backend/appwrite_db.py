import os
import bcrypt
from datetime import datetime
from dotenv import load_dotenv


from appwrite.client import Client
import os
from dotenv import load_dotenv
from appwrite.client import Client
from appwrite.services.account import Account
from appwrite.services.databases import Databases
from appwrite.query import Query
from appwrite.exception import AppwriteException
from appwrite.id import ID

# Load .env ONLY for local development
load_dotenv()

# ------------------ ENV VARIABLES ------------------
APPWRITE_ENDPOINT = os.getenv("APPWRITE_ENDPOINT")
APPWRITE_PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID")
APPWRITE_API_KEY = os.getenv("APPWRITE_API_KEY")

# ------------------ VALIDATION (IMPORTANT) ------------------
if not APPWRITE_ENDPOINT or not APPWRITE_PROJECT_ID or not APPWRITE_API_KEY:
    raise RuntimeError(
        "Missing Appwrite environment variables. "
        "Check Streamlit Secrets or .env file."
    )

# ------------------ CLIENT ------------------
client = Client()
client.set_endpoint(APPWRITE_ENDPOINT)
client.set_project(APPWRITE_PROJECT_ID)
client.set_key(APPWRITE_API_KEY)

account = Account(client)
databases = Databases(client)

# ------------------ CONFIG ------------------
DB_ID = "6956b49b002ccad37ae6"

USERS_COLLECTION = "users"
RESULTS_COLLECTION = "results"




def send_email_otp(email):
    try:
        # Create a temporary user ID
        user_id = ID.unique()

        account.create_email_token(
            user_id=user_id,
            email=email
        )

        # Return ONLY user_id (same as JS)
        return True, user_id

    except AppwriteException as e:
        return False, str(e)


def verify_email_otp(user_id, otp):
    try:
        # THIS is the correct OTP verification step
        account.create_session(
            user_id=user_id,
            secret=otp
        )

        return True, "OTP verified successfully"

    except AppwriteException:
        return False, "Invalid or expired OTP"


# =====================================================
# ================= USERS =============================
# =====================================================

# def register_user(username, password, role, email=None):
#     try:
#         existing = databases.list_documents(
#             database_id=DB_ID,
#             collection_id=USERS_COLLECTION,
#             queries=[Query.equal("username", username)]
#         )

#         if existing["total"] > 0:
#             return False, "Username already exists"

#         hashed_password = bcrypt.hashpw(
#             password.encode(), bcrypt.gensalt()
#         ).decode()

#         databases.create_document(
#             database_id=DB_ID,
#             collection_id=USERS_COLLECTION,
#             document_id="unique()",
#             data={
#                 "username": username,
#                 "password": hashed_password,
#                 "role": role,
#                 "email": email,
#                 "created_at": datetime.utcnow().isoformat()
#             }
#         )

#         return True, "User registered successfully"

#     except AppwriteException as e:
#         return False, str(e)


def register_user(username, password, role, email=None):
    try:
        existing = databases.list_documents(
            database_id=DB_ID,
            collection_id=USERS_COLLECTION,
            queries=[Query.equal("username", username)]
        )

        if existing["total"] > 0:
            return False, "Username already exists"

        hashed_password = bcrypt.hashpw(
            password.encode(), bcrypt.gensalt()
        ).decode()

        databases.create_document(
            database_id=DB_ID,
            collection_id=USERS_COLLECTION,
            document_id="unique()",
            data={
                "username": username,
                "password": hashed_password,
                "role": "Student",  # 🔒 Forced
                "email": email,
                "created_at": datetime.utcnow().isoformat()
            }
        )

        return True, "User registered successfully"

    except AppwriteException as e:
        return False, str(e)

def authenticate_user(username, password):
    try:
        response = databases.list_documents(
            database_id=DB_ID,
            collection_id=USERS_COLLECTION,
            queries=[Query.equal("username", username)]
        )

        print("DEBUG RESPONSE:", response)
        print("TYPE:", type(response))

        if not response or not isinstance(response, dict):
            return False, None, "Invalid response from Appwrite"

        if response.get("total", 0) == 0:
            return False, None, "Invalid username or password"

        user = response["documents"][0]

        if bcrypt.checkpw(password.encode(), user["password"].encode()):
            return True, user["role"], "Login successful"

        return False, None, "Invalid username or password"

    except Exception as e:
        print("ERROR:", e)
        return False, None, str(e)
        
# def authenticate_user(username, password):
#     try:
#         response = databases.list_documents(
#             database_id=DB_ID,
#             collection_id=USERS_COLLECTION,
#             queries=[Query.equal("username", username)]
#         )

#         if response["total"] == 0:
#             return False, None, "Invalid username or password"

#         user = response["documents"][0]

#         if bcrypt.checkpw(password.encode(), user["password"].encode()):
#             return True, user["role"], "Login successful"

#         return False, None, "Invalid username or password"

#     except AppwriteException as e:
#         return False, None, str(e)

# =====================================================
# ================= RESULTS ===========================
# =====================================================

def normalize_student(student):
    return {
        "seat_no": student.get("Seat No"),
        "name": student.get("Name"),
        "prn_no": student.get("PRN No"),
        "status": student.get("Status"),
        "percentage": student.get("Percentage"),
        "code": student.get("Code", []),
        "ua": student.get("UA", []),
        "ca": student.get("CA", []),
        "total": student.get("Total", []),
        "status1": student.get("Status1", []),

        # 🔥 REQUIRED METADATA
        "course": student.get("Course"),
        "year": str(student.get("Year")),
        "semester": student.get("Semester"),
        "academic_year": student.get("AcademicYear"),
        "exam_name": student.get("Exam"),
    }




def save_results(data):
    try:
        for student in data:
            row = normalize_student(student)

            if not row["seat_no"]:
                continue

            databases.create_document(
                database_id=DB_ID,
                collection_id=RESULTS_COLLECTION,
                document_id="unique()",
                data=row
            )
        return True

    except AppwriteException as e:
        print("Appwrite save error:", e)
        return False


# def save_results(data):
#     try:
#         for student in data:
#             row = normalize_student(student)

#             if not row["seat_no"]:
#                 continue

#             # 🔍 CHECK IF RECORD ALREADY EXISTS
#             existing = databases.list_documents(
#                 database_id=DB_ID,
#                 collection_id=RESULTS_COLLECTION,
#                 queries=[
#                     Query.equal("seat_no", row["seat_no"]),
#                     Query.equal("course", row["course"]),
#                     Query.equal("year", row["year"]),
#                     Query.equal("semester", row["semester"]),
#                     Query.equal("academic_year", row["academic_year"]),
#                 ]
#             )

#             # ❌ Skip if already present
#             if existing["total"] > 0:
#                 continue

#             # ✅ Insert only if NOT exists
#             databases.create_document(
#                 database_id=DB_ID,
#                 collection_id=RESULTS_COLLECTION,
#                 document_id="unique()",
#                 data=row
#             )

#         return True

#     except AppwriteException as e:
#         print("Appwrite save error:", e)
#         return False



# def load_results():
#     try:
#         response = databases.list_documents(
#             database_id=DB_ID,
#             collection_id=RESULTS_COLLECTION
#         )
#         return response["documents"]

#     except AppwriteException as e:
#         print("Appwrite load error:", e)
#         return []

def load_results():
    try:
        all_documents = []
        limit = 100  # max allowed
        offset = 0

        while True:
            response = databases.list_documents(
                database_id=DB_ID,
                collection_id=RESULTS_COLLECTION,
                queries=[
                    Query.limit(limit),
                    Query.offset(offset)
                ]
            )

            documents = response.get("documents", [])
            all_documents.extend(documents)

            if len(documents) < limit:
                break  # no more data

            offset += limit

        return all_documents

    except AppwriteException as e:
        print("Appwrite load error:", e)
        return []

# def get_short_results():
#     """
#     Returns minimal student data for dashboards & lists
#     """
#     documents = load_results()
#     short_data = []

#     for d in documents:
#         short_data.append({
#             "Seat No": str(d.get("seat_no", "")),
#             "Name": d.get("name", ""),
#             "Percentage": d.get("percentage", ""),
#             "Status": d.get("status", "")
#         })

#     return short_data

def get_short_results():
    documents = load_results()
    short_data = []

    for d in documents:
        short_data.append({
            "Seat No": str(d.get("seat_no", "")),
            "Name": d.get("name", ""),
            "Percentage": d.get("percentage", ""),
            "Status": d.get("status", ""),

            # 🔥 MATCH DB COLUMN NAMES EXACTLY
            "course": d.get("course", ""),
            "year": str(d.get("year", "")),
            "semester": d.get("semester", ""),
            "academic_year": d.get("academic_year", "")
        })

    return short_data



# def get_detailed_results():
#     """
#     Returns full subject-wise data
#     """
#     documents = load_results()
#     detailed_data = []

#     for d in documents:
#         detailed_data.append({
#             "Seat No": str(d.get("seat_no", "")),
#             "Name": d.get("name", ""),
#             "PRN No": d.get("prn_no", ""),
#             "Status": d.get("status", ""),
#             "Percentage": d.get("percentage", ""),
#             "Code": d.get("code", []) or [],
#             "UA": d.get("ua", []) or [],
#             "CA": d.get("ca", []) or [],
#             "Total": d.get("total", []) or [],
#             "Status1": d.get("status1", []) or []
#         })

#     return detailed_data

def get_detailed_results():
    documents = load_results()
    detailed_data = []

    for d in documents:
        detailed_data.append({
            # 🔹 Student identity
            "seat_no": str(d.get("seat_no", "")),
            "name": d.get("name", ""),
            "prn_no": d.get("prn_no", ""),
            "status": d.get("status", ""),
            "percentage": d.get("percentage", ""),

            # 🔹 Subject-wise data
            "code": d.get("code", []) or [],
            "ua": d.get("ua", []) or [],
            "ca": d.get("ca", []) or [],
            "total": d.get("total", []) or [],
            "status1": d.get("status1", []) or [],

            # 🔹 Metadata (EXACT DB COLUMN NAMES)
            "course": d.get("course", ""),
            "year": str(d.get("year", "")),
            "semester": d.get("semester", ""),
            "exam_name": d.get("exam_name", ""),
            "academic_year": d.get("academic_year", "")
        })

    return detailed_data

def delete_all_results():
    try:
        limit = 100
        offset = 0

        while True:
            response = databases.list_documents(
                database_id=DB_ID,
                collection_id=RESULTS_COLLECTION,
                queries=[
                    Query.limit(limit),
                    Query.offset(offset)
                ]
            )

            documents = response["documents"]

            if not documents:
                break

            for doc in documents:
                databases.delete_document(
                    database_id=DB_ID,
                    collection_id=RESULTS_COLLECTION,
                    document_id=doc["$id"]
                )

            # If fewer than limit, no more docs left
            if len(documents) < limit:
                break

        return True

    except Exception as e:
        print("Delete error:", e)
        return False
    

def data_exists(course, year, semester, academic_year):
    data = get_short_results()

    for d in data:
        if (
            d.get("course") == course and
            str(d.get("year")) == str(year) and
            d.get("semester") == semester and
            d.get("academic_year") == academic_year
        ):
            return True
    return False




