from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
load_dotenv()

class CVExplanation(BaseModel):
    score_explanation: str
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]

async def explain_cv(
    cv_text: str,
    category: str,
    position: str,
    cv_scores,
    weights,
    seniority_score: float,
    salary: dict
) -> CVExplanation:

    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    parser = PydanticOutputParser(pydantic_object=CVExplanation)

    prompt = PromptTemplate(
        template="""
Si expert na HR a kariérny poradca.

Na základe týchto dát vypracuj analýzu kandidáta.

POZÍCIA: {position}
KATEGÓRIA: {category}

SENIORITY SKÓRE: {seniority_score}/100
HODNOTENIE FAKTOROV:
{cv_scores}

VÁHY FAKTOROV PRE TENTO ODBOR:
{weights}

TRHOVÝ PLAT: {market_min} - {market_max} CZK
ODHADOVANÝ PLAT: {estimated_min} - {estimated_max} CZK

Vypracuj:
1. Vysvetlenie skóre - prečo také skóre dostal
2. Silné stránky kandidáta
3. Slabiny a gapy
4. Konkrétne odporúčania ako dosiahnuť +30% mzdy

Buď konkrétny, nie generický.
Odpovedaj výhradne v slovenčine.

{format_instructions}

CV:
{cv_text}
        """,
        input_variables=["cv_text", "category", "position", "cv_scores", "weights",
                        "seniority_score", "market_min", "market_max", "estimated_min", "estimated_max"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | llm | parser

    result = chain.invoke({
        "cv_text": cv_text,
        "category": category,
        "position": position,
        "cv_scores": cv_scores.model_dump(),
        "weights": weights.model_dump(),
        "seniority_score": seniority_score,
        "market_min": salary["market_min"],
        "market_max": salary["market_max"],
        "estimated_min": salary["estimated_min"],
        "estimated_max": salary["estimated_max"],
    })

    return result