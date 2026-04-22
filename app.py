from flask import Flask, render_template, request, redirect, url_for
import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

# Cargar variables del archivo .env
load_dotenv()

app = Flask(__name__)

# Variables de entorno
remitente = os.getenv("EMAIL_USER")
clave = os.getenv("EMAIL_PASS")

# Configurar Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET")
)

# Página principal
@app.route("/")
def index():
    return render_template("index.html")

# Agregar producto con imagen
@app.route("/agregar", methods=["GET", "POST"])
def agregar():
    if request.method == "POST":
        nombre = request.form["nombre"]
        precio = request.form["precio"]
        foto = request.files["foto"]

        if foto:
            # 🔥 Subir imagen a Cloudinary
            resultado = cloudinary.uploader.upload(foto)
            url_imagen = resultado["secure_url"]

            print("Nombre:", nombre)
            print("Precio:", precio)
            print("Imagen URL:", url_imagen)

        return redirect(url_for("index"))

    return render_template("agregar.html")


if __name__ == "__main__":
    print("EMAIL_USER:", remitente)
    print("EMAIL_PASS:", clave)
    app.run(debug=True)