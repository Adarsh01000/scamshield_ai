import os
import sys

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

from src.data.url_dataset import DATASET
from src.agents.url_features import extract_url_features

def train_and_save_model(model_save_path: str = "src/models/url_classifier.joblib"):
    print("[1/4] Extracting features for dataset URLs...")
    rows = []
    labels = []
    
    for url, label in DATASET:
        feat_dict = extract_url_features(url)["features"]
        rows.append(feat_dict)
        labels.append(label)
        
    df = pd.DataFrame(rows)
    feature_names = list(df.columns)
    
    print(f"[2/4] Dataset size: {len(df)} samples ({labels.count(0)} legitimate, {labels.count(1)} scam/phishing)")
    
    # Train / test split (80 / 20) with stratification
    X_train, X_test, y_train, y_test = train_test_split(
        df, labels, test_size=0.20, random_state=42, stratify=labels
    )
    
    print("[3/4] Training Random Forest Classifier...")
    clf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    cm = confusion_matrix(y_test, y_pred)
    
    metrics = {
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1_score": round(float(f1), 4),
        "confusion_matrix": cm.tolist(),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "feature_importances": {
            feat: round(float(imp), 4)
            for feat, imp in zip(feature_names, clf.feature_importances_)
        }
    }
    
    print(f"--- URL Model Evaluation Results ---")
    print(f"Accuracy : {metrics['accuracy']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall   : {metrics['recall']:.4f}")
    print(f"F1-Score : {metrics['f1_score']:.4f}")
    print(f"Confusion Matrix (TN, FP / FN, TP):\n{cm}")
    
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    payload = {
        "model": clf,
        "feature_names": feature_names,
        "metrics": metrics
    }
    joblib.dump(payload, model_save_path)
    print(f"[4/4] Model artifact saved to: {model_save_path}")
    return metrics

if __name__ == "__main__":
    train_and_save_model()
