# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AlertSettings.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class AlertForm(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(450, 198)
        Form.setMinimumSize(QtCore.QSize(424, 124))
        Form.setMaximumSize(QtCore.QSize(800, 800))
        Form.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        Form.setAcceptDrops(False)
        self.gridLayout_3 = QtWidgets.QGridLayout(Form)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.addModifyButton = QtWidgets.QPushButton(Form)
        self.addModifyButton.setObjectName("addModifyButton")
        self.gridLayout_2.addWidget(self.addModifyButton, 2, 0, 1, 1)
        self.userMenu = QtWidgets.QPushButton(Form)
        self.userMenu.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.userMenu.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.userMenu.setAcceptDrops(True)
        self.userMenu.setObjectName("userMenu")
        self.gridLayout_2.addWidget(self.userMenu, 0, 1, 1, 1)
        self.userLabel = QtWidgets.QLabel(Form)
        self.userLabel.setObjectName("userLabel")
        self.gridLayout_2.addWidget(self.userLabel, 0, 0, 1, 1)
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
        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Specify Alert Settings"))
        self.addModifyButton.setToolTip(_translate("Form", "<html><head/><body><p>Click here to add new user or modify email and line token of a user. You cannot modify user name here.</p></body></html>"))
        self.addModifyButton.setText(_translate("Form", "Update User"))
        self.userMenu.setToolTip(_translate("Form", "<html><head/><body><p>Select user from list</p></body></html>"))
        self.userMenu.setText(_translate("Form", "PushButton"))
        self.userLabel.setText(_translate("Form", "<html><head/><body><p align=\"center\"><span style=\" font-size:10pt; font-weight:600;\">Select User</span></p></body></html>"))
        self.deleteUserButton.setText(_translate("Form", "Delete User"))
        self.emailCheckBox.setToolTip(_translate("Form", "<html><head/><body><p>Check this box to send alert to specified email</p></body></html>"))
        self.emailCheckBox.setText(_translate("Form", "Email"))
        self.lineCheckBox.setToolTip(_translate("Form", "<html><head/><body><p>Check this box to send alert to your line account</p></body></html>"))
        self.lineCheckBox.setText(_translate("Form", "Line Token"))
        self.userNameLabel.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:10pt; font-weight:600;\">User Name</span></p></body></html>"))

class AlertSetting(QtWidgets.QDialog, AlertForm):
    def __init__(self, *args, obj=None, **kwargs):
        super().__init__(*args, **kwargs)
        with open('users.txt', 'r') as f:
            self.usersList = f.readlines().split('\n')
        self.filename = "SHG_default_Settings.txt"
        self.load_parameters_from_file()
        self.changed = False
        self.grp = [item('X-axis Scale     :', self.xscale, suffix='V = 1 μm', limits=(0.00000001, 100000000), siPrefix=True),
                    item('X-axis V max   :', self.xvmax,
                         suffix='V', limits=(-10, 10)),
                    item('X-axis V min    :', self.xvmin,
                         suffix='V', limits=(-10, 10)),
                    item('Set x-axis position:', self.xpos,
                         suffix='V', siPrefix=True),
                    item('X-axis max       :', self.xmax,
                         suffix='μm', readonly=True),
                    item('X-axis min       :', self.xmin,
                         suffix='μm', readonly=True),
                    item('Y-axis Scale     :', self.yscale, suffix='V = 1 μm',
                         limits=(0.00000001, 100000000), siPrefix=True),
                    item('Y-axis V max   :', self.yvmax,
                         suffix='V', limits=(-10, 10)),
                    item('Y-axis V min    :', self.yvmin,
                         suffix='V', limits=(-10, 10)),
                    item('Set y-axis position:', self.ypos,
                         suffix='V', siPrefix=True),
                    item('Y-axis max       :', self.ymax,
                         suffix='μm', readonly=True),
                    item('Y-axis min        :', self.ymin, suffix='μm', readonly=True)]
        self.galset_setupUi(self, self.grp)
        self.setWindowTitle("Galvanometer Settings")
        self.cancelButton.clicked.connect(self.cancel_galsetting)
        self.okayButton.clicked.connect(self.okay_galsetting)
        self.defaultButton.clicked.connect(self.goDefault)
        self.setdefaultButton.clicked.connect(self.setAsDefault)
        self.treeWidget.paramSet.sigTreeStateChanged.connect(self.galsetchange)
        
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = AlertForm()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

