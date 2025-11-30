# pistao.py (versão adaptativa)
import numpy as np
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QLinearGradient

class PistonWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.phase = 0
        self.rpm = 3000
        self.cycle_type = "otto"  # otto, atkinson, diesel
        
    def set_rpm(self, rpm):
        self.rpm = rpm
        
    def set_cycle_type(self, cycle_type):
        """Define o tipo de ciclo: otto, atkinson, diesel"""
        self.cycle_type = cycle_type
        self.phase = 0  # Reinicia a animação
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("White"))
        
        w = self.width()
        h = self.height()
        
        # Dimensões do motor
        cilindro_h = int(h*0.6)
        cilindro_w = int(cilindro_h * 0.66)
        cilindro_y = (h - cilindro_h) // 2
        cilindro_x = (w-cilindro_w) // 2

        fase_ciclo = (self.phase % (4 * np.pi)) / np.pi
        
        # ===== COMPORTAMENTO ESPECÍFICO POR CICLO =====
        if self.cycle_type == "atkinson":
            # Atkinson: válvula de admissão fecha tarde, expansão maior
            if fase_ciclo < 0.5:  # Admissão até meio curso
                pos_pistao = fase_ciclo * 2
                fase_nome = "ADMISSÃO (parcial)"
                cor_gas = QColor(100, 150, 255, 80)
                valv_adm = True
            elif fase_ciclo < 1.5:  # Admissão continua + compressão
                pos_pistao = 1.0
                fase_nome = "ADM. TARDIA"
                cor_gas = QColor(100, 150, 255, 100)
                valv_adm = True if fase_ciclo < 0.8 else False
            elif fase_ciclo < 2:  # Compressão
                pos_pistao = 2 - fase_ciclo
                fase_nome = "COMPRESSÃO"
                cor_gas = QColor(150, 150, 255, 150)
                valv_adm = False
            elif fase_ciclo < 3.2:  # Expansão LONGA
                pos_pistao = (fase_ciclo - 2) * 1.2  # 20% mais longa!
                fase_nome = "EXPANSÃO+"
                cor_gas = QColor(255, 150, 50, 200)
                valv_adm = False
            else:  # Exaustão
                pos_pistao = 4 - fase_ciclo
                fase_nome = "EXAUSTÃO"
                cor_gas = QColor(120, 120, 120, 150)
                valv_adm = False
                
        elif self.cycle_type == "diesel":
            # Diesel: compressão alta, combustão a pressão constante
            if fase_ciclo < 1:  # Admissão
                pos_pistao = fase_ciclo
                fase_nome = "ADMISSÃO"
                cor_gas = QColor(100, 200, 255, 120)  # Azul claro (só ar!)
                valv_adm = True
            elif fase_ciclo < 2:  # Compressão ALTA
                pos_pistao = 2 - fase_ciclo
                fase_nome = "COMPRESSÃO ALTA"
                cor_gas = QColor(150, 180, 255, 180)
                valv_adm = False
            elif fase_ciclo < 2.4:  # Injeção + combustão progressiva
                pos_pistao = fase_ciclo - 2
                fase_nome = "INJEÇÃO/COMBUSTÃO"
                cor_gas = QColor(255, 120, 30, 220)  # Laranja intenso
                valv_adm = False
            elif fase_ciclo < 3:  # Expansão
                pos_pistao = fase_ciclo - 2
                fase_nome = "EXPANSÃO"
                cor_gas = QColor(255, 150, 50, 180)
                valv_adm = False
            else:  # Exaustão
                pos_pistao = 4 - fase_ciclo
                fase_nome = "EXAUSTÃO"
                cor_gas = QColor(80, 80, 80, 180)  # Mais escuro (fuligem)
                valv_adm = False
                
        else:  # Otto (padrão)
            if fase_ciclo < 1:
                pos_pistao = fase_ciclo
                fase_nome = "ADMISSÃO"
                cor_gas = QColor(100, 150, 255, 100)
                valv_adm = True
            elif fase_ciclo < 2:
                pos_pistao = 2 - fase_ciclo
                fase_nome = "COMPRESSÃO"
                cor_gas = QColor(150, 150, 255, 150)
                valv_adm = False
            elif fase_ciclo < 3:
                pos_pistao = fase_ciclo - 2
                fase_nome = "EXPLOSÃO"
                cor_gas = QColor(255, 150, 50, 200)
                valv_adm = False
            else:
                pos_pistao = 4 - fase_ciclo
                fase_nome = "EXAUSTÃO"
                cor_gas = QColor(120, 120, 120, 150)
                valv_adm = False
        
        # Limita posição
        pos_pistao = max(0, min(1, pos_pistao))
        pistao_y = cilindro_y + 20 + int(pos_pistao * (cilindro_h - 80))
        
        # Desenha cilindro
        painter.setPen(QPen(QColor("#475569"), 4))
        painter.setBrush(QBrush(QColor("#334155")))
        painter.drawRect(cilindro_x, cilindro_y, cilindro_w, cilindro_h)
        
        # Gás
        gas_h = pistao_y - cilindro_y - 20
        if gas_h > 0:
            gradient = QLinearGradient(cilindro_x, cilindro_y + 20, cilindro_x, pistao_y)
            gradient.setColorAt(0, cor_gas.lighter(120))
            gradient.setColorAt(1, cor_gas)
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(cilindro_x + 4, cilindro_y + 20, cilindro_w - 8, gas_h)
        
        # Efeito de explosão
        if self.cycle_type == "otto" and 2 <= fase_ciclo < 2.3:
            intensidade = int(255 * (1 - (fase_ciclo - 2) / 0.3))
            painter.setBrush(QBrush(QColor(255, 200, 0, intensidade)))
            painter.drawEllipse(cilindro_x + 20, cilindro_y + 10, cilindro_w - 40, 40)
        elif self.cycle_type == "diesel" and 2 <= fase_ciclo < 2.5:
            # Combustão progressiva no Diesel
            intensidade = int(200 * (1 - abs(fase_ciclo - 2.25) / 0.25))
            painter.setBrush(QBrush(QColor(255, 150, 0, intensidade)))
            painter.drawEllipse(cilindro_x + 15, cilindro_y + 10, cilindro_w - 30, 50)
        
        # Cabeçote
        painter.setBrush(QBrush(QColor("#64748b")))
        painter.setPen(QPen(QColor("#334155"), 2))
        painter.drawRect(cilindro_x - 10, cilindro_y - 15, cilindro_w + 20, 15)
        
        # Vela (Otto/Atkinson) ou Injetor (Diesel)
        if self.cycle_type == "diesel":
            painter.setBrush(QBrush(QColor("#ef4444")))  # Vermelho = injetor
            painter.drawRect(cilindro_x + cilindro_w // 2 - 4, cilindro_y - 30, 8, 15)
            painter.drawEllipse(cilindro_x + cilindro_w // 2 - 6, cilindro_y - 35, 12, 10)
        else:
            painter.setBrush(QBrush(QColor("#94a3b8")))
            painter.drawRect(cilindro_x + cilindro_w // 2 - 5, cilindro_y - 30, 10, 15)
            painter.drawEllipse(cilindro_x + cilindro_w // 2 - 8, cilindro_y - 35, 16, 10)
        
        # Faísca (Otto/Atkinson) ou spray (Diesel)
        if self.cycle_type != "diesel" and 1.9 <= fase_ciclo < 2.1:
            painter.setPen(QPen(QColor(255, 255, 100), 2))
            spark_x = cilindro_x + cilindro_w // 2
            spark_y = cilindro_y - 15
            for i in range(3):
                offset = (i - 1) * 8
                painter.drawLine(spark_x + offset, spark_y, spark_x + offset, spark_y + 15)
        elif self.cycle_type == "diesel" and 2 <= fase_ciclo < 2.4:
            # Spray de combustível
            painter.setPen(QPen(QColor(255, 200, 100), 1))
            spray_x = cilindro_x + cilindro_w // 2
            spray_y = cilindro_y - 15
            for i in range(5):
                offset = (i - 2) * 6
                painter.drawLine(spray_x + offset, spray_y, spray_x + offset * 2, spray_y + 20)
        
        # Pistão
        pistao_h = 30
        gradient_pistao = QLinearGradient(cilindro_x, pistao_y, cilindro_x, pistao_y + pistao_h)
        gradient_pistao.setColorAt(0, QColor("#94a3b8"))
        gradient_pistao.setColorAt(1, QColor("#64748b"))
        painter.setBrush(QBrush(gradient_pistao))
        painter.setPen(QPen(QColor("#334155"), 2))
        painter.drawRect(cilindro_x + 5, pistao_y, cilindro_w - 10, pistao_h)
        
        # Anéis
        painter.setPen(QPen(QColor("#1e293b"), 2))
        for offset in [8, 16, 24]:
            painter.drawLine(cilindro_x + 5, pistao_y + offset, 
                           cilindro_x + cilindro_w - 5, pistao_y + offset)
        
        # Biela e virabrequim
        biela_top_y = pistao_y + pistao_h
        biela_bottom_y = cilindro_y + cilindro_h + 30
        biela_x = cilindro_x + cilindro_w // 2
        
        painter.setPen(QPen(QColor("#475569"), 6))
        painter.drawLine(biela_x, biela_top_y, biela_x, biela_bottom_y)
        
        painter.setBrush(QBrush(QColor("#94a3b8")))
        painter.drawEllipse(biela_x - 8, biela_top_y - 5, 16, 10)
        
        vira_y = biela_bottom_y + 10
        vira_offset_x = int(20 * np.cos(self.phase))
        
        painter.setBrush(QBrush(QColor("#64748b")))
        painter.drawEllipse(biela_x - 25, vira_y - 15, 50, 30)
        painter.setBrush(QBrush(QColor("#94a3b8")))
        painter.drawEllipse(biela_x + vira_offset_x - 8, vira_y - 8, 16, 16)
        
        # Válvulas
        valvula_exh = (fase_ciclo >= 3)
        
        valvula_adm_y = cilindro_y if valv_adm else cilindro_y - 10
        painter.setBrush(QBrush(QColor("#22c55e") if valv_adm else QColor("#475569")))
        painter.drawRect(cilindro_x + 15, valvula_adm_y - 15, 15, 15)
        painter.setPen(QPen(QColor("#334155"), 2))
        painter.drawLine(cilindro_x + 22, valvula_adm_y - 15, cilindro_x + 22, valvula_adm_y - 25)
        
        valvula_exh_y = cilindro_y if valvula_exh else cilindro_y - 10
        painter.setBrush(QBrush(QColor("#ef4444") if valvula_exh else QColor("#475569")))
        painter.drawRect(cilindro_x + cilindro_w - 30, valvula_exh_y - 15, 15, 15)
        painter.setPen(QPen(QColor("#334155"), 2))
        painter.drawLine(cilindro_x + cilindro_w - 22, valvula_exh_y - 15, 
                        cilindro_x + cilindro_w - 22, valvula_exh_y - 25)
        
        # Texto
        painter.setPen(QPen(QColor("Black")))
        font = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(10, h - 40, fase_nome)
        
        font_small = QFont("Arial", 10)
        painter.setFont(font_small)
        painter.drawText(10, h - 20, f"{self.cycle_type.upper()} | RPM: {self.rpm}")
        
        # Incremento
        incremento = (self.rpm / 3000) * 0.15
        self.phase += incremento
