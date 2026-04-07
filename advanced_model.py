import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load dataset
data = pd.read_csv("dataset.csv")

# Show columns
print("Columns:", data.columns)

# -------------------------------
# STEP 1: Convert symptoms properly
# -------------------------------

# Get all unique symptoms
symptoms = set()
for col in data.columns[1:]:
    symptoms.update(data[col].dropna().unique())

symptoms = list(symptoms)

# Create new binary feature dataframe
X = pd.DataFrame(0, index=data.index, columns=symptoms)

# Fill 1 where symptom exists
for i in range(len(data)):
    for col in data.columns[1:]:
        symptom = data.iloc[i][col]
        if pd.notna(symptom):
            X.loc[i, symptom] = 1

# Target column
y = data["Disease"]

# -------------------------------
# STEP 2: Train-Test Split
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -------------------------------
# STEP 3: Train Model
# -------------------------------
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# -------------------------------
# STEP 4: Accuracy
# -------------------------------
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("Model Accuracy:", accuracy * 100)

# -------------------------------
# STEP 5: Prediction Function
# -------------------------------
def predict_disease(input_symptoms):
    # Create input dataframe
    input_data = pd.DataFrame(0, index=[0], columns=symptoms)

    # Mark symptoms as 1
    for symptom in input_symptoms:
        if symptom in input_data.columns:
            input_data[symptom] = 1

    # Prediction
    prediction = model.predict(input_data)[0]
    probabilities = model.predict_proba(input_data)[0]

    # Top 3 predictions
    top3 = sorted(
        zip(model.classes_, probabilities),
        key=lambda x: x[1],
        reverse=True
    )[:3]

    return prediction, top3


# -------------------------------
# STEP 6: Example Test
# -------------------------------
if __name__ == "__main__":
    test_symptoms = ["itching", "skin_rash"]  # example
    disease, top3 = predict_disease(test_symptoms)

    print("Predicted Disease:", disease)
    print("Top 3 Predictions:", top3)