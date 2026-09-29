"""
Crop Leaf Disease Prediction Engine.
Performs real inference using trained TensorFlow/Keras model and class_names.json.
Provides safe error handling when model is not trained yet, and low-confidence filtering.
"""

import os
import json
import numpy as np
from PIL import Image
from ml.disease.disease_info import get_disease_info

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DEFAULT_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'plant_disease_model.keras')
DEFAULT_CLASSES_PATH = os.path.join(BASE_DIR, 'models', 'class_names.json')
CONFIDENCE_THRESHOLD = 50.0  # Minimum percentage required for reliable diagnostic


class DiseasePredictor:
    """Real TensorFlow/Keras Disease Prediction Service."""

    def __init__(self, model_path=None, classes_path=None, img_size=(224, 224)):
        self.model_path = model_path or DEFAULT_MODEL_PATH
        self.classes_path = classes_path or DEFAULT_CLASSES_PATH
        self.img_size = img_size
        self._model = None
        self._class_names = None
        self._load_error = None

    def is_model_available(self) -> bool:
        """Check if both the trained model file and class names JSON exist."""
        return os.path.exists(self.model_path) and os.path.exists(self.classes_path)

    def _lazy_load(self):
        """Lazy load model and classes into memory on first inference request."""
        if self._model is not None and self._class_names is not None:
            return True

        if not self.is_model_available():
            self._load_error = "Disease detection model is not trained yet."
            return False

        try:
            # 1. Load Class Names
            with open(self.classes_path, 'r', encoding='utf-8') as f:
                self._class_names = json.load(f)

            # 2. Import Keras / TensorFlow and Load Model
            try:
                import keras
                self._model = keras.models.load_model(self.model_path)
            except Exception:
                import tensorflow as tf
                self._model = tf.keras.models.load_model(self.model_path)
            self._load_error = None
            return True
        except ImportError:
            self._load_error = "TensorFlow / Keras is not installed in the environment."
            return False
        except Exception as e:
            self._load_error = f"Error loading disease detection model: {str(e)}"
            return False

    def preprocess_image(self, image_input):
        """
        Validate and preprocess an input image (file path, file object, or PIL Image)
        into a tensor suitable for model inference.
        """
        try:
            if isinstance(image_input, str):
                if not os.path.exists(image_input):
                    raise ValueError(f"Image file not found: {image_input}")
                img = Image.open(image_input)
            elif isinstance(image_input, Image.Image):
                img = image_input
            else:
                # File-like stream
                img = Image.open(image_input)

            # Convert to RGB (handles RGBA, Grayscale, etc.)
            img_rgb = img.convert('RGB')
            # Resize with High Quality Lanczos/Bicubic resampling
            img_resized = img_rgb.resize(self.img_size, Image.Resampling.BILINEAR)
            img_array = np.array(img_resized, dtype=np.float32)

            # Add batch dimension: (1, 224, 224, 3)
            img_batch = np.expand_dims(img_array, axis=0)
            return img_batch
        except Exception as e:
            raise ValueError(f"Invalid image format or corrupted file: {str(e)}")

    def predict(self, image_input) -> dict:
        """
        Run REAL model prediction on the provided image.
        Returns a standardized dictionary with crop, disease, confidence, and treatment info.
        """
        # 1. Verify model readiness
        if not self._lazy_load():
            return {
                "status": "error",
                "message": self._load_error or "Disease detection model is not trained yet.",
                "error_code": "MODEL_NOT_TRAINED"
            }

        # 2. Preprocess Image
        try:
            input_tensor = self.preprocess_image(image_input)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Image processing failed: {str(e)}",
                "error_code": "INVALID_IMAGE"
            }

        # 3. Perform Real Model Inference
        try:
            raw_predictions = self._model.predict(input_tensor, verbose=0)
            # Probability distribution
            probabilities = raw_predictions[0]
            predicted_idx = int(np.argmax(probabilities))
            max_prob = float(probabilities[predicted_idx])
            confidence_pct = round(max_prob * 100.0, 1)

            if predicted_idx >= len(self._class_names):
                raw_class_name = "Unknown"
            else:
                raw_class_name = self._class_names[predicted_idx]

        except Exception as e:
            return {
                "status": "error",
                "message": f"Model inference error: {str(e)}",
                "error_code": "INFERENCE_FAILED"
            }

        # 4. Handle Low Confidence Scenarios
        if confidence_pct < CONFIDENCE_THRESHOLD:
            return {
                "status": "low_confidence",
                "crop": "Uncertain Crop Specimen",
                "disease": "Unable to confidently identify the disease from this image.",
                "confidence": confidence_pct,
                "is_healthy": False,
                "symptoms": [
                    "The uploaded leaf photograph is blurry, dark, off-center, or contains ambiguous symptoms.",
                    "The image does not sufficiently match known visual disease signatures."
                ],
                "recommended_action": [
                    "Take a well-lit, close-up photograph focusing directly on the affected leaf blade.",
                    "Ensure the leaf surface is clearly in focus without heavy shadow, glare, or background clutter.",
                    "Re-upload the new clear photo for a definitive diagnosis."
                ],
                "prevention": "Ensure good natural lighting and clean focus when capturing diagnostic field images.",
                "message": "Unable to confidently identify the disease from this image."
            }

        # 5. Fetch Full Agronomic Details for the predicted class
        info = get_disease_info(raw_class_name)

        return {
            "status": "success",
            "raw_class": raw_class_name,
            "crop": info["crop"],
            "disease": info["disease"],
            "confidence": confidence_pct,
            "is_healthy": info["is_healthy"],
            "symptoms": info["symptoms"],
            "recommended_action": info["recommended_action"],
            "prevention": info["prevention"]
        }


# Global singleton instance
predictor = DiseasePredictor()


def predict_disease(image_input) -> dict:
    """Convenience helper function for disease prediction."""
    return predictor.predict(image_input)
