import cv2
import requests
import time

API_URL = "http://localhost:8000/detect"

video_path = "videos/sample.mp4"

DETECT_EVERY_N_FRAMES = 3

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

fram_count = 0

while True:
    read_result = cap.read()
    ret = read_result[0]
    frame = read_result[1]

    if ret is False:
        print("End of video or cannot read frame.")
        break

    fram_count += 1

    if fram_count % DETECT_EVERY_N_FRAMES != 0:
        cv2.imshow("Smart Surveillance", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("User requested to quit.")
            break
        time.sleep(0.03)
        continue

    encode_result = cv2.imencode('.jpg', frame)

    encode_success = encode_result[0]
    encoded_image = encode_result[1]

    if encode_success is True:
        image_bytes = encoded_image.tobytes()

        file_tuple = ('frame.jpg', image_bytes, 'image/jpeg')
        files_dictionary = {'file': file_tuple}

        try:
            response = requests.post(API_URL, files=files_dictionary)

            status_code = response.status_code
            if status_code == 200:
                response_json = response.json()

                if "detections" in response_json:
                    detections = response_json["detections"]

                    for detection in detections:
                        label = detection["label"]
                        confidence = detection["confidence"]
                        bbox = detection["bbox"]

                        x1 = bbox[0]
                        y1 = bbox[1]
                        x2 = bbox[2]
                        y2 = bbox[3]

                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                        confidence_text = f"{label} {confidence:.2f}"

                        cv2.putText(
                            frame,                       
                            confidence_text,           
                            (x1, y1 - 10),               
                            cv2.FONT_HERSHEY_SIMPLEX,  
                            0.5,                        
                            (0, 255, 0),               
                            2                           
                        )
                else:
                    print("Warning: 'detections' not found in response JSON.")
            else:
                error_text = response.text
                print("Detection API returned error:", error_text)

        except Exception as error:
            error_message = str(error)
            print("Error while sending frame to detection API:", error_message)

    else:
        print("Error: Could not encode frame as JPEG.")

    cv2.imshow("Smart Surveillance", frame)

    key_pressed = cv2.waitKey(1)
    q_key_code = ord('q')
    key_is_q = (key_pressed & 0xFF) == q_key_code

    if key_is_q:
        print("User requested to quit.")
        break

    time.sleep(0.03)

cap.release()
cv2.destroyAllWindows()