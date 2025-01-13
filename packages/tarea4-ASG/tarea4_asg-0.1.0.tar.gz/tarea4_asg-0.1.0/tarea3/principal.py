import sys
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QToolTip, QMessageBox

from tarea3.Control.basedatos import BD
from tarea3.Control.mostrar_reservas import MostrarReservas
from tarea3.Vistas.ui_frmMainMenu import Ui_asg_ventanaMain

class Tarea(QMainWindow, Ui_asg_ventanaMain):
    def __init__(self):
        super().__init__()
        self.ui = Ui_asg_ventanaMain()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon("./Recursos/img/brianda1.png"))

        self.valid_user = "hotel"
        self.valid_password = "Brianda23$"

        self.ui.asg_pushButton.clicked.connect(self.login_action)
        self.ui.passEdit.returnPressed.connect(self.ui.asg_pushButton.click)
        self.ui.actionSalir.triggered.connect(self.close)

    def show_tooltip(self, message, color):
        QToolTip.setFont(self.ui.asg_pushButton.font())
        self.ui.asg_pushButton.setStyleSheet(f"color: {color};")
        QToolTip.showText(self.ui.asg_pushButton.mapToGlobal(self.ui.asg_pushButton.rect().center()), message)

    def login_action(self):
        user = self.ui.usuarioEdit.text()
        password = self.ui.passEdit.text()

        if user == self.valid_user and password == self.valid_password:
            self.establecer_conexion_bd()

        else:
           self.show_tooltip("Acceso denegado", "red")
           self.ui.usuarioEdit.clear()
           self.ui.passEdit.clear()

    def establecer_conexion_bd(self):
        bd = BD()
        if bd.CrearConexion():
            self.show_message_box("Conexión exitosa", "Acceso concedido", QMessageBox.Icon.Information)
            self.ui.asg_pushButton.clicked.connect(self.mostrar_reservas_ui)
            self.mostrar_reservas_ui()
        else:
            self.show_message_box("Conexión fallida", "Acceso denegado", QMessageBox.Icon.Critical)

    def show_message_box(self, title, text, icon):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setIcon(icon)
        msg_box.exec()

    def mostrar_reservas_ui(self):
        self.hide()
        self.reservas_ui = MostrarReservas()
        self.reservas_ui.show()


def main():
    app = QApplication(sys.argv)
    main_window = Tarea()
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
