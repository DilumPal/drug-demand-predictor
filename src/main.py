from fastapi import FastAPI, HTTPException
import joblib
import pandas as pd
from pydantic import BaseModel
import os

app = FastAPI(title="Inventory Prediction API")

MODEL_PATH = "models/stockout_model.pkl"

# Load model at startup
try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
    else:
        model = None
        print(f"Warning: Model not found at {MODEL_PATH}")
except Exception as e:
    model = None
    print(f"Error loading model: {e}")

class ItemInput(BaseModel):
    daily_sales_avg: float
    current_stock: float
    lead_time_days: int
    category: str
    supplier_tier: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the Real-Time Drug Demand & Stockout Predictor API. Send a POST request to /predict to get predictions."}

@app.post("/predict")
def predict_stockout(data: ItemInput):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded on the server.")
        
    input_df = pd.DataFrame([data.model_dump()])
    
    try:
        prediction = model.predict(input_df)[0]
        probability = model.predict_proba(input_df)[0][1]

        return {
            "out_of_stock_risk": bool(prediction),
            "risk_probability": round(float(probability), 4),
            "recommendation": (
                "Reorder immediately"
                if probability > 0.65
                else "Stock levels healthy"
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
