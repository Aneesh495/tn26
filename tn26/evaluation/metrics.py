"""Scoring rules, calibration metrics, and loss functions for electoral probabilistic forecasts."""
from typing import Dict, List, Optional
import numpy as np
import pandas as pd


class ElectoralEvaluationMetrics:
    """Calculates proper scoring rules, Brier scores, and calibration diagnostics."""

    @staticmethod
    def multiclass_brier_score(probabilities: np.ndarray, one_hot_actual: np.ndarray) -> float:
        """Compute proper Brier Score:
        BS = (1 / N) * sum_i sum_k (p_{ik} - y_{ik})^2
        Lower is better; 0 indicates perfect probability calibration.
        """
        n = probabilities.shape[0]
        diff = probabilities - one_hot_actual
        bs = np.sum(diff ** 2) / float(n)
        return round(float(bs), 4)

    @staticmethod
    def multiclass_log_loss(probabilities: np.ndarray, one_hot_actual: np.ndarray, eps: float = 1e-15) -> float:
        """Compute multiclass cross-entropy log-loss:
        Loss = - (1 / N) * sum_i sum_k y_{ik} * log(p_{ik})
        """
        n = probabilities.shape[0]
        clipped = np.clip(probabilities, eps, 1.0 - eps)
        loss = - np.sum(one_hot_actual * np.log(clipped)) / float(n)
        return round(float(loss), 4)

    @staticmethod
    def expected_calibration_error(
        probabilities: np.ndarray,
        actual_labels: np.ndarray,
        n_bins: int = 10,
    ) -> float:
        """Compute Expected Calibration Error (ECE) partitioning predicted confidences into bins."""
        confidences = np.max(probabilities, axis=1)
        predictions = np.argmax(probabilities, axis=1)
        accuracies = (predictions == actual_labels)

        bin_boundaries = np.linspace(0.0, 1.0, n_bins + 1)
        ece = 0.0
        n = len(actual_labels)

        for i in range(n_bins):
            in_bin = (confidences > bin_boundaries[i]) & (confidences <= bin_boundaries[i + 1])
            prop_in_bin = np.mean(in_bin)
            if prop_in_bin > 0:
                accuracy_in_bin = np.mean(accuracies[in_bin])
                avg_confidence_in_bin = np.mean(confidences[in_bin])
                ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin

        return round(float(ece), 4)

    @staticmethod
    def mean_absolute_seat_error(predicted_seats: Dict[str, int], actual_seats: Dict[str, int]) -> float:
        """Compute Mean Absolute Seat Error across parties."""
        errors = [abs(predicted_seats.get(p, 0) - actual_seats.get(p, 0)) for p in actual_seats]
        return round(float(np.mean(errors)), 2)
