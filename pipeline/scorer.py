from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from pipeline.weights import SectorWeights
load_dotenv()

RUBRIC = {
    "years_of_experience": {
        0: "žiadna prax",
        2: "menej ako 1 rok",
        4: "1-2 roky",
        6: "3-5 rokov",
        8: "5-8 rokov",
        10: "8+ rokov"
    },
    "education_level": {
        0: "žiadne vzdelanie",
        3: "základná škola",
        5: "stredná škola",
        7: "bakalár",
        9: "magister/inžinier",
        10: "PhD"
    },
    "role_seniority": {
        0: "žiadna prax",
        3: "stáž/brigáda",
        5: "junior pozície",
        7: "mid pozície",
        9: "senior pozície",
        10: "lead/manažérske pozície"
    },
    "skillset_relevance": {
        0: "žiadne relevantné skills",
        4: "málo relevantných skills",
        7: "pokrýva základné skills",
        9: "pokrýva väčšinu skills",
        10: "pokrýva všetky kľúčové skills"
    },
    "certifications": {
        0: "žiadne certifikáty",
        4: "jeden certifikát",
        7: "viac certifikátov",
        10: "množstvo relevantných certifikátov"
    },
    "language_skills": {
        0: "žiadny cudzí jazyk",
        3: "jeden jazyk základne A1-A2",
        6: "jeden jazyk dobre B1-B2",
        8: "jeden jazyk plynule C1-C2",
        10: "dva a viac jazykov plynule"
    },
    "project_scope": {
        0: "žiadne projekty",
        3: "malé interné projekty",
        6: "stredné projekty",
        8: "veľké projekty/korporáty",
        10: "medzinárodné projekty/enterprise"
    },
    "personality_traits": {
        0: "žiadne náznaky soft skills",
        4: "základné soft skills",
        7: "dobre viditeľné soft skills",
        10: "výrazné leadership a komunikačné schopnosti"
    }
}

class CVScores(BaseModel):
    years_of_experience: Optional[int] = None
    education_level: Optional[int] = None
    role_seniority: Optional[int] = None
    skillset_relevance: Optional[int] = None
    certifications: Optional[int] = None
    language_skills: Optional[int] = None
    project_scope: Optional[int] = None
    personality_traits: Optional[int] = None

def calculate_score(cv_scores: CVScores, weights: SectorWeights) -> float:
    total_score = 0
    total_weight = 0

    for factor in CVScores.model_fields:
        value = getattr(cv_scores, factor)
        weight = getattr(weights, factor)

        if value is None:
            continue

        total_score += value * weight
        total_weight += weight

    if total_weight == 0:
        return 0

    return round((total_score / total_weight) * 10, 1)

async def score_cv(cv_text: str, weights: SectorWeights) -> tuple[CVScores, float]:
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    parser = PydanticOutputParser(pydantic_object=CVScores)

    prompt = PromptTemplate(
        template="""
Si expert na HR. Na základe tohto CV ohodnoť každý faktor podľa rubriky.
Ak faktor nie je možné určiť z CV, vráť null.
Vráť iba JSON, nič iné.

RUBRIKA:
{rubric}

{format_instructions}

CV:
{cv_text}
        """,
        input_variables=["cv_text", "rubric"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | llm | parser
    cv_scores = chain.invoke({"cv_text": cv_text, "rubric": str(RUBRIC)})

    final_score = calculate_score(cv_scores, weights)
    return cv_scores, final_score