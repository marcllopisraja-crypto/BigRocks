
import base64
import hashlib
init_db()

import os

st.write("PATH BD:", os.path.abspath(DB_PATH))
st.write("EXISTEIX:", os.path.exists(DB_PATH))

try:

	usuaris = fetch_query("SELECT username FROM usuaris")
	st.write("USUARIS:", usuaris)
except Exception as e:
	st.write("ERROR:", e)
import sqlite3
from datetime import datetime

import pandas as pd
import streamlit as st

# ============================================================
# BIG ROCKS - SORIGUE
# APP.py complet - versio responsive i corregida per mobile
# ============================================================

DB_PATH = "bigrocks.db"
PRIMARY = "#009CDE"
PRIMARY_DARK = "#216D8C"
PRIMARY_HOVER = "#43B8ED"
TEXT = "#232323"
GREY = "#53565A"
BORDER = "#BBBBBB"
SUCCESS = "#03A446"
WARNING = "#CE9F00"
ERROR = "#E53A4F"
LIGHT_BLUE = "#E7F2F7"

LOGO_NEGATIVE_CANDIDATES = [
    "sorigue_logo_RGB-negativo.png",
    "sorigue_logo_negativo.png",
    "sorigue_logo_blanc.png",
    "sorigue_blanc.png",
]
LOGO_POSITIVE_CANDIDATES = [
    "sorigue_logo_RGB-positivo.png",
    "sorigue_logo.png",
]

st.set_page_config(
    page_title="Big Rocks - Sorigué",
    layout="wide",
    page_icon="🪨",
    initial_sidebar_state="expanded",
)

# ============================================================
# 1. TRADUCCIONS
# ============================================================

TRANS = {
    "ca": {
        "login_title": "Accés a la Plataforma",
        "login_subtitle": "Seguiment mensual dels teus Big Rocks i TARs",
        "login_tab": "Iniciar sessió",
        "reg_tab": "Registrar nou usuari",
        "usr": "Nom d'usuari",
        "pwd": "Contrasenya",
        "new_usr": "Nou nom d'usuari",
        "lang_reg": "Idioma per defecte",
        "enter": "Entrar",
        "register": "Registrar",
        "err_login": "Usuari o contrasenya incorrectes.",
        "succ_reg": "Usuari creat correctament. Ara pots iniciar sessió.",
        "err_reg": "Aquest nom d'usuari ja existeix.",
        "required_fields": "Introdueix usuari i contrasenya per continuar.",
        "conn_as": "Connectat com:",
        "lang": "Idioma",
        "nav_months": "Navegar pels mesos",
        "closed_month": "Aquest mes està tancat.",
        "unlock": "Desbloquejar mes",
        "open_month": "Mes obert i editable",
        "logout": "Tancar sessió",
        "eval_close": "Avaluar i tancar mes",
        "no_br_title": "Encara no tens cap Big Rock creada",
        "no_br_body": "Crea la primera Big Rock per començar el seguiment mensual.",
        "key_ppl": "Persones clau",
        "key_meet": "Reunions",
        "global_prog": "Assoliment global",
        "state": "Estat",
        "desc": "Descripció de la tasca",
        "details": "Detalls, preguntes i pròxims passos",
        "prog": "Progrés",
        "need": "Pregunta o necessitat",
        "next_steps": "Pròxims passos",
        "save_notes": "Guardar notes",
        "create_br": "Crear nova Big Rock",
        "config_br": "Configura la teva nova Big Rock",
        "title_br": "Títol de la Big Rock",
        "save": "Guardar Big Rock",
        "summary": "Resum de tancament",
        "global_comp": "Grau de compliment global",
        "successes": "Èxits completats",
        "carry_over": "Es traspassen",
        "cancel": "Cancel·lar i tornar",
        "confirm_close": "Confirmar tancament i crear mes següent",
        "active_brs": "Big Rocks actives",
        "completed_tars": "TARs completats",
        "pending_tars": "TARs pendents",
        "avg_progress": "Progrés mitjà",
        "export_csv": "Exportar CSV",
        "archive": "Arxivar",
        "delete_help": "Arxivar aquesta TAR",
        "people_placeholder": "Ex. Xavier, Gerard, equip nord...",
        "meetings_placeholder": "Ex. Seguiment setmanal, comitè mensual...",
        "title_placeholder": "Ex. Reduir incidències crítiques de l'obra",
        "tar_placeholder": "Descriu una acció concreta i mesurable",
        "saved": "Canvis guardats correctament.",
        "status_open": "Obert",
        "status_closed": "Tancat",
        "help_title": "Consell d'usabilitat",
        "help_body": "Mantingues les Big Rocks concretes: objectiu clar, persones clau i 3-4 TARs mesurables.",
        "empty_cta": "Crea la primera Big Rock",
        "month_status": "Estat del mes",
        "brand_subtitle": "Seguiment d'objectius",
        "months": ["Gener", "Febrer", "Març", "Abril", "Maig", "Juny", "Juliol", "Agost", "Setembre", "Octubre", "Novembre", "Desembre"],
    },
    "es": {
        "login_title": "Acceso a la Plataforma",
        "login_subtitle": "Seguimiento mensual de tus Big Rocks y TARs",
        "login_tab": "Iniciar sesión",
        "reg_tab": "Registrar nuevo usuario",
        "usr": "Nombre de usuario",
        "pwd": "Contraseña",
        "new_usr": "Nuevo nombre de usuario",
        "lang_reg": "Idioma por defecto",
        "enter": "Entrar",
        "register": "Registrar",
        "err_login": "Usuario o contraseña incorrectos.",
        "succ_reg": "Usuario creado correctamente. Ahora puedes iniciar sesión.",
        "err_reg": "Este nombre de usuario ya existe.",
        "required_fields": "Introduce usuario y contraseña para continuar.",
        "conn_as": "Conectado como:",
        "lang": "Idioma",
        "nav_months": "Navegar por los meses",
        "closed_month": "Este mes está cerrado.",
        "unlock": "Desbloquear mes",
        "open_month": "Mes abierto y editable",
        "logout": "Cerrar sesión",
        "eval_close": "Evaluar y cerrar mes",
        "no_br_title": "Aún no tienes ninguna Big Rock creada",
        "no_br_body": "Crea la primera Big Rock para empezar el seguimiento mensual.",
        "key_ppl": "Personas clave",
        "key_meet": "Reuniones",
        "global_prog": "Avance global",
        "state": "Estado",
        "desc": "Descripción de la tarea",
        "details": "Detalles, preguntas y próximos pasos",
        "prog": "Progreso",
        "need": "Pregunta o necesidad",
        "next_steps": "Próximos pasos",
        "save_notes": "Guardar notas",
        "create_br": "Crear nueva Big Rock",
        "config_br": "Configura tu nueva Big Rock",
        "title_br": "Título de la Big Rock",
        "save": "Guardar Big Rock",
        "summary": "Resumen de cierre",
        "global_comp": "Grado de cumplimiento global",
        "successes": "Éxitos completados",
        "carry_over": "Se traspasan",
        "cancel": "Cancelar y volver",
        "confirm_close": "Confirmar cierre y crear mes siguiente",
        "active_brs": "Big Rocks activas",
        "completed_tars": "TARs completados",
        "pending_tars": "TARs pendientes",
        "avg_progress": "Progreso medio",
        "export_csv": "Exportar CSV",
        "archive": "Archivar",
        "delete_help": "Archivar esta TAR",
        "people_placeholder": "Ej. Xavier, Gerard, equipo norte...",
        "meetings_placeholder": "Ej. Seguimiento semanal, comité mensual...",
        "title_placeholder": "Ej. Reducir incidencias críticas de la obra",
        "tar_placeholder": "Describe una acción concreta y medible",
        "saved": "Cambios guardados correctamente.",
        "status_open": "Abierto",
        "status_closed": "Cerrado",
        "help_title": "Consejo de usabilidad",
        "help_body": "Mantén las Big Rocks concretas: objetivo claro, personas clave y 3-4 TARs medibles.",
        "empty_cta": "Crea la primera Big Rock",
        "month_status": "Estado del mes",
        "brand_subtitle": "Seguimiento de objetivos",
        "months": ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
    },
}


def t(key):
    lang = st.session_state.get("idioma", "ca")
    return TRANS.get(lang, TRANS["ca"]).get(key, key)

# ============================================================
# 2. CSS CORPORATIU I CORRECCIONS MOBILE
# ============================================================

def inject_css():
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');

:root {{
    --s-primary: {PRIMARY};
    --s-primary-dark: {PRIMARY_DARK};
    --s-primary-hover: {PRIMARY_HOVER};
    --s-text: {TEXT};
    --s-grey: {GREY};
    --s-border: {BORDER};
    --s-success: {SUCCESS};
    --s-warning: {WARNING};
    --s-error: {ERROR};
    --s-light-blue: {LIGHT_BLUE};
}}

/* Important: no forcem la font als icons interns de Streamlit, per evitar textos tipus keyboard_double_arrow_right */
html, body, input, textarea, button, select {{
    font-family: 'Montserrat', Arial, sans-serif !important;
}}

p, label, h1, h2, h3, h4, h5, h6,
[data-testid="stMarkdownContainer"],
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-baseweb="select"] div,
[data-baseweb="select"] span {{
    font-family: 'Montserrat', Arial, sans-serif !important;
}}

.material-symbols-rounded,
.material-symbols-outlined,
.material-icons,
[data-testid="collapsedControl"] span,
[data-testid="stExpanderToggleIcon"] span {{
    font-family: 'Material Symbols Rounded', 'Material Icons' !important;
    font-weight: normal !important;
    font-style: normal !important;
    line-height: 1 !important;
    letter-spacing: normal !important;
    text-transform: none !important;
    display: inline-block !important;
    white-space: nowrap !important;
    word-wrap: normal !important;
    direction: ltr !important;
    -webkit-font-feature-settings: 'liga' !important;
    -webkit-font-smoothing: antialiased !important;
}}

.block-container {{
    padding-top: 1.8rem;
    padding-bottom: 3rem;
    max-width: 1360px;
}}

h1 {{
    font-size: 42px !important;
    line-height: 50px !important;
    font-weight: 700 !important;
    color: var(--s-text) !important;
}}

h2 {{
    font-size: 28px !important;
    line-height: 34px !important;
    font-weight: 700 !important;
    color: var(--s-text) !important;
}}

h3 {{
    font-size: 20px !important;
    line-height: 28px !important;
    font-weight: 600 !important;
    color: var(--s-text) !important;
}}

/* Amaguem elements de Streamlit Cloud que embruten la vista en mobile */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
[data-testid="stToolbar"] {{display: none !important;}}
[data-testid="stDecoration"] {{display: none !important;}}
[data-testid="stStatusWidget"] {{display: none !important;}}

/* Sidebar */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, var(--s-primary) 0%, #08A7E8 100%) !important;
}}

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] .sidebar-white {{
    color: #FFFFFF !important;
}}

[data-testid="stSidebar"] label {{
    font-weight: 700 !important;
}}

.sidebar-logo-text {{
    color: #FFFFFF;
    font-size: 48px;
    font-weight: 700;
    line-height: 1;
    text-align: center;
    margin: 20px 0 8px 0;
    letter-spacing: -1.5px;
}}

.sidebar-app-title {{
    color: #FFFFFF;
    font-size: 18px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 4px;
}}

.sidebar-app-subtitle {{
    color: rgba(255,255,255,.86);
    font-size: 13px;
    text-align: center;
    margin-bottom: 22px;
}}

.sidebar-status-card {{
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.38);
    border-radius: 8px;
    padding: 14px 16px;
    margin: 14px 0 18px 0;
}}

.sidebar-pill {{
    display: inline-flex;
    align-items: center;
    border-radius: 999px;
    padding: 7px 13px;
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.35);
    color: #FFFFFF;
    font-size: 13px;
    font-weight: 700;
}}

/* Selectbox: fons blanc, text fosc, fletxa visible. Especialment dins sidebar. */
[data-baseweb="select"] > div {{
    background: #FFFFFF !important;
    border: 1px solid var(--s-border) !important;
    border-radius: 4px !important;
    min-height: 40px !important;
    box-shadow: none !important;
}}

[data-baseweb="select"] > div:hover {{
    border-color: #359ECE !important;
}}

[data-baseweb="select"] svg {{
    fill: var(--s-grey) !important;
    color: var(--s-grey) !important;
    opacity: 1 !important;
    width: 18px !important;
    height: 18px !important;
}}

[data-baseweb="select"] span,
[data-baseweb="select"] div,
[data-testid="stSidebar"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-baseweb="select"] div {{
    color: var(--s-text) !important;
}}

[data-testid="stSidebar"] [data-baseweb="select"] input {{
    color: var(--s-text) !important;
}}

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {{
    border-radius: 4px !important;
    border: 1px solid var(--s-border) !important;
    color: var(--s-text) !important;
    background: #FFFFFF !important;
    min-height: 40px !important;
}}

[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {{
    border-color: #359ECE !important;
    box-shadow: 0 0 0 1px #359ECE !important;
}}

/* Botons Sorigue */
.stButton > button,
[data-testid="stFormSubmitButton"] button,
.stDownloadButton > button {{
    border-radius: 4px !important;
    min-height: 38px !important;
    padding: 8px 14px !important;
    font-weight: 700 !important;
    border: 1px solid var(--s-primary) !important;
    background: var(--s-primary) !important;
    color: #FFFFFF !important;
    transition: all .15s ease-in-out !important;
    cursor: pointer !important;
}}

.stButton > button:hover,
[data-testid="stFormSubmitButton"] button:hover,
.stDownloadButton > button:hover {{
    background: var(--s-primary-hover) !important;
    border-color: var(--s-primary-hover) !important;
    color: #FFFFFF !important;
}}

.stButton > button:active,
[data-testid="stFormSubmitButton"] button:active,
.stDownloadButton > button:active {{
    background: var(--s-primary-dark) !important;
    border-color: var(--s-primary-dark) !important;
}}

[data-testid="stSidebar"] .stButton > button {{
    background: rgba(255,255,255,0.10) !important;
    border: 1px solid rgba(255,255,255,0.48) !important;
    color: #FFFFFF !important;
}}

[data-testid="stSidebar"] .stButton > button:hover {{
    background: rgba(255,255,255,0.22) !important;
}}

/* Cards */
.bigrock-card {{
    background: #FFFFFF;
    border-left: 6px solid var(--s-primary);
    border-radius: 8px;
    padding: 22px 24px;
    margin: 0 0 16px 0;
    box-shadow: 0 2px 9px rgba(35,35,35,.08);
    border-top: 1px solid #EEF2F4;
    border-right: 1px solid #EEF2F4;
    border-bottom: 1px solid #EEF2F4;
}}

.bigrock-title {{
    font-size: 24px;
    font-weight: 700;
    color: var(--s-text);
    margin-bottom: 6px;
}}

.bigrock-meta {{
    color: var(--s-grey);
    font-size: 14px;
    margin-bottom: 14px;
}}

.kpi-card {{
    background: #FFFFFF;
    border-radius: 8px;
    padding: 18px 20px;
    box-shadow: 0 2px 9px rgba(35,35,35,.08);
    border-top: 4px solid var(--s-primary);
    min-height: 112px;
}}

.kpi-label {{
    color: var(--s-grey);
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .02em;
}}

.kpi-value {{
    font-size: 34px;
    line-height: 42px;
    color: var(--s-text);
    font-weight: 700;
    margin-top: 8px;
}}

.s-progress {{
    width: 100%;
    background: #E0E2E3;
    border-radius: 999px;
    overflow: hidden;
    height: 28px;
    margin: 6px 0 16px 0;
}}

.s-progress-inner {{
    height: 100%;
    border-radius: 999px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 13px;
    color: #FFFFFF;
    min-width: 38px;
}}

.tar-mobile-card {{
    background: #FFFFFF;
    border: 1px solid #E0E2E3;
    border-radius: 8px;
    padding: 12px 14px 8px 14px;
    margin: 10px 0 14px 0;
    box-shadow: 0 1px 4px rgba(35,35,35,.04);
}}

.tar-badge {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 5px;
    background: var(--s-light-blue);
    color: var(--s-primary-dark);
    font-weight: 700;
    padding: 7px 11px;
    min-width: 64px;
    font-size: 13px;
    margin-bottom: 8px;
}}

.empty-state {{
    background: #FFFFFF;
    border-radius: 8px;
    padding: 46px 28px;
    text-align: center;
    border: 1px dashed #C6E0EC;
    box-shadow: 0 2px 9px rgba(35,35,35,.06);
}}

.empty-icon {{
    height: 85px;
    width: 85px;
    border-radius: 50%;
    background: #C6E0EC;
    color: var(--s-primary-dark);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 34px;
    font-weight: 700;
    margin-bottom: 20px;
}}

.help-box {{
    background: var(--s-light-blue);
    border: 1px solid var(--s-primary-dark);
    border-radius: 4px;
    padding: 14px 16px;
}}

.help-box-title {{
    color: var(--s-primary-dark);
    font-weight: 700;
    margin-bottom: 4px;
}}

/* Expander net: sense textos arrow_right/keyboard... ni icones substituides */
.streamlit-expanderHeader,
[data-testid="stExpander"] summary {{
    font-family: 'Montserrat', Arial, sans-serif !important;
    font-weight: 700 !important;
    color: var(--s-text) !important;
    line-height: 24px !important;
    min-height: 44px !important;
}}

[data-testid="stExpander"] details {{
    border-radius: 8px !important;
}}

[data-testid="stRadio"] label {{
    color: var(--s-text) !important;
}}

/* Mobile */
@media (max-width: 768px) {{
    .block-container {{
        padding-top: .9rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }}
    h1 {{
        font-size: 32px !important;
        line-height: 38px !important;
    }}
    .kpi-card {{
        min-height: 92px;
        padding: 14px 15px;
    }}
    .kpi-value {{
        font-size: 28px;
        line-height: 34px;
    }}
    .bigrock-card {{
        padding: 18px 16px;
        margin-bottom: 12px;
    }}
    .bigrock-title {{
        font-size: 22px;
        line-height: 28px;
    }}
    .sidebar-logo-text {{
        font-size: 42px;
        margin-top: 12px;
    }}
    .sidebar-status-card {{
        margin: 10px 0 14px 0;
    }}
    [data-testid="stSidebar"] {{
        min-width: 305px !important;
        max-width: 305px !important;
    }}
    [data-testid="stSidebar"] .block-container {{
        padding-top: 1rem;
    }}
}}
</style>
""",
        unsafe_allow_html=True,
    )


inject_css()

# ============================================================
# 3. BASE DE DADES I SEGURETAT
# ============================================================

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def run_query(query, params=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    lastrowid = cur.lastrowid
    conn.close()
    return lastrowid


def fetch_query(query, params=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, params)
    data = cur.fetchall()
    conn.close()
    return data


def column_exists(table, column):
    rows = fetch_query(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in rows)


def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16)
    if isinstance(salt, str):
        salt = bytes.fromhex(salt)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120000)
    return salt.hex(), digest.hex()


def verify_password(password, stored_password, stored_salt=None):
    # Compatibilitat amb usuaris antics: si no hi ha salt, valida password en text pla i despres migra.
    if stored_salt is None or stored_salt == "":
        return password == stored_password
    _, digest = hash_password(password, stored_salt)
    return digest == stored_password


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS usuaris (
            username TEXT PRIMARY KEY,
            password TEXT,
            language TEXT DEFAULT 'ca',
            password_salt TEXT,
            created_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS big_rocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            mes TEXT,
            nom TEXT,
            persones TEXT,
            reunions TEXT,
            notes_progres TEXT,
            pregunta TEXT,
            passos TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_br INTEGER,
            num TEXT,
            descripcio TEXT,
            progres INTEGER,
            estat TEXT DEFAULT 'Actiu',
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY(id_br) REFERENCES big_rocks(id)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS mesos_tancats (
            username TEXT,
            mes TEXT,
            closed_at TEXT,
            PRIMARY KEY(username, mes)
        )
        """
    )
    conn.commit()
    conn.close()

    migrations = {
        "usuaris": [("language", "TEXT DEFAULT 'ca'"), ("password_salt", "TEXT"), ("created_at", "TEXT")],
        "big_rocks": [("created_at", "TEXT"), ("updated_at", "TEXT")],
        "tars": [("created_at", "TEXT"), ("updated_at", "TEXT")],
        "mesos_tancats": [("closed_at", "TEXT")],
    }
    for table, cols in migrations.items():
        for col, col_type in cols:
            if not column_exists(table, col):
                try:
                    run_query(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
                except sqlite3.OperationalError:
                    pass


init_db()

# ============================================================
# 4. UTILITATS
# ============================================================

def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def get_month_key(lang=None):
    lang = lang or st.session_state.get("idioma", "ca")
    months = TRANS[lang]["months"]
    now = datetime.now()
    return f"{months[now.month - 1]} {now.year}"


def normalize_month_to_lang(month_text, target_lang):
    if not month_text or " " not in month_text:
        return get_month_key(target_lang)
    parts = month_text.split(" ")
    month_name = parts[0]
    year = parts[-1]
    for lang in ("ca", "es"):
        if month_name in TRANS[lang]["months"]:
            idx = TRANS[lang]["months"].index(month_name)
            return f"{TRANS[target_lang]['months'][idx]} {year}"
    return month_text


def next_month(month_text, target_lang):
    parts = month_text.split(" ")
    if len(parts) < 2:
        return get_month_key(target_lang)
    month_name = parts[0]
    year = int(parts[-1])
    idx = None
    for lang in ("ca", "es"):
        if month_name in TRANS[lang]["months"]:
            idx = TRANS[lang]["months"].index(month_name)
            break
    if idx is None:
        return get_month_key(target_lang)
    if idx == 11:
        return f"{TRANS[target_lang]['months'][0]} {year + 1}"
    return f"{TRANS[target_lang]['months'][idx + 1]} {year}"


def progress_color(progress):
    if progress <= 25:
        return ERROR
    if progress <= 50:
        return WARNING
    if progress <= 90:
        return "#D9AF00"
    return SUCCESS


def progress_bar(progress, label=None):
    progress = int(progress or 0)
    color = progress_color(progress)
    text_color = "#FFFFFF"
    label_text = label if label else f"{progress}%"
    st.markdown(
        f"""
        <div class="s-progress">
            <div class="s-progress-inner" style="width:{max(progress, 4)}%; background:{color}; color:{text_color};">
                {label_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def file_to_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def find_existing(candidates):
    for name in candidates:
        if os.path.exists(name):
            return name
    return None


def logo_for_sidebar():
    negative = find_existing(LOGO_NEGATIVE_CANDIDATES)
    if negative:
        b64 = file_to_b64(negative)
        return f'<img src="data:image/png;base64,{b64}" style="width:220px; max-width:100%; display:block; margin: 12px auto 18px auto;">'
    return '<div class="sidebar-logo-text">sorigué</div>'


def logo_for_login():
    positive = find_existing(LOGO_POSITIVE_CANDIDATES)
    if positive:
        b64 = file_to_b64(positive)
        return f'<img src="data:image/png;base64,{b64}" style="width:250px; max-width:100%; display:block; margin: 0 auto 22px auto;">'
    return '<div style="font-size:48px; font-weight:700; color:white; text-align:center; margin-bottom:18px;">sorigué</div>'


def kpi_card(label, value):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_brs(username, month):
    return fetch_query(
        """
        SELECT id, nom, persones, reunions, notes_progres, pregunta, passos
        FROM big_rocks
        WHERE username=? AND mes=?
        ORDER BY id ASC
        """,
        (username, month),
    )


def get_tars(br_id, active_only=True):
    if active_only:
        return fetch_query(
            "SELECT id, num, descripcio, progres FROM tars WHERE id_br=? AND estat='Actiu' ORDER BY id ASC",
            (br_id,),
        )
    return fetch_query(
        "SELECT id, num, descripcio, progres, estat FROM tars WHERE id_br=? ORDER BY id ASC",
        (br_id,),
    )


def month_is_closed(username, month):
    return len(fetch_query("SELECT 1 FROM mesos_tancats WHERE username=? AND mes=?", (username, month))) > 0


def dashboard_stats(username, month):
    brs = get_brs(username, month)
    all_tars = []
    for br in brs:
        all_tars.extend(get_tars(br[0], active_only=True))
    total = len(all_tars)
    completed = sum(1 for tar in all_tars if int(tar[3]) == 100)
    pending = sum(1 for tar in all_tars if int(tar[3]) < 100)
    avg = int(sum(int(tar[3]) for tar in all_tars) / total) if total else 0
    return len(brs), completed, pending, avg


def update_db_val(table, field, val, uid):
    allowed = {
        "tars": {"descripcio", "progres", "estat"},
        "big_rocks": {"notes_progres", "pregunta", "passos", "nom", "persones", "reunions"},
    }
    if table not in allowed or field not in allowed[table]:
        return
    run_query(f"UPDATE {table} SET {field}=?, updated_at=? WHERE id=?", (val, now_iso(), uid))


def archive_tar(tar_id):
    run_query("UPDATE tars SET estat='Arxivat', updated_at=? WHERE id=?", (now_iso(), tar_id))


def change_language():
    username = st.session_state.get("usuari_actual")
    selected = st.session_state.get("idioma_selector", "ca")
    if username:
        run_query("UPDATE usuaris SET language=? WHERE username=?", (selected, username))
    previous_month = st.session_state.get("mes_actual")
    st.session_state.idioma = selected
    if previous_month:
        st.session_state.mes_actual = normalize_month_to_lang(previous_month, selected)


def export_month_dataframe(username, month):
    rows = []
    for br in get_brs(username, month):
        br_id, nom, persones, reunions, notes, pregunta, passos = br
        for tar in get_tars(br_id, active_only=True):
            rows.append(
                {
                    "usuari": username,
                    "mes": month,
                    "big_rock": nom,
                    "persones_clau": persones,
                    "reunions": reunions,
                    "tar": tar[1],
                    "descripcio": tar[2],
                    "progres": tar[3],
                    "notes_progres": notes,
                    "pregunta": pregunta,
                    "passos": passos,
                }
            )
    return pd.DataFrame(rows)

# ============================================================
# 5. SESSION STATE
# ============================================================

if "usuari_actual" not in st.session_state:
    st.session_state.usuari_actual = None
if "idioma" not in st.session_state:
    st.session_state.idioma = "ca"
if "pantalla" not in st.session_state:
    st.session_state.pantalla = "dashboard"
if "mostrar_formulari_br" not in st.session_state:
    st.session_state.mostrar_formulari_br = False
if "mes_actual" not in st.session_state:
    st.session_state.mes_actual = get_month_key(st.session_state.idioma)

# ============================================================
# 6. LOGIN I REGISTRE
# ============================================================

if st.session_state.usuari_actual is None:
    left, center, right = st.columns([1, 1.35, 1])
    with center:
        st.markdown(
            f"""
            <div style="background:{PRIMARY}; border-radius:10px; padding:36px 38px 34px 38px; margin-top:32px; box-shadow:0 3px 14px rgba(35,35,35,.12);">
                {logo_for_login()}
                <div style="color:#FFFFFF; font-size:28px; line-height:34px; font-weight:700; text-align:center;">{t('login_title')}</div>
                <div style="color:#E7F2F7; font-size:14px; line-height:21px; text-align:center; margin-top:8px;">{t('login_subtitle')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        tab1, tab2 = st.tabs([t("login_tab"), t("reg_tab")])

        with tab1:
            with st.form("login_form"):
                usuari = st.text_input(t("usr"), placeholder="marc.llopis")
                contrasenya = st.text_input(t("pwd"), type="password", placeholder="********")
                submitted = st.form_submit_button(t("enter"), type="primary", use_container_width=True)
                if submitted:
                    if not usuari.strip() or not contrasenya.strip():
                        st.error(t("required_fields"))
                    else:
                        user_data = fetch_query(
                            "SELECT password, password_salt, language FROM usuaris WHERE username=?",
                            (usuari.strip(),),
                        )
                        if user_data and verify_password(contrasenya, user_data[0][0], user_data[0][1]):
                            st.session_state.usuari_actual = usuari.strip()
                            st.session_state.idioma = user_data[0][2] if user_data[0][2] else "ca"
                            st.session_state.mes_actual = get_month_key(st.session_state.idioma)
                            st.session_state.pantalla = "dashboard"
                            if not user_data[0][1]:
                                salt, digest = hash_password(contrasenya)
                                run_query(
                                    "UPDATE usuaris SET password=?, password_salt=? WHERE username=?",
                                    (digest, salt, usuari.strip()),
                                )
                            st.rerun()
                        else:
                            st.error(t("err_login"))

        with tab2:
            with st.form("register_form"):
                nou_usuari = st.text_input(t("new_usr"), placeholder="nom.cognom")
                nova_contra = st.text_input(t("pwd"), type="password", placeholder="Mínim recomanat: 8 caràcters")
                nou_idioma = st.selectbox(
                    t("lang_reg"),
                    options=["ca", "es"],
                    format_func=lambda x: "Català" if x == "ca" else "Español",
                )
                submitted = st.form_submit_button(t("register"), type="primary", use_container_width=True)
                if submitted:
                    if not nou_usuari.strip() or not nova_contra.strip():
                        st.error(t("required_fields"))
                    else:
                        try:
                            salt, digest = hash_password(nova_contra)
                            run_query(
                                """
                                INSERT INTO usuaris (username, password, language, password_salt, created_at)
                                VALUES (?, ?, ?, ?, ?)
                                """,
                                (nou_usuari.strip(), digest, nou_idioma, salt, now_iso()),
                            )
                            st.success(t("succ_reg"))
                        except sqlite3.IntegrityError:
                            st.error(t("err_reg"))
    st.stop()

# ============================================================
# 7. SIDEBAR
# ============================================================

USUARI = st.session_state.usuari_actual

with st.sidebar:
    st.markdown(logo_for_sidebar(), unsafe_allow_html=True)
    st.markdown(f"<div class='sidebar-app-title'>BIG ROCKS</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sidebar-app-subtitle'>{t('brand_subtitle')}</div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="sidebar-status-card">
            <div class="sidebar-pill">Persona</div>
            <div class="sidebar-white" style="font-size:14px; margin-top:10px; font-weight:500;">{t('conn_as')}</div>
            <div class="sidebar-white" style="font-size:16px; margin-top:2px; font-weight:700;">{USUARI}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    lang_idx = 0 if st.session_state.idioma == "ca" else 1
    idioma_triat = st.selectbox(
        t("lang"),
        ["ca", "es"],
        index=lang_idx,
        format_func=lambda x: "Català" if x == "ca" else "Castellano",
        key="idioma_selector",
        on_change=change_language,
    )
    st.session_state.idioma = idioma_triat

    mesos_disponibles = [
        row[0]
        for row in fetch_query(
            "SELECT DISTINCT mes FROM big_rocks WHERE username=? ORDER BY id DESC",
            (USUARI,),
        )
    ]
    mes_ini = get_month_key(st.session_state.idioma)
    if mes_ini not in mesos_disponibles:
        mesos_disponibles.insert(0, mes_ini)
    if st.session_state.mes_actual not in mesos_disponibles:
        st.session_state.mes_actual = mes_ini

    mes_seleccionat = st.selectbox(
        t("nav_months"),
        mesos_disponibles,
        index=mesos_disponibles.index(st.session_state.mes_actual),
        key="mes_selector",
    )
    st.session_state.mes_actual = mes_seleccionat
    MES = st.session_state.mes_actual
    es_tancat = month_is_closed(USUARI, MES)

    if es_tancat:
        st.markdown(
            f"""
            <div class='sidebar-status-card'>
                <div class='sidebar-white' style='font-weight:700;'>{t('status_closed')}</div>
                <div class='sidebar-white' style='margin-top:5px;'>{t('closed_month')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(t("unlock"), use_container_width=True):
            run_query("DELETE FROM mesos_tancats WHERE username=? AND mes=?", (USUARI, MES))
            st.rerun()
    else:
        st.markdown(
            f"""
            <div class='sidebar-status-card'>
                <div class='sidebar-white' style='font-weight:700;'>{t('status_open')}</div>
                <div class='sidebar-white' style='margin-top:5px;'>{t('open_month')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:34px;'></div>", unsafe_allow_html=True)
    if st.button(t("logout"), use_container_width=True):
        for key in ["usuari_actual", "pantalla", "mostrar_formulari_br"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# ============================================================
# 8. DASHBOARD PRINCIPAL
# ============================================================

MES = st.session_state.mes_actual
es_tancat = month_is_closed(USUARI, MES)

if st.session_state.pantalla == "dashboard":
    col_title, col_help = st.columns([2.25, 1])
    with col_title:
        st.title(f"Big Rocks · {MES}")
    with col_help:
        st.markdown(
            f"""
            <div class="help-box">
                <div class="help-box-title">{t('help_title')}</div>
                <div style="font-size:13px; color:#232323;">{t('help_body')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    br_count, completed, pending, avg = dashboard_stats(USUARI, MES)
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        kpi_card(t("active_brs"), br_count)
    with k2:
        kpi_card(t("avg_progress"), f"{avg}%")
    with k3:
        kpi_card(t("completed_tars"), completed)
    with k4:
        kpi_card(t("pending_tars"), pending)

    st.write("")
    action_col1, action_col2, _ = st.columns([1.35, 1.2, 3])
    with action_col1:
        if not es_tancat:
            if st.button(t("eval_close"), type="primary", use_container_width=True):
                st.session_state.pantalla = "resum"
                st.rerun()
    with action_col2:
        df_export = export_month_dataframe(USUARI, MES)
        if not df_export.empty:
            st.download_button(
                t("export_csv"),
                df_export.to_csv(index=False).encode("utf-8-sig"),
                file_name=f"bigrocks_{USUARI}_{MES}.csv".replace(" ", "_"),
                mime="text/csv",
                use_container_width=True,
            )

    st.write("")
    brs = get_brs(USUARI, MES)

    if not brs:
        st.markdown(
            f"""
            <div class="empty-state">
                <div class="empty-icon">BR</div>
                <h2>{t('no_br_title')}</h2>
                <p style="color:#53565A; font-size:16px;">{t('no_br_body')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if not es_tancat:
            _, cta_col, _ = st.columns([1, 1, 1])
            with cta_col:
                if st.button(t("empty_cta"), type="primary", use_container_width=True):
                    st.session_state.mostrar_formulari_br = True
    else:
        for br in brs:
            br_id, nom, persones, reunions, notes_progres, pregunta, passos = br
            tars = get_tars(br_id, active_only=True)
            progres_mitja = int(sum(int(tar[3]) for tar in tars) / len(tars)) if tars else 0

            st.markdown(
                f"""
                <div class="bigrock-card">
                    <div class="bigrock-title">{nom}</div>
                    <div class="bigrock-meta"><strong>{t('key_ppl')}:</strong> {persones or '-'} &nbsp;&nbsp;|&nbsp;&nbsp; <strong>{t('key_meet')}:</strong> {reunions or '-'}</div>
                    <div style="font-weight:700; color:#53565A; font-size:13px; text-transform:uppercase;">{t('global_prog')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            progress_bar(progres_mitja, f"{progres_mitja}%")

            # TARs en format vertical perque sigui net a mobil i tambe acceptable a desktop
            for tar in tars:
                tar_id, num, desc, progres = tar
                progres = int(progres) if int(progres) in [0, 50, 100] else 0
                st.markdown("<div class='tar-mobile-card'>", unsafe_allow_html=True)
                top_a, top_b = st.columns([1, 1])
                with top_a:
                    st.markdown(f"<div class='tar-badge'>{num}</div>", unsafe_allow_html=True)
                with top_b:
                    if not es_tancat:
                        st.button(
                            t("archive"),
                            key=f"btn_archive_{tar_id}",
                            on_click=archive_tar,
                            args=(tar_id,),
                            disabled=es_tancat,
                            help=t("delete_help"),
                            use_container_width=True,
                        )
                k_desc = f"desc_{tar_id}"
                st.text_input(
                    t("desc"),
                    value=desc,
                    key=k_desc,
                    label_visibility="collapsed",
                    disabled=es_tancat,
                    placeholder=t("desc"),
                    on_change=lambda tid=tar_id, k=k_desc: update_db_val("tars", "descripcio", st.session_state[k], tid),
                )
                k_radio = f"radio_{tar_id}"
                st.radio(
                    t("state"),
                    options=[0, 50, 100],
                    format_func=lambda x: f"{x}%",
                    index=[0, 50, 100].index(progres),
                    horizontal=True,
                    key=k_radio,
                    label_visibility="collapsed",
                    disabled=es_tancat,
                    on_change=lambda tid=tar_id, k=k_radio: update_db_val("tars", "progres", st.session_state[k], tid),
                )
                progress_bar(progres)
                st.markdown("</div>", unsafe_allow_html=True)

            # Expander sense icona manual ni prefixos que puguin solapar-se
            with st.expander(t("details"), expanded=False):
                notes_key = f"notes_{br_id}"
                preg_key = f"preg_{br_id}"
                passos_key = f"passos_{br_id}"
                notes = st.text_area(t("prog"), value=notes_progres or "", key=notes_key, disabled=es_tancat)
                preg = st.text_input(t("need"), value=pregunta or "", key=preg_key, disabled=es_tancat)
                passos_val = st.text_input(t("next_steps"), value=passos or "", key=passos_key, disabled=es_tancat)
                if not es_tancat:
                    if st.button(t("save_notes"), key=f"save_{br_id}"):
                        run_query(
                            "UPDATE big_rocks SET notes_progres=?, pregunta=?, passos=?, updated_at=? WHERE id=?",
                            (notes, preg, passos_val, now_iso(), br_id),
                        )
                        st.success(t("saved"))

    if not es_tancat:
        st.write("")
        if st.button(t("create_br"), type="primary"):
            st.session_state.mostrar_formulari_br = not st.session_state.mostrar_formulari_br

        if st.session_state.mostrar_formulari_br:
            st.subheader(t("config_br"))
            with st.form("form_nova_br"):
                nou_nom = st.text_input(t("title_br"), placeholder=t("title_placeholder"))
                c1, c2 = st.columns(2)
                persones = c1.text_input(t("key_ppl"), placeholder=t("people_placeholder"))
                reunions = c2.text_input(t("key_meet"), placeholder=t("meetings_placeholder"))
                st.markdown("### TARs")
                t1 = st.text_input("TAR 1", placeholder=t("tar_placeholder"))
                t2 = st.text_input("TAR 2", placeholder=t("tar_placeholder"))
                t3 = st.text_input("TAR 3", placeholder=t("tar_placeholder"))
                t4 = st.text_input("TAR 4", placeholder=t("tar_placeholder"))
                submitted = st.form_submit_button(t("save"), type="primary", use_container_width=True)
                if submitted:
                    if not nou_nom.strip():
                        st.error(t("title_br"))
                    else:
                        br_id = run_query(
                            """
                            INSERT INTO big_rocks
                            (username, mes, nom, persones, reunions, notes_progres, pregunta, passos, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, '', '', '', ?, ?)
                            """,
                            (USUARI, MES, nou_nom.strip(), persones.strip(), reunions.strip(), now_iso(), now_iso()),
                        )
                        for i, desc_tar in enumerate([t1, t2, t3, t4], start=1):
                            if desc_tar.strip():
                                run_query(
                                    """
                                    INSERT INTO tars (id_br, num, descripcio, progres, estat, created_at, updated_at)
                                    VALUES (?, ?, ?, ?, 'Actiu', ?, ?)
                                    """,
                                    (br_id, f"TAR {i}", desc_tar.strip(), 0, now_iso(), now_iso()),
                                )
                        st.session_state.mostrar_formulari_br = False
                        st.rerun()

# ============================================================
# 9. RESUM I TANCAMENT DE MES
# ============================================================

elif st.session_state.pantalla == "resum":
    st.title(f"{t('summary')} · {MES}")

    brs = get_brs(USUARI, MES)
    tars_completats = []
    tars_pendents = []
    sumatori_progres = 0
    total_tars = 0

    for br in brs:
        br_id, nom, persones, reunions, *_ = br
        for tar in get_tars(br_id, active_only=True):
            _, _, desc, progres = tar
            progres = int(progres)
            sumatori_progres += progres
            total_tars += 1
            if progres == 100:
                tars_completats.append((nom, desc))
            else:
                tars_pendents.append((nom, desc, progres))

    compliment_global = int(sumatori_progres / total_tars) if total_tars else 0
    st.markdown(f"### {t('global_comp')}")
    progress_bar(compliment_global, f"{compliment_global}%")

    ce, ct = st.columns(2)
    with ce:
        st.success(t("successes"))
        if tars_completats:
            for nom, desc in tars_completats:
                st.markdown(f"- **{nom}** → {desc}")
        else:
            st.caption("-")
    with ct:
        st.warning(t("carry_over"))
        if tars_pendents:
            for nom, desc, progres in tars_pendents:
                st.markdown(f"- **{nom}** → {desc} ({progres}%)")
        else:
            st.caption("-")

    def confirm_month_close():
        run_query(
            "INSERT OR IGNORE INTO mesos_tancats (username, mes, closed_at) VALUES (?, ?, ?)",
            (USUARI, MES, now_iso()),
        )
        nou_mes = next_month(MES, st.session_state.idioma)
        brs_actuals = get_brs(USUARI, MES)
        for br in brs_actuals:
            br_id, nom, persones, reunions, *_ = br
            pendents_db = fetch_query(
                "SELECT num, descripcio, progres FROM tars WHERE id_br=? AND estat='Actiu' AND progres < 100 ORDER BY id ASC",
                (br_id,),
            )
            if pendents_db:
                new_br_id = run_query(
                    """
                    INSERT INTO big_rocks
                    (username, mes, nom, persones, reunions, notes_progres, pregunta, passos, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, '', '', '', ?, ?)
                    """,
                    (USUARI, nou_mes, nom, persones, reunions, now_iso(), now_iso()),
                )
                for tar in pendents_db:
                    run_query(
                        """
                        INSERT INTO tars (id_br, num, descripcio, progres, estat, created_at, updated_at)
                        VALUES (?, ?, ?, ?, 'Actiu', ?, ?)
                        """,
                        (new_br_id, tar[0], tar[1], tar[2], now_iso(), now_iso()),
                    )
        st.session_state.mes_actual = nou_mes
        st.session_state.pantalla = "dashboard"
        st.rerun()

    st.write("")
    cb1, cb2, _ = st.columns([1, 2, 1])
    with cb1:
        if st.button(t("cancel"), use_container_width=True):
            st.session_state.pantalla = "dashboard"
            st.rerun()
    with cb2:
        st.button(t("confirm_close"), on_click=confirm_month_close, type="primary", use_container_width=True)
