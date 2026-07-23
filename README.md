# Energy Sentinel

Energy Sentinel is an end-to-end machine learning project for monitoring household energy consumption and detecting abnormal appliance behavior using real smart meter data from the UK-DALE dataset.

This project demonstrates the full ML engineering lifecycle — from raw data ingestion and feature engineering to anomaly detection modeling, REST API development, and an interactive dashboard.

---

## Real World Relevance

Household energy monitoring is a growing problem. Smart meters generate continuous streams of appliance-level data that most households have no visibility into. Abnormal appliance behavior — a fridge running hotter than usual, a washing machine cycling more than expected — often goes unnoticed until the electricity bill arrives or the appliance fails.

Energy Sentinel addresses this by:

- Automatically learning what normal behavior looks like for each appliance
- Flagging deviations from that learned pattern in real time
- Assigning risk levels so households can prioritize which appliances to inspect
- Generating plain-language recommendations that are actionable without technical knowledge

This kind of system is directly applicable to smart home platforms, energy management services, and utility companies looking to offer value-added monitoring to their customers.

---

## What This Project Does

- Loads and processes real smart meter data (UK-DALE House 1)
- Engineers time-based, rolling, and daily features per appliance
- Trains per-appliance anomaly detection models using Isolation Forest
- Compares Isolation Forest against LOF and One-Class SVM
- Assigns risk levels (Low / Medium / High) based on anomaly scores
- Generates rule-based recommendations from anomaly results
- Exposes all results via a FastAPI REST backend
- Visualizes everything through a multi-page Streamlit dashboard
- Containerized with Docker Compose for reproducible deployment

---

## Dataset

**UK-DALE — UK Domestic Appliance-Level Electricity**

- Source: https://jack-kelly.com/data/
- House 1, low-frequency data (6-second intervals)
- Date range used: January 2013 — December 2013 (1 full year)
- Resampled to 1-minute intervals for analysis

**Appliances used:**

| Channel | Appliance       |
|---------|-----------------|
| 1       | Aggregate       |
| 5       | Washing Machine |
| 6       | Dishwasher      |
| 7       | TV              |
| 10      | Kettle          |
| 12      | Fridge          |
| 13      | Microwave       |

---

## Project Structure

```
energy-sentinel/
│
├── data/
│   ├── raw/                        # UK-DALE raw .dat files (gitignored)
│   └── processed/                  # Cleaned and resampled parquet files (gitignored)
│
├── notebooks/
│   ├── 01_eda.ipynb                # Exploratory data analysis
│   ├── 02_preprocessing.ipynb      # Data cleaning pipeline
│   ├── 03_feature_engineering.ipynb
│   └── 04_modeling.ipynb           # Anomaly detection and model comparison
│
├── src/
│   ├── config/settings.py          # Project-wide configuration (pydantic-settings)
│   ├── data/loader.py              # UK-DALE channel loader with validation
│   ├── preprocessing/cleaner.py    # Missing value handling and threshold cleaning
│   ├── features/builder.py         # Time, rolling, and daily feature engineering
│   ├── models/
│   │   ├── train.py                # Train Isolation Forest, LOF, One-Class SVM
│   │   └── predictor.py            # Load model bundle and run inference
│   ├── services/
│   │   ├── monitoring_service.py   # Energy summaries and trends
│   │   ├── health_service.py       # Anomaly detection and risk scoring
│   │   ├── analytics_service.py    # Usage patterns and peak hours
│   │   └── recommendation_service.py
│   ├── schemas/                    # Pydantic request/response schemas
│   ├── api/
│   │   ├── main.py                 # FastAPI app entrypoint
│   │   └── routes/                 # One route file per service
│   ├── db/
│   │   ├── models.py               # SQLAlchemy ORM models
│   │   └── session.py              # DB engine and session setup
│   └── utils/logger.py             # Centralized logging
│
├── dashboard/
│   ├── app.py                      # Streamlit home page
│   └── pages/
│       ├── 1_monitoring.py
│       ├── 2_appliance_health.py
│       ├── 3_analytics.py
│       └── 4_recommendations.py
│
├── artifacts/                      # Saved .joblib model files (gitignored)
├── tests/
├── docker-compose.yml
├── Dockerfile.api
├── Dockerfile.dashboard
├── requirements.txt
├── .env.example
└── pyproject.toml
```

---

## Machine Learning Approach

**Problem type:** Unsupervised anomaly detection — no fault labels exist in the dataset, so we detect deviations from learned normal behavior.

**Primary model:** Isolation Forest
- Trained per appliance on full 525,600 records (1-minute resolution, 2013)
- Contamination set to 5%
- Selected for speed, scalability, and no distributional assumptions

**Comparison models** (evaluated on 10,000-row sample):
- Local Outlier Factor
- One-Class SVM

**Features engineered per appliance:**
- Time features: hour of day, day of week, weekend indicator, month
- Rolling features (60-minute window): mean, std, max, min power
- Daily features: energy consumed (kWh), activity rate (% time ON), activation cycles

**Risk scoring:**
- Anomaly score > 0.0 → Low
- Anomaly score between -0.05 and 0.0 → Medium
- Anomaly score ≤ -0.05 → High

---

## Tech Stack

| Layer            | Technology                        |
|------------------|-----------------------------------|
| Data Processing  | pandas, numpy, pyarrow            |
| Machine Learning | scikit-learn, joblib              |
| API Backend      | FastAPI, uvicorn, pydantic        |
| Database         | PostgreSQL, SQLAlchemy            |
| Dashboard        | Streamlit, matplotlib, seaborn    |
| Containerization | Docker, Docker Compose            |
| Configuration    | pydantic-settings, python-dotenv  |

---

## Installation

**Prerequisites:** Python 3.10+, Git

**1. Clone the repository**
```bash
git clone https://github.com/md-faiyazkhan/energy-sentinel.git
cd energy-sentinel
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
pip install -e .
```

**4. Set up environment variables**
```bash
cp .env.example .env
```

Edit `.env` with your database credentials.

**5. Download UK-DALE data**

Download House 1 low-frequency data from:
https://data.ukedc.rl.ac.uk/simplebrowse/edc/efficiency/residential/EnergyConsumption/Domestic/UK-DALE-2017/UK-DALE-FULL-disaggregated

Place the extracted files at: `data/raw/house_1/`

---

## Usage

### Run Notebooks (in order)

```bash
jupyter notebook
```

1. `01_eda.ipynb` — Explore raw data
2. `02_preprocessing.ipynb` — Clean and save processed data
3. `03_feature_engineering.ipynb` — Build and save feature dataset
4. `04_modeling.ipynb` — Train models and save artifacts

### Run API

```bash
uvicorn src.api.main:app --reload
```

API available at: http://127.0.0.1:8000  
Swagger docs at: http://127.0.0.1:8000/docs

### Run Dashboard

```bash
streamlit run dashboard/app.py
```

Dashboard available at: http://localhost:8501

### Run with Docker Compose

```bash
docker-compose up --build
```

| Service   | URL                        |
|-----------|----------------------------|
| API       | http://localhost:8000      |
| Dashboard | http://localhost:8501      |
| Swagger   | http://localhost:8000/docs |

---

## API Endpoints

| Method | Endpoint                                  | Description                           |
|--------|-------------------------------------------|---------------------------------------|
| GET    | /monitoring/summary                       | Energy consumption summary            |
| GET    | /monitoring/monthly-trend                 | Monthly average power trend           |
| GET    | /monitoring/appliance-breakdown           | Energy per appliance in kWh           |
| GET    | /health/summary                           | Health status for all appliances      |
| GET    | /health/{appliance}                       | Detailed anomaly results per appliance|
| GET    | /analytics/hourly-pattern/{appliance}     | Average power by hour of day          |
| GET    | /analytics/weekday-vs-weekend/{appliance} | Weekday vs weekend comparison         |
| GET    | /analytics/peak-hour/{appliance}          | Peak usage hour                       |
| GET    | /analytics/daily-activity/{appliance}     | Daily activity rate                   |
| GET    | /recommendations/                         | Rule-based appliance recommendations  |

---

## Author

Md Faiyaz Khan  
GitHub: https://github.com/md-faiyazkhan
