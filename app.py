import streamlit as st
import time
import os
import sys
import traceback

import backend.appwrite_db
# from appwrite_users import register_user, authenticate_user
from backend.appwrite_db import register_user, authenticate_user, send_email_otp, verify_email_otp
# from backend.appwrite_db import register_user, authenticate_user, send_email_otp, verify_email_otp


from pages.dashboard import show as dashboard_page
from pages.upload_pdf import show as upload_pdf_page
from pages.student_search import show as student_search_page
from pages.division_analysis import show as division_analysis_page
from pages.subject_analysis import show as subject_analysis_page
from pages.pass_fail_analysis import show as pass_fail_analysis_page
from pages.top_students import show as top_students_page
from pages.excel_report import show as excel_report_page
from pages.update_results import show as update_results_page
from pages.my_results import show as my_results_page



# Page config
st.set_page_config(
    page_title="College Result Manager",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state
if "user" not in st.session_state:
    st.session_state.user = None

if "user_type" not in st.session_state:
    st.session_state.user_type = None


# def show_login_page():
#     st.title("🎓 College Result Management System")
#     st.markdown("---")

#     tab1, tab2 = st.tabs(["Login", "Register"])

#     with tab1:
#         with st.form("login_form"):
#             username = st.text_input("Username")
#             password = st.text_input("Password", type="password")
#             login = st.form_submit_button("Login")

#             if login:
#                 success, role, msg = authenticate_user(username, password)
#                 if success:
#                     st.session_state.user = username
#                     st.session_state.user_type = role
#                     st.success(msg)
#                     time.sleep(1)
#                     st.rerun()
#                 else:
#                     st.error(msg)

#     with tab2:
#         with st.form("register_form"):
#             username = st.text_input("Username")
#             password = st.text_input("Password", type="password")
#             confirm = st.text_input("Confirm Password", type="password")
#             role = st.selectbox("Role", ["Student", "Admin"])
#             email = st.text_input("Email (optional)")
#             register = st.form_submit_button("Register")

#             if register:
#                 if password != confirm:
#                     st.error("Passwords do not match")
#                 else:
#                     success, msg = register_user(username, password, role, email)
#                     if success:
#                         st.success(msg)
#                     else:
#                         st.error(msg)

def show_login_page():
    st.title("🎓 College Result Management System")
    st.markdown("---")

    tab1, tab2 = st.tabs(["Login", "Register"])

    # ---------------- LOGIN ----------------
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login = st.form_submit_button("Login")

            if login:
                success, role, msg = authenticate_user(username, password)
                if success:
                    st.session_state.user = username
                    st.session_state.user_type = role
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    # ---------------- REGISTER ----------------
    with tab2:
        st.subheader("🧑‍🎓 Student Registration")

        # Session state init
        st.session_state.setdefault("otp_sent", False)
        st.session_state.setdefault("otp_verified", False)
        st.session_state.setdefault("otp_user_id", None)

        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")

        # STEP 1: SEND OTP
        if not st.session_state.otp_sent:
            if st.button("📧 Send OTP"):
                if not username or not email or not password:
                    st.warning("All fields are required")
                elif password != confirm:
                    st.error("Passwords do not match")
                else:
                    success, res = send_email_otp(email)
                    if success:
                        st.session_state.otp_sent = True
                        st.session_state.otp_user_id = res
                        st.success("OTP sent to your email")
                    else:
                        st.error(res)

        # STEP 2: VERIFY OTP & REGISTER
        if st.session_state.otp_sent:
            otp = st.text_input("Enter OTP", max_chars=6)

            if st.button("✅ Verify OTP & Register"):
                verified, msg = verify_email_otp(
                    st.session_state.otp_user_id,
                    otp
                )

                if not verified:
                    st.error(msg)
                else:
                    success, msg = register_user(
                        username=username,
                        password=password,
                        role="Student",
                        email=email
                    )

                    if success:
                        st.success("🎉 Account created! You can login now.")
                        # RESET STATE
                        st.session_state.otp_sent = False
                        st.session_state.otp_verified = True
                        st.session_state.otp_user_id = None
                    else:
                        st.error(msg)

def show_home_page():
    st.title("🎓 College Result Management System")
    st.markdown("---")
    
    st.markdown("""
    <div style="text-align: center;">
        <h2>Welcome to the College Result Management System</h2>
        <p>This system helps colleges manage and analyze student results efficiently.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background-color: #f0f2f6; color: black; padding: 20px; border-radius: 10px; text-align: center;">
            <h3>📊 Analytics</h3>
            <p>Comprehensive analysis of student performance with visualizations</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background-color: #f0f2f6; color: black; padding: 20px; border-radius: 10px; text-align: center;">
            <h3>🔍 Search</h3>
            <p>Easily search for students and their detailed results</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background-color: #f0f2f6; color: black; padding: 20px; border-radius: 10px; text-align: center;">
            <h3>📝 Reports</h3>
            <p>Generate detailed reports in Excel and PDF formats</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    <div style="background-color: #e6f7ff; color: black; padding: 20px; border-radius: 10px;">
        <h3>About Our Work</h3>
        <p>This system was developed to streamline the process of managing and analyzing college results. 
        It provides administrators with powerful tools to upload, process, and analyze student performance data, 
        while giving students easy access to their results.</p>
        <p>Key features include:</p>
        <ul>
            <li>PDF result processing and extraction</li>
            <li>Comprehensive performance analytics</li>
            <li>Student search functionality</li>
            <li>Report generation in multiple formats</li>
            <li>Role-based access control</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9em;">
        <p>Developed by Shreyash Patil | Analytics Dashboard</p>
    </div>
    """, unsafe_allow_html=True)

def show_main_app():
    st.sidebar.title(f"Welcome, {st.session_state.user}")
    st.sidebar.write(f"Role: {st.session_state.user_type}")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.user_type = None
        st.rerun()

    if st.session_state.user_type == "Admin":
        menu = [
            "Home",
            "Dashboard",
            "Upload PDF",
            "Top Students",
            "Division Analysis",
            "Pass/Fail Analysis",
            "Subject Analysis",
            "Student Search",
            "Excel Report",
            "Update Results",
            "My result"
        ]
    else:
        menu = [
            "Home",
            "Dashboard",
            "Top Students",
            "Division Analysis",
            "Pass/Fail Analysis",
            "Subject Analysis",
            "Student Search",
            "Excel Report"
        ]

    
    
    choice = st.sidebar.selectbox("Menu", menu)

    try:
        if choice == "Home":
            show_home_page()
        elif choice == "Dashboard":
            if st.session_state.get("role") == "Admin":
                if st.button("🔍 Debug Connection"):
                    from appwrite_helper import databases, DB_ID, RESULTS_COLLECTION
                    from appwrite.query import Query
                    try:
                        r = databases.list_documents(
                            database_id=DB_ID,
                            collection_id=RESULTS_COLLECTION,
                            queries=[Query.limit(1)]
                        )
                        st.success(f"Connected! Total docs: {r['total'] if isinstance(r, dict) else r.total}")
                        dashboard_page()
                    except Exception as e:
                        st.error(f"Connection error: {e}")
            # dashboard_page()
        elif choice == "Upload PDF":
            upload_pdf_page()
        elif choice == "Top Students":
            top_students_page()
        elif choice == "Division Analysis":
            division_analysis_page()
        elif choice == "Pass/Fail Analysis":
            pass_fail_analysis_page()
        elif choice == "Subject Analysis":
            subject_analysis_page()
        elif choice == "Student Search":
            student_search_page()
        elif choice == "Excel Report":
            excel_report_page()
        elif choice == "Update Results":
            update_results_page()
        elif choice == "Update Results":
            my_results_page()
    except Exception:
        st.error("Something went wrong")
        st.code(traceback.format_exc())


def main():
    if st.session_state.user is None:
        show_login_page()
    else:
        show_main_app()


if __name__ == "__main__":
    main()


