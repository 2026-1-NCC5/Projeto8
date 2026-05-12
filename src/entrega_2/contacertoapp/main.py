"""
ContaCerto — Interface de Contagem de Alimentos
Projeto: Lideranças Empáticas
Requer: pip install PySide6 ultralytics opencv-python pyodbc
"""

import os
import sys
import cv2
import time
import random
import string
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QScrollArea, QSizePolicy,
    QStackedWidget, QGraphicsDropShadowEffect, QSpacerItem, QComboBox
)
from PySide6.QtCore import (
    Qt, QTimer, QThread, Signal, QPropertyAnimation,
    QEasingCurve, QRect, QSize
)
from PySide6.QtGui import (
    QImage, QPixmap, QFont, QColor, QPainter, QPen,
    QLinearGradient, QBrush, QIcon, QPalette
)

COLORS = {
    "bg_dark": "#0F1117",
    "bg_panel":     "#161B22",
    "bg_card":      "#1C2333",
    "bg_hover":     "#222B3A",
    "border":       "#2D3748",
    "border_light": "#374151",
    "green":        "#22C55E",
    "green_dark":   "#16A34A",
    "green_bg":     "#052E16",
    "red":          "#EF4444",
    "blue":         "#3B82F6",
    "blue_light":   "#60A5FA",
    "yellow":       "#F59E0B",
    "text_primary": "#F1F5F9",
    "text_sec":     "#94A3B8",
    "text_muted":   "#475569",
    "white":        "#FFFFFF",
    "live_dot":     "#22C55E",
}

ALIMENTOS_INFO = {
    "arroz":    {"cor": "#3B82F6", "emoji": "🌾", "peso": "1kg/un",   "peso_kg": 1.000},
    "feijao":   {"cor": "#8B5CF6", "emoji": "🫘", "peso": "1kg/un",   "peso_kg": 1.000},
    "acucar":   {"cor": "#F59E0B", "emoji": "🍬", "peso": "1kg/un",   "peso_kg": 1.000},
    "macarrao": {"cor": "#EC4899", "emoji": "🍝", "peso": "500g/un",  "peso_kg": 0.500},
    "fuba":     {"cor": "#F97316", "emoji": "🌽", "peso": "1kg/un",   "peso_kg": 1.000},
    "oleo":     {"cor": "#06B6D4", "emoji": "🫙", "peso": "900ml/un", "peso_kg": 0.900},
    "leite_po": {"cor": "#10B981", "emoji": "🥛", "peso": "400g/un",  "peso_kg": 0.400},
}

model_path = os.getenv("MODEL_PATH", default="./models/*.pt")

# ── Thread de captura de câmera ────────────────────────────────────────────────

class CameraThread(QThread):
    frame_ready    = Signal(QImage)
    # Emite {classe: qtd} dos itens NO FRAME atual (para UI de "vendo agora")
    detection_ready = Signal(dict)
    # Emite (classe, peso_kg) quando um item CRUZA a linha pela primeira vez
    item_contado   = Signal(str, float)

    # Proporção X da linha de contagem (0.5 = centro da imagem)
    LINHA_X_PROP = 0.5
    LIMIAR       = 0.5

    def __init__(self, model_path=None, camera_idx=2):
        super().__init__()
        self.model_path    = model_path
        self.camera_idx    = camera_idx
        self.running       = False
        self.paused        = False
        self.model         = None
        # IDs já contabilizados — nunca serão contados de novo
        self.ids_contados  = set()
        # Posição X anterior de cada track_id
        self.pos_anterior  = {}

    def run(self):
        self.running = True

        if self.model_path:
            try:
                from ultralytics import YOLO
                self.model = YOLO(self.model_path)
            except Exception as e:
                print(f"Aviso: modelo não carregado — {e}")

        # Tenta DirectShow (mais estável no Windows)
        cap = cv2.VideoCapture(self.camera_idx, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(self.camera_idx)
        if not cap.isOpened():
            print("ERRO: câmera não encontrada.")
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Cores BGR por classe
        cores_bgr = {
            "arroz":    (228, 148,  68),
            "feijao":   (150,  92, 139),
            "acucar":   ( 11, 158, 245),
            "macarrao": (201,  72, 236),
            "fuba":     ( 22, 163, 249),
            "oleo":     (212, 182,   6),
            "leite_po": (129, 185,  16),
        }

        # Pesos por classe (kg)
        pesos = {info["peso_kg"]: k for k, info in ALIMENTOS_INFO.items()}
        pesos_map = {k: v["peso_kg"] for k, v in ALIMENTOS_INFO.items()}

        while self.running:
            if self.paused:
                self.msleep(50)
                continue

            ret, frame = cap.read()
            if not ret:
                break

            h_frame, w_frame = frame.shape[:2]
            linha_x = int(w_frame * self.LINHA_X_PROP)

            # Desenha a linha de contagem (vermelha tracejada)
            for y in range(0, h_frame, 20):
                cv2.line(frame, (linha_x, y), (linha_x, min(y+10, h_frame)),
                         (0, 80, 220), 2)
            cv2.putText(frame, "CONTAGEM", (linha_x + 6, 18),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 80, 220), 1)

            contagem_frame = {}

            if self.model:
                try:
                    results = self.model.track(
                        frame, persist=True,
                        verbose=False, conf=self.LIMIAR,
                        tracker="bytetrack.yaml"
                    )

                    if results[0].boxes.id is not None:
                        boxes   = results[0].boxes.xyxy.cpu().numpy()
                        ids     = results[0].boxes.id.cpu().numpy().astype(int)
                        classes = results[0].boxes.cls.cpu().numpy().astype(int)
                        confs   = results[0].boxes.conf.cpu().numpy()

                        for box, tid, cid, conf in zip(boxes, ids, classes, confs):
                            x1, y1, x2, y2 = box.astype(int)
                            cx = (x1 + x2) // 2   # centroide X
                            cy = (y1 + y2) // 2

                            classe = self.model.names[cid]
                            cor    = cores_bgr.get(classe, (200, 200, 200))

                            # ── Lógica de cruzamento da linha ──────────────
                            # Conta SE: estava à esquerda E agora está à direita
                            # E ainda não foi contado nesta sessão
                            pos_ant = self.pos_anterior.get(tid)
                            if (pos_ant is not None
                                    and pos_ant < linha_x
                                    and cx >= linha_x
                                    and tid not in self.ids_contados):
                                self.ids_contados.add(tid)
                                peso = pesos_map.get(classe, 1.0)
                                self.item_contado.emit(classe, peso)
                                # Flash verde na linha ao contar
                                cv2.line(frame, (linha_x, 0), (linha_x, h_frame),
                                         (0, 220, 80), 3)

                            self.pos_anterior[tid] = cx

                            # Desenha bounding box
                            ja_contado = tid in self.ids_contados
                            cor_box = (0, 200, 80) if ja_contado else cor
                            cv2.rectangle(frame, (x1, y1), (x2, y2), cor_box, 2)

                            # Label com classe, confiança e status
                            status = "✓" if ja_contado else f"#{tid}"
                            label  = f"{classe} {int(conf*100)}% {status}"
                            cv2.putText(frame, label, (x1, y1 - 8),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.48, cor_box, 2)

                            # Ponto no centroide
                            cv2.circle(frame, (cx, cy), 4, cor_box, -1)

                            contagem_frame[classe] = contagem_frame.get(classe, 0) + 1

                    self.detection_ready.emit(contagem_frame)

                except Exception as e:
                    print(f"Erro de detecção: {e}")

            # Converte para QImage e emite
            rgb  = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
            self.frame_ready.emit(qimg.copy())

            self.msleep(30)

        cap.release()

    def reset_contagem(self):
        """Limpa o histórico de IDs contados (nova sessão)."""
        self.ids_contados.clear()
        self.pos_anterior.clear()

    def stop(self):
        self.running = False
        self.wait()

# ── Widgets customizados ───────────────────────────────────────────────────────

class SidebarButton(QPushButton):
    def __init__(self, icon_text, label, parent=None):
        super().__init__(parent)
        self.icon_text  = icon_text
        self.label_text = label
        self.active     = False
        self.setFixedHeight(44)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(self._style(False))

    def _style(self, active):
        bg     = "#1E293B" if active else "transparent"
        border = f"border-left: 3px solid {COLORS['green']};" if active else "border-left: 3px solid transparent;"
        text   = COLORS["text_primary"] if active else COLORS["text_sec"]
        return f"""
            QPushButton {{
                background: {bg};
                {border}
                color: {text};
                text-align: left;
                padding: 0 16px;
                border-radius: 0;
                font-size: 13px;
                font-weight: {'600' if active else '400'};
            }}
            QPushButton:hover {{
                background: #1E293B;
                color: {COLORS["text_primary"]};
            }}
        """

    def set_active(self, active):
        self.active = active
        self.setStyleSheet(self._style(active))

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # Ícone
        painter.setFont(QFont("Segoe UI Emoji", 14))
        painter.drawText(QRect(14, 0, 30, self.height()), Qt.AlignVCenter, self.icon_text)
        # Label
        painter.setFont(QFont("Segoe UI", 12))
        painter.setPen(QColor(COLORS["text_primary"] if self.active else COLORS["text_sec"]))
        painter.drawText(QRect(48, 0, self.width()-48, self.height()), Qt.AlignVCenter, self.label_text)


class LiveBadge(QLabel):
    def __init__(self, parent=None):
        super().__init__(" ● AO VIVO", parent)
        self.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['green']};
                background: {COLORS['green_bg']};
                border: 1px solid {COLORS['green_dark']};
                border-radius: 10px;
                padding: 2px 10px;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 1px;
            }}
        """)
        # Pisca o ponto
        self._timer = QTimer()
        self._timer.timeout.connect(self._blink)
        self._timer.start(800)
        self._state = True

    def _blink(self):
        self._state = not self._state
        dot = "●" if self._state else "○"
        self.setText(f" {dot} AO VIVO")


class ItemCard(QFrame):
    def __init__(self, alimento, info, parent=None):
        super().__init__(parent)
        self.alimento = alimento
        self.contagem = 0
        self.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
            }}
            QFrame:hover {{
                border-color: {info['cor']};
                background: {COLORS['bg_hover']};
            }}
        """)
        self.setFixedHeight(62)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(12)

        # Dot colorido
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {info['cor']}; font-size: 10px; background: transparent; border: none;")
        dot.setFixedWidth(14)
        layout.addWidget(dot)

        # Nome
        nome_label = QLabel(alimento.replace("_", " ").title())
        nome_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 13px; font-weight: 500; background: transparent; border: none;")
        layout.addWidget(nome_label)

        layout.addStretch()

        # Peso
        self.peso_label = QLabel(info['peso'])
        self.peso_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px; background: transparent; border: none;")
        layout.addWidget(self.peso_label)

        # Botão menos
        btn_menos = QPushButton("−")
        btn_menos.setFixedSize(26, 26)
        btn_menos.setCursor(Qt.PointingHandCursor)
        btn_menos.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['bg_panel']};
                color: {COLORS['text_sec']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                font-size: 16px;
                font-weight: 300;
            }}
            QPushButton:hover {{ background: {COLORS['red']}; color: white; border-color: {COLORS['red']}; }}
        """)
        btn_menos.clicked.connect(self._decrement)
        layout.addWidget(btn_menos)

        # Contagem
        self.count_label = QLabel("0")
        self.count_label.setFixedWidth(28)
        self.count_label.setAlignment(Qt.AlignCenter)
        self.count_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px; font-weight: 700; background: transparent; border: none;")
        layout.addWidget(self.count_label)

        # Botão mais
        btn_mais = QPushButton("+")
        btn_mais.setFixedSize(26, 26)
        btn_mais.setCursor(Qt.PointingHandCursor)
        btn_mais.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['bg_panel']};
                color: {COLORS['text_sec']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                font-size: 16px;
                font-weight: 300;
            }}
            QPushButton:hover {{ background: {COLORS['green']}; color: white; border-color: {COLORS['green']}; }}
        """)
        btn_mais.clicked.connect(self._increment)
        layout.addWidget(btn_mais)

    def _increment(self):
        self.contagem += 1
        self.count_label.setText(str(self.contagem))

    def _decrement(self):
        if self.contagem > 0:
            self.contagem -= 1
            self.count_label.setText(str(self.contagem))

    def set_count(self, n):
        self.contagem = n
        self.count_label.setText(str(n))


class ActivityItem(QFrame):
    def __init__(self, icon, title, subtitle, time_str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: transparent; border: none;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(10)

        # Ícone
        icon_label = QLabel(icon)
        icon_label.setFixedSize(26, 26)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"""
            background: {COLORS['green_bg']};
            color: {COLORS['green']};
            border-radius: 13px;
            font-size: 12px;
            border: none;
        """)
        layout.addWidget(icon_label)

        # Texto
        text_col = QVBoxLayout()
        text_col.setSpacing(1)
        t = QLabel(title)
        t.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 12px; font-weight: 500; background: transparent; border: none;")
        s = QLabel(subtitle)
        s.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px; background: transparent; border: none;")
        text_col.addWidget(t)
        text_col.addWidget(s)
        layout.addLayout(text_col)

        layout.addStretch()

        # Hora
        time_label = QLabel(time_str)
        time_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px; background: transparent; border: none;")
        layout.addWidget(time_label)


class MetricCard(QFrame):
    def __init__(self, title, value, unit, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
            }}
        """)
        self.setMinimumHeight(80)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px; font-weight: 600; letter-spacing: 0.5px; background: transparent; border: none;")

        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 20px; font-weight: 700; background: transparent; border: none;")

        self.unit_label = QLabel(unit)
        self.unit_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px; background: transparent; border: none;")

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.unit_label)

    def update_value(self, value):
        self.value_label.setText(str(value))


# ── Janela principal ────────────────────────────────────────────────────────────

class ContaCerto(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ContaCerto — Lideranças Empáticas")
        self.setMinimumSize(1280, 800)
        self.resize(1440, 900)

        # Estado da sessão
        self.session_id   = self._gen_session_id()
        self.session_time = 0
        self.total_items  = 0
        self.is_counting  = False
        self.is_paused    = False
        self.item_cards   = {}

        # Timer geral
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self._tick)
        self.clock_timer.start(1000)

        # Câmera thread
        self.cam_thread = None

        self._build_ui()
        self._apply_global_style()

    def _gen_session_id(self):
        return "#" + "".join(random.choices(string.ascii_uppercase + string.digits, k=7))

    def _apply_global_style(self):
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background: {COLORS['bg_dark']};
                color: {COLORS['text_primary']};
                font-family: 'Segoe UI', sans-serif;
            }}
            QScrollBar:vertical {{
                background: {COLORS['bg_panel']};
                width: 6px;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['border_light']};
                border-radius: 3px;
                min-height: 30px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sidebar ────────────────────────────────────────────────────────────
        sidebar = self._build_sidebar()
        root.addWidget(sidebar)

        # ── Conteúdo principal ─────────────────────────────────────────────────
        main_col = QVBoxLayout()
        main_col.setContentsMargins(0, 0, 0, 0)
        main_col.setSpacing(0)

        # Header
        header = self._build_header()
        main_col.addWidget(header)

        # Separador
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {COLORS['border']};")
        main_col.addWidget(sep)

        # Corpo
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        # Camera area
        cam_area = self._build_camera_area()
        body.addWidget(cam_area, 3)

        # Separador vertical
        vsep = QFrame()
        vsep.setFixedWidth(1)
        vsep.setStyleSheet(f"background: {COLORS['border']};")
        body.addWidget(vsep)

        # Painel direito
        right_panel = self._build_right_panel()
        body.addWidget(right_panel, 1)

        main_col.addLayout(body, 1)

        # Bottom bar
        bottom = self._build_bottom_bar()
        main_col.addWidget(bottom)

        main_widget = QWidget()
        main_widget.setLayout(main_col)
        root.addWidget(main_widget, 1)

    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_panel']};
                border-right: 1px solid {COLORS['border']};
            }}
        """)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Logo
        logo_area = QFrame()
        logo_area.setFixedHeight(64)
        logo_area.setStyleSheet(f"background: {COLORS['bg_panel']}; border-bottom: 1px solid {COLORS['border']};")
        logo_layout = QHBoxLayout(logo_area)
        logo_layout.setContentsMargins(16, 0, 16, 0)

        logo_icon = QLabel("CC")
        logo_icon.setFixedSize(34, 34)
        logo_icon.setAlignment(Qt.AlignCenter)
        logo_icon.setStyleSheet(f"""
            background: {COLORS['green']};
            color: white;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 800;
        """)

        logo_text = QVBoxLayout()
        logo_text.setSpacing(0)
        t1 = QLabel("Conta Certo")
        t1.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 13px; font-weight: 700; background: transparent;")
        t2 = QLabel("Counter v0.1.0")
        t2.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 10px; background: transparent;")
        logo_text.addWidget(t1)
        logo_text.addWidget(t2)

        logo_layout.addWidget(logo_icon)
        logo_layout.addSpacing(10)
        logo_layout.addLayout(logo_text)
        layout.addWidget(logo_area)

        # # Seção OPERAÇÃO
        # self._section_label(layout, "OPERAÇÃO")
        # self.btn_contagem  = self._nav_btn(layout, "📷", "Contagem", True)
        # self._nav_btn(layout, "🕐", "Histórico", False)

        # # Seção GESTÃO
        # self._section_label(layout, "GESTÃO")
        # self._nav_btn(layout, "📢", "Campanhas", False)
        # self._nav_btn(layout, "👥", "Equipes", False)
        # self._nav_btn(layout, "📊", "Relatórios", False)

        # layout.addStretch()

        # # Seção SUPORTE
        # self._section_label(layout, "SUPORTE")
        # self._nav_btn(layout, "❓", "Ajuda", False)
        # self._nav_btn(layout, "⚙️", "Configurações", False)

        # Usuário
        user_area = QFrame()
        user_area.setFixedHeight(56)
        user_area.setStyleSheet(f"background: transparent; border-top: 1px solid {COLORS['border']};")
        ul = QHBoxLayout(user_area)
        ul.setContentsMargins(16, 0, 16, 0)

        av = QLabel("JO")
        av.setFixedSize(30, 30)
        av.setAlignment(Qt.AlignCenter)
        av.setStyleSheet(f"background: {COLORS['blue']}; color: white; border-radius: 15px; font-size: 11px; font-weight: 700;")

        utxt = QVBoxLayout()
        utxt.setSpacing(0)
        u1 = QLabel("Operador")
        u1.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 12px; font-weight: 500; background: transparent;")
        u2 = QLabel("Estação A")
        u2.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 10px; background: transparent;")
        utxt.addWidget(u1)
        utxt.addWidget(u2)

        ul.addWidget(av)
        ul.addSpacing(8)
        ul.addLayout(utxt)
        layout.addWidget(user_area)

        return sidebar

    def _section_label(self, layout, text):
        lbl = QLabel(text)
        lbl.setContentsMargins(16, 12, 16, 4)
        lbl.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 10px; font-weight: 700; letter-spacing: 1px; background: transparent;")
        layout.addWidget(lbl)

    def _nav_btn(self, layout, icon, label, active):
        btn = QPushButton()
        btn.setFixedHeight(40)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setText(f"  {icon}  {label}")
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {'#1E293B' if active else 'transparent'};
                color: {COLORS['text_primary'] if active else COLORS['text_sec']};
                text-align: left;
                padding-left: 16px;
                border: none;
                border-left: 3px solid {COLORS['green'] if active else 'transparent'};
                font-size: 13px;
                font-weight: {'600' if active else '400'};
            }}
            QPushButton:hover {{
                background: #1E293B;
                color: {COLORS['text_primary']};
            }}
        """)
        layout.addWidget(btn)
        return btn

    def _build_header(self):
        header = QFrame()
        header.setFixedHeight(64)
        header.setStyleSheet(f"background: {COLORS['bg_panel']};")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(16)

        # Título + ID
        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title = QLabel("Contagem ao vivo")
        title.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 16px; font-weight: 700; background: transparent;")
        self.session_label = QLabel(self.session_id)
        self.session_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px; background: transparent;")
        title_col.addWidget(title)
        title_col.addWidget(self.session_label)
        layout.addLayout(title_col)

        layout.addStretch()

        # Steps
        steps_widget = self._build_steps()
        layout.addWidget(steps_widget)

        layout.addStretch()

        # Timer
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 15px;
            font-weight: 700;
            font-family: 'Courier New', monospace;
            background: transparent;
        """)
        layout.addWidget(self.timer_label)

        layout.addSpacing(8)

        # Botão retomar/pausar
        self.btn_pause = QPushButton("⏸  Pausar")
        self.btn_pause.setFixedHeight(36)
        self.btn_pause.setCursor(Qt.PointingHandCursor)
        self.btn_pause.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_sec']};
                border: 1px solid {COLORS['border_light']};
                border-radius: 8px;
                padding: 0 16px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {COLORS['bg_hover']};
                color: {COLORS['text_primary']};
            }}
        """)
        self.btn_pause.clicked.connect(self._toggle_pause)
        layout.addWidget(self.btn_pause)

        # Botão encerrar
        btn_end = QPushButton("✓  Encerrar e revisar    Ctrl+E")
        btn_end.setFixedHeight(36)
        btn_end.setCursor(Qt.PointingHandCursor)
        btn_end.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['green']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0 16px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {COLORS['green_dark']};
            }}
        """)
        btn_end.clicked.connect(self._end_session)
        layout.addWidget(btn_end)

        return header

    def _build_steps(self):
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        steps = [
            ("1", "Configurar", True, True),
            ("2", "Contar",     True, False),
            ("3", "Revisar",    False, False),
            ("4", "Enviar",     False, False),
        ]

        for i, (num, label, done, active) in enumerate(steps):
            # Círculo
            circle = QLabel("✓" if done and not active else num)
            circle.setFixedSize(28, 28)
            circle.setAlignment(Qt.AlignCenter)
            if done and not active:
                bg = COLORS['green']
                fg = "white"
            elif active:
                bg = COLORS['blue']
                fg = "white"
            else:
                bg = COLORS['bg_card']
                fg = COLORS['text_muted']

            circle.setStyleSheet(f"""
                background: {bg};
                color: {fg};
                border-radius: 14px;
                font-size: 11px;
                font-weight: 700;
            """)

            col = QVBoxLayout()
            col.setSpacing(4)
            col.setAlignment(Qt.AlignHCenter)
            col.addWidget(circle, 0, Qt.AlignHCenter)

            lbl = QLabel(label)
            lbl.setAlignment(Qt.AlignCenter)
            color = COLORS['green'] if (done and not active) else (COLORS['blue_light'] if active else COLORS['text_muted'])
            lbl.setStyleSheet(f"color: {color}; font-size: 10px; font-weight: {'600' if active else '400'}; background: transparent;")
            col.addWidget(lbl)

            step_w = QWidget()
            step_w.setStyleSheet("background: transparent;")
            step_w.setLayout(col)
            layout.addWidget(step_w)

            # Linha entre steps
            if i < len(steps) - 1:
                line = QFrame()
                line.setFixedSize(40, 2)
                line.setStyleSheet(f"background: {COLORS['green'] if done else COLORS['border']}; border: none;")
                layout.addWidget(line, 0, Qt.AlignVCenter)

        return w

    def _detect_cameras(self):
        friendly_names = []
        try:
            import subprocess
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 "Get-PnpDevice -Class Camera -Status OK | Select-Object -ExpandProperty FriendlyName"],
                capture_output=True, text=True, timeout=4
            )
            if result.returncode == 0:
                friendly_names = [l.strip() for l in result.stdout.splitlines() if l.strip()]
        except Exception:
            pass

        available = []
        name_idx = 0
        for i in range(6):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                name = friendly_names[name_idx] if name_idx < len(friendly_names) else f"Câmera {i}"
                available.append((i, name))
                name_idx += 1
                cap.release()

        return available if available else [(i, f"Câmera {i}") for i in range(3)]

    def _build_camera_area(self):
        area = QFrame()
        area.setStyleSheet(f"background: {COLORS['bg_dark']};")

        layout = QVBoxLayout(area)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Câmera
        cam_container = QFrame()
        cam_container.setStyleSheet("background: #000000;")

        cam_layout = QVBoxLayout(cam_container)
        cam_layout.setContentsMargins(0, 0, 0, 0)

        self.cam_label = QLabel()
        self.cam_label.setAlignment(Qt.AlignCenter)
        self.cam_label.setStyleSheet("background: #000000;")
        self.cam_label.setMinimumSize(640, 420)

        # Overlay de pausa
        self.pause_overlay = QLabel("⏸  Pausado")
        self.pause_overlay.setAlignment(Qt.AlignCenter)
        self.pause_overlay.setStyleSheet(f"""
            color: white;
            font-size: 18px;
            font-weight: 600;
            background: rgba(0,0,0,0.6);
            border-radius: 8px;
            padding: 8px 20px;
        """)
        self.pause_overlay.hide()

        cam_layout.addWidget(self.cam_label)

        layout.addWidget(cam_container, 1)

        # Barra inferior da câmera
        cam_bar = QFrame()
        cam_bar.setFixedHeight(40)
        cam_bar.setStyleSheet(f"background: {COLORS['bg_panel']}; border-top: 1px solid {COLORS['border']};")
        bar_layout = QHBoxLayout(cam_bar)
        bar_layout.setContentsMargins(16, 0, 16, 0)
        bar_layout.setSpacing(8)

        self.cam_info = QLabel("Câmera 0 — 640×480")
        self.cam_info.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px; background: transparent;")
        bar_layout.addWidget(self.cam_info)
        bar_layout.addStretch()

        # Seleção de câmera
        cam_select_label = QLabel("Câmera:")
        cam_select_label.setStyleSheet(f"color: {COLORS['text_sec']}; font-size: 12px; background: transparent;")
        bar_layout.addWidget(cam_select_label)

        self.cam_combo = QComboBox()
        self.cam_combo.setFixedHeight(28)
        self.cam_combo.setCursor(Qt.PointingHandCursor)
        self.cam_combo.setStyleSheet(f"""
            QComboBox {{
                background: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border_light']};
                border-radius: 6px;
                padding: 0 8px;
                font-size: 12px;
                min-width: 110px;
            }}
            QComboBox:hover {{
                border-color: {COLORS['green']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox QAbstractItemView {{
                background: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border_light']};
                selection-background-color: {COLORS['green_dark']};
                selection-color: white;
            }}
        """)
        for idx, name in self._detect_cameras():
            self.cam_combo.addItem(f"{idx} — {name}", idx)
        default = self.cam_combo.findData(2)
        if default >= 0:
            self.cam_combo.setCurrentIndex(default)
        bar_layout.addWidget(self.cam_combo)

        # Botão iniciar câmera
        self.btn_cam = QPushButton("▶  Iniciar Câmera")
        self.btn_cam.setFixedHeight(28)
        self.btn_cam.setCursor(Qt.PointingHandCursor)
        self.btn_cam.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['green']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 0 12px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background: {COLORS['green_dark']}; }}
        """)
        self.btn_cam.clicked.connect(self._toggle_camera)
        bar_layout.addWidget(self.btn_cam)

        layout.addWidget(cam_bar)

        return area

    def _build_right_panel(self):
        panel = QFrame()
        panel.setFixedWidth(340)
        panel.setStyleSheet(f"background: {COLORS['bg_panel']};")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # ── Sessão ativa ───────────────────────────────────────────────────────
        sess_header = QHBoxLayout()
        sess_title = QLabel("SESSÃO ATIVA")
        sess_title.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 10px; font-weight: 700; letter-spacing: 1px; background: transparent;")
        self.live_badge = LiveBadge()
        sess_header.addWidget(sess_title)
        sess_header.addStretch()
        sess_header.addWidget(self.live_badge)
        layout.addLayout(sess_header)

        self.total_label = QLabel("0")
        self.total_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 40px; font-weight: 800; background: transparent;")
        layout.addWidget(self.total_label)

        items_sub = QLabel("itens contados")
        items_sub.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px; background: transparent;")
        layout.addWidget(items_sub)

        # Separador
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {COLORS['border']};")
        layout.addWidget(sep)

        # ── Itens detectados ───────────────────────────────────────────────────
        det_title = QLabel("Itens detectados")
        det_title.setStyleSheet(f"color: {COLORS['text_sec']}; font-size: 12px; font-weight: 600; background: transparent;")
        layout.addWidget(det_title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        items_widget = QWidget()
        items_widget.setStyleSheet("background: transparent;")
        items_layout = QVBoxLayout(items_widget)
        items_layout.setContentsMargins(0, 0, 0, 0)
        items_layout.setSpacing(6)

        for alimento, info in ALIMENTOS_INFO.items():
            card = ItemCard(alimento, info)
            self.item_cards[alimento] = card
            items_layout.addWidget(card)

        items_layout.addStretch()
        scroll.setWidget(items_widget)
        layout.addWidget(scroll, 1)

        # Separador
        sep2 = QFrame()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet(f"background: {COLORS['border']};")
        layout.addWidget(sep2)

        # ── Atividade recente ──────────────────────────────────────────────────
        act_title = QLabel("Atividade recente")
        act_title.setStyleSheet(f"color: {COLORS['text_sec']}; font-size: 12px; font-weight: 600; background: transparent;")
        layout.addWidget(act_title)

        self.activity_layout = QVBoxLayout()
        self.activity_layout.setSpacing(0)
        self._add_activity("✓", "Sessão iniciada", "Sistema pronto para contagem", "agora")
        layout.addLayout(self.activity_layout)

        return panel

    def _build_bottom_bar(self):
        bar = QFrame()
        bar.setFixedHeight(90)
        bar.setStyleSheet(f"background: {COLORS['bg_panel']}; border-top: 1px solid {COLORS['border']};")

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        self.metric_balanca  = MetricCard("BALANÇA AO VIVO", "—", "kg  ● Desconectada")
        self.metric_total    = MetricCard("TOTAL DA SESSÃO", "0 un", "")
        self.metric_taxa     = MetricCard("TAXA", "0.0 un/min", "")

        layout.addWidget(self.metric_balanca, 1)
        layout.addWidget(self.metric_total,   1)
        layout.addWidget(self.metric_taxa,    1)

        return bar

    def _add_activity(self, icon, title, subtitle, time_str):
        item = ActivityItem(icon, title, subtitle, time_str)
        self.activity_layout.insertWidget(0, item)
        # Máximo 5 itens
        while self.activity_layout.count() > 5:
            w = self.activity_layout.takeAt(self.activity_layout.count()-1).widget()
            if w:
                w.deleteLater()

    # ── Lógica ────────────────────────────────────────────────────────────────

    def _tick(self):
        self.session_time += 1
        h = self.session_time // 3600
        m = (self.session_time % 3600) // 60
        s = self.session_time % 60
        self.timer_label.setText(f"{h:02d}:{m:02d}:{s:02d}")

        # Atualiza taxa
        if self.session_time > 0:
            taxa = (self.total_items / self.session_time) * 60
            self.metric_taxa.update_value(f"{taxa:.1f} un/min")

    def _toggle_camera(self):
        if self.cam_thread and self.cam_thread.isRunning():
            self.cam_thread.stop()
            self.cam_thread = None
            self.btn_cam.setText("▶  Iniciar Câmera")
            self.cam_label.clear()
            self.cam_label.setStyleSheet("background: #000000;")
            self.cam_combo.setEnabled(True)
        else:
            import os
            cam_idx = self.cam_combo.currentData()
            self.cam_thread = CameraThread(
                model_path="best2.0.pt" if os.path.exists("best2.0.pt") else None,
                camera_idx=cam_idx
            )
            self.cam_thread.frame_ready.connect(self._update_frame)
            self.cam_thread.detection_ready.connect(self._update_detections)
            self.cam_thread.item_contado.connect(self._on_item_contado)
            self.cam_thread.start()
            self.btn_cam.setText("⏹  Parar Câmera")
            self.cam_combo.setEnabled(False)
            cam_name = self.cam_combo.currentText()
            self.cam_info.setText(f"{cam_name} — 640×480")
            self._add_activity("📷", "Câmera iniciada", f"{cam_name} • aguardando itens cruzarem a linha", "agora")

    def _update_frame(self, qimg):
        pixmap = QPixmap.fromImage(qimg)
        self.cam_label.setPixmap(
            pixmap.scaled(self.cam_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def _update_detections(self, contagem_frame):
        """Atualiza apenas o indicador visual de 'vendo agora' — não altera a contagem acumulada."""
        pass  # A contagem acumulada é gerida por _on_item_contado

    def _on_item_contado(self, classe, peso_kg):
        """
        Chamado UMA VEZ por item, quando ele cruza a linha de contagem.
        Incrementa a contagem acumulada do card correspondente.
        """
        if classe in self.item_cards:
            card = self.item_cards[classe]
            card.contagem += 1
            card.count_label.setText(str(card.contagem))

        self.total_items += 1
        self.total_label.setText(str(self.total_items))

        # Calcula total em kg para o metric
        total_kg = sum(
            self.item_cards[al].contagem * ALIMENTOS_INFO[al]["peso_kg"]
            for al in self.item_cards
        )
        self.metric_total.update_value(f"{self.total_items} un")
        self.metric_balanca.update_value(f"{total_kg:.2f} kg")

        # Registra na atividade
        info  = ALIMENTOS_INFO.get(classe, {})
        peso_str = info.get("peso", "?")
        self._add_activity(
            "✓",
            f"{classe.replace('_',' ').title()} contado",
            f"+1 un  •  +{peso_kg:.3f} kg  •  {peso_str}",
            self.timer_label.text()
        )

    def _toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.cam_thread:
            self.cam_thread.paused = self.is_paused

        if self.is_paused:
            self.btn_pause.setText("▶  Retomar")
            self._add_activity("⏸", "Sessão pausada", "Captura interrompida",
                               self.timer_label.text())
        else:
            self.btn_pause.setText("⏸  Pausar")
            self._add_activity("▶", "Sessão retomada", "Captura em andamento", "agora")

    def _end_session(self):
        total_un = sum(card.contagem for card in self.item_cards.values())
        total_kg = sum(
            self.item_cards[al].contagem * ALIMENTOS_INFO[al]["peso_kg"]
            for al in self.item_cards
        )
        self._add_activity(
            "✓",
            f"Sessão encerrada",
            f"{total_un} itens  •  {total_kg:.2f} kg total",
            self.timer_label.text()
        )
        if self.cam_thread:
            self.cam_thread.stop()

    def closeEvent(self, event):
        if self.cam_thread:
            self.cam_thread.stop()
        super().closeEvent(event)


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Paleta dark global
    palette = QPalette()
    palette.setColor(QPalette.Window,          QColor(COLORS["bg_dark"]))
    palette.setColor(QPalette.WindowText,      QColor(COLORS["text_primary"]))
    palette.setColor(QPalette.Base,            QColor(COLORS["bg_panel"]))
    palette.setColor(QPalette.AlternateBase,   QColor(COLORS["bg_card"]))
    palette.setColor(QPalette.Text,            QColor(COLORS["text_primary"]))
    palette.setColor(QPalette.Button,          QColor(COLORS["bg_card"]))
    palette.setColor(QPalette.ButtonText,      QColor(COLORS["text_primary"]))
    palette.setColor(QPalette.Highlight,       QColor(COLORS["green"]))
    palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(palette)

    window = ContaCerto()
    window.show()
    sys.exit(app.exec())