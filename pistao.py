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
# WIDGET PISTÃO
# =======================
class PistonWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.phase = 0  # Fase do ciclo (0 a 4π)
        self.rpm = 3000
        
    def set_rpm(self, rpm):
        """Define o RPM para ajustar a velocidade da animação"""
        self.rpm = rpm
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("White"))  # Fundo escuro
        
        w = self.width()
        h = self.height()
        
        # Dimensões do motor
        cilindro_x = w // 2 - 60
        cilindro_y = 20
        cilindro_w = 120
        cilindro_h = 180
        
        # Posição do pistão baseada na fase (ciclo de 4 tempos = 4π radianos)
        # 0 a π: Admissão (pistão desce)
        # π a 2π: Compressão (pistão sobe)
        # 2π a 3π: Explosão (pistão desce)
        # 3π a 4π: Exaustão (pistão sobe)
        
        fase_ciclo = (self.phase % (4 * np.pi)) / np.pi  # 0 a 4
        
        # Calcula posição do pistão (0 = topo, 1 = fundo)
        if fase_ciclo < 1:  # Admissão
            pos_pistao = fase_ciclo
            fase_nome = "ADMISSÃO"
            cor_gas = QColor(100, 150, 255, 100)  # Azul (ar+combustível)
        elif fase_ciclo < 2:  # Compressão
            pos_pistao = 2 - fase_ciclo
            fase_nome = "COMPRESSÃO"
            cor_gas = QColor(150, 150, 255, 150)  # Azul mais escuro
        elif fase_ciclo < 3:  # Explosão
            pos_pistao = fase_ciclo - 2
            fase_nome = "EXPLOSÃO"
            cor_gas = QColor(255, 150, 50, 200)  # Laranja (fogo)
        else:  # Exaustão
            pos_pistao = 4 - fase_ciclo
            fase_nome = "EXAUSTÃO"
            cor_gas = QColor(120, 120, 120, 150)  # Cinza (gases queimados)
        
        pistao_y = cilindro_y + 20 + int(pos_pistao * (cilindro_h - 80))
        
        # Desenha paredes do cilindro
        painter.setPen(QPen(QColor("#475569"), 4))
        painter.setBrush(QBrush(QColor("#334155")))
        painter.drawRect(cilindro_x, cilindro_y, cilindro_w, cilindro_h)
        
        # Desenha o gás/mistura dentro do cilindro
        gas_h = pistao_y - cilindro_y - 20
        if gas_h > 0:
            # Gradiente para o gás
            gradient = QLinearGradient(cilindro_x, cilindro_y + 20, cilindro_x, pistao_y)
            gradient.setColorAt(0, cor_gas.lighter(120))
            gradient.setColorAt(1, cor_gas)
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(cilindro_x + 4, cilindro_y + 20, cilindro_w - 8, gas_h)
        
        # Efeito de explosão
        if 2 <= fase_ciclo < 2.3:
            intensidade = int(255 * (1 - (fase_ciclo - 2) / 0.3))
            painter.setBrush(QBrush(QColor(255, 200, 0, intensidade)))
            painter.drawEllipse(cilindro_x + 20, cilindro_y + 10, cilindro_w - 40, 40)
        
        # Desenha cabeçote (topo do cilindro)
        painter.setBrush(QBrush(QColor("#64748b")))
        painter.setPen(QPen(QColor("#334155"), 2))
        painter.drawRect(cilindro_x - 10, cilindro_y - 15, cilindro_w + 20, 15)
        
        # Vela de ignição
        painter.setBrush(QBrush(QColor("#94a3b8")))
        painter.drawRect(cilindro_x + cilindro_w // 2 - 5, cilindro_y - 30, 10, 15)
        painter.drawEllipse(cilindro_x + cilindro_w // 2 - 8, cilindro_y - 35, 16, 10)
        
        # Faísca durante explosão
        if 1.9 <= fase_ciclo < 2.1:
            painter.setPen(QPen(QColor(255, 255, 100), 2))
            spark_x = cilindro_x + cilindro_w // 2
            spark_y = cilindro_y - 15
            for i in range(3):
                offset = (i - 1) * 8
                painter.drawLine(spark_x + offset, spark_y, spark_x + offset, spark_y + 15)
        
        # Desenha o pistão
        pistao_h = 30
        gradient_pistao = QLinearGradient(cilindro_x, pistao_y, cilindro_x, pistao_y + pistao_h)
        gradient_pistao.setColorAt(0, QColor("#94a3b8"))
        gradient_pistao.setColorAt(1, QColor("#64748b"))
        painter.setBrush(QBrush(gradient_pistao))
        painter.setPen(QPen(QColor("#334155"), 2))
        painter.drawRect(cilindro_x + 5, pistao_y, cilindro_w - 10, pistao_h)
        
        # Anéis do pistão
        painter.setPen(QPen(QColor("#1e293b"), 2))
        painter.drawLine(cilindro_x + 5, pistao_y + 8, cilindro_x + cilindro_w - 5, pistao_y + 8)
        painter.drawLine(cilindro_x + 5, pistao_y + 16, cilindro_x + cilindro_w - 5, pistao_y + 16)
        painter.drawLine(cilindro_x + 5, pistao_y + 24, cilindro_x + cilindro_w - 5, pistao_y + 24)
        
        # Biela
        biela_top_y = pistao_y + pistao_h
        biela_bottom_y = cilindro_y + cilindro_h + 30
        biela_x = cilindro_x + cilindro_w // 2
        
        painter.setPen(QPen(QColor("#475569"), 6))
        painter.drawLine(biela_x, biela_top_y, biela_x, biela_bottom_y)
        
        # Pino do pistão
        painter.setBrush(QBrush(QColor("#94a3b8")))
        painter.drawEllipse(biela_x - 8, biela_top_y - 5, 16, 10)
        
        # Virabrequim (simplificado)
        vira_y = biela_bottom_y + 10
        vira_raio = 20
        angulo_vira = self.phase
        vira_offset_x = int(vira_raio * np.cos(angulo_vira))
        
        painter.setBrush(QBrush(QColor("#64748b")))
        painter.drawEllipse(biela_x - 25, vira_y - 15, 50, 30)
        painter.setBrush(QBrush(QColor("#94a3b8")))
        painter.drawEllipse(biela_x + vira_offset_x - 8, vira_y - 8, 16, 16)
        
        # Válvula de admissão (esquerda)
        valvula_adm_aberta = (fase_ciclo < 1)
        valvula_adm_y = cilindro_y if valvula_adm_aberta else cilindro_y - 10
        painter.setBrush(QBrush(QColor("#22c55e") if valvula_adm_aberta else QColor("#475569")))
        painter.drawRect(cilindro_x + 15, valvula_adm_y - 15, 15, 15)
        painter.setPen(QPen(QColor("#334155"), 2))
        painter.drawLine(cilindro_x + 22, valvula_adm_y - 15, cilindro_x + 22, valvula_adm_y - 25)
        
        # Válvula de exaustão (direita)
        valvula_exh_aberta = (fase_ciclo >= 3)
        valvula_exh_y = cilindro_y if valvula_exh_aberta else cilindro_y - 10
        painter.setBrush(QBrush(QColor("#ef4444") if valvula_exh_aberta else QColor("#475569")))
        painter.drawRect(cilindro_x + cilindro_w - 30, valvula_exh_y - 15, 15, 15)
        painter.setPen(QPen(QColor("#334155"), 2))
        painter.drawLine(cilindro_x + cilindro_w - 22, valvula_exh_y - 15, 
                        cilindro_x + cilindro_w - 22, valvula_exh_y - 25)
        
        # Fluxo de gases na admissão
        if fase_ciclo < 1 and int(self.phase * 10) % 3 == 0:
            painter.setBrush(QBrush(QColor(100, 150, 255, 150)))
            for i in range(3):
                y_offset = i * 15
                if cilindro_y - 30 - y_offset > 0:
                    painter.drawEllipse(cilindro_x + 15, cilindro_y - 35 - y_offset, 15, 10)
        
        # Fluxo de gases na exaustão
        if fase_ciclo >= 3 and int(self.phase * 10) % 3 == 0:
            painter.setBrush(QBrush(QColor(120, 120, 120, 150)))
            for i in range(3):
                y_offset = i * 15
                if cilindro_y - 30 - y_offset > 0:
                    painter.drawEllipse(cilindro_x + cilindro_w - 30, cilindro_y - 35 - y_offset, 15, 10)
        
        # Texto da fase atual
        painter.setPen(QPen(QColor("Black")))
        font = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(10, h - 40, fase_nome)
        
        # RPM
        font_small = QFont("Arial", 10)
        painter.setFont(font_small)
        painter.drawText(10, h - 20, f"RPM: {self.rpm}")
        
        # Legenda das válvulas
        painter.drawText(w - 100, 30, "🟢 Admissão")
        painter.drawText(w - 100, 50, "🔴 Exaustão")
        
        # Incrementa a fase baseado no RPM
        # A cada frame, avançar proporcionalmente ao RPM
        incremento = (self.rpm / 3000) * 0.15  # Normalizado para 3000 RPM
        self.phase += incremento

