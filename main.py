import tkinter as tk
from tkinter import messagebox
import face_recognition
import cv2
import pickle
import numpy as np
import os
from PIL import Image, ImageTk
import datetime
import threading
import sqlite3
from sqlite3 import Error

class App:
    # below are functions that i made in order to simplify the creation of GUI elements using the tkinter library
    def create_button(self, window, h, w,  text, size, color, command): # this function creates a tkinter button
        button = tk.Button(
            window,
            text=text,
            activebackground="black",
            activeforeground="white",
            fg="white",
            bg=color,
            command=command,
            height=h,
            width=w,
            cursor="hand2",
            font=('Courier', size, "bold")

        )
        return button
    def create_messagebox(self, title, description):  # this function creates a messagebox window
        messagebox.showinfo(title,description)

    def create_image_label(self, window):  # this function creates an image label for the webcam
       label = tk.Label(window)
       label.grid(row=0, column=0)
       return label

    def create_text(self, window, text, size, position):  # this function creates the text in the window
        label = tk.Label(window, text=text)
        label.config(font=("Courier", size), justify=position)
        return label
    def create_input_text(self, window):  # this function creates an input box that accepts users' text input
        inputtxt = tk.Text(window,
                           height = 2,
                           width = 18,
                           font = ("Arial", 25))
        return inputtxt

    def run(self):  # this function runs the code
        self.db = 'clc_attendance_data.db'  # initialize the database that will be connected
        self.connection = sqlite3.connect('clc_attendance_data.db')  # connect the database for future queries
        self.start_window.mainloop()  # run the start_window (see code below)
    def __init__(self):
        # create the initial window called start_window
        self.start_window = tk.Tk()
        self.start_window.resizable(False,False)  # the window isn't resizeable by the user's actions
        self.start_window.geometry('1000x600')
        self.start_window.title('CLC Attendance')

        # add login and register button on the left side of the window
        self.login_button = self.create_button(self.start_window, 2, 11, 'Login', 16, 'green', self.login)  #
        self.login_button.place(x=20, y=400)  # the coordinates here are just trial and error, no math included
        self.login_button_text = self.create_text(self.start_window,"Login if you have\nregistered", 10, "center")
        self.login_button_text.place(x=24, y=469)  # the coordinates here are just trial and error, no math included

        self.register_button = self.create_button(self.start_window, 2, 11, 'Register', 16, 'blue', self.register)
        self.register_button.place(x=190, y=400)
        self.register_button_text = self.create_text(self.start_window,"Register as a\nnew user", 10, "center")
        self.register_button_text.place(x=212, y=469)

        # welcome text
        self.welcome_text = self.create_text(self.start_window,"Welcome to the CLC\nattendance system", 17, "center")
        self.welcome_text.place(x=55, y=70)

        # add the CLC logo on top of the buttons
        logo = Image.open("clc_logo.jpg")  # use the PIL library to import the image
        logo = logo.resize((225, 225))
        logo_tk = ImageTk.PhotoImage(logo)  # reformats the logo into an appropriate format
        self.logo_label = tk.Label(self.start_window, image = logo_tk)  # add the logo to the start window
        self.logo_label.image = logo_tk
        self.logo_label.place(x=70, y=140)

        # add the live camera to start_window
        self.camera = self.create_image_label(self.start_window)
        self.camera.place(x=370, y=0, width=600, height=600)
        self.add_camera(self.camera)

        # the code below loads the encoded files of the (encoded) registered students for the login process
        file = open('encodings.p', 'rb')
        known_encoding_student_list = pickle.load(file)
        file.close()
        self.known_encoding_list, self.student = known_encoding_student_list

    def process_camera(self):
        # this function updates the interface...
        # ... with new frames from the device's camera
        ret, frame = self.cap.read()  # reads a frame from the camera
        self.capture = frame
        img_ = cv2.cvtColor(self.capture, cv2.COLOR_BGR2RGB)  # convert the frame to RGB, a standard format (this is a numpy array)
        self.capture_pil = Image.fromarray(img_)  # uses PIL library to convert img_ (numpy array) into a PIL image
        imgtk = ImageTk.PhotoImage(self.capture_pil)  # converts it into an format that Tkinter accepts
        self.label.imgtk = imgtk
        self.label.configure(image=imgtk)
        self.label.after(5, self.process_camera)  # loops every 5 ms for smooth camera

    def add_camera(self, cam):
        # this function attaches the camera feed
        if not hasattr(self, 'cap'): # if class (object) App does not have cap,
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # set the first parameter to 0 because I'm using my computer's camera
                                                           # captures the camera feed using CAP_DSHOW (usually for windows)
        self.label = cam  # references tkinter label (cam) as label
        self.process_camera() # calls previous function

    def login(self):
        # first, the camera will capture the student into an image and be resized 1/4 of its size
        # reducing the resolution of the image = less pixels = less calculation = faster processing
        student_image = cv2.resize(self.capture, (0,0), None, 0.25, 0.25)

        # then, it will convert the color profile to RGB which is standardized...
        # ... since opencv uses BGR as a default
        student_image = cv2.cvtColor(student_image,cv2.COLOR_BGR2RGB)

        # facial features in student_image is stored in captured_face...
        # ... using face_recognition library (Geitgey, 2018)
        captured_face = face_recognition.face_locations(student_image)  # scans the student image for any faces
        captured_face_encoding = face_recognition.face_encodings(student_image, captured_face)  # get the encodings of the face

        # this for loop compares the face encodings with the known encodings
        for encoded_face, face_loc in zip(captured_face_encoding, captured_face):  # loops for each encoding and corresponding face
            match = face_recognition.compare_faces(self.known_encoding_list, encoded_face)  # returns a list of boolean values..
                                                                                        #.. if encoded_face is a match to each known encoding
            distance = face_recognition.face_distance(self.known_encoding_list, encoded_face)  # returns all distance values of each face
            match_index = np.argmin(distance)  # this finds the minimum distance of the list above, which means the most similar face

            if match[match_index]:  # if boolean list match is True at the same index as match_index it is  as a successful face recognition
                result_name = self.student[match_index]  # selects corresponding student name of the match index
                print ("face: ", result_name)

                # store the face recognition results to be used later
                self.user = result_name
                self.show_login_confirmation_window(result_name)  # calls a function to show the confirmation window

    def show_login_confirmation_window(self,name):  # this function shows the identity confirmation before proceeding with attendance
        # create the confirmation window of the face recognition results before proceeding with attendance
        self.login_confirmation_window = tk.Toplevel(self.start_window) # this places the windows on top of start_window
        self.login_confirmation_window.resizable(False, False)
        self.login_confirmation_window.geometry('405x400')
        self.login_confirmation_window.title('Login Confirmation')

        # confirmation text
        self.confirm_text = self.create_text(self.login_confirmation_window,
                                             f"Welcome,\n{name}.\nIs that correct?",20, 'center'
                                             )
        self.confirm_text.place(x=75, y=100)

        # yes button
        self.login_yes_button = self.create_button(self.login_confirmation_window, 2, 15, 'Yes',
                                                           15, 'green', self.subject_selection)  # if the user chooses yes, 
                                                                                                        # ...proceed with attendance
        self.login_yes_button.place(x=10, y=300)

        # retry button if the facial recognition system produces different results
        self.login_retry_button = self.create_button(self.login_confirmation_window, 2, 15, 'No, retry',
                                                     15, 'blue', self.retry_login)  # if the user chooses no,...
                                                                                              # ...go back to previous window
        self.login_retry_button.place(x=205, y=300)

    def retry_login(self):
        self.login_confirmation_window.destroy()  # this erases the current window so...
        # ...users can access the previous window

    def subject_selection(self):
        # destroy the login confirmation window if it exists to reduce clutter
        if hasattr(self, 'login_confirmation_window') and self.login_confirmation_window.winfo_exists():
            self.login_confirmation_window.destroy()

        self.subject_selection_window = tk.Toplevel()
        self.subject_selection_window.resizable(False, False)
        self.subject_selection_window.geometry('600x500')
        self.subject_selection_window.title('Subject Selection')

        # text for subject selection
        self.select_subject_text = self.create_text(self.subject_selection_window, 'Select a subject', 20, 'center')
        self.select_subject_text.place(x=160, y=50)

        subjects = ['Math', 'Physics', 'Chemistry', 'Economics', 'English', 'Business'] # list that contains all subjects in CLC
        # the structure of the button placement will have two rows and three columns resulting in a total of 6 subjects
        x_positions = [100, 350]  # this contains the possible horizontal (x) positions for a button
        y_positions = [150, 250, 350]  # this contains the possible vertical (y) positions for a button
        # teh above code allows for consistency and organizations of the button placements on each row and column

        i = 0  # this value is the iterator for the for loop below
        # the for loop below will calculate the positions of each button
        for subject in subjects:
            x = x_positions[i%2]  # if i is even, then return x_positions[0], which is 100, otherwise return x_positions[1] which is 350
            y = y_positions[i//2] # this returns the rounded-down value of i divided by two, which corresponds to y_positions
            subject_button = self.create_button(self.subject_selection_window, 2, 10, subject, 15, 'blue',
                                        lambda s=subject:self.teacher_selection(s))  # in this lambda function s is defined as...
                                                                                     #... chosen subject  as a peramater...
                                                                                     #...for the function teacher_selection
            subject_button.place(x=x, y=y, height=80, width=150)
            i += 1  # reiterate by adding 1 to i after each loop finishes

    def teacher_selection(self,subject):  # function to select the teacher to the corresponding subject
        self.subject_selection_window.destroy()  # destroys the previous window
        self.selected_subject = subject  # use subject (from the previous function) as a reference

        # a dictionary subject_teachers is created to store lists of teachers to their corresponding subject
        subject_teachers = {
            'Math': ['Lili', 'Mike', 'Cevin', 'Alel', 'Khris', 'Lisa', 'Jolie'],
            'Physics': ['Dave', 'Michael C'],
            'Chemistry': ['Lili', 'Kadek', 'Kartika'],
            'Economics': ['Gaby', 'Helena'],
            'English': ['Lisa'],
            'Business': ['Gaby']
        }

        teachers = subject_teachers[subject]  # contains the value of the subject parameter based on the dictionary above
        num_teachers = len(teachers)  # set the number of rows needed for the teacher selection since different...
                                     # ...subjects have different amount of teachers
        num_columns = 2  # buttons for the teachers will have 2 columns
        num_rows = (num_teachers + num_columns - 1) // num_columns  # formula for hw many rows to fit all teachers given num_columns
        y_start = 150  # first row is 150 px from the top
        y_space = 100  # 100px of vertical space
        y_positions = [y_start + i * y_space for i in range(num_rows)]  # loops to create a list of y-positions of each row
        teacher_selectio_window_height = y_positions[-1] + y_space + 80   # trial end error for the vertical positions

        # create the teacher selection window based on the calculated height
        self.teacher_selection_window = tk.Toplevel()
        self.teacher_selection_window.resizable(False, False)
        self.teacher_selection_window.geometry(f'600x{teacher_selectio_window_height}')  # uses teacher_selection_window_height as vertical heigh
        self.teacher_selection_window.title('Teacher Selection')

        # text for teacher selection
        self.teacher_selection_text = self.create_text(
            self.teacher_selection_window,f"Select a teacher for {subject}", 17, 'center')  # uses subject as reference for the text
        self.teacher_selection_text.place(x=160, y=50)

        x_positions = [100,350]  # stores horizontal positions
        i = 0  # iterator of for loop below
        for teacher in teachers:
            x = x_positions[i % num_columns]  # return 100 if is even, otherwise return 350
            y = y_positions[i // num_columns]  # divides by number of columns and rounds it down
            teacher_button = self.create_button(self.teacher_selection_window, 2, 10, teacher, 15, 'blue',
                                                lambda t=teacher:self.attendance_confirmation(t))  # uses lambda function to carry...
                                                                                            #... parameter t for attendance_confirmation()
            teacher_button.place(x=x, y=y, height=80, width=150)
            i += 1  # reiterates i by adding 1 after each loop

        # add a back button at the bottom
        self.back_to_subject_selection_button  = self.create_button(self.teacher_selection_window, 2, 15,
                                                                    'Back', 15, 'grey', self.back_to_subject_selection
        )
        self.back_to_subject_selection_button.place(x=225, y=teacher_selectio_window_height - 100)

    def back_to_subject_selection(self):
        self.teacher_selection_window.destroy()  # if user decides to go back to the previous window, destroy current window...
        self.selected_subject = None  #... and erase the value of selected_subject
        self.subject_selection()  # reopen subject selection
    def attendance_confirmation(self,teacher):  # records teacher name and user name
        self.teacher_selection_window.destroy()  # destroy previous window
        self.selected_teacher = teacher  # self.selected_teacher will contain the selected teacher by the student
        self.attendance_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # record the time of attendance

        student_name = self.user  # record student name
        self.show_attendance_confirmation_window(student_name)  # calls function that takes the parameter student_name

    def show_attendance_confirmation_window(self,student_name):  # function for showing attendance confirmation window
        self.attendance_confirmation_window = tk.Toplevel(self.start_window)
        self.attendance_confirmation_window.resizable(False, False)
        self.attendance_confirmation_window.geometry('700x400')
        self.attendance_confirmation_window.title('Attendance Confirmation')
        attendance_information = (f"Name: {student_name}\nSubject: {self.selected_subject}\n"
                                  f"Teacher: {self.selected_teacher}\nTime: {self.attendance_time}")  # text that contains all attendance info
        self.attendance_information_text = self.create_text(self.attendance_confirmation_window,
                                                            attendance_information, 25, 'left')  # put the text above into tkinter text
        self.attendance_information_text.place(x=160, y=50)

        self.attendance_confirmation_close_button = self.create_button(self.attendance_confirmation_window, 2, 15,  # button to close window
                                                                       'Close', 15, 'grey', self.attendance_confirmation_window.destroy)
        self.attendance_confirmation_close_button.place(x=225, y=300)

        # calls insert_attendance function which inserts attendance information into the database
        self.insert_attendance(student_name,self.selected_subject,self.selected_teacher)

    def insert_attendance(self, student_name, subject_name, teacher_name):  # takes these 3 parameters needed for attendance
        self.attendance_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # record time
        try:  # if try fails, then go to exception error
            cursor = self.connection.cursor()  # connect database for commands using cursor
            #  check if student name exists. '?' takes a parameter, which we assign as student_name
            cursor.execute('SELECT student_id FROM Students WHERE name = ?;', (student_name,))
            student = cursor.fetchone()  # retrieves / fetches the first row from the set of that query
            if student is None:  # print statement does not exist
                print(f"Student {student_name} not found in the database.")
                return
            student_id = student[0]  # assigns it into a list if it does exist for future reference

            #  check if subject name exists. '?' takes a parameter, which we assign as subject_name
            cursor.execute('SELECT subject_id FROM Subjects WHERE name = ?;', (subject_name,))
            subject = cursor.fetchone()
            if subject is None:
                print(f"Subject {subject_name} not found in the database.")
                return
            subject_id = subject[0]

            #  check if teacher name exists. '?' takes a parameter, which we assign as teacher_name
            cursor.execute('SELECT teacher_id FROM Teachers WHERE name = ?;', (teacher_name,))
            teacher = cursor.fetchone()
            if teacher is None:
                print(f"Teacher {teacher_name} not found in the database.")
                return
            teacher_id = teacher[0]

            # after confirming no missing data, we insert the three parameters into the Attendance table in the database
            cursor.execute('''
                            INSERT INTO Attendance (student_id, subject_id, teacher_id, attendance_time)
                            VALUES (?, ?, ?, ?);
                        ''', (student_id, subject_id, teacher_id, self.attendance_time))
            self.connection.commit()  # permanently save by committing

            print(f"attended : {student_name} in {subject_name} with {teacher_name}.")
        except Error as e:  # prints sqlite3 error if try fails
            print(e)
    def add_image(self,label): # function for adding registration image
        img = ImageTk.PhotoImage(self.capture_pil)  # uses previously defined PIL image
        self.label_image = img  # stores the image in self.label_image
        label.configure(image=self.label_image)  # display the image
        self.register_image = self.capture.copy()  # duplicates the image into register_image

    def register(self):
        # create window for register
        self.register_window = tk.Toplevel(self.start_window)
        self.register_window.resizable(False, False)
        self.register_window.geometry('1000x600')
        self.register_window.title('Attendance Registration')

        # continue button
        self.register_continue_button = self.create_button(self.register_window, 2, 11,'Continue',15, 'Green',
                                                           self.register_continue)
        self.register_continue_button.place(x=5, y=280)

        # back button
        self.register_back_button = self.create_button(self.register_window, 2, 11,'Back', 15, 'Grey',
                                                       self.back_to_start_window)
        self.register_back_button.place(x=203, y=280)

        # frame for the face in th registration window
        self.register_face_frame = self.create_image_label(self.register_window)
        self.register_face_frame.place(x=350, y=30)

        # calls the add_image function
        self.add_image(self.register_face_frame)

        # input box
        self.register_input = self.create_input_text(self.register_window)
        self.register_input.place(x=12, y=165)

        # input text
        self.register_input_text = self.create_text(self.register_window, "Input your name below\nin lowercase and no spaces\n(eg.yannlecun)", 16, 'center')
        self.register_input_text.place(x=0, y=50)
    def back_to_start_window(self):  # destroys current window to go back to previous window
        self.register_window.destroy()

    def register_continue(self):
        # get the inputted name and check if a name is inputted, and parse if necessary
        name = self.register_input.get('1.0', 'end-1c').strip()
        if not name:  # error handling if name isn't inputted
            self.create_messagebox('Registration Error', 'Please enter a name.')
            return

        # calls the insert_student function to insert the student's name in the database if successful
        success = self.insert_student(name)
        if not success:
            self.register_window.destroy()
            return

        # check if the image captured contains a face
        img_rgb = cv2.cvtColor(self.register_image, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img_rgb)
        if len(encodings) == 0:  # this means that there is no face detected as the array is nonexistent
            self.create_messagebox('Registration Error', 'No face detected in the image. Please try again.')
            self.delete_student(name)  # deletes information of the student using delete_student function
            self.register_window.destroy()
            return

        # define the path directory as "Images"
        img_path = os.path.join('Images', f'{name}.jpg')

        # check if the path exists, make path if it does not
        if not os.path.exists('Images'):
            os.makedirs('Images')

        # save the captured image to the 'Image' directory
        cv2.imwrite(img_path, self.register_image)
        self.show_register_loading_screen()

        # start the encoding process into a different thread
        threading.Thread(target=self.update_encodings, args=(name,), daemon=True).start()

    def insert_student(self, name):
        try:
            cursor = self.connection.cursor()
            # insert name and registration_date of registry in the database
            cursor.execute('INSERT INTO Students (name, registration_date) VALUES (?, ?);', (name, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            self.connection.commit()  # commits action
            print(f"Student {name} registered in the database.")  # print statement in the terminal just to confirm
            return True
        except sqlite3.IntegrityError:  # exception error if the name that the user inputted is already inside the database
            self.create_messagebox('Registration Error', f'The name "{name}",please try again.')
            return False
        except Error as e: # exception for other sqlite3 errors
            print(e)
            return False

    def delete_student(self, name):  # function for deleting a student in the database
        try:
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM Students WHERE name = ?;', (name,))
            self.connection.commit()
            print(f"Student {name} deleted from the database.")
        except Error as e:
            print(e)

    def show_register_loading_screen(self):  # window to notify users that registration is in process
        self.register_loading_window = tk.Toplevel(self.register_window)
        self.register_loading_window.resizable(False, False)
        self.register_loading_window.geometry('300x200')
        self.register_loading_window.title('Registration Loading')

        # register loading text
        self.register_loading_text = self.create_text(self.register_loading_window,'Registration processing,\nplease wait...',13, 'center')
        self.register_loading_text.pack(expand=True)
        self.register_waiting_text = self.create_text(self.register_loading_window, '(This should take less than 30 seconds)', 10, 'center')
        self.register_waiting_text.pack(expand=True)

    def update_encodings(self, name):  # updates the file encode.p with  the new registered face encodings
        img_path = 'Images'  # declare image path directory
        img_path_list = os.listdir(img_path)  # gives a list of all files and directories inside a list

        student_list = []  # this will hold the actual image data of the students loaded from opencv library
        student_name = []  # this will contain the corresponding name from the filenames

        for student in img_path_list:  # loops through every student in img_path_list
            img = cv2.imread(os.path.join(img_path, student))  # loads the image into a numpy array
            if img is not None:  # if image exists
                student_list.append(img)  # append the numpy array to student_list
                student_name.append(os.path.splitext(student)[0])  # parses the file type (.jpg, .png, etc.) and appends the name into student_name
            else:  # if image does not exist
                print(f"Failed to load {student}")

        def find_encodings(student_list, student_name):  # a function defined in update_encodings to find encodings of the student
            encoding_list = []  # will contain the encodings of students that have facial features
            valid_student_name = []  # will contain names of students that have actual faces in their image
            for i, s,in enumerate(student_list):  # loops through the index 'i' and the image data 's'
                student_rgb = cv2.cvtColor(s, cv2.COLOR_BGR2RGB)  # changes the default BGR into RGB, a standard format
                encodings = face_recognition.face_encodings(student_rgb)  # use built-in functions in the face recognition library...
                                                                        #... by Adam Geitgey, and finds faces in student_rgb and produce an...
                                                                        #...encoding vector for each face found
                if len(encodings) > 0:  # if the encodings isn't empty, which means that there is a face found
                    encoded = encodings[0]  # append the first encoding into encoding_list
                    encoding_list.append(encoded)
                    valid_student_name.append(student_name[i])  # append the corresponding student name into valid_student_name
                else:  # otherwise, no face is found and returns an error statement
                    print(f"No face found in {student_name[i]}")
            return encoding_list, valid_student_name

        print("encoding start")  # print statement in the terminal to confirm that encoding process has started

        # known_encodings is a  list of all encoding vectors for each valid/existing image
        # valid_student name is a  list of names corresponding to each encoding vector
        known_encodings, valid_student_name = find_encodings(student_list, student_name)
        known_encodings_student = [known_encodings, valid_student_name]  # create one combined list that holds both encodings and their names
        print("encoding end")  # print statement in the terminal to confirm that encoding process has ended

        # open a file named encodings.p, in binary write mode ('wb')
        with open("encodings.p",'wb') as f:  # uses pickle library to convert known_encodings_student into binary
            pickle.dump(known_encodings_student, f)  # save encodings to instantly have all known faces without needing to redo the encodings
        print("encoding saved")  # print statement for confirmation

        # save the encoding list after registration is done so that the code doesn't need to be rerun after each registration
        self.known_encoding_list, self.student = known_encodings_student
        self.start_window.after(0, self.encoding_done, name)

    def encoding_done(self, name):
        self.register_loading_window.destroy()  # destroy the register loading window if the encoding process finishes
        # create a messagebox that notifies the users that the registration process is successful
        self.create_messagebox('Registration Success', f'Successfully registered as {name}. You can now login')
        self.register_window.destroy()

if __name__ == '__main__':
    app = App()
    app.run()