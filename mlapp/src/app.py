import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from flask import Flask, render_template, request, jsonify
from model_pipeline import predict_student_score, get_dataset_analytics, load_pipeline

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)

# Ensure pipeline is loaded or trained at startup
try:
    load_pipeline()
    print("Model Pipeline initiated successfully.")
except Exception as e:
    print(f"Error loading pipeline: {e}")

PRESET_PROFILES = {
    'high_achiever': {
        'name': 'High Achiever',
        'icon': '🌟',
        'data': {
            'study_time_hours': 6.5,
            'attendance_percent': 98.0,
            'sleep_hours': 8.0,
            'gender': 'Female',
            'parental_education': 'Masters',
            'internet_access': 'Yes',
            'extracurricular_activities': 'Yes',
            'part_time_job': 'No'
        }
    },
    'average_student': {
        'name': 'Average Student',
        'icon': '📚',
        'data': {
            'study_time_hours': 3.5,
            'attendance_percent': 85.0,
            'sleep_hours': 7.0,
            'gender': 'Male',
            'parental_education': 'Bachelors',
            'internet_access': 'Yes',
            'extracurricular_activities': 'Yes',
            'part_time_job': 'No'
        }
    },
    'at_risk': {
        'name': 'At-Risk Student',
        'icon': '⚠️',
        'data': {
            'study_time_hours': 1.5,
            'attendance_percent': 65.0,
            'sleep_hours': 5.5,
            'gender': 'Male',
            'parental_education': 'High School',
            'internet_access': 'No',
            'extracurricular_activities': 'No',
            'part_time_job': 'Yes'
        }
    },
    'working_student': {
        'name': 'Working Student',
        'icon': '💼',
        'data': {
            'study_time_hours': 4.0,
            'attendance_percent': 88.0,
            'sleep_hours': 6.5,
            'gender': 'Female',
            'parental_education': 'High School',
            'internet_access': 'Yes',
            'extracurricular_activities': 'No',
            'part_time_job': 'Yes'
        }
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def api_predict():
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({'error': 'No input JSON provided'}), 400

        result = predict_student_score(data)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics', methods=['GET'])
def api_analytics():
    try:
        analytics = get_dataset_analytics()
        return jsonify({'success': True, 'data': analytics})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/presets', methods=['GET'])
def api_presets():
    return jsonify({'success': True, 'presets': PRESET_PROFILES})

@app.route('/api/health', methods=['GET'])
def api_health():
    try:
        pipeline = load_pipeline()
        return jsonify({
            'status': 'healthy',
            'model_type': 'LinearRegression',
            'metrics': pipeline.get('metrics', {}),
            'features': pipeline.get('feature_cols', [])
        })
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Flask ML Application on http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
