from flask import Flask
import os
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

app = Flask(__name__)

# Obtener variables de entorno
remitente = os.getenv("EMAIL_USER")
clave = os.getenv("EMAIL_PASS")

@app.route("/")
def index():
    return "Sistema funcionando correctamente"

if __name__ == "__main__":
    print("EMAIL_USER:", remitente)
    print("EMAIL_PASS:", clave)
    app.run(debug=True)