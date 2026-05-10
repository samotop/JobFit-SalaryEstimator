from pipeline.extractor import extract_text
from pipeline.classifier import classify_cv
from pipeline.weights import get_weights
from pipeline.scorer import score_cv
from pipeline.scraper import scrape_salary
from pipeline.salary import estimate_salary
from pipeline.explainer import explain_cv
from logger import logger
import asyncio


async def run_pipeline(file_path: str):
    try:
        logger.info(f"Pipeline spustená pre súbor: {file_path}")

        cv_text = extract_text(file_path)
        logger.info("Text úspešne extrahovaný z CV")

        classification = await classify_cv(cv_text)
        logger.info(f"Klasifikácia: {classification.category} / {classification.position}")

        weights = await get_weights(classification.category, classification.position)
        logger.info("Váhy načítané")

        cv_scores, seniority_score = await score_cv(cv_text, weights)
        logger.info(f"Seniority skóre: {seniority_score}/100")

        salary_data = await scrape_salary(classification.category, classification.position)
        logger.info(f"Trhový plat: {salary_data['salary']['min']} - {salary_data['salary']['max']} CZK")

        salary = estimate_salary(salary_data["salary"], seniority_score)
        logger.info(f"Odhadovaný plat: {salary['estimated_min']} - {salary['estimated_max']} CZK")

        explanation = await explain_cv(
            cv_text, classification.category, classification.position,
            cv_scores, weights, seniority_score, salary
        )
        logger.info("Pipeline dokončená")

        return classification, cv_scores, seniority_score, salary, explanation, weights

    except Exception as e:
        logger.error(f"Pipeline zlyhala: {e}")
        raise