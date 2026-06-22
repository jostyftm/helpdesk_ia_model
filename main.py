from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import numpy as np
import os
from typing import Optional

# ==========================================
# 1. CONFIGURACIÓN E INICIALIZACIÓN
# ==========================================
app = FastAPI(
    title="Service Desk Predictor AI",
    description="Microservicio predictivo para la probabilidad de cierre de tickets basado en el tiempo de resolución, sitio y grupo asignado.",
    version="1.0.0"
)

# Definir la ruta absoluta donde deben estar los archivos .pkl
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'modelo_helpdesk_rf.pkl')
SCALER_PATH = os.path.join(BASE_DIR, 'scaler_helpdesk.pkl')

# Variables globales para almacenar los artefactos de Machine Learning
modelo_ia = None
escalador = None

# Evento que se ejecuta al arrancar el servidor
@app.on_event("startup")
def cargar_artefactos():
    global modelo_ia, escalador
    try:
        # Cargamos el Random Forest y el StandardScaler en memoria RAM
        modelo_ia = joblib.load(MODEL_PATH)
        escalador = joblib.load(SCALER_PATH)
        print("✅ [SISTEMA] Artefactos de Machine Learning cargados exitosamente.")
    except FileNotFoundError:
        print("❌ [ERROR CRÍTICO] No se encontraron los archivos .pkl en el directorio base.")
    except Exception as e:
        print(f"❌ [ERROR CRÍTICO] Falla al cargar el modelo: {e}")

# ==========================================
# 2. DEFINICIÓN DE ESTRUCTURAS DE DATOS (DTOs)
# ==========================================
class TicketInput(BaseModel):
    # Field permite documentar y validar la entrada de datos en la API
    tiempo_resolucion_dias: float = Field(..., description="Días transcurridos desde la creación del ticket", example=2.5)
    sitio_cod: int = Field(..., description="Código numérico del sitio (Ej: AREA DE TECNOLOGIA = 1)", example=1)
    grupo_cod: int = Field(..., description="Código numérico del grupo de soporte (Ej: Area de Operaciones = 0)", example=0)

class PrediccionOutput(BaseModel):
    estado_estimado: str
    probabilidad_cierre: float
    advertencia: Optional[str] = None

# ==========================================
# 3. ENDPOINTS DE LA API
# ==========================================

# Endpoint de monitorización (Healthcheck)
@app.get("/", tags=["Sistema"])
def estado_servicio():
    if modelo_ia is None or escalador is None:
        raise HTTPException(status_code=503, detail="Servicio no disponible: Modelos ML no cargados.")
    return {"status": "En línea", "mensaje": "Motor de Inferencia de Helpdesk activo."}

# Endpoint principal de predicción
@app.post("/api/v1/predecir-estado", response_model=PrediccionOutput, tags=["Machine Learning"])
def predecir_ticket(ticket: TicketInput):
    if modelo_ia is None or escalador is None:
        raise HTTPException(status_code=503, detail="Motor predictivo no inicializado.")
    
    try:
        # A. Extraer los datos del JSON recibido y convertirlos en el formato matemático esperado
        # El orden DEBE ser exactamente el mismo que se usó en el entrenamiento (X_bal)
        datos_crudos = np.array([[
            ticket.tiempo_resolucion_dias,
            ticket.sitio_cod,
            ticket.grupo_cod
        ]])

        # B. Aplicar la regla de escalamiento (StandardScaler)
        datos_procesados = escalador.transform(datos_crudos)

        # C. Realizar la inferencia con el Random Forest
        clase_predicha = modelo_ia.predict(datos_procesados)[0]
        probabilidades = modelo_ia.predict_proba(datos_procesados)[0]

        # D. Lógica de negocio sobre la predicción (1 = Cerrado, 0 = Abierto)
        if clase_predicha == 1:
            estado = "Cerrado"
            confianza = float(probabilidades[1])
            alerta = None
        else:
            estado = "Abierto / Riesgo de Estancamiento"
            confianza = float(probabilidades[0])
            alerta = "El ticket presenta características que históricamente no conducen a un cierre inmediato. Revisar SLA."

        # Retornar la respuesta estructurada
        return PrediccionOutput(
            estado_estimado=estado,
            probabilidad_cierre=round(confianza, 4),
            advertencia=alerta
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la inferencia predictiva: {str(e)}")