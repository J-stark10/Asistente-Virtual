from flask import Flask, render_template, request, jsonify
import pdfplumber
from rapidfuzz import process


def corregir_texto(texto):

    texto = texto.lower()

    correcciones = {
        "api rest": "api restful",
        "api rest full": "api restful",
        "a p i": "api",
        "git hub": "github",
        "git ignore": ".gitignore",
        "git ignor": ".gitignore",
        "j son": "json",
        "json": "json",
        "jwt": "jwt",
        "micro servicios": "microservicios",
        "crm": "crm",
        "erp": "erp",
        "sql": "sql",
        "html": "html",
        "css": "css",
        "javascript": "javascript"
    }

    for mal, bien in correcciones.items():
        texto = texto.replace(mal, bien)

    return texto

app = Flask(__name__)

preguntas_respuestas = {}



def cargar_pdf():
    global preguntas_respuestas

    texto = ""

    with pdfplumber.open("documento.pdf") as pdf:
        for pagina in pdf.pages:
            contenido = pagina.extract_text(x_tolerance=2, y_tolerance=2)
            if contenido:
                texto += contenido + "\n"

    texto = texto.replace("￾", "")

    lineas = [l.strip() for l in texto.split("\n") if l.strip()]

    pregunta_actual = None
    respuesta_actual = []

    for linea in lineas:

        if "?" in linea:
            if pregunta_actual:
                preguntas_respuestas[pregunta_actual] = " ".join(respuesta_actual)

            pregunta_actual = linea
            respuesta_actual = []

        else:
            respuesta_actual.append(linea)

    if pregunta_actual:
        preguntas_respuestas[pregunta_actual] = " ".join(respuesta_actual)

cargar_pdf()

@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/preguntar", methods=["POST"])
def preguntar():

    pregunta_usuario = request.json["pregunta"]

    # 🔥 limpiar voz mal entendida
    pregunta_usuario = corregir_texto(pregunta_usuario)

    mejor = process.extractOne(
        pregunta_usuario,
        preguntas_respuestas.keys()
    )

    if mejor and mejor[1] > 40:   # 👈 más flexible
        respuesta = preguntas_respuestas[mejor[0]]
    else:
        respuesta = "No encontré una respuesta en el documento."

    return jsonify({
        "pregunta_encontrada": mejor[0] if mejor else "",
        "respuesta": respuesta
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)