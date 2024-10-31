# Importamos librerías
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Levantamos servidor
App = Flask(__name__, static_url_path='/static')
App.secret_key = 'your_secret_key'  # Clave secreta para mensajes flash

# Configuración de la base de datos
App.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
App.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
App.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
App.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
App.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(App)

# Creamos rutas

# Ruta index
@App.route('/')
def index():
    return render_template('index.html')

# Ruta register
@App.route('/register')
def register():
    return render_template('register.html')

# Ruta para manejar el registro
@App.route('/registrar-usuario', methods=['POST'])
def registrar_usuario():
    print("Entrando a la función registrar_usuario()")  # Mensaje de depuración
    if request.method == 'POST':
        correo = request.form['email']
        contraseña = request.form['password']
        nombre = request.form['nombre']
        direccion = request.form['direccion']
        telefono = request.form['telefono']

        print("Datos del formulario recibidos:")  # Mensaje de depuración
        print("Correo:", correo)
        print("Contraseña:", contraseña)
        print("Nombre:", nombre)
        print("Dirección:", direccion)
        print("Teléfono:", telefono)

        # Verificar si el correo ya está registrado
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuarios WHERE CORREO = %s', (correo,))
        usuario_existente = cur.fetchone()
        cur.close()

        if usuario_existente:
            flash('El correo electrónico ya está registrado', 'error')
            print("Usuario ya registrado:", correo)  # Mensaje de depuración
            return redirect(url_for('index'))
        else:
            # Insertar usuario en la base de datos
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO usuarios (CORREO, CONTRASEÑA, NOMBRE, DIRECCION, NRO_TELEFONO) VALUES (%s, %s, %s, %s, %s)', (correo, contraseña, nombre, direccion, telefono))
            mysql.connection.commit()
            cur.close()
            flash('Registro exitoso. Ahora puedes iniciar sesión', 'success')
            print("Usuario registrado:", correo)  # Mensaje de depuración
            return redirect(url_for('index'))  # Redireccionar a la página de inicio después del registro

# Ruta inicio
@App.route('/inicio')
def inicio():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios")
    usuarios = cur.fetchall()
    cur.close()
    return render_template('inicio.html', usuarios=usuarios)
    print("Llamando a la función inicio()")  # Mensaje de depuración
    return render_template('inicio.html')

@App.route ('/usuarios')
def usuarios():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios")
    usuarios = cur.fetchall()
    cur.close()
    return render_template('usuarios.html', usuarios=usuarios)
    print("Llamando a la función usuarios()")  # Mensaje de depuración
    return render_template('usuarios.html')

# Ruta pedidos
@App.route('/pedidos')
def pedidos():
    return render_template('pedidos.html')


# Ruta base de datos

# Consulta a la base de datos y posterior visualización de datos
# Ruta para mostrar datos de la tabla usuarios
@App.route('/data')
def data():
    # Conectar a la base de datos
    cur = mysql.connection.cursor()
    # Ejecutar consulta SQL para seleccionar todos los registros de la tabla usuarios
    cur.execute('SELECT * FROM usuarios')
    # Obtener los datos resultantes de la consulta
    data = cur.fetchall()
    # Cerrar el cursor
    cur.close()
    # Renderizar la plantilla HTML 'index.html' con los datos obtenidos
    return render_template('index.html', usuarios=data)

    
@App.route('/delete/<string:correo>')
def delete(correo):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM usuarios WHERE Correo = %s', (correo,))
    mysql.connection.commit()
    cur.close()
    flash('Usuario eliminado')
    return redirect(url_for('usuarios'))


@App.route('/usuarios/editar-direccion/<string:correo>', methods=['GET', 'POST'])
def editar_direccion(correo):
    if request.method == 'POST':
        nueva_direccion = request.form['nueva_direccion']

        cur = mysql.connection.cursor()
        cur.execute('UPDATE usuarios SET Direccion = %s WHERE Correo = %s', (nueva_direccion, correo))
        mysql.connection.commit()
        cur.close()

        flash('Dirección actualizada exitosamente', 'success')
        return redirect(url_for('usuarios'))  

    cur = mysql.connection.cursor()
    cur.execute('SELECT Direccion FROM usuarios WHERE Correo = %s', (correo,))
    usuario = cur.fetchone()
    cur.close()

    return redirect(url_for('usuarios', correo=usuario['Correo'], usuario=usuario))


@App.route('/usuarios/delete/<string:correo>')
def delete_usuario(correo):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM usuarios WHERE Correo = %s', (correo,))
    mysql.connection.commit()
    cur.close()
    flash('Usuario eliminado exitosamente', 'success')
    return redirect(url_for('usuarios')) 



# Inicialización de la base de datos
def init_db():
    with App.app_context():
        cur = mysql.connection.cursor()
        cur.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        Correo VARCHAR(100) PRIMARY KEY,
        Contraseña VARCHAR(100),
        Nombre VARCHAR(100),
        Direccion VARCHAR(100),
        Nro VARCHAR(20)
    )
''')
        mysql.connection.commit()

# Levantamos servidor
if __name__ == '__main__':
    init_db() # Inicializar la base de datos antes de manejar cualquier solicitud
    App.run(port=8000, debug=True)
