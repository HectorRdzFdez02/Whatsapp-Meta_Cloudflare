from flask import Flask, request

app = Flask(__name__)
contador=0

#No hace falta que se llame la funcion asi puede llamarse como se quiera solo que la ruta del decorador es donde se van a conectar
#por lo que si tiene que ser la ruta a la que vayan a enviar los mensajes la que se ponga en el decorador
@app.post("/webhook")
def webhook():
    print("headers",request.headers)
    print("data",request.data.decode())
    print("form",request.form)
    print("args:", request.args)
    if request.is_json:
        print("json",request.get_json())
    else:
        print("No hay json")
    
    print("file",request.files)
    print("*"*20)
    return "OK", 200

@app.get("/webhook")
def confirmarConexionWebhook():
    global contador
    print("Se ha llegado al get de webhook")

    print("headers",request.headers)
    print("+"*10,"  ",contador)
    contador+=1
    print("")
    print("args:", request.args)


    return "Webhook listo para acceder", 200

@app.get("/")
def inicio():
    print("se ha llegado al inicio")
    return "Inicio", 200

app.run(host="0.0.0.0",port=5000)