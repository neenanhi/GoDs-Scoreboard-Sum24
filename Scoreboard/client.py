from PyQt5.QtCore import QObject, pyqtSignal, QThread
import socket
import threading

class ClientThread(QThread):
    new_data = pyqtSignal(str)

    def __init__(self, role):
        super(ClientThread, self).__init__()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', 12346))
        self.running = True
        threading.Thread(target=self.receive_data, daemon=True).start()

    # def run(self):
    #     while self.running:
    #         data = self.receive_data()
    #         if 'timer:start'in data:
    #             _,_,hh,mm,ss = data.split(':')
    #             self..startTimer

    def receive_data(self):
        buffer = ""
        while self.running:
            try:
                data = self.client_socket.recv(1024).decode()
                if data:
                    buffer += data
                    while '\n' in buffer:
                        command, buffer = buffer.split('\n', 1)
                        print(f"Received data: {data}")
                        self.new_data.emit(data)
            except:
                self.running = False
                self.client_socket.close()

    def send_data(self, data):
        try:
            self.client_socket.sendall((data + '\n').encode())
            print(f"Sent data: {data}")
        except:
            self.running = False
            self.client_socket.close()

    def stop(self):
        self.running = False
        self.client_socket.close()
