from PyQt5.QtCore import QObject, pyqtSignal, QThread
import socket
import threading

class ServerThread(QThread):
    new_data = pyqtSignal(str)

    def __init__(self):
        super(ServerThread, self).__init__()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', 12346))
        self.server_socket.listen(5)
        self.clients = []
        self.running = True

        #starting accept_connections thread
        threading.Thread(target=self.accept_connections, daemon=True).start()

    def accept_connections(self):
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                self.clients.append(client_socket)
                threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
            except OSError:
                break

    def handle_client(self, client_socket):
        while self.running:
            # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # client_socket.connect((self.host, self.port))
            try:
                data = client_socket.recv(1024).decode()
                if data:
                    self.new_data.emit(data)
                    self.broadcast(data)
                else:
                    break
            except (OSError, ConnectionResetError):
                break
        self.remove_client(client_socket)
        client_socket.close()

    def broadcast(self, message):
        for client in self.clients:
            try:
                client.sendall((message + '\n').encode())
            except OSError:
                self.remove_client(client)
                client.close()

    def remove_client(self, client_socket):
        if client_socket in self.clients:
            self.clients.remove(client_socket)

    def stop(self):
        self.running = False
        for client in self.clients:
            client.close()
        self.clients.clear()
        try:
            self.server_socket.close()
        except OSError:
            pass