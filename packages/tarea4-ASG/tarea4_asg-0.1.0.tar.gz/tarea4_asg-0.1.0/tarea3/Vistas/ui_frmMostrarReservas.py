# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'frmMostrarReservasfZtpfN.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QHeaderView, QListWidget,
    QListWidgetItem, QMainWindow, QMenuBar, QPushButton,
    QSizePolicy, QSplitter, QTableWidget, QTableWidgetItem,
    QWidget)

class Ui_MostrarReservas(object):
    def setupUi(self, MostrarReservas):
        if not MostrarReservas.objectName():
            MostrarReservas.setObjectName(u"MostrarReservas")
        MostrarReservas.setWindowModality(Qt.WindowModality.WindowModal)
        MostrarReservas.resize(681, 633)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MostrarReservas.sizePolicy().hasHeightForWidth())
        MostrarReservas.setSizePolicy(sizePolicy)
        MostrarReservas.setMinimumSize(QSize(0, 0))
        MostrarReservas.setMaximumSize(QSize(5000, 659))
        font = QFont()
        font.setPointSize(9)
        MostrarReservas.setFont(font)
        MostrarReservas.setStyleSheet(u"background-color: #f0f0f0;\n"
"color: #333333;\n"
"")
        self.centralwidget = QWidget(MostrarReservas)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setStyleSheet(u"background-color: #2D2D2D;\n"
"color: #E0E0E0;\n"
"")
        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setGeometry(QRect(60, 50, 572, 431))
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy1)
        self.splitter.setMinimumSize(QSize(500, 200))
        self.splitter.setMaximumSize(QSize(16777215, 492))
        self.splitter.setBaseSize(QSize(0, 0))
        self.splitter.setStyleSheet(u"handle {\n"
"    background-color: #444444;\n"
"    border: 1px solid #555555;\n"
"}\n"
"")
        self.splitter.setLineWidth(0)
        self.splitter.setMidLineWidth(0)
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(21)
        self.asg_listaWidget = QListWidget(self.splitter)
        self.asg_listaWidget.setObjectName(u"asg_listaWidget")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.asg_listaWidget.sizePolicy().hasHeightForWidth())
        self.asg_listaWidget.setSizePolicy(sizePolicy2)
        self.asg_listaWidget.setMinimumSize(QSize(100, 400))
        self.asg_listaWidget.setMaximumSize(QSize(119, 492))
        self.asg_listaWidget.setStyleSheet(u"background-color: #3C3C3C;\n"
"border: 1px solid #555555;\n"
"border-radius: 5px;\n"
"color: #E0E0E0;\n"
"\n"
"QListWidget::item {\n"
"    padding: 5px;\n"
"}\n"
"\n"
"QListWidget::item:selected {\n"
"    background-color: #505050;\n"
"    color: #FFFFFF;\n"
"}\n"
"")
        self.splitter.addWidget(self.asg_listaWidget)
        self.asg_tablaWidget = QTableWidget(self.splitter)
        if (self.asg_tablaWidget.columnCount() < 4):
            self.asg_tablaWidget.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        self.asg_tablaWidget.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.asg_tablaWidget.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.asg_tablaWidget.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.asg_tablaWidget.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        self.asg_tablaWidget.setObjectName(u"asg_tablaWidget")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy3.setHorizontalStretch(190)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.asg_tablaWidget.sizePolicy().hasHeightForWidth())
        self.asg_tablaWidget.setSizePolicy(sizePolicy3)
        self.asg_tablaWidget.setMinimumSize(QSize(400, 400))
        self.asg_tablaWidget.setMaximumSize(QSize(498, 492))
        font1 = QFont()
        font1.setPointSize(8)
        font1.setBold(False)
        self.asg_tablaWidget.setFont(font1)
        self.asg_tablaWidget.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.asg_tablaWidget.setAutoFillBackground(False)
        self.asg_tablaWidget.setStyleSheet(u"background-color: #3C3C3C;\n"
"border: 1px solid #555555;\n"
"border-radius: 5px;\n"
"gridline-color: #555555;\n"
"color: #E0E0E0;\n"
"\n"
"QHeaderView::section {\n"
"    background-color: #444444;\n"
"    color: #FFFFFF;\n"
"    font-weight: bold;\n"
"    border: 1px solid #666666;\n"
"}\n"
"\n"
"QTableWidget::item {\n"
"    border: 1px solid #555555;\n"
"}\n"
"\n"
"QTableWidget::item:selected {\n"
"    background-color: #505050;\n"
"    color: #FFFFFF;\n"
"}\n"
"")
        self.asg_tablaWidget.setAutoScroll(True)
        self.asg_tablaWidget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.asg_tablaWidget.setTextElideMode(Qt.TextElideMode.ElideLeft)
        self.asg_tablaWidget.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerItem)
        self.asg_tablaWidget.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerItem)
        self.asg_tablaWidget.setGridStyle(Qt.PenStyle.SolidLine)
        self.asg_tablaWidget.setRowCount(0)
        self.asg_tablaWidget.setColumnCount(4)
        self.splitter.addWidget(self.asg_tablaWidget)
        self.asg_tablaWidget.horizontalHeader().setMinimumSectionSize(32)
        self.asg_tablaWidget.horizontalHeader().setDefaultSectionSize(122)
        self.asg_botonReservar = QPushButton(self.centralwidget)
        self.asg_botonReservar.setObjectName(u"asg_botonReservar")
        self.asg_botonReservar.setGeometry(QRect(430, 500, 181, 41))
        font2 = QFont()
        font2.setPointSize(11)
        self.asg_botonReservar.setFont(font2)
        self.asg_botonReservar.setStyleSheet(u"\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #555555;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #666666;\n"
"}\n"
"\n"
"")
        self.asg_edit_reserva = QPushButton(self.centralwidget)
        self.asg_edit_reserva.setObjectName(u"asg_edit_reserva")
        self.asg_edit_reserva.setGeometry(QRect(70, 500, 101, 41))
        self.asg_edit_reserva.setFont(font2)
        self.asg_edit_reserva.setStyleSheet(u"QPushButton:hover {\n"
"    background-color: #555555;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #666666;\n"
"}")
        MostrarReservas.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MostrarReservas)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 681, 33))
        MostrarReservas.setMenuBar(self.menubar)

        self.retranslateUi(MostrarReservas)

        QMetaObject.connectSlotsByName(MostrarReservas)
    # setupUi

    def retranslateUi(self, MostrarReservas):
        MostrarReservas.setWindowTitle(QCoreApplication.translate("MostrarReservas", u"Mostrar Reservas", None))
        ___qtablewidgetitem = self.asg_tablaWidget.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MostrarReservas", u"Fecha", None));
        ___qtablewidgetitem1 = self.asg_tablaWidget.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MostrarReservas", u"Persona", None));
        ___qtablewidgetitem2 = self.asg_tablaWidget.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MostrarReservas", u"Tel\u00e9fono", None));
        ___qtablewidgetitem3 = self.asg_tablaWidget.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MostrarReservas", u"Tipo de Reserva", None));
#if QT_CONFIG(tooltip)
        self.asg_botonReservar.setToolTip(QCoreApplication.translate("MostrarReservas", u"Acceder a la pantalla de Reservas", None))
#endif // QT_CONFIG(tooltip)
        self.asg_botonReservar.setText(QCoreApplication.translate("MostrarReservas", u"Reservar", None))
#if QT_CONFIG(tooltip)
        self.asg_edit_reserva.setToolTip(QCoreApplication.translate("MostrarReservas", u"Acceder a la pantalla de Reservas para editar", None))
#endif // QT_CONFIG(tooltip)
        self.asg_edit_reserva.setText(QCoreApplication.translate("MostrarReservas", u"Editar", None))
    # retranslateUi

