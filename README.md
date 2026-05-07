# 🔐 SecurePass AI — Password Strength Analyzer

> An AI-powered password strength analyzer with ML model, encryption vault, and visual analytics.  
> College project — Graphic Era Hill University, Dehradun.

---

## 📌 About The Project

**SecurePass AI** is a smart password security tool that uses a **Machine Learning model** to analyze password strength in real-time. It features a password vault with **Fernet encryption**, visual analytics with Plotly charts, and a sleek dark UI built with Streamlit.

---

## ✨ Features

- 🔍 Real-time Password Strength Analysis (Weak / Medium / Strong)
- 🤖 ML Model — RandomForest Classifier (99.6% accuracy)
- 🔒 Password Vault with Fernet Encryption
- 📊 Visual Analytics — Confusion Matrix, Strength Distribution
- 🔑 Password Generator
- 🗄️ SQLite Database for secure storage
- 🖥️ Dark UI with custom Streamlit CSS

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit, Custom CSS |
| ML Model | Scikit-learn, RandomForest |
| Features | TF-IDF char n-grams + 8 handcrafted features |
| Encryption | Cryptography (Fernet) |
| Database | SQLite |
| Visualization | Plotly, Matplotlib, Seaborn |
| Libraries | Pandas, NumPy, SciPy |

---

## 🤖 Model Details

| Property | Value |
|----------|-------|
| Algorithm | RandomForest Classifier |
| Features | TF-IDF char n-grams (1-3) + 8 handcrafted features |
| Training samples | 80,000 passwords |
| Test Accuracy | **99.6%** |
| Classes | Weak (0), Medium (1), Strong (2) |

---

## 👨‍💻 About This Project

**Developed by: Umang Shaily**  
MCA Student — Graphic Era Hill University, Dehradun

- Built complete Streamlit web application with dark UI
- Trained ML model on 670K password dataset
- Implemented Fernet encryption for password vault
- Designed SQLite database schema
- Performed manual testing and bug fixing throughout

---

## 🚀 How To Run

### Requirements
- Python 3.8 or above
- pip

### Step 1 — Clone the repository
```bash
git clone https://github.com/umange12/securepass-ai.git
cd securepass-ai
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Train the ML model (first time only)
```bash
cd model
python train_model.py
cd ..
```

### Step 4 — Run the app
```bash
streamlit run app.py
```

### Step 5 — Open in browser
```
http://localhost:8501
```

---

## 📁 Project Structure

```
SecurePass_AI/
├── app.py                        # Main Streamlit application
├── requirements.txt              # Python dependencies
├── securepass.db                 # SQLite database
├── data/
│   └── data.csv                  # 670K password dataset
├── model/
│   ├── train_model.py            # Model training script
│   ├── password_strength_model.pkl  # Trained ML model
│   └── vectorizer.pkl            # TF-IDF vectorizer
└── graphs/
    ├── confusion_matrix.png      # Model evaluation graph
    └── strength_distribution.png
```

---

## 🧪 Test Cases (QA)

| Test Case | Input | Expected Output | Status |
|-----------|-------|-----------------|--------|
| TC-01: Weak password | "123456" | Strength: Weak | ✅ Pass |
| TC-02: Medium password | "Hello@123" | Strength: Medium | ✅ Pass |
| TC-03: Strong password | "X#9kL$mP2@nQ" | Strength: Strong | ✅ Pass |
| TC-04: Empty input | No password entered | Validation error | ✅ Pass |
| TC-05: Password vault save | Valid password entry | Encrypted & stored | ✅ Pass |
| TC-06: Password generator | Click generate | Random strong password generated | ✅ Pass |
| TC-07: Special chars only | "!@#$%^&*" | Strength analyzed correctly | ✅ Pass |

---

## 📄 License

Academic project — Graphic Era Hill University, Dehradun.  
Developer: Umang Shaily

---

## 🙋‍♂️ Contact

**Umang Shaily**  
📧 shailyumang59@gmail.com  
🔗 [GitHub](https://github.com/umange12)
