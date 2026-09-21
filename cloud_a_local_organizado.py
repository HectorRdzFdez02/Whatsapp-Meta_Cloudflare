import boto3
import os
from dotenv import load_dotenv

load_dotenv()

#Rutas carpetas
ruta_base=os.getenv("RUTA_BASE")
ruta_Descargado=ruta_base+os.getenv("RUTA_DESCARGADO")
ruta_Fotos_Raw=ruta_base+os.getenv("RUTA_FOTOS_RAW")
ruta_Cloudflare=os.getenv("RUTA_CLOUDFLARE")

#Cloudflare
endpoint_almacenamiento=os.getenv("ENDPOINT_ALMACENAMIENTO")
nombre_bucket=os.getenv("NOMBRE_BUCKET")
access_key=os.getenv("ACCESS_KEY")
secret_access_key=os.getenv("SECRET_ACCESS_KEY")


#objeto cloudflare
#parametro 1 = tipo de servidor, parametro 2 = ruta servidor de almacenamiento, parametro 3 = usuario, parametro 4 = contrasenia, parametro 5 = region servidor
cloudflare= boto3.client("s3", endpoint_url=endpoint_almacenamiento, aws_access_key_id=access_key, aws_secret_access_key=secret_access_key, region_name="auto")

fotos_cloudflare=cloudflare.list_objects_v2(Bucket=nombre_bucket, Prefix=ruta_Cloudflare)

print(fotos_cloudflare)
print(len(fotos_cloudflare))

lista_fotos=[]

for i in fotos_cloudflare["Contents"]:
    print(i["Key"])
    nombre_archivo=str(i["Key"]).split("/")[1]
    lista_fotos.append(nombre_archivo)

lista_fotos.pop(0)
print(lista_fotos)

if lista_fotos:
    for i in lista_fotos:
        datos_fotos=i.split("_")

        nTelefono=datos_fotos[1]
        fecha_fotos=datos_fotos[2]
        #Le quito el dia para obtener el año y el mes que quiero guardar
        fecha_fotos=fecha_fotos[:len(fecha_fotos)-3]
        print(nTelefono,fecha_fotos)

        #Comprobamos que exista la carpeta a la que vamos a mandar las fotos si no existe se crea
        ruta_organizada=os.path.join(ruta_Descargado,nTelefono,fecha_fotos,ruta_Fotos_Raw)
        os.makedirs(ruta_organizada, exist_ok=True)


        #Descarga la foto
        cloudflare.download_file(nombre_bucket,ruta_Cloudflare+i,os.path.join(ruta_organizada,i))

    for i in lista_fotos:
        print("nombre_bucket,ruta_Cloudflare+i")
        cloudflare.delete_object(Bucket=nombre_bucket,Key=ruta_Cloudflare+i)

else:
    print("No hay fotos nuevas")