# f0_predictor/utils.py
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Optional, Union

import matplotlib.pyplot as plt
import numpy as np


def plot_waveform_and_f0(sound, time_stamps, original_f0, predicted_f0, save_path=None):
    """Plot waveform and F0 contours in a combined figure with synchronized x-axes."""
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(30, 10), height_ratios=[1, 2], sharex=True)

    # Plot waveform in top subplot
    samples = sound.values.squeeze()
    time = np.arange(len(samples)) / sound.sampling_frequency
    ax1.plot(time, samples, color='gray', alpha=0.6, linewidth=0.5)
    ax1.set_ylabel('Amplitude')
    ax1.set_title('Waveform')
    ax1.grid(True)

    # Plot F0 contours in bottom subplot
    ax2.plot(time_stamps, original_f0, label='Original F0', alpha=0.6, marker="o", linestyle="-", markersize=3)
    ax2.plot(time_stamps, predicted_f0, label='Predicted F0 (Viterbi)', alpha=0.6, marker="o", linestyle="-", markersize=3)
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Frequency (Hz)')
    ax2.set_title('F0 Contour Comparison with Viterbi Smoothing')
    ax2.legend()
    ax2.grid(True)

    # Adjust layout to prevent overlap
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=1200, bbox_inches='tight')
    plt.show()


def evaluate_prediction(
    original_f0: np.ndarray,
    predicted_f0: np.ndarray
) -> Optional[Dict[str, float]]:
    voiced_mask = original_f0 > 0
    if np.sum(voiced_mask) == 0:
        return None

    original_voiced = original_f0[voiced_mask]
    predicted_voiced = predicted_f0[voiced_mask]

    mse = np.mean((original_voiced - predicted_voiced) ** 2)
    rmse = np.sqrt(mse)
    mae = np.mean(np.abs(original_voiced - predicted_voiced))

    return {'MSE': mse, 'RMSE': rmse, 'MAE': mae}