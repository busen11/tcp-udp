import cv2, socket, pickle, struct, threading

server_ip = "10.15.184.117"  # Sunucunun IP adresi
port = 9999  # TCP portu

# TCP soketi oluştur
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_ip, port))
server_socket.listen(1)
print(f"Sunucu {server_ip}:{port} adresinde dinleniyor...")

conn, addr = server_socket.accept()  # İstemciden bağlantı bekle
print(f"Baglanti alindi: {addr}")

vid = cv2.VideoCapture(0)  # Kameradan görüntü al

# Video Gönderme Fonksiyonu
def send_video():
    while True:
        _, frame = vid.read()
        data = pickle.dumps(frame)  # Görüntüyü serileştir (byte'a çevir)
        conn.sendall(struct.pack("Q", len(data)) + data)  # Veri uzunluğu + görüntü gönder

# Video Alma Fonksiyonu
def receive_video():
    data = b""
    payload_size = struct.calcsize("Q")

    while True:
        while len(data) < payload_size:
            packet = conn.recv(4 * 1024)  # Veri al (buffer boyutu)
            if not packet: 
                break
            data += packet

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q", packed_msg_size)[0]

        while len(data) < msg_size:
            data += conn.recv(4 * 1024)

        frame_data = data[:msg_size]
        data = data[msg_size:]
        frame = pickle.loads(frame_data)  # Byte'ı tekrar görüntüye çevir
        cv2.imshow("Client Video", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# İki fonksiyonu eş zamanlı çalıştırmak için Thread kullanıyoruz
t1 = threading.Thread(target=send_video)
t2 = threading.Thread(target=receive_video)

t1.start()
t2.start()

t1.join()
t2.join()

conn.close()
server_socket.close()
cv2.destroyAllWindows()
