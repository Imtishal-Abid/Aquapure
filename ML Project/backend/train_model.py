# ── Imports ────────────────────────────────────────────────
import pandas as pd
import numpy as np
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, precision_recall_fscore_support
import pickle
import json
import os

# ── Load Dataset ───────────────────────────────────────────
df = pd.read_csv("dataset/water_potability.csv")

print("Shape:", df.shape)
print("Missing values:\n", df.isnull().sum())

# Fill missing values with column mean
df.fillna(df.mean(), inplace=True)

# Features and label
X = df.drop("Potability", axis=1)
y = df["Potability"]

print("\nClass distribution:\n", y.value_counts())

# ── Train/Test Split + Scaling ─────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

print("\nTrain size:", X_train_scaled.shape)
print("Test size: ", X_test_scaled.shape)

models = {
    "svm": SVC(kernel='rbf', C=1.0, gamma='scale', probability=True, random_state=42),
    "knn": KNeighborsClassifier(n_neighbors=5, metric='minkowski', p=2),
    "nn": MLPClassifier(hidden_layer_sizes=(100,), max_iter=500, random_state=42),
    "nb": GaussianNB()
}

metrics = {}
os.makedirs("models", exist_ok=True)

for name, model in models.items():
    print(f"\n=== Training {name.upper()} ===")
    model.fit(X_train_scaled, y_train)
    preds = model.predict(X_test_scaled)
    
    acc = accuracy_score(y_test, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, preds, average='weighted', zero_division=0)
    
    print(f"Accuracy: {round(acc * 100, 2)}%")
    print(classification_report(y_test, preds, zero_division=0))
    
    metrics[name] = {
        "accuracy": round(acc, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1score": round(f1, 4)
    }
    
    with open(f"models/{name}_model.pkl", "wb") as f:
        pickle.dump(model, f)

with open("models/scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)

with open("models/metrics.json", "w") as f:
    json.dump(metrics, f, indent=4)

print("\nAll models and metrics saved to models/")