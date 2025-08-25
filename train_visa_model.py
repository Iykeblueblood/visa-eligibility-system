# train_visa_model.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
from visa_rules_engine import SKILLED_WORKER_RULES, evaluate_applicant # Use the new engine

print("Loading data...")
df = pd.read_csv("visa_mock_data.csv")

# --- Define the exact feature set and order ---
FEATURE_ORDER = [
    'total_points', 'num_mandatory_failures', 'num_warning_flags',
    'points_age', 'points_education', 'points_language', 'points_work', 'points_bonus'
]

# --- Feature Engineering using the Rule Engine ---
print("Applying rules engine to generate features...")
features = []
for index, row in df.iterrows():
    applicant_dict = row.to_dict()
    # Use the new universal evaluator with the correct rule set
    rule_engine_output = evaluate_applicant(applicant_dict, SKILLED_WORKER_RULES)
    
    # Create features from the engine's output
    features.append({
        'total_points': rule_engine_output['total_points'],
        'num_mandatory_failures': len(rule_engine_output['mandatory_failures']),
        'num_warning_flags': len(rule_engine_output['warning_flags']),
        'points_age': rule_engine_output['points_per_category'].get('Age', 0),
        'points_education': rule_engine_output['points_per_category'].get('Education', 0),
        'points_language': rule_engine_output['points_per_category'].get('Language', 0),
        'points_work': rule_engine_output['points_per_category'].get('Work Experience', 0),
        'points_bonus': rule_engine_output['points_per_category'].get('Bonus', 0),
    })

df_features = pd.DataFrame(features)
print("Feature generation complete.")

# --- Model Training ---
# Enforce the feature order before splitting
X = df_features[FEATURE_ORDER]
y = df['is_eligible']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

print("Training RandomForestClassifier model...")
model = RandomForestClassifier(n_estimators=150, random_state=42, class_weight='balanced', max_depth=10)
model.fit(X_train, y_train)

# --- Evaluate and Save ---
print("Model evaluation:")
predictions = model.predict(X_test)
print(classification_report(y_test, predictions))

joblib.dump(model, 'visa_model.joblib')
print("Model retrained with enforced feature order and saved to visa_model.joblib")