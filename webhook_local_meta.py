from flask import Flask, request
from datetime import datetime
import requests
import boto3
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
contador=0
#Webhook_Meta
token_webhook=os.getenv("TOKEN_WEBHOOK")
token_permanente_meta=os.getenv("TOKEN_PERMANENTE_META")

#Cloudflare
endpoint_almacenamiento=os.getenv("ENDPOINT_ALMACENAMIENTO")
nombre_bucket=os.getenv("NOMBRE_BUCKET")
access_key=os.getenv("ACCESS_KEY")
secret_access_key=os.getenv("SECRET_ACCESS_KEY")

#objeto cloudflare
#parametro 1 = tipo de servidor, parametro 2 = ruta servidor de almacenamiento, parametro 3 = usuario, parametro 4 = contrasenia, parametro 5 = region servidor
cloudflare= boto3.client("s3", endpoint_url=endpoint_almacenamiento, aws_access_key_id=access_key, aws_secret_access_key=secret_access_key, region_name="auto")

def datos_Json(json):
    #CONTINUAR AQUI
    comienzo=json["entry"][0]["changes"][0]["value"]

    n_Telefono=comienzo["messages"][0]["from"]
    user_name=comienzo["contacts"][0]["profile"]["name"]
    timestamp=comienzo["messages"][0]["timestamp"]
    tipo_texto=comienzo["messages"][0]["type"]

    if tipo_texto == "text":
        cuerpo=comienzo["messages"][0]["text"]["body"]
    elif tipo_texto == "image":
        cuerpo=[comienzo["messages"][0]["image"]["url"],comienzo["messages"][0]["image"]["id"]]
    else:
        cuerpo=None

    return n_Telefono,user_name,tipo_texto,cuerpo,timestamp

#No ponemos global variable por que no la modificamos
def foto_a_cloudflare(cuerpo,fecha):

    ruta_foto=cuerpo[0]
    id_foto=cuerpo[1]

    #Cambiar por ruta actual para fotos
    nombre_foto=f"facturas/factura_{fecha}_{id_foto}.jpg"
    preguntaFoto= requests.get(ruta_foto, headers={"Authorization": f"Bearer {token_permanente_meta}"})

    if preguntaFoto.status_code == 200:

        cloudflare.put_object(Bucket=nombre_bucket, Key=nombre_foto, Body=preguntaFoto.content, ContentType="image/jpeg")


def descargarFoto(cuerpo,fecha):

    ruta_foto=cuerpo[0]
    id_foto=cuerpo[1]
    
    #Cambiar por ruta actual para fotos
    rutaArchivos=f"factura_{id_foto}.jpg"
    preguntaFoto= requests.get(ruta_foto, headers={"Authorization": f"Bearer {token_permanente_meta}"})

    if preguntaFoto.status_code == 200:
        with open(rutaArchivos,"wb") as f:
            f.write(preguntaFoto.content)


def timestamp_a_Fecha(timestamp):
    fecha=datetime.fromtimestamp(int(timestamp)).date()
    return fecha

#No hace falta que se llame la funcion asi puede llamarse como se quiera solo que la ruta del decorador es donde se van a conectar
#por lo que si tiene que ser la ruta a la que vayan a enviar los mensajes la que se ponga en el decorador
@app.post("/webhook")
def webhook():

    global contador

    headers=request.headers
    data=request.data
    form=request.form
    args=request.args
    files=request.files

    json_exists=request.is_json

    print("headers",headers)
    print("data",data.decode())
    print("form",form)
    print("args:",args)

    if json_exists:
        json=request.get_json()
        print("json",json)

        n_Telefono,user_name,tipo_texto,cuerpo,timestamp=datos_Json(json)

        print("DATOS"*10,"   ",n_Telefono,"   ",user_name,"   ",tipo_texto,"   ",cuerpo,"   ",timestamp)

        if tipo_texto == "image":
            fecha=timestamp_a_Fecha(timestamp)
            foto_a_cloudflare(cuerpo,fecha)


    else:
        print("No hay json")
    
    print("file",files)


    print("*"*20,"   ",contador)
    contador+=1

    return "OK", 200

@app.get("/webhook")
def confirmarConexionWebhook():
    global contador
    global token_webhook
    print("Se ha llegado al get de webhook")

    print("headers",request.headers)
    print("+"*10,"  ",contador)
    contador+=1
    print("")
    args=request.args
    print("args:", args)

    token_meta=args.get("hub.verify_token")
    challenge= args.get("hub.challenge")

    if token_meta == token_webhook:
        return challenge, 200
    else:
        return "Token incorrecto script", 403

@app.get("/")
def inicio():
    print("se ha llegado al inicio")
    return "Inicio", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000)