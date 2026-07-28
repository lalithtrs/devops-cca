import os
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODEL_DIR = os.path.join(BASE_DIR, 'models')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

DATASET_FILE = os.path.join(DATA_DIR, 'dataset.csv')
MODEL_FILE = os.path.join(MODEL_DIR, 'linear_model.pkl')
PIPELINE_FILE = os.path.join(MODEL_DIR, 'pipeline.joblib')

FEATURE_COLS = [
    'study_time_hours', 'attendance_percent', 'sleep_hours',
    'gender', 'parental_education', 'internet_access',
    'extracurricular_activities', 'part_time_job'
]

CATEGORICAL_MAP = {
    'gender': ['Female', 'Male'],
    'parental_education': ['Bachelors', 'High School', 'Masters', 'None', 'PhD'],
    'internet_access': ['No', 'Yes'],
    'extracurricular_activities': ['No', 'Yes'],
    'part_time_job': ['No', 'Yes']
}

def preprocess_df(df_input):
    df_copy = df_input.copy()
    for col, cat_list in CATEGORICAL_MAP.items():
        if col in df_copy.columns:
            df_copy[col] = pd.Categorical(df_copy[col], categories=cat_list)
    dummies = pd.get_dummies(df_copy[FEATURE_COLS], columns=list(CATEGORICAL_MAP.keys()), drop_first=True)
    return dummies

def train_and_save_pipeline():
    if not os.path.exists(DATASET_FILE):
        raise FileNotFoundError(f"{DATASET_FILE} not found")

    df = pd.read_csv(DATASET_FILE)
    df = df.fillna('None')

    # Check categories from data
    for col in CATEGORICAL_MAP.keys():
        unique_vals = sorted([str(x) for x in df[col].unique()])
        CATEGORICAL_MAP[col] = sorted(list(set(CATEGORICAL_MAP[col] + unique_vals)))

    X_dummies = preprocess_df(df)
    dummy_columns = X_dummies.columns.tolist()
    y = df['final_exam_score'].astype(float)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_dummies)

    model = LinearRegression()
    model.fit(X_scaled, y)

    y_pred = model.predict(X_scaled)
    r2 = r2_score(y, y_pred)
    mae = mean_absolute_error(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))

    pipeline_data = {
        'model': model,
        'scaler': scaler,
        'dummy_columns': dummy_columns,
        'feature_cols': FEATURE_COLS,
        'categorical_map': CATEGORICAL_MAP,
        'metrics': {
            'r2': round(float(r2), 4),
            'mae': round(float(mae), 2),
            'rmse': round(float(rmse), 2),
            'total_samples': len(df)
        }
    }

    joblib.dump(pipeline_data, PIPELINE_FILE)
    joblib.dump(model, MODEL_FILE)
    print(f"Model and pipeline successfully saved. R2: {r2:.4f}, MAE: {mae:.2f}")
    return pipeline_data

def load_pipeline():
    if os.path.exists(PIPELINE_FILE):
        try:
            return joblib.load(PIPELINE_FILE)
        except Exception:
            return train_and_save_pipeline()
    else:
        return train_and_save_pipeline()

def predict_student_score(input_data):
    """
    input_data: dict containing student attributes
    """
    pipeline = load_pipeline()
    model = pipeline['model']
    scaler = pipeline['scaler']
    dummy_columns = pipeline['dummy_columns']

    # Default missing fields safely
    clean_input = {
        'study_time_hours': float(input_data.get('study_time_hours', 4.0)),
        'attendance_percent': float(input_data.get('attendance_percent', 85.0)),
        'sleep_hours': float(input_data.get('sleep_hours', 7.0)),
        'gender': str(input_data.get('gender', 'Male')),
        'parental_education': str(input_data.get('parental_education', 'Bachelors')),
        'internet_access': str(input_data.get('internet_access', 'Yes')),
        'extracurricular_activities': str(input_data.get('extracurricular_activities', 'Yes')),
        'part_time_job': str(input_data.get('part_time_job', 'No'))
    }

    input_df = pd.DataFrame([clean_input])
    input_dummies = preprocess_df(input_df)
    scaled_input = scaler.transform(input_dummies)

    raw_prediction = float(model.predict(scaled_input)[0])
    predicted_score = round(max(0.0, min(100.0, raw_prediction)), 2)

    # Determine letter grade
    if predicted_score >= 90:
        grade = 'A'
        status = 'Excellent'
        badge_color = 'emerald'
    elif predicted_score >= 80:
        grade = 'B'
        status = 'Good'
        badge_color = 'blue'
    elif predicted_score >= 70:
        grade = 'C'
        status = 'Satisfactory'
        badge_color = 'amber'
    elif predicted_score >= 60:
        grade = 'D'
        status = 'Needs Improvement'
        badge_color = 'orange'
    else:
        grade = 'F'
        status = 'At Risk'
        badge_color = 'rose'

    # Compute Feature Contributions (Coefficient * Standardized Value)
    coefs = model.coef_
    means = scaler.mean_
    stds = scaler.scale_
    feature_vals = input_dummies.iloc[0].values

    contributions = {}
    for col_name, coef, val, mean, std in zip(dummy_columns, coefs, feature_vals, means, stds):
        standardized_val = (val - mean) / std
        impact = coef * standardized_val
        contributions[col_name] = round(float(impact), 2)

    # Generate targeted recommendations
    recommendations = []
    if clean_input['study_time_hours'] < 5.0:
        boost = round(min(100 - predicted_score, (5.0 - clean_input['study_time_hours']) * 3.5), 1)
        recommendations.append({
            'type': 'study_time',
            'title': 'Increase Weekly Study Hours',
            'desc': f"Increasing study time to 5.0+ hrs/day could boost exam score by approximately +{boost} points.",
            'priority': 'high' if clean_input['study_time_hours'] < 3.0 else 'medium'
        })
    if clean_input['attendance_percent'] < 90.0:
        boost = round(min(100 - predicted_score, (90.0 - clean_input['attendance_percent']) * 0.25), 1)
        recommendations.append({
            'type': 'attendance',
            'title': 'Improve Class Attendance',
            'desc': f"Boosting attendance to 90%+ could add up to +{boost} points to your final score.",
            'priority': 'high' if clean_input['attendance_percent'] < 80.0 else 'medium'
        })
    if clean_input['sleep_hours'] < 7.0:
        recommendations.append({
            'type': 'sleep',
            'title': 'Optimize Sleep Schedule',
            'desc': "Getting 7.5 - 8 hours of sleep improves focus and memory retention during exams.",
            'priority': 'medium'
        })
    if clean_input['part_time_job'] == 'Yes' and clean_input['study_time_hours'] < 4.0:
        recommendations.append({
            'type': 'work_balance',
            'title': 'Balance Part-time Work & Study',
            'desc': "Students working part-time perform significantly better when reserving dedicated study blocks.",
            'priority': 'medium'
        })

    if not recommendations:
        recommendations.append({
            'type': 'maintain',
            'title': 'Keep Up the Outstanding Routine',
            'desc': "Your habits align strongly with top-tier academic performance!",
            'priority': 'low'
        })

    return {
        'predicted_score': predicted_score,
        'grade': grade,
        'status': status,
        'badge_color': badge_color,
        'inputs': clean_input,
        'contributions': contributions,
        'recommendations': recommendations
    }

def get_dataset_analytics():
    if not os.path.exists(DATASET_FILE):
        return {}

    df = pd.read_csv(DATASET_FILE)
    
    # Grade distribution
    grade_counts = df['final_grade'].value_counts().to_dict()
    
    # Study time vs Avg Score
    df['study_bin'] = pd.cut(df['study_time_hours'], bins=[0, 2, 4, 6, 10], labels=['0-2h', '2-4h', '4-6h', '6h+'])
    study_avg = df.groupby('study_bin', observed=False)['final_exam_score'].mean().round(2).to_dict()

    # Attendance vs Avg Score
    df['att_bin'] = pd.cut(df['attendance_percent'], bins=[50, 75, 85, 95, 100], labels=['50-75%', '75-85%', '85-95%', '95-100%'])
    att_avg = df.groupby('att_bin', observed=False)['final_exam_score'].mean().round(2).to_dict()

    # Part time job vs Avg score
    job_avg = df.groupby('part_time_job')['final_exam_score'].mean().round(2).to_dict()

    # Gender vs Avg Score
    gender_avg = df.groupby('gender')['final_exam_score'].mean().round(2).to_dict()

    pipeline = load_pipeline()
    metrics = pipeline.get('metrics', {})

    return {
        'total_students': len(df),
        'avg_score': round(float(df['final_exam_score'].mean()), 2),
        'min_score': round(float(df['final_exam_score'].min()), 2),
        'max_score': round(float(df['final_exam_score'].max()), 2),
        'grade_distribution': grade_counts,
        'study_vs_score': study_avg,
        'attendance_vs_score': att_avg,
        'job_vs_score': job_avg,
        'gender_vs_score': gender_avg,
        'metrics': metrics
    }

if __name__ == '__main__':
    train_and_save_pipeline()
