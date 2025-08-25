# app.py
import streamlit as st
import pandas as pd
import joblib
from visa_rules_engine import (
    SKILLED_WORKER_RULES, 
    STUDENT_VISA_RULES, 
    TOURIST_VISA_RULES,
    evaluate_applicant
)
import plotly.graph_objects as go
import google.generativeai as genai

# --- Page Config ---
st.set_page_config(page_title="Intelligent Visa Eligibility System", layout="wide", page_icon="🛂")

# --- Define the feature order - MUST MATCH train_visa_model.py ---
FEATURE_ORDER = [
    'total_points', 'num_mandatory_failures', 'num_warning_flags',
    'points_age', 'points_education', 'points_language', 'points_work', 'points_bonus'
]

# --- API & Model Loading ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key); gemini_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception:
    st.warning("Google API Key not found. Generative AI analysis is disabled."); gemini_model = None
try:
    model = joblib.load('visa_model.joblib')
except Exception:
    st.warning("ML model not found. The 'Skilled Worker' category will run on rules only."); model = None

# --- Generative AI Function (Corrected with the critical fix) ---
def get_gemini_analysis(visa_category, applicant_data, rule_output, final_status, ml_prob=None):
    if not gemini_model: return "Generative AI analysis is disabled."

    profile_details, assessment_results = "", ""

    if visa_category == "Skilled Worker":
        profile_details = f"- Age: {applicant_data.get('age', 'N/A')}\n- Education: {applicant_data.get('education_level', 'N/A')}\n- Skilled Work Experience: {applicant_data.get('work_experience_years', 'N/A')} years\n- Occupation Demand: {applicant_data.get('occupation_demand_level', 'N/A')}\n- Settlement Funds: ${applicant_data.get('settlement_funds', 0):,.0f} for a family of {applicant_data.get('family_size', 1)}"
        
        # --- THIS IS THE FIX ---
        # 1. Create the formatted string for the ML probability first.
        ml_prob_text = f"{ml_prob:.2%}" if ml_prob is not None else "N/A"
        # 2. Use the simple text variable in the final f-string.
        assessment_results = f"- Final System Status: {final_status}\n- Rule-Based Points Score: {rule_output.get('total_points', 0)}\n- ML Model Probability: {ml_prob_text}"

    elif visa_category == "Student Visa":
        profile_details = f"- Academic GPA: {applicant_data.get('gpa', 'N/A')}\n- Financial Coverage: {applicant_data.get('financial_coverage', 'N/A')}\n- Language Score: {applicant_data.get('language_test_score', 'N/A')}\n- Ties to Home Country: {applicant_data.get('family_ties', 'N/A')} and {'has property' if applicant_data.get('has_property') else 'no property'}"
        assessment_results = f"- Final System Status: {final_status}\n- Rule-Based Points Score: {rule_output.get('total_points', 0)}"
    
    elif visa_category == "Tourist Visa":
        profile_details = f"- Funds per day of trip: {applicant_data.get('funds_per_day', 'N/A')}\n- Purpose of Visit: {applicant_data.get('purpose', 'N/A')}\n- Employment Status: {applicant_data.get('employment_status', 'N/A')}\n- Previous Travel History: {applicant_data.get('travel_history', 'N/A')}"
        assessment_results = f"- Final System Status: {final_status}\n- Rule-Based Points Score: {rule_output.get('total_points', 0)}"

    failures_text = ', '.join([f'"{item["description"]}"' for item in rule_output.get('mandatory_failures', [])]) or 'None'
    flags_text = ', '.join([f'"{item["description"]}"' for item in rule_output.get('warning_flags', [])]) or 'None'

    prompt = (f"Analyze the following applicant profile for a **{visa_category}** visa. The analysis should be for a case officer.\n\n"
              f"**Applicant Profile:**\n{profile_details}\n\n"
              f"**Rule-Based Assessment Results:**\n{assessment_results}\n"
              f"- Mandatory Failures Identified: {failures_text}\n"
              f"- Warning Flags Raised: {flags_text}\n\n"
              f"**Your Task:**\nBased on the **{visa_category}** context, provide:\n"
              f"1.  **Executive Summary:** A brief summary of the applicant's chances.\n"
              f"2.  **Key Strengths:** Strongest aspects for this visa type.\n"
              f"3.  **Key Weaknesses/Risks:** Primary concerns.\n"
              f"4.  **Recommendation:** A final recommendation (Approve, Refuse, Further Review).")
    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Failed to get analysis from Gemini API. Error: {e}")
        return "Could not retrieve Generative AI analysis."

# --- Sidebar ---
with st.sidebar:
    st.title("🛂 Applicant Profile")
    visa_category = st.radio("Select Visa Category", ("Skilled Worker", "Student Visa", "Tourist Visa"), horizontal=True)
    st.markdown("---")
    applicant_data = {}
    if visa_category == "Skilled Worker":
        st.header("Core Details"); applicant_data.update({'age': st.slider("Age", 18, 60, 30), 'education_level': st.selectbox("Highest Education", ['PhD', 'Masters', 'DualDegree', 'Bachelors', 'Diploma', 'HighSchool']),'work_experience_years': st.slider("Years of Skilled Work Experience", 0, 20, 5), 'occupation_demand_level': st.selectbox("Occupation Demand Level", ['Critical', 'High', 'Medium', 'Low'])})
        st.header("Language Skills (IELTS)"); applicant_data.update({'ielts_listening': st.number_input("Listening Score", 0.0, 9.0, 7.5, 0.5), 'ielts_reading': st.number_input("Reading Score", 0.0, 9.0, 7.0, 0.5),'ielts_writing': st.number_input("Writing Score", 0.0, 9.0, 7.0, 0.5), 'ielts_speaking': st.number_input("Speaking Score", 0.0, 9.0, 7.0, 0.5)})
        st.header("Financial & Adaptability"); applicant_data.update({'family_size': st.number_input("Family Members", 1, 10, 1), 'settlement_funds': st.number_input("Settlement Funds (CAD)", 0, 200000, 25000, 1000),'has_job_offer': st.checkbox("Has a valid job offer?"), 'has_relative': st.checkbox("Has a relative in the country?"), 'has_local_work_experience': st.checkbox("Have you worked here before?"), 'has_positive_travel_history': st.checkbox("Has positive travel history (USA, UK, etc)?")})
        st.header("Admissibility"); applicant_data.update({'has_criminal_record': st.checkbox("History of criminal record?"), 'has_previous_refusal': st.checkbox("Has a previous visa refusal?")})
    elif visa_category == "Student Visa":
        st.header("Academic Profile"); applicant_data.update({'has_loa': st.checkbox("I have a Letter of Acceptance from a DLI.", value=True), 'gpa': st.select_slider("My previous GPA was:", ['< 2.5', '2.5 - 3.0', '3.0 - 3.5', '> 3.5'], value='> 3.5'), 'study_gap': st.selectbox("Gap since last education:", ['< 1 year', '1 - 3 years', '> 3 years']), 'is_course_relevant': st.checkbox("Is the course relevant to your background?", value=True)})
        st.header("Financial Capacity"); total_cost = st.number_input("Total 1st Year Cost (Tuition + Living)", 20000, 80000, 35000); funds = st.number_input("Funds you have available now (CAD)", 0, 200000, 45000); applicant_data['financial_coverage'] = '> 150%' if funds > total_cost * 1.5 else '100% - 150%' if funds >= total_cost else '100% (Minimum)' if funds == total_cost else '< 100%'
        st.header("Language Proficiency"); applicant_data['language_test_score'] = st.selectbox("Your English Test Score:", ['High (IELTS 7+)', 'Good (IELTS 6.5)', 'Adequate (IELTS 6.0)', 'Low (IELTS < 6.0)'])
        st.header("Ties to Home Country"); applicant_data.update({'family_ties': st.selectbox("Family ties in home country:", ['Immediate family', 'Extended family', 'None']), 'has_property': st.checkbox("Do you or your family own property at home?"), 'has_job_prospects': st.checkbox("Do you have a job offer to return to?")})
        st.header("Admissibility"); applicant_data.update({'has_misrepresentation': st.checkbox("History of visa misrepresentation?"), 'has_previous_refusal': st.checkbox("Has a previous visa refusal?")})
    elif visa_category == "Tourist Visa":
        st.header("Trip Details"); duration = st.slider("Trip Duration (days)", 1, 90, 14); applicant_data['trip_duration'] = duration; funds_avail = st.number_input("Funds available for trip (CAD)", 0, 50000, 4000); applicant_data['funds_per_day'] = '> $300' if duration > 0 and funds_avail/duration > 300 else '$200 - $300' if duration > 0 and funds_avail/duration >= 200 else '$100 - $200' if duration > 0 and funds_avail/duration >= 100 else '< $100'; applicant_data['purpose'] = st.selectbox("Main purpose of visit:", ['Tourism (detailed itinerary)', 'Visiting Family (with invitation)', 'Tourism (basic plan)', 'Other'])
        st.header("Ties to Home Country"); applicant_data.update({'employment_status': st.selectbox("Your employment status at home:", ['Stable full-time job', 'Part-time / Self-employed', 'Unemployed/Student']), 'family_ties': st.selectbox("Family ties at home:", ['Spouse and/or children', 'Parents / Siblings', 'None']), 'has_property': st.checkbox("Do you own property/assets at home?")})
        st.header("Personal History"); applicant_data.update({'travel_history': st.selectbox("Your past international travel:", ['Extensive (USA/UK/Schengen)', 'Some regional travel', 'None']), 'has_host_or_booking': st.checkbox("Do you have an invitation letter or hotel bookings?", value=True)})
        st.header("Admissibility"); applicant_data.update({'has_criminal_record': st.checkbox("History of criminal record?"), 'has_misrepresentation': st.checkbox("History of visa misrepresentation?"), 'has_previous_refusal': st.checkbox("Has a previous visa refusal?")})
    assess_button = st.button("Assess Eligibility", use_container_width=True)

# --- Main Page ---
st.title("Intelligent Visa Eligibility System")
st.markdown("Select a category, fill in the detailed profile, and receive a comprehensive, points-based assessment.")

if assess_button:
    st.header(f"Assessment Results for: {visa_category} Visa")
    
    eligibility_probability = None 
    rules_to_apply = {"Skilled Worker": SKILLED_WORKER_RULES, "Student Visa": STUDENT_VISA_RULES, "Tourist Visa": TOURIST_VISA_RULES}.get(visa_category)
    rule_engine_output = evaluate_applicant(applicant_data, rules_to_apply)
    score = rule_engine_output['total_points']

    if visa_category == "Skilled Worker" and model:
        features_dict = {
            'total_points': score, 'num_mandatory_failures': len(rule_engine_output['mandatory_failures']), 'num_warning_flags': len(rule_engine_output['warning_flags']),
            'points_age': rule_engine_output['points_per_category'].get('Age', 0), 'points_education': rule_engine_output['points_per_category'].get('Education', 0),
            'points_language': rule_engine_output['points_per_category'].get('Language', 0), 'points_work': rule_engine_output['points_per_category'].get('Work Experience', 0),
            'points_bonus': rule_engine_output['points_per_category'].get('Bonus', 0)
        }
        model_features_df = pd.DataFrame([features_dict])[FEATURE_ORDER]
        eligibility_probability = model.predict_proba(model_features_df)[0][1]

    PASS_SCORE, BORDERLINE_SCORE = 75, 50
    if rule_engine_output['mandatory_failures']: status, color, score = "INELIGIBLE (MANDATORY FAILURE)", "red", 0
    elif score >= PASS_SCORE: status, color = "LIKELY ELIGIBLE", "green"
    elif score >= BORDERLINE_SCORE: status, color = "BORDERLINE / FURTHER REVIEW NEEDED", "orange"
    else: status, color = "LIKELY INELIGIBLE", "red"
    
    fig = go.Figure(go.Indicator(mode="gauge+number", value=score, title={'text': f"Eligibility Score: {status}"}, domain={'x': [0, 1], 'y': [0, 1]}, gauge={'axis': {'range': [None, 100]}, 'bar': {'color': color}, 'steps': [{'range': [0, BORDERLINE_SCORE], 'color': '#FF6347'}, {'range': [BORDERLINE_SCORE, PASS_SCORE], 'color': '#FFA500'}]})); st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"Points Breakdown (Total: {rule_engine_output['total_points']})"); st.write(rule_engine_output['points_per_category'])
        if eligibility_probability is not None: st.info(f"Machine Learning Model Check: {eligibility_probability:.2%} probability of eligibility.")
    with col2:
        st.subheader("Important Notices")
        if rule_engine_output.get('mandatory_failures'): st.error("Mandatory Eligibility Criteria Failed:"); [st.write(f"- {rule['description']}") for rule in rule_engine_output['mandatory_failures']]
        if rule_engine_output.get('warning_flags'): st.warning("Warning Flags Raised:"); [st.write(f"- {rule['description']}") for rule in rule_engine_output['warning_flags']]
        if not rule_engine_output.get('mandatory_failures') and not rule_engine_output.get('warning_flags'): st.success("No critical failures or warning flags were identified.")

    st.markdown("---"); st.subheader("🤖 Generative AI Analysis")
    with st.spinner(f"Generating holistic assessment for {visa_category}..."):
        ai_analysis = get_gemini_analysis(visa_category, applicant_data, rule_engine_output, status, eligibility_probability)
        st.markdown(ai_analysis)