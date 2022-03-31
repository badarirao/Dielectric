# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AlertSettings.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize
import os, re

class AlertForm(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(450, 198)
        Form.setMinimumSize(QtCore.QSize(450, 198))
        Form.setMaximumSize(QtCore.QSize(450, 198))
        Form.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        Form.setAcceptDrops(False)
        self.gridLayout_3 = QtWidgets.QGridLayout(Form)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.addModifyButton = QtWidgets.QPushButton(Form)
        self.addModifyButton.setObjectName("addModifyButton")
        self.gridLayout_2.addWidget(self.addModifyButton, 2, 0, 1, 1)
        self.deleteUserButton = QtWidgets.QPushButton(Form)
        self.deleteUserButton.setObjectName("deleteUserButton")
        self.gridLayout_2.addWidget(self.deleteUserButton, 2, 1, 1, 1)
        self.frame = QtWidgets.QFrame(Form)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setObjectName("gridLayout")
        self.lineToken = QtWidgets.QLineEdit(self.frame)
        self.lineToken.setObjectName("lineToken")
        self.gridLayout.addWidget(self.lineToken, 3, 1, 1, 1)
        self.emailCheckBox = QtWidgets.QCheckBox(self.frame)
        self.emailCheckBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.emailCheckBox.setStyleSheet("font: 75 bold 11pt \"Arial\";")
        self.emailCheckBox.setObjectName("emailCheckBox")
        self.gridLayout.addWidget(self.emailCheckBox, 1, 0, 1, 1)
        self.lineCheckBox = QtWidgets.QCheckBox(self.frame)
        self.lineCheckBox.setStyleSheet("font: 75 bold 11pt \"Arial\";")
        self.lineCheckBox.setObjectName("lineCheckBox")
        self.gridLayout.addWidget(self.lineCheckBox, 3, 0, 1, 1)
        self.userName = QtWidgets.QLineEdit(self.frame)
        self.userName.setObjectName("userName")
        self.gridLayout.addWidget(self.userName, 0, 1, 1, 1)
        self.email = QtWidgets.QLineEdit(self.frame)
        self.email.setObjectName("email")
        self.gridLayout.addWidget(self.email, 1, 1, 1, 1)
        self.userNameLabel = QtWidgets.QLabel(self.frame)
        self.userNameLabel.setObjectName("userNameLabel")
        self.gridLayout.addWidget(self.userNameLabel, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.frame, 1, 0, 1, 2)
        self.userMenu = QtWidgets.QPushButton(Form)
        self.userMenu.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.userMenu.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.userMenu.setAcceptDrops(True)
        self.userMenu.setObjectName("userMenu")
        self.gridLayout_2.addWidget(self.userMenu, 0, 0, 1, 2)
        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.addModifyButton.setToolTip(_translate("Form", "<html><head/><body><p>Click here to add new user or modify email and line token of a user. You cannot modify user name here.</p></body></html>"))
        self.addModifyButton.setText(_translate("Form", "Update User"))
        self.deleteUserButton.setText(_translate("Form", "Delete User"))
        self.emailCheckBox.setToolTip(_translate("Form", "<html><head/><body><p>Check this box to send alert to specified email</p></body></html>"))
        self.emailCheckBox.setText(_translate("Form", "Email"))
        self.lineCheckBox.setToolTip(_translate("Form", "<html><head/><body><p>Check this box to send alert to your line account</p></body></html>"))
        self.lineCheckBox.setText(_translate("Form", "Line Token"))
        self.userNameLabel.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:10pt; font-weight:600;\">User Name</span></p></body></html>"))
        self.userMenu.setToolTip(_translate("Form", "<html><head/><body><p>Select user from list</p></body></html>"))
        self.userMenu.setText(_translate("Form", "Select User"))

class AlertSetting(QtWidgets.QDialog, AlertForm):
    def __init__(self, settingPath = '',currentPath = '', *args, obj=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.settingPath = settingPath
        self.currentPath = currentPath
        self.currentUser = 'None'
        self.currentIndex = 0
        self.alertNames = QtWidgets.QMenu()
        self.alertNames.setMinimumSize(QSize(250,20))
        self.userMenu.setMenu(self.alertNames)
        self.userMenu.setLayoutDirection(QtCore.Qt.RightToLeft)
        os.chdir(self.settingPath)
        self.api = "api:"
        self.loadUserDetails()
        self.currentIndex = len(self.userList)-1
        self.alertNames.triggered.connect(self.showUserDetails)
        self.actions[self.currentIndex].trigger()
        self.addModifyButton.clicked.connect(self.updateUserinFile)
        self.deleteUserButton.clicked.connect(self.deleteUserFromFile)
        os.chdir(self.currentPath)
        #self.setWindowTitle("Specify Alert Settings")
    
    def loadUserDetails(self):
        self.alertNames.clear()
        self.actions = []
        with open('users.txt', 'r') as f:
            self.userList = f.readlines()
            self.api = self.userList[0].rstrip()
            self.userList = self.userList[1:]
        self.userList.append('None  ')
        self.userList.insert(0,'New-User  ')
        for i,user in enumerate(self.userList):
            user = user.rstrip()
            user = user.split(' ')
            if len(user) < 5:
                toAdd = 5 - len(user)
                l = ['']*toAdd
                user.extend(l)
            elif len(user) > 5:
                user = user[:5]
            self.actions.append(self.alertNames.addAction(user[0]))
            self.userList[i] = user
    
    def showUserDetails(self,x):
        userName = x.text()
        if userName == 'None':
            self.userName.setText('')
            self.email.setText('')
            self.lineToken.setText('')
            self.frame.setEnabled(False)
            self.addModifyButton.setEnabled(False)
            self.deleteUserButton.setEnabled(False)
        else:
            self.frame.setEnabled(True)
            self.addModifyButton.setEnabled(True)
            self.deleteUserButton.setEnabled(True)
            for i,user in enumerate(self.userList):
                if user[0] == userName:
                    self.currentIndex = i
                    if userName == 'New-User':
                        self.userName.setText('')
                    else:
                        self.userName.setText(user[0])
                    self.email.setText(user[1])
                    self.lineToken.setText(user[2])
                    if user[3] == '1':
                        self.emailCheckBox.setChecked(True)
                    else:
                        self.emailCheckBox.setChecked(False)
                    if user[4] == '1':
                        self.lineCheckBox.setChecked(True)
                    else:
                        self.lineCheckBox.setChecked(False)
        self.currentUser = [userName,
                            self.email.text(),
                            self.lineToken.text(),
                            self.emailCheckBox.isChecked(),
                            self.lineCheckBox.isChecked()]
        
    def updateUserinFile(self):
        os.chdir(self.settingPath)
        updated = True
        user = ['','','','0','0']
        namePattern = '^[A-Za-z0-9_-]'
        emailPattern = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        lineTokenPattern = '^[A-Za-z0-9]'
        if bool(re.match(namePattern,self.userName.text())):
            user[0] = self.userName.text()
            if re.fullmatch(emailPattern,self.email.text()):
                user[1] = self.email.text()
                if self.emailCheckBox.isChecked():
                    user[3] = '1'
            else:
                print("Email incorrect")
            if bool(re.match(lineTokenPattern,self.lineToken.text())):
                user[2] = self.lineToken.text()
                if self.lineCheckBox.isChecked():
                    user[4] = '1'
            else:
                print("Line Token incorrect")
            if user[1] == '' and user[2] == '':
                print("No email or line  token provided. User not stored.")
                updated = False
        else:
            print("Invalid user name")
            updated = False
        newUser = True
        # Check user name position
        for i,u in enumerate(self.userList):
            if user[0] == u[0]:
                newUser = False
                self.currentIndex = i
                break
        if updated:
            if not newUser:
                self.userList[self.currentIndex] = user
                print("Successfully updated")
            else:
                self.userList.append(user)
                self.currentIndex = len(self.userList)-1
                print("Successfully added")
            with open('users.txt','w') as f:
                f.write(self.api)
                for u in self.userList:
                    if u[0] != 'New-User' and u[0]!= 'None':
                        line = ' '.join(u)
                        f.write('\n')
                        f.write(line)
                f.flush()
            self.loadUserDetails()
        else:
            print("Not updated")
            
    def deleteUserFromFile(self):
        if self.userList[self.currentIndex][0] != 'New-User':
            self.alertNames.removeAction(self.actions[self.currentIndex])
            self.actions.pop(self.currentIndex)
            self.userList.pop(self.currentIndex)
            with open('users.txt','w') as f:
                f.write(self.api)
                for u in self.userList:
                    if u[0] != 'New-User' and u[0]!= 'None':
                        line = ' '.join(u)
                        f.write('\n')
                        f.write(line)
            self.currentIndex = len(self.userList)-1
            self.actions[self.currentIndex].trigger()
        else:
            self.actions[-1].trigger()
    
    def closeEvent(self, event):
        os.chdir(self.currentPath)
        self.actions[self.currentIndex].trigger()
        event.accept()
                
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = AlertForm()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

