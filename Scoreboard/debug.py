# can send data to server scoreboard & itself,
# closes socket connections too early but putting .close()
# outside of while loop causes program to crash

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QSettings

from scoreboard import Ui_MainWindow
from client import ClientThread
from server import ServerThread

class MainWindow(QMainWindow):
    def __init__(self, role):
        super(MainWindow, self).__init__()
        self.role = role
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.client_thread = ClientThread(role)
        self.client_thread.new_data.connect(self.process_data)
        self.client_thread.start()

        if role == 'scoreboard':
            self.ui.stackedWidget.setCurrentIndex(0)
            self.ui.scoreboard_btn1.setChecked(True)
            
            self.server_thread = ServerThread()
            self.server_thread.new_data.connect(self.process_data)
            self.server_thread.start()

        elif role == 'blue_console':
            self.ui.stackedWidget.setCurrentIndex(1)
            self.ui.blue_btn1.setChecked(True)
        elif role == 'red_console':
            self.ui.stackedWidget.setCurrentIndex(2)
            self.ui.red_btn1.setChecked(True)

        self.ui.iconMenu.hide() #load with full menu open

        self.subtotal1 = 0 #change to num*worth once values are reloadable
        self.subtotal2 = 0
        self.subtotal3 = 0
        self.subtotal4 = 0
        self.subtotal5 = 0
        self.subtotal6 = 0
        self.subtotal7 = 0
        self.subtotal8 = 0
        self.subtotal9 = 0
        self.subtotal10 = 0

        self.ui.totalScore0.display(f"{self.ui.totalScore0.intValue():03}") #making score load as three 000
        self.ui.totalScore1.display(f"{self.ui.totalScore1.intValue():03}")
        self.ui.blueScore.display(f"{self.ui.totalScore0.intValue():03}")
        self.ui.redScore.display(f"{self.ui.totalScore1.intValue():03}")

        # making objectives reloadable, & toggling between edit/save
        self.settings = QSettings("GoDs", "ScoreboardConsole")
        # self.objs = {"obj1": self.ui.obj1, #creating dict of objectives from each lineEdit
        #              "obj2": self.ui.obj2,
        #              "obj3": self.ui.obj3,
        #              "obj4": self.ui.obj4,
        #              "obj5": self.ui.obj5,
        #              "obj6": self.ui.obj6,
        #              "obj7": self.ui.obj7,
        #              "obj8": self.ui.obj8,
        #              "obj9": self.ui.obj9,
        #              "obj10": self.ui.obj10,
        #              }
        self.objs = {f"obj{i+1}": getattr(self.ui, f"obj{i+1}") for i in range(10)}

        self.loadObjectives()

        self.ui.editSavebtn0.setText("Edit")
        self.ui.editSavebtn1.setText("Edit")
        self.ui.editSavebtn0.clicked.connect(self.toggle_editSave)
        self.ui.editSavebtn1.clicked.connect(self.toggle_editSave)
        self.editableObjs(False)

        # updating points, adds to subtotal everytime the points change
        self.ui.obj1Num.valueChanged.connect(self.updateSubtotal1) #1
        self.ui.obj1Worth.valueChanged.connect(self.updateSubtotal1) 
        self.ui.obj2Num.valueChanged.connect(self.updateSubtotal2) #2
        self.ui.obj2Worth.valueChanged.connect(self.updateSubtotal2)
        self.ui.obj3Num.valueChanged.connect(self.updateSubtotal3) #3
        self.ui.obj3Worth.valueChanged.connect(self.updateSubtotal3)
        self.ui.obj4Num.valueChanged.connect(self.updateSubtotal4) #4
        self.ui.obj4Worth.valueChanged.connect(self.updateSubtotal4)
        self.ui.obj5Num.valueChanged.connect(self.updateSubtotal5) #5
        self.ui.obj5Worth.valueChanged.connect(self.updateSubtotal5)
        self.ui.obj6Num.valueChanged.connect(self.updateSubtotal6) #6
        self.ui.obj6Worth.valueChanged.connect(self.updateSubtotal6)
        self.ui.obj7Num.valueChanged.connect(self.updateSubtotal7) #7
        self.ui.obj7Worth.valueChanged.connect(self.updateSubtotal7)
        self.ui.obj8Num.valueChanged.connect(self.updateSubtotal8) #8
        self.ui.obj8Worth.valueChanged.connect(self.updateSubtotal8)
        self.ui.obj9Num.valueChanged.connect(self.updateSubtotal9) #9
        self.ui.obj9Worth.valueChanged.connect(self.updateSubtotal9)
        self.ui.obj10Num.valueChanged.connect(self.updateSubtotal10) #10
        self.ui.obj10Worth.valueChanged.connect(self.updateSubtotal10)

        self.ui.sendTotal0.clicked.connect(self.updateTotal0)
        self.ui.sendTotal1.clicked.connect(self.updateTotal1)


        # navigate between pages from menu buttons
        # using anonymous function lambda to avoid defining simple function needed to connect with button
        self.ui.scoreboard_btn1.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.scoreboard_btn2.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0)) 
        self.ui.blue_btn1.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.blue_btn2.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.red_btn1.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(2)) 
        self.ui.red_btn2.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(2))

    def process_data(self, data):
        print(f"Processing data: {data}")
        command, value = data.split(':')
        if command == 'blue_score':
            self.ui.blueScore.display(f"{int(value):03}")
        elif command == 'red_score':
            self.ui.redScore.display(f"{int(value):03}")
        elif command == 'game_time':
            pass

    # function to reload objectives upon opening/closing app
    def loadObjectives(self):
        for key, objective in self.objs.items():
            savedObj = self.settings.value(key, "")
            objective.setText(savedObj)

    # function to save objectives to be reloaded upon opening/closing app
    def saveObjectives(self):
        for key, objective in self.objs.items():
            self.settings.setValue(key, objective.text())

    # setting objectives to be read only if not editable
    # (False is passed as a parameter of the function)
    def editableObjs(self, editable):
        for objective in self.objs.values():
            objective.setReadOnly(not editable)

    # functionality of edit/save button
    # if button is on Edit, change to Save, leave objectives as editable Line Edits
    # else if button is on Save, change to Edit and set objectives to Read Only
    def toggle_editSave(self):
        if self.ui.editSavebtn0.text() == "Edit":
            self.editableObjs(True)
            self.ui.editSavebtn0.setText("Save")
        if self.ui.editSavebtn1.text() == "Edit":
            self.editableObjs(True)
            self.ui.editSavebtn1.setText("Save")
        else:
            self.editableObjs(False)
            self.saveObjectives()
            self.ui.editSavebtn0.setText("Edit")
            self.ui.editSavebtn1.setText("Edit")

    # function to save objectives upon closing
    def closeEvent(self, event):
        self.saveObjectives()
        event.accept()
    
    # functions to update subtotal of each objective, change value & display
    def updateSubtotal1(self):
        self.subtotal1 = self.ui.obj1Num.value() * self.ui.obj1Worth.value()
        self.ui.obj1Score.setText(str(self.subtotal1))
    def updateSubtotal2(self):
        self.subtotal2 = self.ui.obj2Num.value() * self.ui.obj2Worth.value()
        self.ui.obj2Score.setText(str(self.subtotal2))
    def updateSubtotal3(self):
        self.subtotal3 = self.ui.obj3Num.value() * self.ui.obj3Worth.value()
        self.ui.obj3Score.setText(str(self.subtotal3))
    def updateSubtotal4(self):
        self.subtotal4 = self.ui.obj4Num.value() * self.ui.obj4Worth.value()
        self.ui.obj4Score.setText(str(self.subtotal4))
    def updateSubtotal5(self):
        self.subtotal5 = self.ui.obj5Num.value() * self.ui.obj5Worth.value()
        self.ui.obj5Score.setText(str(self.subtotal5))
    def updateSubtotal6(self):
        self.subtotal6 = self.ui.obj6Num.value() * self.ui.obj6Worth.value()
        self.ui.obj6Score.setText(str(self.subtotal6))
    def updateSubtotal7(self):
        self.subtotal7 = self.ui.obj7Num.value() * self.ui.obj7Worth.value()
        self.ui.obj7Score.setText(str(self.subtotal7))
    def updateSubtotal8(self):
        self.subtotal8 = self.ui.obj8Num.value() * self.ui.obj8Worth.value()
        self.ui.obj8Score.setText(str(self.subtotal8))
    def updateSubtotal9(self):
        self.subtotal9 = self.ui.obj9Num.value() * self.ui.obj9Worth.value()
        self.ui.obj9Score.setText(str(self.subtotal9))
    def updateSubtotal10(self):
        self.subtotal10 = self.ui.obj10Num.value() * self.ui.obj10Worth.value()
        self.ui.obj10Score.setText(str(self.subtotal10))
    
    # functions to update total score of each team
    def updateTotal0(self):
        self.totalScore0 = self.subtotal1 + self.subtotal2 + self.subtotal3 + self.subtotal4 + self.subtotal5
        self.ui.totalScore0.display(f"{self.totalScore0:03}")
        # self.ui.blueScore.display(f"{self.totalScore0:03}")
        self.client_thread.send_data(f'blue_score:{self.totalScore0}')

    def updateTotal1(self):
        self.totalScore1 = self.subtotal6 + self.subtotal7 + self.subtotal8 + self.subtotal9 + self.subtotal10
        self.ui.totalScore1.display(f"{self.totalScore1:03}")
        # self.ui.redScore.display(f"{self.totalScore1:03}")
        self.client_thread.send_data(f'red_score:{self.totalScore1}')

if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open("style.qss", "r") as style_file: #loading style file
        style_str = style_file.read()

    app.setStyleSheet(style_str)

    if len(sys.argv) > 1:
        role = sys.argv[1]
    else:
        role = 'scoreboard'
        
    window = MainWindow(role)
    window.show()

    sys.exit(app.exec())


# server.py

from PyQt5.QtCore import QThread, pyqtSignal
import socket
import threading

class ServerThread(QThread):
    new_data = pyqtSignal(str)

    def __init__(self, host='0.0.0.0', port=12346):
        super(ServerThread, self).__init__()
        self.host = host
        self.port = port
        self.clients = []

    def run(self):
        print("Server is running..")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print("Server listening on port", self.port)

        while True: #looking for connections
            try:
                print(f"server socket: {server_socket}")
                client_socket, addr = server_socket.accept()
                print(f"Accepted connection from {addr}")
                self.clients.append(client_socket)
                threading.Thread(target=self.handle_client, args=(client_socket,)).start()
            except:
                continue

    def handle_client(self, client_socket):
        while True:
            # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # client_socket.connect((self.host, self.port))
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    print("Client disconnected")
                    break
                print(f"Received data: {data}")
                self.new_data.emit(data)
                self.broadcast(data)
            except Exception as e:
                print(f"Error handling client data: {e}")
                break
            print("Closing client socket")
            client_socket.close()
            print("Removing client from the list")
            self.clients.remove(client_socket)

    def broadcast(self, message):
        print(f"Broadcasting message: {message}")
        for client_socket in self.clients:
            try:
                client_socket.sendall(message.encode('utf-8'))
            except Exception as e:
                print(f"Error broadcasting to client: {e}")
                self.clients.remove(client_socket)


# client.py
 
from PyQt5.QtCore import QThread, pyqtSignal
import socket
import threading

class ClientThread(QThread):
    new_data = pyqtSignal(str)

    def __init__(self, role, host='127.0.0.1', port=12346):
        super(ClientThread, self).__init__()
        self.host = host
        self.port = port
        self.role = role

    def run(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            threading.Thread(target=self.listen_for_data).start()
        except Exception as e:
            print(f"Connection error: {e}")

    def listen_for_data(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode('utf-8')
                if data:
                    print(f"Received data: {data}")
                    self.new_data.emit(data)
            except:
                break

    def send_data(self, data):
        try:
            # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # client_socket.settimeout(5)
            # print(f"Attempting to connect to the server...")
            # client_socket.connect(('127.0.0.1', 12346))
            # print(f"Connected to the server")
            self.client_socket.sendall(data.encode('utf-8'))
            print(f"Sent data: {data}")
            # self.client_socket.close()
            reply = self.client_socket.recv(1024).decode('utf-8')
            print(f"Received reply: {reply}")
        except socket.error as e:
            print(f"Error sending data: {e}")

    def broadcast(self, message):
        for client_socket in self.clients:
            try:
                client_socket.sendall(message.encode('utf-8'))
            except:
                self.clients.remove(client_socket)