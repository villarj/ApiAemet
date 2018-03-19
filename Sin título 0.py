#Importamos todas las librerias que vamos a utilizar
import http.client
import ssl
import json
import csv
#import urllib

#Para que no tengamos problemas con los certificados.
ssl._create_default_https_context = ssl._create_unverified_context

#Definimos la key para conectarse a la api de aemet
key='eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ2aWxsYXJyakB1bmljYW4uZXMiLCJqdGkiOiJkZDc5ZjVmNy1hODQwLTRiYWQtYmMzZi1jNjI3Y2ZkYmUxNmYiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTUyMDg0NzgyOSwidXNlcklkIjoiZGQ3OWY1ZjctYTg0MC00YmFkLWJjM2YtYzYyN2NmZGJlMTZmIiwicm9sZSI6IiJ9.LMl_cKCtYi3RPwLwO7fJYZMes-bdMVR91lRFZbUSv84'

#Creamos la conexión con la web de opendata para que este disponible en todas las funciones.
conn = http.client.HTTPSConnection("opendata.aemet.es")
#Definimos la cabecera de la web
headers = {'cache-control': "no-cache" }

#Obtenemos todas las características de todas las estaciones climatológicas
conn.request("GET", "/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones/?api_key="+key, headers=headers)

res = conn.getresponse()
data = res.read().decode('utf-8')

#Transformamos los datos a formato json
data = json.loads(data)

#print(data)



conn.request("GET", data['datos'], headers=headers)
res= conn.getresponse()
datos = res.read().decode('utf-8','ignore')
datos= json.loads(datos)
#print(datos)

estacionAeropuerto=0

estacionesCantabria=[]

for estacion in datos:
    if(estacion['nombre']=='SANTANDER AEROPUERTO'): 
        estacionAeropuerto=estacion
        #print(estacion)
    if(estacion['provincia']=='CANTABRIA'): 
        estacionesCantabria.append(estacion)
#Obtenemos el indicativo de la estacion
print(estacionAeropuerto['indicativo'])

#print(estacionesCantabria)
#Creamos una función que nos devuelva las estaciones que queremos
def buscarEstacion(nombreProvincia):
    estacionesCantabria=[]
    for estacion in datos:
        if(estacion['provincia']==nombreProvincia): 
            estacionesCantabria.append(estacion)
    return estacionesCantabria

print(buscarEstacion("CANTABRIA"))



#Ahora que tenemos el indicativo vamos a consultar para esa estacion
#GET /api/valores/climatologicos/diarios/datos/fechaini/{fechaIniStr}/fechafin/{fechaFinStr}/estacion/{idema}
fechaI="2018-01-01T00%3A00%3A00UTC"
fechaF="2018-01-31T00%3A00%3A00UTC"


conn.request("GET", "/opendata/api/valores/climatologicos/diarios/datos/fechaini/"+fechaI+"/fechafin/"+fechaF+"/estacion/"+estacionAeropuerto['indicativo']+"/?api_key=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ2aWxsYXJyakB1bmljYW4uZXMiLCJqdGkiOiJkZDc5ZjVmNy1hODQwLTRiYWQtYmMzZi1jNjI3Y2ZkYmUxNmYiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTUyMDg0NzgyOSwidXNlcklkIjoiZGQ3OWY1ZjctYTg0MC00YmFkLWJjM2YtYzYyN2NmZGJlMTZmIiwicm9sZSI6IiJ9.LMl_cKCtYi3RPwLwO7fJYZMes-bdMVR91lRFZbUSv84", headers=headers)

res = conn.getresponse()
dataSantander = res.read().decode('utf-8')


dataSantander = json.loads(dataSantander)

conn.request("GET", dataSantander['datos'], headers=headers)
res= conn.getresponse()
datosSantander = res.read().decode('utf-8','ignore')
datosSantander= json.loads(datosSantander)

#Vemos los resultados.
#for resultados in datosSantander:
#    print(resultados['fecha'],":",resultados['tmed'],"C")
 
with open('prueba.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(["Fecha","Tmed"])
    
    for resultados in datosSantander:
        print(resultados['fecha'],":",resultados['tmed'],"C")
        spamwriter.writerow([resultados['fecha'], resultados['tmed']])




#Para crear metadatos.
import xml.etree.cElementTree as ET




#Creamos un archivo de metadatos asociado al archivo anterior

#<eml:eml packageId="Javi.8.1" system="knb" xmlns:eml="eml://ecoinformatics.org/eml-2.1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="eml://ecoinformatics.org/eml-2.1.1 eml.xsd"> 
eml = ET.Element("eml:eml",system="knb",xmlns="eml://ecoinformatics.org/eml-2.1.1")

acceso = ET.SubElement(eml, "access", authSystem="knb", order="allowFirst")
permiso=ET.SubElement(acceso,"allow")
ET.SubElement(permiso,"principal").text="público"
ET.SubElement(permiso,"permission").text="lectura"
#Creamos otro hijo de eml
dataset=ET.SubElement(eml,"dataset")
ET.SubElement(dataset,"title").text="Datos de temperatura media en enero"
coverage=ET.SubElement(dataset,"coverage")
coverageG=ET.SubElement(coverage,"geographicCoverage")
ET.SubElement(coverageG,"geographicDescription").text="Santander"
ET.SubElement(coverageG,"latitud").text=estacionAeropuerto['latitud']
ET.SubElement(coverageG,"longitud").text=estacionAeropuerto['longitud']
ET.SubElement(coverageG,"altitud").text=estacionAeropuerto['altitud']
coverageT=ET.SubElement(coverage,"temporalCoverage")
ET.SubElement(coverageT,"FechaComienzo").text=datosSantander[0]['fecha']
ET.SubElement(coverageT,"FechaComienzo").text=datosSantander[30]['fecha']
tablaDatos=ET.SubElement(dataset,"dataTable")
ET.SubElement(tablaDatos,"NombreArchivo").text="prueba1.csv"
atributoLista=ET.SubElement(tablaDatos,"attributeList")
atributoFecha=ET.SubElement(atributoLista,"attribute",id="Fecha")
ET.SubElement(atributoFecha,"name").text="Fecha"
ET.SubElement(atributoFecha,"formatString").text="YYYY-MM-DD"
atributoTemp=ET.SubElement(atributoLista,"attribute",id="Temperatura")
ET.SubElement(atributoTemp,"name").text="Temperatura"
ET.SubElement(atributoTemp,"Unidadades").text="ºC"

#ET.SubElement(doc, "field1", name="blah").text = "some value1"
#field1=ET.SubElement(doc,"field1")
#ET.SubElement(field1,"pppp").text="Valorcetee"
#ET.SubElement(doc, "field2", name="asdfasd").text = "some vlaue2"



tree = ET.ElementTree(eml)

#Escribimos los datos en un archivo
tree.write("filename.xml",encoding='UTF-8', xml_declaration=True)
print(tree)

print("Final")