from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import cloudinary
import cloudinary.uploader
import os
import pandas as pd
from datetime import datetime, timedelta

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
# MODELOS
# =========================
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    precio = db.Column(db.Float)
    stock = db.Column(db.Integer)
    imagen = db.Column(db.String(300))


class Venta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer)
    nombre = db.Column(db.String(100))
    cantidad = db.Column(db.Integer)
    total = db.Column(db.Float)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)


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
    ventas = Venta.query.all()

    total_ventas = sum([v.total for v in ventas])

    return render_template(
        "index.html",
        productos=productos,
        total_ventas=total_ventas
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
# EDITAR PRODUCTO
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
# ELIMINAR
# =========================
@app.route("/eliminar/<int:id>")
def eliminar(id):
    producto = Producto.query.get(id)
    if producto:
        db.session.delete(producto)
        db.session.commit()
    return redirect(url_for("index"))

# =========================
# VENDER PRODUCTO
# =========================
@app.route("/vender/<int:id>", methods=["POST"])
def vender(id):
    producto = Producto.query.get(id)
    cantidad = int(request.form["cantidad"])

    if producto and producto.stock >= cantidad:
        producto.stock -= cantidad

        venta = Venta(
            producto_id=producto.id,
            nombre=producto.nombre,
            cantidad=cantidad,
            total=producto.precio * cantidad
        )

        db.session.add(venta)
        db.session.commit()

    return redirect(url_for("index"))

# =========================
# REPORTE DIARIO
# =========================
@app.route("/reporte/dia")
def reporte_dia():
    hoy = datetime.utcnow().date()

    ventas = Venta.query.filter(
        db.func.date(Venta.fecha) == hoy
    ).all()

    data = [{
        "Producto": v.nombre,
        "Cantidad": v.cantidad,
        "Total": v.total,
        "Fecha": v.fecha
    } for v in ventas]

    df = pd.DataFrame(data)
    archivo = "reporte_dia.xlsx"
    df.to_excel(archivo, index=False)

    return send_file(archivo, as_attachment=True)

# =========================
# REPORTE SEMANAL
# =========================
@app.route("/reporte/semana")
def reporte_semana():
    hace_7_dias = datetime.utcnow() - timedelta(days=7)

    ventas = Venta.query.filter(
        Venta.fecha >= hace_7_dias
    ).all()

    data = [{
        "Producto": v.nombre,
        "Cantidad": v.cantidad,
        "Total": v.total,
        "Fecha": v.fecha
    } for v in ventas]

    df = pd.DataFrame(data)
    archivo = "reporte_semana.xlsx"
    df.to_excel(archivo, index=False)

    return send_file(archivo, as_attachment=True)

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)