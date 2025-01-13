# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'frmMainMenuxeOlfi.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QFormLayout, QLabel, QLayout,
    QLineEdit, QMainWindow, QMenu, QMenuBar,
    QPushButton, QSizePolicy, QStatusBar, QWidget)

class Ui_asg_ventanaMain(object):
    def setupUi(self, asg_ventanaMain):
        if not asg_ventanaMain.objectName():
            asg_ventanaMain.setObjectName(u"asg_ventanaMain")
        asg_ventanaMain.setWindowModality(Qt.WindowModality.WindowModal)
        asg_ventanaMain.resize(380, 205)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(asg_ventanaMain.sizePolicy().hasHeightForWidth())
        asg_ventanaMain.setSizePolicy(sizePolicy)
        asg_ventanaMain.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        asg_ventanaMain.setAutoFillBackground(False)
        asg_ventanaMain.setStyleSheet(u"            background-color: rgb(34, 40, 49);\n"
"            color: white;")
        asg_ventanaMain.setIconSize(QSize(0, 0))
        self.actionSalir = QAction(asg_ventanaMain)
        self.actionSalir.setObjectName(u"actionSalir")
        self.centralwidget = QWidget(asg_ventanaMain)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy1)
        self.centralwidget.setMinimumSize(QSize(379, 10))
        self.centralwidget.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.centralwidget.setAutoFillBackground(False)
        self.centralwidget.setStyleSheet(u"     QLabel {\n"
"                font-size: 14px;\n"
"                color: white;\n"
"            }\n"
"            QLineEdit {\n"
"                background-color: rgb(57, 62, 70);\n"
"                border: 1px solid rgb(0, 173, 181);\n"
"                border-radius: 5px;\n"
"                padding: 5px;\n"
"                color: white;\n"
"            }\n"
"            QLineEdit:focus {\n"
"                border: 1px solid rgb(0, 255, 255);\n"
"            }\n"
"            QPushButton {\n"
"                background-color: rgb(0, 173, 181);\n"
"                color: white;\n"
"                border-radius: 10px;\n"
"                padding: 5px;\n"
"                font-size: 12px;\n"
"                font-weight: bold;\n"
"            }\n"
"            QPushButton:hover {\n"
"                background-color: rgb(0, 200, 200);\n"
"            }\n"
"            QPushButton:pressed {\n"
"                background-color: rgb(0, 150, 150);\n"
"            }")
        self.formLayout_2 = QFormLayout(self.centralwidget)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.formLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.FieldsStayAtSizeHint)
        self.formLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self.formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignCenter)
        self.formLayout.setFormAlignment(Qt.AlignmentFlag.AlignCenter)
        self.formLayout.setHorizontalSpacing(6)
        self.formLayout.setContentsMargins(-1, 9, 9, 0)
        self.usuarioLabel = QLabel(self.centralwidget)
        self.usuarioLabel.setObjectName(u"usuarioLabel")
        font = QFont()
        self.usuarioLabel.setFont(font)
        self.usuarioLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.usuarioLabel)

        self.usuarioEdit = QLineEdit(self.centralwidget)
        self.usuarioEdit.setObjectName(u"usuarioEdit")
        self.usuarioEdit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.usuarioEdit)

        self.passLabel = QLabel(self.centralwidget)
        self.passLabel.setObjectName(u"passLabel")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.passLabel)

        self.passEdit = QLineEdit(self.centralwidget)
        self.passEdit.setObjectName(u"passEdit")
        self.passEdit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.passEdit.setInputMethodHints(Qt.InputMethodHint.ImhHiddenText|Qt.InputMethodHint.ImhNoAutoUppercase|Qt.InputMethodHint.ImhNoPredictiveText|Qt.InputMethodHint.ImhSensitiveData)
        self.passEdit.setEchoMode(QLineEdit.EchoMode.Password)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.passEdit)

        self.asg_pushButton = QPushButton(self.centralwidget)
        self.asg_pushButton.setObjectName(u"asg_pushButton")
        self.asg_pushButton.setEnabled(True)
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.asg_pushButton.sizePolicy().hasHeightForWidth())
        self.asg_pushButton.setSizePolicy(sizePolicy2)
        self.asg_pushButton.setMaximumSize(QSize(75, 16777215))
        self.asg_pushButton.setSizeIncrement(QSize(0, 0))
        self.asg_pushButton.setBaseSize(QSize(0, 0))
        font1 = QFont()
        font1.setBold(True)
        font1.setKerning(False)
        font1.setStyleStrategy(QFont.NoAntialias)
        self.asg_pushButton.setFont(font1)
        self.asg_pushButton.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.asg_pushButton.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
        self.asg_pushButton.setAcceptDrops(False)
        self.asg_pushButton.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.asg_pushButton)


        self.formLayout_2.setLayout(3, QFormLayout.FieldRole, self.formLayout)

        asg_ventanaMain.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(asg_ventanaMain)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 380, 33))
        self.menuMen = QMenu(self.menubar)
        self.menuMen.setObjectName(u"menuMen")
        asg_ventanaMain.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(asg_ventanaMain)
        self.statusbar.setObjectName(u"statusbar")
        asg_ventanaMain.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuMen.menuAction())
        self.menuMen.addAction(self.actionSalir)

        self.retranslateUi(asg_ventanaMain)

        QMetaObject.connectSlotsByName(asg_ventanaMain)
    # setupUi

    def retranslateUi(self, asg_ventanaMain):
        asg_ventanaMain.setWindowTitle(QCoreApplication.translate("asg_ventanaMain", u"Tarea3", None))
        self.actionSalir.setText(QCoreApplication.translate("asg_ventanaMain", u"Salir", None))
        self.usuarioLabel.setText(QCoreApplication.translate("asg_ventanaMain", u"Usuario", None))
#if QT_CONFIG(tooltip)
        self.usuarioEdit.setToolTip(QCoreApplication.translate("asg_ventanaMain", u"Introduce usuario", None))
#endif // QT_CONFIG(tooltip)
        self.usuarioEdit.setText("")
        self.passLabel.setText(QCoreApplication.translate("asg_ventanaMain", u"Contrase\u00f1a", None))
#if QT_CONFIG(tooltip)
        self.passEdit.setToolTip(QCoreApplication.translate("asg_ventanaMain", u"Introduce password", None))
#endif // QT_CONFIG(tooltip)
        self.passEdit.setInputMask("")
        self.passEdit.setText("")
#if QT_CONFIG(tooltip)
        self.asg_pushButton.setToolTip(QCoreApplication.translate("asg_ventanaMain", u"Click para hacer Login", None))
#endif // QT_CONFIG(tooltip)
        self.asg_pushButton.setText(QCoreApplication.translate("asg_ventanaMain", u"Login", None))
        self.menuMen.setTitle(QCoreApplication.translate("asg_ventanaMain", u"Men\u00fa", None))
    # retranslateUi

