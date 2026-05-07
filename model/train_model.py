import pandas as pd
import joblib
import os
import numpy as np
import scipy.sparse as sp
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

print("=" * 55)
print("   SecurePass AI — Model Training (Master Level)")
print("=" * 55)

# ── Step 1: Load or Generate Dataset ──────────────────────
data_path = '../data/data.csv'

if os.path.exists(data_path):
    print("\n✅ data.csv found! Loading dataset...")
    df = pd.read_csv(data_path, on_bad_lines='skip').dropna()
    df['password'] = df['password'].astype(str)
    print(f"   Loaded {len(df):,} passwords from CSV")
else:
    print("\n⚠️  data.csv not found — Generating synthetic dataset...")
    print("   (This is normal — model will still work great!)\n")

    import random, string

    def make_weak():
        choices = [
            lambda: ''.join(random.choices(string.digits, k=random.randint(4,8))),
            lambda: ''.join(random.choices(string.ascii_lowercase, k=random.randint(4,7))),
            lambda: random.choice(['password','123456','qwerty','abc123',
                                   'letmein','welcome','monkey','dragon',
                                   'master','login','admin','pass','test']),
            lambda: ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(4,6))),
        ]
        return random.choice(choices)()

    def make_medium():
        choices = [
            lambda: ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(7,10))),
            lambda: random.choice(string.ascii_uppercase) + ''.join(random.choices(string.ascii_lowercase, k=5)) + str(random.randint(10,999)),
            lambda: ''.join(random.choices(string.ascii_letters, k=8)) + str(random.randint(100,9999)),
            lambda: ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(8,11))),
        ]
        return random.choice(choices)()

    def make_strong():
        sym = "!@#$%^&*"
        choices = [
            lambda: (''.join(random.choices(string.ascii_uppercase, k=random.randint(2,3)))
                     + ''.join(random.choices(string.ascii_lowercase, k=random.randint(4,6)))
                     + ''.join(random.choices(string.digits, k=random.randint(2,3)))
                     + ''.join(random.choices(sym, k=random.randint(2,3)))),
            lambda: ''.join(random.choices(string.ascii_letters + string.digits + sym, k=random.randint(14,20))),
            lambda: (''.join(random.choices(string.ascii_letters, k=10))
                     + ''.join(random.choices(string.digits, k=4))
                     + random.choice(sym) * 2),
        ]
        pw = random.choice(choices)()
        lst = list(pw); random.shuffle(lst)
        return ''.join(lst)

    print("   Generating 30,000 Weak passwords...")
    weak   = [(make_weak(),   0) for _ in range(30000)]
    print("   Generating 30,000 Medium passwords...")
    medium = [(make_medium(), 1) for _ in range(30000)]
    print("   Generating 30,000 Strong passwords...")
    strong = [(make_strong(), 2) for _ in range(30000)]

    all_data = weak + medium + strong
    random.shuffle(all_data)
    df = pd.DataFrame(all_data, columns=['password','strength'])

    os.makedirs('../data', exist_ok=True)
    df.to_csv(data_path, index=False)
    print(f"\n✅ Generated & saved {len(df):,} passwords to data/data.csv")

print(f"\n📊 Dataset Summary:")
print(f"   Total passwords : {len(df):,}")
vc = df['strength'].value_counts().sort_index()
labels = {0:'Weak', 1:'Medium', 2:'Strong'}
for k,v in vc.items():
    print(f"   {labels[k]:8s} ({k}) : {v:,}")

# ── Step 2: Sample if very large ──────────────────────────
np.random.seed(42)
sample_size = min(80000, len(df))
idx = np.random.choice(len(df), sample_size, replace=False)
X = df['password'].values[idx]
y = df['strength'].values[idx]
print(f"\n🔢 Using {sample_size:,} samples for training")

# ── Step 3: Feature Extraction ────────────────────────────
def extract_hand_features(passwords):
    feats = []
    for p in passwords:
        feats.append([
            len(p),
            sum(c.isupper() for c in p),
            sum(c.islower() for c in p),
            sum(c.isdigit() for c in p),
            sum(not c.isalnum() for c in p),
            len(set(p)),
            int(len(p) >= 12),
            int(len(p) >= 16),
        ])
    return np.array(feats)

print("\n📐 Step 1: TF-IDF Vectorization (char n-grams 1–3)...")
vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(1,3),
                              max_features=6000, sublinear_tf=True)
X_tfidf = vectorizer.fit_transform(X)

print("📐 Step 2: Extracting handcrafted features (8 features)...")
X_hand = sp.csr_matrix(extract_hand_features(X))

print("📐 Step 3: Combining both feature sets...")
X_all = sp.hstack([X_tfidf, X_hand])
print(f"   Final feature shape: {X_all.shape}")

# ── Step 4: Train/Test Split ──────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X_all, y, test_size=0.2, random_state=42, stratify=y)
print(f"\n📂 Train size : {X_train.shape[0]:,}")
print(f"   Test size  : {X_test.shape[0]:,}")

# ── Step 5: Train Model ───────────────────────────────────
print("\n🌲 Step 4: Training RandomForest (200 trees, balanced)...")
print("   Please wait — this takes ~1-2 minutes...\n")
model = RandomForestClassifier(
    n_estimators=200,
    n_jobs=-1,
    random_state=42,
    class_weight='balanced'
)
model.fit(X_train, y_train)

# ── Step 6: Evaluate ──────────────────────────────────────
y_pred = model.predict(X_test)
acc    = accuracy_score(y_test, y_pred)

print("=" * 55)
print(f"  ✅ MODEL ACCURACY : {acc*100:.2f}%")
print("=" * 55)
print()
print(classification_report(y_test, y_pred,
      target_names=['Weak','Medium','Strong']))

# ── Step 7: Save graphs ───────────────────────────────────
os.makedirs('../graphs', exist_ok=True)

# Confusion Matrix
print("📊 Saving Confusion Matrix graph...")
plt.figure(figsize=(7,5))
sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt='d',
            cmap='Blues', xticklabels=['Weak','Medium','Strong'],
            yticklabels=['Weak','Medium','Strong'])
plt.title(f'Confusion Matrix  (Accuracy: {acc*100:.2f}%)', fontsize=14)
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.tight_layout()
plt.savefig('../graphs/confusion_matrix.png', dpi=150)
plt.close()

# Strength Distribution Bar Chart
print("📊 Saving Strength Distribution graph...")
plt.figure(figsize=(6,4))
counts = [int((y==0).sum()), int((y==1).sum()), int((y==2).sum())]
colors = ['#ff4466','#ffcc33','#00cc66']
bars = plt.bar(['Weak','Medium','Strong'], counts, color=colors, edgecolor='white', linewidth=0.5)
for bar, count in zip(bars, counts):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 200,
             f'{count:,}', ha='center', va='bottom', fontweight='bold')
plt.title('Password Strength Distribution in Dataset', fontsize=13)
plt.ylabel('Number of Passwords')
plt.tight_layout()
plt.savefig('../graphs/strength_distribution.png', dpi=150)
plt.close()

# ── Step 8: Save Model ────────────────────────────────────
os.makedirs('../model', exist_ok=True)
joblib.dump(model,      '../model/password_strength_model.pkl')
joblib.dump(vectorizer, '../model/vectorizer.pkl')

print()
print("=" * 55)
print("  🎉 TRAINING COMPLETE!")
print("=" * 55)
print(f"  ✅ Accuracy        : {acc*100:.2f}%")
print(f"  ✅ Model saved     : model/password_strength_model.pkl")
print(f"  ✅ Vectorizer saved: model/vectorizer.pkl")
print(f"  ✅ Graphs saved    : graphs/")
print()
print("  Now run: streamlit run app.py")
print("=" * 55)
