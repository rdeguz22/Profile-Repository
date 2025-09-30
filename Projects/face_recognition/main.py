import cv2
from simple_recognition import SimpleRecognition


class Main:
    def __init__(self, images_path="images/"):
        self.sfr = SimpleRecognition()
        self.sfr.load_encoding_images(images_path)

    def run(self):
        capture = cv2.VideoCapture(0)

        while True:
            ret, frame = capture.read()
            if not ret:
                break

            face_locations, face_names = self.sfr.detect_known_faces(frame)

            for face_loc, name in zip(face_locations, face_names):
                y1, x2, y2, x1 = face_loc
                cv2.putText(frame, name, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 200, 200), 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2),
                              (0, 200, 200), 4)

            cv2.imshow("Frame", frame)

            key = cv2.waitKey(1)
            if key == 27:
                break

        capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    app = Main(images_path="images/")
    app.run()