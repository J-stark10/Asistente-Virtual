from flask import Flask, render_template, request, jsonify
import pdfplumber
from rapidfuzz import process

app = Flask(__name__)

preguntas_respuestas = {}

def cargar_pdf():
    global preguntas_respuestas

    texto = ""

    with pdfplumber.open("documento.pdf") as pdf:
        for pagina in pdf.pages:
            contenido = pagina.extract_text()
            if contenido:
                texto += contenido + "\n"

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

    mejor = process.extractOne(
        pregunta_usuario,
        preguntas_respuestas.keys()
    )

    if mejor and mejor[1] > 50:
        respuesta = preguntas_respuestas[mejor[0]]
    else:
        respuesta = "No encontré una respuesta en el documento."

    return jsonify({
        "pregunta_encontrada": mejor[0] if mejor else "",
        "respuesta": respuesta
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)