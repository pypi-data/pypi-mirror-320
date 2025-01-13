# -*- coding: utf-8 -*-

import sqlite3


class BD:

    conexion = None
    puntero = None
    rutaBD = "tarea3/Modelo/reservas.db"

    # --- CONSTRUCTOR
    def __init__(self):
        self.conexion = None
        self.puntero = None

    # --- MEDOTOS
    def CrearConexion(self):
        try:
            # conexión SQLite
            self.conexion = sqlite3.connect(self.rutaBD)

            # conexión postgresql
            # self.conexion = psycopg2.connect(dbname=bd, user=u, host=h, password=psw, port=p)

            # conexión mysql
            # self.conexion=mysql.connector.connect(database=bd, user=u, host=h, passwd=psw)

            self.puntero = self.conexion.cursor()
            print("Conexión a la base de datos establecida.")
            return True
        except ValueError:
            return False

    def Consulta(self, sentencia):

        try:
            self.puntero.execute(sentencia)

        except Exception:
            return 'Error'

        if sentencia.upper().startswith('SELECT'):
            rows = self.puntero.fetchall()
            # rows = puntero.fetchall()
            linea = ''
            aux = 0
            for row in rows:  # recorre todos las filas q te devuelve el select
                aux = aux + 1
                # print len(rows[0])
                for i in range(0, len(rows[0])):  # recorre las columnas y lo concatena en un string
                    if i < len(rows[0]) - 1:
                        linea = linea + str(row[i]) + ','
                    else:
                        linea = linea + str(row[i])  # para q al final no aparezca una coma
                # print len(rows)
                if aux < len(rows):
                    linea = linea + '\n'

            return rows

        else:
            self.conexion.commit()
            if sentencia.upper().startswith('INSERT'):
                return 'Insertado'
            elif sentencia.upper().startswith('UPDATE'):
                return 'Modificado'
            elif sentencia.upper().startswith('DELETE'):
                return 'Eliminado'
            else:
                return 'commit'

    def ConsultaDic(self, sentencia):
        # puntero = self.conexion.cursor()
        try:
            self.puntero.execute(sentencia)
        # puntero.execute(sentencia)
        except Exception:
            return 'Error al ejecutar sentencia'
  
        if sentencia.upper().startswith('SELECT'):
            rows = self.puntero.fetchall()
            return rows

    def CerrarConexion(self):
        self.puntero.close()
        self.conexion.close()


pass

