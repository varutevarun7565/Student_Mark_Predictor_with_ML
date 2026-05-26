import sqlite3

conn = sqlite3.connect('students.db')

cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    hours REAL,
    attendance REAL,
    sleep REAL,
    midsem REAL,
    predicted_marks REAL,
    grade TEXT,
    status TEXT
)
''')

conn.commit()
conn.close()

print("Database created successfully")