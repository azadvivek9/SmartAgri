"""
Crop Leaf Disease Detection - Transfer Learning Training Pipeline.
Uses TensorFlow / Keras with MobileNetV2 pre-trained on ImageNet.
Saves model to models/plant_disease_model.keras and class names to models/class_names.json.
"""

import os
import sys
import json
import argparse
from datetime import datetime

# Configure project paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DEFAULT_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'plant_disease_model.keras')
DEFAULT_CLASSES_PATH = os.path.join(BASE_DIR, 'models', 'class_names.json')

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, '.env'))
except ImportError:
    pass

CANDIDATE_DATA_DIRS = [
    os.path.join(os.path.expanduser('~'), 'Downloads', 'PlantVillage-Dataset-master', 'PlantVillage-Dataset-master', 'raw', 'color'),
    os.path.join(os.path.expanduser('~'), 'Downloads', 'PlantVillage-Dataset-master', 'raw', 'color'),
    os.path.join(os.path.expanduser('~'), 'Downloads', 'PlantVillage', 'raw', 'color'),
    os.path.join(os.path.expanduser('~'), 'Downloads', 'PlantVillage', 'color'),
    os.path.join(os.path.expanduser('~'), 'Downloads', 'PlantVillage'),
    os.path.join(BASE_DIR, 'data', 'PlantVillage', 'raw', 'color'),
    os.path.join(BASE_DIR, 'data', 'PlantVillage', 'color'),
    os.path.join(BASE_DIR, 'data', 'PlantVillage'),
    os.path.join(BASE_DIR, 'data', 'plantvillage'),
    os.path.join(BASE_DIR, 'data', 'PlantVillage-Dataset'),
    os.path.join(BASE_DIR, 'data', 'plant_village'),
    os.path.join(BASE_DIR, 'data', 'dataset'),
    os.path.join(BASE_DIR, 'data', 'plantvillage_dataset'),
    os.path.join(BASE_DIR, 'PlantVillage'),
    os.path.join(BASE_DIR, 'plantvillage')
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Train Crop Leaf Disease Detection Model with Transfer Learning (MobileNetV2)"
    )
    parser.add_argument(
        '--data_dir', '-d',
        type=str,
        default=os.environ.get('PLANTVILLAGE_DIR', ''),
        help="Path to PlantVillage dataset folder containing class subdirectories"
    )
    parser.add_argument(
        '--model_out', '-m',
        type=str,
        default=DEFAULT_MODEL_PATH,
        help="Path where trained .keras model will be saved (default: models/plant_disease_model.keras)"
    )
    parser.add_argument(
        '--classes_out', '-c',
        type=str,
        default=DEFAULT_CLASSES_PATH,
        help="Path where class_names.json will be saved (default: models/class_names.json)"
    )
    parser.add_argument(
        '--img_size',
        type=int,
        default=224,
        help="Input image height and width (default: 224)"
    )
    parser.add_argument(
        '--batch_size', '-b',
        type=int,
        default=32,
        help="Training batch size (default: 32)"
    )
    parser.add_argument(
        '--epochs', '-e',
        type=int,
        default=15,
        help="Number of initial training epochs (default: 15)"
    )
    parser.add_argument(
        '--fine_tune_epochs',
        type=int,
        default=5,
        help="Number of fine-tuning epochs (default: 5)"
    )
    parser.add_argument(
        '--learning_rate', '-lr',
        type=float,
        default=1e-3,
        help="Initial learning rate (default: 0.001)"
    )
    return parser.parse_args()


def _is_valid_dataset_dir(path):
    """Check if directory contains class subdirectories with image files."""
    if not os.path.isdir(path):
        return False
    subdirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) and not d.startswith('.')]
    # PlantVillage has multiple class folders (usually 38)
    return len(subdirs) >= 2


def find_dataset_dir(user_specified_dir=""):
    """Locate the dataset directory or check candidate locations."""
    if user_specified_dir:
        abs_path = os.path.abspath(user_specified_dir)
        if _is_valid_dataset_dir(abs_path):
            return abs_path
        # Check if user specified parent directory that has raw/color or color
        for sub in [os.path.join(abs_path, 'raw', 'color'), os.path.join(abs_path, 'color')]:
            if _is_valid_dataset_dir(sub):
                return os.path.abspath(sub)

    # Check candidate directories
    for path in CANDIDATE_DATA_DIRS:
        if _is_valid_dataset_dir(path):
            return os.path.abspath(path)

    return None


def main():
    args = parse_args()

    print("=" * 70)
    print("      AgriSmart Plant Disease Detection - Model Training      ")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. Check for TensorFlow installation
    try:
        import tensorflow as tf
        from tensorflow import keras
        from tensorflow.keras import layers
        from tensorflow.keras.applications import MobileNetV2
        from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
        print(f"[OK] TensorFlow Version: {tf.__version__}")
        print(f"[INFO] GPU Available: {bool(tf.config.list_physical_devices('GPU'))}")
    except ImportError:
        print("\n[ERROR] TensorFlow is not installed in your Python environment.")
        print("Please install TensorFlow using:")
        print("    pip install tensorflow pillow numpy")
        sys.exit(1)

    # 2. Locate Dataset
    dataset_path = find_dataset_dir(args.data_dir)
    if not dataset_path:
        print("\n" + "!" * 70)
        print("[DATASET NOT FOUND] PlantVillage dataset folder could not be located.")
        print("!" * 70)
        print("\nPlease provide the dataset in either of the following ways:")
        print("1. Place the PlantVillage dataset folder at:")
        print(f"   {os.path.join(BASE_DIR, 'data', 'PlantVillage')}")
        print("2. Or specify the path via command line argument:")
        print("   python ml/disease/train_model.py --data_dir /path/to/PlantVillage")
        print("3. Or set the PLANTVILLAGE_DIR environment variable:")
        print("   set PLANTVILLAGE_DIR=c:\\path\\to\\PlantVillage")
        print("=" * 70)
        sys.exit(1)

    print(f"[INFO] Dataset Directory Located: {dataset_path}")

    # Validate subdirectories
    classes = sorted([
        d for d in os.listdir(dataset_path)
        if os.path.isdir(os.path.join(dataset_path, d)) and not d.startswith('.')
    ])

    if not classes:
        print(f"[ERROR] No class subdirectories found inside: {dataset_path}")
        print("The dataset folder must contain subfolders for each crop disease class.")
        sys.exit(1)

    num_classes = len(classes)
    print(f"[INFO] Detected {num_classes} Disease/Healthy Classes.")

    img_size = (args.img_size, args.img_size)
    batch_size = args.batch_size

    # 3. Load Datasets (80% Train, 20% Validation)
    print("\n[STEP 1/4] Loading training & validation datasets...")
    train_ds = tf.keras.utils.image_dataset_from_directory(
        dataset_path,
        validation_split=0.2,
        subset="training",
        seed=42,
        image_size=img_size,
        batch_size=batch_size,
        label_mode='categorical'
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        dataset_path,
        validation_split=0.2,
        subset="validation",
        seed=42,
        image_size=img_size,
        batch_size=batch_size,
        label_mode='categorical'
    )

    class_names = train_ds.class_names
    print(f"[OK] Training batches: {len(train_ds)}, Validation batches: {len(val_ds)}")

    # 4. Save Class Names JSON
    os.makedirs(os.path.dirname(args.classes_out), exist_ok=True)
    with open(args.classes_out, 'w', encoding='utf-8') as f:
        json.dump(class_names, f, indent=2)
    print(f"[SAVED] Class names ({len(class_names)} classes) saved to: {args.classes_out}")

    # Optimize pipeline with streaming prefetch (avoids RAM OOM and shuffle buffer freeze on laptop)
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.prefetch(buffer_size=AUTOTUNE)

    # 5. Build Transfer Learning Model Architecture
    print("\n[STEP 2/4] Building Transfer Learning Architecture (MobileNetV2)...")
    
    data_augmentation = keras.Sequential([
        layers.RandomFlip("horizontal_and_vertical"),
        layers.RandomRotation(0.15),
        layers.RandomZoom(0.15),
    ], name="data_augmentation")

    base_model = MobileNetV2(
        input_shape=(args.img_size, args.img_size, 3),
        include_top=False,
        weights='imagenet'
    )
    base_model.trainable = False  # Freeze base feature extractor for fast & stable convergence

    inputs = keras.Input(shape=(args.img_size, args.img_size, 3), name="input_image")
    x = data_augmentation(inputs)
    x = preprocess_input(x)  # MobileNetV2 scales inputs from [-1, 1]
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D(name="avg_pool")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.3, name="dropout_1")(x)
    x = layers.Dense(256, activation='relu', name="dense_features")(x)
    x = layers.Dropout(0.2, name="dropout_2")(x)
    outputs = layers.Dense(num_classes, activation='softmax', name="disease_prediction")(x)

    model = keras.Model(inputs, outputs, name="CropDiseaseMobileNetV2")

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=args.learning_rate),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    model.summary(print_fn=lambda x: print(f"  {x}"))

    # Ensure output model directory exists before training
    os.makedirs(os.path.dirname(args.model_out), exist_ok=True)

    # Callbacks: Auto-saves best model on every epoch improvement
    callbacks = [
        keras.callbacks.ModelCheckpoint(
            filepath=args.model_out,
            monitor='val_accuracy',
            mode='max',
            save_best_only=True,
            verbose=1
        ),
        keras.callbacks.EarlyStopping(
            monitor='val_accuracy',
            patience=4,
            restore_best_weights=True,
            verbose=1
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=2,
            min_lr=1e-6,
            verbose=1
        )
    ]

    # 6. Train Feature Extractor Head
    print(f"\n[STEP 3/4] Training Classifier Head for {args.epochs} epochs...")
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=args.epochs,
        callbacks=callbacks,
        verbose=1
    )

    # 7. Fine-Tuning Phase (Optional Unfreeze Top Layers)
    if args.fine_tune_epochs > 0:
        print(f"\n[FINE-TUNING] Unfreezing top 20 layers of MobileNetV2 for {args.fine_tune_epochs} epochs...")
        base_model.trainable = True
        # Freeze all layers before the last 20
        for layer in base_model.layers[:-20]:
            layer.trainable = False

        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=1e-5),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

        history_fine = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=args.epochs + args.fine_tune_epochs,
            initial_epoch=len(history.history['loss']),
            callbacks=callbacks,
            verbose=1
        )

    # 8. Evaluate & Save Model
    print("\n[STEP 4/4] Evaluating and saving final model...")
    val_loss, val_acc = model.evaluate(val_ds, verbose=0)
    print(f"--> Final Validation Accuracy: {val_acc * 100:.2f}%")
    print(f"--> Final Validation Loss: {val_loss:.4f}")

    # Ensure best/final model is persisted to disk
    model.save(args.model_out)
    print(f"\n[SUCCESS] Model successfully saved to:")
    print(f"   --> {args.model_out}")
    print(f"   --> {args.classes_out}")
    print("=" * 70)


if __name__ == '__main__':
    main()
