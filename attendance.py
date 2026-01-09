from tkinter import *
from tkinter import filedialog
import cv2
import boto3
import time

# AWS Rekognition client (keeping your keys for now)
session = boto3.Session(
    aws_access_key_id='YOUR_AWS_ACCESS_KEY',
    aws_secret_access_key='YOUR_AWS_SECRET_KEY',
)
rek = session.client('rekognition', 'us-east-1')


def start_facial_recognition():
    cap = cv2.VideoCapture(0)
    last_capture_time = 0
    name = ''

    while True:
        ret, img = cap.read()
        if not ret:
            break

        # Process the face every 5 seconds
        if time.time() - last_capture_time > 5:
            last_capture_time = time.time()
            cv2.imwrite('opencv.png', img)
            with open('opencv.png', 'rb') as image_file:
                try:
                    response = rek.search_faces_by_image(
                        CollectionId='585',
                        Image={'Bytes': image_file.read()}
                    )

                    if response['FaceMatches']:
                        name = response['FaceMatches'][0]['Face']['ExternalImageId']
                    else:
                        name = "Unknown"

                    print(response)

                except Exception as e:
                    print("Failed to get the face:", e)

        cv2.putText(img, name, (200, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
        cv2.imshow('Face Recognition', img)

        if cv2.waitKey(30) & 0xFF == 27:  # ESC to quit
            break

    cap.release()
    cv2.destroyAllWindows()


def new_student():
    student_name = NewStudent_name.get().strip()
    if not student_name:
        print("Please enter a student name.")
        return

    print(f"Creating new student: {student_name}")
    cap = cv2.VideoCapture(0)
    time.sleep(2)
    ret, image = cap.read()
    cap.release()

    if not ret:
        print("Failed to capture image.")
        return

    filename = f'opencv_{int(time.time())}.png'
    cv2.imwrite(filename, image)

    with open(filename, 'rb') as image_file:
        response = rek.index_faces(
            CollectionId='585',
            Image={'Bytes': image_file.read()},
            ExternalImageId=student_name
        )
        print(response)


def upload_image():
    student_name = NewStudent_name.get().strip()
    if not student_name:
        print("Please enter a student name.")
        return

    file_path = filedialog.askopenfilename()
    if not file_path:
        return

    with open(file_path, 'rb') as image_file:
        response = rek.index_faces(
            CollectionId='585',
            Image={'Bytes': image_file.read()},
            ExternalImageId=student_name
        )
        print(response)


# ----------------- Tkinter UI -----------------
root = Tk()
root.title("Face Recognition Attendance")
root.geometry("800x200")

Label(root, text="Enter Student Name:").grid(row=0, column=0, padx=5, pady=5)
NewStudent_name = Entry(root)
NewStudent_name.grid(row=0, column=1, padx=5, pady=5)

Button(root, text="Take Picture of New Student", command=new_student).grid(row=0, column=2, padx=5)
Button(root, text="Upload Image of New Student", command=upload_image).grid(row=0, column=3, padx=5)
Button(root, text="Take Attendance", command=start_facial_recognition).grid(row=1, column=1, columnspan=2, pady=20)

root.mainloop()
