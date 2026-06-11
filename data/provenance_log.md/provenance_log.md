# Dataset Provenance Log

All datasets used in this project are documented here per open data best practice.
Update this file whenever a dataset is added or refreshed.

---

## 1. MoE Education Statistics Bulletin 2022

| Field | Value |
|---|---|
| **Source** | Zambia Ministry of Education — Directorate of Planning and Information |
| **Title** | Education Statistics Bulletin 2022 |
| **Access date** | May 2026 |
| **Format** | PDF (manually extracted to CSV) |
| **File** | `data/raw/moe_bulletin_2022.csv` |
| **Licence** | Public Government Document |
| **Tables used** | 1.4 (school counts), 2.1 (enrolment), 3.3 (dropout), 5.1–5.3 (teacher counts by year), 5.5 (PTR), 5.6 (qualified teachers), 5.7 (attrition totals), 5.8 (attrition by reason) |
| **Coverage** | All 10 provinces, primary and secondary, 2020–2022 |
| **SHA-256** | *(update after saving CSV)* |
| **Notes** | Values were manually extracted from the PDF bulletin. The Chongwe District is a sub-district of Lusaka Province — district-level data is proxied by Lusaka Province figures pending direct EMIS data access. |

---

## 2. UNESCO Institute for Statistics (UIS) — Zambia Time-Series

| Field | Value |
|---|---|
| **Source** | UNESCO Institute for Statistics |
| **URL** | http://data.uis.unesco.org |
| **Title** | Zambia Education Indicators 2010–2022 |
| **Access date** | May 2026 |
| **Format** | CSV export from UIS Data Browser |
| **File** | `data/raw/uis_zambia_2010_2022.csv` |
| **Licence** | Creative Commons Attribution (CC-BY) |
| **Indicators used** | PTRHC (pupil-teacher ratio), TRQUAL (qualified teachers %), NRST (teacher counts) |
| **Coverage** | National level, 2010–2022 |
| **SHA-256** | *(update after saving CSV)* |

---

## 3. Zambia LCMS 2022 (supplementary)

| Field | Value |
|---|---|
| **Source** | Zambia Central Statistical Office |
| **Title** | Living Conditions Monitoring Survey 2022 |
| **Access date** | May 2026 |
| **Format** | Public report |
| **Licence** | Public Government Document |
| **Use** | Contextual reference only — socioeconomic background for rural provinces. No LCMS variables are used as model features. |

---

## Update Instructions

When you add or refresh a dataset:

1. Save the file to `data/raw/`
2. Add a row here with source, access date, and licence
3. Generate SHA-256: `shasum -a 256 data/raw/your_file.csv`
4. Paste the hash in the SHA-256 field above
5. Commit the update to `provenance_log.md` (the CSV itself is gitignored)
