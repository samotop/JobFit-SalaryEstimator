import asyncio
import streamlit as st
from pipeline.extractor import extract_text
from pipeline.classifier import classify_cv
from pipeline.weights import get_weights
from pipeline.scorer import score_cv
from pipeline.scraper import scrape_salary
from pipeline.salary import estimate_salary
from pipeline.explainer import explain_cv
import tempfile
import os
from logger import logger

st.set_page_config(
    page_title="JobFit & Salary Estimator",
    page_icon="💼",
    layout="wide"
)

st.title("💼 JobFit & Salary Estimator")
st.markdown("Nahraj svoje CV a zisti svoje seniority skóre, odhadovaný plat a odporúčania na rast.")

uploaded_file = st.file_uploader("Nahraj CV (PDF alebo DOCX)", type=["pdf", "docx"])

if uploaded_file and st.button("Analyzovať CV", type="primary"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name


    async def run():
        with st.status("Analyzujem CV...", expanded=True) as status:
            st.write("📄 Extrahujem text z CV...")
            cv_text = extract_text(tmp_path)
            logger.info("Text úspešne extrahovaný z CV")

            st.write("🔍 Klasifikujem odbor a pozíciu...")
            classification = await classify_cv(cv_text)
            logger.info(f"Klasifikácia: {classification.category} / {classification.position}")

            st.write("⚖️ Načítavam váhy pre odbor...")
            weights = await get_weights(classification.category, classification.position)
            logger.info("Váhy načítané")

            st.write("📊 Hodnotím CV...")
            cv_scores, seniority_score = await score_cv(cv_text, weights)
            logger.info(f"Seniority skóre: {seniority_score}/100")

            st.write("💰 Scrapujem platy z platy.cz...")
            salary_data = await scrape_salary(classification.category, classification.position)
            logger.info(f"Trhový plat: {salary_data['salary']['min']} - {salary_data['salary']['max']} CZK")

            st.write("🧮 Počítam salary estimate...")
            salary = estimate_salary(salary_data["salary"], seniority_score)
            logger.info(f"Odhadovaný plat: {salary['estimated_min']} - {salary['estimated_max']} CZK")

            st.write("🧠 Generujem vysvetlenie...")
            explanation = await explain_cv(
                cv_text, classification.category, classification.position,
                cv_scores, weights, seniority_score, salary
            )
            logger.info("Pipeline dokončená")

            status.update(label="Analýza dokončená!", state="complete")
            return classification, cv_scores, seniority_score, salary, explanation, weights

    try:
        classification, cv_scores, seniority_score, salary, explanation, weights = asyncio.run(run())
    except Exception as e:
        logger.error(f"Pipeline zlyhala: {e}")
        st.error(f"Nastala chyba: {e}")
        st.stop()

    os.unlink(tmp_path)

    # VÝSLEDKY
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Pozícia", classification.position)
    with col2:
        st.metric("Seniority skóre", f"{seniority_score}/100")
    with col3:
        st.metric("Odhadovaný plat", f"{salary['estimated_min']:,} - {salary['estimated_max']:,} CZK")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💪 Silné stránky")
        for s in explanation.strengths:
            st.success(s)

        st.subheader("⚠️ Slabiny")
        for w in explanation.weaknesses:
            st.warning(w)

    with col2:
        st.subheader("🚀 Odporúčania na +30% mzdu")
        for r in explanation.recommendations:
            st.info(r)

    st.divider()
    st.subheader("📋 Vysvetlenie skóre")
    st.write(explanation.score_explanation)

    with st.expander("🔢 Detail hodnotenia faktorov"):
        scores = cv_scores.model_dump()
        weights_dict = weights.model_dump()
        for factor, value in scores.items():
            if value is not None:
                st.write(f"**{factor}**: {value}/10 (váha: {weights_dict[factor]})")