Face Recognition Project

A Python application that uses OpenCV and face recognition to detect and recognize faces in real time via webcam.
This project loads known images, encodes them, and then identifies faces when they appear in the camera feed.

Features:
Load & Encode Images - add known faces form an images/ folder
Real time recognition - uses OpenCV to capture live video
Face Detection - draws bounding boxes and labels around detected faces

Libraries:
- [OpenCV](https://opencv.org/) – for video capture and image processing
- [face_recognition](https://github.com/ageitgey/face_recognition) – for facial encodings & recognition
- [numpy](https://numpy.org/) – array operations