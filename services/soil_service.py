class SoilService:
    def analyze(self, ph, nitrogen, phosphorus, potassium, organic_carbon=0.65, moisture=55.0, soil_type="Alluvial Loam"):
        """
        Analyze soil parameters and generate scientific fertilizer & irrigation guidance.
        """
        # 1. pH evaluation
        if ph < 5.5:
            ph_status = "Strongly Acidic"
            ph_badge = "badge-danger"
            ph_advice = "Soil acidity reduces availability of Phosphorus and Molybdenum. Apply Agricultural Lime (Calcium Carbonate) @ 250-400 kg/acre."
        elif ph < 6.2:
            ph_status = "Moderately Acidic"
            ph_badge = "badge-warning"
            ph_advice = "Mildly acidic; incorporate well-rotted Farm Yard Manure (FYM) and avoid excessive ammonium-based fertilizers."
        elif ph <= 7.5:
            ph_status = "Optimal / Neutral"
            ph_badge = "badge-success"
            ph_advice = "Ideal pH range for maximum nutrient availability and beneficial soil microbial activity."
        elif ph <= 8.2:
            ph_status = "Moderately Alkaline"
            ph_badge = "badge-warning"
            ph_advice = "Slightly alkaline. Apply Agricultural Gypsum (150-200 kg/acre) and green manure (Dhaincha/Sunhemp) to buffer pH."
        else:
            ph_status = "Strongly Alkaline / Saline"
            ph_badge = "badge-danger"
            ph_advice = "High sodicity/salinity restricts Micronutrient uptake (Zinc, Iron). Apply Gypsum with deep flushing and sulfur."

        # 2. Nitrogen evaluation (kg/ha equivalent)
        if nitrogen < 50:
            n_status = "Low"
            n_badge = "badge-danger"
            n_level_pct = 35
        elif nitrogen <= 100:
            n_status = "Normal"
            n_badge = "badge-success"
            n_level_pct = 75
        else:
            n_status = "High"
            n_badge = "badge-info"
            n_level_pct = 95

        # 3. Phosphorus evaluation (kg/ha equivalent)
        if phosphorus < 25:
            p_status = "Low"
            p_badge = "badge-danger"
            p_level_pct = 30
        elif phosphorus <= 60:
            p_status = "Normal"
            p_badge = "badge-success"
            p_level_pct = 70
        else:
            p_status = "High"
            p_badge = "badge-info"
            p_level_pct = 92

        # 4. Potassium evaluation (kg/ha equivalent)
        if potassium < 120:
            k_status = "Low"
            k_badge = "badge-danger"
            k_level_pct = 32
        elif potassium <= 280:
            k_status = "Normal"
            k_badge = "badge-success"
            k_level_pct = 80
        else:
            k_status = "High"
            k_badge = "badge-info"
            k_level_pct = 96

        # 5. Organic Carbon evaluation (%)
        if organic_carbon < 0.4:
            oc_status = "Low"
            oc_badge = "badge-danger"
        elif organic_carbon <= 0.75:
            oc_status = "Medium / Normal"
            oc_badge = "badge-success"
        else:
            oc_status = "Rich / High"
            oc_badge = "badge-success"

        # 6. Overall Health Score Calculation (0 - 100)
        score = 100
        if ph_status != "Optimal / Neutral": score -= 15
        if n_status == "Low": score -= 18
        elif n_status == "High": score -= 5
        if p_status == "Low": score -= 15
        elif p_status == "High": score -= 5
        if k_status == "Low": score -= 12
        if oc_status == "Low": score -= 15
        
        score = max(35, min(98, score))
        if score >= 80:
            health_category = "Good / Optimal"
            health_color = "#2d6a4f"
        elif score >= 60:
            health_category = "Moderate — Needs Balanced Nutrition"
            health_color = "#d97706"
        else:
            health_category = "Poor — Requires Active Soil Amendment"
            health_color = "#dc2626"

        # 7. Fertilizer Recommendations
        fert_recommendations = []
        if n_status == "Low":
            fert_recommendations.append({
                'name': 'Urea (46% N) & Neem Coated Urea',
                'nutrient': 'Nitrogen (N)',
                'dosage': '45 - 55 kg / Acre',
                'timing': 'Apply in 2-3 split doses: 1/3 at basal, 1/3 at active tillering, 1/3 before panicle initiation.',
                'icon': 'fa-solid fa-flask-vial'
            })
        elif n_status == "Normal":
            fert_recommendations.append({
                'name': 'Balanced Urea Top-Dressing',
                'nutrient': 'Nitrogen (N)',
                'dosage': '25 - 30 kg / Acre',
                'timing': 'Apply during peak vegetative flush only. Do not exceed to avoid excessive succulent foliage.',
                'icon': 'fa-solid fa-flask-vial'
            })

        if p_status == "Low":
            fert_recommendations.append({
                'name': 'Single Super Phosphate (SSP 16% P2O5) / DAP',
                'nutrient': 'Phosphorus (P) + Calcium + Sulfur',
                'dosage': '50 - 75 kg / Acre (SSP) OR 30 kg / Acre (DAP)',
                'timing': 'Apply 100% as basal dose placed 4-5 cm below seed depth during sowing/transplanting.',
                'icon': 'fa-solid fa-cubes'
            })
        elif p_status == "Normal":
            fert_recommendations.append({
                'name': 'Maintenance DAP / SSP',
                'nutrient': 'Phosphorus (P)',
                'dosage': '25 kg / Acre',
                'timing': 'Apply at field preparation / basal incorporation.',
                'icon': 'fa-solid fa-cubes'
            })

        if k_status == "Low" or k_status == "Normal":
            fert_recommendations.append({
                'name': 'Muriate of Potash (MOP 60% K2O)',
                'nutrient': 'Potassium (K)',
                'dosage': '20 - 30 kg / Acre',
                'timing': 'Split: 50% basal + 50% at flowering/grain filling to boost resistance and grain weight.',
                'icon': 'fa-solid fa-gem'
            })

        # Organic amendment
        fert_recommendations.append({
            'name': 'Well-Decomposed Farm Yard Manure (FYM) / Vermicompost',
            'nutrient': 'Organic Carbon & Soil Microbiome',
            'dosage': '2 - 3 Tonnes / Acre (FYM) OR 500 kg / Acre (Vermicompost)',
            'timing': 'Spread evenly 15-20 days prior to final field plowing.',
            'icon': 'fa-solid fa-seedling'
        })

        # 8. Precautions
        precautions = [
            "Never mix Urea with SSP directly in advance; mix only at the time of field broadcasting.",
            "Avoid applying nitrogen fertilizer during midday heat or when heavy downpours are imminent.",
            "Incorporate phosphatic fertilizers deep into the root zone because phosphorus is relatively immobile in soil.",
            "For light sandy/loam soils, always prefer split application of Nitrogen and Potash to prevent leaching losses."
        ]

        # 9. Irrigation Guidance based on moisture
        if moisture < 40:
            irrigation_status = "Dry — Irrigation Immediately Required"
            irrigation_badge = "badge-danger"
            water_need = "High (60-70 mm)"
            irrigation_timing = "Schedule morning or evening flood/sprinkler irrigation within 24 hours."
            moisture_desc = f"Soil moisture is at {moisture}%, well below the field capacity threshold."
        elif moisture <= 65:
            irrigation_status = "Optimal Moisture Level"
            irrigation_badge = "badge-success"
            water_need = "Maintenance (20-30 mm)"
            irrigation_timing = "No immediate irrigation needed. Next check in 3-4 days based on weather forecast."
            moisture_desc = f"Soil moisture is healthy at {moisture}%, providing ideal capillary water to root zones."
        else:
            irrigation_status = "Saturated / Excessive Moisture"
            irrigation_badge = "badge-warning"
            water_need = "Drainage / Nil"
            irrigation_timing = "Do NOT irrigate. Ensure field drainage channels are unblocked to prevent root asphyxiation."
            moisture_desc = f"Soil moisture is high ({moisture}%). Temporary aeration required."

        return {
            'health_score': score,
            'health_category': health_category,
            'health_color': health_color,
            'soil_type': soil_type,
            'ph': {
                'value': ph,
                'status': ph_status,
                'badge': ph_badge,
                'advice': ph_advice
            },
            'nitrogen': {
                'value': nitrogen,
                'status': n_status,
                'badge': n_badge,
                'pct': n_level_pct
            },
            'phosphorus': {
                'value': phosphorus,
                'status': p_status,
                'badge': p_badge,
                'pct': p_level_pct
            },
            'potassium': {
                'value': potassium,
                'status': k_status,
                'badge': k_badge,
                'pct': k_level_pct
            },
            'organic_carbon': {
                'value': organic_carbon,
                'status': oc_status,
                'badge': oc_badge
            },
            'moisture': {
                'value': moisture,
                'status': irrigation_status,
                'badge': irrigation_badge,
                'water_need': water_need,
                'timing': irrigation_timing,
                'desc': moisture_desc
            },
            'fertilizers': fert_recommendations,
            'precautions': precautions
        }
