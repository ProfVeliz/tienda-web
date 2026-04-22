from flask import Flask, render_template, request, redirect, url_for
import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

# Cargar variables del .env (solo local)
load_dotenv()

app = Flask(__name__)

# Configuración Cloudinary (usa .env o variables de Render)
cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET")
)

# ====== RUTA PRINCIPAL ======
@app.route("/")
def index():
    return render_template("index.html")


# ====== AGREGAR PRODUCTO ======
@app.route("/agregar", methods=["GET", "POST"])
def agregar():
    if request.method == "POST":
        nombre = request.form["nombre"]
        precio = request.form["precio"]
        stock = request.form["stock"]
        foto = request.files["foto"]

        url_imagen = None

        if foto and foto.filename != "":
            # Subir imagen a Cloudinary
            resultado = cloudinary.uploader.upload(foto)
            url_imagen = resultado["secure_url"]

        # (Por ahora solo mostramos en consola)
        print("Nombre:", nombre)
        print("Precio:", precio)
        print("Stock:", stock)
        print("Imagen URL:", url_imagen)

        return redirect(url_for("index"))

    return render_template("agregar.html")


# ====== INICIO APP ======
if __name__ == "__main__":
    app.run(debug=True)