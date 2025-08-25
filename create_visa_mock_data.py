# create_visa_mock_data.py
import pandas as pd
import numpy as np
import random

def generate_applicant(is_eligible_profile):
    """Generates a single applicant record."""
    if is_eligible_profile:
        # Profile for a likely eligible candidate
        age = np.random.randint(25, 38)
        edu_level = random.choice(['Bachelors', 'Masters', 'PhD'])
        work_years = np.random.randint(3, 10)
        ielts = [np.random.uniform(6.5, 8.5) for _ in range(4)]
        family_size = np.random.randint(1, 4)
        funds = np.random.randint(20000 + (family_size * 5000), 80000)
        has_criminal_record = False
        has_misrepresentation = False
        has_previous_refusal = np.random.choice([True, False], p=[0.2, 0.8])
        occupation_demand = random.choice(['High', 'Critical', 'Medium'])
        has_positive_travel_history = True
    else:
        # Profile for a likely ineligible candidate
        age = np.random.randint(38, 50)
        edu_level = random.choice(['HighSchool', 'Diploma', 'Bachelors'])
        work_years = np.random.randint(0, 4)
        ielts = [np.random.uniform(5.0, 6.5) for _ in range(4)]
        family_size = np.random.randint(1, 5)
        funds = np.random.randint(5000, 20000 + (family_size * 2000))
        has_criminal_record = np.random.choice([True, False], p=[0.3, 0.7])
        has_misrepresentation = np.random.choice([True, False], p=[0.1, 0.9])
        has_previous_refusal = np.random.choice([True, False], p=[0.6, 0.4])
        occupation_demand = random.choice(['Low', 'Medium'])
        has_positive_travel_history = np.random.choice([True, False], p=[0.4, 0.6])

    return {
        "age": age,
        "education_level": edu_level,
        "work_experience_years": work_years,
        "ielts_listening": round(ielts[0], 1),
        "ielts_reading": round(ielts[1], 1),
        "ielts_writing": round(ielts[2], 1),
        "ielts_speaking": round(ielts[3], 1),
        "settlement_funds": funds,
        "family_size": family_size,
        "occupation_demand_level": occupation_demand,
        "has_positive_travel_history": has_positive_travel_history,
        "has_job_offer": np.random.choice([True, False]),
        "has_relative": np.random.choice([True, False]),
        "spouse_language_proficient": np.random.choice([True, False]),
        "has_local_work_experience": np.random.choice([True, False]),
        "has_local_education": np.random.choice([True, False]),
        "has_criminal_record": has_criminal_record,
        "failed_medical_exam": np.random.choice([True, False], p=[0.05, 0.95]),
        "has_misrepresentation": has_misrepresentation,
        "has_valid_passport": np.random.choice([True, False], p=[0.98, 0.02]),
        "has_employment_gap": np.random.choice([True, False]),
        "has_previous_refusal": has_previous_refusal,
        "is_eligible": 1 if is_eligible_profile else 0
    }

print("Generating enhanced mock visa applicant data...")
applicants = [generate_applicant(is_eligible_profile=True) for _ in range(750)]
applicants.extend([generate_applicant(is_eligible_profile=False) for _ in range(750)])

df = pd.DataFrame(applicants)
df.to_csv("visa_mock_data.csv", index=False)
print("Data saved to visa_mock_data.csv")