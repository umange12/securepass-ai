# 🔐 SecurePass AI — MCA Practical Project

## Overview
SecurePass AI is an advanced password strength analyzer built with:
- **ML Model**: RandomForest Classifier (99.6% Accuracy)
- **Features**: TF-IDF char n-grams + handcrafted security features
- **Encryption**: Fernet symmetric encryption for vault
- **UI**: Streamlit with custom dark glassmorphism CSS

## How to Run

### Step 1: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Train the ML model (first time only)
```bash
cd model
python train_model.py
cd ..
```

### Step 3: Launch the app
```bash
streamlit run app.py
```

## Model Details
| Property | Value |
|---|---|
| Algorithm | RandomForest Classifier |
| Features | TF-IDF char n-grams (1-3) + 8 handcrafted features |
| Training samples | 80,000 passwords |
| Test Accuracy | 99.6% |
| Classes | Weak (0), Medium (1), Strong (2) |

## Project Structure
```
SecurePass_AI/
├── app.py               ← Main Streamlit app
├── requirements.txt     ← Python dependencies
├── README.md            ← This file
├── data/
│   └── data.csv         ← 670K password dataset
├── model/
│   ├── train_model.py   ← Model training script
│   ├── password_strength_model.pkl  ← Trained model
│   └── vectorizer.pkl   ← TF-IDF vectorizer
└── graphs/              ← Generated after training
    └── confusion_matrix.png
```
