import os
import numpy as np
import tensorflow as tf
from tensorflow_privacy.privacy.optimizers.dp_optimizer_keras import DPKerasAdamOptimizer
from tensorflow.keras.losses import BinaryCrossentropy
from tensorflow.keras.metrics import BinaryAccuracy, Precision, Recall, AUC
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau, TensorBoard
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from datetime import datetime
import json
import matplotlib.pyplot as plt

from cnn_model import build_model
from preprocessing import preprocess_image

# === Dataset directories ===
train_dir = os.path.join('data', 'train')
val_dir = os.path.join('data', 'val')

# === Data Generators ===
batch_size = 4
img_size = (128, 128)

train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.15,
    height_shift_range=0.15,
    zoom_range=0.15,
    horizontal_flip=True,
    brightness_range=[0.8, 1.2],
    fill_mode='nearest'
)
val_datagen = ImageDataGenerator(rescale=1./255)

train_gen = train_datagen.flow_from_directory(
    train_dir,
    target_size=img_size,
    color_mode='grayscale',
    batch_size=batch_size,
    class_mode='binary',
    shuffle=True
)
val_gen = val_datagen.flow_from_directory(
    val_dir,
    target_size=img_size,
    color_mode='grayscale',
    batch_size=batch_size,
    class_mode='binary',
    shuffle=False
)

# === Build Model ===
global_model_path = "global_latest.h5"
if os.path.exists(global_model_path):
    print(f"📥 Loading global model as initial model: {global_model_path}")
    model = tf.keras.models.load_model(global_model_path, compile=False)
else:
    print("⚠️ No global model found, building a new model from scratch")
    model = build_model()

# === Compile model ===
optimizer = DPKerasAdamOptimizer(
    l2_norm_clip=1.0,
    noise_multiplier=1.1,
    num_microbatches=batch_size,
    learning_rate=0.001
)
model.compile(
    optimizer=optimizer,
    loss=BinaryCrossentropy(from_logits=False, reduction=tf.keras.losses.Reduction.NONE),
    metrics=[BinaryAccuracy(), Precision(), Recall(), AUC()]
)

# === Callbacks ===
callbacks = [
    EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True, verbose=1),
    ModelCheckpoint('model_best.h5', save_best_only=True, monitor='val_loss', verbose=1),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-7, verbose=1),
    TensorBoard(log_dir=f'./logs/{datetime.now().strftime("%Y%m%d-%H%M%S")}', histogram_freq=1)
]

# === Train ===
history = model.fit(
    train_gen,
    steps_per_epoch=len(train_gen),
    validation_data=val_gen,
    validation_steps=len(val_gen),
    epochs=5,
    callbacks=callbacks,
    verbose=1
)

# === Evaluate best validation accuracy ===
best_val_acc = max(history.history['val_binary_accuracy'])
accuracy_threshold = 0.7
print(f"\n🎯 Best Validation Accuracy: {best_val_acc:.4f}")

# === Save model if above threshold ===
if best_val_acc >= accuracy_threshold:
    model.save('model_final.h5')
    print("✅ Final model saved as model_final.h5")
    model.save('model_best.h5')
    print("✅ Best model saved as model_best.h5")
else:
    print("❌ Model accuracy below threshold, not saving")
    if os.path.exists('model_best.h5'):
        os.remove('model_best.h5')
    if os.path.exists('model_final.h5'):
        os.remove('model_final.h5')

# === Update metadata.json with num_samples, address, val_accuracy ===
metadata = {
    "num_samples": train_gen.samples,
    "address": "0xAC35B995FE7Bb8FcdA4b3fc2D209fb1fCbdc4345",  # update per node
    "val_accuracy": float(best_val_acc),
    "name": "nodeA",
    "timestamp": datetime.now().isoformat()
}
with open("metadata.json", "w") as f:
    json.dump(metadata, f)
print("📄 Updated metadata.json with validation accuracy")

# === Send model to PoCL server if training was successful ===
if best_val_acc >= accuracy_threshold:
    print("\n🚀 Training completed successfully! Sending model to PoCL server...")
    try:
        from file_transfer_client import FileTransferClient
        
        # Configuration - Update these for your Tailscale setup
        POCL_HOST = "100.64.0.1"  # Replace with actual PoCL Tailscale IP
        POCL_PORT = 8888
        
        client = FileTransferClient(POCL_HOST, POCL_PORT)
        
        # Check if PoCL server is reachable
        if client.check_pocl_server_status():
            print(f"✅ PoCL server is reachable at {POCL_HOST}:{POCL_PORT}")
            
            # Send model and metadata
            if client.send_model_and_metadata():
                print("🎉 Model successfully sent to PoCL server!")
            else:
                print("⚠️ Failed to send model to PoCL server")
                print("💡 You can manually send the model later using file_transfer_client.py")
        else:
            print(f"❌ PoCL server is not reachable at {POCL_HOST}:{POCL_PORT}")
            print("💡 Please ensure:")
            print("   1. PoCL server is running (file_transfer_server.py)")
            print("   2. Tailscale is connected")
            print("   3. Correct IP address and port")
            print("💡 You can manually send the model later using file_transfer_client.py")
            
    except ImportError:
        print("⚠️ file_transfer_client.py not found - skipping automatic transfer")
        print("💡 You can manually send the model using the file transfer client")
    except Exception as e:
        print(f"⚠️ Error during automatic transfer: {e}")
        print("💡 You can manually send the model later using file_transfer_client.py")
else:
    print("❌ Model accuracy below threshold - not sending to PoCL server")

# === Optional: plot training metrics (same as before) ===
plt.figure(figsize=(15, 10))
plt.subplot(2, 3, 1)
plt.plot(history.history['binary_accuracy'], label='Train Acc')
plt.plot(history.history['val_binary_accuracy'], label='Val Acc')
plt.title('Model Accuracy')
plt.legend()
plt.subplot(2, 3, 2)
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Val Loss')
plt.title('Model Loss')
plt.legend()
plt.subplot(2, 3, 3)
plt.plot(history.history['precision'], label='Train Precision')
plt.plot(history.history['val_precision'], label='Val Precision')
plt.title('Precision')
plt.legend()
plt.subplot(2, 3, 4)
plt.plot(history.history['recall'], label='Train Recall')
plt.plot(history.history['val_recall'], label='Val Recall')
plt.title('Recall')
plt.legend()
plt.subplot(2, 3, 5)
plt.plot(history.history['auc'], label='Train AUC')
plt.plot(history.history['val_auc'], label='Val AUC')
plt.title('AUC')
plt.legend()
plt.tight_layout()
plt.savefig('training_metrics.png', dpi=300)
print("📊 Saved training_metrics.png")
