<div align="center">

# 💧 Aquapure
**Advanced Machine Learning for Water Potability Analysis**

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-LightGray?logo=flask)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-F7931E?logo=scikit-learn)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

</div>

## 🚀 About the Project
**Aquapure** is a robust, data-driven web application engineered to determine water potability through advanced machine learning techniques. It processes various chemical and physical water quality parameters to provide real-time, accurate safety assessments for public health and environmental monitoring.

## ✨ Key Features
* **Intelligent Prediction:** Utilizes a trained ensemble model to classify water samples with high precision.
* **Interactive Dashboard:** A clean, responsive frontend interface for seamless user input.
* **Predictive Analytics:** Analyzes multiple input variables simultaneously to calculate potability.
* **History Tracking:** Securely stores past predictions in a local SQLite database for future analysis.

## 🛠️ Technical Stack
* **Machine Learning:** Built with `Scikit-learn`, employing ensemble methods to boost prediction accuracy.
* **Backend:** Powered by `Flask` for handling model inference and API requests.
* **Frontend:** Developed using `HTML5`, `Tailwind CSS`, and `JavaScript` for a modern, responsive user experience.
* **Data Persistence:** Uses `SQLite` for local storage of interaction history.

## 🧠 How it Works
1. **Data Input:** The frontend collects chemical parameters (Hardness, Solids, pH, etc.).
2. **Inference:** The data is sent to the Flask backend, where it is passed through the pre-trained ML model.
3. **Prediction:** The model returns a classification (Potable/Not Potable) and a confidence score.
4. **Storage:** The result is saved into `history.db` for record-keeping.

## ⚙️ How to Run
1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Imtishal-Abid/Aquapure.git](https://github.com/Imtishal-Abid/Aquapure.git)
