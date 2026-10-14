import sys
import os
import time
import json
import sqlite3
import uuid
import platform
import subprocess
import threading
import hashlib
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QLineEdit, QTextEdit, QListWidget,
    QListWidgetItem, QComboBox, QSpinBox, QFileDialog, QMessageBox, QFrame,
    QDialog, QFormLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QCheckBox, QGroupBox, QScrollArea, QSplitter, QTabWidget
)
from PyQt6.QtCore import Qt, QSize, QUrl, QTimer
from PyQt6.QtGui import QIcon, QFont, QPixmap, QColor
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

# ==============================================================================
# 1. NÚCLEO DE BASE DE DADOS, SEGURANÇA E INTELIGÊNCIA ARTIFICIAL
# ==============================================================================

BLACKLIST_FILE = "comunic_blacklist.json"
APPEALS_FILE = "comunic_appeals.json"
FEED_FILE = "comunic_feed.json"
LICENSE_FILE = "comunic_license.json"
FREE_CHAT_FILE = "comunic_free_chat.json"
SOS_CONTACTS_FILE = "comunic_sos_contacts.json"

def carregar_ficheiro(filename, default_val):
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return default_val

def guardar_ficheiro(filename, data):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception:
        pass

GLOBAL_FEEDBACK_LIST = carregar_ficheiro("comunic_feedback.json", [])
GLOBAL_BROADCAST_MESSAGES = []
GLOBAL_SECURITY_LOGS = []
GLOBAL_BLACKLISTED_USERS = carregar_ficheiro(BLACKLIST_FILE, [])
GLOBAL_APPEALS_LIST = carregar_ficheiro(APPEALS_FILE, [])
GLOBAL_FREE_CHAT_MESSAGES = carregar_ficheiro(FREE_CHAT_FILE, [
    {
        "author": "Sistema Comunic",
        "country": "Moçambique",
        "time": "2026-10-10 12:00",
        "content": "Bem-vindo ao Bate-Papo Livre de Apoio Emocional. Partilhe ideias e converse livremente com compatriotas do seu país."
    }
])
GLOBAL_FEED_POSTS = carregar_ficheiro(FEED_FILE, [
    {
        "author": "António Bila",
        "country": "Moçambique",
        "time": "2026-10-10 10:30",
        "content": "📸 Plataforma Comunic atualizada com segurança soberana e painéis de entretenimento! 🚀"
    }
])

ADMIN_PASSWORD_HASH = hashlib.sha256("Bila2026".encode('utf-8')).hexdigest()

"Comunic Escuro (Tatico)" = """
    QMainWindow { background-color: #0b141a; color: #e9edef; font-family: 'Segoe UI', Arial; }
    QLabel { color: #e9edef; font-family: 'Segoe UI', Arial; font-size: 13px; }
    QTabWidget::pane { border: none; background: #111b21; border-radius: 8px; }
    QTabBar::tab { background: #202c33; color: #8696a0; padding: 10px 15px; margin: 2px; border-radius: 6px; font-weight: bold; font-size: 12px; }
    QTabBar::tab:selected { background: #005c4b; color: #ffffff; }
    QListWidget { background-color: #111b21; color: #e9edef; border: none; border-radius: 8px; padding: 5px; }
    QListWidget::item { background-color: #202c33; color: #e9edef; border-radius: 8px; margin-bottom: 8px; padding: 12px; }
    QListWidget::item:selected { background-color: #2a3942; }
    QCheckBox { color: #e9edef; spacing: 8px; padding: 5px; font-size: 13px; }
    QLineEdit, QTextEdit, QComboBox, QSpinBox { background-color: #2a3942; color: #ffffff; border: none; border-radius: 10px; padding: 10px; font-size: 13px; }
    QPushButton { border-radius: 18px; background-color: #00a884; color: white; font-weight: bold; border: none; padding: 8px 16px; }
    QPushButton:hover { background-color: #029374; }
    QFrame#SideMenu { background-color: #111b21; border-right: 1px solid #202c33; }
    QPushButton.MenuButton {
        background-color: transparent; color: #8696a0; text-align: left;
        padding: 10px 14px; font-size: 13px; font-weight: 600; border: none; border-radius: 6px;
    }
    QPushButton.MenuButton:hover { background-color: #202c33; color: #00a884; }
    QPushButton.MenuButton:checked { background-color: #005c4b; color: #FFFFFF; }
"""

CYBERPUNK_NEON_STYLE = """
    QMainWindow { background-color: #05050a; color: #00ffcc; font-family: 'Segoe UI', Arial; }
    QLabel { color: #00ffcc; font-family: 'Segoe UI', Arial; font-size: 13px; }
    QTabWidget::pane { border: 1px solid #ff007f; background: #0b0b16; border-radius: 8px; }
    QTabBar::tab { background: #15152b; color: #ff007f; padding: 10px 15px; margin: 2px; border-radius: 6px; font-weight: bold; font-size: 12px; }
    QTabBar::tab:selected { background: #ff007f; color: #ffffff; }
    QListWidget { background-color: #0b0b16; color: #00ffcc; border: 1px solid #00ffcc; border-radius: 8px; padding: 5px; }
    QListWidget::item { background-color: #15152b; color: #00ffcc; border-radius: 8px; margin-bottom: 8px; padding: 12px; border: 1px solid #ff007f; }
    QListWidget::item:selected { background-color: #2b1535; }
    QCheckBox { color: #00ffcc; spacing: 8px; padding: 5px; font-size: 13px; }
    QLineEdit, QTextEdit, QComboBox, QSpinBox { background-color: #15152b; color: #00ffcc; border: 1px solid #00ffcc; border-radius: 10px; padding: 10px; font-size: 13px; }
    QPushButton { border-radius: 18px; background-color: #ff007f; color: white; font-weight: bold; border: none; padding: 8px 16px; }
    QPushButton:hover { background-color: #ff3399; }
    QFrame#SideMenu { background-color: #0b0b16; border-right: 1px solid #ff007f; }
    QPushButton.MenuButton {
        background-color: transparent; color: #00ffcc; text-align: left;
        padding: 10px 14px; font-size: 13px; font-weight: 600; border: none; border-radius: 6px;
    }
    QPushButton.MenuButton:hover { background-color: #15152b; color: #ff007f; }
    QPushButton.MenuButton:checked { background-color: #ff007f; color: #FFFFFF; }
"""

LISTA_IDIOMAS_MUNDIAIS = [
    "Português", "Inglês (English)", "Espanhol (Español)", "Francês (Français)", 
    "Alemão (Deutsch)", "Russo (Русский)", "Mandarim (中文)", "Hindi (हिन्दी)", 
    "Árabe (العربية)", "Japonês (日本語)", "Coreano (한국어)", "Italiano (Italiano)", 
    "Neerlandês (Nederlands)", "Turco (Türkçe)", "Polaco (Polski)", 
    "Vietnamita (Tiếng Việt)", "Swahili (Kiswahili)", "Ucraniano (Українська)", 
    "Sueco (Svenska)", "Grego (Ελληνικά)"
]

class ComunicEnterpriseDatabase:
    def __init__(self, db_name="comunic_industrial_master.db"):
        self.db_path = db_name
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.init_schema()

    def init_schema(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT UNIQUE NOT NULL,
                username TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                device_model TEXT,
                device_uuid TEXT,
                sim_slots TEXT,
                ram_gb TEXT,
                storage_gb TEXT,
                failed_attempts INTEGER DEFAULT 0,
                is_blocked INTEGER DEFAULT 0,
                trial_start_date TEXT,
                is_paid INTEGER DEFAULT 0,
                recovery_key TEXT,
                state TEXT DEFAULT 'Maputo',
                nationality TEXT DEFAULT 'Moçambique',
                avatar_path TEXT DEFAULT ''
            )
        ''')
        
        # Migração automática de BD antiga se faltarem colunas
        self.cursor.execute("PRAGMA table_info(users)")
        cols = [col[1] for col in self.cursor.fetchall()]
        if "state" not in cols:
            try: self.cursor.execute("ALTER TABLE users ADD COLUMN state TEXT DEFAULT 'Maputo'")
            except Exception: pass
        if "nationality" not in cols:
            try: self.cursor.execute("ALTER TABLE users ADD COLUMN nationality TEXT DEFAULT 'Moçambique'")
            except Exception: pass
        if "avatar_path" not in cols:
            try: self.cursor.execute("ALTER TABLE users ADD COLUMN avatar_path TEXT DEFAULT ''")
            except Exception: pass

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT,
                receiver TEXT,
                original_text TEXT,
                translated_text TEXT,
                status TEXT DEFAULT 'delivered',
                timestamp TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reporter TEXT,
                reported_contact TEXT,
                reason TEXT,
                status TEXT DEFAULT 'Pending',
                timestamp TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sos_contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_phone TEXT,
                contact_name TEXT,
                contact_phone TEXT
            )
        ''')
        self.conn.commit()

    def register_user(self, phone, username, pwd, hw):
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            rec_key = f"COMUNIC-REC-{uuid.uuid4().hex[:8].upper()}"
            self.cursor.execute('''
                INSERT INTO users (phone, username, password_hash, device_model, device_uuid, sim_slots, ram_gb, storage_gb, trial_start_date, recovery_key)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (phone, username, pwd, hw['model'], hw['uuid'], hw['sims'], hw['ram'], hw['storage'], now, rec_key))
            self.conn.commit()
            return True, rec_key
        except sqlite3.IntegrityError:
            return False, None

    def get_user(self, phone):
        self.cursor.execute('SELECT device_model, sim_slots, ram_gb, storage_gb, username, is_blocked, password_hash, recovery_key, trial_start_date, is_paid, state, nationality, avatar_path FROM users WHERE phone = ?', (phone,))
        return self.cursor.fetchone()

    def update_user_profile(self, phone, username, state, nationality, avatar):
        self.cursor.execute('UPDATE users SET username = ?, state = ?, nationality = ?, avatar_path = ? WHERE phone = ?', (username, state, nationality, avatar, phone))
        self.conn.commit()

    def update_user_password_and_phone(self, old_phone, new_phone, new_pwd):
        try:
            self.cursor.execute('UPDATE users SET phone = ?, password_hash = ? WHERE phone = ?', (new_phone, new_pwd, old_phone))
            self.conn.commit()
            return True
        except Exception:
            return False

    def delete_user_account(self, phone):
        self.cursor.execute('DELETE FROM users WHERE phone = ?', (phone,))
        self.conn.commit()

    def update_failed_login(self, phone, reset=False):
        if reset:
            self.cursor.execute('UPDATE users SET failed_attempts = 0 WHERE phone = ?', (phone,))
        else:
            self.cursor.execute('UPDATE users SET failed_attempts = failed_attempts + 1 WHERE phone = ?', (phone,))
            self.cursor.execute('SELECT failed_attempts FROM users WHERE phone = ?', (phone,))
            res = self.cursor.fetchone()
            if res and res[0] >= 5:
                self.cursor.execute('UPDATE users SET is_blocked = 1 WHERE phone = ?', (phone,))
        self.conn.commit()


class DeviceSecurityProtocol:
    @staticmethod
    def get_hardware_telemetry():
        return {
            "model": f"{platform.system()} {platform.machine()} (Verified Enterprise)",
            "uuid": str(uuid.getnode()),
            "sims": "Dual SIM",
            "ram": "8 GB",
            "storage": "256 GB"
        }


class EmergencySOSController:
    @staticmethod
    def trigger_fake_shutdown():
        print("\n[MODO SEGURANÇA TÁTICO]: Encerramento Falso (Fake Shutdown) ativado.")
        print("[RASTREAMENTO OCULTO]: Ecrã simulado em preto. Transmissão contínua de GPS e captura silenciosa de fotografias em segundo plano.")


class ArtificialIntelligenceEngine:
    def __init__(self, target_lang="Português"):
        self.target_lang = target_lang

    def translate_bilingual(self, text):
        if not text:
            return ""
        if "hello" in text.lower():
            return "Olá (Tradução Automática Bilíngue)"
        elif "good morning" in text.lower():
            return "Bom dia (Tradução Automática Bilíngue)"
        return f"[{self.target_lang} Translation]: {text}"

    def text_to_speech(self, text):
        print(f"[IA - TEXTO PARA VOZ]: A reproduzir em voz alta -> '{text}'")

    def transcribe_audio(self):
        return "Transcrição de Áudio da IA: 'Nota de voz recebida e convertida em texto com sucesso absoluto.'"


# ==============================================================================
# 2. DIÁLOGOS E COMPONENTES AVANÇADOS DO COMUNIC
# ==============================================================================

class NewConversationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("💬 Iniciar Nova Conversa")
        self.setFixedSize(400, 260)
        self.setStyleSheet("background-color: #111b21; color: #e9edef; font-family: 'Segoe UI', Arial;")
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Iniciar Nova Conversa Direta</b>").setStyleSheet("color: #00a884; font-size: 14px;"))
        
        layout.addWidget(QLabel("Nome do Contacto / Destinatário:"))
        self.inp_name = QLineEdit()
        layout.addWidget(self.inp_name)
        
        layout.addWidget(QLabel("Número de Telemóvel ou ID:"))
        self.inp_phone = QLineEdit()
        layout.addWidget(self.inp_phone)
        
        btn_start = QPushButton("🚀 Iniciar Chat")
        btn_start.clicked.connect(self.accept)
        layout.addWidget(btn_start)

class CameraFilterDialog(QDialog):
    def __init__(self, mode="photo", parent=None):
        super().__init__(parent)
        self.mode = mode
        self.setWindowTitle("📷 Câmara & Estúdio Criativo (Até 5 Filtros) — Comunic")
        self.setFixedSize(540, 740)
        self.setStyleSheet("background-color: #111b21; color: #e9edef; font-family: 'Segoe UI', Arial;")
        
        layout = QVBoxLayout(self)
        lbl_title = QLabel("🤖🔥 Estúdio Supremo — Robôs, Frutas, Tattoos & AR")
        lbl_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #00a884;")
        layout.addWidget(lbl_title)
        
        self.lbl_viewfinder = QLabel("📷 [ VIZOR DA CÂMARA EM DIRETO ]\n\n✨ Filtros Ativos: [ Nenhum ]")
        self.lbl_viewfinder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_viewfinder.setWordWrap(True)
        self.lbl_viewfinder.setStyleSheet("background-color: #0b141a; color: #8696a0; border-radius: 12px; font-size: 12px; min-height: 110px; border: 2px dashed #00a884; padding: 10px;")
        layout.addWidget(self.lbl_viewfinder)
        
        layout.addWidget(QLabel("🎛️ Selecione de 1 a 5 Filtros em Simultâneo:"))
        scroll_filters = QScrollArea()
        scroll_filters.setWidgetResizable(True)
        scroll_filters.setStyleSheet("background-color: #0b141a; border: none;")
        
        content_widget = QWidget()
        self.filters_layout = QVBoxLayout(content_widget)
        self.filter_checkboxes = []
        opcoes_filtros = [
            "🤖⚡ Armadura Cibernética Decepticon", "🤖🍍 Robô de Frutas Suprema",
            "🍉 Mecha-Melancia & Salada Explosiva", "👁️ Olhos Azuis Intensos",
            "🔴 Olhos Vermelhos de Demónio", "🦁 Máscara de Leão Selvagem",
            "🐺 Máscara de Lobo Uivante", "✒️ Tatuagem Tribal (Bochecha)",
            "✒️ Tatuagem de Dragão (Ombro)", "🎨 Tom de Pele Neon Glow Noturno",
            "🤪 Vista Panorâmica Distorcida", "👗 Vestido de Gala Feminino",
            "👔 Traje Formal Masculino (Smoking)", "🦸 Traje de Super-Herói Cósmico",
            "🕶️ Óculos Cyberpunk", "🔥 Chamas Ardentes ao Redor"
        ]
        for nome_filtro in opcoes_filtros:
            chk = QCheckBox(nome_filtro)
            chk.stateChanged.connect(self.atualizar_preview_filtros)
            self.filters_layout.addWidget(chk)
            self.filter_checkboxes.append(chk)
        scroll_filters.setWidget(content_widget)
        layout.addWidget(scroll_filters)
        
        btn_text = "📸 Capturar com estes Filtros" if mode == "photo" else "🔴 Iniciar Live"
        self.btn_capture = QPushButton(btn_text)
        self.btn_capture.clicked.connect(self.validar_e_aceitar)
        layout.addWidget(self.btn_capture)
        self.selected_filters_list = []

    def atualizar_preview_filtros(self):
        selecionados = [chk.text() for chk in self.filter_checkboxes if chk.isChecked()]
        if len(selecionados) > 5:
            sender = self.sender()
            if sender: sender.setChecked(False)
            QMessageBox.warning(self, "Limite de Filtros", "Pode selecionar no máximo 5 filtros em simultâneo!")
            return
        self.selected_filters_list = selecionados
        txt_ativos = ", ".join(selecionados) if selecionados else "Nenhum"
        self.lbl_viewfinder.setText(f"📷 [ VIZOR DA CÂMARA EM DIRETO ]\n\n✨ Filtros Ativos ({len(selecionados)}/5): <b>{txt_ativos}</b>")

    def validar_e_aceitar(self):
        if not self.selected_filters_list:
            self.selected_filters_list = ["✨ Normal (Sem Filtro)"]
        self.accept()

class PaymentLockDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.setWindowTitle("🔒 COMUNIC — Conta Bloqueada (Período de Teste Expirado)")
        self.setFixedSize(480, 580)
        self.setStyleSheet("background-color: #111b21; color: #e9edef; font-family: 'Segoe UI', Arial;")
        
        layout = QVBoxLayout(self)
        lbl_alert = QLabel("⚠️ PERÍODO DE TESTE GRATUITO EXPIRODADO")
        lbl_alert.setStyleSheet("font-size: 15px; font-weight: bold; color: #ff5252;")
        layout.addWidget(lbl_alert)
        
        info_txt = QLabel(
            f"Olá, <b>{username}</b>. Os seus 7 dias de avaliação gratuita do COMUNIC terminaram.\n\n"
            "Para continuar a desfrutar da plataforma de forma vitalícia e desbloquear o acesso total, efetue o pagamento único de:\n\n"
            "💎 <b>Valor:</b> 50 MT\n📱 <b>Método:</b> M-Pesa\n📞 <b>Número:</b> 842495357\n👤 <b>Nome:</b> António Bila"
        )
        info_txt.setWordWrap(True)
        info_txt.setStyleSheet("color: #e9edef; font-size: 13px; background-color: #0b141a; padding: 14px; border-radius: 8px;")
        layout.addWidget(info_txt)
        
        layout.addWidget(QLabel("🔑 Insira o seu Código de Ativação:"))
        self.input_code = QLineEdit()
        self.input_code.setPlaceholderText("Insira o código de ativação...")
        layout.addWidget(self.input_code)
        
        self.btn_activate = QPushButton("🚀 Ativar Conta com Código")
        self.btn_activate.clicked.connect(self.verificar_ativacao)
        layout.addWidget(self.btn_activate)
        
        self.btn_exit = QPushButton("Sair da Aplicação")
        self.btn_exit.setStyleSheet("background-color: #D32F2F; color: white;")
        self.btn_exit.clicked.connect(sys.exit)
        layout.addWidget(self.btn_exit)

    def verificar_ativacao(self):
        codigo = self.input_code.text().strip()
        if codigo == "BILA-VIP-2026" or codigo == "50MT":
            licenca = carregar_ficheiro(LICENSE_FILE, {})
            licenca["is_activated"] = True
            guardar_ficheiro(LICENSE_FILE, licenca)
            QMessageBox.information(self, "Sucesso", "Conta ativada com sucesso!")
            self.accept()
        else:
            QMessageBox.warning(self, "Código Inválido", "O código de ativação inserido está incorreto.")

class ContactDevDialog(QDialog):
    def __init__(self, username, country, parent=None):
        super().__init__(parent)
        self.username = username
        self.country = country
        self.setWindowTitle("✉️ Fale Connosco")
        self.setFixedSize(420, 360)
        self.setStyleSheet("background-color: #111b21; color: #e9edef;")
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Envie a sua mensagem ou comprovativo M-Pesa de 50 MT:"))
        self.input_msg = QTextEdit()
        layout.addWidget(self.input_msg)
        
        btn = QPushButton("Enviar ao Desenvolvedor")
        btn.clicked.connect(self.send)
        layout.addWidget(btn)

    def send(self):
        t = self.input_msg.toPlainText().strip()
        if not t: return
        GLOBAL_FEEDBACK_LIST.append({"user": self.username, "country": self.country, "msg": t})
        guardar_ficheiro("comunic_feedback.json", GLOBAL_FEEDBACK_LIST)
        QMessageBox.information(self, "Enviado", "Mensagem encaminhada com sucesso.")
        self.accept()

class CreatePostDialog(QDialog):
    def __init__(self, username, country, parent=None):
        super().__init__(parent)
        self.username = username
        self.country = country
        self.filtros_foto_anexados = []
        self.setWindowTitle("🌐 Criar Publicação Global")
        self.setFixedSize(460, 440)
        self.setStyleSheet("background-color: #111b21; color: #e9edef;")
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Escreva a sua legenda:"))
        self.input_post = QTextEdit()
        layout.addWidget(self.input_post)
        
        self.lbl_status_foto = QLabel("📷 Nenhuma fotografia anexada.")
        layout.addWidget(self.lbl_status_foto)
        
        btn_cam = QPushButton("📷 Câmara & Multi-Filtros")
        btn_cam.clicked.connect(self.abrir_camara_filtro)
        layout.addWidget(btn_cam)
        
        btn_pub = QPushButton("🚀 Publicar Globalmente")
        btn_pub.clicked.connect(self.publicar)
        layout.addWidget(btn_pub)

    def abrir_camara_filtro(self):
        cam = CameraFilterDialog(mode="photo", parent=self)
        if cam.exec():
            self.filtros_foto_anexados = cam.selected_filters_list
            self.lbl_status_foto.setText(f"✅ Filtros: {', '.join(self.filtros_foto_anexados)}")

    def publicar(self):
        texto = self.input_post.toPlainText().strip()
        if not texto and not self.filtros_foto_anexados: return
        conteudo = texto
        if self.filtros_foto_anexados:
            conteudo += f"\n\n[📸 Filtros: {', '.join(self.filtros_foto_anexados)}]"
        GLOBAL_FEED_POSTS.insert(0, {"author": self.username, "country": self.country, "time": datetime.now().strftime("%Y-%m-%d %H:%M"), "content": conteudo})
        guardar_ficheiro(FEED_FILE, GLOBAL_FEED_POSTS)
        self.accept()

class LivePlayerWindow(QDialog):
    def __init__(self, live_title, attached_file, user_language, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"🔴 Transmissão em Direto — {live_title}")
        self.setFixedSize(520, 520)
        self.setStyleSheet("background-color: #0b141a; color: #e9edef;")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"📡 A transmitir: {live_title}").setStyleSheet("font-weight: bold; color: #ff5252; font-size: 14px;"))
        
        file_info = f"📎 Ficheiro Anexado: <b>{os.path.basename(attached_file)}</b>" if attached_file else "🎥 [Transmissão em Direto Padrão com Multi-Filtros]"
        layout.addWidget(QLabel(file_info))
        
        lbl = QLabel("🎥 [Feed de Vídeo em Direto / Multimédia Ativo]")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("background-color: #111b21; border-radius: 8px; min-height: 220px; border: 1px solid #00a884;")
        layout.addWidget(lbl)
        
        btn = QPushButton("Sair da Transmissão")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

class AIChatRoomDialog(QDialog):
    def __init__(self, user_language, parent=None):
        super().__init__(parent)
        self.user_language = user_language
        self.setWindowTitle("🤖 Assistente Oficial — COMUNIC AI")
        self.setFixedSize(520, 760)
        self.setStyleSheet("background-color: #0b141a; color: #e9edef;")
        layout = QVBoxLayout(self)
        self.chat_list = QListWidget()
        self.chat_list.addItem("🤖 Olá! Sou a Inteligência Artificial do COMUNIC.")
        layout.addWidget(self.chat_list)
        
        hbox = QHBoxLayout()
        self.inp = QLineEdit()
        self.inp.setPlaceholderText("Escreva à IA...")
        btn = QPushButton("Enviar")
        
        # Conectamos o botão à função segura que processa a conversa
        btn.clicked.connect(self.enviar_e_responder)
        
        hbox.addWidget(self.inp)
        hbox.addWidget(btn)
        layout.addLayout(hbox)

    def enviar_e_responder(self):
        texto_utilizador = self.inp.text().strip()
        if texto_utilizador:
            # 1. Mostra a mensagem do utilizador no chat imediatamente
            self.chat_list.addItem(f"👤 Tu: {texto_utilizador}")
            self.inp.clear()
            self.chat_list.scrollToBottom()
            
            # 2. Indicador visual de processamento online
            self.chat_list.addItem("🤖 Assistente Comunic: A contactar o núcleo online...")
            self.chat_list.scrollToBottom()
            
            # 3. Dispara a Thread para não congelar a interface do app
            threading.Thread(target=self.processar_resposta_online, args=(texto_utilizador,), daemon=True).start()

    def processar_resposta_online(self, pergunta):
        import urllib.request
        import json
        
        api_url = "https://api.groq.com/openai/v1/chat/completions"
        api_key = "TUA_API_KEY_AQUI"  # Insere a tua chave de API aqui quando quiseres
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": "És o assistente oficial do COMUNIC, uma aplicação segura, moderna e orientada à privacidade."},
                {"role": "user", "content": pergunta}
            ],
            "temperature": 0.7
        }
        
        try:
            req = urllib.request.Request(
                api_url, 
                data=json.dumps(payload).encode('utf-8'), 
                headers=headers, 
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                resposta_real = res_data['choices'][0]['message']['content']
        except Exception as e:
            resposta_real = f"🌐 [Modo Nuvem COMUNIC]: Mensagem recebida ('{pergunta}'). Insere a tua chave de API para obter respostas em tempo real."
        
        from PyQt6.QtCore import QMetaObject, Qt
        self.atualizar_chat_seguro(resposta_real)

    def atualizar_chat_seguro(self, texto_resposta):
        row = self.chat_list.count() - 1
        if row >= 0:
            item = self.chat_list.takeItem(row)
            del item
        self.chat_list.addItem(texto_resposta)
        self.chat_list.scrollToBottom()

class ChatRoomDialog(QDialog):
    def __init__(self, contact_name, user_language, parent=None):
        super().__init__(parent)
        self.contact_name = contact_name
        self.user_language = user_language
        self.setWindowTitle(f"Chat com {contact_name}")
        self.setFixedSize(540, 780)
        self.setStyleSheet("background-color: #0b141a; color: #e9edef;")
        
        layout = QVBoxLayout(self)
        self.chat_list = QListWidget()
        item = QListWidgetItem("🌐 Original: Hello friend!\n🔤 Tradução: Olá amigo!\nStatus: 📕 [Livro Fechado - Entregue (Clique para ler)]")
        item.setData(Qt.ItemDataRole.UserRole, {"orig": "Hello friend!", "trans": "Olá amigo!", "read": False})
        self.chat_list.addItem(item)
        self.chat_list.itemClicked.connect(self.marcar_lido)
        layout.addWidget(self.chat_list)

        hbox = QHBoxLayout()
        self.inp = QLineEdit()
        btn = QPushButton("Enviar")
        hbox.addWidget(self.inp)
        hbox.addWidget(btn)
        layout.addLayout(hbox)

    def marcar_lido(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data and not data["read"]:
            data["read"] = True
            item.setText(f"🌐 Original: {data['orig']}\n🔤 Tradução: {data['trans']}\nStatus: 📖 [Livro Aberto - Lido com Som 📖]")
            print("[SOM 📖]: Livro aberto, efeito de som reproduzido.")

class SOSDialog(QDialog):
    def __init__(self, sos_contacts, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🚨 PAINEL DE EMERGÊNCIA SOS GLOBAL")
        self.setFixedSize(460, 480)
        self.setStyleSheet("background-color: #2C0B0E; color: #FFFFFF;")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("⚠️ ALERTA DE EMERGÊNCIA ATIVO").setStyleSheet("color: #FF5252; font-weight: bold; font-size: 16px;"))
        layout.addWidget(QLabel("📍 GPS Live: Lat: -25.9692, Lon: 32.5732 | Maputo"))
        self.lst = QListWidget()
        for c in sos_contacts:
            if c: self.lst.addItem(f"✅ Notificado: {c}")
        layout.addWidget(self.lst)
        btn = QPushButton("⏹️ Desativar SOS")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

class FindMyFriendDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🤝 Encontro Direto (Navegação GPS P2P)")
        self.setFixedSize(460, 420)
        self.setStyleSheet("background-color: #111b21; color: #e9edef; font-family: 'Segoe UI', Arial;")
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("🗺️ Conexão Ponto a Point (P2P) — Find My Friend").setStyleSheet("font-weight: bold; color: #00a884; font-size: 14px;"))
        
        layout.addWidget(QLabel("Nome do Amigo / Utilizador:"))
        self.inp_name = QLineEdit()
        layout.addWidget(self.inp_name)
        
        layout.addWidget(QLabel("Número de Telemóvel do Amigo:"))
        self.inp_phone = QLineEdit()
        layout.addWidget(self.inp_phone)
        
        btn_connect = QPushButton("🛰️ Conectar & Iniciar Rota GPS em Direto")
        btn_connect.clicked.connect(self.conectar_amigo)
        layout.addWidget(btn_connect)

    def conectar_amigo(self):
        nome = self.inp_name.text().strip()
        tel = self.inp_phone.text().strip()
        if not nome or not tel:
            QMessageBox.warning(self, "Aviso", "Preencha o nome e o número de telemóvel do amigo.")
            return
        QMessageBox.information(self, "Conexão P2P Ativa", f"Conexão estabelecida com sucesso com <b>{nome}</b> ({tel}). Localização em direto iniciada!")
        self.accept()


# ==============================================================================
# 3. WORKSPACE COM AS 14 ABAS NATIVAS COMPLETAS E ATUALIZADAS
# ==============================================================================

class ComunicIndustrialWorkspace(QMainWindow):
    def __init__(self, db_manager, user_phone, user_name):
        super().__init__()
        self.db = db_manager
        self.phone = user_phone
        self.username = user_name
        self.user_language = "Português"
        self.user_country = "Moçambique"
        self.ai = ArtificialIntelligenceEngine()
        self.current_theme = "Comunic Escuro (Tatico)"
        
        rec = self.db.get_user(self.phone)
        if rec and len(rec) >= 13:
            self.state = rec[10] if rec[10] else "Maputo"
            self.nationality = rec[11] if rec[11] else "Moçambique"
            self.avatar_path = rec[12] if rec[12] else ""
        else:
            self.state = "Maputo"
            self.nationality = "Moçambique"
            self.avatar_path = ""

        self.setWindowTitle(f"COMUNIC — Plataforma Social & Global | Utilizador: {self.username}")
        self.resize(1450, 900)
        self.setStyleSheet("Comunic Escuro (Tatico)")

        self.sos_contacts_list = ["Madala 86 (+258 84 000 8686)", "Casa / Senhora (+258 84 111 2233)"]

        self.sos_timer = QTimer(self)
        self.sos_timer.timeout.connect(self.disparar_aviso_sos_10min)
        self.sos_timer.start(600000)

        self.build_ui()

    def build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.side_menu = QFrame()
        self.side_menu.setObjectName("SideMenu")
        self.side_menu.setFixedWidth(260)
        menu_lay = QVBoxLayout(self.side_menu)
        menu_lay.setContentsMargins(12, 20, 12, 20)

        title = QLabel("COMUNIC")
        title.setStyleSheet("font-size: 24px; font-weight: 800; margin-bottom: 15px; letter-spacing: 2px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        menu_lay.addWidget(title)

        self.tab_buttons = []
        tabs_def = [
            ("1. Chats", 0), ("2. Feed", 1), ("3. Contactos", 2),
            ("4. Lives", 3), ("5. Entretenimento", 4), ("6. Bate-papo livre", 5),
            ("7. Perfil", 6), ("8. Definições", 7), ("9. Painel Admin", 8),
            ("10. Find My Friend", 9), ("11. Guia", 10), ("12. Fale Connosco", 11),
            ("13. SOS", 12), ("14. Câmera", 13)
        ]

        for text, index in tabs_def:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setProperty("class", "MenuButton")
            btn.clicked.connect(lambda checked, idx=index: self.switch_tab(idx))
            menu_lay.addWidget(btn)
            self.tab_buttons.append(btn)

        menu_lay.addStretch()

        self.stack = QStackedWidget()
        self.build_fourteen_tabs()

        layout.addWidget(self.side_menu, 1)
        layout.addWidget(self.stack, 5)
        self.switch_tab(0)

    def switch_tab(self, index):
        for i, b in enumerate(self.tab_buttons):
            b.setChecked(i == index)
        self.stack.setCurrentIndex(index)

    def build_fourteen_tabs(self):
        self.stack.addWidget(self.tab_1_chats())
        self.stack.addWidget(self.tab_2_feed())
        self.stack.addWidget(self.tab_3_contacts())
        self.stack.addWidget(self.tab_4_lives())
        self.stack.addWidget(self.tab_5_entertainment())
        self.stack.addWidget(self.tab_6_free_chat())
        self.stack.addWidget(self.tab_7_profile())
        self.stack.addWidget(self.tab_8_settings())
        self.stack.addWidget(self.tab_9_admin())
        self.stack.addWidget(self.tab_10_find_friend())
        self.stack.addWidget(self.tab_11_guide())
        self.stack.addWidget(self.tab_12_contact_us())
        self.stack.addWidget(self.stack_13_sos())
        self.stack.addWidget(self.tab_14_camera())

    def tab_1_chats(self):
        w = QWidget()
        l = QVBoxLayout(w)
        
        top_chat = QHBoxLayout()
        top_chat.addWidget(QLabel("<b>Aba 1: Chats Inteligentes</b>").setStyleSheet("font-size: 15px; font-weight: bold;"))
        top_chat.addStretch()
        btn_new_chat = QPushButton("💬 Iniciar Nova Conversa")
        btn_new_chat.clicked.connect(self.iniciar_nova_conversa)
        top_chat.addWidget(btn_new_chat)
        l.addLayout(top_chat)

        self.chat_list_main = QListWidget()
        self.chat_list_main.addItem("🤖 👤 Assistente Comunic (IA Ativa)")
        self.chat_list_main.addItem("🟢 👤 Ana Sousa")
        self.chat_list_main.itemDoubleClicked.connect(lambda item: AIChatRoomDialog(self.user_language, self).exec() if "Assistente" in item.text() else ChatRoomDialog("Ana Sousa", self.user_language, self).exec())
        l.addWidget(self.chat_list_main)
        return w

    def iniciar_nova_conversa(self):
        dlg = NewConversationDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            nome = dlg.inp_name.text().strip()
            tel = dlg.inp_phone.text().strip()
            if nome:
                self.chat_list_main.addItem(f"🟢 👤 {nome} ({tel})")
                QMessageBox.information(self, "Sucesso", f"Conversa iniciada com {nome}!")

    def tab_2_feed(self):
        w = QWidget()
        l = QVBoxLayout(w)
        top = QHBoxLayout()
        top.addWidget(QLabel("<b>Aba 2: Feed Mundial</b>").setStyleSheet("font-size: 15px; font-weight: bold;"))
        top.addStretch()
        btn_post = QPushButton("➕ Criar Publicação")
        btn_post.clicked.connect(lambda: (CreatePostDialog(self.username, self.user_country, self).exec(), self.atualizar_feed()))
        top.addWidget(btn_post)
        l.addLayout(top)

        self.feed_list = QListWidget()
        self.atualizar_feed()
        l.addWidget(self.feed_list)
        return w

    def atualizar_feed(self):
        self.feed_list.clear()
        for p in GLOBAL_FEED_POSTS:
            self.feed_list.addItem(f"👤 {p['author']} ({p['country']}) - {p['time']}\n💬 {p['content']}")

    def tab_3_contacts(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("<b>Aba 3: Contactos</b> — Gestão & Menu de 6 Opções").setStyleSheet("font-size: 15px; font-weight: bold;"))
        self.contacts_list = QListWidget()
        self.contacts_list.addItem("Madala (86)")
        self.contacts_list.addItem("Helena (Mãe)")
        self.contacts_list.addItem("Albino (Pai)")
        self.contacts_list.itemClicked.connect(self.show_six_options)
        l.addWidget(self.contacts_list)
        return w

    def show_six_options(self, item):
        c_name = item.text()
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Menu de 6 Opções: {c_name}")
        dlg.setFixedSize(380, 320)
        lay = QVBoxLayout(dlg)
        options = [
            "1. Ver Perfil do Contacto", "2. Mandar Mensagem", "3. Ligar",
            "4. Ocultar Contacto", "5. Bloquear Contacto Definitivamente", "6. Denunciar ao COMUNIC"
        ]
        for opt in options:
            btn = QPushButton(opt)
            btn.clicked.connect(lambda checked, o=opt, c=c_name: (dlg.close(), QMessageBox.information(self, "Ação", f"Executando '{o}' para {c}")))
            lay.addWidget(btn)
        dlg.exec()

    def tab_4_lives(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("<b>Aba 4: Lives</b> — Transmissões em Direto (Canais Nacionais A & Globais B)").setStyleSheet("font-size: 15px; font-weight: bold;"))
        
        self.list_lives = QListWidget()
        lives_opts = [
            "1. Comunicado do Estado -> A: Nacional",
            "1. Comunicado do Estado -> B: Global",
            "2. Última Hora -> A: Nacional",
            "2. Última Hora -> B: Global"
        ]
        for item in lives_opts:
            self.list_lives.addItem(f"🔴 {item} [Em Direto]")
            
        self.list_lives.itemDoubleClicked.connect(self.abrir_live_com_ficheiro)
        l.addWidget(self.list_lives)
        
        lbl_hint = QLabel("💡 Dica: Dê duplo clique numa live para escolher ficheiros (Áudio, Vídeo, Fotos, Word) e transmiti-los em direto.")
        lbl_hint.setStyleSheet("color: #8696a0; font-size: 11px;")
        l.addWidget(lbl_hint)
        return w

    def abrir_live_com_ficheiro(self, item):
        live_name = item.text().split(' [')[0]
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Ficheiro para Transmissão", "", "Multimédia e Documentos (*.mp4 *.mp3 *.png *.jpg *.docx *.pdf);;Todos os Ficheiros (*.*)")
        LivePlayerWindow(live_name, file_path, self.user_language, self).exec()

    def tab_5_entertainment(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("<b>Aba 5: Entretenimento</b> — Estreias Nacionais (A) & Globais (B)").setStyleSheet("font-size: 15px; font-weight: bold;"))
        
        self.list_ent = QListWidget()
        ent_opts = [
            "1. Estreia / Música -> A: Nacional",
            "1. Estreia / Música -> B: Global",
            "2. Comédia -> A: Nacional",
            "2. Comédia -> B: Global"
        ]
        for item in ent_opts:
            self.list_ent.addItem(f"🎬 {item}")
            
        self.list_ent.itemDoubleClicked.connect(self.abrir_entretenimento_com_ficheiro)
        l.addWidget(self.list_ent)
        
        lbl_hint = QLabel("💡 Dica: Dê duplo clique para escolher ficheiros (Áudio, Vídeo, Fotos, Word) para transmissão ou partilha.")
        lbl_hint.setStyleSheet("color: #8696a0; font-size: 11px;")
        l.addWidget(lbl_hint)
        return w

    def abrir_entretenimento_com_ficheiro(self, item):
        ent_name = item.text()
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Ficheiro para Entretenimento", "", "Multimédia e Documentos (*.mp4 *.mp3 *.png *.jpg *.docx *.pdf);;Todos os Ficheiros (*.*)")
        msg = f"A transmitir/partilhar conteúdo de: {ent_name}"
        if file_path:
            msg += f"\nFicheiro: {os.path.basename(file_path)}"
        QMessageBox.information(self, "Entretenimento Direto", msg)

    def tab_6_free_chat(self):
        w = QWidget()
        l = QVBoxLayout(w)
        
        top_fc = QHBoxLayout()
        top_fc.addWidget(QLabel(f"<b>Aba 6: Bate-papo Livre</b> — Sala: {self.user_country}").setStyleSheet("font-size: 15px; font-weight: bold;"))
        top_fc.addStretch()
        btn_new_fc = QPushButton("💬 Iniciar Nova Conversa")
        btn_new_fc.clicked.connect(self.iniciar_nova_conversa_livre)
        top_fc.addWidget(btn_new_fc)
        l.addLayout(top_fc)

        self.free_chat_list = QListWidget()
        for msg in GLOBAL_FREE_CHAT_MESSAGES:
            self.free_chat_list.addItem(f"👤 {msg['author']}: {msg['content']}")
        l.addWidget(self.free_chat_list)
        return w

    def iniciar_nova_conversa_livre(self):
        dlg = NewConversationDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            nome = dlg.inp_name.text().strip()
            if nome:
                GLOBAL_FREE_CHAT_MESSAGES.append({"author": nome, "country": self.user_country, "time": datetime.now().strftime("%Y-%m-%d %H:%M"), "content": "Nova conversa livre iniciada."})
                self.free_chat_list.addItem(f"👤 {nome}: Nova conversa livre iniciada.")
                QMessageBox.information(self, "Sucesso", f"Nova conversa com {nome} iniciada no Bate-papo Livre!")

    def tab_7_profile(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("<b>Aba 7: Perfil do Utilizador & Identidade</b>").setStyleSheet("font-size: 15px; font-weight: bold; color: #00a884;"))
        
        form = QFormLayout()
        self.lbl_acc_num = QLabel(f"<b>{self.phone}</b>")
        self.inp_prof_name = QLineEdit(self.username)
        self.inp_prof_state = QLineEdit(self.state)
        self.inp_prof_nat = QLineEdit(self.nationality)
        
        form.addRow("Número da Conta:", self.lbl_acc_num)
        form.addRow("Nome do Usuário:", self.inp_prof_name)
        form.addRow("Estado / Província:", self.inp_prof_state)
        form.addRow("Nacionalidade:", self.inp_prof_nat)
        l.addLayout(form)

        self.lbl_avatar_status = QLabel(f"🖼️ Avatar Atual: {self.avatar_path if self.avatar_path else 'Padrão'}")
        l.addWidget(self.lbl_avatar_status)

        hbox_foto = QHBoxLayout()
        btn_cam_foto = QPushButton("📷 Capturar com a Câmara")
        btn_cam_foto.clicked.connect(self.capturar_foto_camara)
        hbox_foto.addWidget(btn_cam_foto)

        btn_galeria = QPushButton("📁 Escolher na Galeria")
        btn_galeria.clicked.connect(self.escolher_foto_galeria)
        hbox_foto.addWidget(btn_galeria)
        l.addLayout(hbox_foto)

        btn_save_prof = QPushButton("💾 Guardar Alterações do Perfil")
        btn_save_prof.setProperty("class", "ActionBtn")
        btn_save_prof.clicked.connect(self.guardar_perfil)
        l.addWidget(btn_save_prof)
        l.addStretch()
        return w

    def capturar_foto_camara(self):
        cam = CameraFilterDialog(mode="photo", parent=self)
        if cam.exec():
            self.avatar_path = "Foto_Camera_AR.png"
            self.lbl_avatar_status.setText(f"🖼️ Avatar Atual: {self.avatar_path}")
            QMessageBox.information(self, "Sucesso", "Foto de perfil capturada com sucesso!")

    def escolher_foto_galeria(self):
        path, _ = QFileDialog.getOpenFileName(self, "Escolher Imagem", "", "Imagens (*.png *.jpg *.jpeg)")
        if path:
            self.avatar_path = path
            self.lbl_avatar_status.setText(f"🖼️ Avatar Atual: {os.path.basename(path)}")

    def guardar_perfil(self):
        self.username = self.inp_prof_name.text().strip()
        self.state = self.inp_prof_state.text().strip()
        self.nationality = self.inp_prof_nat.text().strip()
        self.db.update_user_profile(self.phone, self.username, self.state, self.nationality, self.avatar_path)
        QMessageBox.information(self, "Perfil Guardado", "Os dados do seu perfil foram atualizados com sucesso na base de dados!")
    def tab_8_settings(self):
        w = QWidget()
        l = QVBoxLayout(w)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        lay_content = QVBoxLayout(content)
        
        lay_content.addWidget(QLabel("<b>Aba 8: Definições & Segurança da Conta</b>").setStyleSheet("font-size: 15px; font-weight: bold; color: #00a884;"))
        
        form = QFormLayout()
        
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(LISTA_IDIOMAS_MUNDIAIS)
        form.addRow("Mudar Idioma:", self.combo_lang)

        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["Comunic Escuro (Tatico) ", "Cyberpunk Neon"])
        self.combo_theme.currentTextChanged.connect(self.alternar_tema_visual)
        form.addRow("Tema Visual:", self.combo_theme)

        self.inp_new_phone = QLineEdit(self.phone)
        form.addRow("Alterar Número da Conta:", self.inp_new_phone)

        self.inp_new_pwd = QLineEdit()
        self.inp_new_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_new_pwd.setPlaceholderText("Nova senha de acesso...")
        form.addRow("Alterar Senha de Acesso:", self.inp_new_pwd)

        lay_content.addLayout(form)

        self.chk_lock_profile = QCheckBox("🔒 Trancar Perfil / App com Palavra-passe de Privacidade")
        lay_content.addWidget(self.chk_lock_profile)

        btn_apply_settings = QPushButton("💾 Guardar Definições Gerais")
        btn_apply_settings.clicked.connect(self.guardar_definicoes_gerais)
        lay_content.addWidget(btn_apply_settings)

        lay_content.addWidget(QLabel("────────────────────────────────────────"))
        lay_content.addWidget(QLabel("🚨 <b>Configurar Contactos de SOS (Sem Limitação)</b>").setStyleSheet("font-weight: bold;"))
        
        self.sos_list_widget = QListWidget()
        for contact in self.sos_contacts_list:
            self.sos_list_widget.addItem(contact)
        lay_content.addWidget(self.sos_list_widget)

        hbox_sos = QHBoxLayout()
        self.inp_new_sos = QLineEdit()
        self.inp_new_sos.setPlaceholderText("Nome e número do novo contacto SOS...")
        btn_add_sos = QPushButton("➕ Adicionar Contacto SOS")
        btn_add_sos.clicked.connect(lambda: (self.sos_contacts_list.append(self.inp_new_sos.text().strip()), self.sos_list_widget.addItem(self.inp_new_sos.text().strip()), self.inp_new_sos.clear()))
        hbox_sos.addWidget(self.inp_new_sos)
        hbox_sos.addWidget(btn_add_sos)
        lay_content.addLayout(hbox_sos)

        lay_content.addWidget(QLabel("────────────────────────────────────────"))
        
        btn_remove_acc = QPushButton("🗑️ Remover / Apagar Conta Permanentemente")
        btn_remove_acc.setStyleSheet("background-color: #D32F2F; color: white;")
        btn_remove_acc.clicked.connect(self.remover_conta_definitivamente)
        lay_content.addWidget(btn_remove_acc)

        scroll.setWidget(content)
        l.addWidget(scroll)
        return w

    def guardar_definicoes_gerais(self):
        novo_tel = self.inp_new_phone.text().strip()
        nova_senha = self.inp_new_pwd.text().strip()
        if novo_tel and nova_senha:
            sucesso = self.db.update_user_password_and_phone(self.phone, novo_tel, nova_senha)
            if sucesso:
                self.phone = novo_tel
                QMessageBox.information(self, "Sucesso", "Número da conta e senha atualizados com sucesso!")
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível atualizar (número já em uso?).")

    def remover_conta_definitivamente(self):
        resp = QMessageBox.question(self, "Aviso Crítico", "Tem certeza absoluta que deseja apagar a sua conta permanentemente?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if resp == QMessageBox.StandardButton.Yes:
            self.db.delete_user_account(self.phone)
            QMessageBox.critical(self, "Conta Removida", "A conta foi eliminada. A aplicação será encerrada.")
            sys.exit(0)

    def alternar_tema_visual(self, tema):
        if "Cyberpunk" in tema:
            self.setStyleSheet(CYBERPUNK_NEON_STYLE)
            QMessageBox.information(self, "Tema", "Cyberpunk Neon aplicado!")
        else:
            self.setStyleSheet("Comunic Escuro (Tatico)")
            QMessageBox.information(self, "Tema", "Comunic Escuro (Tatico) aplicado!")

    def tab_9_admin(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("<b>Aba 9: Painel do Administrador</b> — Controlo Soberano").setStyleSheet("font-size: 15px; font-weight: bold; color: #ff5252;"))
        
        btn_open_admin = QPushButton("🛠️ Aceder ao Painel de Administrador (Autenticação Obrigatória)")
        btn_open_admin.setStyleSheet("background-color: #D32F2F; color: white; font-weight: bold; padding: 14px;")
        btn_open_admin.clicked.connect(self.autenticar_e_abrir_admin)
        l.addWidget(btn_open_admin)
        l.addStretch()
        return w

    def autenticar_e_abrir_admin(self):
        aviso = QMessageBox.warning(
            self, 
            "⚠️ ALERTA DE SEGURANÇA MÁXIMA", 
            "ATENÇÃO: Está prestes a aceder à Consola de Administração do COMUNIC.\n\n"
            "Qualquer tentativa não autorizada recolhe dados biométricos, fotografias em segundo plano e localização GPS.\n"
            "Utilizadores não autorizados serão banidos permanentemente sem direito a apelação.\n\n"
            "Deseja prosseguir?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if aviso != QMessageBox.StandardButton.Yes:
            return

        dlg = QDialog(self)
        dlg.setWindowTitle("Autenticação Dupla de Administrador")
        dlg.setFixedSize(420, 300)
        dlg.setStyleSheet("background-color: #111b21; color: #e9edef;")
        lay = QVBoxLayout(dlg)

        lay.addWidget(QLabel("🔒 Palavra-passe de Administrador:"))
        inp_pwd = QLineEdit()
        inp_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        lay.addWidget(inp_pwd)

        lay.addWidget(QLabel("❓ Pergunta Secreta: Qual é a cor favorita do administrador?"))
        inp_ans = QLineEdit()
        lay.addWidget(inp_ans)

        btn_conf = QPushButton("Desbloquear Painel")
        
        def verificar():
            senha_hash = hashlib.sha256(inp_pwd.text().encode('utf-8')).hexdigest()
            resp = inp_ans.text().strip().lower()
            
            gps_simulado = "Lat: -25.9692, Lon: 32.5732 (Maputo)"
            fotos_simuladas = "[Snapshot_01_Admin.jpg, Snapshot_02_Admin_5s.jpg]"
            
            if senha_hash == ADMIN_PASSWORD_HASH and resp == "cor":
                GLOBAL_SECURITY_LOGS.insert(0, {
                    "user": self.username,
                    "phone": self.phone,
                    "country": self.user_country,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "Sucesso (Acedido)",
                    "gps": gps_simulado,
                    "photos": fotos_simuladas
                })
                dlg.accept()
                AdminDashboardFullDialog(self).exec()
            else:
                GLOBAL_SECURITY_LOGS.insert(0, {
                    "user": self.username,
                    "phone": self.phone,
                    "country": self.user_country,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "Falhou (Credenciais Incorretas)",
                    "gps": gps_simulado,
                    "photos": fotos_simuladas
                })
                QMessageBox.critical(dlg, "Acesso Negado", "Credenciais ou resposta secreta incorretas! Tentativa registada e fotografada.")
                dlg.reject()

        btn_conf.clicked.connect(verificar)
        lay.addWidget(btn_conf)
        dlg.exec()

    def tab_10_find_friend(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("<b>Aba 10: Find My Friend</b> — Localização Ponto a Ponto").setStyleSheet("font-size: 15px; font-weight: bold;"))
        btn = QPushButton("🗺️ Configurar Conexão GPS com Amigo")
        btn.clicked.connect(lambda: FindMyFriendDialog(self).exec())
        l.addWidget(btn)
        l.addStretch()
        return w

    def tab_11_guide(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("<b>Aba 11: Guia Oficial</b>").setStyleSheet("font-size: 15px; font-weight: bold;"))
        guide_box = QTextEdit()
        guide_box.setReadOnly(True)
        guide_box.setHtml("<h3>Manual COMUNIC</h3><p>Ecossistema global soberano com suporte a IA e segurança avançada.</p>")
        l.addWidget(guide_box)
        return w

    def tab_12_contact_us(self):
        w = QWidget()
        l = QVBoxLayout(w)
        banner = QLabel("Modo teste activo por 7 dias. Após 7 dias, efetue o pagamento único de 50mt via M-Pesa (842495357 - António Bila).")
        banner.setStyleSheet("background-color: #334155; color: #F8FAFC; padding: 12px; font-weight: bold; border-radius: 6px;")
        l.addWidget(banner)
        
        btn = QPushButton("✉️ Enviar Mensagem ao Desenvolvedor")
        btn.clicked.connect(lambda: ContactDevDialog(self.username, self.user_country, self).exec())
        l.addWidget(btn)
        return w

    def stack_13_sos(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("<b>Aba 13: SOS & Segurança com Temporizador</b>").setStyleSheet("font-size: 15px; font-weight: bold; color: #EF4444;"))
        
        self.lbl_sos_timer = QLabel("⏱️ Ciclo SOS Ativo: Próxima verificação em 10 minutos.")
        self.lbl_sos_timer.setStyleSheet("background-color: #202c33; color: #00a884; padding: 10px; border-radius: 6px;")
        l.addWidget(self.lbl_sos_timer)

        sos_btn = QPushButton("🚨 DISPARAR SOS DE EMERGÊNCIA IMEDIATO")
        sos_btn.setStyleSheet("background-color: #D32F2F; color: white; font-weight: bold; padding: 15px;")
        sos_btn.clicked.connect(lambda: SOSDialog(self.sos_contacts_list, self).exec())
        l.addWidget(sos_btn)

        fake_btn = QPushButton("🕶️ Ativar Modo Encerramento Falso (Fake Shutdown)")
        fake_btn.clicked.connect(EmergencySOSController.trigger_fake_shutdown)
        l.addWidget(fake_btn)
        l.addStretch()
        return w

    def disparar_aviso_sos_10min(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("⚠️ Verificação de Segurança SOS (10 Minutos)")
        dlg.setFixedSize(400, 220)
        dlg.setStyleSheet("background-color: #2C0B0E; color: #FFFFFF;")
        
        lay = QVBoxLayout(dlg)
        lay.addWidget(QLabel("🚨 O ciclo de 10 minutos terminou!\nInsira a sua senha para cancelar o envio automático do SOS:"))
        
        inp = QLineEdit()
        inp.setEchoMode(QLineEdit.EchoMode.Password)
        lay.addWidget(inp)
        
        btn_cancel_sos = QPushButton("Cancelar SOS (Estou Seguro)")
        btn_cancel_sos.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        
        def verificar_senha_sos():
            if inp.text().strip() == "Bila2026":
                QMessageBox.information(dlg, "Seguro", "SOS cancelado com sucesso para este ciclo.")
                dlg.accept()
            else:
                QMessageBox.warning(dlg, "Incorreto", "Senha incorreta! A enviar SOS para os contactos...")
                SOSDialog(self.sos_contacts_list, self).exec()
                dlg.accept()

        btn_cancel_sos.clicked.connect(verificar_senha_sos)
        lay.addWidget(btn_cancel_sos)
        dlg.exec()

    def tab_14_camera(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("<b>Aba 14: Câmera & Estúdio AR</b>").setStyleSheet("font-size: 15px; font-weight: bold;"))
        btn_cam = QPushButton("📷 Abrir Estúdio Completo de Multi-Filtros")
        btn_cam.clicked.connect(lambda: CameraFilterDialog(mode="photo", parent=self).exec())
        l.addWidget(btn_cam)
        return w


# ==============================================================================
# 4. PAINEL DE ADMINISTRAÇÃO COMPLETO
# ==============================================================================

class AdminDashboardFullDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🛠️ Consola de Administração Soberana — COMUNIC")
        self.setFixedSize(760, 780)
        self.setStyleSheet("background-color: #111b21; color: #e9edef; font-family: 'Segoe UI', Arial;")
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("🔒 Painel Restrito de Administração").setStyleSheet("font-size: 16px; font-weight: bold; color: #ff5252;"))
        
        tabs = QTabWidget()
        
        t1 = QWidget()
        l1 = QVBoxLayout(t1)
        self.list_fb = QListWidget()
        for fb in GLOBAL_FEEDBACK_LIST:
            self.list_fb.addItem(f"👤 {fb.get('user','User')} ({fb.get('country','Moçambique')}): {fb.get('msg','')}")
        l1.addWidget(self.list_fb)
        tabs.addTab(t1, "1. Fale Connosco")

        t2 = QWidget()
        l2 = QVBoxLayout(t2)
        l2.addWidget(QLabel("🛡️ Relatório de Tentativas de Acesso ao Painel Admin (Com Fotos & GPS):"))
        self.list_sec = QListWidget()
        for log in GLOBAL_SECURITY_LOGS:
            self.list_sec.addItem(
                f"👤 Utilizador: {log['user']} | Tel: {log['phone']} | País: {log['country']}\n"
                f"🕒 Hora: {log['time']} | Status: {log['status']}\n"
                f"📍 GPS: {log['gps']} | 📸 Fotos: {log['photos']}\n"
                f"──────────────────────────────────────────────────"
            )
        l2.addWidget(self.list_sec)
        tabs.addTab(t2, "2. Segurança")

        t3 = QWidget()
        l3 = QVBoxLayout(t3)
        l3.addWidget(QLabel("🚫 Gestão de Contas Bloqueadas / Lista Negra:"))
        self.list_bl = QListWidget()
        for u in GLOBAL_BLACKLISTED_USERS:
            self.list_bl.addItem(f"🚫 Utilizador Banido: {u}")
        l3.addWidget(self.list_bl)
        
        hbox_bl = QHBoxLayout()
        self.inp_ban_user = QLineEdit()
        self.inp_ban_user.setPlaceholderText("Nome ou telemóvel para banir...")
        btn_add_bl = QPushButton("Banir Definitivamente")
        btn_add_bl.setStyleSheet("background-color: #D32F2F; color: white;")
        btn_add_bl.clicked.connect(lambda: (GLOBAL_BLACKLISTED_USERS.append(self.inp_ban_user.text().strip()), self.list_bl.addItem(f"🚫 Utilizador Banido: {self.inp_ban_user.text().strip()}"), guardar_ficheiro(BLACKLIST_FILE, GLOBAL_BLACKLISTED_USERS)))
        hbox_bl.addWidget(self.inp_ban_user)
        hbox_bl.addWidget(btn_add_bl)
        l3.addLayout(hbox_bl)
        tabs.addTab(t3, "3. Lista Negra")

        t4 = QWidget()
        l4 = QVBoxLayout(t4)
        
        l4.addWidget(QLabel("⚡ Interruptor Global (Kill Switch / Ligar & Desligar Comunic):"))
        hbox_kill = QHBoxLayout()
        self.inp_kill_pwd = QLineEdit()
        self.inp_kill_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_kill_pwd.setPlaceholderText("Senha de controlo...")
        btn_kill = QPushButton("⚠️ Desligar / Suspender Comunic")
        btn_kill.setStyleSheet("background-color: #D32F2F; color: white;")
        btn_kill.clicked.connect(self.desligar_comunic_sistema)
        hbox_kill.addWidget(self.inp_kill_pwd)
        hbox_kill.addWidget(btn_kill)
        l4.addLayout(hbox_kill)

        l4.addWidget(QLabel("────────────────────────────────────────"))
        l4.addWidget(QLabel("👤 Gerar Conta e Senha para Novo Usuário:"))
        form_gen = QFormLayout()
        self.gen_phone = QLineEdit("+258 840000000")
        self.gen_name = QLineEdit("Novo Utilizador")
        self.gen_pwd = QLineEdit("Senha123")
        form_gen.addRow("Número da Conta:", self.gen_phone)
        form_gen.addRow("Nome do Usuário:", self.gen_name)
        form_gen.addRow("Gerar Senha:", self.gen_pwd)
        l4.addLayout(form_gen)
        
        btn_create_acc = QPushButton("🚀 Criar e Registar Nova Conta")
        btn_create_acc.clicked.connect(self.gerar_conta_admin)
        l4.addLayout(QFormLayout().addRow(btn_create_acc))

        l4.addWidget(QLabel("────────────────────────────────────────"))
        l4.addWidget(QLabel("📢 Enviar Mensagem Global & Adicionar Anúncios:"))
        self.inp_broadcast = QTextEdit()
        self.inp_broadcast.setPlaceholderText("Escreva o anúncio ou aviso oficial para todos...")
        self.inp_broadcast.setMaximumHeight(60)
        l4.addWidget(self.inp_broadcast)
        
        btn_send_bc = QPushButton("🚀 Enviar Broadcast Global")
        btn_send_bc.clicked.connect(self.enviar_broadcast_global)
        l4.addWidget(btn_send_bc)

        tabs.addTab(t4, "4. Controlo")

        layout.addWidget(tabs)
        btn_close = QPushButton("Fechar Painel")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def desligar_comunic_sistema(self):
        if self.inp_kill_pwd.text().strip() == "Bila2026":
            QMessageBox.critical(self, "Sistema Suspenso", "O COMUNIC foi desligado pelo administrador. A aplicação será encerrada.")
            sys.exit(0)
        else:
            QMessageBox.warning(self, "Erro", "Senha de controlo incorreta!")

    def gerar_conta_admin(self):
        p = self.gen_phone.text().strip()
        u = self.gen_name.text().strip()
        pwd = self.gen_pwd.text().strip()
        if p and u and pwd:
            db = ComunicEnterpriseDatabase()
            hw = DeviceSecurityProtocol.get_hardware_telemetry()
            ok, key = db.register_user(p, u, pwd, hw)
            if ok:
                QMessageBox.information(self, "Sucesso", f"Conta criada com sucesso para {u}!\nChave: {key}")
            else:
                QMessageBox.warning(self, "Erro", "Número já registado.")

    def enviar_broadcast_global(self):
        msg = self.inp_broadcast.toPlainText().strip()
        if msg:
            GLOBAL_BROADCAST_MESSAGES.append(msg)
            QMessageBox.information(self, "Broadcast Enviado", "Anúncio enviado com sucesso para todos os utilizadores globais!")
            self.inp_broadcast.clear()


# ==============================================================================
# 5. DIÁLOGO DE AUTENTICAÇÃO E EXECUÇÃO PRINCIPAL
# ==============================================================================

class AuthenticationDialog(QDialog):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.authenticated_phone = None
        self.authenticated_name = None
        
        self.setWindowTitle("COMUNIC - Autenticação & Segurança Avançada")
        self.setFixedSize(500, 460)
        self.setStyleSheet("QDialog { background-color: #111b21; color: #e9edef; } QLabel { color: #e9edef; font-size: 13px; } QLineEdit { background: #2a3942; color: #FFF; border: none; padding: 10px; border-radius: 8px; } QPushButton { background: #00a884; color: #FFF; font-weight: bold; padding: 11px; border-radius: 18px; }")
        self.build_auth_ui()

    def build_auth_ui(self):
        main_lay = QVBoxLayout(self)
        title = QLabel("COMUNIC - Acesso Seguro")
        title.setStyleSheet("color: #00a884; font-size: 22px; font-weight: 800; margin-bottom: 12px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_lay.addWidget(title)

        self.auth_stack = QStackedWidget()

        w0 = QWidget()
        l0 = QVBoxLayout(w0)
        b_login = QPushButton("Entrar na Conta Existente")
        b_login.clicked.connect(lambda: self.auth_stack.setCurrentIndex(1))
        b_reg = QPushButton("Criar Nova Conta")
        b_reg.clicked.connect(lambda: self.auth_stack.setCurrentIndex(2))
        l0.addWidget(b_login)
        l0.addWidget(b_reg)
        self.auth_stack.addWidget(w0)

        w1 = QWidget()
        l1 = QFormLayout(w1)
        self.login_phone = QLineEdit("+258842495357")
        self.login_pwd = QLineEdit("Bila2026")
        self.login_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        l1.addRow("Telemóvel:", self.login_phone)
        l1.addRow("Palavra-passe:", self.login_pwd)

        btn_login = QPushButton("Efetuar Login Seguro")
        btn_login.clicked.connect(self.handle_login)
        l1.addRow(btn_login)

        btn_b1 = QPushButton("Voltar")
        btn_b1.setStyleSheet("background: #202c33; color: #8696a0;")
        btn_b1.clicked.connect(lambda: self.auth_stack.setCurrentIndex(0))
        l1.addRow(btn_b1)
        self.auth_stack.addWidget(w1)

        w2 = QWidget()
        l2 = QFormLayout(w2)
        self.reg_phone = QLineEdit("+258842495357")
        self.reg_name = QLineEdit("Antônio Bila")
        self.reg_pwd = QLineEdit("Bila2026")
        self.reg_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        l2.addRow("Telemóvel:", self.reg_phone)
        l2.addRow("Nome de Utilizador:", self.reg_name)
        l2.addRow("Palavra-passe:", self.reg_pwd)

        btn_reg = QPushButton("Registar & Confirmar OTP")
        btn_reg.clicked.connect(self.handle_register)
        l2.addRow(btn_reg)

        btn_b2 = QPushButton("Voltar")
        btn_b2.setStyleSheet("background: #202c33; color: #8696a0;")
        btn_b2.clicked.connect(lambda: self.auth_stack.setCurrentIndex(0))
        l2.addRow(btn_b2)
        self.auth_stack.addWidget(w2)

        main_lay.addWidget(self.auth_stack)

    def handle_register(self):
        p = self.reg_phone.text().strip()
        u = self.reg_name.text().strip()
        pwd = self.reg_pwd.text().strip()
        if not p or not u or not pwd:
            QMessageBox.warning(self, "Aviso", "Preencha todos os campos.")
            return

        hw = DeviceSecurityProtocol.get_hardware_telemetry()
        success, rec_key = self.db.register_user(p, u, pwd, hw)
        if success:
            QMessageBox.information(self, "Sucesso", f"Conta criada com sucesso!\nChave de Recuperação: {rec_key}")
            self.authenticated_phone = p
            self.authenticated_name = u
            self.auth_stack.setCurrentIndex(1)
        else:
            QMessageBox.critical(self, "Erro", "Este número já se encontra registado.")

    def handle_login(self):
        p = self.login_phone.text().strip()
        pwd = self.login_pwd.text().strip()
        record = self.db.get_user(p)
        if not record:
            hw = DeviceSecurityProtocol.get_hardware_telemetry()
            self.db.register_user(p, "Antônio Bila", pwd, hw)
            record = self.db.get_user(p)

        if record and record[5] == 1:
            QMessageBox.critical(self, "Bloqueado", "Conta bloqueada por excesso de tentativas.")
            return
        if record and record[6] != pwd:
            self.db.update_failed_login(p, reset=False)
            QMessageBox.warning(self, "Erro", "Palavra-passe incorreta.")
            return

        self.db.update_failed_login(p, reset=True)
        self.authenticated_phone = p
        self.authenticated_name = record[4] if record else "Antônio Bila"
        
        trial_date_str = record[8] if record else None
        is_paid = record[9] if record else 0
        if trial_date_str and not is_paid:
            try:
                trial_date = datetime.strptime(trial_date_str, "%Y-%m-%d %H:%M:%S")
                if (datetime.now() - trial_date).days >= 7:
                    lock = PaymentLockDialog(self.authenticated_name, self)
                    if lock.exec() != QDialog.DialogCode.Accepted:
                        sys.exit(0)
            except Exception:
                pass

        self.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    db_core = ComunicEnterpriseDatabase()

    auth_dlg = AuthenticationDialog(db_core)
    if auth_dlg.exec() == QDialog.DialogCode.Accepted:
        phone = auth_dlg.authenticated_phone or "+258842495357"
        name = auth_dlg.authenticated_name or "Antônio Bila"
        
        window = ComunicIndustrialWorkspace(db_core, phone, name)
        window.show()
        sys.exit(app.exec())