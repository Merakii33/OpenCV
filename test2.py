import cv2
import mediapipe as mp
import numpy as np
import serial

def get_str_guester(up_fingers, list_lms):
    # 在这里编写您的手势识别逻辑
    return "Guesture"

if __name__ == "__main__":
    mpHands = mp.solutions.hands
    hands = mpHands.Hands()
    mpDraw = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)

    serial_port = "COM3"  # 根据实际情况修改串口号
    serial_baud = 9600
    serial_timeout = 1
    try:
        serial = serial.Serial(serial_port, serial_baud, timeout=serial_timeout)
        print("Serial port opened successfully")
    except serial.SerialException:
        print("Failed to open serial port")

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            print("Error reading frame")
            break

        image_height, image_width, _ = frame.shape
        imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            mpDraw.draw_landmarks(frame, hand, mpHands.HAND_CONNECTIONS)

            list_lms = []
            for i in range(21):
                pos_x = hand.landmark[i].x * image_width
                pos_y = hand.landmark[i].y * image_height
                list_lms.append([int(pos_x), int(pos_y)])

            list_lms = np.array(list_lms, dtype=np.int32)
            hull_index = [0, 1, 2, 3, 6, 10, 14, 19, 18, 17, 10]
            hull = cv2.convexHull(list_lms[hull_index, :])
            cv2.polylines(frame, [hull], True, (0, 255, 0), 2)

            ll = [4, 8, 12, 16, 20]
            up_fingers = []

            for i in ll:
                pt = (int(list_lms[i][0]), int(list_lms[i][1]))
                dist = cv2.pointPolygonTest(hull, pt, True)
                if dist < 0:
                    up_fingers.append(i)

            str_guesture = get_str_guester(up_fingers, list_lms)
            cv2.putText(frame, ' %s' % str_guesture, (90, 90), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 0), 4, cv2.LINE_AA)

            for i in ll:
                pos_x = hand.landmark[i].x * image_width
                pos_y = hand.landmark[i].y * image_height
                cv2.circle(frame, (int(pos_x), int(pos_y)), 3, (0, 255, 255), -1)

        cv2.imshow("hands", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break

    try:
        if serial.isOpen():
            serial.write(str_guesture.encode())
    except serial.SerialException:
        print("Failed to write to serial")
    cap.release()
    cv2.destroyAllWindows()
    serial.close()