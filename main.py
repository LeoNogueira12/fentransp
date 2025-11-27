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

from pistao import PistonWidget
from otto import ciclo_otto_ideal

# =======================
# Constantes físicas
# =======================
R = 287.0
gamma = 1.4
cv = R / (gamma - 1)
# Parâmetros ocultos (modelo ideal)
T1_FIXO = 300.0
ALFA_FIXO = 3.35

# =======================
# GERAR CURVAS PV / PT
# =======================
def gerar_curvas(estados):
    P1, V1, T1 = estados["1"]
    P2, V2, T2 = estados["2"]
    P3, _, T3 = estados["3"]
    P4, _, T4 = estados["4"]

    v12 = np.linspace(V1, V2, 50)
    p12 = P1 * (V1 / v12) ** gamma

    v34 = np.linspace(V2, V1, 50)
    p34 = P3 * (V2 / v34) ** gamma

    v = np.concatenate([v12, [V2, V2], v34, [V1, V1]])
    p = np.concatenate([p12, [P2, P3], p34, [P4, P1]])

    T = p*v / R

    return v, p, T

# =======================
# INTERFACE
# =======================
class SiMo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador de Motores ideais")
        self.criar_interface()
        self.timer = QTimer()
        self.timer.timeout.connect(self.piston.update)

    def criar_interface(self):
        layout = QHBoxLayout()
        controls = QVBoxLayout()

        self.cilindrada = QLineEdit("2.0")
        self.cilindros = QLineEdit("4")
        self.compressao = QLineEdit("10")
        self.pressao = QLineEdit("101325")
        self.rpm = QLineEdit("3000")
        self.modo = QComboBox()
        self.modo.addItems(["Aspirado", "Turbo ideal"])

        for texto, campo in [
            ("Cilindrada total (L)", self.cilindrada),
            ("Cilindros", self.cilindros),
            ("Taxa de compressão", self.compressao),
            ("Pressão de admissão (Pa)", self.pressao),
            ("RPM", self.rpm),
            ("Modo", self.modo)
        ]:
            controls.addWidget(QLabel(texto))
            controls.addWidget(campo)

        btn = QPushButton("Simular")
        btn.clicked.connect(self.simular)
        controls.addWidget(btn)

        self.resultado = QLabel("")
        controls.addWidget(self.resultado)

        layout.addLayout(controls)

        graficos = QVBoxLayout()
        self.fig, self.ax = plt.subplots(1,2, figsize=(6,3))
        self.canvas = FigureCanvas(self.fig)

        graficos.addWidget(self.canvas)
        self.piston = PistonWidget()
        self.piston.setMinimumHeight(300)
        graficos.addWidget(self.piston)

        layout.addLayout(graficos)
        self.setLayout(layout)

    def simular(self):
        V = float(self.cilindrada.text())
        N = int(self.cilindros.text())
        r = float(self.compressao.text())
        P1 = float(self.pressao.text())
        T1=T1_FIXO
        alpha = ALFA_FIXO
        rpm = float(self.rpm.text())
        
        if self.modo.currentText() == "Turbo ideal":
            P1 *= 1.5   # aumento ideal de 50%

        estados, Qin, Qout, W, eta = ciclo_otto_ideal(P1, T1, r, alpha, V, N)
        freq = rpm / 120
        potencia = W * freq * N / 1000

        potencia_cv = (potencia*1000) / 735.5

        v, p, T = gerar_curvas(estados)

        self.ax[0].clear()
        self.ax[0].plot(v, p)
        self.ax[0].set_title("Diagrama P-V")
        self.ax[0].set_xlabel("Volume (m³)")
        self.ax[0].set_ylabel("Pressão (Pa)")

        self.ax[1].clear()
        self.ax[1].plot(T, p)
        self.ax[1].set_title("Diagrama P-T")
        self.ax[1].set_xlabel("Temperatura (K)")

        self.canvas.draw()

        self.resultado.setText(
            f"Potência estimada:\n"
            f"{potencia:.2f} kW\n"
            f"{potencia_cv:.1f} cv\n\n"
            f"Eficiência térmica ideal: {eta*100:.2f}%"
        )

        self.piston.set_rpm(rpm)
        self.timer.start(50)


# =======================
# EXECUÇÃO
# =======================
app = QApplication(sys.argv)
janela = SiMo()
janela.show()
sys.exit(app.exec())
