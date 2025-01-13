import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QApplication, QListWidgetItem, QTableWidgetItem, QMessageBox

from tarea3.Control.basedatos import BD
from tarea3.Control.reservar import Reservar
from tarea3.Vistas.ui_frmMostrarReservas import Ui_MostrarReservas


class MostrarReservas(QMainWindow, Ui_MostrarReservas):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("./Recursos/img/brianda1.png"))

        self.datos = None
        self.bd = BD()
        self.setupUi(self)

        self.conectar_bd()
        self.f_introducirDatos()
        self.salon_seleccionado = None
        self.reserva_seleccionada = None

        self.ventana_reservar = Reservar(self.bd)

        self.asg_listaWidget.itemClicked.connect(self.seleccionar_salon)
        self.asg_botonReservar.clicked.connect(self.abrir_ventana_reservar)
        self.ventana_reservar.reserva_guardada.connect(self.actualizar_reservas)
        self.asg_edit_reserva.clicked.connect(self.abrir_ventana_editar)
        self.asg_tablaWidget.cellClicked.connect(self.seleccionar_reserva)
        self.asg_edit_reserva.setVisible(False)

    def conectar_bd(self):
        self.bd.CrearConexion()

    def seleccionar_reserva(self, row):
        reserva = []
        for col in range(self.asg_tablaWidget.columnCount()):
            reserva.append(self.asg_tablaWidget.item(row, col).text())

        # guardar la reserva seleccionada para editarla
        self.reserva_seleccionada = reserva
        print(f"Reserva seleccionada: {self.reserva_seleccionada}")
        # hacer visible el botón de editar reserva
        self.asg_edit_reserva.setVisible(True)

    def seleccionar_salon(self, item):
        if not item:
            print("No se ha seleccionado ningún salón.")
            return
        self.salon_seleccionado = item.text()
        self.mostrar_reservas_en_tabla(self.salon_seleccionado)

    def f_introducirDatos(self):
        self.datos = self.bd.Consulta("SELECT nombre FROM salones")
        self.asg_listaWidget.clear()
        for f, fila in enumerate(self.datos):
            print(f"Fila {f}: {fila}")
            item = QListWidgetItem(fila[0])
            self.asg_listaWidget.addItem(item)

    def obtener_reservas(self, salon):
        consulta = (
            f"SELECT r.fecha, "
            f"r.persona, "
            f"r.telefono, "
            f"t.nombre "
            f"FROM reservas r "
            f"JOIN salones s ON r.salon_id = s.salon_id "
            f"JOIN tipos_reservas t ON r.tipo_reserva_id = t.tipo_reserva_id "
            f"WHERE s.nombre = '{salon}' "
            f"ORDER BY r.fecha DESC;"
        )
        resultado = self.bd.Consulta(consulta)

        if resultado != 'Error':
            return resultado
        else:
            return []

    def actualizar_reservas(self):
        salon = self.salon_seleccionado
        if salon:
            print(f"Actualizando reservas para el salón: {salon}")
            self.mostrar_reservas_en_tabla(salon)

    def mostrar_reservas_en_tabla(self, salon):
        reservas = self.obtener_reservas(salon)

        if not salon:
            print("No se ha seleccionado ningún salón.")
            return

        # Limpiar la tabla antes de insertar los nuevos datos
        self.asg_tablaWidget.setRowCount(0)

        if not reservas:
            print("No hay reservas para este salón.")
            return

        for fila, reserva in enumerate(reservas):
            self.asg_tablaWidget.insertRow(fila)
            for columna, valor in enumerate(reserva):
                # No queremos editar desde la tabla
                item = QTableWidgetItem(str(valor))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.asg_tablaWidget.setItem(fila, columna, item)

        self.asg_tablaWidget.resizeRowsToContents()
        self.asg_tablaWidget.resizeColumnsToContents()

    def abrir_ventana_reservar(self):
        if not self.salon_seleccionado:
            QMessageBox.warning(self, "Advertencia", "Por favor, seleccione un salón antes de reservar.")
            return

        self.reserva_seleccionada = None
        self.ventana_reservar.configurar_salon(self.salon_seleccionado)
        self.ventana_reservar.limpiar_campos()
        self.ventana_reservar.show()

    def abrir_ventana_editar(self):
        if not self.salon_seleccionado:
            QMessageBox.warning(self, "Advertencia", "Por favor, seleccione un salón antes de reservar.")
            return
        # si clicamos en reservar y volvemos, debemos volver a seleccionar la reserva,
        # puesto que la hemos vaciado al hacer click en reservar
        if not self.reserva_seleccionada:
            QMessageBox.warning(self, "Advertencia", "Por favor, seleccione una reserva para editar.")
            return

        self.ventana_reservar.configurar_salon(self.salon_seleccionado)
        self.ventana_reservar.cargar_reserva(self.reserva_seleccionada)

        self.ventana_reservar.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    controlador = MostrarReservas()
    controlador.show()
    sys.exit(app.exec())
