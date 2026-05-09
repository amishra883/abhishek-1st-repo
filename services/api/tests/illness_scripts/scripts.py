"""Clinically detailed illness scripts.

Each script captures a distinct presentation with its own EMR backdrop,
expected deterministic outputs (red flags, quality gaps), and golden
agent outputs that the summary and recommendation agents must satisfy.

Naming: <protocol>_<clinical_pattern>
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class IllnessScript:
    id: str
    label: str
    chief_complaint: str
    patient_id: str
    emr_history: Dict[str, Any]
    answers: Dict[str, Any]

    expected_red_flag_ids: List[str]
    expected_quality_gap_ids: List[str]

    golden_summary: Dict[str, Any]
    golden_recommendation: Dict[str, Any]

    summary_must_contain: List[str] = field(default_factory=list)
    summary_must_not_contain: List[str] = field(default_factory=list)
    recommendation_must_contain: List[str] = field(default_factory=list)
    recommendation_must_not_contain: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Chest Pain Scripts
# ---------------------------------------------------------------------------

CHEST_PAIN_ACS_CLASSIC = IllnessScript(
    id="cp_acs_classic",
    label="Classic ACS: 58M diabetic with exertional pressure radiating to jaw",
    chief_complaint="chest pain",
    patient_id="CP001",
    emr_history={
        "conditions": ["hypertension", "type_2_diabetes", "hyperlipidemia"],
        "meds": ["lisinopril", "metformin", "aspirin"],
        "labs": {"a1c": "8.1", "ldl": "145"},
        "studies": ["ecg_2024_normal_sinus"],
        "vitals": {"blood_pressure": "158/94", "heart_rate": "98", "oxygen_saturation": "96"},
        "social_history": {"tobacco": "former"},
    },
    answers={
        "onset": "Today",
        "quality": "Pressure",
        "severity": 8,
        "radiation": ["Jaw", "Left arm"],
        "sob": "Yes",
        "exertional": "Yes",
    },
    expected_red_flag_ids=["possible_acs_pattern"],
    expected_quality_gap_ids=["statin_gap_if_cad_or_diabetes", "bp_control_gap_if_hypertension"],
    golden_summary={
        "hpi": "58-year-old male with HTN, T2DM, and hyperlipidemia presents with acute-onset substernal chest pressure (8/10) radiating to jaw and left arm, worsened with exertion, associated with dyspnea. Onset today.",
        "key_positives": [
            "pressure quality",
            "radiation to jaw and left arm",
            "exertional worsening",
            "shortness of breath",
            "acute onset",
        ],
        "key_negatives": [],
        "relevant_history": [
            "hypertension — uncontrolled (158/94)",
            "type 2 diabetes — A1c 8.1",
            "hyperlipidemia — LDL 145, no statin",
            "former tobacco use",
            "prior normal ECG",
        ],
        "priority": "urgent",
    },
    golden_recommendation={
        "treatment_considerations": [
            "Obtain stat 12-lead ECG",
            "Serial troponins",
            "Aspirin 325mg if not contraindicated",
            "Cardiology consult if ECG or troponin abnormal",
        ],
        "patient_education": [
            "You are being evaluated for a possible heart-related cause of your chest pain",
            "Call 911 immediately if pain worsens or you feel faint",
        ],
        "preventive_measures": [
            "Statin initiation for LDL 145 with diabetes",
            "Blood pressure optimization — current 158/94",
            "A1c goal below 7 — currently 8.1",
        ],
        "quality_gap_prompts": [
            "Patient has diabetes without a statin on med list.",
            "Hypertensive with uncontrolled BP (158/94).",
        ],
    },
    summary_must_contain=["pressure", "jaw", "left arm", "dyspnea", "diabetes"],
    summary_must_not_contain=["diagnos", "myocardial infarction", "STEMI"],
    recommendation_must_contain=["ECG", "troponin"],
    recommendation_must_not_contain=["diagnos"],
)

CHEST_PAIN_GERD = IllnessScript(
    id="cp_gerd",
    label="GERD mimic: 34F burning chest after meals, no cardiac risk",
    chief_complaint="chest pain",
    patient_id="CP002",
    emr_history={
        "conditions": [],
        "meds": ["omeprazole"],
        "labs": {},
        "studies": [],
        "vitals": {"blood_pressure": "118/72", "heart_rate": "74", "oxygen_saturation": "99"},
        "social_history": {"tobacco": "never"},
    },
    answers={
        "onset": "More than 1 week ago",
        "quality": "Burning",
        "severity": 4,
        "radiation": ["Does not spread"],
        "sob": "No",
        "exertional": "No",
    },
    expected_red_flag_ids=[],
    expected_quality_gap_ids=[],
    golden_summary={
        "hpi": "34-year-old female with no significant cardiac history presents with chronic burning chest discomfort (4/10), non-radiating, non-exertional, without dyspnea. Symptoms ongoing for more than one week.",
        "key_positives": [
            "burning quality",
            "chronic duration",
        ],
        "key_negatives": [
            "no radiation",
            "no shortness of breath",
            "not exertional",
            "no cardiac risk factors",
        ],
        "relevant_history": [
            "on omeprazole — possible GERD history",
            "normal vitals",
            "nonsmoker",
        ],
        "priority": "routine",
    },
    golden_recommendation={
        "treatment_considerations": [
            "Assess adequacy of current PPI therapy",
            "Consider GI referral if symptoms persist despite PPI",
            "Low threshold for ECG given chest pain complaint",
        ],
        "patient_education": [
            "Burning chest discomfort can be related to acid reflux",
            "Avoid eating within 3 hours of lying down",
            "Return if pain changes in character or becomes exertional",
        ],
        "preventive_measures": [
            "Dietary modification counseling",
            "Weight management if applicable",
        ],
        "quality_gap_prompts": [],
    },
    summary_must_contain=["burning", "non-exertional", "omeprazole"],
    summary_must_not_contain=["ACS", "infarction", "urgent"],
    recommendation_must_contain=["PPI", "ECG"],
    recommendation_must_not_contain=["troponin", "cardiology consult"],
)

CHEST_PAIN_MSK = IllnessScript(
    id="cp_msk",
    label="Musculoskeletal: 27M sharp reproducible chest wall pain after gym",
    chief_complaint="chest pain",
    patient_id="CP003",
    emr_history={
        "conditions": [],
        "meds": [],
        "labs": {},
        "studies": [],
        "vitals": {"blood_pressure": "122/76", "heart_rate": "68", "oxygen_saturation": "99"},
        "social_history": {"tobacco": "never"},
    },
    answers={
        "onset": "1-2 days ago",
        "quality": "Sharp",
        "severity": 5,
        "radiation": ["Does not spread"],
        "sob": "No",
        "exertional": "No",
    },
    expected_red_flag_ids=[],
    expected_quality_gap_ids=[],
    golden_summary={
        "hpi": "27-year-old male with no medical history presents with sharp chest pain (5/10), non-radiating, non-exertional, without dyspnea. Started 1-2 days ago.",
        "key_positives": [
            "sharp quality",
            "subacute onset",
        ],
        "key_negatives": [
            "no radiation",
            "no shortness of breath",
            "not exertional",
            "no cardiac history",
            "no medications",
        ],
        "relevant_history": [
            "no known medical conditions",
            "normal vitals",
        ],
        "priority": "routine",
    },
    golden_recommendation={
        "treatment_considerations": [
            "Consider NSAIDs for musculoskeletal pain if no contraindications",
            "Chest wall palpation to assess reproducibility",
        ],
        "patient_education": [
            "Sharp, non-exertional chest pain in a young patient is often musculoskeletal",
            "Return if pain becomes pressure-like, exertional, or associated with shortness of breath",
        ],
        "preventive_measures": [
            "Proper warm-up before physical activity",
        ],
        "quality_gap_prompts": [],
    },
    summary_must_contain=["sharp", "non-radiating"],
    summary_must_not_contain=["ACS", "urgent", "statin"],
    recommendation_must_contain=["musculoskeletal"],
    recommendation_must_not_contain=["troponin", "aspirin"],
)

CHEST_PAIN_PE_CONCERN = IllnessScript(
    id="cp_pe_concern",
    label="PE concern: 42F sharp pleuritic pain with SOB, recent travel",
    chief_complaint="chest pain",
    patient_id="CP004",
    emr_history={
        "conditions": [],
        "meds": ["oral_contraceptive"],
        "labs": {},
        "studies": [],
        "vitals": {"blood_pressure": "130/82", "heart_rate": "110", "oxygen_saturation": "93"},
        "social_history": {"tobacco": "never"},
    },
    answers={
        "onset": "Today",
        "quality": "Sharp",
        "severity": 7,
        "radiation": ["Back"],
        "sob": "Yes",
        "exertional": "Yes",
    },
    expected_red_flag_ids=[],
    expected_quality_gap_ids=[],
    golden_summary={
        "hpi": "42-year-old female on oral contraceptives presents with acute sharp chest pain (7/10) radiating to back, worse with exertion, associated with dyspnea. Tachycardic at 110 with oxygen saturation 93%.",
        "key_positives": [
            "sharp pleuritic quality",
            "radiation to back",
            "shortness of breath",
            "exertional worsening",
            "tachycardia (HR 110)",
            "hypoxia (SpO2 93%)",
        ],
        "key_negatives": [
            "no prior cardiac history",
            "no pressure quality",
        ],
        "relevant_history": [
            "oral contraceptive use — VTE risk factor",
            "tachycardia and hypoxia on vitals",
        ],
        "priority": "urgent",
    },
    golden_recommendation={
        "treatment_considerations": [
            "Assess Wells score for PE probability",
            "Consider D-dimer or CT pulmonary angiography",
            "Supplemental oxygen for SpO2 93%",
            "Obtain ECG to evaluate tachycardia",
        ],
        "patient_education": [
            "Your symptoms and vital signs need further urgent evaluation",
            "Blood clots in the lungs can cause chest pain and shortness of breath",
        ],
        "preventive_measures": [
            "Discuss VTE risk with oral contraceptive use",
            "Encourage mobility during prolonged travel",
        ],
        "quality_gap_prompts": [],
    },
    summary_must_contain=["sharp", "dyspnea", "tachycardia", "oral contraceptive"],
    summary_must_not_contain=["diagnos", "pulmonary embolism"],
    recommendation_must_contain=["Wells", "D-dimer"],
    recommendation_must_not_contain=["diagnos", "confirmed PE"],
)

CHEST_PAIN_ANXIETY = IllnessScript(
    id="cp_anxiety_palpitations",
    label="Anxiety-related: 23F palpitations with tightness, no risk factors",
    chief_complaint="chest tightness",
    patient_id="CP005",
    emr_history={
        "conditions": ["generalized_anxiety_disorder"],
        "meds": ["sertraline"],
        "labs": {"tsh": "2.1"},
        "studies": [],
        "vitals": {"blood_pressure": "116/70", "heart_rate": "88", "oxygen_saturation": "99"},
        "social_history": {"tobacco": "never"},
    },
    answers={
        "onset": "Within 1 week",
        "quality": "Palpitations",
        "severity": 3,
        "radiation": ["Does not spread"],
        "sob": "No",
        "exertional": "No",
    },
    expected_red_flag_ids=[],
    expected_quality_gap_ids=[],
    golden_summary={
        "hpi": "23-year-old female with generalized anxiety disorder presents with intermittent palpitations and chest tightness (3/10), non-radiating, non-exertional, without dyspnea. Symptoms for less than one week.",
        "key_positives": [
            "palpitations",
            "known anxiety disorder",
        ],
        "key_negatives": [
            "no radiation",
            "no shortness of breath",
            "not exertional",
            "no cardiac risk factors",
            "normal TSH",
        ],
        "relevant_history": [
            "generalized anxiety disorder on sertraline",
            "normal TSH — thyroid unlikely contributor",
            "normal vitals",
        ],
        "priority": "routine",
    },
    golden_recommendation={
        "treatment_considerations": [
            "ECG to rule out arrhythmia",
            "Assess anxiety symptom control on current SSRI dose",
            "Consider Holter monitor if palpitations are recurrent",
        ],
        "patient_education": [
            "Anxiety can cause palpitations and chest tightness",
            "Caffeine and stimulants can worsen palpitations",
            "Return if you experience syncope or sustained rapid heartbeat",
        ],
        "preventive_measures": [
            "Stress management techniques",
            "Limit caffeine intake",
        ],
        "quality_gap_prompts": [],
    },
    summary_must_contain=["anxiety", "palpitations", "sertraline"],
    summary_must_not_contain=["ACS", "urgent", "troponin"],
    recommendation_must_contain=["ECG", "anxiety"],
    recommendation_must_not_contain=["aspirin", "statin"],
)

# ---------------------------------------------------------------------------
# Urinary Scripts
# ---------------------------------------------------------------------------

URINARY_SIMPLE_UTI = IllnessScript(
    id="uri_simple_uti",
    label="Simple UTI: 28F dysuria and frequency, no systemic symptoms",
    chief_complaint="painful urination",
    patient_id="URI001",
    emr_history={
        "conditions": [],
        "meds": [],
        "labs": {},
        "studies": [],
        "vitals": {"temperature": "98.6", "blood_pressure": "120/74", "heart_rate": "72"},
        "social_history": {},
    },
    answers={
        "onset": "1-2 days ago",
        "dysuria": "Yes",
        "frequency": "Yes",
        "hematuria": "No",
        "flank_pain": "No",
        "fever": "No",
    },
    expected_red_flag_ids=[],
    expected_quality_gap_ids=[],
    golden_summary={
        "hpi": "28-year-old female presents with 1-2 days of dysuria and urinary frequency. Afebrile, no flank pain, no hematuria.",
        "key_positives": [
            "dysuria",
            "urinary frequency",
        ],
        "key_negatives": [
            "no fever",
            "no flank pain",
            "no hematuria",
        ],
        "relevant_history": [
            "no significant medical history",
            "afebrile, normal vitals",
        ],
        "priority": "routine",
    },
    golden_recommendation={
        "treatment_considerations": [
            "Obtain urinalysis",
            "Empiric antibiotic if UA positive — consider nitrofurantoin or TMP-SMX",
            "Urine culture for susceptibility if recurrent",
        ],
        "patient_education": [
            "Drink plenty of water to help flush the urinary tract",
            "Take the full course of antibiotics if prescribed",
            "Return if fever, back pain, or vomiting develop",
        ],
        "preventive_measures": [
            "Post-coital voiding",
            "Adequate hydration",
        ],
        "quality_gap_prompts": [],
    },
    summary_must_contain=["dysuria", "frequency", "afebrile"],
    summary_must_not_contain=["pyelonephritis", "sepsis"],
    recommendation_must_contain=["urinalysis", "antibiotic"],
    recommendation_must_not_contain=["CT scan", "IV antibiotics", "hospitalization"],
)

URINARY_PYELONEPHRITIS = IllnessScript(
    id="uri_pyelo",
    label="Pyelonephritis: 35F flank pain, fever, dysuria",
    chief_complaint="burning urination",
    patient_id="URI002",
    emr_history={
        "conditions": ["recurrent_uti"],
        "meds": [],
        "labs": {"urinalysis": "prior positive nitrites and leukocytes"},
        "studies": [],
        "vitals": {"temperature": "101.8", "blood_pressure": "108/68", "heart_rate": "104"},
        "social_history": {},
    },
    answers={
        "onset": "1-2 days ago",
        "dysuria": "Yes",
        "frequency": "Yes",
        "hematuria": "Yes",
        "flank_pain": "Yes",
        "fever": "Yes",
    },
    expected_red_flag_ids=["possible_pyelonephritis"],
    expected_quality_gap_ids=[],
    golden_summary={
        "hpi": "35-year-old female with history of recurrent UTIs presents with 1-2 days of dysuria, frequency, gross hematuria, left flank pain, and fever (101.8F). Tachycardic at 104.",
        "key_positives": [
            "dysuria",
            "urinary frequency",
            "gross hematuria",
            "flank pain",
            "fever 101.8F",
            "tachycardia (HR 104)",
        ],
        "key_negatives": [],
        "relevant_history": [
            "recurrent UTIs",
            "prior UA with positive nitrites and leukocytes",
            "tachycardic, borderline hypotensive",
        ],
        "priority": "urgent",
    },
    golden_recommendation={
        "treatment_considerations": [
            "Obtain urinalysis and urine culture with sensitivities",
            "CBC and BMP to assess for systemic infection",
            "Consider fluoroquinolone or TMP-SMX pending culture",
            "Assess for IV fluid need given borderline BP and tachycardia",
            "Consider renal ultrasound given recurrent UTIs and flank pain",
        ],
        "patient_education": [
            "Fever with back pain may mean infection has reached the kidneys",
            "Seek emergency care if unable to keep fluids down or fever exceeds 103F",
            "Complete the full antibiotic course even if feeling better",
        ],
        "preventive_measures": [
            "Urology or gynecology referral for recurrent UTI workup",
            "Consider prophylactic antibiotics for recurrent UTIs",
        ],
        "quality_gap_prompts": [],
    },
    summary_must_contain=["flank pain", "fever", "hematuria", "recurrent"],
    summary_must_not_contain=["diagnos"],
    recommendation_must_contain=["urine culture", "renal ultrasound"],
    recommendation_must_not_contain=["diagnos"],
)

URINARY_DIABETIC_COMPLICATED = IllnessScript(
    id="uri_diabetic_complicated",
    label="Complicated UTI: 62M diabetic with hematuria and flank pain, afebrile",
    chief_complaint="urinary",
    patient_id="URI003",
    emr_history={
        "conditions": ["type_2_diabetes", "chronic_kidney_disease"],
        "meds": ["metformin", "insulin_glargine", "lisinopril"],
        "labs": {"a1c": "9.2", "bmp": {"creatinine": "1.8", "gfr": "42"}},
        "studies": ["renal_ultrasound_2024_bilateral_cortical_thinning"],
        "vitals": {"temperature": "98.9", "blood_pressure": "142/88", "heart_rate": "82"},
        "social_history": {"tobacco": "current"},
    },
    answers={
        "onset": "Within 1 week",
        "dysuria": "Yes",
        "frequency": "Yes",
        "hematuria": "Yes",
        "flank_pain": "Yes",
        "fever": "No",
    },
    expected_red_flag_ids=[],
    expected_quality_gap_ids=[],
    golden_summary={
        "hpi": "62-year-old male with poorly controlled T2DM (A1c 9.2), CKD stage 3b (GFR 42), presents with one week of dysuria, frequency, hematuria, and flank pain. Afebrile.",
        "key_positives": [
            "dysuria",
            "urinary frequency",
            "gross hematuria",
            "flank pain",
            "poorly controlled diabetes",
            "CKD with elevated creatinine",
        ],
        "key_negatives": [
            "afebrile",
        ],
        "relevant_history": [
            "type 2 diabetes — A1c 9.2, poorly controlled",
            "CKD stage 3b — Cr 1.8, GFR 42",
            "prior renal US showing bilateral cortical thinning",
            "current tobacco use",
            "on metformin and insulin",
        ],
        "priority": "urgent",
    },
    golden_recommendation={
        "treatment_considerations": [
            "Urinalysis and urine culture — complicated UTI in setting of CKD",
            "Renal-dose-adjusted antibiotics — avoid nephrotoxic agents",
            "Repeat BMP to monitor renal function",
            "Urology referral for hematuria workup given age and CKD",
            "Consider CT urogram if renal function permits",
        ],
        "patient_education": [
            "Diabetes and kidney disease increase risk of urinary infections",
            "Hematuria needs further workup to rule out other causes",
            "Seek emergency care if fever develops or urine output drops",
        ],
        "preventive_measures": [
            "Tobacco cessation counseling",
            "A1c optimization — goal below 7",
            "Nephrology follow-up for CKD progression monitoring",
        ],
        "quality_gap_prompts": [],
    },
    summary_must_contain=["CKD", "A1c", "hematuria", "creatinine"],
    summary_must_not_contain=["diagnos", "cancer"],
    recommendation_must_contain=["renal-dose", "urology"],
    recommendation_must_not_contain=["diagnos"],
)

URINARY_YOUNG_MALE_STI = IllnessScript(
    id="uri_young_male_sti_concern",
    label="STI concern: 22M dysuria without classic UTI features",
    chief_complaint="painful urination",
    patient_id="URI004",
    emr_history={
        "conditions": [],
        "meds": [],
        "labs": {},
        "studies": [],
        "vitals": {"temperature": "98.4", "blood_pressure": "118/72", "heart_rate": "70"},
        "social_history": {},
    },
    answers={
        "onset": "Within 1 week",
        "dysuria": "Yes",
        "frequency": "No",
        "hematuria": "No",
        "flank_pain": "No",
        "fever": "No",
    },
    expected_red_flag_ids=[],
    expected_quality_gap_ids=[],
    golden_summary={
        "hpi": "22-year-old male presents with dysuria for less than one week. No urinary frequency, hematuria, flank pain, or fever.",
        "key_positives": [
            "dysuria",
        ],
        "key_negatives": [
            "no frequency",
            "no hematuria",
            "no flank pain",
            "no fever",
            "no urinary urgency",
        ],
        "relevant_history": [
            "no significant medical history",
            "normal vitals",
        ],
        "priority": "routine",
    },
    golden_recommendation={
        "treatment_considerations": [
            "Obtain urinalysis",
            "Consider STI screening — GC/chlamydia NAAT given age and isolated dysuria",
            "Urine culture if UA suggests bacterial infection",
        ],
        "patient_education": [
            "Dysuria in young males can be caused by urinary infection or sexually transmitted infection",
            "Complete any prescribed treatment and notify partners if STI is found",
        ],
        "preventive_measures": [
            "Safe sex practices",
            "Routine STI screening per guidelines",
        ],
        "quality_gap_prompts": [],
    },
    summary_must_contain=["dysuria", "male"],
    summary_must_not_contain=["pyelonephritis", "urgent"],
    recommendation_must_contain=["STI", "urinalysis"],
    recommendation_must_not_contain=["IV antibiotics", "hospitalization"],
)


ALL_SCRIPTS = [
    CHEST_PAIN_ACS_CLASSIC,
    CHEST_PAIN_GERD,
    CHEST_PAIN_MSK,
    CHEST_PAIN_PE_CONCERN,
    CHEST_PAIN_ANXIETY,
    URINARY_SIMPLE_UTI,
    URINARY_PYELONEPHRITIS,
    URINARY_DIABETIC_COMPLICATED,
    URINARY_YOUNG_MALE_STI,
]
