import sqlite3
from sqlite3 import Error
connection = sqlite3.connect('clc_attendance_data.db')
cursor = connection.cursor()

student_table = ('''
    CREATE TABLE IF NOT EXISTS Students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    registration_date TIMESTAMP
    );
''')

subjects_table = ('''
    CREATE TABLE IF NOT EXISTS Subjects (
    subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
    );
''')

teacher_table = ('''
    CREATE TABLE IF NOT EXISTS Teachers (
    teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
    );
''')

attendance_table = ('''
    CREATE TABLE IF NOT EXISTS Attendance (
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    teacher_id INTEGER NOT NULL,
    attendance_time TIMESTAMP ,
    FOREIGN KEY (student_id) REFERENCES Students (student_id),
    FOREIGN KEY (subject_id) REFERENCES Subjects (subject_id),
    FOREIGN KEY (teacher_id) REFERENCES Teachers (teacher_id)
    );
''')
cursor.execute(student_table)
cursor.execute(subjects_table)
cursor.execute(teacher_table)
cursor.execute(attendance_table)
connection.commit()

def fill_tables(conn):
    subjects = ['Math', 'Physics', 'Chemistry', 'Economics', 'English', 'Business']
    teachers = {
        'Math': ['Lili', 'Mike', 'Cevin', 'Alel', 'Khris', 'Lisa', 'Jolie'],
        'Physics': ['Dave', 'Michael C'],
        'Chemistry': ['Lili', 'Kadek', 'Kartika'],
        'Economics': ['Gaby', 'Helena'],
        'English': ['Lisa'],
        'Business': ['Gaby']
    }

    try:
        cursor = conn.cursor()
        for subject in subjects:
            cursor.execute('INSERT OR IGNORE INTO Subjects (name) VALUES (?);', (subject,))

        all_teachers = set()
        for teacher_list in teachers.values():
            all_teachers.update(teacher_list)
        for teacher in all_teachers:
            cursor.execute('INSERT OR IGNORE INTO Teachers (name) VALUES (?);', (teacher,))

        conn.commit()
        print("done")
    except Error as e:
        print(e)
fill_tables(connection)
connection.close()