import sys
import os
import numpy as np
import matplotlib.pyplot as plt

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QComboBox, QVBoxLayout, QHBoxLayout, QGroupBox, QSlider
)
from PyQt6.QtCore import QTimer, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QLinearGradient, QFontDatabase

# =======================
# Constantes físicas
# =======================
R = 287.0
k = 1.4
cv = R / (k - 1)
T1_FIXO = 300.0
ALFA_FIXO = 3.35

# =======================
# CÁLCULOS CICLO OTTO
# =======================
def ciclo_otto_ideal(P1, T1, r, alpha, V_total, Ncyl):
    Vd = (V_total / 1000) / Ncyl 
    Vc = Vd / (r - 1)
    V1 = Vd + Vc
    V2 = Vc

    m = (P1 * V1) / (R * T1)

    T2 = T1 * r**(k-1)
    P2 = P1 * r**k

    T3 = alpha * T2
    P3 = P2 * alpha

    T4 = T3 / r**(k-1)
    P4 = P3 / r**k

    Qin = m * cv * (T3 - T2)
    Qout = m * cv * (T4 - T1)
    W = Qin - Qout

    eta = 1 - 1/(r**(k-1))

    estados = {
        "1": (P1, V1, T1),
        "2": (P2, V2, T2),
        "3": (P3, V2, T3),
        "4": (P4, V1, T4)
    }

    return estados, Qin, Qout, W, eta
