from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import joblib
import pandas as pd
from pydantic import BaseModel
import os

app = FastAPI(title="Inventory Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    product_id: str = "DRG001"
    category: str
    supplier_tier: str
    daily_sales_avg: float
    sales_std_dev: float
    current_stock: float
    lead_time_days: int
    reorder_point: float
    supplier_reliability: float
    seasonality_factor: float

@app.get("/")
def read_root():
    return {"message": "Welcome to the Real-Time Drug Demand & Stockout Predictor API."}

@app.post("/predict")
def predict_stockout(data: ItemInput):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded on the server.")
        
    input_df = pd.DataFrame([data.model_dump()])
    
    # Drop product_id before passing to model since it wasn't used in training
    if "product_id" in input_df.columns:
        input_df = input_df.drop(columns=["product_id"])
    
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
