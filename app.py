import streamlit as st
import pandas as pd
from advanced_model import predict_disease
from rapidfuzz import process

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="AI Medical Checker", page_icon="🩺", layout="wide")

# -------------------------------
# PREMIUM CSS
# -------------------------------
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}

/* Titles */
h1 {
    text-align: center;
    color: #00f5d4;
}
h2, h3 {
    text-align: center;
    color: #a8dadc;
}

/* Button */
.stButton>button {
    background: linear-gradient(90deg, #00f5d4, #00bbf9);
    color: black;
    border-radius: 12px;
    height: 3em;
    width: 100%;
    font-size: 18px;
    font-weight: bold;
}

/* Input */
.stTextInput>div>div>input {
    background-color: #1e1e1e;
    color: white;
    border-radius: 10px;
}

/* Card UI */
.card {
    background: rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 15px;
    margin: 15px 0;
    text-align: center;
    box-shadow: 0px 0px 15px rgba(0,0,0,0.3);
}

</style>
""", unsafe_allow_html=True)

# -------------------------------
# TITLE
# -------------------------------
st.markdown("<h1>🩺 AI Medical Symptom Checker</h1>", unsafe_allow_html=True)
st.markdown("<h3>Smart Disease Prediction System</h3>", unsafe_allow_html=True)

# -------------------------------
# LOAD DATA
# -------------------------------
data = pd.read_csv("dataset.csv")
desc = pd.read_csv("symptom_Description.csv")
prec = pd.read_csv("symptom_precaution.csv")
severity_df = pd.read_csv("Symptom-severity.csv")

# -------------------------------
# EXTRACT SYMPTOMS
# -------------------------------
symptoms = set()
for col in data.columns[1:]:
    symptoms.update(data[col].dropna().unique())

symptom_list = sorted(list(symptoms))

# -------------------------------
# SEVERITY FUNCTION
# -------------------------------
def get_severity(symptoms):
    score = 0
    details = []

    for s in symptoms:
        val = severity_df[severity_df['Symptom'] == s]['weight'].values
        if len(val) > 0:
            weight = int(val[0])
            score += weight
            details.append((s, weight))

    return score, details

# -------------------------------
# INPUT TABS
# -------------------------------
tab1, tab2 = st.tabs(["🧾 Select Symptoms", "✍️ Enter Symptoms"])

selected_symptoms = []

# -------------------------------
# CHECKBOX UI
# -------------------------------
with tab1:
    col1, col2, col3 = st.columns(3)

    for i, symptom in enumerate(symptom_list):
        if i % 3 == 0:
            if col1.checkbox(symptom):
                selected_symptoms.append(symptom)
        elif i % 3 == 1:
            if col2.checkbox(symptom):
                selected_symptoms.append(symptom)
        else:
            if col3.checkbox(symptom):
                selected_symptoms.append(symptom)

# -------------------------------
# TEXT INPUT
# -------------------------------
with tab2:
    user_input = st.text_input("Enter symptoms (comma separated)")
    st.caption("Example: fever, headache, vomiting")

    if user_input:
        input_symptoms = [s.strip().lower().replace(" ", "_") for s in user_input.split(",")]

        for inp in input_symptoms:
            match = process.extractOne(inp, symptom_list)
            if match and match[1] > 70:
                selected_symptoms.append(match[0])

# -------------------------------
# CENTER BUTTON
# -------------------------------
st.write("")
col1, col2, col3 = st.columns([1,1,1])

with col2:
    predict = st.button("🔍 Predict Disease", use_container_width=True)

# -------------------------------
# PREDICTION
# -------------------------------
if predict:

    selected_symptoms = list(set(selected_symptoms))

    if len(selected_symptoms) < 2:
        st.warning("⚠️ Please provide at least 2 symptoms")
    else:
        disease, top3 = predict_disease(selected_symptoms)

        # -------------------------------
        # MAIN RESULT CARD
        # -------------------------------
        st.markdown(f"""
        <div class="card">
            <h2>🧠 Most Likely Disease</h2>
            <h1>{disease}</h1>
        </div>
        """, unsafe_allow_html=True)

        # -------------------------------
        # SEVERITY CARD
        # -------------------------------
        score, details = get_severity(selected_symptoms)

        severity_html = ""
        for s, w in details:
            if w >= 5:
                severity_html += f"🔴 <b>{s}</b> (High)<br>"
            elif w >= 3:
                severity_html += f"🟡 <b>{s}</b> (Medium)<br>"
            else:
                severity_html += f"🟢 <b>{s}</b> (Low)<br>"

        st.markdown(f"""
        <div class="card">
            <h3>📊 Symptom Severity</h3>
            {severity_html}
            <br><b>Total Score:</b> {score}
        </div>
        """, unsafe_allow_html=True)

        # -------------------------------
        # DESCRIPTION CARD
        # -------------------------------
        try:
            d = desc[desc['Disease'] == disease]['Description'].values[0]
        except:
            d = "Not available"

        st.markdown(f"""
        <div class="card">
            <h3>📖 Description</h3>
            {d}
        </div>
        """, unsafe_allow_html=True)

        # -------------------------------
        # PRECAUTIONS CARD
        # -------------------------------
        try:
            p = prec[prec['Disease'] == disease].values[0][1:]
            precaution_html = "<br>".join([f"👉 {i}" for i in p])
        except:
            precaution_html = "Not available"

        st.markdown(f"""
        <div class="card">
            <h3>🛡️ Precautions</h3>
            {precaution_html}
        </div>
        """, unsafe_allow_html=True)

        # -------------------------------
        # TOP 3 CARD
        # -------------------------------
        top_html = "<br>".join([f"{d} → {round(p*100,2)}%" for d, p in top3])

        st.markdown(f"""
        <div class="card">
            <h3>📊 Other Possible Diseases</h3>
            {top_html}
        </div>
        """, unsafe_allow_html=True)

        # -------------------------------
        # SYMPTOMS CARD
        # -------------------------------
        st.markdown(f"""
        <div class="card">
            <h3>✅ Interpreted Symptoms</h3>
            {", ".join(selected_symptoms)}
        </div>
        """, unsafe_allow_html=True)

        # -------------------------------
        # WARNING
        # -------------------------------
        st.warning("⚠️ This is not a medical diagnosis. Please consult a doctor.")

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")

st.markdown("<center>⚡ AI Final Year Project | Built with Streamlit</center>", unsafe_allow_html=True)
