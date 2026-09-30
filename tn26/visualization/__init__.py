"""Publication-grade visualization suite for the tn26 research platform."""
from tn26.visualization.style import apply_academic_style
from tn26.visualization.maps_and_choropleths import RegionalSeatVisualizer
from tn26.visualization.flow_diagrams import VoterFlowVisualizer
from tn26.visualization.diagnostic_plots import ForensicDiagnosticPlots

__all__ = [
    "apply_academic_style",
    "RegionalSeatVisualizer",
    "VoterFlowVisualizer",
    "ForensicDiagnosticPlots",
]
