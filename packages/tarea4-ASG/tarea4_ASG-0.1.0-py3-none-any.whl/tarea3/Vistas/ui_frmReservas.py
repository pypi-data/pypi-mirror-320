# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'frmReservasMwfkir.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QCheckBox, QComboBox,
    QDateEdit, QDateTimeEdit, QFrame, QGridLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QWidget)

class Ui_Reservas(object):
    def setupUi(self, Reservas):
        if not Reservas.objectName():
            Reservas.setObjectName(u"Reservas")
        Reservas.setWindowModality(Qt.WindowModality.WindowModal)
        Reservas.resize(823, 367)
        Reservas.setStyleSheet(u"background-color: #2E2E2E;\n"
"        color: #FFFFFF;\n"
"        font-family: Arial, sans-serif;\n"
"        font-size: 14px;\n"
"           border: 1px solid #555555;  \n"
"        border-radius: 5px;\n"
"        padding: 5px;\n"
"")
        self.gridLayoutWidget = QWidget(Reservas)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(40, 30, 760, 201))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setVerticalSpacing(3)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName(u"label_2")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setBaseSize(QSize(0, 0))
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setWeight(QFont.Medium)
        font.setKerning(False)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet(u";")
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.label_2, 1, 1, 1, 1)

        self.asg_fecha = QDateEdit(self.gridLayoutWidget)
        self.asg_fecha.setObjectName(u"asg_fecha")
        self.asg_fecha.setStyleSheet(u"        background-color: #3A3A3A;\n"
"        color: #FFFFFF;\n"
"        border: 1px solid #555555;  /* Borde para los campos */\n"
"        border-radius: 5px;\n"
"        padding: 4px;")
        self.asg_fecha.setDateTime(QDateTime(QDate(1999, 12, 31), QTime(19, 0, 0)))
        self.asg_fecha.setMinimumDate(QDate.currentDate())
        self.asg_fecha.setCurrentSection(QDateTimeEdit.Section.DaySection)
        self.asg_fecha.setCalendarPopup(True)

        self.gridLayout.addWidget(self.asg_fecha, 2, 3, 1, 1)

        self.asg_tipoReserva = QComboBox(self.gridLayoutWidget)
        self.asg_tipoReserva.setObjectName(u"asg_tipoReserva")
        self.asg_tipoReserva.setStyleSheet(u"        background-color: #3A3A3A;\n"
"        color: #FFFFFF;\n"
"        border: 1px solid #555555;  /* Borde para los campos */\n"
"        border-radius: 5px;\n"
"        padding: 4px;")

        self.gridLayout.addWidget(self.asg_tipoReserva, 3, 3, 1, 1)

        self.label_6 = QLabel(self.gridLayoutWidget)
        self.label_6.setObjectName(u"label_6")
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setBaseSize(QSize(0, 0))
        self.label_6.setFont(font)
        self.label_6.setStyleSheet(u";")
        self.label_6.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.label_6, 0, 4, 1, 1)

        self.label_3 = QLabel(self.gridLayoutWidget)
        self.label_3.setObjectName(u"label_3")
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setBaseSize(QSize(0, 0))
        self.label_3.setFont(font)
        self.label_3.setStyleSheet(u";")
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.label_3, 3, 1, 1, 1)

        self.asg_textoCongreso = QLabel(self.gridLayoutWidget)
        self.asg_textoCongreso.setObjectName(u"asg_textoCongreso")
        self.asg_textoCongreso.setEnabled(True)
        font1 = QFont()
        font1.setFamilies([u"Arial"])
        font1.setKerning(True)
        self.asg_textoCongreso.setFont(font1)
        self.asg_textoCongreso.setInputMethodHints(Qt.InputMethodHint.ImhNone)
        self.asg_textoCongreso.setFrameShape(QFrame.Shape.NoFrame)
        self.asg_textoCongreso.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.asg_textoCongreso, 3, 4, 1, 1)

        self.asg_numeroAsis = QSpinBox(self.gridLayoutWidget)
        self.asg_numeroAsis.setObjectName(u"asg_numeroAsis")
        self.asg_numeroAsis.setStyleSheet(u"        background-color: #3A3A3A;\n"
"        color: #FFFFFF;\n"
"        border: 1px solid #555555;  /* Borde para los campos */\n"
"        border-radius: 4px;\n"
"        padding: 2px;\n"
"    \n"
"")
        self.asg_numeroAsis.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.gridLayout.addWidget(self.asg_numeroAsis, 4, 3, 1, 1)

        self.label = QLabel(self.gridLayoutWidget)
        self.label.setObjectName(u"label")
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setBaseSize(QSize(0, 0))
        self.label.setFont(font)
        self.label.setStyleSheet(u";")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)

        self.asg_numJorn = QSpinBox(self.gridLayoutWidget)
        self.asg_numJorn.setObjectName(u"asg_numJorn")
        self.asg_numJorn.setStyleSheet(u"        background-color: #3A3A3A;\n"
"        color: #FFFFFF;\n"
"        border: 1px solid #555555;  /* Borde para los campos */\n"
"        border-radius: 5px;\n"
"        padding: 1px;")
        self.asg_numJorn.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.gridLayout.addWidget(self.asg_numJorn, 3, 5, 1, 1)

        self.label_4 = QLabel(self.gridLayoutWidget)
        self.label_4.setObjectName(u"label_4")
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setBaseSize(QSize(0, 0))
        self.label_4.setFont(font)
        self.label_4.setStyleSheet(u";")
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.label_4, 2, 1, 1, 1)

        self.asg_lineaTel = QLineEdit(self.gridLayoutWidget)
        self.asg_lineaTel.setObjectName(u"asg_lineaTel")
        self.asg_lineaTel.setStyleSheet(u"        background-color: #3A3A3A;\n"
"        color: #FFFFFF;\n"
"        border: 1px solid #555555;  /* Borde para los campos */\n"
"        border-radius: 5px;\n"
"        padding: 4px;")

        self.gridLayout.addWidget(self.asg_lineaTel, 1, 3, 1, 1)

        self.asg_tipoCocina = QComboBox(self.gridLayoutWidget)
        self.asg_tipoCocina.setObjectName(u"asg_tipoCocina")
        self.asg_tipoCocina.setStyleSheet(u"        background-color: #3A3A3A;\n"
"        color: #FFFFFF;\n"
"        border: 1px solid #555555;  /* Borde para los campos */\n"
"        border-radius: 5px;\n"
"        padding: 1px;")

        self.gridLayout.addWidget(self.asg_tipoCocina, 0, 5, 1, 1)

        self.label_5 = QLabel(self.gridLayoutWidget)
        self.label_5.setObjectName(u"label_5")
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setBaseSize(QSize(0, 0))
        self.label_5.setFont(font)
        self.label_5.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.label_5, 4, 1, 1, 1)

        self.asg_lineaNombre = QLineEdit(self.gridLayoutWidget)
        self.asg_lineaNombre.setObjectName(u"asg_lineaNombre")
        self.asg_lineaNombre.setStyleSheet(u"        background-color: #3A3A3A;\n"
"        color: #FFFFFF;\n"
"        border: 1px solid #555555;  /* Borde para los campos */\n"
"        border-radius: 5px;\n"
"        padding: 4px;")

        self.gridLayout.addWidget(self.asg_lineaNombre, 0, 3, 1, 1)

        self.asg_checkBox = QCheckBox(self.gridLayoutWidget)
        self.asg_checkBox.setObjectName(u"asg_checkBox")
        self.asg_checkBox.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.asg_checkBox.setStyleSheet(u"")

        self.gridLayout.addWidget(self.asg_checkBox, 4, 5, 1, 1)

        self.horizontalLayoutWidget = QWidget(Reservas)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(30, 250, 771, 80))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer_2 = QSpacerItem(20, 75, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.asg_volver = QPushButton(self.horizontalLayoutWidget)
        self.asg_volver.setObjectName(u"asg_volver")
        self.asg_volver.setStyleSheet(u"    QPushButton {\n"
"        background-color: #444444;\n"
"        color: #FFFFFF;\n"
"        border: 1px solid #666666;\n"
"        border-radius: 5px;\n"
"        padding: 5px 10px;\n"
"    }\n"
"    QPushButton:hover {\n"
"        background-color: #555555;\n"
"    }\n"
"    QPushButton:pressed {\n"
"        background-color: #666666;\n"
"    }")

        self.horizontalLayout.addWidget(self.asg_volver)

        self.asg_finalizar = QPushButton(self.horizontalLayoutWidget)
        self.asg_finalizar.setObjectName(u"asg_finalizar")
        self.asg_finalizar.setStyleSheet(u"    QPushButton {\n"
"        background-color: #444444;\n"
"        color: #FFFFFF;\n"
"        border: 1px solid #666666;\n"
"        border-radius: 5px;\n"
"        padding: 5px 10px;\n"
"    }\n"
"    QPushButton:hover {\n"
"        background-color: #555555;\n"
"    }\n"
"    QPushButton:pressed {\n"
"        background-color: #666666;\n"
"    }")

        self.horizontalLayout.addWidget(self.asg_finalizar)

        QWidget.setTabOrder(self.asg_lineaNombre, self.asg_lineaTel)
        QWidget.setTabOrder(self.asg_lineaTel, self.asg_fecha)
        QWidget.setTabOrder(self.asg_fecha, self.asg_tipoReserva)
        QWidget.setTabOrder(self.asg_tipoReserva, self.asg_numeroAsis)
        QWidget.setTabOrder(self.asg_numeroAsis, self.asg_tipoCocina)
        QWidget.setTabOrder(self.asg_tipoCocina, self.asg_numJorn)
        QWidget.setTabOrder(self.asg_numJorn, self.asg_checkBox)

        self.retranslateUi(Reservas)

        QMetaObject.connectSlotsByName(Reservas)
    # setupUi

    def retranslateUi(self, Reservas):
        Reservas.setWindowTitle(QCoreApplication.translate("Reservas", u"Reservas", None))
        self.label_2.setText(QCoreApplication.translate("Reservas", u"Tel\u00e9fono", None))
#if QT_CONFIG(tooltip)
        self.asg_fecha.setToolTip(QCoreApplication.translate("Reservas", u"Selecciona fecha para Reserva", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.asg_tipoReserva.setToolTip(QCoreApplication.translate("Reservas", u"Selecciona el tipo de Reserva", None))
#endif // QT_CONFIG(tooltip)
        self.label_6.setText(QCoreApplication.translate("Reservas", u"Tipo de Cocina", None))
#if QT_CONFIG(tooltip)
        self.label_3.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.label_3.setText(QCoreApplication.translate("Reservas", u"Tipo de Reserva", None))
        self.asg_textoCongreso.setText(QCoreApplication.translate("Reservas", u"N\u00famero de jornadas del Congreso", None))
#if QT_CONFIG(tooltip)
        self.asg_numeroAsis.setToolTip(QCoreApplication.translate("Reservas", u"Selecciona el n\u00famero de asistentes", None))
#endif // QT_CONFIG(tooltip)
        self.label.setText(QCoreApplication.translate("Reservas", u"Nombre ", None))
#if QT_CONFIG(tooltip)
        self.asg_numJorn.setToolTip(QCoreApplication.translate("Reservas", u"Selecciona cuantas jornadas durar\u00e1 el congreso", None))
#endif // QT_CONFIG(tooltip)
        self.label_4.setText(QCoreApplication.translate("Reservas", u"Fecha", None))
#if QT_CONFIG(tooltip)
        self.asg_lineaTel.setToolTip(QCoreApplication.translate("Reservas", u"Introduce tel\u00e9fono para la reserva", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.asg_tipoCocina.setToolTip(QCoreApplication.translate("Reservas", u"Selecciona el tipo de Cocina", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.label_5.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.label_5.setStyleSheet(QCoreApplication.translate("Reservas", u";", None))
        self.label_5.setText(QCoreApplication.translate("Reservas", u"N\u00famero de Asistentes", None))
#if QT_CONFIG(tooltip)
        self.asg_lineaNombre.setToolTip(QCoreApplication.translate("Reservas", u"Introduce nombre para la reserva", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.asg_checkBox.setToolTip(QCoreApplication.translate("Reservas", u"Seleccciona solo si los asistentes necesitan habitaci\u00f3n", None))
#endif // QT_CONFIG(tooltip)
        self.asg_checkBox.setText(QCoreApplication.translate("Reservas", u"\u00bfHabitaciones para asistentes?", None))
        self.asg_volver.setText(QCoreApplication.translate("Reservas", u"Volver", None))
        self.asg_finalizar.setText(QCoreApplication.translate("Reservas", u"Finalizar Reserva", None))
    # retranslateUi

