# 💼 Job Fit & Salary Estimator

AI systém ktorý na základe CV vyhodnotí skúsenosti, zručnosti a senioritu kandidáta, odhadne tržnú mzdu a poskytne konkrétne odporúčania na kariérny rast.

## 🚀 Spustenie

### 1. Inštalácia
```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Nastavenie API kľúča
Vytvor súbor `.env` v root adresári:
```
OPENAI_API_KEY="API KEY"
```

### 3. Spustenie
```bash
python -m streamlit run app.py
```


## ⚙️ Ako funguje pipeline

1. Extrakcia textu z CV (PDF alebo DOCX)
2. Scraping zoznamu pozícií z platy.cz (len pri prvom spustení, potom cache)
3. Identifikácia odboru a pozície (LLM)
4. Načítanie váh pre odbor (cache alebo LLM)
5. Ohodnotenie CV podľa rubriky (LLM)
6. Výpočet seniority skóre (0–100)
7. Scraping tržného platu pre danú pozíciu z platy.cz
8. Výpočet salary estimate
9. Vysvetlenie a odporúčania (LLM)
## 📊 Výstup

- **Seniority Score** (0–100) – zložené z rokov praxe, vzdelania, seniority rolí, skillsetu, certifikátov, jazykov, rozsahu projektov a osobnostných rysov
- **Salary Estimate** – odhadovaný plat v CZK odvodený z reálnych dát z platy.cz
- **Vysvetlenie** – silné stránky, slabiny a konkrétne odporúčania na dosiahnutie +30% mzdy

## 📁 Štruktúra projektu

```
JobFit_SalaryEstimator/
├── app.py                  # Streamlit UI
├── main.py                 # Pipeline bez UI
├── logger.py               # Logovanie
├── pipeline/
│   ├── extractor.py        # Extrakcia textu z CV
│   ├── classifier.py       # Identifikácia odboru a pozície
│   ├── weights.py          # Váhy faktorov pre odbory
│   ├── scorer.py           # Scoring CV
│   ├── scraper.py          # Scraping platy.cz
│   ├── salary.py           # Výpočet salary estimate
│   └── explainer.py        # LLM vysvetlenie
├── data/
│   ├── positions.json      # Cache pozícií z platy.cz
│   └── weights.json        # Cache váh pre odbory
├── logs/
│   └── pipeline.log        # Logy
├── .env                    # API kľúč
└── requirements.txt
```

## 🗂️ Dáta

### positions.json
Obsahuje zoznam všetkých kategórií a pozícií z platy.cz. Pri prvom spustení sa automaticky vytvorí scrapeovaním zoznamu pozícií z platy.cz a uloží do cache. Pri každom ďalšom spustení sa načíta zo súboru.

### weights.json
Cache váh faktorov pre jednotlivé odbory a pozície generovaných LLM. Pri prvom spustení pre daný odbor a pozíciu sa váhy vygenerujú cez LLM a uložia do cache. Pri ďalšom spustení s rovnakou kombináciou sa načítajú zo súboru.
## 🔧 Technológie

- **Python** – hlavný jazyk
- **LangChain + OpenAI GPT-4o** – LLM pipeline
- **Playwright + playwright-stealth** – scraping platy.cz
- **Streamlit** – UI
- **pdfplumber + python-docx** – extrakcia textu z CV
- **Pydantic** – validácia výstupov

## 📝 Poznámky

- Systém podporuje CV v akomkoľvek jazyku
- Systém vyžaduje CV s dostatočným množstvom textu – skenované obrázky bez textu nie sú podporované.
- Výstupy sú v slovenčine
- Scraping platy.cz prebieha pri každom spustení pre aktuálne tržné dáta
- Váhy odborov sa cachujú – pri rovnakej kategórii a pozícii sa LLM nevolá znova
