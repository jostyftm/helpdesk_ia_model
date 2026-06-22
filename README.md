# Service Desk Predictor AI 🚀

Este repositorio contiene un microservicio de Inteligencia Artificial desarrollado con **FastAPI** y empoderado por un modelo de **Random Forest**. Su objetivo es predecir la probabilidad de cierre de tickets de soporte técnico (Mesa de Ayuda) basándose en el tiempo de resolución, el sitio y el grupo asignado.

Este proyecto forma parte del Taller 4 de Aprendizaje de Máquina Aplicado y está diseñado para ser desplegado de manera ágil utilizando contenedores Docker.

## 📂 Estructura del Proyecto

Asegúrate de que tu directorio contenga los siguientes archivos antes de iniciar el despliegue:

\`\`\`text
/
├── main.py                     # Código fuente de la API REST (FastAPI)
├── modelo_helpdesk_rf.pkl      # Modelo Random Forest serializado
├── scaler_helpdesk.pkl         # Escalador StandardScaler serializado
├── requirements.txt            # Dependencias de Python
├── Dockerfile                  # Instrucciones de construcción de la imagen
├── docker-compose.yml          # Orquestación del contenedor
└── README.md                   # Documentación del proyecto
\`\`\`

## ⚙️ Requisitos Previos

* [Docker](https://docs.docker.com/get-docker/) instalado en tu sistema.
* [Docker Compose](https://docs.docker.com/compose/install/) instalado (viene incluido en Docker Desktop).

## 🚀 Instalación y Despliegue

Gracias a la contenedorización, levantar este servicio no interfiere con tu entorno local y requiere un solo comando.

1. Abre tu terminal y navega hasta la carpeta del proyecto.
2. Construye y levanta el servicio en segundo plano (modo detached) ejecutando:

   \`\`\`bash
   docker-compose up -d --build
   \`\`\`

3. Para verificar que el contenedor se está ejecutando correctamente y que los modelos `.pkl` fueron cargados, revisa los logs del sistema:

   \`\`\`bash
   docker-compose logs -f
   \`\`\`

## 🌐 Uso y Pruebas de la API

Una vez que el contenedor esté en ejecución, el servidor Uvicorn estará escuchando en el puerto `8000`.

### Interfaz Interactiva (Swagger UI)
FastAPI genera automáticamente la documentación y una interfaz de pruebas. Abre tu navegador y dirígete a:
**👉 [http://localhost:8000/docs](http://localhost:8000/docs)**

Desde allí, puedes acceder al endpoint `POST /api/v1/predecir-estado`, hacer clic en *"Try it out"*, y enviar un payload JSON de prueba como el siguiente:

\`\`\`json
{
  "tiempo_resolucion_dias": 2.5,
  "sitio_cod": 1,
  "grupo_cod": 0
}
\`\`\`

#### --- DICCIONARIO PARA PROBAR TU API ---
Códigos de Sitio:
  0 -> AREA DE TECNOLOGIA
  1 -> Auditoria
  2 -> TECNOLOGIA

#### Códigos de Grupo:
  0 -> Area de Operaciones
  1 -> Area de Tecnologias
  2 -> Desconocido
  3 -> Logistica

El sistema responderá con el estado estimado y su respectiva probabilidad de cierre.

## 🛑 Detener el Servicio

Para apagar el microservicio y liberar el puerto, ejecuta:

\`\`\`bash
docker-compose down
\`\`\`