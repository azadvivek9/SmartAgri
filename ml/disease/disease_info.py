"""
Plant Pathology Knowledge Base & Class Metadata.
Provides detailed agronomic descriptions, symptoms, recommended treatments,
and prevention strategies for PlantVillage dataset classes.
"""

# Knowledge catalog for all 38 PlantVillage classes
PLANT_DISEASE_CATALOG = {
    # ------------------ APPLE ------------------
    "Apple___Apple_scab": {
        "crop": "Apple",
        "disease": "Apple Scab (Venturia inaequalis)",
        "is_healthy": False,
        "symptoms": [
            "Olive-green to black velvety spots on upper leaf surfaces",
            "Leaves turn yellow, curl, and drop prematurely (defoliation)",
            "Sunken, corky brown scabs and deformation on developing fruit",
            "Stunted shoot development and reduced tree vigor"
        ],
        "recommended_action": [
            "Apply Captan 50% WP @ 2.5 g/L or Mancozeb 75% WP @ 2.5 g/L at green tip and petal fall stages.",
            "In case of active lesion spread, apply systemic fungicides like Difenoconazole 25% EC @ 0.5 ml/L.",
            "Rake and shred or burn fallen leaves in autumn to eliminate overwintering fungal ascospores."
        ],
        "prevention": "Plant scab-resistant cultivars (e.g., Enterprise, Liberty) and maintain open canopy pruning for air circulation."
    },
    "Apple___Black_rot": {
        "crop": "Apple",
        "disease": "Black Rot / Frogeye Leaf Spot (Botryosphaeria obtusa)",
        "is_healthy": False,
        "symptoms": [
            "Small purple specks that enlarge into circular 'frogeye' spots with dark margins and light centers",
            "Firm, brown rotting fruit lesions with concentric rings turning black with pycnidia",
            "Cankers on twigs and large branches that gird fruit-bearing limbs"
        ],
        "recommended_action": [
            "Prune out dead wood, fire blight strikes, and cankered limbs at least 15 cm below visible infection.",
            "Apply Thiophanate-methyl 70% WP @ 1 g/L or Captan from pink bud stage through harvest.",
            "Remove and destroy all mummified fruit hanging on trees or lying on the orchard floor."
        ],
        "prevention": "Maintain tree vigor with balanced soil nutrition, prevent mechanical bark injuries, and sterilize pruning tools."
    },
    "Apple___Cedar_apple_rust": {
        "crop": "Apple",
        "disease": "Cedar Apple Rust (Gymnosporangium juniperi-virginianae)",
        "is_healthy": False,
        "symptoms": [
            "Bright yellow-orange circular lesions on upper leaf surfaces surrounded by red border",
            "Raised tube-like aecia (spore cups) protruding from the underside of leaves",
            "Premature defoliation and small, distorted, unmarketable fruit"
        ],
        "recommended_action": [
            "Apply Myclobutanil 10% WP @ 1 g/L or Mancozeb 75% WP @ 2.5 g/L from tight cluster until petal fall.",
            "Eradicate nearby Eastern Red Cedar or juniper trees within a 1-2 km radius if feasible.",
            "Remove visible rust galls from nearby ornamental junipers before early spring rains."
        ],
        "prevention": "Grow rust-resistant apple varieties (e.g., Freedom, Redfree, Liberty) and monitor nearby cedar stands."
    },
    "Apple___healthy": {
        "crop": "Apple",
        "disease": "Healthy Apple Specimen",
        "is_healthy": True,
        "symptoms": [
            "Deep green, intact foliage with crisp leaf margins and healthy cuticle layer",
            "Uniform chlorophyll distribution with zero chlorotic spots or fungal lesions",
            "Vigorous shoot extension and firm leaf turgidity"
        ],
        "recommended_action": [
            "Maintain regular orchard scouting and balanced N-P-K + micronutrient fertilization.",
            "Ensure regular irrigation scheduling during fruit swell and dry periods.",
            "Apply prophylactic calcium spray to prevent bitter pit in developing apples."
        ],
        "prevention": "Continue seasonal dormant oil sprays, clean sanitation, and balanced tree canopy management."
    },

    # ------------------ BLUEBERRY ------------------
    "Blueberry___healthy": {
        "crop": "Blueberry",
        "disease": "Healthy Blueberry Specimen",
        "is_healthy": True,
        "symptoms": [
            "Lush green, waxy leaves free of spotty discoloration or margin necrosis",
            "Active vegetative terminal growth and strong root-soil symbiotic balance",
            "No signs of stem canker or mummy berry fungal structures"
        ],
        "recommended_action": [
            "Maintain soil pH in the acidic range (4.5 – 5.5) using elemental sulfur or peat moss.",
            "Apply organic pine bark mulch to preserve root zone moisture and inhibit weeds.",
            "Ensure steady drip irrigation with low-salinity water."
        ],
        "prevention": "Continue standard acidophilic fertilizer management and seasonal fruit sanitation."
    },

    # ------------------ CHERRY ------------------
    "Cherry_(including_sour)___Powdery_mildew": {
        "crop": "Cherry",
        "disease": "Cherry Powdery Mildew (Podosphaera clandestina)",
        "is_healthy": False,
        "symptoms": [
            "White talcum powder-like circular patches of mycelium on young leaves and green shoots",
            "Infected leaves curl upward, distort, blister, and become brittle",
            "Poor fruit set, fruit discoloration, and unmarketable surface blemishes"
        ],
        "recommended_action": [
            "Spray Wettable Sulfur 80% WP @ 3 g/L or Myclobutanil @ 0.5 ml/L at first sign of powdery patches.",
            "In organic orchards, apply Potassium Bicarbonate @ 3-4 g/L or Neem oil (10,000 ppm) @ 2 ml/L.",
            "Prune inner branches to improve canopy sunlight exposure and reduce micro-humidity."
        ],
        "prevention": "Avoid excess nitrogen fertilizer that promotes dense succulent growth vulnerable to fungal penetration."
    },
    "Cherry_(including_sour)___healthy": {
        "crop": "Cherry",
        "disease": "Healthy Cherry Specimen",
        "is_healthy": True,
        "symptoms": [
            "Glossy, vibrant green foliage with distinct serrated margins",
            "Zero fungal mycelia, leaf spot lesions, or gummosis cankers",
            "Optimal branch vigor and healthy flower/fruit development"
        ],
        "recommended_action": [
            "Apply balanced fruit tree fertilizer with adequate zinc, boron, and potassium.",
            "Maintain drip irrigation and avoid wetting the trunk or lower foliage.",
            "Inspect regularly for early aphid or borer infestation."
        ],
        "prevention": "Keep good orchard sanitation, dormant copper applications, and routine pruning."
    },

    # ------------------ CORN (MAIZE) ------------------
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "crop": "Corn (Maize)",
        "disease": "Gray Leaf Spot (Cercospora zeae-maydis)",
        "is_healthy": False,
        "symptoms": [
            "Small tan spots that expand into elongated, rectangular lesions bounded by leaf veins",
            "Lesions turn grayish-brown with yellow chlorotic halos in humid weather",
            "Extensive blighting of upper photosynthetic leaves leading to premature plant death and lodging"
        ],
        "recommended_action": [
            "Apply strobilurin or triazole fungicides (e.g., Azoxystrobin + Difenoconazole @ 1 ml/L) at tasseling stage.",
            "Avoid planting continuous corn; rotate with non-host crops like soybean or pulses.",
            "Practice deep tillage where appropriate to bury infected crop debris."
        ],
        "prevention": "Select high-yielding hybrids with proven genetic resistance to Cercospora leaf spot."
    },
    "Corn_(maize)___Common_rust_": {
        "crop": "Corn (Maize)",
        "disease": "Common Corn Rust (Puccinia sorghi)",
        "is_healthy": False,
        "symptoms": [
            "Small, oval to elongated cinnamon-brown pustules scattered across both upper and lower leaf surfaces",
            "Pustules rupture epidermal tissue, releasing powdery golden-brown rust spores",
            "Severe chlorosis, leaf death, and reduced kernel size under cool, humid conditions"
        ],
        "recommended_action": [
            "Foliar application of Propiconazole 25% EC (Tilt) @ 1 ml/L or Pyraclostrobin @ 1 ml/L.",
            "Spray when pustules first appear on leaves before pollination.",
            "Ensure proper field drainage to prevent localized high canopy moisture."
        ],
        "prevention": "Plant resistant corn hybrids and avoid ultra-late season planting schedules."
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "crop": "Corn (Maize)",
        "disease": "Northern Corn Leaf Blight (Exserohilum turcicum)",
        "is_healthy": False,
        "symptoms": [
            "Long, elliptical, cigar-shaped grayish-green to tan lesions (2.5 – 15 cm long)",
            "Lesions merge, causing extensive scorched leaf appearance across the field canopy",
            "Dark olive fungal sporulation visible within lesions during wet mornings"
        ],
        "recommended_action": [
            "Apply Mancozeb 75% WP @ 2.5 g/L or Azoxystrobin + Propiconazole formulation @ 1 ml/L.",
            "Prioritize fungicide application between V8 stage and 2 weeks post-silking if weather is wet.",
            "Incorporate crop residues into soil post-harvest to reduce fungal inoculum."
        ],
        "prevention": "Plant corn hybrids with Ht-gene multi-race resistance and implement 2-year crop rotation."
    },
    "Corn_(maize)___healthy": {
        "crop": "Corn (Maize)",
        "disease": "Healthy Corn Specimen",
        "is_healthy": True,
        "symptoms": [
            "Robust, deep green broad leaf blades with prominent, clean central midribs",
            "Absence of necrotic lesions, rust pustules, or leaf striping",
            "Strong vegetative stalk girth and active photosynthetic efficiency"
        ],
        "recommended_action": [
            "Apply split nitrogen doses (basal, knee-high, and pre-tasseling stages).",
            "Maintain soil moisture during critical silking and grain-filling periods.",
            "Monitor for Fall Armyworm and stem borer using pheromone traps."
        ],
        "prevention": "Ensure balanced soil N-P-K nutrition, optimum plant density, and weed-free field borders."
    },

    # ------------------ GRAPE ------------------
    "Grape___Black_rot": {
        "crop": "Grape",
        "disease": "Grape Black Rot (Guignardia bidwellii)",
        "is_healthy": False,
        "symptoms": [
            "Small circular reddish-brown leaf spots with dark margins and tiny black dots (pycnidia)",
            "Infected berries develop light brown soft spots, shrivel rapidly, and turn into hard, black mummies",
            "Black elliptical lesions on young green shoots and tendrils"
        ],
        "recommended_action": [
            "Apply Mancozeb 75% WP @ 2.5 g/L or Myclobutanil 10% WP @ 1 g/L from bud break to 4 weeks post-bloom.",
            "Remove and destroy all mummified berries from vines and ground during winter pruning.",
            "Canopy shoot thinning to facilitate airflow and rapid drying after morning dews."
        ],
        "prevention": "Select well-drained vineyard sites with good sun exposure and practice rigorous canopy management."
    },
    "Grape___Esca_(Black_Measles)": {
        "crop": "Grape",
        "disease": "Esca / Black Measles (Phaeoacremonium / Fomitiporia complex)",
        "is_healthy": False,
        "symptoms": [
            "Interveinal chlorosis and necrosis creating a distinctive 'tiger-stripe' leaf pattern",
            "Dark purple to black speckling on berry skins resembling measles",
            "Wood discolored in cross-section with yellowish-white spongy wood decay and sudden vine apoplexy"
        ],
        "recommended_action": [
            "Disinfect all pruning shears with 70% alcohol or 10% bleach between individual vines.",
            "Apply pruning wound sealants containing fungicides (e.g., pyraclostrobin or copper paste).",
            "Prune late in the dormant season when wound healing is rapid."
        ],
        "prevention": "Avoid making large pruning wounds during wet weather and replace severely debilitated vines."
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "crop": "Grape",
        "disease": "Isariopsis Leaf Spot / Grape Leaf Blight (Pseudocercospora cladosporioides)",
        "is_healthy": False,
        "symptoms": [
            "Irregular, angular dark brown to black spots on upper leaf surfaces",
            "Dark olive-green velvety fungal growth on the underside of corresponding leaf spots",
            "Severe leaf yellowing, early defoliation, and decreased sugar accumulation in grape clusters"
        ],
        "recommended_action": [
            "Spray Copper Oxychloride 50% WP @ 2.5 g/L or Azoxystrobin @ 1 ml/L upon disease detection.",
            "Ensure complete spray penetration through the fruiting zone and inner canopy.",
            "Destroy fallen vineyard leaf debris to eliminate fungal survival structures."
        ],
        "prevention": "Maintain vine training system to ensure high canopy aeration and reduce humidity around bunches."
    },
    "Grape___healthy": {
        "crop": "Grape",
        "disease": "Healthy Grape Specimen",
        "is_healthy": True,
        "symptoms": [
            "Vibrant green, multi-lobed leaves with smooth intact lamina and clear veins",
            "No signs of powdery mildew, downy mildew, or berry black rot",
            "Vigorous shoot growth with strong tendril formation"
        ],
        "recommended_action": [
            "Maintain balanced vineyard fertigation (potassium and magnesium support berry quality).",
            "Execute summer shoot positioning, leaf removal around grape clusters, and suckering.",
            "Keep soil well-drained and maintain cover crops between rows."
        ],
        "prevention": "Continue preventative IPM fungicide schedule and post-harvest vine maintenance."
    },

    # ------------------ ORANGE ------------------
    "Orange___Haunglongbing_(Citrus_greening)": {
        "crop": "Orange (Citrus)",
        "disease": "Citrus Greening / Huanglongbing (Candidatus Liberibacter)",
        "is_healthy": False,
        "symptoms": [
            "Asymmetrical, blotchy mottled yellow patterns across leaf veins (not matching zinc deficiency)",
            "Leaves become small, upright, and thickened with yellow raised veins",
            "Small, lopsided, bitter fruit that remains green at the stylar end and drops prematurely",
            "Severe branch dieback and eventual tree mortality"
        ],
        "recommended_action": [
            "Control the Asian Citrus Psyllid vector with Imidacloprid 17.8% SL @ 0.5 ml/L or Thiamethoxam.",
            "Immediately remove and eradicate severely infected trees to prevent orchard-wide transmission.",
            "Apply foliar nutritional sprays (Zinc, Manganese, Boron, Potassium) to prolong productive life of mild trees."
        ],
        "prevention": "Plant only certified disease-free nursery stock from insect-proof screenhouses."
    },

    # ------------------ PEACH ------------------
    "Peach___Bacterial_spot": {
        "crop": "Peach",
        "disease": "Bacterial Spot (Xanthomonas campestris pv. pruni)",
        "is_healthy": False,
        "symptoms": [
            "Small, water-soaked polygonal spots turning purple-brown, drying, and falling out ('shot-hole' effect)",
            "Leaves turn yellow and drop prematurely, leaving twigs bare",
            "Deep, pitted, cracked lesions and gum exudation on peach fruit surface"
        ],
        "recommended_action": [
            "Apply Copper Hydroxide or Copper Sulfate during late dormancy and early post-bloom stages.",
            "Apply Oxytetracycline bactericide sprays during warm, humid bloom and fruit set periods.",
            "Avoid excessive nitrogen fertilization which produces susceptible vegetative flush."
        ],
        "prevention": "Select resistant peach cultivars and avoid planting in sandy, wind-exposed soil sites."
    },
    "Peach___healthy": {
        "crop": "Peach",
        "disease": "Healthy Peach Specimen",
        "is_healthy": True,
        "symptoms": [
            "Elongated, lanceolate deep-green leaves with clean margins and zero shot-holes",
            "Smooth bark on shoots with no gummosis, bacterial cankers, or leaf curl",
            "Healthy fruit development with intact skin velvet"
        ],
        "recommended_action": [
            "Maintain annual open-center pruning to allow full sun penetration.",
            "Ensure regular irrigation during fruit stone hardening and sizing.",
            "Apply dormant lime-sulfur or copper spray in late winter to prevent leaf curl."
        ],
        "prevention": "Consistent orchard floor weed management and seasonal scouting for peach tree borers."
    },

    # ------------------ PEPPER (BELL) ------------------
    "Pepper,_bell___Bacterial_spot": {
        "crop": "Pepper (Bell)",
        "disease": "Bacterial Leaf Spot (Xanthomonas vesicatoria)",
        "is_healthy": False,
        "symptoms": [
            "Small, circular to irregular water-soaked spots on leaves turning dark brown with pale centers",
            "Severe lower leaf yellowing and rapid defoliation exposing fruit to sunscald",
            "Raised, rough, blister-like corky scabs on bell pepper fruit"
        ],
        "recommended_action": [
            "Spray Copper Oxychloride 50% WP @ 2.5 g/L combined with Streptocycline 100 ppm (1g in 10L water).",
            "Immediately remove and safely dispose of heavily infected individual plants.",
            "Avoid overhead sprinkler irrigation; use drip lines to keep canopy completely dry."
        ],
        "prevention": "Use certified hot-water treated seeds, resistant pepper hybrids, and practice 2-3 year solanaceous rotation."
    },
    "Pepper,_bell___healthy": {
        "crop": "Pepper (Bell)",
        "disease": "Healthy Pepper Specimen",
        "is_healthy": True,
        "symptoms": [
            "Broad, dark green glossy leaves with intact veins and zero leaf spots",
            "Vigorous branching structure with healthy floral buds and fruit set",
            "No leaf cupping, mosaic mottling, or viral distortion"
        ],
        "recommended_action": [
            "Provide balanced fertilizer with calcium and magnesium to prevent blossom end rot.",
            "Stake or trellis pepper plants to keep heavy fruit off the soil surface.",
            "Maintain uniform soil moisture using organic or plastic mulch."
        ],
        "prevention": "Routine scouting for thrips and aphids to prevent vectoring of spotted wilt viruses."
    },

    # ------------------ POTATO ------------------
    "Potato___Early_blight": {
        "crop": "Potato",
        "disease": "Potato Early Blight (Alternaria solani)",
        "is_healthy": False,
        "symptoms": [
            "Dark brown to black necrotic spots with concentric rings creating a 'target board' pattern",
            "Spots surrounded by chlorotic yellow halos on mature lower leaves first",
            "Extensive foliar drying and brown dry rot lesions on potato tubers"
        ],
        "recommended_action": [
            "Spray Mancozeb 75% WP @ 2.5 g/L or Chlorothalonil 75% WP @ 2 g/L at first appearance of spots.",
            "For active spread, apply systemic fungicides like Difenoconazole 25% EC @ 0.5 ml/L or Azoxystrobin.",
            "Ensure adequate nitrogen and potassium fertilization to prevent premature crop senescence."
        ],
        "prevention": "Practice 3-year crop rotation with non-solanaceous crops and use certified disease-free seed tubers."
    },
    "Potato___Late_blight": {
        "crop": "Potato",
        "disease": "Potato Late Blight (Phytophthora infestans)",
        "is_healthy": False,
        "symptoms": [
            "Water-soaked, dark green to purplish-black rapidly expanding lesions on leaf tips and margins",
            "Delicate white cottony mold/mildew visible on the underside of lesions in cool, humid mornings",
            "Rapid collapse and rotting of entire haulms with a foul odor; brown granular rot inside tubers"
        ],
        "recommended_action": [
            "Apply systemic fungicides: Metalaxyl 8% + Mancozeb 64% WP (Ridomil MZ) @ 2.5 g/L or Cymoxanil @ 2 g/L.",
            "Spray proactively when weather is overcast, cool (15-22°C), and relative humidity >90%.",
            "Destroy and burn blighted potato haulms 10-14 days before harvest to protect tubers."
        ],
        "prevention": "Plant resistant cultivars (e.g., Kufri Girdhari, Kufri Jyoti), ensure high earthing up, and avoid excessive irrigation."
    },
    "Potato___healthy": {
        "crop": "Potato",
        "disease": "Healthy Potato Specimen",
        "is_healthy": True,
        "symptoms": [
            "Vigorous, dense green canopy with clean, undamaged compound leaves",
            "Zero water-soaked blighted margins, target spots, or viral crinkling",
            "Strong root and stolon network with active tuber initiation"
        ],
        "recommended_action": [
            "Execute proper earthing up at 30-35 days after planting to cover developing tubers.",
            "Maintain steady moisture during tuber initiation and bulking stages.",
            "Apply prophylactic copper spray before monsoon or foggy winter spells."
        ],
        "prevention": "Use certified seed tubers, treat seeds with Trichoderma viride, and maintain clean field sanitation."
    },

    # ------------------ RASPBERRY ------------------
    "Raspberry___healthy": {
        "crop": "Raspberry",
        "disease": "Healthy Raspberry Specimen",
        "is_healthy": True,
        "symptoms": [
            "Compound leaves with bright green color, distinct serrated edges, and clean underside",
            "Healthy primocanes and floricanes with intact bark and no spur blight cankers",
            "Vigorous blossom set and berry development"
        ],
        "recommended_action": [
            "Prune spent floricanes immediately after harvesting to improve air circulation.",
            "Maintain trellis support system to keep canes off the damp ground.",
            "Provide drip irrigation and mulch to keep the shallow root system moist."
        ],
        "prevention": "Ensure good drainage to avoid Phytophthora root rot and apply dormant lime sulfur."
    },

    # ------------------ SOYBEAN ------------------
    "Soybean___healthy": {
        "crop": "Soybean",
        "disease": "Healthy Soybean Specimen",
        "is_healthy": True,
        "symptoms": [
            "Trifoliate leaves with vibrant, uniform green color and velvety pubescence",
            "No rust pustules, frog-eye leaf spots, or bacterial blight lesions",
            "Strong nodulation on taproot and vigorous pod formation"
        ],
        "recommended_action": [
            "Maintain weed-free conditions during the first 45 days after sowing.",
            "Scout for defoliating caterpillars and stem flies; use yellow sticky traps.",
            "Ensure adequate soil phosphorus and potassium for optimal nitrogen fixation."
        ],
        "prevention": "Treat seeds with Rhizobium and Trichoderma, and practice crop rotation with cereals."
    },

    # ------------------ SQUASH ------------------
    "Squash___Powdery_mildew": {
        "crop": "Squash",
        "disease": "Squash Powdery Mildew (Podosphaera xanthii)",
        "is_healthy": False,
        "symptoms": [
            "White talc-like powdery spots expanding across both upper and lower leaf surfaces and petioles",
            "Leaves turn chlorotic yellow, brown, and dry up brittle ('paper-like')",
            "Premature vine decline resulting in sunscalded, tasteless, low-yield squash fruit"
        ],
        "recommended_action": [
            "Spray Wettable Sulfur 80% WP @ 3 g/L or Azoxystrobin 23% SC @ 1 ml/L upon initial white spot emergence.",
            "Apply organic bio-fungicides such as Potassium Bicarbonate @ 3 g/L or Horticultural Neem Oil @ 2.5 ml/L.",
            "Prune overcrowded older canopy leaves to enhance sunlight penetration and aeration."
        ],
        "prevention": "Plant powdery mildew-resistant squash hybrids and avoid overhead sprinkler watering."
    },

    # ------------------ STRAWBERRY ------------------
    "Strawberry___Leaf_scorch": {
        "crop": "Strawberry",
        "disease": "Strawberry Leaf Scorch (Diplocarpon earlianum)",
        "is_healthy": False,
        "symptoms": [
            "Numerous small, irregular purple to dark brown spots on upper leaf surfaces",
            "Spots enlarge and coalesce, causing entire leaf to appear scorched, burnt, and curled",
            "Lesions extend to petioles, calyxes, and fruit runners, reducing strawberry yield"
        ],
        "recommended_action": [
            "Apply Captan 50% WP @ 2.5 g/L or Myclobutanil @ 0.5 ml/L after post-harvest renovation.",
            "Remove and destroy heavily scorched foliage during annual bed renovation.",
            "Ensure plants are spaced at 20-25 cm in raised beds to minimize leaf dampness."
        ],
        "prevention": "Plant scorch-tolerant strawberry varieties, use clean drip irrigation, and refresh straw mulch."
    },
    "Strawberry___healthy": {
        "crop": "Strawberry",
        "disease": "Healthy Strawberry Specimen",
        "is_healthy": True,
        "symptoms": [
            "Lush trifoliate leaves with deep green color and healthy serrations",
            "Clean crowns and runners with zero crown rot, leaf spot, or powdery mildew",
            "Abundant, uniform white flowering and conical red fruit development"
        ],
        "recommended_action": [
            "Maintain raised beds with clean pine needle or straw mulching.",
            "Provide regular fertigation with balanced N-P-K and calcium for fruit firmness.",
            "Inspect underside of leaves weekly for two-spotted spider mites."
        ],
        "prevention": "Use certified virus-indexed runner plants and avoid overhead evening irrigations."
    },

    # ------------------ TOMATO ------------------
    "Tomato___Bacterial_spot": {
        "crop": "Tomato",
        "disease": "Tomato Bacterial Spot (Xanthomonas perforans)",
        "is_healthy": False,
        "symptoms": [
            "Small (less than 3 mm), dark brown water-soaked angular spots on leaves",
            "Centers of older leaf spots frequently dry and tear away, leaving ragged holes",
            "Blister-like raised dark scabs on tomato fruits surrounded by white halos"
        ],
        "recommended_action": [
            "Apply Copper Oxychloride 50% WP @ 2.5 g/L + Streptocycline 100 ppm (1g in 10L water) weekly during wet weather.",
            "Avoid working in the tomato field when foliage is wet from rain or morning dew.",
            "Sterilize tomato stakes, trellis wires, and pruning shears before reuse."
        ],
        "prevention": "Use hot-water treated disease-free seeds and implement 2-3 year rotation away from solanaceous crops."
    },
    "Tomato___Early_blight": {
        "crop": "Tomato",
        "disease": "Tomato Early Blight (Alternaria solani)",
        "is_healthy": False,
        "symptoms": [
            "Circular dark brown spots with characteristic concentric rings ('bulls-eye' pattern) on older lower leaves",
            "Yellow chlorotic zone surrounding individual leaf lesions",
            "Progressive defoliation from base upwards, exposing tomatoes to sunscald",
            "Dark, sunken, leathery cankers on stems near the soil line"
        ],
        "recommended_action": [
            "Spray Mancozeb 75% WP @ 2.5 g/L or Chlorothalonil 75% WP @ 2 g/L at the first sign of lower leaf spots.",
            "In case of advanced spread, apply Difenoconazole 25% EC @ 0.5 ml/L or Azoxystrobin @ 1 ml/L.",
            "Prune off infected lower leaves up to 30 cm above ground level and destroy them."
        ],
        "prevention": "Stake plants, apply straw/plastic mulch to stop rain-splash, and practice 3-year crop rotation."
    },
    "Tomato___Late_blight": {
        "crop": "Tomato",
        "disease": "Tomato Late Blight (Phytophthora infestans)",
        "is_healthy": False,
        "symptoms": [
            "Large, irregular water-soaked pale to dark green lesions on leaves that turn brown and papery",
            "Delicate white fungal mold visible on the underside of affected leaves in cool, damp conditions",
            "Dark brown to black lesions on stems and greasy, firm brown marbling on green tomato fruits"
        ],
        "recommended_action": [
            "Immediately apply Metalaxyl 8% + Mancozeb 64% WP @ 2.5 g/L or Cymoxanil + Mancozeb @ 2 g/L.",
            "Spray proactively when temperatures are 15–22°C with persistent rainfall or dense fog.",
            "Remove and incinerate severely blighted plants to stop rapid airborne spore dispersal."
        ],
        "prevention": "Avoid overhead watering, ensure generous plant spacing for rapid drying, and choose resistant hybrids."
    },
    "Tomato___Leaf_Mold": {
        "crop": "Tomato",
        "disease": "Tomato Leaf Mold (Passalora fulva / Cladosporium)",
        "is_healthy": False,
        "symptoms": [
            "Pale green to yellowish indistinct patches on the upper surface of older leaves",
            "Dense, velvety olive-green to grayish-brown fungal spores coating the underside of corresponding spots",
            "Leaves wither, curl, turn brown, and drop prematurely in high humidity (>85%)"
        ],
        "recommended_action": [
            "Foliar spray of Copper Hydroxide @ 2 g/L or Azoxystrobin @ 1 ml/L.",
            "Maximize greenhouse or polytunnel ventilation to reduce relative humidity below 80%.",
            "Prune dense inner foliage to facilitate continuous airflow through the canopy."
        ],
        "prevention": "Grow resistant tomato varieties (with Cf-genes) and maintain heated airflow in covered structures."
    },
    "Tomato___Septoria_leaf_spot": {
        "crop": "Tomato",
        "disease": "Septoria Leaf Spot (Septoria lycopersici)",
        "is_healthy": False,
        "symptoms": [
            "Numerous small (2-3 mm) circular spots with dark brown margins and light gray/tan centers",
            "Tiny black specks (pycnidia) visible inside the center of mature lesions under magnification",
            "Rapid yellowing and drop of affected leaves starting from the bottom of the plant"
        ],
        "recommended_action": [
            "Spray Mancozeb 75% WP @ 2.5 g/L or Chlorothalonil 75% WP @ 2 g/L every 7-10 days in wet seasons.",
            "Prune off infected lower leaves touching the soil surface.",
            "Install mulch around plant bases to prevent soil-to-leaf water splashing."
        ],
        "prevention": "Destroy all tomato vine residue post-harvest and maintain 2-year crop rotation."
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "crop": "Tomato",
        "disease": "Two-Spotted Spider Mite Infestation (Tetranychus urticae)",
        "is_healthy": False,
        "symptoms": [
            "Fine yellow or white stippling (speckling) across the upper leaf surface",
            "Delicate silky web webbing visible on the underside of leaves and branch axils",
            "Leaves turn bronze or yellow, dry out, and drop; severe stunted plant growth during hot dry weather"
        ],
        "recommended_action": [
            "Foliar application of Spiromesifen 22.9% SC @ 1 ml/L or Abamectin 1.8% EC @ 0.5 ml/L.",
            "Spray underside of leaves thoroughly where mites colonize.",
            "Introduce predatory mites (Phytoseiulus persimilis) in greenhouse environments as biological control."
        ],
        "prevention": "Avoid broad-spectrum synthetic pyrethroids that kill natural mite predators, and keep field borders weed-free."
    },
    "Tomato___Target_Spot": {
        "crop": "Tomato",
        "disease": "Tomato Target Spot (Corynespora cassiicola)",
        "is_healthy": False,
        "symptoms": [
            "Small pinpoint brown spots that expand into circular lesions with light brown centers and dark borders",
            "Concentric rings frequently visible within older spots, resembling target boards",
            "Premature defoliation and sunken, dark brown circular lesions on tomato fruit"
        ],
        "recommended_action": [
            "Spray Azoxystrobin + Difenoconazole @ 1 ml/L or Chlorothalonil 75% WP @ 2 g/L.",
            "Avoid overhead irrigation; maintain dry canopy conditions.",
            "Remove diseased crop debris immediately to reduce inoculum density."
        ],
        "prevention": "Ensure good row spacing and avoid planting tomato next to other host crops like cucumber or cotton."
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "crop": "Tomato",
        "disease": "Tomato Yellow Leaf Curl Virus (TYLCV)",
        "is_healthy": False,
        "symptoms": [
            "Severe upward curling and cupping of leaf margins with prominent chlorotic (yellow) borders",
            "Leaves become noticeably reduced in size, thick, and leathery",
            "Severe plant stunting, bushy erect appearance, and massive flower drop with zero fruit set"
        ],
        "recommended_action": [
            "Control whitefly (Bemisia tabaci) vector with Diafenthiuron 50% WP @ 1 g/L or Thiamethoxam 25% WG @ 0.3 g/L.",
            "Install yellow sticky traps (15-20 traps per acre) across the field to monitor and trap whiteflies.",
            "Rogue out and destroy infected viral plants immediately in airtight plastic bags."
        ],
        "prevention": "Plant TYLCV-resistant hybrids, use 50-mesh insect-proof netting in nurseries, and practice clean field borders."
    },
    "Tomato___Tomato_mosaic_virus": {
        "crop": "Tomato",
        "disease": "Tomato Mosaic Virus (ToMV)",
        "is_healthy": False,
        "symptoms": [
            "Mottled light and dark green mosaic patterns across foliage blades",
            "Leaf distortion, 'shoestring' or fern-like thinning of leaflets, and blistered leaf surface",
            "Uneven ripening and brown internal necrotic browning inside tomato fruit walls"
        ],
        "recommended_action": [
            "No chemical cure exists for viral pathogens; rogue and destroy infected plants immediately.",
            "Wash hands thoroughly with soap/water and dip tools in 20% non-fat dry milk solution before handling plants.",
            "Do not smoke or use tobacco products near tomato crops (tobacco carries mosaic virus)."
        ],
        "prevention": "Use certified virus-free seed stock, resistant varieties (Tm-2 gene), and sanitize all greenhouse surfaces."
    },
    "Tomato___healthy": {
        "crop": "Tomato",
        "disease": "Healthy Tomato Specimen",
        "is_healthy": True,
        "symptoms": [
            "Vibrant, dark green compound leaves with healthy pubescence and firm turgor",
            "Zero chlorotic spots, mosaic mottling, fungal lesions, or marginal curling",
            "Strong central leader stem with vigorous flowering trusses and uniform fruit set"
        ],
        "recommended_action": [
            "Maintain consistent drip irrigation to prevent blossom end rot and fruit splitting.",
            "Prune side suckers regularly and tie vines securely to sturdy stakes or trellises.",
            "Provide balanced potassium and calcium fertigation during fruit development."
        ],
        "prevention": "Continue preventative crop scouting, companion planting (marigolds), and balanced fertilization."
    }
}


def parse_class_name(raw_class_name: str) -> dict:
    """
    Parse a raw folder or class label into crop and disease components.
    Handles PlantVillage format (e.g., 'Tomato___Early_blight') as well as
    variations like 'Tomato_Early_blight' or 'Tomato Early Blight'.
    """
    if not raw_class_name:
        return {"crop": "Unknown", "disease": "Unknown Disease", "is_healthy": False}

    cleaned = raw_class_name.strip()

    # Direct match in catalog
    if cleaned in PLANT_DISEASE_CATALOG:
        entry = PLANT_DISEASE_CATALOG[cleaned]
        return {
            "crop": entry["crop"],
            "disease": entry["disease"],
            "is_healthy": entry["is_healthy"]
        }

    # Split by '___' or '__'
    if "___" in cleaned:
        parts = cleaned.split("___", 1)
    elif "__" in cleaned:
        parts = cleaned.split("__", 1)
    else:
        parts = cleaned.split("_", 1) if "_" in cleaned else [cleaned, ""]

    crop_part = parts[0].replace("_", " ").strip()
    disease_part = parts[1].replace("_", " ").strip() if len(parts) > 1 else ""

    # Clean up crop name
    if "Cherry" in crop_part:
        crop_name = "Cherry"
    elif "Corn" in crop_part:
        crop_name = "Corn (Maize)"
    elif "Pepper" in crop_part:
        crop_name = "Pepper (Bell)"
    else:
        crop_name = crop_part.capitalize()

    # Clean up disease name
    is_healthy = "healthy" in disease_part.lower() or disease_part == ""
    if is_healthy:
        disease_name = f"Healthy {crop_name} Specimen"
    else:
        disease_name = disease_part.title() if disease_part else "Foliar Plant Disorder"

    return {
        "crop": crop_name,
        "disease": disease_name,
        "is_healthy": is_healthy
    }


def get_disease_info(class_name: str) -> dict:
    """
    Retrieve comprehensive diagnosis info (symptoms, treatment, prevention)
    for a given class name. If class is not explicitly in catalog,
    intelligently constructs an accurate agronomic profile.
    """
    if class_name in PLANT_DISEASE_CATALOG:
        item = PLANT_DISEASE_CATALOG[class_name]
        return {
            "crop": item["crop"],
            "disease": item["disease"],
            "is_healthy": item["is_healthy"],
            "symptoms": item["symptoms"],
            "recommended_action": item["recommended_action"],
            "prevention": item["prevention"]
        }

    # Fallback / parsed class
    parsed = parse_class_name(class_name)
    crop = parsed["crop"]
    disease = parsed["disease"]
    is_healthy = parsed["is_healthy"]

    if is_healthy:
        symptoms = [
            f"Vibrant, natural chlorophyll coloration across {crop} leaf surface",
            "Smooth intact cuticle with no fungal pustules, necrotic spots, or halos",
            "Optimal leaf turgor and active photosynthetic canopy development"
        ]
        treatment = [
            f"Maintain standard balanced N-P-K fertilization according to {crop} growth stage.",
            "Continue regular moisture monitoring to avoid drought or waterlogging stress.",
            "Perform weekly scouting on leaf undersides for proactive pest management."
        ]
        prevention = "Continue good agronomic hygiene, clean weeding, and proper irrigation."
    else:
        symptoms = [
            f"Visible foliar lesions, discoloration, or spotting characteristic of {disease} on {crop}",
            "Disruption of normal photosynthetic tissue leading to localized chlorosis or necrosis",
            "Risk of canopy decline and yield loss if left unmanaged"
        ]
        treatment = [
            f"Isolate affected {crop} foliage and apply suitable broad-spectrum fungicide or bactericide spray.",
            "Avoid overhead irrigation to keep leaf blades dry and prevent spore germination.",
            "Prune heavily infected lower leaves and safely dispose of infected crop residues."
        ]
        prevention = f"Practice 2-3 year crop rotation, use certified disease-free seeds, and ensure good field drainage for {crop}."

    return {
        "crop": crop,
        "disease": disease,
        "is_healthy": is_healthy,
        "symptoms": symptoms,
        "recommended_action": treatment,
        "prevention": prevention
    }
