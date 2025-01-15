import re
import sqlite3
import os

class DB_SQLite:
    def __init__(self, ruta_relativa, ruta_absoluta=None):
        """
        Inicializa la conexión a la base de datos SQLite.
        
        :param Nombre: Nombre de la base de datos.
        """
        try:
            Nombre = self.obtener_ruta_absoluta(ruta_relativa, ruta_absoluta)
            self.conn = sqlite3.connect(f'{Nombre}.db')
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Error al conectar con la base de datos: {e}")
            self.conn = None

    def obtener_ruta_absoluta(self, db_relative_path: str, base_directory: str) -> str:
        """
        Resuelve una ruta relativa a una ruta absoluta partiendo del directorio base.
        
        Args:
            db_relative_path (str): Ruta relativa de la base de datos (ej: "../../database/data")
            base_directory (str): Ruta absoluta del directorio base (ej: "C:/Users/Admin/Desktop/Repos/SuperMaker/sistema_caja/backend/app")
            
        Returns:
            str: Ruta absoluta de la base de datos
        """
        # Combina el directorio base con la ruta relativa de la base de datos
        full_path = os.path.join(base_directory, db_relative_path)
        
        # Resuelve la ruta absoluta
        absolute_path = os.path.abspath(full_path)
        
        return absolute_path

    def __enter__(self):
        """
        Método para el manejo del contexto 'with'.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Método para el manejo del contexto 'with'.
        Cierra la conexión a la base de datos al salir del contexto.
        """
        try:
            self.cerrar()
        except Exception as e:
            print(f"Error al cerrar la conexión: {e}")

    def cerrar(self):
        """
        Cierra la conexión a la base de datos.
        """
        if self.conn:
            self.conn.close()
            self.conn = None

    def Crear_tabla_nueva(self, Tabla, **columnas):
        """
        Crea una nueva tabla en la base de datos.

        :param Tabla: Nombre de la tabla.
        :param columnas: Columnas de la tabla y sus tipos.
        """
        try:
            columnas = ", ".join(f"{Columna} {Tipo}" for Columna, Tipo in columnas.items())

            Resultado = f'''
                CREATE TABLE IF NOT EXISTS {Tabla} (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    {columnas}
                ) 
            '''

            self.cursor.execute(Resultado)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error al crear la tabla: {e}")

    def Ingresar(self, Tabla, **valores_columnas):
        """
        Inserta un nuevo registro en la tabla especificada.

        :param Tabla: Nombre de la tabla.
        :param valores_columnas: Valores de las columnas a insertar.
        """
        try:
            # Separar las columnas y los valores para la consulta
            columnas = ', '.join(valores_columnas.keys())
            valores = tuple(valores_columnas.values())

            # Crear la consulta de inserción
            placeholders = ', '.join(['?'] * len(valores_columnas))  # Para evitar inyecciones SQL
            consulta = f"INSERT INTO {Tabla} ({columnas}) VALUES ({placeholders})"

            # Ejecutar la consulta
            self.cursor.execute(consulta, valores)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error al ingresar datos: {e}")
    
    def Modificar(self, Tabla, categoria, nuevo_value, Agregado = None):
        """
        Modifica un registro existente en la tabla especificada.

        :param Tabla: Nombre de la tabla.
        :param Nombre: Nombre del registro a modificar.
        :param categoria: Columna a modificar.
        :param nuevo_value: Nuevo valor para la columna.
        """
        try:
            # Validar que el nombre de la tabla no sea peligroso
            if not Tabla.isidentifier():
                raise ValueError(f"El nombre de la tabla '{Tabla}' no es válido.")

            consulta = f"UPDATE {Tabla} SET {categoria} = ?"

            # Validar y agregar cláusulas adicionales
            if not Agregado == None:
                Agregado, parametros = self.validar_agregado(Agregado)
                consulta += f" {Agregado}"
                parametros.insert(0, nuevo_value)
            #print(consulta, parametros)
            
            self.cursor.execute(consulta, parametros)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error al modificar datos: {e}")

    def Eliminar(self, Tabla, Agregado = None):
        """
        Modifica un registro existente en la tabla especificada.

        :param Tabla: Nombre de la tabla.
        :param Nombre: Nombre del registro a modificar.
        :param categoria: Columna a modificar.
        :param nuevo_value: Nuevo valor para la columna.
        """
        try:
            # Validar que el nombre de la tabla no sea peligroso
            if not Tabla.isidentifier():
                raise ValueError(f"El nombre de la tabla '{Tabla}' no es válido.")

            consulta = f"DELETE FROM {Tabla}"

            # Validar y agregar cláusulas adicionales
            if not Agregado == None:
                Agregado, parametros = self.validar_agregado(Agregado)
                consulta += f" {Agregado}"
            #print(consulta, parametros)
            
            self.cursor.execute(consulta, parametros)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error al modificar datos: {e}")

    def Consultar(self, Tabla=None, Agregado=None, Columna='*'):
        """
        Consulta registros de la tabla especificada.

        :param Tabla: Nombre de la tabla.
        :param Agregado: Cláusula adicional para la consulta (e.g., WHERE).
        :param Columna: Columnas a seleccionar.
        :return: Resultados de la consulta.
        """
        try:
            # Si no se especifica tabla, se asume una consulta especial
            if Tabla is None and Agregado == "last_insert_rowid()":
                consulta = "SELECT last_insert_rowid()"
                self.cursor.execute(consulta)
                return self.cursor.fetchone()
            elif Tabla is None and Agregado == "rowcount":
                return self.cursor.rowcount   
            # Validar que el nombre de la tabla no sea peligroso
            if not Tabla.isidentifier():
                raise ValueError(f"El nombre de la tabla '{Tabla}' no es válido.")

            # Validar que las columnas sean válidas
            if Columna != '*':
                self.validar_columnas(Columna)
            # Construir la consulta base
            consulta = f"SELECT {Columna} FROM {Tabla}"

            # Validar y agregar cláusulas adicionales
            if not Agregado == None:
                Agregado, parametros = self.validar_agregado(Agregado)
                consulta += f" {Agregado}"
            #print(consulta, parametros)

            # Ejecutar la consulta usando parámetros
            self.cursor.execute(consulta, parametros)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error al consultar datos: {e}")

    def validar_columnas(self, Columna):
        """
        Valida si las columnas en la consulta son identificadores válidos o expresiones SQL válidas.
        
        :param Columna: Columnas a validar (e.g., Producto,SUM(Cantidad)).
        :return: True si la columna es válida, False en caso contrario.
        """
        # Verificar que el valor no esté vacío
        if not Columna:
            raise ValueError("La columna no puede estar vacía.")
        
        # Expresión regular para verificar identificadores y expresiones SQL válidas
        # Esta expresión permite identificadores simples o funciones agregadas como SUM(Cantidad)
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$|^SUM\([a-zA-Z_][a-zA-Z0-9_]*\)$|^AVG\([a-zA-Z_][a-zA-Z0-9_]*\)$|^COUNT\([a-zA-Z_][a-zA-Z0-9_]*\)$|^MIN\([a-zA-Z_][a-zA-Z0-9_]*\)$|^MAX\([a-zA-Z_][a-zA-Z0-9_]*\)$'
        
        # Separar la cadena por comas y validar cada parte
        columnas = Columna.split(',')
        
        for columna in columnas:
            if not re.match(pattern, columna.strip()):
                return False  # Si alguna parte no es válida, retorna False

        return True  # Si todas las partes son válidas
    
    def validar_agregado(self, agregado):
        """
        Valida y procesa la cláusula adicional para la consulta.

        :param agregado: Cláusula adicional (e.g., WHERE).
        :return: Cláusula procesada y parámetros.
        """
        try:
            # Eliminar espacios extras en toda la cláusula
            agregado = ' '.join(agregado.split())

            # Lista de palabras clave peligrosas
            # Verificar que no contenga palabras clave peligrosas
            if any(palabra in agregado.upper() for palabra in ['DROP', 'INSERT']):
                raise ValueError(f"El parámetro {agregado} contiene una cláusula peligrosa.")

            # Utilizar expresión regular para capturar condiciones
            partes = re.findall(r"'(.*?)'|\"(.*?)\"|(\S+)", agregado)

            parametros = []  # Lista de valores para los placeholders
            partes_procesadas = []  # Lista de fragmentos SQL procesados

            operadores = ['=', 'LIKE', '<', '>', '<=', '>=', '!=']  # Operadores soportados

            for i, parte in enumerate(partes):
                if parte[0]:  # Si está entre comillas simples
                    valor = parte[0]
                    parametros.append(valor)
                elif parte[1]:  # Si está entre comillas dobles
                    valor = parte[1]
                    parametros.append(valor)
                else:  # Caso de palabra o expresión sin comillas
                    valor = parte[2]

                    # Verificar si contiene un operador
                    for operador in operadores:
                        if operador in valor.upper():
                            columna, valor = map(str.strip, valor.split(operador, 1))
                            partes_procesadas.append(f"{columna} {operador} ?")
                            if valor != '':
                                parametros.append(valor)
                                #print("Fin_semi: ",partes_procesadas)
                            break
                    else:
                        # Si no es un operador, agregarlo como está (e.g., AND, OR)
                        partes_procesadas.append(valor)
                        #print("Fin: ",partes_procesadas)

            # Reconstruir la cláusula con las partes procesadas
            agregado = ' '.join(partes_procesadas)

            return agregado, parametros
        except Exception as e:
            print(f"Error al validar el agregado: {e}")
