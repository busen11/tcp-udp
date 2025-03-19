import cv2, imutils, socket, numpy as np
import threading

BUFF_SIZE = 65536
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_ip = "10.15.184.117"
port = 9999
client_socket.sendto(b"HELLO", (server_ip, port))  # Bağlantıyı başlat

# ** Video Gönderme **
def send_video():
    vid = cv2.VideoCapture(0)

    while True:
        _, frame = vid.read()
        frame = imutils.resize(frame, width=400)
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        client_socket.sendto(buffer.tobytes(), (server_ip, port))  # Direkt byte olarak gönder

        cv2.imshow("CLIENT (Gonderilen)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# ** Video Alma **
def receive_video():
    while True:
        packet, _ = client_socket.recvfrom(BUFF_SIZE)
        frame = np.frombuffer(packet, dtype=np.uint8)
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

        if frame is not None:
            cv2.imshow("CLIENT (Alinan)", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# ** Thread'leri Başlat **
t1 = threading.Thread(target=send_video)
t2 = threading.Thread(target=receive_video)

t1.start()
t2.start()

t1.join()
t2.join()

client_socket.close()
cv2.destroyAllWindows()
