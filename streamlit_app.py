import streamlit as st
import pickle
import pandas as pd
import sqlite3

# Load ML model
model = pickle.load(open("model.pkl", "rb"))

st.set_page_config(
    page_title="Student Performance Predictor",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 Student Performance Predictor")
st.write("Predict final student marks using ML")

# Inputs
name = st.text_input("Student Name")

hours = st.number_input(
    "Study Hours",
    min_value=0.0,
    max_value=24.0
)

attendance = st.number_input(
    "Attendance %",
    min_value=0.0,
    max_value=100.0
)

sleep = st.number_input(
    "Sleep Hours",
    min_value=0.0,
    max_value=24.0
)

midsem = st.number_input(
    "Mid-Sem Marks (/20)",
    min_value=0.0,
    max_value=20.0
)

# Predict button
if st.button("Predict Performance"):

    input_data = pd.DataFrame(
        [[hours, attendance, sleep, midsem]],
        columns=[
            "hours",
            "attendance",
            "sleep",
            "midsem"
        ]
    )

    prediction = model.predict(input_data)
    marks = round(prediction[0], 2)

    if marks >= 90:
        grade = "A+"
        status = "PASS ✅"
        advice = "Excellent performance."
    elif marks >= 75:
        grade = "A"
        status = "PASS ✅"
        advice = "Very good performance."
    elif marks >= 60:
        grade = "B"
        status = "PASS ✅"
        advice = "Good performance."
    elif marks >= 40:
        grade = "C"
        status = "PASS ✅"
        advice = "Average performance."
    else:
        grade = "F"
        status = "FAIL ❌"
        advice = "Needs improvement."

    st.success(f"Predicted Marks: {marks}")
    st.write(f"Grade: {grade}")
    st.write(f"Status: {status}")
    st.info(advice)

    # save to DB
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO predictions
        (
            name,
            hours,
            attendance,
            sleep,
            midsem,
            predicted_marks,
            grade,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
        name,
        hours,
        attendance,
        sleep,
        midsem,
        marks,
        grade,
        status
    ))

    conn.commit()
    conn.close()

# Dashboard
st.subheader("📊 Student Records")

conn = sqlite3.connect("students.db")
df = pd.read_sql_query(
    "SELECT * FROM predictions ORDER BY id DESC",
    conn
)
conn.close()

st.dataframe(df)

if not df.empty:
    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇ Download CSV",
        csv,
        "student_predictions.csv",
        "text/csv"
    )