import os
import json
import logging
import joblib
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class CropRecommendationService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CropRecommendationService, cls).__new__(cls)
            cls._instance._init_service()
        return cls._instance

    def _init_service(self):
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.model_path = os.path.join(self.base_dir, 'models', 'crop_recommendation_model.pkl')
        self.metadata_path = os.path.join(self.base_dir, 'models', 'crop_model_metadata.json')
        self.catalog_path = os.path.join(self.base_dir, 'data', 'crop_catalog.json')
        self.planning_path = os.path.join(self.base_dir, 'data', 'crop_planning_metadata.json')
        self.dataset_path = os.path.join(self.base_dir, 'data', 'crop_recommendation.csv')
        if not os.path.exists(self.dataset_path):
            self.dataset_path = os.path.join(self.base_dir, 'data', 'crop_yield.csv')

        self.model = None
        self.metadata = {}
        self.catalog = {}
        self.planning_data = {}
        self.dataset_df = None
        self._load_artifacts()

    def _load_artifacts(self):
        # Load ML model
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                logger.info(f"Loaded ML model from {self.model_path}")
            except Exception as e:
                logger.error(f"Error loading ML model from {self.model_path}: {e}")

        # Load Metadata
        if os.path.exists(self.metadata_path):
            try:
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            except Exception as e:
                logger.error(f"Error loading metadata from {self.metadata_path}: {e}")

        # Load Crop Catalog
        if os.path.exists(self.catalog_path):
            try:
                with open(self.catalog_path, 'r', encoding='utf-8') as f:
                    self.catalog = json.load(f)
            except Exception as e:
                logger.error(f"Error loading crop catalog from {self.catalog_path}: {e}")

        # Load Crop Planning Metadata
        if os.path.exists(self.planning_path):
            try:
                with open(self.planning_path, 'r', encoding='utf-8') as f:
                    self.planning_data = json.load(f)
            except Exception as e:
                logger.error(f"Error loading crop planning metadata from {self.planning_path}: {e}")

        # Pre-cache dataset DataFrame for fast candidate exploration
        if os.path.exists(self.dataset_path):
            try:
                df = pd.read_csv(self.dataset_path)
                for c in df.columns:
                    if df[c].dtype == 'object' or pd.api.types.is_string_dtype(df[c]):
                        df[c] = df[c].astype(str).str.strip()
                self.dataset_df = df
                logger.info(f"Loaded dataset ({len(df)} rows) for target exploration.")
            except Exception as e:
                logger.error(f"Error loading dataset from {self.dataset_path}: {e}")

    def get_metadata(self):
        return self.metadata

    def validate_inputs(self, raw_data):
        """
        Validate and normalize farmer input data.
        Returns (is_valid, cleaned_data_or_error_message)
        """
        errors = []
        cleaned = {}

        # 1. Season validation
        season = str(raw_data.get('season', '')).strip()
        allowed_seasons = self.metadata.get('allowed_seasons', ['Autumn', 'Kharif', 'Rabi', 'Summer', 'Whole Year', 'Winter'])
        matched_season = None
        for s in allowed_seasons:
            if s.lower() in season.lower() or season.lower() in s.lower():
                matched_season = s
                break
        if not matched_season:
            matched_season = allowed_seasons[0] if allowed_seasons else 'Kharif'
        cleaned['Season'] = matched_season

        # 2. State validation
        state = str(raw_data.get('state', raw_data.get('location', ''))).strip()
        allowed_states = self.metadata.get('allowed_states', [])
        matched_state = None
        for s in allowed_states:
            if s.lower() in state.lower() or state.lower() in s.lower():
                matched_state = s
                break
        if not matched_state:
            matched_state = 'Uttar Pradesh' if 'Uttar Pradesh' in allowed_states else (allowed_states[0] if allowed_states else 'Uttar Pradesh')
        cleaned['State'] = matched_state

        # 3. Numerical fields validation
        num_fields = {
            'area': ('Area', 0.1, 50000000.0, 5.0),
            'rainfall': ('Annual_Rainfall', 50.0, 7000.0, 1100.0),
            'fertilizer': ('Fertilizer', 0.0, 5000000000.0, 250.0),
            'pesticide': ('Pesticide', 0.0, 20000000.0, 10.0)
        }

        alt_names = {
            'area': ['area', 'farm_area', 'land_area'],
            'rainfall': ['rainfall', 'annual_rainfall', 'rain'],
            'fertilizer': ['fertilizer', 'fertilizer_usage', 'fertilizer_kg'],
            'pesticide': ['pesticide', 'pesticide_usage', 'pesticide_kg']
        }

        for std_key, (col_name, min_val, max_val, default_val) in num_fields.items():
            val = None
            for alias in alt_names[std_key]:
                if alias in raw_data and raw_data[alias] not in (None, ''):
                    val = raw_data[alias]
                    break
            
            if val is None:
                val = default_val

            try:
                if isinstance(val, str):
                    val_str = val.lower().replace('acres', '').replace('acre', '').replace('ha', '').replace('mm', '').replace('kg', '').strip()
                    val = float(val_str)
                else:
                    val = float(val)

                if val < 0:
                    errors.append(f"{col_name} cannot be negative.")
                elif val > max_val:
                    errors.append(f"{col_name} value ({val}) exceeds realistic upper limit.")
                else:
                    cleaned[col_name] = val
            except (ValueError, TypeError):
                errors.append(f"Invalid numeric value for {col_name}: '{val}'")

        if errors:
            return False, "; ".join(errors)

        return True, cleaned

    def _get_crop_info(self, crop_name, season=""):
        info = self.catalog.get(crop_name)
        if not info:
            info = {
                'season': season or 'Current Season',
                'duration': '90 - 120 Days',
                'water': 'Moderate (450 - 700 mm)',
                'icon': 'fa-solid fa-seedling',
                'why_suitable': f'Soil, regional climate and input balance provide optimal agro-climatic conditions for {crop_name}.',
                'farming_tips': [
                    f'Use certified quality seed varieties of {crop_name}.',
                    'Maintain balanced basal fertilizer and adequate moisture at sowing.',
                    'Adopt integrated pest and weed management throughout vegetative growth.'
                ]
            }
        return info

    def _determine_suitability(self, confidence):
        thresholds = self.metadata.get('suitability_thresholds', {'high': 40.0, 'moderate': 20.0})
        high_thresh = thresholds.get('high', 40.0)
        mod_thresh = thresholds.get('moderate', 20.0)

        if confidence >= high_thresh:
            return "HIGH"
        elif confidence >= mod_thresh:
            return "MODERATE"
        else:
            return "LOW"

    def _determine_alternative_match(self, confidence):
        if confidence >= 35.0:
            return "STRONG MATCH"
        elif confidence >= 15.0:
            return "MODERATE MATCH"
        else:
            return "FAIR MATCH"

    def predict(self, raw_data):
        """
        Execute full ML recommendation pipeline.
        Returns dict with success status, primary match, and top 3 alternatives.
        """
        if self.model is None:
            self._load_artifacts()
            if self.model is None:
                return {
                    'success': False,
                    'error': 'ML model is not loaded. Please ensure train_crop_model.py has been executed.'
                }

        is_valid, validated_data = self.validate_inputs(raw_data)
        if not is_valid:
            return {
                'success': False,
                'error': f'Validation error: {validated_data}'
            }

        feature_cols = self.metadata.get('feature_names', ['Season', 'State', 'Area', 'Annual_Rainfall', 'Fertilizer', 'Pesticide'])
        input_df = pd.DataFrame([validated_data])[feature_cols]

        try:
            probabilities = self.model.predict_proba(input_df)[0]
            classes = self.model.classes_

            sorted_indices = np.argsort(probabilities)[::-1]

            primary_idx = sorted_indices[0]
            primary_crop = str(classes[primary_idx])
            primary_conf = float(probabilities[primary_idx] * 100.0)
            primary_conf_display = round(primary_conf, 1)

            primary_info = self._get_crop_info(primary_crop, validated_data.get('Season', ''))
            suitability = self._determine_suitability(primary_conf)

            primary_match = {
                'recommended_crop': primary_crop,
                'crop_name': primary_crop,
                'confidence': primary_conf_display,
                'suitability': suitability,
                'suitable_season': primary_info.get('season', validated_data.get('Season', '')),
                'growing_period': primary_info.get('duration', '90 - 120 Days'),
                'water_requirement': primary_info.get('water', 'Medium (500 - 750 mm)'),
                'icon': primary_info.get('icon', 'fa-solid fa-seedling'),
                'why_suitable': primary_info.get('why_suitable', ''),
                'farming_tips': primary_info.get('farming_tips', [])
            }

            alternatives = []
            for alt_idx in sorted_indices[1:4]:
                alt_crop = str(classes[alt_idx])
                alt_conf = float(probabilities[alt_idx] * 100.0)
                alt_conf_display = round(alt_conf, 1)
                alt_info = self._get_crop_info(alt_crop, validated_data.get('Season', ''))
                alt_suitability = self._determine_alternative_match(alt_conf)

                alternatives.append({
                    'name': alt_crop,
                    'crop_name': alt_crop,
                    'confidence': alt_conf_display,
                    'suitability': alt_suitability,
                    'duration': alt_info.get('duration', '90 - 120 Days'),
                    'water': alt_info.get('water', 'Medium'),
                    'icon': alt_info.get('icon', 'fa-solid fa-seedling'),
                    'description': alt_info.get('why_suitable', '')
                })

            return {
                'success': True,
                'primary_match': primary_match,
                'alternatives': alternatives,
                'input': validated_data,
                'metadata': {
                    'model_type': self.metadata.get('model_type', 'RandomForestClassifier'),
                    'num_classes': len(classes),
                    'test_accuracy': self.metadata.get('evaluation', {}).get('test_accuracy', 0.50)
                }
            }

        except Exception as e:
            logger.exception(f"Error during ML prediction: {e}")
            return {
                'success': False,
                'error': f"Prediction calculation error: {str(e)}"
            }

    def explore_target_conditions(self, crop_name, target_confidence, current_inputs):
        """
        Explore agro-climatic conditions from the actual dataset and trained model
        that move towards or maximize the target confidence for the given crop.
        """
        if self.model is None or self.dataset_df is None:
            self._load_artifacts()
            if self.model is None or self.dataset_df is None:
                return {
                    'success': False,
                    'error': 'ML Model or dataset not available for exploration.'
                }

        # Normalize target
        try:
            target_conf = float(target_confidence)
            target_conf = max(10.0, min(98.0, target_conf))
        except (ValueError, TypeError):
            target_conf = 75.0

        # Match crop in dataset
        df_crop = self.dataset_df[self.dataset_df['Crop'].str.lower() == str(crop_name).strip().lower()]
        if df_crop.empty:
            # Fallback to substring matching
            for c in self.dataset_df['Crop'].unique():
                if str(crop_name).lower() in c.lower() or c.lower() in str(crop_name).lower():
                    df_crop = self.dataset_df[self.dataset_df['Crop'] == c]
                    crop_name = c
                    break

        if df_crop.empty:
            return {
                'success': False,
                'error': f"No dataset records found for crop '{crop_name}'"
            }

        # Validate current inputs
        _, current_clean = self.validate_inputs(current_inputs)

        curr_rain = float(current_clean.get('Annual_Rainfall', 1100.0))
        curr_fert = float(current_clean.get('Fertilizer', 500.0))
        curr_pest = float(current_clean.get('Pesticide', 10.0))
        curr_area = float(current_clean.get('Area', 5.0))
        curr_season = current_clean.get('Season', 'Kharif')
        curr_state = current_clean.get('State', 'Uttar Pradesh')

        # Candidate pool generation
        candidates = []
        # Determine primary season for crop
        plan_meta_season = self.planning_data.get(crop_name, {}).get('season', '')
        if 'Kharif' in plan_meta_season:
            best_season = 'Kharif'
        elif 'Rabi' in plan_meta_season:
            best_season = 'Rabi'
        elif 'Whole Year' in plan_meta_season or 'Annual' in plan_meta_season:
            best_season = 'Whole Year'
        elif 'Summer' in plan_meta_season or 'Zaid' in plan_meta_season:
            best_season = 'Summer'
        elif not df_crop.empty:
            best_season = df_crop['Season'].mode()[0]
        else:
            best_season = current_clean.get('Season', 'Kharif')

        # 1. Top actual dataset sample rows for this crop (scaled to farmer's acreage)
        df_crop_season = df_crop[df_crop['Season'].str.lower() == best_season.lower()]
        target_df = df_crop_season if not df_crop_season.empty else df_crop

        sample_size = min(35, len(target_df))
        sampled = target_df.sample(sample_size, random_state=42)
        for _, row in sampled.iterrows():
            row_area = float(row['Area']) if float(row['Area']) > 0 else 1.0
            fert_per_ha = float(row['Fertilizer']) / row_area
            pest_per_ha = float(row['Pesticide']) / row_area
            candidates.append({
                'Season': best_season,
                'State': current_clean.get('State', row['State']),
                'Area': curr_area,
                'Annual_Rainfall': float(row['Annual_Rainfall']),
                'Fertilizer': round(max(50.0, min(50000.0, fert_per_ha * curr_area)), 1),
                'Pesticide': round(max(0.1, min(1000.0, pest_per_ha * curr_area)), 1)
            })

        # 2. Interpolations between current farmer parameters and crop medians / quantiles
        med_rain = float(target_df['Annual_Rainfall'].median())
        med_area = float(target_df['Area'].median())

        # Per-area fertilizer and pesticide rate for realistic farm scaling
        fert_rates = (df_crop['Fertilizer'] / (df_crop['Area'] + 1e-5)).replace([np.inf, -np.inf], np.nan).dropna()
        pest_rates = (df_crop['Pesticide'] / (df_crop['Area'] + 1e-5)).replace([np.inf, -np.inf], np.nan).dropna()
        med_fert_rate = float(fert_rates.median()) if not fert_rates.empty else 120.0
        med_pest_rate = float(pest_rates.median()) if not pest_rates.empty else 2.5

        scaled_fert = max(50.0, min(50000.0, med_fert_rate * curr_area))
        scaled_pest = max(0.1, min(1000.0, med_pest_rate * curr_area))

        for alpha in [0.15, 0.35, 0.55, 0.75, 0.90, 1.0]:
            candidates.append({
                'Season': curr_season if curr_season in df_crop['Season'].values else best_season,
                'State': curr_state,
                'Area': curr_area,
                'Annual_Rainfall': round(curr_rain * (1 - alpha) + med_rain * alpha, 1),
                'Fertilizer': round(curr_fert * (1 - alpha) + scaled_fert * alpha, 1),
                'Pesticide': round(curr_pest * (1 - alpha) + scaled_pest * alpha, 1)
            })

        # Also add quantile rainfall profile candidates
        for q in [0.25, 0.50, 0.75]:
            candidates.append({
                'Season': best_season,
                'State': curr_state,
                'Area': curr_area,
                'Annual_Rainfall': round(float(df_crop['Annual_Rainfall'].quantile(q)), 1),
                'Fertilizer': round(scaled_fert * (0.8 + q * 0.4), 1),
                'Pesticide': round(scaled_pest * (0.8 + q * 0.4), 1)
            })

        # Build DataFrame of candidates
        feature_cols = ['Season', 'State', 'Area', 'Annual_Rainfall', 'Fertilizer', 'Pesticide']
        df_candidates = pd.DataFrame(candidates)[feature_cols]

        # Score candidates with actual ML model
        probs = self.model.predict_proba(df_candidates)
        classes = list(self.model.classes_)
        if crop_name not in classes:
            # Fallback closest class
            matched_class = None
            for cl in classes:
                if cl.lower() in str(crop_name).lower():
                    matched_class = cl
                    break
            crop_name = matched_class or classes[0]

        crop_idx = classes.index(crop_name)
        crop_probs = probs[:, crop_idx] * 100.0

        # If user target is higher than max probability, pick highest probability candidate
        # Otherwise pick the candidate closest to target
        if target_conf > np.max(crop_probs):
            best_idx = int(np.argmax(crop_probs))
        else:
            best_idx = int(np.argmin(np.abs(crop_probs - target_conf)))

        best_cand = candidates[best_idx]
        achieved_prob = round(float(crop_probs[best_idx]), 1)

        # Agronomic nutrient requirements map (N, P, K in kg/ha, pH)
        nutrients_map = {
            'Rice': {'nitrogen': 100, 'phosphorus': 45, 'potassium': 45, 'ph': 6.2, 'fert_rate': 140.0, 'pest_rate': 2.8},
            'Wheat': {'nitrogen': 120, 'phosphorus': 60, 'potassium': 40, 'ph': 6.8, 'fert_rate': 150.0, 'pest_rate': 2.2},
            'Maize': {'nitrogen': 120, 'phosphorus': 60, 'potassium': 50, 'ph': 6.5, 'fert_rate': 140.0, 'pest_rate': 2.5},
            'Castor seed': {'nitrogen': 60, 'phosphorus': 40, 'potassium': 30, 'ph': 6.5, 'fert_rate': 80.0, 'pest_rate': 1.8},
            'Cotton(lint)': {'nitrogen': 120, 'phosphorus': 60, 'potassium': 60, 'ph': 7.0, 'fert_rate': 160.0, 'pest_rate': 4.5},
            'Cotton': {'nitrogen': 120, 'phosphorus': 60, 'potassium': 60, 'ph': 7.0, 'fert_rate': 160.0, 'pest_rate': 4.5},
            'Sugarcane': {'nitrogen': 200, 'phosphorus': 80, 'potassium': 120, 'ph': 6.8, 'fert_rate': 280.0, 'pest_rate': 5.0},
            'Potato': {'nitrogen': 150, 'phosphorus': 80, 'potassium': 100, 'ph': 5.8, 'fert_rate': 220.0, 'pest_rate': 3.5},
            'Soyabean': {'nitrogen': 30, 'phosphorus': 60, 'potassium': 40, 'ph': 6.5, 'fert_rate': 90.0, 'pest_rate': 2.0},
            'Groundnut': {'nitrogen': 25, 'phosphorus': 50, 'potassium': 40, 'ph': 6.2, 'fert_rate': 85.0, 'pest_rate': 2.2},
            'Gram': {'nitrogen': 20, 'phosphorus': 40, 'potassium': 20, 'ph': 7.0, 'fert_rate': 60.0, 'pest_rate': 1.5},
            'Rapeseed &Mustard': {'nitrogen': 80, 'phosphorus': 40, 'potassium': 30, 'ph': 6.8, 'fert_rate': 100.0, 'pest_rate': 1.8},
            'Mustard': {'nitrogen': 80, 'phosphorus': 40, 'potassium': 30, 'ph': 6.8, 'fert_rate': 100.0, 'pest_rate': 1.8},
            'Banana': {'nitrogen': 200, 'phosphorus': 60, 'potassium': 250, 'ph': 6.5, 'fert_rate': 300.0, 'pest_rate': 4.0},
            'Coconut': {'nitrogen': 100, 'phosphorus': 50, 'potassium': 150, 'ph': 6.5, 'fert_rate': 180.0, 'pest_rate': 2.5},
            'Arhar/Tur': {'nitrogen': 25, 'phosphorus': 50, 'potassium': 25, 'ph': 7.0, 'fert_rate': 70.0, 'pest_rate': 2.0},
            'Moong(Green Gram)': {'nitrogen': 20, 'phosphorus': 40, 'potassium': 20, 'ph': 6.8, 'fert_rate': 55.0, 'pest_rate': 1.6},
            'Urad': {'nitrogen': 20, 'phosphorus': 40, 'potassium': 20, 'ph': 6.8, 'fert_rate': 55.0, 'pest_rate': 1.6},
            'Jowar': {'nitrogen': 80, 'phosphorus': 40, 'potassium': 40, 'ph': 7.0, 'fert_rate': 100.0, 'pest_rate': 1.8},
            'Bajra': {'nitrogen': 70, 'phosphorus': 35, 'potassium': 35, 'ph': 7.2, 'fert_rate': 90.0, 'pest_rate': 1.5},
            'Barley': {'nitrogen': 60, 'phosphorus': 30, 'potassium': 30, 'ph': 7.2, 'fert_rate': 80.0, 'pest_rate': 1.5},
            'Sunflower': {'nitrogen': 60, 'phosphorus': 40, 'potassium': 30, 'ph': 6.8, 'fert_rate': 95.0, 'pest_rate': 2.0},
            'Onion': {'nitrogen': 100, 'phosphorus': 50, 'potassium': 80, 'ph': 6.5, 'fert_rate': 150.0, 'pest_rate': 3.0},
            'Tobacco': {'nitrogen': 80, 'phosphorus': 50, 'potassium': 100, 'ph': 6.0, 'fert_rate': 160.0, 'pest_rate': 3.5}
        }

        crop_nutrients = nutrients_map.get(crop_name, {})
        if not crop_nutrients:
            for k, v in nutrients_map.items():
                if k.lower() in str(crop_name).lower() or str(crop_name).lower() in k.lower():
                    crop_nutrients = v
                    break

        curr_n = float(current_inputs.get('nitrogen', 85))
        curr_p = float(current_inputs.get('phosphorus', 42))
        curr_k = float(current_inputs.get('potassium', 45))
        curr_ph = float(current_inputs.get('ph', 6.8))

        target_n = crop_nutrients.get('nitrogen', curr_n)
        target_p = crop_nutrients.get('phosphorus', curr_p)
        target_k = crop_nutrients.get('potassium', curr_k)
        target_ph = crop_nutrients.get('ph', curr_ph)

        suggested_inputs = {
            'state': best_cand['State'],
            'season': best_cand['Season'],
            'area': round(float(best_cand['Area']), 1) if float(best_cand['Area']) <= 5000 else 5.0,
            'rainfall': round(float(best_cand['Annual_Rainfall'])),
            'fertilizer': round(float(best_cand['Fertilizer'])),
            'pesticide': round(float(best_cand['Pesticide']), 1),
            'nitrogen': round(target_n),
            'phosphorus': round(target_p),
            'potassium': round(target_k),
            'ph': round(target_ph, 1)
        }

        # Calculate exact differences
        changes = {}
        field_meta = [
            ('rainfall', 'Annual Rainfall', 'Annual_Rainfall', ' mm', curr_rain, suggested_inputs['rainfall']),
            ('fertilizer', 'Fertilizer Usage', 'Fertilizer', ' kg', curr_fert, suggested_inputs['fertilizer']),
            ('pesticide', 'Pesticide Usage', 'Pesticide', ' kg', curr_pest, suggested_inputs['pesticide']),
            ('season', 'Cropping Season', 'Season', '', curr_season, suggested_inputs['season']),
            ('nitrogen', 'Nitrogen (N)', 'Nitrogen', ' kg/ha', curr_n, suggested_inputs['nitrogen']),
            ('phosphorus', 'Phosphorus (P)', 'Phosphorus', ' kg/ha', curr_p, suggested_inputs['phosphorus']),
            ('potassium', 'Potassium (K)', 'Potassium', ' kg/ha', curr_k, suggested_inputs['potassium']),
            ('ph', 'Soil pH', 'ph', '', curr_ph, suggested_inputs['ph'])
        ]

        for key, label, col, unit, old_v, new_v in field_meta:
            if str(old_v) != str(new_v) and abs(float(old_v) - float(new_v) if isinstance(old_v, (int, float)) and isinstance(new_v, (int, float)) else 1) > 0.05:
                changes[key] = {
                    'label': label,
                    'from': old_v,
                    'to': new_v,
                    'unit': unit,
                    'direction': 'up' if isinstance(old_v, (int, float)) and new_v > old_v else 'down'
                }

        achievable = abs(achieved_prob - target_conf) <= 15.0

        if achievable:
            message = f"To reach approximately {achieved_prob}% suitability for {crop_name} on your {suggested_inputs['area']} acre farm in {suggested_inputs['state']}, the model recommends the following conditions:"
        else:
            message = f"{target_conf}% target for {crop_name} was calibrated to the nearest agro-climatic model profile ({achieved_prob}%). Required conditions:"

        crop_catalog_info = self._get_crop_info(crop_name, suggested_inputs['season'])
        plan_meta = self.planning_data.get(crop_name, {})

        crop_info = {
            'crop_name': crop_name,
            'suitable_season': plan_meta.get('season', crop_catalog_info.get('season', suggested_inputs['season'])),
            'growing_period': plan_meta.get('growing_duration', crop_catalog_info.get('duration', '90 - 120 Days')),
            'water_requirement': plan_meta.get('water_requirement', crop_catalog_info.get('water', 'Moderate (450 - 750 mm)')),
            'icon': crop_catalog_info.get('icon', plan_meta.get('icon', 'fa-solid fa-seedling')),
            'why_suitable': f"Target suitability conditions tailored for {crop_name} in {suggested_inputs['state']} during {suggested_inputs['season']} season.",
            'farming_tips': plan_meta.get('farming_practices', crop_catalog_info.get('farming_tips', [])),
            'suitability': self._determine_suitability(achieved_prob)
        }

        return {
            'success': True,
            'crop': crop_name,
            'target_suitability': target_conf,
            'achieved_probability': achieved_prob,
            'achievable': achievable,
            'suggested_inputs': suggested_inputs,
            'changes': changes,
            'message': message,
            'crop_info': crop_info
        }

    def get_planning_crops(self):
        """Return list of all crops available for crop planning advisory."""
        if not self.planning_data:
            self._load_artifacts()
        
        crops = list(self.planning_data.keys())
        if not crops and self.model is not None:
            crops = list(self.model.classes_)
        return sorted(crops)

    def get_crop_plan(self, crop_name, location=None, check_date=None):
        """
        Return comprehensive, crop-specific planning information.
        Date-aware and location-aware.
        """
        import datetime
        if not self.planning_data:
            self._load_artifacts()

        if check_date is None:
            check_date = datetime.date.today()
        elif isinstance(check_date, str):
            try:
                check_date = datetime.date.fromisoformat(check_date)
            except Exception:
                check_date = datetime.date.today()

        # Find matching crop in planning metadata
        crop_clean = str(crop_name).strip()
        plan_meta = self.planning_data.get(crop_clean)
        matched_crop_name = crop_clean

        if not plan_meta:
            for k, v in self.planning_data.items():
                if k.lower() == crop_clean.lower():
                    plan_meta = v
                    matched_crop_name = k
                    break

        if not plan_meta:
            for k, v in self.planning_data.items():
                if crop_clean.lower() in k.lower() or k.lower() in crop_clean.lower():
                    plan_meta = v
                    matched_crop_name = k
                    break

        # Fallback if crop is completely unknown
        if not plan_meta:
            plan_meta = {
                "season": "Kharif / Rabi",
                "sowing_period": "June – July / October – November",
                "sowing_months": [6, 7, 10, 11],
                "harvest_period": "October – December / March – April",
                "temperature": "20 – 30°C",
                "temp_desc": "Best growth occurs in mild to warm temperatures with adequate sunlight.",
                "rainfall": "600 – 1000 mm",
                "soil_type": "Well-drained loamy or sandy loam soil",
                "soil_ph": "6.0 – 7.5",
                "water_requirement": "Medium (500 – 700 mm)",
                "growing_duration": "90 – 120 Days",
                "important_conditions": [
                    "Maintain proper field drainage and avoid water stagnation.",
                    "Ensure adequate soil moisture during flowering and grain/pod development.",
                    "Soil should remain within the recommended neutral pH range."
                ],
                "farming_practices": [
                    "Use certified high-yielding and disease-resistant seed varieties.",
                    "Apply balanced NPK fertilizers based on soil test results.",
                    "Adopt integrated pest and weed management at critical vegetative stages."
                ],
                "icon": "fa-solid fa-seedling"
            }
            matched_crop_name = crop_clean

        current_month = check_date.month
        current_year = check_date.year
        sowing_months = plan_meta.get("sowing_months", [6, 7])
        sowing_period = plan_meta.get("sowing_period", "Seasonal")

        # Determine Date-Aware Planting Status
        if len(sowing_months) >= 10:
            status = "Good time to plan"
            status_type = "active"
            status_badge = "success"
            status_message = "Perennial / Year-round crop. Suitable for planting in almost any month with assured irrigation."
            next_window = f"Active Year-Round ({current_year})"
        elif current_month in sowing_months:
            status = "Recommended planting window"
            status_type = "active"
            status_badge = "success"
            status_message = f"Currently in the ideal sowing window ({sowing_period}). Optimal time to sow or transplant."
            next_window = f"{sowing_period} {current_year}"
        else:
            # Check if upcoming in current year
            upcoming = [m for m in sowing_months if m > current_month]
            if upcoming:
                diff = min(upcoming) - current_month
                if diff <= 2:
                    status = "Planting window approaching"
                    status_type = "approaching"
                    status_badge = "warning"
                    status_message = f"Sowing window ({sowing_period}) is approaching in {diff} month{'s' if diff > 1 else ''}. Ideal time for field preparation, seed procurement, and soil testing."
                else:
                    status = "Good time to plan"
                    status_type = "planning"
                    status_badge = "info"
                    status_message = f"Upcoming sowing window starts in {diff} months ({sowing_period}). Plan your land and inputs ahead of time."
                next_window = f"{sowing_period} {current_year}"
            else:
                # Sowing window for current calendar year has passed
                status = "Planting window has passed"
                status_type = "passed"
                status_badge = "secondary"
                next_year = current_year + 1
                status_message = f"Recommended sowing window for this season has passed. Next suitable planting window begins in {sowing_period} {next_year}."
                next_window = f"{sowing_period} {next_year}"

        # Location contextual note and regional agronomic tailoring
        location_note = ""
        soil_type_val = plan_meta.get("soil_type", "Loamy soil")

        if location and str(location).strip():
            loc_clean = str(location).strip()
            loc_lower = loc_clean.lower()

            if "bihar" in loc_lower or "patna" in loc_lower:
                location_note = f"Agro-Climatic Zone: Middle Gangetic Plain ({loc_clean}) — fertile alluvial soils with high water retention."
                if "rice" in matched_crop_name.lower() or "wheat" in matched_crop_name.lower() or "maize" in matched_crop_name.lower():
                    soil_type_val = f"Fertile Gangetic alluvium & clay loam ({loc_clean})"
            elif "uttar pradesh" in loc_lower or "meerut" in loc_lower or "lucknow" in loc_lower:
                location_note = f"Agro-Climatic Zone: Upper/Middle Gangetic Plains ({loc_clean}) — rich sandy-to-clay loam soils."
                if "sugarcane" in matched_crop_name.lower() or "wheat" in matched_crop_name.lower() or "potato" in matched_crop_name.lower():
                    soil_type_val = f"Deep fertile loam & clay loam ({loc_clean})"
            elif "maharashtra" in loc_lower or "pune" in loc_lower or "mumbai" in loc_lower:
                location_note = f"Agro-Climatic Zone: Western Plateau & Hills ({loc_clean}) — rich black cotton soil (Regur)."
                if "cotton" in matched_crop_name.lower() or "soyabean" in matched_crop_name.lower() or "jowar" in matched_crop_name.lower() or "sugarcane" in matched_crop_name.lower():
                    soil_type_val = f"Black cotton soil (Regur) & clay loam ({loc_clean})"
            elif "punjab" in loc_lower or "haryana" in loc_lower or "chandigarh" in loc_lower:
                location_note = f"Agro-Climatic Zone: Trans-Gangetic Plain ({loc_clean}) — highly productive canal & tubewell irrigated alluvium."
            elif "rajasthan" in loc_lower or "jaipur" in loc_lower:
                location_note = f"Agro-Climatic Zone: Western Dry / Semi-Arid Region ({loc_clean}) — light sandy loam with drip/sprinkler compatibility."
            elif "madhya pradesh" in loc_lower or "bhopal" in loc_lower:
                location_note = f"Agro-Climatic Zone: Central Plateau & Hills ({loc_clean}) — deep black and mixed red-black soils."
            elif "gujarat" in loc_lower or "ahmedabad" in loc_lower:
                location_note = f"Agro-Climatic Zone: Gujarat Plains & Hills ({loc_clean}) — alluvial and medium-to-deep black soils."
            elif "west bengal" in loc_lower or "kolkata" in loc_lower:
                location_note = f"Agro-Climatic Zone: Lower Gangetic Plain ({loc_clean}) — deltaic fertile alluvial soil with high moisture retention."
            elif "karnataka" in loc_lower or "bengaluru" in loc_lower:
                location_note = f"Agro-Climatic Zone: Southern Plateau & Hills ({loc_clean}) — red sandy loam and laterite soils."
            elif "telangana" in loc_lower or "hyderabad" in loc_lower or "andhra" in loc_lower:
                location_note = f"Agro-Climatic Zone: Southern Plateau ({loc_clean}) — red sandy (Chalka) and black soils."
            elif "tamil nadu" in loc_lower or "chennai" in loc_lower:
                location_note = f"Agro-Climatic Zone: East Coast Plains & Hills ({loc_clean}) — red loam and coastal alluvium."
            else:
                location_note = f"Planning tailored for regional agro-climatic conditions of {loc_clean}."

        return {
            "success": True,
            "crop_name": matched_crop_name,
            "season": plan_meta.get("season", "Kharif"),
            "sowing_period": plan_meta.get("sowing_period", "June – July"),
            "harvest_period": plan_meta.get("harvest_period", "October – November"),
            "temperature": plan_meta.get("temperature", "20 – 30°C"),
            "temp_desc": plan_meta.get("temp_desc", "Best growth occurs in mild to warm temperatures."),
            "rainfall": plan_meta.get("rainfall", "800 – 1200 mm"),
            "rainfall_desc": f"Requires {plan_meta.get('rainfall', 'adequate')} annual rainfall or supplemental irrigation.",
            "soil_type": soil_type_val,
            "soil_ph": plan_meta.get("soil_ph", "6.0 – 7.5"),
            "soil_ph_desc": "Soil should remain within the recommended pH range for optimal nutrient uptake.",
            "water_requirement": plan_meta.get("water_requirement", "Medium"),
            "water_desc": f"Crop water demand is {plan_meta.get('water_requirement', 'Medium')}.",
            "growing_duration": plan_meta.get("growing_duration", "100 – 130 Days"),
            "important_conditions": plan_meta.get("important_conditions", []),
            "farming_practices": plan_meta.get("farming_practices", []),
            "icon": plan_meta.get("icon", "fa-solid fa-seedling"),
            "status": status,
            "status_type": status_type,
            "status_badge": status_badge,
            "status_message": status_message,
            "next_window": next_window,
            "current_date": check_date.strftime("%d %B %Y"),
            "location": str(location).strip() if location else None,
            "location_note": location_note
        }

crop_service = CropRecommendationService()

