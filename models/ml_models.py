import os
import random
import numpy as np
from PIL import Image

class CropRecommender:
    """
    Intelligent Crop Recommendation Engine.
    Ready for Scikit-Learn Model (.pkl) integration with high-precision rule-based fallback.
    """
    def __init__(self, model_path=None):
        self.model_path = model_path or os.path.join(os.path.dirname(__file__), '..', 'ml', 'crop_model.pkl')
        self.model = self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                import joblib
                return joblib.load(self.model_path)
            except Exception as e:
                print(f"[ML Notice] Could not load crop ML model ({e}), using agronomic expert engine.")
        return None

    def recommend(self, n, p, k, ph, temp, humidity, rainfall, season="Kharif", location=""):
        """
        Evaluate agro-climatic & soil parameters and return primary + alternative crop suggestions.
        """
        # Crop profiles with optimal parameter centroids & tolerances
        crops_knowledge = {
            'Rice': {
                'n_range': (60, 120), 'p_range': (35, 60), 'k_range': (30, 50),
                'ph_range': (5.0, 7.5), 'temp_range': (20, 35), 'humidity_range': (65, 95),
                'rain_range': (150, 300), 'seasons': ['Kharif (Monsoon)', 'Kharif', 'Monsoon'],
                'suitability_score': 0,
                'duration': '120 - 145 Days',
                'water': 'High (1200 - 1500 mm)',
                'icon': 'fa-solid fa-wheat-awn',
                'description': 'Optimal moisture and warm humid climate make your field ideal for high-yielding Paddy cultivars (Basmati / PR-126).',
                'tips': [
                    'Maintain 3-5 cm standing water layer during early tillering stage.',
                    'Apply basal dose of Zinc Sulfate (25 kg/ha) with NPK mixture.',
                    'Keep vigil for stem borer and leaf folder during peak tillering.'
                ]
            },
            'Wheat': {
                'n_range': (80, 140), 'p_range': (40, 75), 'k_range': (30, 60),
                'ph_range': (6.0, 7.8), 'temp_range': (12, 26), 'humidity_range': (40, 70),
                'rain_range': (30, 100), 'seasons': ['Rabi (Winter)', 'Rabi', 'Winter'],
                'suitability_score': 0,
                'duration': '115 - 135 Days',
                'water': 'Medium (450 - 650 mm)',
                'icon': 'fa-solid fa-seedling',
                'description': 'Cool vegetative temperatures and rich nitrogen balance strongly favor premium bread wheat (HD-2967 / PBW-550).',
                'tips': [
                    'Ensure first irrigation (CRI stage) within 21 days of sowing.',
                    'Top dress nitrogen in two equal splits at first and second irrigation.',
                    'Scout for yellow rust symptoms in cool, misty morning conditions.'
                ]
            },
            'Maize': {
                'n_range': (60, 100), 'p_range': (30, 60), 'k_range': (30, 50),
                'ph_range': (5.5, 7.5), 'temp_range': (18, 32), 'humidity_range': (50, 80),
                'rain_range': (60, 150), 'seasons': ['Kharif (Monsoon)', 'Spring', 'Rabi', 'Kharif'],
                'suitability_score': 0,
                'duration': '90 - 110 Days',
                'water': 'Medium (500 - 700 mm)',
                'icon': 'fa-solid fa-cubes-stacked',
                'description': 'Well-drained soil with adequate organic carbon ensures superior grain filling and hybrid vigor.',
                'tips': [
                    'Avoid waterlogging at all costs; ensure adequate drainage furrows.',
                    'Apply Potassium fertilizer to enhance stem strength against lodging.',
                    'Monitor for Fall Armyworm during early whorl vegetative stage.'
                ]
            },
            'Cotton': {
                'n_range': (90, 150), 'p_range': (35, 65), 'k_range': (35, 60),
                'ph_range': (6.0, 8.2), 'temp_range': (22, 36), 'humidity_range': (50, 85),
                'rain_range': (60, 130), 'seasons': ['Kharif (Monsoon)', 'Kharif', 'Summer'],
                'suitability_score': 0,
                'duration': '150 - 180 Days',
                'water': 'Medium to High (700 - 1100 mm)',
                'icon': 'fa-solid fa-cloud',
                'description': 'Deep fertile soil with moderate rainfall profile offers excellent boll retention and lint quality.',
                'tips': [
                    'Install pheromone traps (5/acre) to monitor pink bollworm activity.',
                    'Foliar spray of 2% DAP at peak flowering to boost boll development.',
                    'Maintain clean weeding during first 60 days of crop establishment.'
                ]
            },
            'Sugarcane': {
                'n_range': (120, 180), 'p_range': (50, 90), 'k_range': (50, 90),
                'ph_range': (6.0, 7.8), 'temp_range': (20, 38), 'humidity_range': (60, 90),
                'rain_range': (100, 250), 'seasons': ['Annual', 'Spring', 'Autumn', 'Kharif'],
                'suitability_score': 0,
                'duration': '300 - 365 Days',
                'water': 'High (1500 - 2200 mm)',
                'icon': 'fa-solid fa-tree',
                'description': 'High nutrient reserve and deep alluvial loam deliver exceptional cane tonnage and high sucrose recovery.',
                'tips': [
                    'Practice trash mulching between rows to conserve soil moisture.',
                    'Apply trichoderma enriched compost to protect sets from red rot.',
                    'Earthing up in 3rd month to provide sturdy anchorage against wind.'
                ]
            },
            'Mustard': {
                'n_range': (50, 90), 'p_range': (25, 50), 'k_range': (20, 45),
                'ph_range': (6.0, 7.5), 'temp_range': (10, 25), 'humidity_range': (40, 65),
                'rain_range': (25, 60), 'seasons': ['Rabi (Winter)', 'Rabi', 'Winter'],
                'suitability_score': 0,
                'duration': '100 - 120 Days',
                'water': 'Low (300 - 450 mm)',
                'icon': 'fa-solid fa-spa',
                'description': 'Low irrigation demand and modest nutrient thresholds make Mustard highly profitable in winter rotations.',
                'tips': [
                    'Ensure sulfur application (20 kg/ha) to maximize seed oil content.',
                    'Thin seedlings to 10-15 cm spacing to allow maximum branch spread.',
                    'Keep ready preventive bio-pesticide spray for aphid attacks in January.'
                ]
            },
            'Chickpea (Gram)': {
                'n_range': (20, 50), 'p_range': (40, 70), 'k_range': (20, 45),
                'ph_range': (6.0, 8.0), 'temp_range': (15, 27), 'humidity_range': (35, 60),
                'rain_range': (20, 70), 'seasons': ['Rabi (Winter)', 'Rabi', 'Winter'],
                'suitability_score': 0,
                'duration': '95 - 115 Days',
                'water': 'Low (300 - 400 mm)',
                'icon': 'fa-solid fa-leaf',
                'description': 'Nitrogen-fixing pulse providing high ROI with minimal inputs while enriching your soil for future crops.',
                'tips': [
                    'Inoculate seeds with Rhizobium culture before sowing.',
                    'Do not over-irrigate during flowering stage to prevent flower drop.',
                    'Install bird perches across field for natural pod borer predation.'
                ]
            },
            'Potato': {
                'n_range': (90, 160), 'p_range': (60, 110), 'k_range': (80, 150),
                'ph_range': (5.0, 6.8), 'temp_range': (14, 23), 'humidity_range': (55, 80),
                'rain_range': (35, 80), 'seasons': ['Rabi (Winter)', 'Rabi', 'Winter'],
                'suitability_score': 0,
                'duration': '80 - 105 Days',
                'water': 'Medium (400 - 550 mm)',
                'icon': 'fa-solid fa-circle',
                'description': 'Potassium-rich, friable soil produces high-grade tubers with superior skin finish and storability.',
                'tips': [
                    'Carry out earthing up properly to protect emerging tubers from sun greening.',
                    'Maintain uniform light irrigations at 7-10 day intervals.',
                    'Apply preventive Mancozeb spray against early/late blight.'
                ]
            }
        }

        # Calculate matching scores
        scored_crops = []
        for crop_name, data in crops_knowledge.items():
            score = 100.0

            # Distance penalties
            def dist_penalty(val, min_v, max_v, weight=1.0):
                if min_v <= val <= max_v:
                    return 0
                diff = min(abs(val - min_v), abs(val - max_v))
                span = max(1.0, max_v - min_v)
                return min(30.0, (diff / span) * 20.0 * weight)

            score -= dist_penalty(n, data['n_range'][0], data['n_range'][1], 1.2)
            score -= dist_penalty(p, data['p_range'][0], data['p_range'][1], 1.0)
            score -= dist_penalty(k, data['k_range'][0], data['k_range'][1], 1.0)
            score -= dist_penalty(ph, data['ph_range'][0], data['ph_range'][1], 1.5)
            score -= dist_penalty(temp, data['temp_range'][0], data['temp_range'][1], 1.4)
            score -= dist_penalty(humidity, data['humidity_range'][0], data['humidity_range'][1], 1.1)
            score -= dist_penalty(rainfall, data['rain_range'][0], data['rain_range'][1], 1.3)

            # Season bonus / penalty
            season_clean = season.lower()
            matching_season = any(s.lower() in season_clean or season_clean in s.lower() for s in data['seasons'])
            if matching_season:
                score += 10.0
            else:
                score -= 15.0

            score = max(15.0, min(98.5, score))
            scored_crops.append((crop_name, score, data))

        # Sort by score descending
        scored_crops.sort(key=lambda x: x[1], reverse=True)

        primary = scored_crops[0]
        crop_name = primary[0]
        confidence = round(primary[1], 1)
        data = primary[2]

        suitability = "High" if confidence >= 80 else ("Moderate" if confidence >= 60 else "Fair")

        alternatives = []
        for alt_name, alt_score, alt_data in scored_crops[1:4]:
            alternatives.append({
                'name': alt_name,
                'confidence': round(alt_score, 1),
                'suitability': "High" if alt_score >= 80 else ("Moderate" if alt_score >= 60 else "Fair"),
                'duration': alt_data['duration'],
                'water': alt_data['water'],
                'icon': alt_data['icon'],
                'description': alt_data['description']
            })

        return {
            'recommended_crop': crop_name,
            'confidence': confidence,
            'suitability': suitability,
            'growing_period': data['duration'],
            'water_requirement': data['water'],
            'suitable_season': season or 'Current Season',
            'icon': data['icon'],
            'why_suitable': data['description'],
            'farming_tips': data['tips'],
            'alternatives': alternatives
        }


class DiseaseDetector:
    """
    Crop Leaf Disease Detection Engine wrapper.
    Delegates to real TensorFlow/Keras DiseasePredictor pipeline in ml.disease.predict.
    """
    def __init__(self, model_path=None, classes_path=None):
        from ml.disease.predict import DiseasePredictor
        self.predictor = DiseasePredictor(model_path=model_path, classes_path=classes_path)

    def is_model_available(self) -> bool:
        return self.predictor.is_model_available()

    def analyze_image(self, file_path, user_hint_crop=None):
        """Analyze leaf image using real TensorFlow/Keras prediction engine."""
        return self.predictor.predict(file_path)

