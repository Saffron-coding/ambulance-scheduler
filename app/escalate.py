#priority map
category = {
    "C1": 1,
    "C2": 2,
    "C3": 3,
    "C4": 4
}

#creates dictionary of all keywords that should escalate priority per category
Escalation_rules ={ "C1": ["cardiac arrest", "not breathing", "unresponsive", "respiratory arrest",
                               "no pulse", "asthma", "blue", "suicidal"],
                        "C2": ["stroke", "heart-attack","severe burn", "unconscious", "seizure", "chest pain"],
                        "C3": ["labour", "abdominal pain", "palpitations", "broken", "fall"],
                        "C4": ["vomiting", "diarrhea", "headache", "dizziness", "numbness"]}

def escalate_priority(user_assigned_category,incident_name, medical_history, patient_notes, patient_age):
    text = f"{incident_name or ''} {medical_history or ''} {patient_notes or ''} {patient_age or ''}".lower()

#assumes user priority is correct
    best_category = user_assigned_category

#check if any keywords appear in text and find the category, if none continue
    if category[user_assigned_category] > 1:
        for rule_category, keywords in Escalation_rules.items():
            if not any(word in text for word in keywords):
                continue
#if keyword match compare user input and escalate
            else:
                if category[rule_category] < category[best_category]:
                    best_category = rule_category
#escalate on age
        if patient_age >=65 and category[best_category] > 1:
            if best_category == "C4":
                best_category = "C3"
            elif best_category == "C3":
                best_category = "C2"
            elif best_category == "C2":
                best_category = "C1"

    return best_category








