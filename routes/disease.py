import os
import uuid
import logging
from PIL import Image
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify, current_app
from werkzeug.utils import secure_filename
from models.database import get_db_connection
from config import Config
from ml.disease.predict import DiseasePredictor
from extensions import limiter, csrf
from routes.auth import login_required

disease_bp = Blueprint('disease', __name__)
logger = logging.getLogger('agrismart.disease')
predictor = DiseasePredictor()


def allowed_file(filename):
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in Config.ALLOWED_EXTENSIONS


def validate_image_content(file_obj):
    """
    Deep image validation using Pillow.
    Ensures the file is genuinely an image (JPEG, PNG, WEBP) and not an executable/corrupt binary.
    """
    try:
        file_obj.seek(0)
        img = Image.open(file_obj)
        img.verify()
        file_obj.seek(0)
        if img.format not in ['JPEG', 'PNG', 'WEBP']:
            return False, f"Unsupported image format: {img.format}. Please upload JPEG, PNG, or WEBP."
        return True, ""
    except Exception:
        file_obj.seek(0)
        return False, "The uploaded file is not a valid image or is corrupted."


# -------------------------------------------------------------------------
# Web Interface Routes (/disease)
# -------------------------------------------------------------------------
@disease_bp.route('/disease', methods=['GET', 'POST'])
@login_required
@limiter.limit("25 per minute", methods=["POST"])
def index():
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    result = None
    uploaded_image_url = None
    error_message = None
    model_ready = predictor.is_model_available()

    if request.method == 'POST':
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                if not allowed_file(file.filename):
                    flash('Unsupported file extension. Please upload JPG, JPEG, PNG, or WEBP.', 'danger')
                else:
                    is_valid, err_msg = validate_image_content(file)
                    if not is_valid:
                        flash(err_msg, 'danger')
                    elif not model_ready:
                        error_message = "Disease detection model is not available yet."
                        flash(error_message, 'warning')
                    else:
                        safe_base = secure_filename(file.filename) or 'leaf.jpg'
                        filename = f"{uuid.uuid4().hex[:12]}_{safe_base}"
                        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
                        save_path = os.path.abspath(os.path.join(Config.UPLOAD_FOLDER, filename))
                        
                        # Prevent directory traversal
                        if not save_path.startswith(os.path.abspath(Config.UPLOAD_FOLDER)):
                            flash('Invalid file destination path.', 'danger')
                            return redirect(url_for('disease.index'))

                        file.save(save_path)

                        # Run Real Model Prediction
                        prediction = predictor.predict(save_path)

                        if prediction.get('status') == 'error':
                            error_message = prediction.get('message', 'Prediction failed.')
                            flash(error_message, 'danger')
                        else:
                            uploaded_image_url = url_for('static', filename='uploads/' + filename)
                            
                            # Format symptoms and treatment for UI display
                            symptoms_list = prediction['symptoms'] if isinstance(prediction['symptoms'], list) else [prediction['symptoms']]
                            treatment_list = prediction['recommended_action'] if isinstance(prediction['recommended_action'], list) else [prediction['recommended_action']]

                            result = {
                                'crop': prediction.get('crop', 'Unknown Crop'),
                                'disease': prediction.get('disease', 'Unknown Disease'),
                                'confidence': prediction.get('confidence', 0),
                                'is_healthy': prediction.get('is_healthy', False),
                                'status': prediction.get('status', 'success'),
                                'symptoms': symptoms_list,
                                'treatment': treatment_list,
                                'prevention': prediction.get('prevention', '')
                            }

                            # Save to Database history
                            cursor.execute('''
                                INSERT INTO disease_records (user_id, image_path, disease, confidence, symptoms, treatment, is_healthy)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                user_id, filename, result['disease'], result['confidence'],
                                "; ".join(symptoms_list), "; ".join(treatment_list),
                                1 if result['is_healthy'] else 0
                            ))
                            conn.commit()
            else:
                flash('Please select an image file to analyze.', 'warning')

    # Fetch recent disease scans for this user
    cursor.execute("SELECT * FROM disease_records WHERE user_id = ? ORDER BY id DESC LIMIT 10", (user_id,))
    history = [dict(r) for r in cursor.fetchall()]
    conn.close()

    return render_template(
        'disease.html',
        user=user,
        result=result,
        uploaded_image_url=uploaded_image_url,
        history=history,
        model_ready=model_ready,
        error_message=error_message
    )


# -------------------------------------------------------------------------
# Standard Flask API: POST /api/disease/predict (and /disease/api/predict)
# -------------------------------------------------------------------------
@disease_bp.route('/api/disease/predict', methods=['POST'])
@disease_bp.route('/disease/api/predict', methods=['POST'])
@disease_bp.route('/disease/predict', methods=['POST'])
@csrf.exempt
@limiter.limit("20 per minute")
def api_predict():
    """
    Real Crop Leaf Disease Prediction API.
    Flow: Upload Image -> Flask -> Pillow Verification -> TensorFlow/Keras -> Real Prediction -> JSON
    """
    # 1. Check Model Availability
    if not predictor.is_model_available():
        return jsonify({
            "status": "error",
            "message": "Disease detection model is not trained or weights are not loaded.",
            "error_code": "MODEL_NOT_TRAINED"
        }), 503

    # Check request payload size
    if request.content_length and request.content_length > Config.MAX_CONTENT_LENGTH:
        return jsonify({
            "status": "error",
            "message": "Uploaded image file is too large. Maximum file size allowed is 16 MB."
        }), 413

    # 2. Check File Upload
    file = None
    if 'image' in request.files:
        file = request.files['image']
    elif 'file' in request.files:
        file = request.files['file']

    if not file or file.filename == '':
        return jsonify({
            "status": "error",
            "message": "No image file provided in request. Please upload an image with key 'image' or 'file'."
        }), 400

    if not allowed_file(file.filename):
        return jsonify({
            "status": "error",
            "message": "Unsupported file format. Supported formats: JPG, JPEG, PNG, WEBP."
        }), 400

    # Deep image format validation
    is_valid, err_msg = validate_image_content(file)
    if not is_valid:
        return jsonify({
            "status": "error",
            "message": err_msg
        }), 400

    try:
        # Save temporary uploaded file safely
        safe_base = secure_filename(file.filename) or 'leaf.jpg'
        filename = f"{uuid.uuid4().hex[:12]}_{safe_base}"
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        save_path = os.path.abspath(os.path.join(Config.UPLOAD_FOLDER, filename))

        if not save_path.startswith(os.path.abspath(Config.UPLOAD_FOLDER)):
            return jsonify({
                "status": "error",
                "message": "Invalid file destination."
            }), 400

        file.save(save_path)

        # Run Real TensorFlow/Keras Prediction
        prediction = predictor.predict(save_path)

        if prediction.get('status') == 'error':
            return jsonify({
                "status": "error",
                "message": prediction.get('message', 'Disease detection model prediction failed.'),
                "error_code": prediction.get('error_code', 'PREDICTION_ERROR')
            }), 500

        symptoms_list = prediction['symptoms'] if isinstance(prediction.get('symptoms'), list) else [prediction.get('symptoms', '')]
        action_list = prediction['recommended_action'] if isinstance(prediction.get('recommended_action'), list) else [prediction.get('recommended_action', '')]
        symptoms_str = "; ".join(symptoms_list)
        action_str = "; ".join(action_list)

        # Handle Low Confidence Response
        if prediction.get('status') == 'low_confidence':
            return jsonify({
                "status": "low_confidence",
                "crop": prediction.get('crop', 'Uncertain Crop Specimen'),
                "disease": "Unable to confidently identify this leaf.",
                "confidence": float(prediction.get('confidence', 0.0)),
                "symptoms": symptoms_list,
                "recommended_action": action_list,
                "prevention": prediction.get('prevention', ''),
                "message": "Unable to confidently identify this leaf."
            }), 200

        # Save record to database if user session is active
        if 'user_id' in session:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO disease_records (user_id, image_path, disease, confidence, symptoms, treatment, is_healthy)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session['user_id'], filename, prediction['disease'], prediction['confidence'],
                    symptoms_str, action_str,
                    1 if prediction.get('is_healthy') else 0
                ))
                conn.commit()
                conn.close()
            except Exception as db_err:
                current_app.logger.warning(f"Failed to record disease scan in DB: {db_err}")

        # Standard Success Response
        return jsonify({
            "status": "success",
            "crop": prediction["crop"],
            "disease": prediction["disease"],
            "confidence": float(prediction["confidence"]),
            "symptoms": symptoms_list,
            "recommended_action": action_list,
            "prevention": prediction.get("prevention", ""),
            "is_healthy": bool(prediction.get("is_healthy", False)),
            "image_url": url_for('static', filename='uploads/' + filename)
        }), 200

    except Exception as e:
        logger.exception(f"Unexpected error in api_predict: {e}")
        return jsonify({
            "status": "error",
            "message": "An unexpected error occurred during leaf image analysis."
        }), 500
