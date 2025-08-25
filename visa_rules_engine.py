# visa_rules_engine.py

# --- A. SKILLED WORKER VISA RULES (Comprehensive Points System) ---
SKILLED_WORKER_RULES = [
    # 1. Core Human Capital (Max 67)
    {"id": "SW_AGE", "category": "Age", "type": "points", "logic": lambda d: 12 if 18<=d['age']<=35 else 11 if d['age']==36 else 10 if d['age']==37 else 9 if d['age']==38 else 8 if d['age']==39 else 7 if d['age']==40 else 6 if d['age']==41 else 5 if d['age']==42 else 4 if d['age']==43 else 3 if d['age']==44 else 2 if d['age']==45 else 1 if d['age']==46 else 0},
    {"id": "SW_EDU", "category": "Education", "type": "points", "logic": lambda d: 25 if d['education_level']=='PhD' else 23 if d['education_level']=='Masters' else 22 if d['education_level']=='DualDegree' else 21 if d['education_level']=='Bachelors' else 19 if d['education_level']=='Diploma' else 5},
    {"id": "SW_WORK", "category": "Work Experience", "type": "points", "logic": lambda d: 15 if d['work_experience_years']>=6 else 13 if 4<=d['work_experience_years']<6 else 11 if 2<=d['work_experience_years']<4 else 9 if d['work_experience_years']==1 else 0},
    {"id": "SW_LANG_L", "category": "Language", "type": "points", "logic": lambda d: 6 if d['ielts_listening']>=8.0 else 5 if d['ielts_listening']>=7.5 else 4 if d['ielts_listening']>=6.0 else 0},
    {"id": "SW_LANG_S", "category": "Language", "type": "points", "logic": lambda d: 6 if d['ielts_speaking']>=7.0 else 5 if d['ielts_speaking']>=6.5 else 4 if d['ielts_speaking']>=6.0 else 0},
    {"id": "SW_LANG_R", "category": "Language", "type": "points", "logic": lambda d: 6 if d['ielts_reading']>=7.0 else 5 if d['ielts_reading']>=6.5 else 4 if d['ielts_reading']>=6.0 else 0},
    {"id": "SW_LANG_W", "category": "Language", "type": "points", "logic": lambda d: 6 if d['ielts_writing']>=7.0 else 5 if d['ielts_writing']>=6.5 else 4 if d['ielts_writing']>=6.0 else 0},
    
    # 2. Adaptability & Bonus Factors (Max 33)
    {"id": "SW_JOB_OFFER", "category": "Bonus", "type": "points", "logic": lambda d: 10 if d.get('has_job_offer') else 0},
    {"id": "SW_DEMAND", "category": "Bonus", "type": "points", "logic": lambda d: 8 if d.get('occupation_demand_level')=='Critical' else 5 if d.get('occupation_demand_level')=='High' else 0},
    {"id": "SW_LOCAL_WORK", "category": "Bonus", "type": "points", "logic": lambda d: 5 if d.get('has_local_work_experience') else 0},
    {"id": "SW_RELATIVE", "category": "Bonus", "type": "points", "logic": lambda d: 5 if d.get('has_relative') else 0},
    {"id": "SW_TRAVEL_HIST", "category": "Bonus", "type": "points", "logic": lambda d: 5 if d.get('has_positive_travel_history') else 0},

    # 3. Mandatory Failures & Flags
    {"id": "SW_FAIL_FUNDS", "type": "mandatory_fail", "description": "Settlement funds below minimum for family size.", "logic": lambda d: d['settlement_funds'] < (15000 + (d.get('family_size', 1) - 1) * 4000)},
    {"id": "SW_FAIL_CRIMINAL", "type": "mandatory_fail", "description": "Applicant has a disqualifying criminal record.", "logic": lambda d: d.get('has_criminal_record')},
    {"id": "SW_FAIL_LANG_MIN", "type": "mandatory_fail", "description": "Minimum language score (IELTS 6.0 in all bands) not met.", "logic": lambda d: min(d['ielts_speaking'], d['ielts_listening'], d['ielts_reading'], d['ielts_writing']) < 6.0},
    {"id": "SW_FLAG_FUNDS", "type": "flag", "description": "Funds are very close to the minimum required level.", "logic": lambda d: (15000+(d.get('family_size',1)-1)*4000) <= d['settlement_funds'] < (17000+(d.get('family_size',1)-1)*4000)},
    {"id": "SW_FLAG_REFUSAL", "type": "flag", "description": "Previous visa refusal needs to be strongly addressed.", "logic": lambda d: d.get('has_previous_refusal')},
]

# --- B. STUDENT VISA RULES (New 100-Point System) ---
STUDENT_VISA_RULES = [
    # 1. Academic Profile (Max 30)
    {"id": "ST_LOA", "category": "Academics", "type": "points", "logic": lambda d: 20 if d.get('has_loa') else -100}, # Effectively a fail
    {"id": "ST_GPA", "category": "Academics", "type": "points", "logic": lambda d: 10 if d.get('gpa') == '> 3.5' else 7 if d.get('gpa') == '3.0 - 3.5' else 4 if d.get('gpa') == '2.5 - 3.0' else 0},

    # 2. Financial Capacity (Max 30)
    {"id": "ST_FIN_COVERAGE", "category": "Financials", "type": "points", "logic": lambda d: 30 if d.get('financial_coverage') == '> 150%' else 20 if d.get('financial_coverage') == '100% - 150%' else 5 if d.get('financial_coverage') == '100% (Minimum)' else -100},
    
    # 3. Language Proficiency (Max 15)
    {"id": "ST_LANG_SCORE", "category": "Language", "type": "points", "logic": lambda d: 15 if d.get('language_test_score') == 'High (IELTS 7+)' else 10 if d.get('language_test_score') == 'Good (IELTS 6.5)' else 5 if d.get('language_test_score') == 'Adequate (IELTS 6.0)' else 0},
    
    # 4. Non-Immigrant Intent / Ties to Home Country (Max 25)
    {"id": "ST_TIES_FAMILY", "category": "Home Ties", "type": "points", "logic": lambda d: 10 if d.get('family_ties') == 'Immediate family' else 5 if d.get('family_ties') == 'Extended family' else 0},
    {"id": "ST_TIES_PROPERTY", "category": "Home Ties", "type": "points", "logic": lambda d: 10 if d.get('has_property') else 0},
    {"id": "ST_TIES_JOB", "category": "Home Ties", "type": "points", "logic": lambda d: 5 if d.get('has_job_prospects') else 0},

    # 5. Mandatory Failures & Flags
    {"id": "ST_FAIL_MISREP", "type": "mandatory_fail", "description": "History of visa misrepresentation.", "logic": lambda d: d.get('has_misrepresentation')},
    {"id": "ST_FLAG_STUDY_GAP", "type": "flag", "description": "A long study gap requires a clear explanation.", "logic": lambda d: d.get('study_gap') == '> 3 years'},
    {"id": "ST_FLAG_REFUSAL", "type": "flag", "description": "Previous visa refusal raises concerns.", "logic": lambda d: d.get('has_previous_refusal')},
    {"id": "ST_FLAG_COURSE_RELEVANCE", "type": "flag", "description": "Chosen course is not clearly relevant to past studies/career.", "logic": lambda d: not d.get('is_course_relevant')},
]

# --- C. TOURIST VISA RULES (New 100-Point System) ---
TOURIST_VISA_RULES = [
    # 1. Financial Capacity (Max 30)
    {"id": "TR_FUNDS", "category": "Financials", "type": "points", "logic": lambda d: 30 if d.get('funds_per_day') == '> $300' else 20 if d.get('funds_per_day') == '$200 - $300' else 10 if d.get('funds_per_day') == '$100 - $200' else -100},

    # 2. Purpose of Visit (Max 25)
    {"id": "TR_PURPOSE", "category": "Purpose", "type": "points", "logic": lambda d: 25 if d.get('purpose') == 'Visiting Family (with invitation)' else 20 if d.get('purpose') == 'Tourism (detailed itinerary)' else 10 if d.get('purpose') == 'Tourism (basic plan)' else 5},
    
    # 3. Ties to Home Country (Max 35)
    {"id": "TR_TIES_EMPLOYMENT", "category": "Home Ties", "type": "points", "logic": lambda d: 15 if d.get('employment_status') == 'Stable full-time job' else 5 if d.get('employment_status') == 'Part-time / Self-employed' else 0},
    {"id": "TR_TIES_FAMILY", "category": "Home Ties", "type": "points", "logic": lambda d: 10 if d.get('family_ties') == 'Spouse and/or children' else 5 if d.get('family_ties') == 'Parents / Siblings' else 0},
    {"id": "TR_TIES_PROPERTY", "category": "Home Ties", "type": "points", "logic": lambda d: 10 if d.get('has_property') else 0},

    # 4. Personal History (Max 10)
    {"id": "TR_TRAVEL_HISTORY", "category": "History", "type": "points", "logic": lambda d: 10 if d.get('travel_history') == 'Extensive (USA/UK/Schengen)' else 5 if d.get('travel_history') == 'Some regional travel' else 0},

    # 5. Mandatory Failures & Flags
    {"id": "TR_FAIL_CRIMINAL_MISREP", "type": "mandatory_fail", "description": "History of criminal record or visa misrepresentation.", "logic": lambda d: d.get('has_criminal_record') or d.get('has_misrepresentation')},
    {"id": "TR_FLAG_LONG_STAY", "type": "flag", "description": "Unusually long trip duration requested for a first-time tourist.", "logic": lambda d: d.get('trip_duration') > 30 and d.get('travel_history') != 'Extensive (USA/UK/Schengen)'},
    {"id": "TR_FLAG_NO_HOST", "type": "flag", "description": "No host or hotel bookings can be a risk factor.", "logic": lambda d: not d.get('has_host_or_booking')},
    {"id": "TR_FLAG_REFUSAL", "type": "flag", "description": "Previous visa refusal needs strong justification.", "logic": lambda d: d.get('has_previous_refusal')},
]

# --- UNIVERSAL EVALUATION ENGINE ---
def evaluate_applicant(applicant_data, rules):
    """
    A universal engine that processes a list of rules against applicant data.
    It calculates points, identifies mandatory failures, and raises warning flags.
    """
    total_points = 0
    points_breakdown = {}
    mandatory_failures = []
    warning_flags = []

    for rule in rules:
        try:
            result = rule['logic'](applicant_data)
            
            if rule['type'] == 'points':
                category = rule.get('category', 'General')
                current_points = points_breakdown.get(category, 0)
                points_breakdown[category] = current_points + result
                total_points += result
            
            elif rule['type'] == 'mandatory_fail' and result:
                mandatory_failures.append(rule)
            
            elif rule['type'] == 'flag' and result:
                warning_flags.append(rule)
        
        except (KeyError, TypeError) as e:
            # This can help debug if a key is missing from the sidebar data
            # print(f"Rule {rule.get('id')} failed with error: {e}")
            continue
            
    # Ensure points don't go below zero from penalties
    total_points = max(0, total_points)

    return {
        "total_points": total_points,
        "points_per_category": points_breakdown,
        "mandatory_failures": mandatory_failures,
        "warning_flags": warning_flags,
    }