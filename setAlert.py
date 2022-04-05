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
        Form.resize(523, 312)
        Form.setMinimumSize(QtCore.QSize(500, 0))
        Form.setMaximumSize(QtCore.QSize(1000, 1000))
        Form.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        Form.setAcceptDrops(False)
        self.gridLayout_3 = QtWidgets.QGridLayout(Form)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.addModifyButton = QtWidgets.QPushButton(Form)
        self.addModifyButton.setMinimumSize(QtCore.QSize(0, 30))
        self.addModifyButton.setMaximumSize(QtCore.QSize(16777215, 30))
        self.addModifyButton.setObjectName("addModifyButton")
        self.gridLayout_2.addWidget(self.addModifyButton, 3, 0, 1, 1)
        self.deleteUserButton = QtWidgets.QPushButton(Form)
        self.deleteUserButton.setMinimumSize(QtCore.QSize(0, 30))
        self.deleteUserButton.setMaximumSize(QtCore.QSize(16777215, 30))
        self.deleteUserButton.setObjectName("deleteUserButton")
        self.gridLayout_2.addWidget(self.deleteUserButton, 3, 1, 1, 1)
        self.frame = QtWidgets.QFrame(Form)
        self.frame.setMinimumSize(QtCore.QSize(0, 120))
        self.frame.setMaximumSize(QtCore.QSize(16777215, 120))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setObjectName("gridLayout")
        self.lineToken = QtWidgets.QLineEdit(self.frame)
        self.lineToken.setMinimumSize(QtCore.QSize(0, 30))
        self.lineToken.setMaximumSize(QtCore.QSize(16777215, 30))
        self.lineToken.setObjectName("lineToken")
        self.gridLayout.addWidget(self.lineToken, 3, 1, 1, 1)
        self.emailCheckBox = QtWidgets.QCheckBox(self.frame)
        self.emailCheckBox.setMinimumSize(QtCore.QSize(0, 30))
        self.emailCheckBox.setMaximumSize(QtCore.QSize(16777215, 30))
        self.emailCheckBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.emailCheckBox.setStyleSheet("font: 75 bold 11pt \"Arial\";")
        self.emailCheckBox.setObjectName("emailCheckBox")
        self.gridLayout.addWidget(self.emailCheckBox, 1, 0, 1, 1)
        self.lineCheckBox = QtWidgets.QCheckBox(self.frame)
        self.lineCheckBox.setMinimumSize(QtCore.QSize(0, 30))
        self.lineCheckBox.setMaximumSize(QtCore.QSize(16777215, 30))
        self.lineCheckBox.setStyleSheet("font: 75 bold 11pt \"Arial\";")
        self.lineCheckBox.setObjectName("lineCheckBox")
        self.gridLayout.addWidget(self.lineCheckBox, 3, 0, 1, 1)
        self.userName = QtWidgets.QLineEdit(self.frame)
        self.userName.setMinimumSize(QtCore.QSize(0, 30))
        self.userName.setMaximumSize(QtCore.QSize(16777215, 30))
        self.userName.setObjectName("userName")
        self.gridLayout.addWidget(self.userName, 0, 1, 1, 1)
        self.email = QtWidgets.QLineEdit(self.frame)
        self.email.setMinimumSize(QtCore.QSize(0, 30))
        self.email.setMaximumSize(QtCore.QSize(16777215, 30))
        self.email.setObjectName("email")
        self.gridLayout.addWidget(self.email, 1, 1, 1, 1)
        self.userNameLabel = QtWidgets.QLabel(self.frame)
        self.userNameLabel.setMinimumSize(QtCore.QSize(0, 30))
        self.userNameLabel.setMaximumSize(QtCore.QSize(16777215, 30))
        self.userNameLabel.setObjectName("userNameLabel")
        self.gridLayout.addWidget(self.userNameLabel, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.frame, 2, 0, 1, 2)
        self.helpButton = QtWidgets.QPushButton(Form)
        self.helpButton.setMinimumSize(QtCore.QSize(0, 30))
        self.helpButton.setMaximumSize(QtCore.QSize(16777215, 30))
        self.helpButton.setCheckable(True)
        self.helpButton.setObjectName("helpButton")
        self.gridLayout_2.addWidget(self.helpButton, 1, 1, 1, 1)
        self.userMenu = QtWidgets.QPushButton(Form)
        self.userMenu.setMinimumSize(QtCore.QSize(0, 30))
        self.userMenu.setMaximumSize(QtCore.QSize(16777215, 30))
        self.userMenu.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.userMenu.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.userMenu.setAcceptDrops(True)
        self.userMenu.setObjectName("userMenu")
        self.gridLayout_2.addWidget(self.userMenu, 1, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.textBrowser = QtWidgets.QTextBrowser(Form)
        self.textBrowser.setOpenExternalLinks(True)
        self.textBrowser.setObjectName("textBrowser")
        self.gridLayout_3.addWidget(self.textBrowser, 1, 0, 1, 1)

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
        self.helpButton.setWhatsThis(_translate("Form", "<html><head/><body><p>Click here to know how to set email and line alerts</p></body></html>"))
        self.helpButton.setText(_translate("Form", "Help"))
        self.userMenu.setToolTip(_translate("Form", "<html><head/><body><p>Select user from list</p></body></html>"))
        self.userMenu.setText(_translate("Form", "Select User"))
        self.textBrowser.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS UI Gothic\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">You can add your email and line token and save under your username, so that you can choose to get alerts about your experiments.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:600; text-decoration: underline;\">Existing User</span></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">If your email and (or) line token are already stored in database, you can choose your name from the dropdown box and then check the email or(and) line checkbox to receive the alert.</span></p>\n"
"<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:12pt;\"><br /></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">You need to opt for the alert each time the software is started afresh.</span></p>\n"
"<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:600; text-decoration: underline;\">New User</span></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">If you are a new user, choose &quot;new user&quot; from drop down menu, and enter your email id, and(or) line token. You can choose to receive alert in either email or line, or both. Just check the box of whichever media you prefer.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:600; text-decoration: underline;\">How to obtain your line token:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; font-weight:600;\">Step 1:</span><span style=\" font-size:12pt;\"> Login to &quot;</span><a href=\"https://notify-bot.line.me/en/\"><span style=\" font-size:12pt; text-decoration: underline; color:#0000ff;\">line notify</span></a><span style=\" font-size:12pt;\">&quot; using your line credentials.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; font-weight:600;\">Step 2:</span><span style=\" font-size:12pt;\"> Click on &quot;My Page&quot;</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; font-weight:600;\">Step 3:</span><span style=\" font-size:12pt;\"> Scroll down and click on &quot;Generate Token&quot;</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; font-weight:600;\">Step 4:</span><span style=\" font-size:12pt;\"> Enter a Token name to be displayed in each message. Then select a line group to which you want to send the message. If you want to send message only to yourself, select 1:1 option.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; font-weight:600;\">Step 5:</span><span style=\" font-size:12pt;\"> Once you have entered the required the required information, click on &quot;Generate Token&quot;.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; font-weight:600;\">Step 6:</span><span style=\" font-size:12pt;\"> You will see a token generated, you have to copy that token and paste it above in the space provided for line token. Now you are all set to receive alert from line.</span></p></body></html>"))



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
        self.addModifyButton.clicked.connect(self.updateUserinFile)
        self.deleteUserButton.clicked.connect(self.deleteUserFromFile)
        self.helpButton.clicked.connect(self.showHelp)
        self.textBrowser.hide()
        self.actions[self.currentIndex].trigger()
        self.resize(530, 220)
        self.resize(530, 220)
        os.chdir(self.currentPath)
        #self.setWindowTitle("Specify Alert Settings")
    
    def showHelp(self):
        if self.helpButton.isChecked():
            self.resize(530, 900)
            self.textBrowser.show()
        else:
            self.textBrowser.hide()
            self.resize(530, 220)
            self.resize(530, 220)
    
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
        self.textBrowser.hide()
        self.resize(530, 220)
        self.resize(530, 220)
        event.accept()
                
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = AlertForm()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

