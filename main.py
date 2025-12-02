import sys
import numpy as np
import matplotlib.pyplot as plt

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QComboBox, QVBoxLayout, QHBoxLayout
)
from PyQt6.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


from pistao import PistonWidget
from otto import ciclo_otto_ideal
from atkinson import ciclo_atkinson_ideal, gerar_curvas_atkinson
from diesel import ciclo_diesel_ideal, gerar_curvas_diesel

# Constantes
R = 287.0
k = 1.4
cv = R / (k - 1)
T1_FIXO = 300.0
ALFA_FIXO = 3.35  

def gerar_curvas_otto(estados):
    """Curvas para ciclo Otto"""
    P1, V1, T1 = estados["1"]
    P2, V2, T2 = estados["2"]
    P3, _, T3 = estados["3"]
    P4, _, T4 = estados["4"]

    # Admissão (0->1) - pressão constante
    v_adm = np.linspace(V1*0.2, V1, 25)
    p_adm = np.full_like(v_adm, P1)
    t_adm = np.full_like(v_adm, T1)

    # Compressão (1->2)
    v12 = np.linspace(V1, V2, 50)
    p12 = P1 * (V1 / v12) ** k
    t12 = T1 * (V1 / v12) ** (k - 1)

    # Combustão (2->3) - volume constante
    v23 = np.full(25, V2)
    p23 = np.linspace(P2, P3, 25)
    t23 = np.linspace(T2, T3, 25)

    # Expansão (3->4)
    v34 = np.linspace(V2, V1, 50)
    p34 = P3 * (V2 / v34) ** k
    t34 = T3 * (V2 / v34) ** (k - 1)

    # Exaustão (4->1) - volume constante
    v_exh = np.full(25, V1)
    p_exh = np.linspace(P4, P1, 25)
    t_exh = np.linspace(T4, T1, 25)

    v = np.concatenate([v_adm, v12, v23, v34, v_exh])
    p = np.concatenate([p_adm, p12, p23, p34, p_exh])
    T = np.concatenate([t_adm, t12, t23, t34, t_exh])

    return v, p, T


class SiMo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador de Motores - Multi Ciclo")
        self.criar_interface()
        self.timer = QTimer()
        self.timer.timeout.connect(self.piston.update)

    def criar_interface(self):
        layout = QHBoxLayout()
        
        # Painel de controles (largura fixa)
        controls = QVBoxLayout()
        controls_widget = QWidget()
        controls_widget.setLayout(controls)
        controls_widget.setMaximumWidth(300)  # Largura fixa de 300px

        # Seletor de ciclo
        self.tipo_ciclo = QComboBox()
        self.tipo_ciclo.addItems(["Otto", "Atkinson", "Diesel"])
        self.tipo_ciclo.currentTextChanged.connect(self.mudar_ciclo)
        
        self.cilindrada = QLineEdit("2.0")
        self.cilindros = QComboBox()
        self.cilindros.addItems(["I3","I4","I5","V6","V8","V10","V12","W16"])
        self.compressao = QLineEdit("10")
        self.pressao = QLineEdit("101325")
        self.rpm = QLineEdit("3000")
        self.modo = QComboBox()
        self.modo.addItems(["Aspirado", "Turbo"])

        for texto, campo in [
            ("Tipo de Ciclo", self.tipo_ciclo),
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
        
        # Botão Pause/Play
        self.btn_pause = QPushButton("Pausar Animação")
        self.btn_pause.clicked.connect(self.toggle_pause)
        self.btn_pause.setEnabled(False)  
        controls.addWidget(self.btn_pause)
        
        self.animacao_pausada = False

        self.resultado = QLabel("")
        controls.addWidget(self.resultado)
        
        # Adiciona o widget de controles ao layout principal
        layout.addWidget(controls_widget)

        # Gráficos e animação
        graficos = QVBoxLayout()
        graficos_widget = QWidget()
        graficos_widget.setLayout(graficos)
        self.fig, self.ax = plt.subplots(1, 2, figsize=(6, 3))
        self.canvas = FigureCanvas(self.fig)

        graficos.addWidget(self.canvas)
        self.piston = PistonWidget()
        self.piston.setMinimumHeight(300)
        graficos.addWidget(self.piston)

        # Adiciona gráficos ao layout principal com stretch
        layout.addWidget(graficos_widget, 1)  
        self.setLayout(layout)
        
    def mudar_ciclo(self, ciclo_nome):
        """Atualiza o pistão quando muda o ciclo"""
        self.piston.set_cycle_type(ciclo_nome.lower())
        
        # Ajusta valores padrão por ciclo
        if ciclo_nome == "Diesel":
            self.compressao.setText("18")  
        elif ciclo_nome == "Atkinson":
            self.compressao.setText("12")
        else:
            self.compressao.setText("10")
    
    def toggle_pause(self):
        """Pausa/despausa a animação"""
        if self.animacao_pausada:
            self.timer.start(50)
            self.btn_pause.setText("Pausar Animação")
            self.animacao_pausada = False
        else:
            self.timer.stop()
            self.btn_pause.setText("Continuar Animação")
            self.animacao_pausada = True

    def simular(self):
        V = float(self.cilindrada.text())
        N = int(self.cilindros.currentText()[1:])
        r = float(self.compressao.text())
        P1 = float(self.pressao.text())
        T1 = T1_FIXO
        alpha = ALFA_FIXO
        rpm = float(self.rpm.text())
        
        if self.modo.currentText() == "Turbo":
            P1 *= 1.5

        ciclo_tipo = self.tipo_ciclo.currentText().lower()
        
        # Executa o ciclo apropriado
        if ciclo_tipo == "atkinson":
            r_exp = r * 1.25
            estados, Qin, Qout, W, eta, _ = ciclo_atkinson_ideal(P1, T1, r, r_exp, alpha, V, N)
            v, p, T = gerar_curvas_atkinson(estados, r, r_exp)
        elif ciclo_tipo == "diesel":
            rc = 2.0
            estados, Qin, Qout, W, eta, _ = ciclo_diesel_ideal(P1, T1, r, rc, V, N)
            v, p, T = gerar_curvas_diesel(estados, rc)
        else:  # Otto
            estados, Qin, Qout, W, eta_ideal = ciclo_otto_ideal(P1, T1, r, alpha, V, N)
            eta = eta_ideal  
            v, p, T = gerar_curvas_otto(estados)

        freq = rpm / 120
        potencia = W * freq * N / 1000
        potencia_cv = (potencia * 1000) / 735.5

        # Atualiza gráficos
        # Volume por cilindro (não total)
        self.ax[0].clear()
        self.ax[0].plot(v * 1000, p / 1000, 'b-', linewidth=2)  # Volume em Litros
        self.ax[0].fill(v * 1000, p / 1000, alpha=0.2)
        self.ax[0].set_title(f"Diagrama P-V ({ciclo_tipo.title()})")
        self.ax[0].set_xlabel("Volume por Cilindro (L)")
        self.ax[0].set_ylabel("Pressão (kPa)")
        self.ax[0].grid(True, alpha=0.3)

        self.ax[1].clear()
        self.ax[1].plot(T, p / 1000, 'r-', linewidth=2)  # Pressão em kPa
        self.ax[1].set_title(f"Diagrama P-T ({ciclo_tipo.title()})")
        self.ax[1].set_xlabel("Temperatura (K)")
        self.ax[1].set_ylabel("Pressão (kPa)")
        self.ax[1].grid(True, alpha=0.3)

        self.canvas.draw()

        self.resultado.setText(
            f"Ciclo: {ciclo_tipo.upper()}\n"
            f"Potência estimada:\n"
            f"{potencia:.2f} kW\n"
            f"{potencia_cv:.1f} cv\n\n"
            f"Eficiência térmica: {eta*100:.2f}%\n"
            f"Trabalho/ciclo: {W:.1f} J"
        )

        self.piston.set_rpm(rpm)
        self.piston.set_cycle_type(ciclo_tipo)
        self.btn_pause.setEnabled(True)  # Habilita o botão de pause
        self.animacao_pausada = False
        self.btn_pause.setText("Pausar Animação")
        self.timer.start(50)


# Execução
app = QApplication(sys.argv)
janela = SiMo()
janela.show()
sys.exit(app.exec())
