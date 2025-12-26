import cv2
import face_recognition
import pickle
import os
import sqlite3
#=========================================
#THIS CODE IS MADE TO MANUALLY REGISTER THE STUDENTS BY HAND (WITHOUT FACE RECOGNITION) IT IS EXTRACTED FROM main.py
img_path = 'Images'
img_path_list = os.listdir(img_path)

student_list = []
student_name = []

for student in img_path_list:
    img = cv2.imread(os.path.join(img_path, student))
    if img is not None:
        student_list.append(img)
        student_name.append(os.path.splitext(student)[0])
    else:
        print(f"Failed to load {student}")
print(student_name)

def find_encodings(student_list):
    encoding_list = []
    for std in student_list:
        std = cv2.cvtColor(std, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(std)[0]
        encoding_list.append(encode)
    return encoding_list

print("started")
known_encodings = find_encodings(student_list)
known_encodings_student = [known_encodings, student_name]
print("done")

file = open("encodings.p",'wb')
pickle.dump(known_encodings_student, file)
file.close()
print("saved")

connection = sqlite3.connect('clc_attendance_data.db')
cursor = connection.cursor()
for student in student_name:
    cursor.execute('INSERT OR IGNORE INTO Students (name) VALUES (?);', (student,))
connection.commit()
connection.close()