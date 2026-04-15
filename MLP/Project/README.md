# 📝 Comment Category Prediction Challenge

[![Kaggle](https://img.shields.io/badge/Kaggle-Competition-blue?logo=kaggle&style=flat-square)](https://www.kaggle.com/t/29651a586efd4d448941ba6fa5561e32)
[![Python](https://img.shields.io/badge/Python-3.8+-yellow?logo=python&style=flat-square)](#)
[![Machine Learning](https://img.shields.io/badge/ML-Classification-green?style=flat-square)](#)

- Kaggle Competition: **Comment Category Prediction Challenge** (2026t1)
- Link: [https://www.kaggle.com/t/29651a586efd4d448941ba6fa5561e32](https://www.kaggle.com/t/29651a586efd4d448941ba6fa5561e32)

## 📌 Project Overview
This project focuses on building a robust predictive model to categorize user-generated comments on an online platform. By analyzing textual, numerical, and categorical features, the goal is to accurately determine the final category assigned to each comment.

The challenge involves handling large-scale data, text preprocessing, and implementing advanced classification algorithms to uncover patterns across metadata and symbolic expressions.

---

## 📊 Dataset Description
The dataset includes metadata such as:
- **Interaction Feedback:** Upvotes, system signals.
- **Symbolic Expressions:** Emoticons and internal symbolic indicators.
- **Textual Content:** The raw user comments.
- **Demographic/Topic Indicators:** Reference indicators like gender, race, religion, etc.

**Task:** Categorize comments into one of 4 distinct classes (`label`).

---

## 🛠 Tech Stack
- **Data Analysis:** `Pandas`, `NumPy`
- **Visualization:** `Matplotlib`, `Seaborn`, `WordCloud`
- **Machine Learning:** `Scikit-learn`, `XGBoost`, `LightGBM`
- **NLP:** `TfidfVectorizer`, `NLTK`, `Regex`
- **Utilities:** `Joblib` (model persistence), `Timer` (custom performance tracking)

---

## 🚀 Methodology
1. **Exploratory Data Analysis (EDA):**
   - Analyzing class distributions (58% majority class).
   - Identifying missing values and data types.
   - Feature engineering (e.g., `total_emoticons`, text lengths).
2. **Preprocessing:**
   - Handling missing values in categorical fields.
   - Text cleaning (lowercase, punctuation removal, stop-word filtering).
   - TF-IDF vectorization with n-grams (1,2) for capturing context.
3. **Modeling:**
   - Evaluated multiple models: Logistic Regression, XGBClassifier, and LGBMClassifier.
   - Hyperparameter tuning using `RandomizedSearchCV`.
4. **Evaluation:**
   - Metrics used: **Accuracy**, **F1-Score**, **Classification Report**, and **Confusion Matrix**.

---

## 📂 Repository Structure
```text
Project/
├── 24f2009339-notebook-t12026.ipynb  # Main exploration & modeling notebook
└── README.md                          # Project documentation
```

---

## 🏆 Key Findings
- **Vocabulary Size:** ~171,000 unique tokens identified after preprocessing.
- **Feature Engineering:** Combining emoticon counts and text metadata significantly improved model performance.
- **Model Choice:** Gradient Boosting models (LGBM/XGB) outperformed linear baselines in handling the non-linear relationships within the metadata.

---
*Developed as part of the MLP Course Project (IIT Madras BS Degree).*
