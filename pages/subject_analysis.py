# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt

# # ✅ Appwrite backend import (MongoDB removed)
# from backend.appwrite_db import load_results


# def load_data(path):
#     """Load data from Appwrite DB or session state"""

#     # 🔄 Load from Appwrite
#     appwrite_data = load_results()

#     if appwrite_data:
#         if path == "Shoert_data":
#             short_data = []
#             for record in appwrite_data:
#                 short_data.append({
#                     "Seat No": record.get('Seat No', ''), 
#                     "Name": record.get('Name', ''), 
#                     "Percentage": record.get('Percentage', ''), 
#                     "Status": record.get('Status', '')
#                 })
#             return short_data

#         return appwrite_data

#     # Fallback to session state
#     return st.session_state.stored_data.get(path, [])


# def subject_analysis(detailed_data):
#     st.header("📚 Subject-wise Analysis")
    
#     if not detailed_data:
#         st.warning("No detailed data available. Please process a PDF first.")
#         return
    
#     subject_stats = {}
    
#     for student in detailed_data:
#         for i in range(len(student["Code"])):
#             code = student["Code"][i]
#             total = student["Total"][i]
            
#             if not isinstance(code, str) or not isinstance(total, str):
#                 continue
            
#             if code not in subject_stats:
#                 subject_stats[code] = {
#                     "total_marks": 0,
#                     "count": 0,
#                     "pass_count": 0,
#                     "fail_count": 0
#                 }
            
#             try:
#                 if total.isdigit():
#                     mark = int(total)
#                     subject_stats[code]["total_marks"] += mark
#                     subject_stats[code]["count"] += 1
                    
#                     status = student["Status1"][i]
#                     if status == "P":
#                         subject_stats[code]["pass_count"] += 1
#                     else:
#                         subject_stats[code]["fail_count"] += 1
#             except:
#                 continue
    
#     analysis_data = []
#     for code, stats in subject_stats.items():
#         if stats["count"] > 0:
#             avg_mark = stats["total_marks"] / stats["count"]
#             pass_rate = (stats["pass_count"] / stats["count"]) * 100
#             analysis_data.append({
#                 "Subject": code,
#                 "Avg. Marks": f"{avg_mark:.2f}",
#                 "Pass Rate": f"{pass_rate:.2f}%",
#                 "Students": stats["count"],
#                 "Passed": stats["pass_count"],
#                 "Failed": stats["fail_count"]
#             })
    
#     if not analysis_data:
#         st.warning("No valid subject data found")
#         return
    
#     df = pd.DataFrame(analysis_data)
    
#     col1, col2 = st.columns([1, 2])
    
#     with col1:
#         st.subheader("Subject Performance")
#         st.dataframe(df)
    
#     with col2:
#         st.subheader("Subject Analysis")
        
#         tab1, tab2 = st.tabs(["Average Marks", "Pass Rate"])
        
#         with tab1:
#             fig, ax = plt.subplots(figsize=(8, 4))
#             bars = ax.bar(
#                 df['Subject'],
#                 df['Avg. Marks'].astype(float),
#                 color='skyblue'
#             )
#             ax.set_ylabel('Average Marks')
#             ax.set_title('Average Marks per Subject')
#             ax.set_xticklabels(df['Subject'], rotation=45, ha='right')
#             ax.bar_label(bars, fmt='%.2f', padding=3)
#             st.pyplot(fig)
        
#         with tab2:
#             fig, ax = plt.subplots(figsize=(8, 4))
#             bars = ax.bar(
#                 df['Subject'],
#                 df['Pass Rate'].str.replace('%', '').astype(float),
#                 color='lightgreen'
#             )
#             ax.set_ylabel('Pass Rate (%)')
#             ax.set_title('Pass Rate per Subject')
#             ax.set_ylim(0, 100)
#             ax.set_xticklabels(df['Subject'], rotation=45, ha='right')
#             ax.bar_label(bars, fmt='%.1f%%', padding=3)
#             st.pyplot(fig)


# def show():
#     detailed_data = load_data("Result_dict")
#     subject_analysis(detailed_data)

# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt

# # Appwrite backend
# from backend.appwrite_db import load_results
# from backend.appwrite_db import get_short_results, get_detailed_results



# # -------------------------------------------------
# # Load data from Appwrite
# # -------------------------------------------------
# # def load_data():
# #     data = load_results()
# #     return data if data else []


# # -------------------------------------------------
# # Subject-wise Analysis
# # -------------------------------------------------
# def subject_analysis(detailed_data):
#     st.header("📚 Subject-wise Analysis")

#     if not detailed_data:
#         st.warning("No detailed data available.")
#         return

#     subject_stats = {}

#     for student in detailed_data:
#         codes = student.get("code", [])
#         totals = student.get("total", [])
#         status_list = student.get("status1", [])

#         # Safety check
#         if not (isinstance(codes, list) and isinstance(totals, list) and isinstance(status_list, list)):
#             continue

#         length = min(len(codes), len(totals), len(status_list))

#         for i in range(length):
#             code = str(codes[i]).strip()
#             total = totals[i]
#             status = str(status_list[i]).strip()

#             if not code:
#                 continue

#             # Initialize subject
#             if code not in subject_stats:
#                 subject_stats[code] = {
#                     "total_marks": 0,
#                     "count": 0,
#                     "pass_count": 0,
#                     "fail_count": 0
#                 }

#             try:
#                 mark = float(total)
#             except:
#                 continue

#             subject_stats[code]["total_marks"] += mark
#             subject_stats[code]["count"] += 1

#             if status == "P":
#                 subject_stats[code]["pass_count"] += 1
#             else:
#                 subject_stats[code]["fail_count"] += 1

#     if not subject_stats:
#         st.warning("No valid subject data found.")
#         return

#     # -------------------------------------------------
#     # Build DataFrame
#     # -------------------------------------------------
#     rows = []
#     for code, stats in subject_stats.items():
#         avg_marks = stats["total_marks"] / stats["count"]
#         pass_rate = (stats["pass_count"] / stats["count"]) * 100

#         rows.append({
#             "Subject": code,
#             "Average Marks": round(avg_marks, 2),
#             "Pass Rate (%)": round(pass_rate, 2),
#             "Students": stats["count"],
#             "Passed": stats["pass_count"],
#             "Failed": stats["fail_count"]
#         })

#     df = pd.DataFrame(rows).sort_values("Average Marks", ascending=False)

#     # -------------------------------------------------
#     # UI
#     # -------------------------------------------------
#     col1, col2 = st.columns([1.2, 2])

#     with col1:
#         st.subheader("📄 Subject Summary")
#         st.dataframe(df.reset_index(drop=True), hide_index=True)

#     with col2:
#         st.subheader("📊 Visual Analysis")

#         tab1, tab2 = st.tabs(["Average Marks", "Pass Rate"])

#         with tab1:
#             fig, ax = plt.subplots(figsize=(8, 4))
#             bars = ax.bar(df["Subject"], df["Average Marks"], color="#64B5F6")
#             ax.set_ylabel("Average Marks")
#             ax.set_title("Average Marks per Subject")
#             ax.set_xticklabels(df["Subject"], rotation=45, ha="right")
#             ax.bar_label(bars, fmt="%.2f")
#             st.pyplot(fig)

#         with tab2:
#             fig, ax = plt.subplots(figsize=(8, 4))
#             bars = ax.bar(df["Subject"], df["Pass Rate (%)"], color="#81C784")
#             ax.set_ylabel("Pass Rate (%)")
#             ax.set_ylim(0, 100)
#             ax.set_title("Pass Rate per Subject")
#             ax.set_xticklabels(df["Subject"], rotation=45, ha="right")
#             ax.bar_label(bars, fmt="%.1f%%")
#             st.pyplot(fig)


# # -------------------------------------------------
# # Streamlit entry
# # -------------------------------------------------
# def show():
#     detailed_data = load_data()
#     subject_analysis(detailed_data)

# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt

# # -------------------------------------------------
# # Appwrite backend
# # -------------------------------------------------
# from backend.appwrite_db import get_detailed_results


# # -------------------------------------------------
# # Normalize Appwrite data (IMPORTANT)
# # -------------------------------------------------
# def normalize_data(raw_data):
#     normalized = []

#     for d in raw_data:
#         normalized.append({
#             "code": d.get("Code", []) or [],
#             "total": d.get("Total", []) or [],
#             "status1": d.get("Status1", []) or []
#         })

#     return normalized


# # -------------------------------------------------
# # Subject-wise Analysis
# # -------------------------------------------------
# def subject_analysis(detailed_data):
#     st.header("📚 Subject-wise Analysis")

#     if not detailed_data:
#         st.warning("No detailed data available.")
#         return

#     subject_stats = {}

#     for student in detailed_data:
#         codes = student["code"]
#         totals = student["total"]
#         status_list = student["status1"]

#         length = min(len(codes), len(totals), len(status_list))

#         for i in range(length):
#             code = str(codes[i]).strip()
#             status = str(status_list[i]).strip()

#             try:
#                 mark = float(totals[i])
#             except:
#                 continue

#             if not code:
#                 continue

#             if code not in subject_stats:
#                 subject_stats[code] = {
#                     "total_marks": 0,
#                     "count": 0,
#                     "pass_count": 0,
#                     "fail_count": 0
#                 }

#             subject_stats[code]["total_marks"] += mark
#             subject_stats[code]["count"] += 1

#             if status == "P":
#                 subject_stats[code]["pass_count"] += 1
#             else:
#                 subject_stats[code]["fail_count"] += 1

#     if not subject_stats:
#         st.warning("No valid subject data found.")
#         return

#     # -------------------------------------------------
#     # Build DataFrame
#     # -------------------------------------------------
#     rows = []
#     for code, stats in subject_stats.items():
#         rows.append({
#             "Subject": code,
#             "Average Marks": round(stats["total_marks"] / stats["count"], 2),
#             "Pass Rate (%)": round((stats["pass_count"] / stats["count"]) * 100, 2),
#             "Students": stats["count"],
#             "Passed": stats["pass_count"],
#             "Failed": stats["fail_count"]
#         })

#     df = pd.DataFrame(rows).sort_values("Average Marks", ascending=False)

#     # -------------------------------------------------
#     # UI
#     # -------------------------------------------------
#     col1, col2 = st.columns([1.2, 2])

#     with col1:
#         st.subheader("📄 Subject Summary")
#         st.dataframe(df.reset_index(drop=True), hide_index=True)

#     with col2:
#         st.subheader("📊 Visual Analysis")

#         tab1, tab2 = st.tabs(["Average Marks", "Pass Rate"])

#         with tab1:
#             fig, ax = plt.subplots(figsize=(8, 4))
#             bars = ax.bar(df["Subject"], df["Average Marks"], color="#64B5F6")
#             ax.set_ylabel("Average Marks")
#             ax.set_title("Average Marks per Subject")
#             ax.set_xticklabels(df["Subject"], rotation=45, ha="right")
#             ax.bar_label(bars, fmt="%.2f")
#             st.pyplot(fig)

#         with tab2:
#             fig, ax = plt.subplots(figsize=(8, 4))
#             bars = ax.bar(df["Subject"], df["Pass Rate (%)"], color="#81C784")
#             ax.set_ylabel("Pass Rate (%)")
#             ax.set_ylim(0, 100)
#             ax.set_title("Pass Rate per Subject")
#             ax.set_xticklabels(df["Subject"], rotation=45, ha="right")
#             ax.bar_label(bars, fmt="%.1f%%")
#             st.pyplot(fig)


# # -------------------------------------------------
# # Streamlit Entry
# # -------------------------------------------------
# def show():
#     raw_data = get_detailed_results()      # ✅ correct source
#     detailed_data = normalize_data(raw_data)
#     subject_analysis(detailed_data)



import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------------------------
# Appwrite backend
# -------------------------------------------------
from backend.appwrite_db import get_detailed_results


# -------------------------------------------------
# Normalize Appwrite data (IMPORTANT)
# -------------------------------------------------
def normalize_data(student):
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

        # ✅ METADATA
        "course": student.get("Course"),
        "year": str(student.get("Year")),
        "semester": student.get("Semester"),
        "exam_name": student.get("Exam"),
        "academic_year": student.get("AcademicYear"),
    }





# -------------------------------------------------
# Subject-wise Analysis
# -------------------------------------------------
def subject_analysis(detailed_data):
    st.header("📚 Subject-wise Analysis")

    if not detailed_data:
        st.warning("No detailed data available.")
        return

    subject_stats = {}

    for student in detailed_data:
        codes = student["code"]
        totals = student["total"]
        status_list = student["status1"]

        length = min(len(codes), len(totals), len(status_list))

        for i in range(length):
            code = str(codes[i]).strip()
            status = str(status_list[i]).strip()

            try:
                mark = float(totals[i])
            except:
                continue

            if not code:
                continue

            if code not in subject_stats:
                subject_stats[code] = {
                    "total_marks": 0,
                    "count": 0,
                    "pass_count": 0,
                    "fail_count": 0
                }

            subject_stats[code]["total_marks"] += mark
            subject_stats[code]["count"] += 1

            if status == "P":
                subject_stats[code]["pass_count"] += 1
            else:
                subject_stats[code]["fail_count"] += 1

    if not subject_stats:
        st.warning("No valid subject data found.")
        return

    # -------------------------------------------------
    # Build DataFrame
    # -------------------------------------------------
    rows = []
    for code, stats in subject_stats.items():
        rows.append({
            "Subject": code,
            "Average Marks": round(stats["total_marks"] / stats["count"], 2),
            "Pass Rate (%)": round((stats["pass_count"] / stats["count"]) * 100, 2),
            "Students": stats["count"],
            "Passed": stats["pass_count"],
            "Failed": stats["fail_count"]
        })

    df = pd.DataFrame(rows).sort_values("Average Marks", ascending=False)

    # -------------------------------------------------
    # UI
    # -------------------------------------------------
    col1, col2 = st.columns([1.2, 2])

    with col1:
        st.subheader("📄 Subject Summary")
        st.dataframe(df.reset_index(drop=True), hide_index=True)

    with col2:
        st.subheader("📊 Visual Analysis")

        tab1, tab2 = st.tabs(["Average Marks", "Pass Rate"])

        with tab1:
            fig, ax = plt.subplots(figsize=(8, 4))
            bars = ax.bar(df["Subject"], df["Average Marks"], color="#64B5F6")
            ax.set_ylabel("Average Marks")
            ax.set_title("Average Marks per Subject")
            ax.set_xticklabels(df["Subject"], rotation=45, ha="right")
            ax.bar_label(bars, fmt="%.2f")
            st.pyplot(fig)

        with tab2:
            fig, ax = plt.subplots(figsize=(8, 4))
            bars = ax.bar(df["Subject"], df["Pass Rate (%)"], color="#81C784")
            ax.set_ylabel("Pass Rate (%)")
            ax.set_ylim(0, 100)
            ax.set_title("Pass Rate per Subject")
            ax.set_xticklabels(df["Subject"], rotation=45, ha="right")
            ax.bar_label(bars, fmt="%.1f%%")
            st.pyplot(fig)


# -------------------------------------------------
# Streamlit Entry
# -------------------------------------------------
def show():
    st.header("📚 Subject-wise Analysis")

    # 🔽 REQUIRED FILTERS
    course = st.selectbox("Course", ["BCS", "BCA"])
    year = st.selectbox("Year", ["1", "2", "3"])
    semester = st.selectbox("Semester", ["SEM-1", "SEM-3", "SEM-5"])
    academic_year = st.text_input("Academic Year (e.g. 2025-26)")

    if not academic_year:
        st.info("Please enter Academic Year to continue")
        return

    raw_data = get_detailed_results()

    if not raw_data:
        st.warning("No detailed data available.")
        return

    # ✅ FIX: normalize EACH student
    normalized = [normalize_data(s) for s in raw_data]

    # 🔥 FILTER FIRST
    filtered_data = [
        d for d in normalized
        if d["course"] == course
        and d["year"] == year
        and d["semester"] == semester
        and d["academic_year"] == academic_year
    ]

    if not filtered_data:
        st.warning("No records found for selected filters.")
        return

    # 🔥 NOW ANALYZE SUBJECTS
    subject_analysis(filtered_data)
