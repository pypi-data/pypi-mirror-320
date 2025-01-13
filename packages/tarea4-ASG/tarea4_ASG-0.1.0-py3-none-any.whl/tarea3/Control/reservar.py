import sys

from PySide6.QtCore import QTimer, Signal, QDate
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QApplication, QMessageBox, QLabel

from tarea3.Vistas.ui_frmReservas import Ui_Reservas


class Reservar(QWidget, Ui_Reservas):
    reserva_guardada = Signal()

    def __init__(self, bd):
        super().__init__()
        self.setWindowIcon(QIcon("./Recursos/img/brianda1.png"))

        self.setupUi(self)
        self.bd = bd
        self.salon = None
        self.reserva_seleccionada = None
        self.asg_tipoReserva.currentTextChanged.connect(self.opcionCongreso)

        self.asg_finalizar.clicked.connect(self.validar_y_guardar_reserva)  # Conectar el botón de finalizar
        self.asg_volver.clicked.connect(self.cerrar_ventana)

        self.toast_label = QLabel(self)
        self.toast_label.setStyleSheet(
            "background-color: rgba(0, 0, 0, 200); color: white; padding: 10px; border-radius: 5px;")
        self.toast_label.setVisible(False)

    def obtener_tipos_reserva(self):
        consulta = "SELECT nombre FROM tipos_reservas"
        resultado = self.bd.Consulta(consulta)

        if resultado != 'Error':
            return [fila[0] for fila in resultado]
        else:
            return []

    def obtener_tipos_cocina(self):
        consulta = "SELECT nombre FROM tipos_cocina"
        resultado = self.bd.Consulta(consulta)

        if resultado != 'Error':

            return [fila[0] for fila in resultado]
        else:
            print("Error al obtener los tipos de cocina.")
            return []

    def configurar_salon(self, salon):
        print(f"Salón configurado: {salon}")
        self.salon = salon

        tipos_reserva = self.obtener_tipos_reserva()
        tipos_cocina = self.obtener_tipos_cocina()

        self.asg_tipoReserva.clear()
        self.asg_tipoCocina.clear()

        if tipos_reserva:
            for tipo in tipos_reserva:
                self.asg_tipoReserva.addItem(tipo)
        else:
            print("No se encontraron tipos de reserva.")

            # Si hay tipos de cocina, añadirlos al ComboBox
        if tipos_cocina:
            for tipo in tipos_cocina:
                self.asg_tipoCocina.addItem(tipo)
        else:
            print("No se encontraron tipos de cocina.")

        self.opcionCongreso(self.asg_tipoReserva.currentText())

    def opcionCongreso(self, tipo_reserva):
        if tipo_reserva == "Congreso":
            self.asg_numJorn.setEnabled(True)
            self.asg_checkBox.setEnabled(True)
            self.asg_textoCongreso.setEnabled(True)
            self.asg_textoCongreso.setVisible(True)
            self.asg_numJorn.setVisible(True)
            self.asg_checkBox.setVisible(True)
        else:
            # Ocultar y deshabilitar los campos si no es Congreso
            self.asg_numJorn.setEnabled(False)
            self.asg_checkBox.setEnabled(False)
            self.asg_textoCongreso.setEnabled(False)
            self.asg_textoCongreso.setVisible(False)
            self.asg_numJorn.setVisible(False)
            self.asg_checkBox.setVisible(False)

    def limpiar_campos(self):

        self.asg_lineaNombre.clear()
        self.asg_lineaTel.clear()
        self.asg_fecha.setDate(QDate.currentDate())
        self.asg_tipoReserva.setCurrentIndex(0)

    def guardar_reserva(self):
        if not self.salon:
            QMessageBox.warning(self, "Advertencia", "No hay un salón configurado para la reserva.")
            return

        nombre = self.asg_lineaNombre.text().strip()
        telefono = self.asg_lineaTel.text().strip()
        fecha = self.asg_fecha.date().toString("dd/MM/yyyy")
        tipo_reserva = self.asg_tipoReserva.currentText()
        tipo_cocina = self.asg_tipoCocina.currentText()
        numero_asistentes = self.asg_numeroAsis.value()
        jornadas = self.asg_numJorn.value()
        habitaciones = self.asg_checkBox.isChecked()

        # Verificar si la reserva ya existe
        consulta_existente = (
            f"SELECT reserva_id FROM reservas WHERE persona = '{nombre}' AND telefono = '{telefono}' "

        )

        try:
            print(f"Nombre: {nombre}, Teléfono: {telefono}, Fecha: {fecha}, Salón: {self.salon}")

            resultado_existente = self.bd.Consulta(consulta_existente)
            print(
                # depuracion
                f"Resultado de la consulta de existencia: {resultado_existente}")

            if resultado_existente != 'Error' and resultado_existente:
                # Si existe, realizar un UPDATE
                reserva_id = resultado_existente[0][0]  # Obtener el reserva_id
                consulta_update = (
                    f"UPDATE reservas SET "
                    f"tipo_reserva_id = (SELECT tipo_reserva_id FROM tipos_reservas WHERE nombre = '{tipo_reserva}'), "
                    f"tipo_cocina_id = (SELECT tipo_cocina_id FROM tipos_cocina WHERE nombre = '{tipo_cocina}'), "
                    f"ocupacion = {numero_asistentes}, "
                    f"jornadas = {jornadas}, "
                    f"habitaciones = {int(habitaciones)} "
                    f"WHERE reserva_id = {reserva_id}"
                )
                print(f"Consulta de actualización: {consulta_update}")
                resultado = self.bd.Consulta(consulta_update)
                if resultado in ['Insertado', 'Modificado']:
                    QMessageBox.information(self, "Éxito", "Reserva actualizada correctamente.")
                    self.reserva_guardada.emit()
                    self.close()
                else:
                    QMessageBox.critical(self, "Error", f"No se pudo actualizar la reserva. Resultado: {resultado}")
            else:
                # Si no existe, hacer un INSERT
                consulta_insert = (
                    f"INSERT INTO reservas (fecha, persona, telefono, tipo_reserva_id, salon_id, tipo_cocina_id, "
                    f"ocupacion, jornadas, habitaciones) "
                    f"VALUES ('{fecha}', '{nombre}', '{telefono}', "
                    f"(SELECT tipo_reserva_id FROM tipos_reservas WHERE nombre = '{tipo_reserva}'), "
                    f"(SELECT salon_id FROM salones WHERE nombre = '{self.salon}'), "
                    f"(SELECT tipo_cocina_id FROM tipos_cocina WHERE nombre = '{tipo_cocina}'), "
                    f"{numero_asistentes}, {jornadas}, {int(habitaciones)})"
                )
                print(f"Consulta de inserción: {consulta_insert}")
                resultado = self.bd.Consulta(consulta_insert)
                if resultado in ['Insertado', 'Modificado']:
                    QMessageBox.information(self, "Éxito", "Reserva guardada correctamente.")
                    self.reserva_guardada.emit()
                    self.close()
                else:
                    QMessageBox.critical(self, "Error", f"No se pudo guardar la reserva. Resultado: {resultado}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al guardar la reserva: {str(e)}")
            print(f"Error: {str(e)}")

    def cargar_reserva(self, reserva):
        self.reserva_seleccionada = reserva
        self.asg_lineaNombre.setText(reserva[1])
        self.asg_lineaTel.setText(reserva[2])
        fecha_str = reserva[0]
        fecha = QDate.fromString(fecha_str, "dd/MM/yyyy")

        if fecha.isValid():
            self.asg_fecha.setDate(fecha)
        else:
            print(f"Error: La fecha '{fecha_str}' no es válida.")

        self.asg_tipoReserva.setCurrentText(reserva[3])

    def validar_y_guardar_reserva(self):

        if not self.asg_lineaNombre.text().strip():
            self.mostrar_error("El nombre es obligatorio.")
            return

        if not self.asg_lineaTel.text().strip():
            self.mostrar_error("El teléfono es obligatorio.")
            return

        if not self.asg_fecha.date().isValid():
            self.mostrar_error("La fecha es obligatoria.")
            return

        if self.asg_numeroAsis.value() == 0:
            self.mostrar_error("El número de asistentes no puede ser 0.")
            return

        if self.asg_tipoReserva.currentText() == "":
            self.mostrar_error("El tipo de reserva es obligatorio.")
            return
        self.guardar_reserva()

    def mostrar_error(self, mensaje):

        self.toast_label.setText(mensaje)
        self.toast_label.setGeometry(200, 50, 300, 40)
        self.toast_label.setVisible(True)

        QTimer.singleShot(3000, self.ocultar_mensaje)

    def ocultar_mensaje(self):
        self.toast_label.setVisible(False)

    def cerrar_ventana(self):
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = Reservar()
    ventana.show()
    sys.exit(app.exec())
