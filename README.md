# Aviator Prediction ML Project

## Overview

This project was developed as part of a **self–directed 100-day learning bootcamp** focused on practical software engineering, data collection, and machine learning experimentation.

The goal of the project was to explore whether historical data from the **popular gambling game "Aviator"** could be used to train machine learning models capable of predicting future outcomes.

The project involved:

* Collecting live game data from the web
* Storing and managing the data in a relational database
* Training supervised machine learning models
* Evaluating model performance using RMSE

The final dataset contains **10,000+ rows of collected data**, which were used for training and testing multiple models.

**Note**:This project is intended **for educational and experimental purposes only**. It does not guarantee accurate predictions and should not be used for gambling decisions.

---

## Learning Goals

This project was designed to practice and combine several real-world skills:

* Web data extraction using **JavaScript**
* Backend scripting with **Python**
* Database management with an **RDBMS**
* Machine Learning experimentation
* Model evaluation and comparison
* Handling real-world datasets

---

## Data Collection

Game data was collected directly from the **HTML content visible in the browser's Developer Tools**.

A **JavaScript script** extracted relevant information from the web page.
The data was then passed to a **Python backend script**, which processed and stored it in a relational database.

The final dataset contains:

* **10,000+ game records**
* Stored in an `Aviator_tracker1.accdb` database file

---

## Machine Learning Pipeline

After collecting enough data, a machine learning pipeline was implemented.

Steps included:

1. Loading the dataset from the database
2. Cleaning and preparing the data
3. Splitting the dataset into:

   * **Training data**
   * **Testing data**
4. Training several **Supervised Machine Learning algorithms**
5. Evaluating performance using **Root Mean Squared Error (RMSE)**

Different models were tested to compare prediction performance.

---

## Model Performance

Three different model versions were trained and stored in the repository.

| Model Version | RMSE Score |
| ------------- | ---------- |
| Model V1      | 7.3        |
| Model V2      | **5.7**    |
| Model V3      | 13.8       |

The **best performing model achieved an RMSE of approximately 5.7 during experimentation**, demonstrating the most promising predictive behavior at the time of testing.

---

## Repository Structure

```
Confy_Aviator_predictor
│
├── Avi_model versions/
│   ├── Avi_model7.3_v1
│   ├── Avi_model5.7_v2
│   └── Avi_model13.8v3
│
├── Avi_Trainer.ipynb
│   Notebook used for training and evaluating the ML models
│
├── Aviator_tracker1.accdb
│   Relational database containing 10,000+ rows of collected game data
│
├── app.py
│   Python backend responsible for storing incoming data from the Avi_fetch.js script
│
└── README.md
```

---

## Technologies Used

* **Python**
* **JavaScript**
* **Machine Learning (Supervised Learning)**
* **Relational Database (RDBMS)**
* **Jupyter Notebook**
* **Browser Developer Tools (HTML extraction)**

---

## How the System Works

1. JavaScript extracts live data from the web page HTML.
2. The data is passed to a Python backend script.
3. Python processes and stores the data inside a relational database.
4. The stored dataset is used to train machine learning models.
5. The models are evaluated using RMSE to measure prediction accuracy.

---

## Future Improvements

Possible improvements to this project include:

* Expanding the dataset with more collected rounds
* Trying additional ML algorithms(Unsupervised)
* Feature engineering for better predictive signals
* Real-time prediction pipeline
* Automated data collection pipeline

---

## Author

**Confiance(Confy-Code)**

This project was built during a **100-day self-directed learning bootcamp** focused on deepening practical skills in programming, data engineering, and machine learning.

---

## Disclaimer

This repository is a **technical experiment and educational project**.
It does **not guarantee the prediction of gambling outcomes** and should not be relied upon for financial decisions.

```tree```
