# import streamlit as st
# import pdfplumber
# import pandas as pd
# import re
# from io import BytesIO

# # ✅ Appwrite backend import (MongoDB removed)
# from backend.appwrite_db import save_results
# from backend.appwrite_db import get_short_results, get_detailed_results


# def normalize_student(student):
#     return {
#         "seat_no": student.get("Seat No"),
#         "name": student.get("Name"),
#         "prn_no": student.get("PRN No"),
#         "status": student.get("Status"),
#         "percentage": student.get("Percentage"),
#         "code": student.get("Code", []),
#         "ua": student.get("UA", []),
#         "ca": student.get("CA", []),
#         "total": student.get("Total", []),
#         "status1": student.get("Status1", []),
#     }


# def extract_student_data_from_bytes(pdf_bytes):
#     student_info_all_with_marks = []

#     try:
#         with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
#             for page in pdf.pages[4:]:
#                 text = page.extract_text()
#                 if not text:
#                     continue

#                 lines = text.split("\n")

#                 seat_indices = [
#                     i for i, line in enumerate(lines)
#                     if "Seat No:" in line
#                 ]

#                 if not seat_indices:
#                     continue

#                 seat_indices.append(len(lines))

#                 for i in range(len(seat_indices) - 1):
#                     seat_idx = seat_indices[i]
#                     block = lines[seat_idx:seat_indices[i + 1]]

#                     college_text = ""
#                     upper_limit = seat_indices[i - 1] if i > 0 else 0

#                     for j in range(seat_idx - 1, upper_limit - 1, -1):
#                         college_text += " " + lines[j]
#                         if "College Code:" in lines[j]:
#                             break

#                     if not (
#                         re.search(r"Sangola\s+College\s*,\s*Sangola", college_text, re.IGNORECASE)
#                         or re.search(r"College\s*Code\s*:\s*SANG\b", college_text, re.IGNORECASE)
#                     ):
#                         continue

#                     student_info = {}
#                     subjects = []

#                     for line in block:
#                         if "Seat No:" in line:
#                             m = re.search(r"Seat No:\s*(\d+)", line)
#                             if m:
#                                 student_info["Seat No"] = m.group(1)

#                         if re.match(r"^\d+\.\s+[A-Z\s]+$", line.strip()):
#                             student_info["Name"] = line.split(".", 1)[1].strip()

#                         if "PRN No." in line:
#                             student_info["PRN No"] = line.split("PRN No.")[-1].split()[0]

#                         if "Status:" in line:
#                             student_info["Status"] = line.split("Status:")[-1].split()[0]

#                         if "Percentage:" in line:
#                             student_info["Percentage"] = (
#                                 line.split("Percentage:")[-1].split("%")[0].strip()
#                             )

#                         if re.match(r"^ECS\d+", line):
#                             parts = line.split()
#                             try:
#                                 subjects.append({
#                                     "Code": parts[0],
#                                     "UA": parts[3],
#                                     "CA": parts[5],
#                                     "Total": parts[8],
#                                     "Status1": parts[-2],
#                                 })
#                             except IndexError:
#                                 continue

#                     if student_info and subjects:
#                         df = pd.DataFrame(subjects)
#                         student_info.update({
#                             "Code": df["Code"].tolist(),
#                             "UA": df["UA"].tolist(),
#                             "CA": df["CA"].tolist(),
#                             "Total": df["Total"].tolist(),
#                             "Status1": df["Status1"].tolist(),
#                         })

#                         student_info_all_with_marks.append(student_info)

#     except Exception as e:
#         st.error(f"Error processing PDF: {e}")
#         return None

#     return student_info_all_with_marks


# def store_data(uploaded_file):
#     if uploaded_file is None:
#         st.warning("Please upload a PDF file first.")
#         return

#     with st.spinner("Processing PDF..."):
#         student_info = extract_student_data_from_bytes(uploaded_file.getvalue())

#         if not student_info:
#             st.error("No student data found in the PDF.")
#             return

#         short_data = [
#             {
#                 "Seat No": r['Seat No'],
#                 "Name": r['Name'],
#                 "Percentage": r['Percentage'],
#                 "Status": r['Status']
#             }
#             for r in student_info
#         ]

#         # Session state (UNCHANGED)
#         st.session_state.stored_data['Result_dict'] = student_info
#         st.session_state.stored_data['Short_data'] = short_data

#         # ✅ FIX: Normalize before saving
#         normalized_data = [normalize_student(s) for s in student_info]

#         success = save_results(student_info)

#         if success:
#             st.success("✅ All data saved successfully to Appwrite database!")
#         else:
#             st.error("❌ Failed to save data to database")

#         st.subheader("Sample Data")
#         st.dataframe(pd.DataFrame(short_data).head())



# def show():
#     if st.session_state.user_type != "Admin":
#         st.error("You need to be an administrator to access this page.")
#         return

#     st.header("📤 Upload Result PDF")
#     uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

#     if st.button("Process PDF"):
#         store_data(uploaded_file)


import streamlit as st
import pdfplumber
import pandas as pd
import re
from io import BytesIO

# ✅ Appwrite backend import (MongoDB removed)
from backend.appwrite_db import save_results, data_exists
from backend.appwrite_db import get_short_results, get_detailed_results


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
    }


def extract_student_data_from_bytes(
    pdf_bytes,
    course,
    year,
    semester,
    exam_name,
    academic_year
):
    student_info_all_with_marks = []

    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages[4:]:
                text = page.extract_text()
                if not text:
                    continue

                lines = text.split("\n")

                seat_indices = [
                    i for i, line in enumerate(lines)
                    if "Seat No:" in line
                ]

                if not seat_indices:
                    continue

                seat_indices.append(len(lines))

                for i in range(len(seat_indices) - 1):
                    seat_idx = seat_indices[i]
                    block = lines[seat_idx:seat_indices[i + 1]]

                    college_text = ""
                    upper_limit = seat_indices[i - 1] if i > 0 else 0

                    for j in range(seat_idx - 1, upper_limit - 1, -1):
                        college_text += " " + lines[j]
                        if "College Code:" in lines[j]:
                            break

                    if not (
                        re.search(r"Sangola\s+College\s*,\s*Sangola", college_text, re.IGNORECASE)
                        or re.search(r"College\s*Code\s*:\s*SANG\b", college_text, re.IGNORECASE)
                    ):
                        continue

                    student_info = {}
                    subjects = []

                    for line in block:
                        if "Seat No:" in line:
                            m = re.search(r"Seat No:\s*(\d+)", line)
                            if m:
                                student_info["Seat No"] = m.group(1)

                        if re.match(r"^\d+\.\s+[A-Z\s]+$", line.strip()):
                            student_info["Name"] = line.split(".", 1)[1].strip()

                        if "PRN No." in line:
                            student_info["PRN No"] = line.split("PRN No.")[-1].split()[0]

                        if "Status:" in line:
                            student_info["Status"] = line.split("Status:")[-1].split()[0]

                        if "Percentage:" in line:
                            student_info["Percentage"] = (
                                line.split("Percentage:")[-1].split("%")[0].strip()
                            )

                        if re.match(r"^ECS\d+", line):
                            parts = line.split()
                            try:
                                subjects.append({
                                    "Code": parts[0],
                                    "UA": parts[3],
                                    "CA": parts[5],
                                    "Total": parts[8],
                                    "Status1": parts[-2],
                                })
                            except IndexError:
                                continue

                    # ✅ ONLY CHANGE IS HERE (ADDING METADATA)
                    if student_info and subjects:
                        df = pd.DataFrame(subjects)

                        student_info.update({
                            "Code": df["Code"].tolist(),
                            "UA": df["UA"].tolist(),
                            "CA": df["CA"].tolist(),
                            "Total": df["Total"].tolist(),
                            "Status1": df["Status1"].tolist(),

                            # 🔥 METADATA (ADMIN PROVIDED)
                            "Course": course,
                            "Year": year,
                            "Semester": semester,
                            "Exam": exam_name,
                            "AcademicYear": academic_year
                        })

                        student_info_all_with_marks.append(student_info)

    except Exception as e:
        st.error(f"Error processing PDF: {e}")
        return None

    return student_info_all_with_marks


def store_data(
    uploaded_file,
    course,
    year,
    semester,
    exam_name,
    academic_year
):
    if uploaded_file is None:
        st.warning("Please upload a PDF file first.")
        return

    # ✅ initialize session state once
    if "stored_data" not in st.session_state:
        st.session_state.stored_data = {}

    with st.spinner("Processing PDF..."):
        student_info = extract_student_data_from_bytes(
            uploaded_file.getvalue(),
            course,
            year,
            semester,
            exam_name,
            academic_year
        )

        if not student_info:
            st.error("No student data found in the PDF.")
            return

        short_data = [
            {
                "Seat No": r["Seat No"],
                "Name": r["Name"],
                "Percentage": r["Percentage"],
                "Status": r["Status"]
            }
            for r in student_info
        ]

        st.session_state.stored_data["Result_dict"] = student_info
        st.session_state.stored_data["Short_data"] = short_data

        success = save_results(student_info)

        if success:
            st.success("✅ All data saved successfully to Appwrite database!")
        else:
            st.error("❌ Failed to save data to database")

        st.subheader("Sample Data")
        st.dataframe(pd.DataFrame(short_data).head())


# def show():
#     if st.session_state.user_type != "Admin":
#         st.error("You need to be an administrator to access this page.")
#         return

#     st.header("📤 Upload Result PDF")

#     # -----------------------------
#     # STEP 1: REQUIRED METADATA
#     # -----------------------------
#     st.subheader("🧾 Enter Result Details")

#     course = st.selectbox("Select Course", ["BCS", "BCA"])
#     year = st.selectbox("Select Year", ["1", "2", "3"])
#     semester = st.selectbox("Select Semester", ["SEM-1", "SEM-3", "SEM-5"])
#     exam_name = st.text_input("Exam Name (e.g. Winter 2024)")
#     academic_year = st.text_input("Academic Year (e.g. 2024-25)")

#     if not exam_name or not academic_year:
#         st.info("Please fill all required fields to continue.")
#         return

#     # -----------------------------
#     # STEP 2: CHECK DATA EXISTENCE
#     # -----------------------------
#     if data_exists(course, year, semester, academic_year):
#         st.error("🚫 Data already exists in the database for this selection.")
#         st.info("👉 If you want to modify it, please go to **Update Results** page.")
#         return

#     st.success("✅ No existing data found. You can upload a new PDF.")

#     st.divider()

#     # -----------------------------
#     # STEP 3: PDF UPLOAD
#     # -----------------------------
#     st.subheader("📄 Upload Result PDF")

#     uploaded_file = st.file_uploader(
#         "Choose a PDF file",
#         type="pdf"
#     )

#     if st.button("🚀 Process & Save Results"):
#         if not uploaded_file:
#             st.warning("Please upload a PDF file.")
#             return

#         store_data(
#             uploaded_file,
#             course,
#             year,
#             semester,
#             exam_name,
#             academic_year
#         )

def show():
    if st.session_state.user_type != "Admin":
        st.error("You need to be an administrator to access this page.")
        return

    st.header("📤 Upload Result PDF")

    # ----------------------------------
    # STEP 1: REQUIRED METADATA
    # ----------------------------------
    st.subheader("🧾 Enter Result Details")

    course = st.selectbox("Select Course", ["BCS", "BCA"])
    year = st.selectbox("Select Year", ["1", "2", "3"])
    semester = st.selectbox("Select Semester", ["SEM-1", "SEM-3", "SEM-5"])
    exam_name = st.text_input("Exam Name (e.g. Winter 2024)")
    academic_year = st.text_input("Academic Year (e.g. 2024-25)")

    # Session flag
    if "can_upload" not in st.session_state:
        st.session_state.can_upload = False

    # ----------------------------------
    # STEP 2: CONTINUE BUTTON
    # ----------------------------------
    if st.button("➡️ Continue"):
        if not exam_name or not academic_year:
            st.warning("Please fill all required fields.")
            st.session_state.can_upload = False
        else:
            if data_exists(course, year, semester, academic_year):
                st.error("🚫 Data already exists in the database.")
                st.info("👉 Please use **Update Results** page to modify existing data.")
                st.session_state.can_upload = False
            else:
                st.success("✅ No existing data found. You can upload a new PDF.")
                st.session_state.can_upload = True

    # ----------------------------------
    # STEP 3: SHOW PDF UPLOAD ONLY IF ALLOWED
    # ----------------------------------
    if st.session_state.can_upload:
        st.divider()
        st.subheader("📄 Upload Result PDF")

        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf"
        )

        if st.button("🚀 Process & Save Results"):
            if not uploaded_file:
                st.warning("Please upload a PDF file.")
                return

            store_data(
                uploaded_file,
                course,
                year,
                semester,
                exam_name,
                academic_year
            )
