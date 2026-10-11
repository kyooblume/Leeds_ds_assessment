# 🇬🇧 UK Tourists in Japan — Spending & Behaviour Dashboard

**▶ Live demo:** https://uk-tourists-japan.streamlit.app

> Data science assessment, Leeds Trinity University (2025) · Python / Streamlit / Altair
> Data: Japan Tourism Agency, *Consumption Trend Survey for Foreigners Visiting Japan* (訪日外国人消費動向調査) — UK respondents n = 583, compared with all visitors

**TL;DR** — An interactive dashboard comparing UK visitors with all international visitors to Japan. UK visitors are **wealthier, stay longer, travel more for business and land mostly at Haneda** — and they buy **traditional crafts rather than cosmetics**. These insights point to premium, culture-focused, long-stay offers.

![Demographics & wealth](docs/screenshots/01_demographics.jpg)

---

## 1. Business question / 目的

Which strategic opportunities does the UK market offer for Japanese tourism businesses?
イギリス人訪日客は他国と比べてどんな特徴があり、どんな商品・サービスが刺さるのか。

## 2. Key findings / 主な発見 (UK vs all visitors)

| Theme | UK | All visitors | So what? |
|---|---:|---:|---|
| Household income ≥ $100k | **42%** | 25% | Wealthier → premium services |
| Net financial assets ≥ $1M | **13%** | 7% | |
| Stay of 7–20 days | **58%** | 37% | Long stays → multi-city / regional itineraries |
| Entry via Haneda | **66%** | 20% | Haneda is the natural gateway for UK campaigns |
| Business purpose (other business + corporate meeting) | **44%** | 26% | Business travellers → "bleisure" extensions |
| Buy traditional crafts | **20%** | 7% | Culture-led products sell |
| Buy cosmetics / perfume | 7% | **19%** | Cosmetics are not a UK hook |
| Use taxis | **41%** | 25% | Higher willingness to pay for convenience |

**Recommendations** — (1) target premium segments, (2) sell culture rather than cosmetics, (3) promote Haneda-based long-stay itineraries.

## 3. Dashboard

| Tab | Content |
|---|---|
| 1. Demographics & Wealth | Age, household income, net financial assets |
| 2. Purpose & Journey | Purpose of visit, entry airport, accommodation, companions, length of stay |
| 3. Detailed Expenditure | Participation rate by spending item, shopping, experiences |
| 4. Conclusions | Strategic recommendations |

<details><summary>More screenshots</summary>

![Purpose & journey](docs/screenshots/02_purpose_journey.jpg)
![Expenditure](docs/screenshots/03_expenditure.jpg)
![Conclusions](docs/screenshots/04_conclusions.jpg)

</details>

## 4. Data / データ

| File | Description |
|---|---|
| `summary_data.csv` | Visitor profile shares (%) — all visitors vs UK |
| `expenditure_data.csv` | Spending participation rate (%) and unit price (¥) — all vs UK |
| `formatted data.xlsx` | Source tables after formatting |

Source: Japan Tourism Agency (観光庁), *Consumption Trend Survey for Foreigners Visiting Japan*. Aggregated public statistics, reused with attribution in line with the publisher's terms of use (出典を明記して利用).

## 5. How to run / 実行方法

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 6. Limitations

- Survey-based aggregate shares; no individual-level data, so no statistical testing between groups.
- Income and asset questions have many "unknown / not stated" answers (UK 31–40%, all visitors 50–60%), so wealth comparisons are indicative.
- One survey period; seasonality and year-to-year change are not covered.

**Tech:** Python · Streamlit · pandas · Altair
