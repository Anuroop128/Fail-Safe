import pandas as pd
import json
import os

# the Deterministic Guardrails
INTERVENTION_MAP = {
    'failures': "ACADEMIC: Student has prior failures. ACTION -> Mandate weekly peer-tutoring sessions.",
    'studytime': "HABIT: Low study time detected (<2 hrs/week). ACTION -> Assign mandatory 'Time Management & Study Skills' seminar.",
    'absences': "ATTENDANCE: High absence rate. ACTION -> Trigger automated academic advisor check-in and draft attendance contract.",
    'risk_behavior': "LIFESTYLE: High risk behavior index (Alcohol/Social). ACTION -> Schedule confidential wellness counseling.",
    'support_index': "SUPPORT: Low family/school support. ACTION -> Connect student with on-campus mentorship program.",
    'freetime': "HABIT: Excessive free time negatively impacting grades. ACTION -> Suggest structured extracurriculars or library hours.",
    'goout': "LIFESTYLE: High frequency of going out. ACTION -> Advisor discussion on work-life balance."
}

def generate_intervention_plan(student_id, top_risk_drivers_df):
    """Ingests SHAP risk drivers and outputs a deterministic intervention plan."""
    plan = {
        "student_id": student_id,
        "interventions": []
    }
    
    print(f"-- INTERVENTION PLAN FOR STUDENT {student_id}--")
    
    for index, row in top_risk_drivers_df.iterrows():
        feature = row['Feature']
        impact = row['SHAP_Impact']
        raw_value = row['Actual_Raw_Value']
        
        if feature in INTERVENTION_MAP:
            action = INTERVENTION_MAP[feature]
            plan["interventions"].append({
                "feature": feature,
                "action": action
            })
            print(f"🔴 [Trigger: {feature} | SHAP Impact: +{impact:.2f}]")
            print(f"   ↳ {action}\n")
        else:
            # Fallback guardrail for features without specific mappings
            print(f"🟡 [Trigger: {feature} | SHAP Impact: +{impact:.2f}]")
            print(f"   ↳ GENERAL: Discuss impact of '{feature}' during next advising session.\n")
            
    return plan

student_plan = generate_intervention_plan(student_id=student_idx, top_risk_drivers_df=top_risk_drivers)


