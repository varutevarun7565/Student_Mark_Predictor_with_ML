from flask import Flask, render_template, request, redirect, send_file
import pickle
import pandas as pd
import sqlite3

app = Flask(__name__)

model = pickle.load(open('model.pkl', 'rb'))


def get_db_data(search=""):
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    if search:
        cursor.execute(
            "SELECT * FROM predictions WHERE name LIKE ? ORDER BY id DESC",
            ('%' + search + '%',)
        )
    else:
        cursor.execute(
            "SELECT * FROM predictions ORDER BY id DESC"
        )

    data = cursor.fetchall()
    conn.close()
    return data


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    history = get_db_data()
    return render_template(
        'dashboard.html',
        history=history
    )


@app.route('/predict', methods=['POST'])
def predict():

    name = request.form['name']
    hours = float(request.form['hours'])
    attendance = float(request.form['attendance'])
    sleep = float(request.form['sleep'])
    midsem = float(request.form['midsem'])

    input_data = pd.DataFrame(
        [[hours, attendance, sleep, midsem]],
        columns=['hours', 'attendance', 'sleep', 'midsem']
    )

    prediction = model.predict(input_data)

    marks = round(prediction[0], 2)

    if marks >= 90:
        grade = "A+"
        status = "PASS ✅"
        advice = "Excellent performance. Keep going."
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

    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO predictions
    (name,hours,attendance,sleep,midsem,predicted_marks,grade,status)
    VALUES (?,?,?,?,?,?,?,?)
    ''',
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

    return render_template(
        'index.html',
        prediction_text=marks,
        grade=grade,
        status=status,
        advice=advice,
        progress=int(marks)
    )


@app.route('/search', methods=['POST'])
def search():
    keyword = request.form['keyword']
    history = get_db_data(keyword)

    return render_template(
        'dashboard.html',
        history=history
    )


@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM predictions WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/dashboard')


@app.route('/export')
def export():

    conn = sqlite3.connect('students.db')

    df = pd.read_sql_query(
        "SELECT * FROM predictions",
        conn
    )

    df.to_csv(
        "student_predictions.csv",
        index=False
    )

    conn.close()

    return send_file(
        "student_predictions.csv",
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True)