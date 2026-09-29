import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, top_k_accuracy_score, classification_report


def inspect_and_train():
    # 1. Path resolution
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_path = os.path.join(base_dir, 'data', 'crop_recommendation.csv')
    if not os.path.exists(data_path):
        data_path = os.path.join(base_dir, 'data', 'crop_yield.csv')

    print("=" * 60)
    print("STEP 1: INSPECTING DATASET")
    print("=" * 60)
    print(f"Loading dataset from: {data_path}")
    
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset not found at {data_path}")

    df = pd.read_csv(data_path)

    # Clean whitespace from text columns
    for col in df.columns:
        if df[col].dtype == 'object' or pd.api.types.is_string_dtype(df[col]):
            df[col] = df[col].astype(str).str.strip()

    # Print dataset statistics
    total_rows, total_cols = df.shape
    col_names = df.columns.tolist()
    missing_vals = df.isnull().sum().to_dict()
    dup_count = int(df.duplicated().sum())

    print(f"Total Rows: {total_rows}")
    print(f"Total Columns: {total_cols}")
    print(f"Column Names: {col_names}")
    print("\nData Types:")
    for col, dtype in df.dtypes.items():
        print(f" - {col}: {dtype}")

    print("\nMissing Values per Column:")
    for col, m in missing_vals.items():
        print(f" - {col}: {m}")
    print(f"Duplicate Rows Count: {dup_count}")

    target_col = 'Crop'
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in dataset!")

    crop_classes = sorted(df[target_col].unique().tolist())
    num_classes = len(crop_classes)
    print(f"\nTarget Column: {target_col}")
    print(f"Number of Crop Classes: {num_classes}")
    print(f"Crop Classes: {crop_classes}")

    print("\nClass Distribution (Top 10 Most Frequent):")
    print(df[target_col].value_counts().head(10))

    # Feature segregation
    cat_features = ['Season', 'State']
    num_features = ['Area', 'Annual_Rainfall', 'Fertilizer', 'Pesticide']
    feature_cols = cat_features + num_features

    print("\nFeature Columns Used for Prediction:")
    print(f"Categorical Features: {cat_features}")
    print(f"Numerical Features: {num_features}")

    num_stats = {}
    print("\nNumerical Features Min/Max/Mean/Median:")
    for col in num_features:
        stat = {
            'min': float(df[col].min()),
            'max': float(df[col].max()),
            'mean': float(df[col].mean()),
            'median': float(df[col].median()),
            'q25': float(df[col].quantile(0.25)),
            'q75': float(df[col].quantile(0.75))
        }
        num_stats[col] = stat
        print(f" - {col}: min={stat['min']:.2f}, max={stat['max']:.2f}, mean={stat['mean']:.2f}, median={stat['median']:.2f}")

    seasons_list = sorted(df['Season'].unique().tolist())
    states_list = sorted(df['State'].unique().tolist())
    print(f"\nUnique Seasons ({len(seasons_list)}): {seasons_list}")
    print(f"Unique States ({len(states_list)}): {states_list}")

    print("\n" + "=" * 60)
    print("STEP 2: PREPARING DATA AND PREPROCESSING PIPELINE")
    print("=" * 60)

    # Clean dataset & avoid data leakage
    df_clean = df.dropna(subset=feature_cols + [target_col]).copy()
    if dup_count > 0:
        df_clean = df_clean.drop_duplicates(subset=feature_cols + [target_col])

    X = df_clean[feature_cols]
    y = df_clean[target_col]

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), num_features),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_features)
        ]
    )

    clf = RandomForestClassifier(
        n_estimators=120,
        max_depth=25,
        min_samples_split=4,
        min_samples_leaf=1,
        random_state=42,
        n_jobs=1
    )

    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', clf)
    ])

    print("Splitting dataset into 80% train and 20% test (Stratified)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print(f"Training Samples: {len(X_train)}")
    print(f"Testing Samples: {len(X_test)}")

    print("\n" + "=" * 60)
    print("STEP 3: TRAINING RANDOM FOREST CLASSIFIER")
    print("=" * 60)
    pipeline.fit(X_train, y_train)

    print("\n" + "=" * 60)
    print("STEP 4: MODEL EVALUATION")
    print("=" * 60)
    train_preds = pipeline.predict(X_train)
    test_preds = pipeline.predict(X_test)
    test_probs = pipeline.predict_proba(X_test)

    train_acc = accuracy_score(y_train, train_preds)
    test_acc = accuracy_score(y_test, test_preds)
    top3_acc = top_k_accuracy_score(y_test, test_probs, k=3, labels=pipeline.classes_)
    top5_acc = top_k_accuracy_score(y_test, test_probs, k=5, labels=pipeline.classes_)

    print(f"Actual Training Accuracy : {train_acc * 100:.2f}%")
    print(f"Actual Testing Accuracy  : {test_acc * 100:.2f}%")
    print(f"Actual Top-3 Accuracy    : {top3_acc * 100:.2f}%")
    print(f"Actual Top-5 Accuracy    : {top5_acc * 100:.2f}%")

    print("\nClassification Report (Sample Subset of Classes):")
    report = classification_report(y_test, test_preds, zero_division=0, output_dict=True)
    for c in crop_classes[:10]:
        if c in report:
            r = report[c]
            print(f" - {c:20s}: Precision={r['precision']:.2f}, Recall={r['recall']:.2f}, F1-score={r['f1-score']:.2f}, Support={int(r['support'])}")

    print("\n" + "=" * 60)
    print("STEP 5: SAVING MODEL AND METADATA")
    print("=" * 60)
    models_dir = os.path.join(base_dir, 'models')
    os.makedirs(models_dir, exist_ok=True)

    model_save_path = os.path.join(models_dir, 'crop_recommendation_model.pkl')
    joblib.dump(pipeline, model_save_path)
    print(f"Trained model saved successfully to: {model_save_path}")

    metadata = {
        'model_type': 'RandomForestClassifier (Pipeline)',
        'target_column': target_col,
        'feature_names': feature_cols,
        'categorical_features': cat_features,
        'numerical_features': num_features,
        'allowed_seasons': seasons_list,
        'allowed_states': states_list,
        'crop_classes': crop_classes,
        'num_classes': num_classes,
        'numerical_ranges': num_stats,
        'evaluation': {
            'train_accuracy': round(float(train_acc), 4),
            'test_accuracy': round(float(test_acc), 4),
            'top3_accuracy': round(float(top3_acc), 4),
            'top5_accuracy': round(float(top5_acc), 4)
        },
        'suitability_thresholds': {
            'high': 40.0,
            'moderate': 20.0,
            'low': 0.0
        },
        'alternative_labels': {
            'high': 'STRONG MATCH',
            'moderate': 'MODERATE MATCH',
            'fair': 'FAIR MATCH'
        }
    }

    metadata_path = os.path.join(models_dir, 'crop_model_metadata.json')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    print(f"Model metadata saved successfully to: {metadata_path}")
    print("Training script execution complete!")


if __name__ == '__main__':
    inspect_and_train()
