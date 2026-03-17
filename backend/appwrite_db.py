import os
import bcrypt
from datetime import datetime
from dotenv import load_dotenv

from appwrite.client import Client
from appwrite.services.account import Account
from appwrite.services.databases import Databases
from appwrite.query import Query
from appwrite.exception import AppwriteException
from appwrite.id import ID

# ------------------ LOAD ENV ------------------
load_dotenv()

APPWRITE_ENDPOINT = os.getenv("APPWRITE_ENDPOINT")
APPWRITE_PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID")
APPWRITE_API_KEY = os.getenv("APPWRITE_API_KEY")

if not APPWRITE_ENDPOINT or not APPWRITE_PROJECT_ID or not APPWRITE_API_KEY:
    raise RuntimeError("Missing Appwrite environment variables")

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

# =====================================================
# ================= OTP ================================
# =====================================================

def send_email_otp(email):
    try:
        user_id = ID.unique()
        account.create_email_token(user_id=user_id, email=email)
        return True, user_id
    except AppwriteException as e:
        return False, str(e)


def verify_email_otp(user_id, otp):
    try:
        account.create_session(user_id=user_id, secret=otp)
        return True, "OTP verified successfully"
    except AppwriteException:
        return False, "Invalid or expired OTP"

# =====================================================
# ================= USERS ==============================
# =====================================================

def register_user(username, password, role, email=None):
    try:
        existing = databases.list_documents(
            database_id=DB_ID,
            collection_id=USERS_COLLECTION,
            queries=[Query.equal("username", username)]
        )

        if existing.total > 0:
            return False, "Username already exists"

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        databases.create_document(
            database_id=DB_ID,
            collection_id=USERS_COLLECTION,
            document_id=ID.unique(),
            data={
                "username": username,
                "password": hashed_password,
                "role": "Student",
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

        if response.total == 0:
            return False, None, "Invalid username or password"

        user = response.documents[0]

        # ✅ FIXED HERE
        if bcrypt.checkpw(password.encode(), user.data["password"].encode()):
            return True, user.data["role"], "Login successful"

        return False, None, "Invalid username or password"

    except Exception as e:
        print("ERROR:", e)
        return False, None, str(e)

# =====================================================
# ================= RESULTS ============================
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
                document_id=ID.unique(),
                data=row
            )
        return True

    except AppwriteException as e:
        print("Appwrite save error:", e)
        return False


def load_results():
    try:
        all_documents = []
        limit = 100
        offset = 0

        while True:
            response = databases.list_documents(
                database_id=DB_ID,
                collection_id=RESULTS_COLLECTION,
                queries=[Query.limit(limit), Query.offset(offset)]
            )

            documents = response.documents
            all_documents.extend(documents)

            if len(documents) < limit:
                break

            offset += limit

        return all_documents

    except AppwriteException as e:
        print("Appwrite load error:", e)
        return []


# def get_short_results():
#     documents = load_results()
#     short_data = []

#     for d in documents:
#         short_data.append({
#             "Seat No": str(d["seat_no"] if "seat_no" in d else ""),
#             "Name": d["name"] if "name" in d else "",
#             "Percentage": d["percentage"] if "percentage" in d else "",
#             "Status": d["status"] if "status" in d else "",
#             "course": d["course"] if "course" in d else "",
#             "year": str(d["year"] if "year" in d else ""),
#             "semester": d["semester"] if "semester" in d else "",
#             "academic_year": d["academic_year"] if "academic_year" in d else ""
#         })

#     return short_data

# def get_short_results(course=None, year=None, semester=None, academic_year=None):
#     documents = load_results()
#     short_data = []

#     for d in documents:
#         try:
#             # ✅ APPLY FILTER ONLY IF VALUES PROVIDED
#             if course and d["course"] != course:
#                 continue
#             if year and str(d["year"]) != str(year):
#                 continue
#             if semester and d["semester"] != semester:
#                 continue
#             if academic_year and d["academic_year"] != academic_year:
#                 continue

#             short_data.append({
#                 "Seat No": str(d["seat_no"]) if "seat_no" in d else "",
#                 "Name": d["name"] if "name" in d else "",
#                 "Percentage": d["percentage"] if "percentage" in d else "",
#                 "Status": d["status"] if "status" in d else "",

#                 "course": d["course"] if "course" in d else "",
#                 "year": str(d["year"]) if "year" in d else "",
#                 "semester": d["semester"] if "semester" in d else "",
#                 "academic_year": d["academic_year"] if "academic_year" in d else ""
#             })

#         except Exception:
#             continue

#     return short_data



def get_short_results(course=None, year=None, semester=None, academic_year=None):
    documents = load_results()
    short_data = []

    for d in documents:
        try:
            # ✅ APPLY FILTER ONLY IF VALUES PROVIDED
            # Fix: Check if parameter is not None AND not empty string
            if course and course.strip() and d.get("course") != course:
                continue
            if year is not None and year != "" and str(d.get("year", "")) != str(year):
                continue
            if semester and semester.strip() and d.get("semester") != semester:
                continue
            if academic_year and academic_year.strip() and d.get("academic_year") != academic_year:
                continue

            short_data.append({
                "Seat No": str(d.get("seat_no", "")),
                "Name": d.get("name", ""),
                "Percentage": d.get("percentage", ""),
                "Status": d.get("status", ""),
                "course": d.get("course", ""),
                "year": str(d.get("year", "")),
                "semester": d.get("semester", ""),
                "academic_year": d.get("academic_year", "")
            })

        except Exception as e:
            print(f"Error processing document: {e}")
            continue

    return short_data


def get_detailed_results(course=None, year=None, semester=None, academic_year=None):
    documents = load_results()
    detailed_data = []

    for d in documents:
        try:
            # ✅ APPLY FILTER IF PROVIDED
            if course and course.strip() and d.get("course") != course:
                continue
            if year is not None and year != "" and str(d.get("year", "")) != str(year):
                continue
            if semester and semester.strip() and d.get("semester") != semester:
                continue
            if academic_year and academic_year.strip() and d.get("academic_year") != academic_year:
                continue

            detailed_data.append({
                "seat_no": str(d.get("seat_no", "")),
                "name": d.get("name", ""),
                "prn_no": d.get("prn_no", ""),
                "status": d.get("status", ""),
                "percentage": d.get("percentage", ""),
                "code": d.get("code", []) or [],
                "ua": d.get("ua", []) or [],
                "ca": d.get("ca", []) or [],
                "total": d.get("total", []) or [],
                "status1": d.get("status1", []) or [],
                "course": d.get("course", ""),
                "year": str(d.get("year", "")),
                "semester": d.get("semester", ""),
                "exam_name": d.get("exam_name", ""),
                "academic_year": d.get("academic_year", "")
            })

        except Exception as e:
            print(f"Error processing document: {e}")
            continue

    return detailed_data
# def get_detailed_results():
#     documents = load_results()
#     detailed_data = []

#     for d in documents:
#         detailed_data.append({
#             "seat_no": str(d.get("seat_no", "")),
#             "name": d.get("name", ""),
#             "prn_no": d.get("prn_no", ""),
#             "status": d.get("status", ""),
#             "percentage": d.get("percentage", ""),
#             "code": d.get("code", []) or [],
#             "ua": d.get("ua", []) or [],
#             "ca": d.get("ca", []) or [],
#             "total": d.get("total", []) or [],
#             "status1": d.get("status1", []) or [],
#             "course": d.get("course", ""),
#             "year": str(d.get("year", "")),
#             "semester": d.get("semester", ""),
#             "exam_name": d.get("exam_name", ""),
#             "academic_year": d.get("academic_year", "")
#         })

#     return detailed_data

# def get_detailed_results():
#     documents = load_results()
#     detailed_data = []

#     for d in documents:
#         detailed_data.append({
#             "seat_no": str(d["seat_no"]) if "seat_no" in d else "",
#             "name": d["name"] if "name" in d else "",
#             "prn_no": d["prn_no"] if "prn_no" in d else "",
#             "status": d["status"] if "status" in d else "",
#             "percentage": d["percentage"] if "percentage" in d else "",

#             "code": d["code"] if "code" in d else [],
#             "ua": d["ua"] if "ua" in d else [],
#             "ca": d["ca"] if "ca" in d else [],
#             "total": d["total"] if "total" in d else [],
#             "status1": d["status1"] if "status1" in d else [],

#             "course": d["course"] if "course" in d else "",
#             "year": str(d["year"]) if "year" in d else "",
#             "semester": d["semester"] if "semester" in d else "",
#             "exam_name": d["exam_name"] if "exam_name" in d else "",
#             "academic_year": d["academic_year"] if "academic_year" in d else ""
#         })

#     return detailed_data
    

def delete_all_results():
    try:
        while True:
            response = databases.list_documents(
                database_id=DB_ID,
                collection_id=RESULTS_COLLECTION,
                queries=[Query.limit(100)]
            )

            documents = response.documents

            if not documents:
                break

            for doc in documents:
                databases.delete_document(
                    database_id=DB_ID,
                    collection_id=RESULTS_COLLECTION,
                    document_id=doc["$id"]
                )

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
