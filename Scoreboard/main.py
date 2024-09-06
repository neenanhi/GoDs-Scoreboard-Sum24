import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog
from PyQt5.QtCore import QSettings, QTimer

from scoreboard import Ui_MainWindow
from client import ClientThread
from server import ServerThread

class MainWindow(QMainWindow):
    def __init__(self, role):
        super(MainWindow, self).__init__()
        self.role = role
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        if role == 'scoreboard':
            self.ui.stackedWidget.setCurrentIndex(0)
            self.ui.scoreboard_btn1.setChecked(True)
            
            self.server_thread = ServerThread()
            self.server_thread.new_data.connect(self.process_data)
            self.server_thread.start()

        elif role == 'blue_console':
            self.ui.stackedWidget.setCurrentIndex(1)
            self.ui.blue_btn1.setChecked(True)
            self.client_thread = ClientThread(role)

            # whenever client thread receives new data from server,
            # it emits the new_data signal to trigger process data function
            self.client_thread.new_data.connect(self.process_data)

        elif role == 'red_console':
            self.ui.stackedWidget.setCurrentIndex(2)
            self.ui.red_btn1.setChecked(True)
            self.client_thread = ClientThread(role)
            self.client_thread.new_data.connect(self.process_data)

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

        self.phases = {
            "Red Prep": (0,0,0),
            "Blue Prep": (0,0,0),
            "Transition Period": (0,0,0),
            "Game Time": (0,0,0),
        }

        self.totalTime = (0,0,0)
        self.timerRunning = False
        self.currentPhaseIndex = 0
        self.updatePhaseDisplay()

        self.ui.nextPhase_btn.clicked.connect(self.nextPhase)
        self.ui.backPhase_btn.clicked.connect(self.backPhase)
        self.ui.startpause.clicked.connect(self.toggle_startPause)
        self.ui.reset.clicked.connect(self.resetTimer)
        self.ui.cancel.clicked.connect(self.cancelTimer)

        self.ui.lcdHours.mousePressEvent = self.editHours
        self.ui.lcdMins.mousePressEvent = self.editMins
        self.ui.lcdSecs.mousePressEvent = self.editSecs

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
        sub1 = self.ui.obj1Score.setText(str(self.subtotal1))
        if self.role != 'blue_console': self.client_thread.send_data(sub1)
    def updateSubtotal2(self):
        self.subtotal2 = self.ui.obj2Num.value() * self.ui.obj2Worth.value()
        sub2 = self.ui.obj2Score.setText(str(self.subtotal2))
        if self.role != 'blue_console': self.client_thread.send_data(sub2)
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
    # updated score data is sent to server
    # data is then broadcasted to all clients in network
    # clients receive data & then process it to update the score display on each client's UI
    def updateTotal0(self):
        self.totalScore0 = self.subtotal1 + self.subtotal2 + self.subtotal3 + self.subtotal4 + self.subtotal5
        self.ui.totalScore0.display(f"{self.totalScore0:03}")
        score = f'blue_score: {self.totalScore0}'
        self.process_data(score)
        if self.role != 'scoreboard':
            self.client_thread.send_data(score)

    def updateTotal1(self):
        self.totalScore1 = self.subtotal6 + self.subtotal7 + self.subtotal8 + self.subtotal9 + self.subtotal10
        self.ui.totalScore1.display(f"{self.totalScore1:03}")
        score = f'red_score: {self.totalScore1}'
        self.process_data(score)
        if self.role != 'scoreboard':
            self.client_thread.send_data(score)

    def updatePhaseDisplay(self):
        phaseName = list(self.phases.keys())[self.currentPhaseIndex]
        phaseHrs, phaseMins, phaseSecs = self.phases[phaseName]
        self.ui.phaseLabel.setText(phaseName)

        if self.currentPhaseIndex == 0:
            self.ui.phaseLabel.setStyleSheet("color: red;")
        elif self.currentPhaseIndex == 1:
            self.ui.phaseLabel.setStyleSheet("color: blue;")
        else:
            self.ui.phaseLabel.setStyleSheet("color: black;")

        self.updateClockDisplay(phaseHrs, phaseMins, phaseSecs)

    def nextPhase(self):
        if self.currentPhaseIndex < (len(self.phases) - 1):
            self.currentPhaseIndex += 1
            self.updatePhaseDisplay()

            if hasattr(self, 'server_thread'):
                    self.server_thread.broadcast(f"phase:change:{self.currentPhaseIndex}\n")
            elif hasattr(self, 'client_thread'):
                self.client_thread.send_data(f"phase:change:{self.currentPhaseIndex}\n")

    def backPhase(self):
        if self.currentPhaseIndex > 0:
            self.currentPhaseIndex -= 1
            self.updatePhaseDisplay()

    def calcTotalTime(self):
        totalHours = sum(phase[0] for phase in self.phases.values())
        totalMins = sum(phase[1] for phase in self.phases.values())
        totalSecs = sum(phase[2] for phase in self.phases.values())

        totalMins += totalSecs // 60
        totalSecs %= 60
        totalHours += totalMins // 60
        totalMins %= 60

        self.totalTime = (totalHours, totalMins, totalSecs)
        print(f"total caclulated time: {self.totalTime}")
    
    def startTimer(self):
        print("startTimer called") 
        if not self.timerRunning: #if not unpausing and in different phase, start from first phase
            print(f"Starting from first phase: {self.currentPhaseIndex}")
            if self.currentPhaseIndex != 0:
                self.currentPhaseIndex = 0
                if hasattr(self, 'server_thread'):
                    self.server_thread.broadcast(f"phase:change:{self.currentPhaseIndex}\n")
                elif hasattr(self, 'client_thread'):
                    self.client_thread.send_data(f"phase:change:{self.currentPhaseIndex}\n")
                self.ui.nextPhase_btn.setEnabled(False)
                self.ui.nextPhase_btn.setStyleSheet("background-color:lightgrey;")
                self.ui.backPhase_btn.setEnabled(False)
                self.ui.backPhase_btn.setStyleSheet("background-color:lightgrey;")
                self.updatePhaseDisplay()

        self.timerRunning = True #otherwise, when start is pressed, continue countdown 
        self.ui.nextPhase_btn.setEnabled(False)
        self.ui.nextPhase_btn.setStyleSheet("background-color:lightgrey;")
        self.ui.backPhase_btn.setEnabled(False)
        self.ui.backPhase_btn.setStyleSheet("background-color:lightgrey;")
        self.calcTotalTime()
        self.ui.startpause.setText("Pause")
        self.updateTotalTimeLabel()
        self.countdown()
        
    def countdown(self):
        print("Countdown called")
        if self.timerRunning:
            #countdown for current phase
            currentPhase = list(self.phases.keys())[self.currentPhaseIndex]
            phaseHrs, phaseMins, phaseSecs = self.phases[currentPhase]
            print(f"Current phase: {currentPhase}, Time: {phaseHrs}:{phaseMins}:{phaseSecs}")

            if phaseSecs > 0: phaseSecs -= 1
            elif phaseMins > 0:
                phaseMins -= 1
                phaseSecs = 59
            elif phaseHrs > 0:
                phaseHrs -= 1
                phaseMins = 59
                phaseSecs = 59
            else:
                phaseSecs = 0

            self.phases[currentPhase] = (phaseHrs, phaseMins, phaseSecs)

            if hasattr(self, 'server_thread'):
                print(f"Broadcasting updated time: {phaseHrs:02}:{phaseMins:02}:{phaseSecs:02}")
                self.server_thread.broadcast(f"timer:update:{phaseHrs:02}:{phaseMins:02}:{phaseSecs:02}\n")
            elif hasattr(self, 'client_thread'):
                print(f"Broadcasting updated time: {phaseHrs:02}:{phaseMins:02}:{phaseSecs:02}")
                self.client_thread.send_data(f"timer:update:{phaseHrs:02}:{phaseMins:02}:{phaseSecs:02}\n")
            
            self.calcTotalTime()
            self.updateClockDisplay(phaseHrs, phaseMins, phaseSecs)

            #when current phase ends, move onto next phase
            if self.phases[currentPhase] == (0,0,0):
                print("Phase ended, switching phase")
                self.nextPhase()
                if (self.currentPhaseIndex == (len(self.phases) - 1)) and (self.totalTime == 0): #when the last phase ends
                    self.timerRunning = False
                    self.ui.startpause.setText("Start")
                    print("Timer stopped, all phases completed")
                    return
                
            QTimer.singleShot(1000, self.countdown)
            self.updateTotalTimeLabel()

    def updateClockDisplay(self, hours, mins, secs):
        self.ui.lcdHours.display(f"{hours:03}")
        self.ui.lcdMins.display(f"{mins:03}")
        self.ui.lcdSecs.display(f"{secs:03}")
    
    def updateTotalTimeLabel(self):
        hours, mins, secs = self.totalTime
        # if secs > 0: secs -= 1
        # elif mins > 0:
        #     mins -= 1
        #     secs = 59
        # elif hours > 0:
        #     hours -= 1
        #     mins = 59
        #     secs = 59

        # self.totalTime = (hours, mins, secs)
        self.ui.totalTime_label.setText(f"Total Time: {int(hours)} hr, {int(mins)} min, {int(secs)} sec")

        if hasattr(self, 'server_thread'):
                self.server_thread.broadcast(f"timer:label:{hours:02}:{mins:02}:{secs:02}\n")
        elif hasattr(self, 'client_thread'):
                self.client_thread.send_data(f"timer:label:{hours:02}:{mins:02}:{secs:02}\n")

    def pauseTimer(self):
        self.timerRunning = False
        self.ui.startpause.setText("Start")
        self.ui.nextPhase_btn.setEnabled(False)
        self.ui.nextPhase_btn.setStyleSheet("background-color:lightgrey;")
        self.ui.backPhase_btn.setEnabled(False)
        self.ui.backPhase_btn.setStyleSheet("background-color:lightgrey;")
        # if hasattr(self, 'server_thread'):
        #     self.server_thread.broadcast(f"timer:pause")
        # elif hasattr(self, 'client_thread'):
        #     self.client_thread.send_data(f"timer:pause")
        
    def resetTimer(self):
        self.calcTotalTime()
        phaseName = list(self.phases.keys())[self.currentPhaseIndex]
        phaseTime = self.phases[phaseName]
        self.ui.nextPhase_btn.setEnabled(True)
        self.ui.nextPhase_btn.setStyleSheet("")
        self.ui.backPhase_btn.setEnabled(True)
        self.ui.backPhase_btn.setStyleSheet("")
        self.updateClockDisplay(*phaseTime)
        self.updateTotalTimeLabel()
        if hasattr(self, 'server_thread'):
            self.server_thread.broadcast(f"timer:reset")

    def cancelTimer(self):
        self.timerRunning = False
        self.totalTime = (0,0,0)
        self.ui.nextPhase_btn.setEnabled(True)
        self.ui.nextPhase_btn.setStyleSheet("")
        self.ui.backPhase_btn.setEnabled(True)
        self.ui.backPhase_btn.setStyleSheet("")
        self.updateClockDisplay(0,0,0)
        self.ui.totalTime_label.setText("Total Time: 0 hr, 0 min, 0 sec")
        if hasattr(self, 'server_thread'):
                self.server_thread.broadcast(f"timer:cancel")

    def toggle_startPause(self):
        if self.timerRunning:
            self.pauseTimer()
        else:
            self.startTimer()

    def editHours(self, event):
        hours, ok = QInputDialog.getInt(self, "", "Enter hours: ", min=0, max=24)
        if ok:
            phaseName = list(self.phases.keys())[self.currentPhaseIndex]
            _, mins, secs = self.phases[phaseName]
            self.phases[phaseName] = (hours, mins, secs)

            self.updateClockDisplay(hours, mins, secs)
            self.calcTotalTime()

    def editMins(self, event):
        mins, ok = QInputDialog.getInt(self, "", "Enter minutes: ", min=0, max=59)
        if ok:
            phaseName = list(self.phases.keys())[self.currentPhaseIndex]
            hours, _, secs = self.phases[phaseName]
            self.phases[phaseName] = (hours, mins, secs)

            self.updateClockDisplay(hours, mins, secs)
            self.calcTotalTime()

    def editSecs(self, event):
        secs, ok = QInputDialog.getInt(self, "", "Enter seconds: ", min=0, max=59)
        if ok:
            phaseName = list(self.phases.keys())[self.currentPhaseIndex]
            hours, mins, _ = self.phases[phaseName]
            self.phases[phaseName] = (hours, mins, secs)

            self.updateClockDisplay(hours, mins, secs)
            self.calcTotalTime()

    # should be called whenever new data is received
    # ex of data string parameter: "blue_score:005"
    # if blue_score or red_score is found in data, extract the score value
    # by splitting the string at the colon (:) and converting
    # the part after into an integer
    # once extracted, update ui display
    def process_data(self, data):
        commands = data.strip().split('\n')
        for command in commands:
            parts = command.split(':')
            if 'blue_score' in command:
                score = int(parts[1])
                self.ui.blueScore.display(f"{score:03}")
            elif 'red_score' in command:
                score = int(parts[1])
                self.ui.redScore.display(f"{score:03}")
            elif 'timer:start' in data:
                if len(parts) >= 5:
                    _,_,hh,mm,ss = parts[:5]
                    self.totalTime = (int(hh), int(mm), int(ss))
                    self.startTimer()
            elif 'timer:pause' in command:
                self.pauseTimer()
            elif 'timer:reset' in command:
                self.resetTimer()
            elif 'timer:cancel' in command:
                self.cancelTimer()
            elif 'timer:update' in command:
                if len(parts) >= 5:
                    _,_,hh,mm,ss = parts[:5]
                    self.updateClockDisplay(int(hh), int(mm), int(ss))
            elif 'phase:change' in command:
                _,_, phaseIndex = parts[:3]
                self.currentPhaseIndex = int(phaseIndex)
                self.updatePhaseDisplay()
            elif 'timer:label' in command:
                hours,mins,secs = data.split(":")[-3:]
                self.totalTime = (int(hours), int(mins), int(secs))
                self.ui.totalTime_label.setText(f"Total Time: {int(hours)} hr, {int(mins)} min, {int(secs)} sec")

    def closeEvent(self, event):
        if self.role == 'scoreboard':
            self.server_thread.stop()
        else:
            self.client_thread.stop()
        super(MainWindow, self).closeEvent(event)

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