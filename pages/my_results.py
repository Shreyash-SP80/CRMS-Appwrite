import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from backend.appwrite_db import get_detailed_results


def show():
    st.header("📊 My Results")

    user = st.session_state.get("user")
    if not user:
        st.error("User not logged in")
        return

    results = get_detailed_results()

    if not results:
        st.info("No results available yet")
        return

    # ---------------------------------
    # Match student by Seat No or Name
    # ---------------------------------
    student = None
    for r in results:
        if (
            user.lower() in r["Name"].lower()
            or user.lower() in r["Seat No"].lower()
        ):
            student = r
            break

    if not student:
        st.warning("No results found for your account")
        return

    # ---------------------------------
    # Summary
    # ---------------------------------
    st.subheader("📌 Result Summary")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Seat No", student["Seat No"])
    col2.metric("Name", student["Name"])
    col3.metric("Status", student["Status"])
    col4.metric(
        "Percentage",
        f"{student['Percentage']}%"
    )

    # ---------------------------------
    # Subject-wise marks
    # ---------------------------------
    st.subheader("📝 Detailed Marks")

    rows = []
    for i in range(len(student["Code"])):
        rows.append({
            "Subject": student["Code"][i],
            "UA": student["UA"][i],
            "CA": student["CA"][i],
            "Total": student["Total"][i],
            "Status": student["Status1"][i],
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, hide_index=True)

    # ---------------------------------
    # Chart
    # ---------------------------------
    df["Total"] = pd.to_numeric(df["Total"], errors="coerce").fillna(0)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(df["Subject"], df["Total"], color="#4CAF50")
    ax.set_ylim(0, 100)
    ax.set_ylabel("Marks")
    ax.set_title("Subject-wise Performance")
    ax.set_xticklabels(df["Subject"], rotation=45, ha="right")

    st.pyplot(fig)
