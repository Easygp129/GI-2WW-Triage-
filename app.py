import streamlit as st

def lower_gi_triage():
    def initial_presentation():
        st.header("Q1. Initial Presentation (Symptoms Check)")
        symptoms = {
            1: "Abdominal mass",
            2: "Change of bowel habit",
            3: "Unexplained weight loss",
            4: "Unexplained rectal bleeding",
            5: "Unexplained abdominal pain",
            6: "Iron-deficiency anaemia (IDA)",
            7: "Anaemia (in the absence of IDA)",
            8: "Incidental finding",
            9: "Rectal mass (FIT not required)",
            10: "Unexplained anal mass (FIT not required)",
            11: "Unexplained anal ulceration (FIT not required)"
        }
        selected = st.multiselect(
            "Which of the following symptom(s) does the patient have?",
            options=list(symptoms.keys()),
            format_func=lambda x: symptoms[x]
        )
        return selected

    def fit_test_status(key_suffix='_all'):
        st.header("Q2. Has the patient had a FIT test done?")
        fit_done = st.radio("Has a FIT test been performed?", ["Yes", "No"], key=f"fit_done_unique_{key_suffix}") == "Yes"

        fit_value, ferritin_done = None, None
        if fit_done:
            fit_value = st.number_input("Enter the FIT test result:", min_value=0, step=1, key=f"fit_value_unique_{key_suffix}")
            ferritin_done = st.radio("Is ferritin level available?", ["Yes", "No"], key=f"ferritin_done_unique_{key_suffix}") == "Yes"

        return fit_done, fit_value, ferritin_done

    def rectal_anal_mass_pathway(key_suffix='dynamic_suffix'):
        st.header("Q2A. (SPECIAL) Rectal/Anal Mass or Ulceration Sub-Pathway")
        suitable_fos = st.radio(
            "The patient has a rectal or anal mass, or anal ulceration. Are they suitable for urgent Flexible Sigmoidoscopy (FOS)?",
            ["Yes", "No"],
            key=f"suitable_fos_unique_{key_suffix}"
        ) == "Yes"

        if suitable_fos:
            st.write("Perform urgent FOS.")
            st.write("After FOS, manage based on findings. If NAD, refer back to Primary Care.")
        else:
            st.write("Consider Clinical Endoscopist Telephone Triage or urgent CR OPA if indicated.")

        return "End of rectal/anal mass pathway"

    def fit_below_10_pathway(key_suffix='_all'):
        st.header("Q2B. FIT <10 or No Ferritin Pathway")
        return_referrer = st.radio(
            "FIT <10 (or missing ferritin). Do you want to return to referrer?",
            ["Yes", "No"],
            key=f"return_referrer_unique_{key_suffix}"
        ) == "Yes"

        if return_referrer:
            st.write("Send template letter to Primary Care advising:")
            st.write("- Repeat FIT test")
            st.write("- NSS pathway (non-specific symptoms)")
            st.write("- If symptoms persist, referral via routine pathway")
        else:
            st.write("Consider local exceptions or reason to proceed.")

        return "End of FIT <10 pathway"

    def fit_above_10_pathway(fit_value, key_suffix='_all'):
        st.header("Q3. Patient with FIT >=10")
        high_risk = st.radio(
            "Does the patient have WHO performance status 3/4, significant comorbidities/dementia, or are they >=80 years old?",
            ["Yes", "No"],
            key=f"high_risk_unique_{key_suffix}"
        ) == "Yes"

        if high_risk:
            st.write("Perform telephone triage. Assess suitability for endoscopy or imaging.")
            return "High-risk group triaged"
        else:
            if fit_value >= 100:
                st.write("FIT >=100. Recommend colonoscopy.")
                return "Colonoscopy pathway"
            else:
                st.write("FIT 10-99. Proceed to age- and symptom-based investigations.")
                return "FIT 10-99 pathway"

    def age_symptom_triage(key_suffix='_all'):
        st.header("Q4A. FIT 10–99 & Age/Symptom Sub-Pathway")
        age = st.number_input("Enter the patient's age:", min_value=0, step=1, key=f"age_unique_{key_suffix}")
        rectal_bleeding = st.radio("Does the patient have rectal bleeding?", ["Yes", "No"], key=f"rectal_bleeding_unique_{key_suffix}") == "Yes"

        if age < 40 and not rectal_bleeding:
            st.write("Offer Colon Capsule. If not suitable, proceed to colonoscopy.")
        elif 40 <= age <= 59 and rectal_bleeding:
            st.write("Book colonoscopy.")
        elif age >= 60 and rectal_bleeding:
            st.write("Book CTC or colonoscopy based on clinical judgment.")
        elif age >= 60 and not rectal_bleeding:
            st.write("Colonoscopy is first choice. If not suitable, book CTC.")
        else:
            st.write("Check local guidelines or consider alternative pathways.")

        return "End of age/symptom triage"

    # Main logic
    st.title("Lower GI 2WW Triage Pathway")

    symptoms = initial_presentation()

    if 9 in symptoms or 10 in symptoms or 11 in symptoms:
        st.subheader("All Questions")
        fit_test_status(key_suffix='symptoms')
        rectal_anal_mass_pathway(key_suffix='symptoms')
        fit_below_10_pathway(key_suffix='symptoms')
        fit_above_10_pathway(fit_value=0, key_suffix='symptoms')  # Replace with an actual value if available
        age_symptom_triage(key_suffix='symptoms')

        result = rectal_anal_mass_pathway(key_suffix='symptoms')
        st.success(result)
        return

    if 1 in symptoms:
        st.write("Note: CT required at PTL (if no index CT) once colonic investigation is complete or if clinically indicated.")

    if 6 in symptoms:
        st.write("Note: OGD required at PTL once colonic investigation is complete or if clinically indicated.")

    fit_done, fit_value, ferritin_done = fit_test_status(key_suffix='main')

    if not fit_done or (fit_value is not None and fit_value < 10):
        result = fit_below_10_pathway(key_suffix='main')
        st.success(result)
        return

    if fit_value is not None and fit_value >= 10:
        result = fit_above_10_pathway(fit_value, key_suffix='main')
        st.success(result)
        return

    st.success("Triage pathway complete. Refer back to local guidelines if unclear.")

if __name__ == "__main__":
    lower_gi_triage()
