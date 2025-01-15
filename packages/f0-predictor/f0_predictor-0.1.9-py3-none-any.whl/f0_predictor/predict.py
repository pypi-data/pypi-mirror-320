# f0_predictor/predict.py
import torch
import numpy as np
import parselmouth
from .model import F0PredictionModel
from .smoother import ViterbiF0Smoother

def predict_f0_for_audio(audio_path, model, scaler, sequence_length=50, batch_size=128):
    """Predict F0 contour for a new audio file with Viterbi smoothing."""
    time_stamps, original_f0 = extract_f0_for_prediction(audio_path)
    predictions = np.zeros_like(original_f0)

    # Process in chunks to reduce memory usage
    chunk_size = 1000  # Process 1000 frames at a time

    for chunk_start in range(0, len(original_f0), chunk_size):
        chunk_end = min(chunk_start + chunk_size, len(original_f0))
        chunk_length = chunk_end - chunk_start

        # Prepare sequences for this chunk
        sequences = np.zeros((chunk_length, sequence_length))
        for i in range(chunk_length):
            start_idx = max(0, chunk_start + i - sequence_length // 2)
            end_idx = start_idx + sequence_length
            if end_idx > len(original_f0):
                start_idx = len(original_f0) - sequence_length
                end_idx = len(original_f0)
            sequences[i] = original_f0[start_idx:end_idx]

        # Scale sequences
        sequences_scaled = sequences.reshape(-1, sequence_length, 1)
        non_zero_mask = sequences_scaled > 0
        if np.any(non_zero_mask):
            sequences_scaled[non_zero_mask] = scaler.transform(
                sequences_scaled[non_zero_mask].reshape(-1, 1)).reshape(-1)

        # Batch predictions
        model.eval()
        with torch.no_grad():
            for i in range(0, len(sequences), batch_size):
                batch = sequences_scaled[i:i+batch_size]
                batch_tensor = torch.FloatTensor(batch).to(next(model.parameters()).device)

                batch_predictions = model(batch_tensor)
                batch_predictions = scaler.inverse_transform(batch_predictions.cpu().numpy())
                predictions[chunk_start+i:chunk_start+i+batch_size] = batch_predictions.flatten()

    # Apply Viterbi smoothing
    smoother = ViterbiF0Smoother()
    smoothed_predictions = smoother.smooth(predictions, original_f0)

    return time_stamps, smoothed_predictions, original_f0

def extract_f0_for_prediction(audio_path, time_step=0.01, pitch_floor=75, pitch_ceiling=600):
    sound = parselmouth.Sound(audio_path)
    pitch = sound.to_pitch(time_step=time_step, pitch_floor=pitch_floor, pitch_ceiling=pitch_ceiling)
    pitch_values = pitch.selected_array['frequency']
    time_stamps = pitch.xs()
    pitch_values[pitch_values == 0] = 0
    return time_stamps, pitch_values

def main(audio_path, model_path=None, output_plot_path=None):
    """Main function to run the F0 prediction pipeline with Viterbi smoothing."""
    from .model import load_or_create_model
    from .utils import plot_waveform_and_f0, evaluate_prediction
    
    # Load audio using parselmouth
    sound = parselmouth.Sound(audio_path)

    # Load or create model
    model, scaler, sequence_length = load_or_create_model(model_path)

    # Use GPU if available
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)

    # Make predictions with Viterbi smoothing
    time_stamps, predictions, original_f0 = predict_f0_for_audio(
        audio_path, model, scaler, sequence_length=sequence_length
    )

    # Plot results with waveform
    plot_waveform_and_f0(sound, time_stamps, original_f0, predictions, output_plot_path)

    # Calculate metrics
    metrics = evaluate_prediction(original_f0, predictions)
    if metrics:
        print("\nPrediction Metrics:")
        for metric_name, value in metrics.items():
            print(f"{metric_name}: {value:.2f}")

    return time_stamps, predictions, original_f0