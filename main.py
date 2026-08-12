"""
Microservice FastAPI - Detection d'intrusion (SentinelCore SIEM)
Expose /health (keep-alive UptimeRobot) et /predict (inference ML)
"""

import os
import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional

# ============================================================
# Chargement du modele au demarrage (une seule fois)
# ============================================================
MODEL_DIR = os.path.join(os.path.dirname(__file__), "model_output")

model = joblib.load(os.path.join(MODEL_DIR, "rf_model.pkl"))
scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
label_encoder = joblib.load(os.path.join(MODEL_DIR, "label_encoder.pkl"))
feature_columns = joblib.load(os.path.join(MODEL_DIR, "feature_columns.pkl"))

app = FastAPI(title="SentinelCore ML API", version="1.0")

# Autorise ton frontend React a appeler cette API (ajuste l'origine en prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # A restreindre a ton domaine frontend en prod
    allow_methods=["*"],
    allow_headers=["*"],
)


class FlowInput(BaseModel):
    features: Dict[str, float]


class PredictionOutput(BaseModel):
    prediction: str
    confidence: float


# ============================================================
# /health - endpoint LEGER pour UptimeRobot (pas de calcul ML)
# ============================================================
@app.get("/health")
def health():
    return {"status": "ok"}


# ============================================================
# /predict - inference reelle du modele
# ============================================================
@app.post("/predict", response_model=PredictionOutput)
def predict(flow: FlowInput):
    row = pd.DataFrame([{col: flow.features.get(col, 0) for col in feature_columns}])
    X_scaled = scaler.transform(row)

    pred = model.predict(X_scaled)[0]
    proba = model.predict_proba(X_scaled)[0]

    label = label_encoder.inverse_transform([pred])[0]
    confidence = float(np.max(proba))

    return PredictionOutput(prediction=label, confidence=round(confidence, 4))


@app.get("/")
def root():
    return {"service": "SentinelCore ML API", "status": "running"}