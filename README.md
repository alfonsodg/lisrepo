#Plataforma de Indexación de Laboratorio Clínico


##Descripción
Es una aplicación que permite la indexación centralizada de la metadata de los resultados de laboratorios, permitiendo ubicar el origen y flujo de los diversos análisis así como facilitar su visualización y comparación. Provee servicios REST para el registro de los datos, así como la consulta de atenciones por DOC_ID y/o nombre del paciente, la misma que es entregada en formato json.


##FIHR
Es un framework del estándar HL7 para una rápida integración de sistemas clínicos, para mayores referencias digirse a [FIHR](https://www.hl7.org/fhir/)


##LOINC
Es un estándar internacional para clasificar las observaciones clínicas en medicina, para mayores referencias dirigirse a [LOINC](https://loinc.org/)


##Arquitectura
* Núcleo
    * Python 2.7 o superior
    * MongoDB 3.0 o superior

* Librerías Python
    * Tornado Web Server 4.5 o superior
    * PyMongo 3.5 o superior


##Base de Datos
El motor de persistencia empleado para este micro servicio es MongoDB, por lo tanto las estructuras de datos son no relacionales.  El diseño de la aplicación permite mejorar la estructura de datos cambiando simplemente el formato de entrada (revisar Formato JSON para Insert), la misma que es recibida por el indexador y enviada directamente al motor MongoDB (sin modificar su contenido).
Adicionalmente, para proveer una búsqueda rápida de datos, el indexador define a su inicio los índices que debe emplear la base de datos, los mismos que son establecidos en **config.json**.


##Estructura de la aplicación (árbol de archivos)
```
imaging_heading -> Directorio Raiz
    server.py -> Servicio
    requirements.txt -> Archivo dependencias Python
    README.md -> Este documento (Guia uso / desarrollador)
    config.json -> Archivo de configuración
    static -> Directorio de archivos estáticos
    templates -> Directorio de plantillas html según URL
    tests -> Directorio con pruebas de la aplicación
        get_data.py -> Prueba funcional de conexión con server
        lab_v1.json -> Archivo json ejemplo con metadata de estudio basado en Fire
    extras -> Directorio con archivos adicionales importantes
        lis.service -> servicio listo para copiar en /etc/systemd/system
    lis_routes.log -> Log generado automáticamente por el servicio, no es versionable
```


##Instalación

###Copiar / clonar el directorio /srv
```
git clone https://alfonsodg@bitbucket.org/controlradiologico/lisrepo.git
```

###Verificar que se tenga instalado la arquitectura base (python y mongodb)

###Instalar ENV
```
virtualenv venv
```

###Activar ENV
```
source venv/bin/activate
```

###Instalar requerimientos de la aplicación contenidos en requirements.txt
```
pip install -r requirements.txt
```
###Modificar config.json a discreción o dejarlo tal como está para instalación por defecto

###Ejecutar server.py
```
python server.py
```

###Comprobar el acceso al servicio, por ejemplo
```
http://localhost:8888/** (cambiar el localhost por el ip correspondiente)
```


##Inicio Automático
Se ha incluído un servicio en extras/lis.service

    /etc/systemd/system/lis.service   
```
[Unit]
Description = Imaging Service
After = network.target

[Service]
WorkingDirectory = /srv/lisrepo
ExecStart = /srv/lisrepo/server.py

[Install]
WantedBy = multi-user.target
```
Una vez creado el archivo activar el servicio de inmediato y al inicio
```
systemctl start lis.service
systemctl enable lis.service
```


##Peticiones Webservices

###Método Post
* /api/v1/register

    Inserta data json de atención (el formato ejemplo está contenido dentro de tests/lab_v1.json o revisar titulo **Formato JSON para INSERT (POST)**)

###Método Get

* /api/v1/work_order/(CODIGO)

    Busca y devuelve resultado por código de orden de laboratorio

* /api/v1/patient/(DOC_ID)

    Busca y devuelve resultados por DOC_ID

* /api/v1/patient_alternate/(DOC_ID)

    Busca y devuelve resultados por código BDUP o algún código definido en subject.reference_alternate del archivo json original

* /api/v1/provider/(DOC_ID)

    Busca y devuelve resultados por DOC_ID de proveedor

###Respuestas:

* {'status':'Error'}

    Error en los parámetros de consulta del webservice, revisar los mismos

* {'status': 'Ok'}
    Dato recibido y guardado (solo para POST)

* [{ {metadata} }]

    Conjunto (lista) de datos resultantes de la consulta y cuya estructura es igual al formato de insert json más {'_id':CODIGO UNICO}


##Seguridad
Para poder llamar a las peticiones se requiere que en la cabecera se incluya **X-Api-Key** con la llave proporcionada por el área pertinente.  Las llaves de seguridad deben ser escritas dentro del archivo **config.json**
```
{'X-Api-Key' : '5954032458e83fc75abf23afd1c01ce3'}
```

##Tests
No olvidar que en la cabecera se debe agregar **X-Api-Key** con la llave correspondiente

###Consultas (URLs)
* http://localhost:8888/api/v1/work_oder/1234
* http://localhost:8888/api/v1/patient/26267267-K
* http://localhost:8888/api/v1/patient_alternate/272827873AA
* http://localhost:8888/api/v1/provider/123456-1

###Insertar Registros
```
curl -d "@lab_v1.json" -H "Content-Type: application/json" -H "X-Api-Key:5954032458e83fc75abf23afd1c01ce3" -X POST http://IP:8888/api/v1/result
```


##Estructura de Datos

###Formato JSON para INSERT (POST)
Debido a la complejidad del mismo, el formato debe definirse en documento previo generado por las áreas competentes considerando [FIHR](https://www.hl7.org/fhir/) como estándar de interoperabilidad.  El documento desarrollado debe incluir los nomencladores respectivos para los analitos siguiendo [LOINC](https://loinc.org/). Ejemplo:
```
    {
      "resourceType": "Observation",
      "id": "5284-lab",
      "meta": {
        "versionId": "1",
        "lastUpdated": "2017-09-22T15:29:57.327+00:00"
      },
      "text": {
        "status": "generated",
        "div": "<div>2005-07-05: Creat SerPl-mCnc = 1 mg/dL</div>"
      },
      "status": "final",
      "category": {
        "coding": [
          {
            "system": "http://hl7.org/fhir/observation-category",
            "code": "laboratory",
            "display": "Laboratorio"
          }
        ],
        "text": "Laboratorio"
      },
      "code": {
        "coding": [
          {
            "system": "http://loinc.org",
            "code": "2160-0",
            "display": "Creat SerPl-mCnc"
          },
          {
            "system": "maestroDePrestaciones",
            "id_kp": "5284",
            "display": "CREATININA EN SANGRE"
          }
        ],
        "text": "Creat SerPl-mCnc"
      },
      "subject": {
        "reference": "Patient/142552",
        "reference_alternate": "3738883-5",
        "name": ""
      },
      "effectiveDateTime": "2005-07-05",
      "valueQuantity": {
        "value": 1.0,
        "unit": "mg/dL",
        "system": "http://unitsofmeasure.org",
        "observation": ""
      },
      "referenceRange": [
        {
          "low": {
            "value": 0.2,
            "unit": "mg/dL",
            "system": "http://unitsofmeasure.org",
            "code": "mg/dL"
          },
          "high": {
            "value": 0.6,
            "unit": "mg/dL",
            "system": "http://unitsofmeasure.org",
            "code": "mg/dL"
          },
          "meaning": {
            "coding": [
              {
                "system": "http://hl7.org/fhir/referencerange-meaning",
                "code": "normal",
                "display": "Rango Normal"
              }
            ],
            "text": "Rango Normal"
          }
        }
      ],
      "requestDetail": {
        "requestNumber": "77783",
        "requestDatetime": "2017-01-01 21:00:00",
        "requestReferrer": "2627727-3",
        "providerId": "11111-8"
      },
      "reportDetail": {
        "reportNumber": "77783",
        "areaLaboratory": "1",
        "equipmentId": "23",
        "processDatetime": "2017-01-01 22:00:00",
        "validationDatetime": "2017-01-01 23:00:00",
        "reportSigner": "15260200-6",
        "providerId": "11111-8"
      }
    }
```

###FORMATO JSON para GET
Es el mismo que para INSERT en un arreglo (lista) de los mismos más el campo: {'_id':NUMERO AUTOGENERADO} en cada atención
```
    [
    {RESULTADO 1},
    {RESULTADO 2}.
    ...
    ]
```


##Configuración
Está contenido dentro del archivo **config.json**
```
    {
      "database": {  -> Información BD mongo
        "host": "IP o nombre del servidor",
        "port": "Puerto",
        "user": "Nombre de usuario",
        "password": "Clave de usuario",
        "name": "Nombre de las base de datos"
      },
      "indexes": {  -> Indices a crear según estructura JSON)
        "id": true,
        "subject.reference": true,
        "subject.reference_alternate": true,
        "reportDetail.reportNumber": true,
        "reportNumber.providerId": true
      },
      "application": {  -> Puerto de la aplicación
        "port": 8888
      },
      "keys": [  -> Llaves de autentificación
        "5954032458e83fc75abf23afd1c01ce1",
        "5954032458e83fc75abf23afd1c01ce2"
      ],
      "log_file_base": "lisrepo.log"  --> Nombre base de log para rotar
    }
```


##Licencia
Este software es entregado bajo licencia GPL v3, excepto en las librerías que no sean compatibles con esta licencia.  Revisar el archivo **gplv3.md
** para los detalles y alcances del mismo
