
import base64
import hashlib
import html
import json
import os
import re
from datetime import datetime

import pandas as pd
import streamlit as st
from supabase import create_client

# ============================================================
# BIG ROCKS - SORIGUE | APP.py V29
# Login net amb correu @sorigue.com + TARs en una sola línia
# Opció B segments + TAR dins targeta + edició amb llapis
# ============================================================

NOTES_PREFIX = "__BIGROCK_NOTES_JSON_V1__"
ALLOWED_EMAIL_DOMAIN = "@sorigue.com"
MICROSOFT_LOGIN_ENABLED = False  # ocult fins que IT habiliti Entra App Registration

PRIMARY = "#009CDE"
PRIMARY_DARK = "#216D8C"
PRIMARY_HOVER = "#43B8ED"
TEXT = "#232323"
GREY = "#53565A"
SUCCESS = "#03A446"
WARNING = "#D9AF00"
ERROR = "#E53A4F"
LIGHT_BLUE = "#E7F2F7"

LANG_OPTIONS = {"ca": "🇦🇩 Català", "es": "🇪🇸 Español"}
PROGRESS_OPTIONS = [0, 25, 50, 75, 100]

USER_EMAIL_MIGRATION = {
    "marc.llopis@sorigue.com": ["marc.llopis", "Marc.llopis", "marc llopis", "Marc Llopis", "marc"],
    "xavier.llopis@sorigue.com": ["Xavier.llopis", "xavier.llopis", "Xavier.llopsi", "xavier.llopsi", "xavier llopis", "Xavier Llopis", "xavier"],
}

st.set_page_config(page_title="Big Rocks - Sorigué", layout="wide", page_icon="BR", initial_sidebar_state="expanded")

TRANS = {
    "ca": {
        "login_title": "Accés a la Plataforma",
        "login_subtitle": "Seguiment mensual dels teus Big Rocks i TARs",
        "legacy_login": "Accés amb usuari i contrasenya",
        "login_tab": "Iniciar sessió",
        "reg_tab": "Registrar usuari",
        "usr": "Usuari",
        "email_user": "Correu corporatiu",
        "pwd": "Contrasenya",
        "new_usr": "Correu corporatiu",
        "lang_reg": "Idioma per defecte",
        "enter": "Entrar",
        "register": "Registrar",
        "err_login": "Usuari o contrasenya incorrectes.",
        "succ_reg": "Usuari creat correctament.",
        "err_reg": "Aquest usuari ja existeix.",
        "required_fields": "Introdueix usuari i contrasenya per continuar.",
        "corp_email_required": "El registre només permet correus corporatius @sorigue.com.",
        "lang_login": "🌍 Idioma",
        "lang": "Idioma",
        "conn_as": "Connectat com:",
        "nav_months": "Navegar pels mesos",
        "status_open": "Obert",
        "status_closed": "Tancat",
        "open_month": "Mes obert i editable",
        "closed_month": "Aquest mes està tancat.",
        "unlock": "Desbloquejar mes",
        "logout": "Tancar sessió",
        "eval_close": "Avaluar i tancar mes",
        "eval_no_close": "Avaluar sense tancar",
        "collapse_all": "Contraure els BR",
        "active_brs": "Big Rocks actives",
        "completed_tars": "TARs completats",
        "pending_tars": "TARs pendents",
        "avg_progress": "Progrés mitjà",
        "help_title": "Consell d'usabilitat",
        "help_body": "Clica una Big Rock per obrir-la. La resta quedaran plegades per mantenir la vista neta.",
        "no_br_title": "Encara no tens cap Big Rock creada",
        "no_br_body": "Crea la primera Big Rock per començar el seguiment mensual.",
        "empty_cta": "Crea la primera Big Rock",
        "key_ppl": "Persones clau",
        "key_meet": "Reunions",
        "details": "Detalls, preguntes i pròxims passos",
        "prog": "Detalls de progrés",
        "need": "Pregunta o necessitat",
        "next_steps": "Pròxims passos",
        "state": "Estat",
        "desc": "Descripció de la tasca",
        "tar_notes": "Anotacions de la TAR",
        "tar_notes_placeholder": "Escriu observacions, acords, incidències o seguiment específic d'aquesta TAR...",
        "save_full_br": "Guardar Big Rock",
        "create_br": "Crear nova Big Rock",
        "config_br": "Configura la teva nova Big Rock",
        "title_br": "Títol de la Big Rock",
        "title_placeholder": "Ex. Reduir incidències crítiques de l'obra",
        "people_placeholder": "Ex. Xavier, Gerard, equip nord...",
        "meetings_placeholder": "Ex. Seguiment setmanal, comitè mensual...",
        "tar_placeholder": "Descriu una acció concreta i mesurable",
        "save": "Guardar Big Rock",
        "saved": "Canvis guardats correctament.",
        "summary": "Resum de tancament",
        "report_title": "Informe de seguiment",
        "global_comp": "Grau de compliment global",
        "successes": "Èxits completats",
        "in_progress": "En curs",
        "carry_over": "Es traspassen",
        "cancel": "Cancel·lar i tornar",
        "confirm_close": "Confirmar tancament i crear mes següent",
        "back": "Tornar",
        "admin_panel": "⚙ Administració",
        "admin_badge": "Administrador",
        "admin_users": "Gestió d'usuaris",
        "admin_no_users": "No s'han trobat usuaris.",
        "force_migration": "Forçar migració usuaris antics",
        "migration_ok": "Migració executada.",
        "progress_views": "Vistes de compliment",
        "view_buttons": "Opció A · Botons",
        "view_segments": "Opció B · Segments",
        "view_pills": "Opció C · Pastilles",
        "view_bar": "Opció D · Barra fina",
        "supabase_error": "No s'ha pogut connectar amb Supabase. Revisa SUPABASE_URL i SUPABASE_KEY a Streamlit Secrets.",
        "months": ["Gener", "Febrer", "Març", "Abril", "Maig", "Juny", "Juliol", "Agost", "Setembre", "Octubre", "Novembre", "Desembre"],
    },
    "es": {
        "login_title": "Acceso a la Plataforma",
        "login_subtitle": "Seguimiento mensual de tus Big Rocks y TARs",
        "legacy_login": "Acceso con usuario y contraseña",
        "login_tab": "Iniciar sesión",
        "reg_tab": "Registrar usuario",
        "usr": "Usuario",
        "email_user": "Correo corporativo",
        "pwd": "Contraseña",
        "new_usr": "Correo corporativo",
        "lang_reg": "Idioma por defecto",
        "enter": "Entrar",
        "register": "Registrar",
        "err_login": "Usuario o contraseña incorrectos.",
        "succ_reg": "Usuario creado correctamente.",
        "err_reg": "Este usuario ya existe.",
        "required_fields": "Introduce usuario y contraseña para continuar.",
        "corp_email_required": "El registro solo permite correos corporativos @sorigue.com.",
        "lang_login": "🌍 Idioma",
        "lang": "Idioma",
        "conn_as": "Conectado como:",
        "nav_months": "Navegar por los meses",
        "status_open": "Abierto",
        "status_closed": "Cerrado",
        "open_month": "Mes abierto y editable",
        "closed_month": "Este mes está cerrado.",
        "unlock": "Desbloquear mes",
        "logout": "Cerrar sesión",
        "eval_close": "Evaluar y cerrar mes",
        "eval_no_close": "Evaluar sin cerrar",
        "collapse_all": "Contraer BR",
        "active_brs": "Big Rocks activas",
        "completed_tars": "TARs completados",
        "pending_tars": "TARs pendientes",
        "avg_progress": "Progreso medio",
        "help_title": "Consejo de usabilidad",
        "help_body": "Haz clic en una Big Rock para abrirla. El resto quedarán plegadas para mantener la vista limpia.",
        "no_br_title": "Aún no tienes ninguna Big Rock creada",
        "no_br_body": "Crea la primera Big Rock para empezar el seguimiento mensual.",
        "empty_cta": "Crea la primera Big Rock",
        "key_ppl": "Personas clave",
        "key_meet": "Reuniones",
        "details": "Detalles, preguntas y próximos pasos",
        "prog": "Detalles de progreso",
        "need": "Pregunta o necesidad",
        "next_steps": "Próximos pasos",
        "state": "Estado",
        "desc": "Descripción de la tarea",
        "tar_notes": "Anotaciones de la TAR",
        "tar_notes_placeholder": "Escribe observaciones, acuerdos, incidencias o seguimiento específico de esta TAR...",
        "save_full_br": "Guardar Big Rock",
        "create_br": "Crear nueva Big Rock",
        "config_br": "Configura tu nueva Big Rock",
        "title_br": "Título de la Big Rock",
        "title_placeholder": "Ej. Reducir incidencias críticas de la obra",
        "people_placeholder": "Ej. Xavier, Gerard, equipo norte...",
        "meetings_placeholder": "Ej. Seguimiento semanal, comité mensual...",
        "tar_placeholder": "Describe una acción concreta y medible",
        "save": "Guardar Big Rock",
        "saved": "Cambios guardados correctamente.",
        "summary": "Resumen de cierre",
        "report_title": "Informe de seguimiento",
        "global_comp": "Grado de cumplimiento global",
        "successes": "Éxitos completados",
        "in_progress": "En curso",
        "carry_over": "Se traspasan",
        "cancel": "Cancelar y volver",
        "confirm_close": "Confirmar cierre y crear mes siguiente",
        "back": "Volver",
        "admin_panel": "⚙ Administración",
        "admin_badge": "Administrador",
        "admin_users": "Gestión de usuarios",
        "admin_no_users": "No se han encontrado usuarios.",
        "force_migration": "Forzar migración usuarios antiguos",
        "migration_ok": "Migración ejecutada.",
        "progress_views": "Vistas de cumplimiento",
        "view_buttons": "Opción A · Botones",
        "view_segments": "Opción B · Segmentos",
        "view_pills": "Opción C · Pastillas",
        "view_bar": "Opción D · Barra fina",
        "supabase_error": "No se ha podido conectar con Supabase. Revisa SUPABASE_URL y SUPABASE_KEY en Streamlit Secrets.",
        "months": ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
    },
}


def t(key):
    return TRANS.get(st.session_state.get("idioma", "ca"), TRANS["ca"]).get(key, key)


def lang_label(code):
    return LANG_OPTIONS.get(code, code)


def safe_html(value):
    return html.escape(str(value or ""))


def inject_css():
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');
:root{{--s-primary:{PRIMARY};--s-primary-dark:{PRIMARY_DARK};--s-primary-hover:{PRIMARY_HOVER};--s-text:{TEXT};--s-grey:{GREY};--s-success:{SUCCESS};--s-warning:{WARNING};--s-error:{ERROR};--s-light-blue:{LIGHT_BLUE};}}
html,body,input,textarea,button,select{{font-family:'Montserrat',Arial,sans-serif!important;}}
p,label,h1,h2,h3,h4,h5,h6,[data-testid="stMarkdownContainer"],[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea,[data-baseweb="select"] div,[data-baseweb="select"] span{{font-family:'Montserrat',Arial,sans-serif!important;}}
.block-container{{padding-top:1.8rem;padding-bottom:3rem;max-width:1360px;}}
h1{{font-size:42px!important;line-height:50px!important;font-weight:700!important;color:var(--s-text)!important;}}
h2{{font-size:28px!important;line-height:34px!important;font-weight:700!important;color:var(--s-text)!important;}}
.login-logo-text{{color:#fff;font-size:56px;font-weight:700;line-height:1;text-align:center;margin:0 auto 24px auto;letter-spacing:-2px;}}
[data-testid="stSidebar"]{{background:linear-gradient(180deg,var(--s-primary) 0%,#08A7E8 100%)!important;}}
[data-testid="stSidebar"] label,[data-testid="stSidebar"] p,[data-testid="stSidebar"] .sidebar-white{{color:#fff!important;}}
[data-testid="stSidebar"] label{{font-weight:700!important;}}
.sidebar-logo-text{{color:#fff;font-size:48px;font-weight:700;text-align:center;margin:20px 0 8px 0;}}
.sidebar-app-title{{color:#fff;font-size:18px;font-weight:700;text-align:center;margin-bottom:4px;}}
.sidebar-app-subtitle{{color:rgba(255,255,255,.88);font-size:13px;text-align:center;margin-bottom:22px;}}
.sidebar-status-card{{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.38);border-radius:8px;padding:14px 16px;margin:14px 0 18px 0;}}
.sidebar-pill{{display:inline-flex;border-radius:999px;padding:7px 13px;background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.35);color:#fff;font-size:13px;font-weight:700;}}
[data-baseweb="select"] > div{{background:#fff!important;border:1px solid #BBBBBB!important;border-radius:4px!important;min-height:40px!important;}}
[data-baseweb="select"] span,[data-baseweb="select"] div,[data-testid="stSidebar"] [data-baseweb="select"] span,[data-testid="stSidebar"] [data-baseweb="select"] div,[data-testid="stSidebar"] [data-baseweb="select"] input{{color:var(--s-text)!important;}}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea{{border-radius:4px!important;border:1px solid #BBBBBB!important;color:var(--s-text)!important;background:#fff!important;min-height:40px!important;}}
.stButton>button,[data-testid="stFormSubmitButton"] button{{border-radius:4px!important;min-height:38px!important;font-weight:700!important;border:1px solid var(--s-primary)!important;background:var(--s-primary)!important;color:#fff!important;}}
.stButton>button:hover,[data-testid="stFormSubmitButton"] button:hover{{background:var(--s-primary-hover)!important;border-color:var(--s-primary-hover)!important;color:#fff!important;}}
[data-testid="stSidebar"] .stButton>button{{background:rgba(255,255,255,.10)!important;border:1px solid rgba(255,255,255,.48)!important;color:#fff!important;}}
.open-card-button button{{text-align:left!important;background:#fff!important;color:var(--s-text)!important;border:1px solid #EEF2F4!important;border-left:6px solid var(--s-primary)!important;border-radius:8px!important;box-shadow:0 2px 9px rgba(35,35,35,.08)!important;padding:14px 18px!important;height:auto!important;min-height:86px!important;}}
.open-card-button button:hover{{background:#F7FBFD!important;border-color:#C6E0EC!important;color:var(--s-text)!important;}}
.info-card,.tar-edit-card{{background:#fff;border-radius:8px;padding:12px 14px;margin:10px 0 12px 0;box-shadow:0 2px 9px rgba(35,35,35,.08);border:1px solid #EEF2F4;border-left:6px solid var(--s-primary);}}
.info-card-meta{{color:var(--s-grey);font-size:13px;}}
.tar-header-one-line{{display:flex;align-items:center;justify-content:space-between;gap:10px;width:100%;white-space:nowrap;}}
.tar-title-inline{{font-size:15px;font-weight:700;color:var(--s-primary-dark);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;min-width:0;}}
.tar-right-inline{{display:flex;align-items:center;gap:10px;flex-shrink:0;font-size:13px;font-weight:700;color:var(--s-text);}}
.tar-pencil{{font-size:16px;color:var(--s-primary-dark);}}
.progress-preview-grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:8px 0 2px 0;}}
.progress-preview{{background:#F7FBFD;border:1px solid #E2EBF0;border-radius:8px;padding:8px 10px;min-height:58px;}}
.progress-preview-title{{font-size:11px;font-weight:700;color:var(--s-grey);margin-bottom:6px;}}
.segment-row{{display:flex;gap:3px;align-items:center;}}
.segment-box{{height:9px;flex:1;border-radius:999px;background:#D9E3E8;}}
.segment-on{{background:var(--s-primary);}}
.pill-row{{display:flex;gap:4px;flex-wrap:wrap;}}
.mini-pill{{font-size:11px;border-radius:999px;padding:3px 6px;background:#E8EEF2;color:#53565A;font-weight:700;}}
.mini-pill-active{{background:var(--s-primary);color:#fff;}}
.bar-thin{{height:8px;border-radius:999px;background:#E0E2E3;overflow:hidden;}}
.bar-thin-inner{{height:100%;border-radius:999px;background:var(--s-primary);}}
.kpi-card{{background:#fff;border-radius:8px;padding:18px 20px;box-shadow:0 2px 9px rgba(35,35,35,.08);border-top:4px solid var(--s-primary);min-height:112px;}}
.kpi-label{{color:var(--s-grey);font-size:13px;font-weight:700;text-transform:uppercase;}}
.kpi-value{{font-size:34px;line-height:42px;color:var(--s-text);font-weight:700;margin-top:8px;}}
.s-progress{{width:100%;background:#E0E2E3;border-radius:999px;overflow:hidden;height:28px;margin:6px 0 16px 0;}}
.s-progress-inner{{height:100%;border-radius:999px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;color:#fff;min-width:38px;}}
.help-box{{background:var(--s-light-blue);border:1px solid var(--s-primary-dark);border-radius:4px;padding:14px 16px;}}
.help-box-title{{color:var(--s-primary-dark);font-weight:700;margin-bottom:4px;}}
.empty-state{{background:#fff;border-radius:8px;padding:46px 28px;text-align:center;border:1px dashed #C6E0EC;box-shadow:0 2px 9px rgba(35,35,35,.06);}}
.empty-icon{{height:85px;width:85px;border-radius:50%;background:#C6E0EC;color:var(--s-primary-dark);display:inline-flex;align-items:center;justify-content:center;font-size:34px;font-weight:700;margin-bottom:20px;}}
.streamlit-expanderHeader,[data-testid="stExpander"] summary{{font-family:'Montserrat',Arial,sans-serif!important;font-weight:700!important;color:var(--s-text)!important;line-height:24px!important;min-height:36px!important;}}

.progress-segments-only{background:#F7FBFD;border:1px solid #E2EBF0;border-radius:8px;padding:8px 10px;margin:8px 0 8px 0;}
.segment-row-large .segment-box{height:10px;}
.segment-percent{margin-left:8px;font-size:13px;color:var(--s-text);white-space:nowrap;}
.tar-card-inner{width:100%;}
.pencil-expander [data-testid="stExpander"] summary{min-height:30px!important;}

@media(max-width:900px){{.progress-preview-grid{{grid-template-columns:1fr 1fr;}}}}
@media(max-width:620px){{.progress-preview-grid{{grid-template-columns:1fr;}}.tar-header-one-line{{white-space:normal;}}}}
</style>
""", unsafe_allow_html=True)

inject_css()

# ============================================================
# SUPABASE
# ============================================================

def clean_supabase_url(url):
    if not url:
        return ""
    value = str(url).strip().rstrip("/")
    if value.endswith("/rest/v1"):
        value = value[:-8]
    return value


def get_secret_value(key, default=""):
    try:
        return st.secrets.get(key, default)
    except Exception:
        return os.environ.get(key, default)


@st.cache_resource(show_spinner=False)
def get_supabase_client():
    url = clean_supabase_url(get_secret_value("SUPABASE_URL", ""))
    key = get_secret_value("SUPABASE_KEY", "")
    if not url or not key:
        return None
    return create_client(url, key)

supabase = get_supabase_client()
if supabase is None:
    st.error(t("supabase_error"))
    st.stop()


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def s_select(table, columns="*"):
    return supabase.table(table).select(columns)


def s_data(response):
    return response.data if hasattr(response, "data") and response.data is not None else []


def db_error_message(err):
    return str(err)

# ============================================================
# AUTH LEGACY
# ============================================================

def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16)
    if isinstance(salt, str):
        salt = bytes.fromhex(salt)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120000)
    return salt.hex(), digest.hex()


def verify_password(password, stored_password, stored_salt=None):
    if stored_salt is None or stored_salt == "":
        return password == stored_password
    try:
        _, digest = hash_password(password, stored_salt)
        return digest == stored_password
    except Exception:
        return False


def get_user(username):
    data = s_data(s_select("usuaris", "username, password, password_salt, language, created_at, last_login").eq("username", username).limit(1).execute())
    return data[0] if data else None


def create_user(username, password, language):
    if get_user(username):
        return False
    salt, digest = hash_password(password)
    supabase.table("usuaris").insert({"username": username, "password": digest, "password_salt": salt, "language": language, "created_at": now_iso(), "last_login": None}).execute()
    return True


def migrate_plain_password(username, password):
    salt, digest = hash_password(password)
    supabase.table("usuaris").update({"password": digest, "password_salt": salt}).eq("username", username).execute()


def update_user_login(username):
    supabase.table("usuaris").update({"last_login": now_iso()}).eq("username", username).execute()

# ============================================================
# NOTES
# ============================================================

def unpack_notes(raw):
    if not raw:
        return "", {}
    if isinstance(raw, str) and raw.startswith(NOTES_PREFIX):
        try:
            obj = json.loads(raw[len(NOTES_PREFIX):])
            return obj.get("br_notes", "") or "", obj.get("tar_notes", {}) or {}
        except Exception:
            return "", {}
    return raw, {}


def pack_notes(br_notes, tar_notes):
    return NOTES_PREFIX + json.dumps({"br_notes": br_notes or "", "tar_notes": tar_notes or {}}, ensure_ascii=False)

# ============================================================
# MESOS
# ============================================================

def get_month_key(lang=None):
    now = datetime.now()
    return f"{now.year}-{now.month:02d}"


def parse_month_to_canonical(month_text):
    if not month_text:
        return get_month_key()
    value = str(month_text).strip()
    if re.match(r"^\d{4}-\d{2}$", value):
        return value
    parts = value.split(" ")
    if len(parts) >= 2:
        month_name = parts[0]
        year = parts[-1]
        if year.isdigit():
            for lang in ("ca", "es"):
                if month_name in TRANS[lang]["months"]:
                    return f"{int(year):04d}-{TRANS[lang]['months'].index(month_name)+1:02d}"
    return value


def month_display(month_key, lang=None):
    lang = lang or st.session_state.get("idioma", "ca")
    canonical = parse_month_to_canonical(month_key)
    if re.match(r"^\d{4}-\d{2}$", canonical):
        year, month = canonical.split("-")
        idx = int(month) - 1
        if 0 <= idx < 12:
            return f"{TRANS[lang]['months'][idx]} {year}"
    return str(month_key)


def month_aliases(month_key):
    canonical = parse_month_to_canonical(month_key)
    aliases = [canonical]
    if re.match(r"^\d{4}-\d{2}$", canonical):
        year, month = canonical.split("-")
        idx = int(month) - 1
        if 0 <= idx < 12:
            aliases.append(f"{TRANS['ca']['months'][idx]} {year}")
            aliases.append(f"{TRANS['es']['months'][idx]} {year}")
    return list(dict.fromkeys(aliases))


def next_month(month_text, target_lang=None):
    canonical = parse_month_to_canonical(month_text)
    if not re.match(r"^\d{4}-\d{2}$", canonical):
        return get_month_key()
    year, month = canonical.split("-")
    year = int(year)
    month = int(month)
    if month == 12:
        return f"{year + 1}-01"
    return f"{year:04d}-{month + 1:02d}"

# ============================================================
# MICROSOFT PREPARAT PER A FUTUR, NO VISIBLE
# ============================================================

def st_user_dict():
    try:
        return st.user.to_dict()
    except Exception:
        try:
            return dict(st.user)
        except Exception:
            return {}


def microsoft_user_email():
    user_info = st_user_dict()
    for key in ["email", "preferred_username", "upn", "mail", "unique_name"]:
        value = user_info.get(key)
        if value and "@" in str(value):
            return str(value).strip().lower()
    return ""


def microsoft_user_name():
    user_info = st_user_dict()
    for key in ["name", "given_name", "preferred_username", "email"]:
        value = user_info.get(key)
        if value:
            return str(value)
    return microsoft_user_email()


def is_allowed_email(email):
    return str(email or "").lower().endswith(ALLOWED_EMAIL_DOMAIN)


def migrate_existing_user_data(email):
    email = str(email or "").lower().strip()
    aliases = USER_EMAIL_MIGRATION.get(email, [])
    local_part = email.split("@")[0] if "@" in email else email
    aliases = list(dict.fromkeys([local_part, email] + aliases))
    for old_username in aliases:
        if old_username and old_username != email:
            for table, payload in [("big_rocks", {"username": email, "updated_at": now_iso()}), ("mesos_tancats", {"username": email}), ("usuaris", {"username": email, "last_login": now_iso()})]:
                try:
                    supabase.table(table).update(payload).eq("username", old_username).execute()
                except Exception:
                    pass


def ensure_microsoft_user_profile(email):
    email = str(email or "").lower().strip()
    if not email:
        return
    try:
        existing = get_user(email)
        if existing:
            supabase.table("usuaris").update({"last_login": now_iso(), "language": st.session_state.get("idioma", "ca")}).eq("username", email).execute()
        else:
            supabase.table("usuaris").insert({"username": email, "password": "MICROSOFT_LOGIN_DISABLED", "password_salt": "", "language": st.session_state.get("idioma", "ca"), "created_at": now_iso(), "last_login": now_iso()}).execute()
    except Exception:
        pass


def admin_users():
    raw = str(get_secret_value("ADMIN_USERS", "marc.llopis@sorigue.com,xavier.llopis@sorigue.com,marc.llopis,Xavier.llopis"))
    return [x.strip().lower() for x in raw.split(",") if x.strip()]


def is_admin_user(username):
    return str(username or "").strip().lower() in admin_users()


def list_users():
    return s_data(s_select("usuaris", "username, language, created_at, last_login").order("username").execute())

# ============================================================
# UI HELPERS
# ============================================================

def progress_color(progress):
    progress = int(progress or 0)
    if progress <= 25:
        return ERROR
    if progress <= 50:
        return WARNING
    if progress <= 75:
        return PRIMARY
    return SUCCESS


def progress_bar(progress, label=None):
    progress = int(progress or 0)
    color = progress_color(progress)
    label_text = label if label else f"{progress}%"
    st.markdown(f"""<div class="s-progress"><div class="s-progress-inner" style="width:{max(progress,4)}%;background:{color};">{label_text}</div></div>""", unsafe_allow_html=True)


def status_dot(progress):
    progress = int(progress or 0)
    if progress == 100:
        return "🟢"
    if progress >= 75:
        return "🔵"
    if progress >= 50:
        return "🟡"
    if progress >= 25:
        return "🟠"
    return "🔴"


def progress_radio_label(value):
    colors = {0: "🔴", 25: "🟠", 50: "🟡", 75: "🔵", 100: "🟢"}
    return f"{colors.get(int(value), '⚪')} {int(value)}%"


def progress_preview_html(progress):
    progress = int(progress or 0)
    active_segments = progress // 25
    segments = "".join([
        f"<span class='segment-box {'segment-on' if i <= active_segments and progress > 0 else ''}'></span>"
        for i in range(1, 5)
    ])
    return f"""
    <div class="progress-segments-only">
        <div class="segment-row segment-row-large">{segments}<strong class="segment-percent">{status_dot(progress)} {progress}%</strong></div>
    </div>
    """


def logo_for_login():
    return '<div class="login-logo-text">sorigué</div>'


def logo_for_sidebar():
    return '<div class="sidebar-logo-text">sorigué</div>'


def kpi_card(label, value):
    st.markdown(f"<div class='kpi-card'><div class='kpi-label'>{label}</div><div class='kpi-value'>{value}</div></div>", unsafe_allow_html=True)

# ============================================================
# DADES
# ============================================================

def get_brs(username, month):
    query = s_select("big_rocks", "id, nom, persones, reunions, notes_progres, pregunta, passos").eq("username", username)
    aliases = month_aliases(month)
    query = query.in_("mes", aliases) if len(aliases) > 1 else query.eq("mes", aliases[0])
    return s_data(query.order("id").execute())


def get_all_tars_for_brs(br_ids):
    if not br_ids:
        return []
    return s_data(s_select("tars", "id, id_br, num, descripcio, progres, estat").in_("id_br", br_ids).eq("estat", "Actiu").order("id").execute())


def group_tars_by_br(tars):
    grouped = {}
    for tar in tars:
        grouped.setdefault(tar.get("id_br"), []).append(tar)
    return grouped


def get_months(username):
    rows = s_data(s_select("big_rocks", "id, mes").eq("username", username).order("id", desc=True).execute())
    seen = []
    for row in rows:
        mes = parse_month_to_canonical(row.get("mes"))
        if mes and mes not in seen:
            seen.append(mes)
    return seen


def month_is_closed(username, month):
    query = s_select("mesos_tancats", "username, mes").eq("username", username)
    aliases = month_aliases(month)
    query = query.in_("mes", aliases) if len(aliases) > 1 else query.eq("mes", aliases[0])
    return len(s_data(query.limit(1).execute())) > 0


def close_month(username, month):
    supabase.table("mesos_tancats").upsert({"username": username, "mes": parse_month_to_canonical(month), "closed_at": now_iso()}).execute()


def unlock_month(username, month):
    aliases = month_aliases(month)
    query = supabase.table("mesos_tancats").delete().eq("username", username)
    query = query.in_("mes", aliases) if len(aliases) > 1 else query.eq("mes", aliases[0])
    query.execute()


def stats_from_tars(tars):
    total = len(tars)
    completed = sum(1 for tar in tars if int(tar.get("progres") or 0) == 100)
    in_progress = sum(1 for tar in tars if 0 < int(tar.get("progres") or 0) < 100)
    pending = sum(1 for tar in tars if int(tar.get("progres") or 0) == 0)
    avg = int(sum(int(tar.get("progres") or 0) for tar in tars) / total) if total else 0
    return {"total": total, "completed": completed, "in_progress": in_progress, "pending": pending, "avg": avg}


def create_bigrock(username, month, nom, persones, reunions, tar_descs, br_notes, pregunta, passos):
    res = supabase.table("big_rocks").insert({"username": username, "mes": parse_month_to_canonical(month), "nom": nom, "persones": persones, "reunions": reunions, "notes_progres": pack_notes(br_notes, {}), "pregunta": pregunta, "passos": passos, "created_at": now_iso(), "updated_at": now_iso()}).execute()
    data = s_data(res)
    if not data:
        return None
    br_id = data[0]["id"]
    rows = [{"id_br": br_id, "num": f"TAR {i}", "descripcio": desc.strip(), "progres": 0, "estat": "Actiu", "created_at": now_iso(), "updated_at": now_iso()} for i, desc in enumerate(tar_descs, start=1) if desc.strip()]
    if rows:
        supabase.table("tars").insert(rows).execute()
    return br_id


def save_bigrock_form(br_id, raw_current_notes, br_notes, pregunta, passos, tar_updates, tar_note_updates):
    _, existing_tar_notes = unpack_notes(raw_current_notes)
    for tar_id, note in tar_note_updates.items():
        existing_tar_notes[str(tar_id)] = note or ""
    supabase.table("big_rocks").update({"notes_progres": pack_notes(br_notes, existing_tar_notes), "pregunta": pregunta, "passos": passos, "updated_at": now_iso()}).eq("id", br_id).execute()
    for tar_id, payload in tar_updates.items():
        supabase.table("tars").update({"descripcio": payload.get("descripcio", ""), "progres": int(payload.get("progres", 0)), "updated_at": now_iso()}).eq("id", tar_id).execute()

# ============================================================
# STATE
# ============================================================

def remember_language(lang):
    if lang not in LANG_OPTIONS:
        lang = "ca"
    st.session_state.idioma = lang
    st.session_state.last_language = lang
    try:
        st.query_params["lang"] = lang
    except Exception:
        pass


def change_language():
    selected = st.session_state.get("idioma_selector", "ca")
    remember_language(selected)
    username = st.session_state.get("usuari_actual")
    if username:
        try:
            supabase.table("usuaris").update({"language": selected}).eq("username", username).execute()
        except Exception:
            pass


def change_login_language():
    remember_language(st.session_state.get("login_lang_selector", "ca"))


def toggle_bigrock(br_id):
    current = st.session_state.get("open_br_id")
    current = str(current) if current is not None else None
    target = str(br_id)
    st.session_state.open_br_id = None if current == target else target


def initial_language():
    try:
        qp_lang = st.query_params.get("lang")
        if isinstance(qp_lang, list):
            qp_lang = qp_lang[0]
        if qp_lang in LANG_OPTIONS:
            return qp_lang
    except Exception:
        pass
    return st.session_state.get("last_language", "ca")

if "usuari_actual" not in st.session_state:
    st.session_state.usuari_actual = None
if "idioma" not in st.session_state:
    st.session_state.idioma = initial_language()
if "last_language" not in st.session_state:
    st.session_state.last_language = st.session_state.idioma
if "pantalla" not in st.session_state:
    st.session_state.pantalla = "dashboard"
if "mostrar_formulari_br" not in st.session_state:
    st.session_state.mostrar_formulari_br = False
if "mes_actual" not in st.session_state:
    st.session_state.mes_actual = get_month_key(st.session_state.idioma)
else:
    st.session_state.mes_actual = parse_month_to_canonical(st.session_state.mes_actual)
if "open_br_id" not in st.session_state:
    st.session_state.open_br_id = None

# ============================================================
# LOGIN
# ============================================================

if st.session_state.usuari_actual is None:
    left, center, right = st.columns([1, 1.35, 1])
    with center:
        st.markdown(f"""<div style="background:{PRIMARY};border-radius:10px;padding:36px 38px 34px 38px;margin-top:32px;box-shadow:0 3px 14px rgba(35,35,35,.12);">{logo_for_login()}<div style="color:#FFFFFF;font-size:28px;line-height:34px;font-weight:700;text-align:center;">{t('login_title')}</div><div style="color:#E7F2F7;font-size:14px;line-height:21px;text-align:center;margin-top:8px;">{t('login_subtitle')}</div></div>""", unsafe_allow_html=True)
        st.write("")
        st.selectbox(t("lang_login"), options=["ca", "es"], index=0 if st.session_state.idioma == "ca" else 1, format_func=lang_label, key="login_lang_selector", on_change=change_login_language)

        # Microsoft queda ocult fins que estigui habilitat, però si hi ha una sessió vàlida ja creada, la respecta.
        if MICROSOFT_LOGIN_ENABLED and hasattr(st, "user") and getattr(st.user, "is_logged_in", False):
            email = microsoft_user_email()
            if is_allowed_email(email):
                migrate_existing_user_data(email)
                ensure_microsoft_user_profile(email)
                st.session_state.usuari_actual = email
                st.session_state.microsoft_user_name = microsoft_user_name()
                st.session_state.pantalla = "dashboard"
                st.session_state.open_br_id = None
                st.rerun()

        st.subheader(t("legacy_login"))
        tab1, tab2 = st.tabs([t("login_tab"), t("reg_tab")])
        with tab1:
            with st.form("legacy_login_form"):
                usuari = st.text_input(t("email_user"), placeholder="usuario@sorigue.com")
                contrasenya = st.text_input(t("pwd"), type="password")
                submitted = st.form_submit_button(t("enter"), type="primary", use_container_width=True)
                if submitted:
                    username_clean = usuari.strip()
                    if not username_clean or not contrasenya.strip():
                        st.error(t("required_fields"))
                    else:
                        try:
                            user = get_user(username_clean)
                            if user and verify_password(contrasenya, user.get("password"), user.get("password_salt")):
                                st.session_state.usuari_actual = username_clean
                                st.session_state.microsoft_user_name = username_clean
                                if user.get("language") in LANG_OPTIONS:
                                    remember_language(user.get("language"))
                                update_user_login(username_clean)
                                if not user.get("password_salt"):
                                    migrate_plain_password(username_clean, contrasenya)
                                st.session_state.pantalla = "dashboard"
                                st.session_state.open_br_id = None
                                st.rerun()
                            else:
                                st.error(t("err_login"))
                        except Exception as e:
                            st.error(db_error_message(e))
        with tab2:
            with st.form("legacy_register_form"):
                nou_usuari = st.text_input(t("new_usr"), placeholder="usuario@sorigue.com")
                nova_contra = st.text_input(t("pwd"), type="password")
                nou_idioma = st.selectbox(t("lang_reg"), options=["ca", "es"], index=0 if st.session_state.idioma == "ca" else 1, format_func=lang_label)
                submitted = st.form_submit_button(t("register"), type="primary", use_container_width=True)
                if submitted:
                    username_new = nou_usuari.strip().lower()
                    if not username_new or not nova_contra.strip():
                        st.error(t("required_fields"))
                    elif not username_new.endswith(ALLOWED_EMAIL_DOMAIN):
                        st.error(t("corp_email_required"))
                    else:
                        try:
                            ok = create_user(username_new, nova_contra, nou_idioma)
                            if ok:
                                st.success(t("succ_reg"))
                            else:
                                st.error(t("err_reg"))
                        except Exception as e:
                            st.error(db_error_message(e))
    st.stop()

# ============================================================
# SIDEBAR
# ============================================================

USUARI = st.session_state.usuari_actual
IS_ADMIN = is_admin_user(USUARI)

with st.sidebar:
    st.markdown(logo_for_sidebar(), unsafe_allow_html=True)
    st.markdown("<div class='sidebar-app-title'>BIG ROCKS</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sidebar-app-subtitle'>{t('login_subtitle')}</div>", unsafe_allow_html=True)
    badge = f"<div class='sidebar-pill'>{t('admin_badge')}</div>" if IS_ADMIN else "<div class='sidebar-pill'>Persona</div>"
    shown_name = st.session_state.get("microsoft_user_name", USUARI)
    st.markdown(f"""<div class="sidebar-status-card">{badge}<div class="sidebar-white" style="font-size:14px;margin-top:10px;font-weight:500;">{t('conn_as')}</div><div class="sidebar-white" style="font-size:16px;margin-top:2px;font-weight:700;">{safe_html(shown_name)}<br><span style="font-size:12px;font-weight:500;opacity:.88;">{safe_html(USUARI)}</span></div></div>""", unsafe_allow_html=True)
    st.selectbox(t("lang"), ["ca", "es"], index=0 if st.session_state.idioma == "ca" else 1, format_func=lang_label, key="idioma_selector", on_change=change_language)
    mesos_disponibles = get_months(USUARI)
    mes_ini = get_month_key(st.session_state.idioma)
    if mes_ini not in mesos_disponibles:
        mesos_disponibles.insert(0, mes_ini)
    st.session_state.mes_actual = parse_month_to_canonical(st.session_state.mes_actual)
    if st.session_state.mes_actual not in mesos_disponibles:
        st.session_state.mes_actual = mes_ini
    mes_seleccionat = st.selectbox(t("nav_months"), mesos_disponibles, index=mesos_disponibles.index(st.session_state.mes_actual), key="mes_selector", format_func=lambda x: month_display(x, st.session_state.idioma))
    mes_seleccionat = parse_month_to_canonical(mes_seleccionat)
    if mes_seleccionat != st.session_state.mes_actual:
        st.session_state.open_br_id = None
    st.session_state.mes_actual = mes_seleccionat
    MES = st.session_state.mes_actual
    es_tancat = month_is_closed(USUARI, MES)
    if es_tancat:
        st.markdown(f"<div class='sidebar-status-card'><div class='sidebar-white' style='font-weight:700;'>{t('status_closed')}</div><div class='sidebar-white' style='margin-top:5px;'>{t('closed_month')}</div></div>", unsafe_allow_html=True)
        if st.button(t("unlock"), use_container_width=True):
            unlock_month(USUARI, MES)
            st.rerun()
    else:
        st.markdown(f"<div class='sidebar-status-card'><div class='sidebar-white' style='font-weight:700;'>{t('status_open')}</div><div class='sidebar-white' style='margin-top:5px;'>{t('open_month')}</div></div>", unsafe_allow_html=True)
    if IS_ADMIN:
        if st.button(t("admin_panel"), use_container_width=True):
            st.session_state.pantalla = "admin"
            st.rerun()
    st.markdown("<div style='height:34px;'></div>", unsafe_allow_html=True)
    if st.button(t("logout"), use_container_width=True):
        last_lang = st.session_state.get("idioma", "ca")
        for key in ["usuari_actual", "pantalla", "mostrar_formulari_br", "open_br_id"]:
            if key in st.session_state:
                del st.session_state[key]
        remember_language(last_lang)
        st.rerun()

# ============================================================
# PANTALLES
# ============================================================

def render_admin_panel():
    if not IS_ADMIN:
        st.error("No autoritzat")
        return
    st.title(t("admin_panel"))
    with st.container(border=True):
        st.subheader(t("admin_users"))
        users = list_users()
        if users:
            st.dataframe(pd.DataFrame(users), use_container_width=True, hide_index=True)
        else:
            st.info(t("admin_no_users"))
    with st.container(border=True):
        if st.button(t("force_migration"), type="primary"):
            for email in USER_EMAIL_MIGRATION:
                migrate_existing_user_data(email)
                ensure_microsoft_user_profile(email)
            st.success(t("migration_ok"))
    if st.button(t("back")):
        st.session_state.pantalla = "dashboard"
        st.rerun()


def render_report(title, allow_close=False):
    st.title(f"{title} · {month_display(MES)}")
    brs = get_brs(USUARI, MES)
    tars = get_all_tars_for_brs([br["id"] for br in brs])
    tars_by_br = group_tars_by_br(tars)
    tars_completats, tars_pendents, tars_en_curs = [], [], []
    sumatori_progres, total_tars = 0, 0
    for br in brs:
        for tar in tars_by_br.get(br["id"], []):
            desc = tar.get("descripcio") or ""
            progres = int(tar.get("progres") or 0)
            sumatori_progres += progres
            total_tars += 1
            if progres == 100:
                tars_completats.append((br.get("nom") or "", desc))
            elif progres == 0:
                tars_pendents.append((br.get("nom") or "", desc, progres))
            else:
                tars_en_curs.append((br.get("nom") or "", desc, progres))
    compliment_global = int(sumatori_progres / total_tars) if total_tars else 0
    st.markdown(f"### {t('global_comp')}")
    progress_bar(compliment_global, f"{compliment_global}%")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.success(t("successes"))
        for nom, desc in tars_completats or []:
            st.markdown(f"- **{nom}** → {desc}")
    with c2:
        st.info(t("in_progress"))
        for nom, desc, progres in tars_en_curs or []:
            st.markdown(f"- **{nom}** → {desc} ({progres}%)")
    with c3:
        st.warning(t("carry_over"))
        for nom, desc, progres in tars_pendents or []:
            st.markdown(f"- **{nom}** → {desc} ({progres}%)")
    def confirm_month_close():
        close_month(USUARI, MES)
        nou_mes = next_month(MES, st.session_state.idioma)
        for br in brs:
            pendents = [tar for tar in tars_by_br.get(br["id"], []) if int(tar.get("progres") or 0) < 100]
            if pendents:
                existing_notes, _ = unpack_notes(br.get("notes_progres"))
                res = supabase.table("big_rocks").insert({"username": USUARI, "mes": nou_mes, "nom": br.get("nom") or "", "persones": br.get("persones") or "", "reunions": br.get("reunions") or "", "notes_progres": pack_notes(existing_notes, {}), "pregunta": br.get("pregunta") or "", "passos": br.get("passos") or "", "created_at": now_iso(), "updated_at": now_iso()}).execute()
                data = s_data(res)
                if data:
                    new_br_id = data[0]["id"]
                    rows = [{"id_br": new_br_id, "num": tar.get("num") or "TAR", "descripcio": tar.get("descripcio") or "", "progres": int(tar.get("progres") or 0), "estat": "Actiu", "created_at": now_iso(), "updated_at": now_iso()} for tar in pendents]
                    if rows:
                        supabase.table("tars").insert(rows).execute()
        st.session_state.mes_actual = nou_mes
        st.session_state.pantalla = "dashboard"
        st.session_state.open_br_id = None
        st.rerun()
    st.write("")
    if allow_close:
        c1, c2, _ = st.columns([1, 2, 1])
        with c1:
            if st.button(t("cancel"), use_container_width=True):
                st.session_state.pantalla = "dashboard"
                st.rerun()
        with c2:
            st.button(t("confirm_close"), on_click=confirm_month_close, type="primary", use_container_width=True)
    else:
        if st.button(t("back")):
            st.session_state.pantalla = "dashboard"
            st.rerun()

# ============================================================
# DASHBOARD
# ============================================================

MES = st.session_state.mes_actual
es_tancat = month_is_closed(USUARI, MES)

if st.session_state.pantalla == "admin":
    render_admin_panel()
elif st.session_state.pantalla == "informe":
    render_report(t("report_title"), allow_close=False)
elif st.session_state.pantalla == "resum":
    render_report(t("summary"), allow_close=True)
else:
    brs = get_brs(USUARI, MES)
    all_tars = get_all_tars_for_brs([br["id"] for br in brs])
    tars_by_br = group_tars_by_br(all_tars)
    all_stats = stats_from_tars(all_tars)
    br_count = len(brs)
    completed = all_stats["completed"]
    pending = all_stats["pending"] + all_stats["in_progress"]
    avg = all_stats["avg"]
    col_title, col_help = st.columns([2.25, 1])
    with col_title:
        st.title(f"Big Rocks · {month_display(MES)}")
    with col_help:
        st.markdown(f"<div class='help-box'><div class='help-box-title'>{t('help_title')}</div><div style='font-size:13px;color:#232323;'>{t('help_body')}</div></div>", unsafe_allow_html=True)
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
    a1, a2, a3, _ = st.columns([1.45, 1.45, 1.25, 2.85])
    with a1:
        if not es_tancat and st.button(t("eval_close"), type="primary", use_container_width=True):
            st.session_state.pantalla = "resum"
            st.rerun()
    with a2:
        if st.button(t("eval_no_close"), use_container_width=True):
            st.session_state.pantalla = "informe"
            st.rerun()
    with a3:
        if st.button(t("collapse_all"), use_container_width=True):
            st.session_state.open_br_id = None
            st.rerun()
    st.write("")
    if not brs:
        st.markdown(f"<div class='empty-state'><div class='empty-icon'>BR</div><h2>{t('no_br_title')}</h2><p style='color:#53565A;font-size:16px;'>{t('no_br_body')}</p></div>", unsafe_allow_html=True)
        if not es_tancat:
            _, cta_col, _ = st.columns([1, 1, 1])
            with cta_col:
                if st.button(t("empty_cta"), type="primary", use_container_width=True):
                    st.session_state.mostrar_formulari_br = True
    else:
        for br in brs:
            br_id = br["id"]
            tar_list = tars_by_br.get(br_id, [])
            stats = stats_from_tars(tar_list)
            progres_mitja = stats["avg"]
            is_open = str(st.session_state.get("open_br_id")) == str(br_id)
            br_notes, tar_notes = unpack_notes(br.get("notes_progres"))
            icon = "▼" if is_open else "▶"
            label = f"{icon} {br.get('nom') or ''}\n{status_dot(progres_mitja)} {progres_mitja}%   ·   {stats['total']} TARs   ·   {stats['completed']} completades   ·   {stats['in_progress']} en curs   ·   {stats['pending']} pendents"
            st.markdown('<div class="open-card-button">', unsafe_allow_html=True)
            st.button(label, key=f"card_br_{br_id}", use_container_width=True, on_click=toggle_bigrock, args=(br_id,))
            st.markdown('</div>', unsafe_allow_html=True)
            if not is_open:
                continue
            st.markdown(f"<div class='info-card'><div class='info-card-meta'><strong>{t('key_ppl')}:</strong> {safe_html(br.get('persones') or '-')} &nbsp;&nbsp;|&nbsp;&nbsp; <strong>{t('key_meet')}:</strong> {safe_html(br.get('reunions') or '-')}</div></div>", unsafe_allow_html=True)
            progress_bar(progres_mitja, f"{progres_mitja}%")
            with st.form(f"form_bigrock_{br_id}"):
                with st.expander(t("details"), expanded=False):
                    notes_key = f"notes_{br_id}"
                    preg_key = f"preg_{br_id}"
                    passos_key = f"passos_{br_id}"
                    st.text_area(t("prog"), value=br_notes, key=notes_key, disabled=es_tancat)
                    st.text_input(t("need"), value=br.get("pregunta") or "", key=preg_key, disabled=es_tancat)
                    st.text_input(t("next_steps"), value=br.get("passos") or "", key=passos_key, disabled=es_tancat)
                st.markdown("### TARs")
                tar_updates = {}
                tar_note_updates = {}
                for tar in tar_list:
                    tar_id = tar["id"]
                    progres = int(tar.get("progres") or 0)
                    progres = progres if progres in PROGRESS_OPTIONS else 0
                    desc_key = f"desc_{tar_id}"
                    prog_key = f"prog_{tar_id}"
                    edit_key = f"edit_{tar_id}"
                    note_key = f"tar_note_{tar_id}"
                    current_progress = int(st.session_state.get(prog_key, progres))
                    displayed_desc = st.session_state.get(desc_key, tar.get("descripcio") or "")
                    if not displayed_desc.strip():
                        displayed_desc = tar.get("num") or "TAR"
                    # Targeta real de Streamlit perquè tot quedi dins del rectangle i no surti cap línia buida.
                    with st.container(border=True):
                        c_title, c_progress, c_edit = st.columns([8.5, 2, 0.8], vertical_alignment="center")
                        with c_title:
                            st.markdown(f"<div class='tar-title-inline'>{safe_html(tar.get('num') or '')} · {safe_html(displayed_desc)}</div>", unsafe_allow_html=True)
                        with c_progress:
                            st.markdown(f"<div class='tar-right-inline'>{status_dot(current_progress)} {current_progress}%</div>", unsafe_allow_html=True)
                        with c_edit:
                            with st.expander("✏️", expanded=False):
                                st.text_input("", value=tar.get("descripcio") or "", key=desc_key, label_visibility="collapsed", disabled=es_tancat, placeholder=t("desc"))
                        st.radio(t("state"), options=PROGRESS_OPTIONS, format_func=progress_radio_label, index=PROGRESS_OPTIONS.index(progres), horizontal=True, key=prog_key, label_visibility="collapsed", disabled=es_tancat)
                        st.markdown(progress_preview_html(st.session_state.get(prog_key, current_progress)), unsafe_allow_html=True)
                        with st.expander(t("tar_notes"), expanded=False):
                            st.text_area(t("tar_notes"), value=tar_notes.get(str(tar_id), ""), key=note_key, disabled=es_tancat, placeholder=t("tar_notes_placeholder"), label_visibility="collapsed")
                    tar_updates[tar_id] = {"descripcio": st.session_state.get(desc_key, displayed_desc), "progres": st.session_state.get(prog_key, progres)}
                    tar_note_updates[tar_id] = st.session_state.get(note_key, tar_notes.get(str(tar_id), ""))
                submit_bigrock = st.form_submit_button(t("save_full_br"), type="primary", use_container_width=True, disabled=es_tancat)
                if submit_bigrock:
                    try:
                        save_bigrock_form(br_id, br.get("notes_progres"), st.session_state.get(notes_key, ""), st.session_state.get(preg_key, ""), st.session_state.get(passos_key, ""), tar_updates, tar_note_updates)
                        st.session_state.open_br_id = str(br_id)
                        st.success(t("saved"))
                        st.rerun()
                    except Exception as e:
                        st.error(db_error_message(e))
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
                with st.expander(t("details"), expanded=True):
                    br_notes_new = st.text_area(t("prog"), placeholder=t("prog"))
                    pregunta_new = st.text_input(t("need"), placeholder=t("need"))
                    passos_new = st.text_input(t("next_steps"), placeholder=t("next_steps"))
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
                        try:
                            new_id = create_bigrock(USUARI, MES, nou_nom.strip(), persones.strip(), reunions.strip(), [t1, t2, t3, t4], br_notes_new, pregunta_new, passos_new)
                            st.session_state.mostrar_formulari_br = False
                            st.session_state.open_br_id = str(new_id)
                            st.rerun()
                        except Exception as e:
                            st.error(db_error_message(e))
