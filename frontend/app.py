import streamlit as st
import requests
import base64
from PIL import Image
import io
import pandas as pd

API_URL = "http://localhost:8001"

st.set_page_config(
    page_title="AI Hematology Analyzer",
    page_icon="🩸",
    layout="wide"
)

st.title("🩸 AI Hematology Analyzer")
st.markdown("Automated Complete Blood Count (CBC) using YOLOv11 and FastAPI.")

# Sidebar for Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["New Scan", "Scan History"])

if page == "New Scan":
    st.header("Upload Microscopic Slide & Enter Lab Data")
    
    # 1. Patient Information
    with st.container(border=True):
        st.subheader("👤 Patient Information")
        c1, c2 = st.columns(2)
        patient_name = c1.text_input("Patient Name", placeholder="e.g. John Doe")
        blood_group = c2.selectbox("Blood Group", ["Unknown", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])

    # 2. Manual Lab Inputs (Organized by categories)
    st.subheader("🧪 Manual Lab Test Entry")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        with st.expander("⏱️ Coagulation & Hematology", expanded=True):
            pt = st.text_input("Prothrombin Time (PT)", placeholder="e.g. 12.5s")
            bt = st.text_input("Bleeding Time (BT)", placeholder="e.g. 3m")
            ct = st.text_input("Clotting Time (CT)", placeholder="e.g. 6m")
            esr = st.text_input("ESR", placeholder="e.g. 15 mm/hr")

    with col_b:
        with st.expander("🧬 Screening & Biochemistry", expanded=True):
            hiv = st.selectbox("HIV 1&2", ["Not Tested", "Non-Reactive", "Reactive"])
            hbsag = st.selectbox("HBsAG", ["Not Tested", "Non-Reactive", "Reactive"])
            rbs = st.text_input("Random Blood Sugar (RBS)", placeholder="e.g. 110 mg/dL")
            crp = st.text_input("CRP", placeholder="e.g. 5 mg/L")
            ferritin = st.text_input("Serum Ferritin", placeholder="e.g. 150 ng/mL")
            hba1c = st.text_input("HbA1C", placeholder="e.g. 5.7%")

    # 3. Slide Upload
    st.subheader("🔬 Microscopy (Automated CBC)")
    uploaded_file = st.file_uploader("Choose a blood slide image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        with col1:
            st.image(uploaded_file, caption='Uploaded Image', use_container_width=True)

        if st.button("Generate Comprehensive Report", type="primary"):
            with st.spinner("Processing image and compiling report..."):
                try:
                    # Construct Form Data
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    data = {
                        "patient_name": patient_name,
                        "blood_group": blood_group,
                        "pt": pt, "bt": bt, "ct": ct,
                        "hiv": hiv, "hbsag": hbsag,
                        "rbs": rbs, "crp": crp, "ferritin": ferritin,
                        "hba1c": hba1c, "esr": esr
                    }
                    
                    response = requests.post(f"{API_URL}/analyze", files=files, data=data)
                    
                    if response.status_code == 200:
                        report_data = response.json()
                        st.success("Analysis and Report Generation Complete!")
                        
                        # --- Display Comprehensive Report ---
                        st.header(f"🩸 Comprehensive Blood Report: {patient_name or 'Unnamed Patient'}")
                        
                        # Automated CBC Metrics
                        st.subheader("🔬 Automated Cell Count (CBC)")
                        counts = report_data.get("counts", {})
                        m_cols = st.columns(max(1, len(counts) if counts else 3))
                        if not counts:
                            st.info("No cells detected in this image.")
                        else:
                            for i, (cell_type, count) in enumerate(counts.items()):
                                m_cols[i % len(m_cols)].metric(label=f"{cell_type} Count", value=count)
                        
                        # Manual Lab Results
                        st.subheader("📋 Laboratory Findings")
                        lab = report_data.get("lab_results", {})
                        
                        tab1, tab2 = st.tabs(["Coagulation/Hematology", "Screening/Biochemistry"])
                        with tab1:
                            st.write(pd.DataFrame({
                                "Test": ["PT", "BT", "CT", "ESR"],
                                "Result": [lab.get('pt'), lab.get('bt'), lab.get('ct'), lab.get('esr')]
                            }))
                        with tab2:
                            st.write(pd.DataFrame({
                                "Test": ["HIV 1&2", "HBsAG", "RBS", "CRP", "Ferritin", "HbA1C"],
                                "Result": [lab.get('hiv'), lab.get('hbsag'), lab.get('rbs'), lab.get('crp'), lab.get('ferritin'), lab.get('hba1c')]
                            }))

                        st.markdown(f"**Diagnostic Analysis Summary**: {report_data.get('analysis', 'Normal')}")
                        
                        # Display Annotated Image
                        with col2:
                            if "annotated_image_base64" in report_data:
                                image_data = base64.b64decode(report_data["annotated_image_base64"])
                                image = Image.open(io.BytesIO(image_data))
                                st.image(image, caption="Annotated Image (YOLOv11 Detection)", use_container_width=True)
                        
                        if "db_warning" in report_data:
                            st.warning(report_data["db_warning"])
                    else:
                        st.error(f"Error from API: {response.text}")
                except Exception as e:
                    st.error(f"Failed to connect to the backend server. Error: {e}")

elif page == "Scan History":
    st.header("Previous Scan Reports")
    
    with st.spinner("Fetching historical reports..."):
        try:
            response = requests.get(f"{API_URL}/reports")
            if response.status_code == 200:
                reports = response.json()
                if not reports:
                    st.info("No reports found in the database.")
                else:
                    # Flatten the data for display including new fields
                    flattened = []
                    for r in reports:
                        lab = r.get('lab_results', {})
                        flat = {
                            "Date": r.get('timestamp', 'Unknown'),
                            "Patient": r.get('patient_name', 'Unknown'),
                            "Blood Group": r.get('blood_group', 'Unknown'),
                            "RBC": r.get('counts', {}).get('RBC', 0),
                            "WBC": r.get('counts', {}).get('WBC', 0),
                            "Platelets": r.get('counts', {}).get('Platelets', 0),
                            "HIV": lab.get('hiv', '-'),
                            "RBS": lab.get('rbs', '-'),
                            "HbA1C": lab.get('hba1c', '-'),
                            "Analysis": r.get('analysis', 'Normal')
                        }
                        flattened.append(flat)
                        
                    df = pd.DataFrame(flattened)
                    st.dataframe(df, use_container_width=True)
            else:
                 st.error("Could not fetch reports from the database.")
        except Exception as e:
            st.error(f"Failed to connect to the backend. Error: {e}")
