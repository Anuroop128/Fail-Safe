from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import joblib
import shap
import io

app = FastAPI(title="FAILSAFE API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = joblib.load('../models/failsafe_xgb_model.pkl')
scaler = joblib.load('../models/failsafe_scaler.pkl')
expected_features = joblib.load('../models/model_features.pkl')
explainer = shap.TreeExplainer(model)

INTERVENTION_MAP = {
    'failures': "Mandate weekly peer-tutoring sessions.",
    'studytime': "Assign mandatory 'Time Management' seminar.",
    'absences': "Trigger automated academic advisor check-in.",
    'risk_behavior': "Schedule confidential wellness counseling.",
    'support_index': "Connect student with on-campus mentorship."
}

@app.post("/predict")
async def predict_risk(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files allowed.")
    
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode('utf-8')), sep=';')
    raw_df = df.copy()
    
    binary_cols = ['schoolsup', 'famsup', 'higher', 'internet']
    for col in binary_cols:
        if col in df.columns:
            df[col] = df[col].map({'yes': 1, 'no': 0}).fillna(0)
            
    df['support_index'] = df.get('schoolsup', 0) + df.get('famsup', 0) + df.get('higher', 0)
    df['risk_behavior'] = df.get('Dalc', 0) + df.get('Walc', 0) + df.get('goout', 0)
    
    df_encoded = pd.get_dummies(df)
    for col in expected_features:
        if col not in df_encoded.columns:
            df_encoded[col] = 0
            
    X_app = df_encoded[expected_features]
    X_scaled = pd.DataFrame(scaler.transform(X_app), columns=expected_features)
    
    
    probabilities = model.predict_proba(X_scaled)[:, 1]
    
    results = []
    for idx in range(len(probabilities)):
        prob = float(probabilities[idx])
        tier = "High" if prob >= 0.65 else "Medium" if prob >= 0.40 else "Low"
        
        shap_vals = explainer.shap_values(X_scaled.iloc[[idx]])[0]
        feature_impacts = [{"feature": expected_features[i], "impact": float(shap_vals[i])} 
                           for i in range(len(expected_features)) if shap_vals[i] > 0]
        
        top_drivers = sorted(feature_impacts, key=lambda x: x["impact"], reverse=True)[:3]
        
        interventions = [
            {"trigger": d["feature"], "action": INTERVENTION_MAP.get(d["feature"], "Discuss in 1-on-1")}
            for d in top_drivers
        ]
        
        results.append({
            "student_id": idx,
            "age": int(raw_df.iloc[idx].get('age', 0)),
            "absences": int(raw_df.iloc[idx].get('absences', 0)),
            "risk_probability": round(prob * 100, 1),
            "risk_tier": tier,
            "top_drivers": top_drivers,
            "interventions": interventions
        })
        
    return {"status": "success", "data": results}