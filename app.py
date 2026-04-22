from flask import Flask, render_template, request, redirect, url_for
import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
from flask_sqlalchemy import SQLAlchemy

# =========================
# CONFIG INICIAL
# =========================
load_dotenv()
app = Flask(__name__)

# =========================
# BASE DE DATOS
# =========================
uri = os.getenv("DATABASE_URL")

if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

if not uri:
    uri = "sqlite:///tienda.db"

app.config["SQLALCHEMY_DATABASE_URI"] = uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =========================
# MODELO
# =========================
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    precio = db.Column(db.Float)
    stock = db.Column(db.Integer)
    imagen = db.Column(db.String(300))

# =========================
# CLOUDINARY
# =========================
cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET")
)

# =========================
# CREAR TABLAS
# =========================
with app.app_context():
    db.create_all()

# =========================
# DASHBOARD
# =========================
@app.route("/")
def index():
    productos = Producto.query.all()

    total_productos = len(productos)
    stock_bajo = len([p for p in productos if p.stock < 5])
    total_valor = sum([p.precio * p.stock for p in productos])

    return render_template(
        "index.html",
        productos=productos,
        total_productos=total_productos,
        stock_bajo=stock_bajo,
        total_valor=total_valor
    )

# =========================
# AGREGAR PRODUCTO
# =========================
@app.route("/agregar", methods=["GET", "POST"])
def agregar():
    if request.method == "POST":
        nombre = request.form["nombre"]
        precio = float(request.form["precio"])
        stock = int(request.form["stock"])

        foto = request.files.get("foto")
        url_imagen = ""

        if foto and foto.filename != "":
            resultado = cloudinary.uploader.upload(foto)
            url_imagen = resultado["secure_url"]

        nuevo = Producto(
            nombre=nombre,
            precio=precio,
            stock=stock,
            imagen=url_imagen
        )

        db.session.add(nuevo)
        db.session.commit()

        return redirect(url_for("index"))

    return render_template("agregar.html")

# =========================
# ELIMINAR PRODUCTO
# =========================
@app.route("/eliminar/<int:id>")
def eliminar(id):
    producto = Producto.query.get(id)

    if producto:
        db.session.delete(producto)
        db.session.commit()

    return redirect(url_for("index"))

# =========================
# EDITAR PRODUCTO COMPLETO
# =========================
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    producto = Producto.query.get(id)

    if request.method == "POST":
        producto.nombre = request.form["nombre"]
        producto.precio = float(request.form["precio"])
        producto.stock = int(request.form["stock"])

        foto = request.files.get("foto")

        if foto and foto.filename != "":
            resultado = cloudinary.uploader.upload(foto)
            producto.imagen = resultado["secure_url"]

        db.session.commit()
        return redirect(url_for("index"))

    return render_template("editar.html", producto=producto)

# =========================
# EDITAR SOLO STOCK (RÁPIDO)
# =========================
@app.route("/editar_stock/<int:id>", methods=["POST"])
def editar_stock(id):
    producto = Producto.query.get(id)

    if producto:
        producto.stock = int(request.form["stock"])
        db.session.commit()

    return redirect(url_for("index"))

# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(debug=True)