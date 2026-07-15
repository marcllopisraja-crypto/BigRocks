
import hashlib
import html
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st
from supabase import create_client

# ============================================================
# BIG ROCKS - SORIGUE | APP.py V45
# Base V44 + optimitzacio de rendiment
# - Cache de consultes Supabase amb TTL curt
# - Menys consultes repetides per mes/estat/usuaris
# - Carrega de TARs consolidada i cache invalidada després de canvis
# - Crear BR amb 4 TARs inicials + afegir fins a 6
# - Editar / eliminar / duplicar BR i TARs
# - Tancament mensual amb traspas, recurrents i resum bilingue
# ============================================================

NOTES_PREFIX = "**BIGROCK_NOTES_JSON_V1**"
ALLOWED_EMAIL_DOMAIN = "@sorigue.com"
PRIMARY = "#009CDE"
PRIMARY_DARK = "#216D8C"
PRIMARY_HOVER = "#43B8ED"
LIGHT_BLUE = "#E7F2F7"
TEXT = "#232323"
GREY = "#53565A"
PROGRESS_OPTIONS = [0, 25, 50, 75, 100]
MAX_TARS_PER_BIGROCK = 6
INITIAL_TARS_ON_CREATE = 4
CACHE_TTL = 60
LANG_OPTIONS = {"ca": "🇦🇩 Català", "es": "🇪🇸 Español"}

USER_EMAIL_MIGRATION = {
    "marc.llopis@sorigue.com": ["marc.llopis", "Marc.llopis", "Marc Llopis", "marc"],
    "xavier.llopis@sorigue.com": ["xavier.llopis", "Xavier.llopis", "Xavier Llopis", "xavier"],
}

st.set_page_config(
    page_title="Big Rocks - Sorigué",
    layout="wide",
    page_icon="BR",
    initial_sidebar_state="expanded",
)

TRANS = {
    "ca": {
        "login_title": "Accés a la Plataforma",
        "login_subtitle": "Seguiment mensual dels teus Big Rocks i TARs",
        "legacy_login": "Accés amb usuari i contrasenya",
        "login_tab": "Iniciar sessió",
        "reg_tab": "Registrar usuari",
        "email_user": "Correu corporatiu",
        "remember_user": "Recordar usuari en aquest dispositiu",
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
        "unlock": "🔓 Reobrir mes",
        "delete_last_month": "🗑 Eliminar últim mes",
        "confirm_delete_last_month": "Confirmo que vull eliminar l'últim mes i totes les seves TARs",
        "deleted_last_month": "Últim mes eliminat correctament.",
        "logout": "Tancar sessió",
        "eval_close": "Avaluar i tancar mes",
        "eval_no_close": "Avaluar sense tancar",
        "collapse_all": "Contraure els BR",
        "active_brs": "Big Rocks actives",
        "completed_tars": "TARs completades",
        "pending_tars": "TARs pendents",
        "avg_progress": "Progrés mitjà",
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
        "state": "Compliment",
        "tar_notes": "Anotacions de la TAR",
        "tar_notes_placeholder": "Escriu observacions, acords, incidències o seguiment específic d'aquesta TAR...",
        "create_br": "Crear nova Big Rock",
        "config_br": "Configura la teva nova Big Rock",
        "title_br": "Títol de la Big Rock",
        "title_placeholder": "Ex. Reduir incidències crítiques de l'obra",
        "people_placeholder": "Ex. Xavier, Gerard, equip nord...",
        "meetings_placeholder": "Ex. Seguiment setmanal, comitè mensual...",
        "tar_placeholder": "Descriu una acció concreta i mesurable",
        "save": "Guardar Big Rock",
        "saved": "Canvis guardats.",
        "summary": "Resum de tancament",
        "report_title": "Informe de seguiment",
        "global_comp": "Compliment global",
        "auto_analysis_title": "Anàlisi automàtica del mes",
        "conclusion": "Conclusió",
        "according_to": "Segons aquest compliment",
        "close_prompt_title": "Mes tancat i nou mes obert",
        "close_prompt_transfer": "S'han traspassat",
        "close_prompt_question": "Vols crear més Big Rocks per al nou mes?",
        "continue": "Continuar",
        "confirm_close": "Confirmar tancament i crear mes següent",
        "back": "Tornar",
        "admin_panel": "⚙ Administració",
        "admin_badge": "Administrador",
        "admin_users": "Gestió d'usuaris",
        "admin_no_users": "No s'han trobat usuaris.",
        "force_migration": "Forçar migració usuaris antics",
        "migration_ok": "Migració executada.",
        "supabase_error": "No s'ha pogut connectar amb Supabase. Revisa SUPABASE_URL i SUPABASE_KEY a Streamlit Secrets.",
        "edit_br": "✏️ Editar Big Rock",
        "delete_br": "🗑 Eliminar Big Rock",
        "duplicate_br": "📋 Duplicar Big Rock",
        "confirm_delete_br": "Confirmo que vull eliminar aquesta Big Rock i totes les seves TARs",
        "br_deleted": "Big Rock eliminada correctament.",
        "br_duplicated": "Big Rock duplicada correctament.",
        "br_recurrent": "Big Rock recurrent",
        "min_one_tar": "Cal crear almenys una TAR per guardar la Big Rock.",
        "min_one_tar_delete": "No es pot eliminar aquesta TAR perquè una Big Rock ha de tenir almenys una TAR.",
        "max_tars_warning": "Aquesta Big Rock ja té 6 TARs. Es recomana partir la Big Rock en dues fases diferenciades per millorar el focus.",
        "add_tar": "➕ Afegir TAR",
        "new_tar": "Nova TAR",
        "delete_tar": "🗑 Eliminar TAR",
        "confirm_delete_tar": "Confirmo que vull eliminar aquesta TAR",
        "tar_added": "TAR afegida correctament.",
        "tar_deleted": "TAR eliminada correctament.",
        "save_br_changes": "Guardar canvis Big Rock",
        "recurrent_detected": "Big Rocks recurrents detectades",
        "reset_recurrent_hint": "Marca les Big Rocks recurrents que vols reiniciar al 0% quan es copiïn al mes següent.",
        "cache_note": "Versió optimitzada: les consultes habituals es cachegen durant 60 segons i s'invaliden quan fas canvis.",
        "months": ["Gener", "Febrer", "Març", "Abril", "Maig", "Juny", "Juliol", "Agost", "Setembre", "Octubre", "Novembre", "Desembre"],
    },
    "es": {
        "login_title": "Acceso a la Plataforma",
        "login_subtitle": "Seguimiento mensual de tus Big Rocks y TARs",
        "legacy_login": "Acceso con usuario y contraseña",
        "login_tab": "Iniciar sesión",
        "reg_tab": "Registrar usuario",
        "email_user": "Correo corporativo",
        "remember_user": "Recordar usuario en este dispositivo",
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
        "unlock": "🔓 Reabrir mes",
        "delete_last_month": "🗑 Eliminar último mes",
        "confirm_delete_last_month": "Confirmo que quiero eliminar el último mes y todas sus TARs",
        "deleted_last_month": "Último mes eliminado correctamente.",
        "logout": "Cerrar sesión",
        "eval_close": "Evaluar y cerrar mes",
        "eval_no_close": "Evaluar sin cerrar",
        "collapse_all": "Contraer BR",
        "active_brs": "Big Rocks activas",
        "completed_tars": "TARs completadas",
        "pending_tars": "TARs pendientes",
        "avg_progress": "Progreso medio",
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
        "state": "Cumplimiento",
        "tar_notes": "Anotaciones de la TAR",
        "tar_notes_placeholder": "Escribe observaciones, acuerdos, incidencias o seguimiento específico de esta TAR...",
        "create_br": "Crear nueva Big Rock",
        "config_br": "Configura tu nueva Big Rock",
        "title_br": "Título de la Big Rock",
        "title_placeholder": "Ej. Reducir incidencias críticas de la obra",
        "people_placeholder": "Ej. Xavier, Gerard, equipo norte...",
        "meetings_placeholder": "Ej. Seguimiento semanal, comité mensual...",
        "tar_placeholder": "Describe una acción concreta y medible",
        "save": "Guardar Big Rock",
        "saved": "Cambios guardados.",
        "summary": "Resumen de cierre",
        "report_title": "Informe de seguimiento",
        "global_comp": "Cumplimiento global",
        "auto_analysis_title": "Análisis automático del mes",
        "conclusion": "Conclusión",
        "according_to": "Según este cumplimiento",
        "close_prompt_title": "Mes cerrado y nuevo mes abierto",
        "close_prompt_transfer": "Se han traspasado",
        "close_prompt_question": "¿Quieres crear más Big Rocks para el nuevo mes?",
        "continue": "Continuar",
        "confirm_close": "Confirmar cierre y crear mes siguiente",
        "back": "Volver",
        "admin_panel": "⚙ Administración",
        "admin_badge": "Administrador",
        "admin_users": "Gestión de usuarios",
        "admin_no_users": "No se han encontrado usuarios.",
        "force_migration": "Forzar migración usuarios antiguos",
        "migration_ok": "Migración ejecutada.",
        "supabase_error": "No se ha podido conectar con Supabase. Revisa SUPABASE_URL y SUPABASE_KEY en Streamlit Secrets.",
        "edit_br": "✏️ Editar Big Rock",
        "delete_br": "🗑 Eliminar Big Rock",
        "duplicate_br": "📋 Duplicar Big Rock",
        "confirm_delete_br": "Confirmo que quiero eliminar esta Big Rock y todas sus TARs",
        "br_deleted": "Big Rock eliminada correctamente.",
        "br_duplicated": "Big Rock duplicada correctamente.",
        "br_recurrent": "Big Rock recurrente",
        "min_one_tar": "Hay que crear al menos una TAR para guardar la Big Rock.",
        "min_one_tar_delete": "No se puede eliminar esta TAR porque una Big Rock debe tener al menos una TAR.",
        "max_tars_warning": "Esta Big Rock ya tiene 6 TARs. Se recomienda dividir la Big Rock en dos fases diferenciadas para mejorar el foco.",
        "add_tar": "➕ Añadir TAR",
        "new_tar": "Nueva TAR",
        "delete_tar": "🗑 Eliminar TAR",
        "confirm_delete_tar": "Confirmo que quiero eliminar esta TAR",
        "tar_added": "TAR añadida correctamente.",
        "tar_deleted": "TAR eliminada correctamente.",
        "save_br_changes": "Guardar cambios Big Rock",
        "recurrent_detected": "Big Rocks recurrentes detectadas",
        "reset_recurrent_hint": "Marca las Big Rocks recurrentes que quieres reiniciar al 0% al copiarlas al mes siguiente.",
        "cache_note": "Versión optimizada: las consultas habituales se cachean durante 60 segundos y se invalidan cuando haces cambios.",
        "months": ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
    },
}


def t(key: str) -> str:
    lang = st.session_state.get("idioma", "ca")
    return TRANS.get(lang, TRANS["ca"]).get(key, key)


def lang_label(code: str) -> str:
    return LANG_OPTIONS.get(code, code)


def safe_html(value) -> str:
    return html.escape(str(value or ""))


def inject_css():
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');
html, body, [class*="css"] {{ font-family: 'Montserrat', sans-serif; }}
.stApp {{
    background:
        linear-gradient(180deg, #F7FBFD 0%, #EEF7FB 100%),
        radial-gradient(circle at 15% 20%, rgba(0,156,222,0.08), transparent 25%),
        linear-gradient(90deg, rgba(0,156,222,0.035) 1px, transparent 1px),
        linear-gradient(0deg, rgba(0,156,222,0.035) 1px, transparent 1px);
    background-size: auto, auto, 42px 42px, 42px 42px;
}}
[data-testid="stSidebar"] {{ background: {PRIMARY}; }}
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{ color: white; }}
[data-testid="stSidebar"] [data-baseweb="select"] span, [data-testid="stSidebar"] input {{ color: {TEXT} !important; }}
.sidebar-logo {{ font-size: 1.9rem; font-weight:700; color:white; letter-spacing:.02em; margin-bottom: .2rem; }}
.sidebar-title {{ font-weight:700; color:white; font-size:1.05rem; margin-bottom:.4rem; }}
.user-card {{ background:rgba(255,255,255,.15); border:1px solid rgba(255,255,255,.28); border-radius:12px; padding:12px; color:white; margin:10px 0 14px 0; }}
.br-card {{ background:white; border-left:7px solid {PRIMARY}; border-radius:14px; padding:14px 16px; box-shadow:0 2px 12px rgba(0,0,0,.07); margin:12px 0; }}
.br-head {{ display:flex; justify-content:space-between; align-items:center; gap:12px; }}
.br-title {{ font-size:1.05rem; font-weight:700; color:{TEXT}; }}
.br-meta {{ color:{GREY}; font-size:.85rem; margin-top:4px; }}
.kpi-card {{ background:white; border-left:6px solid {PRIMARY}; border-radius:14px; padding:14px; box-shadow:0 2px 12px rgba(0,0,0,.07); }}
.kpi-label {{ color:{GREY}; font-size:.85rem; }}
.kpi-value {{ color:{TEXT}; font-size:1.45rem; font-weight:700; margin-top:4px; }}
.br-progress-wrap {{ width:100%; background:#EAF4F8; border-radius:999px; overflow:hidden; height:10px; margin-top:9px; }}
.br-progress-fill {{ height:10px; background:{PRIMARY}; width: var(--w); }}
.tar-card {{ background:white; border:1px solid #E2EBF0; border-radius:14px; padding:0; box-shadow:0 1px 9px rgba(0,0,0,.06); margin:12px 0; overflow:hidden; }}
.tar-inner {{ display:flex; align-items:stretch; width:100%; }}
.tar-side {{ width:8px; background:{PRIMARY}; flex:0 0 8px; }}
.tar-content {{ padding:12px 14px; flex:1; }}
.tar-title-line {{ display:flex; align-items:center; justify-content:space-between; gap:8px; }}
.tar-title {{ font-weight:700; color:{PRIMARY_DARK}; }}
.tar-progress-value {{ font-weight:700; color:{PRIMARY_DARK}; white-space:nowrap; }}
.small-muted {{ color:{GREY}; font-size:.85rem; }}
.report-card {{ background:white; border-left:6px solid {PRIMARY}; border-radius:14px; padding:14px 16px; margin:12px 0; box-shadow:0 2px 12px rgba(0,0,0,.07); }}
.empty-state {{ background:white; border:1px dashed #B8DCEB; border-radius:18px; text-align:center; padding:34px 22px; margin-top:22px; }}
.stButton button {{ border-radius:8px !important; }}
.stSelectSlider [data-testid="stTickBar"] {{ color:{GREY}; }}
</style>
""", unsafe_allow_html=True)


inject_css()

# ============================================================
# SUPABASE + CACHE
# ============================================================


def clean_supabase_url(url: str) -> str:
    value = str(url or "").strip().rstrip("/")
    if value.endswith("/rest/v1"):
        value = value[:-8]
    return value


def get_secret_value(key: str, default: str = ""):
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


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def s_select(table: str, columns: str = "*"):
    return supabase.table(table).select(columns)


def s_data(response):
    return response.data if hasattr(response, "data") and response.data is not None else []


def db_error_message(err) -> str:
    return str(err)


def clear_data_cache():
    try:
        st.cache_data.clear()
    except Exception:
        pass

# ============================================================
# AUTH
# ============================================================


def hash_password(password: str, salt=None) -> Tuple[str, str]:
    if salt is None:
        salt = os.urandom(16)
    if isinstance(salt, str):
        salt = bytes.fromhex(salt)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120000)
    return salt.hex(), digest.hex()


def verify_password(password: str, stored_password: str, stored_salt: str = "") -> bool:
    if not stored_salt:
        return password == stored_password
    try:
        _, digest = hash_password(password, stored_salt)
        return digest == stored_password
    except Exception:
        return False


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def get_user_cached(username: str):
    data = s_data(
        s_select("usuaris", "username, password, password_salt, language, created_at, last_login")
        .eq("username", username)
        .limit(1)
        .execute()
    )
    return data[0] if data else None


def get_user(username: str):
    return get_user_cached(username)


def create_user(username: str, password: str, language: str) -> bool:
    if get_user(username):
        return False
    salt, digest = hash_password(password)
    supabase.table("usuaris").insert({
        "username": username,
        "password": digest,
        "password_salt": salt,
        "language": language,
        "created_at": now_iso(),
        "last_login": None,
    }).execute()
    clear_data_cache()
    return True


def migrate_plain_password(username: str, password: str):
    salt, digest = hash_password(password)
    supabase.table("usuaris").update({"password": digest, "password_salt": salt}).eq("username", username).execute()
    clear_data_cache()


def update_user_login(username: str):
    supabase.table("usuaris").update({"last_login": now_iso()}).eq("username", username).execute()
    clear_data_cache()

# ============================================================
# NOTES + MONTHS
# ============================================================


def unpack_notes(raw):
    if not raw:
        return "", {}, {}
    if isinstance(raw, str) and raw.startswith(NOTES_PREFIX):
        try:
            obj = json.loads(raw[len(NOTES_PREFIX):])
            return obj.get("br_notes", "") or "", obj.get("tar_notes", {}) or {}, obj.get("meta", {}) or {}
        except Exception:
            return "", {}, {}
    return raw, {}, {}


def pack_notes(br_notes, tar_notes, meta=None):
    return NOTES_PREFIX + json.dumps({"br_notes": br_notes or "", "tar_notes": tar_notes or {}, "meta": meta or {}}, ensure_ascii=False)


def br_is_recurrent(raw_notes) -> bool:
    _, _, meta = unpack_notes(raw_notes)
    return bool(meta.get("recurrent", False))


def get_month_key(lang=None):
    now = datetime.now()
    return f"{now.year:04d}-{now.month:02d}"


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
                    return f"{int(year):04d}-{TRANS[lang]['months'].index(month_name) + 1:02d}"
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


def next_month(month_text):
    canonical = parse_month_to_canonical(month_text)
    if not re.match(r"^\d{4}-\d{2}$", canonical):
        return get_month_key()
    year, month = map(int, canonical.split("-"))
    if month == 12:
        return f"{year + 1}-01"
    return f"{year:04d}-{month + 1:02d}"

# ============================================================
# DATA QUERIES - CACHED
# ============================================================


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def get_brs_cached(username: str, month: str):
    aliases = month_aliases(month)
    query = s_select("big_rocks", "id, nom, persones, reunions, notes_progres, pregunta, passos, mes").eq("username", username)
    query = query.in_("mes", aliases) if len(aliases) > 1 else query.eq("mes", aliases[0])
    return s_data(query.order("id").execute())


def get_brs(username: str, month: str):
    return get_brs_cached(username, parse_month_to_canonical(month))


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def get_all_tars_for_brs_cached(br_ids_tuple: tuple):
    br_ids = list(br_ids_tuple)
    if not br_ids:
        return []
    return s_data(
        s_select("tars", "id, id_br, num, descripcio, progres, estat")
        .in_("id_br", br_ids)
        .eq("estat", "Actiu")
        .order("id")
        .execute()
    )


def get_all_tars_for_brs(br_ids: List[int]):
    return get_all_tars_for_brs_cached(tuple(br_ids))


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def get_months_cached(username: str):
    rows = s_data(s_select("big_rocks", "id, mes").eq("username", username).order("id", desc=True).execute())
    seen = []
    for row in rows:
        mes = parse_month_to_canonical(row.get("mes"))
        if mes and mes not in seen:
            seen.append(mes)
    return seen


def get_months(username: str):
    return get_months_cached(username)


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def month_is_closed_cached(username: str, month: str) -> bool:
    aliases = month_aliases(month)
    query = s_select("mesos_tancats", "username, mes").eq("username", username)
    query = query.in_("mes", aliases) if len(aliases) > 1 else query.eq("mes", aliases[0])
    return len(s_data(query.limit(1).execute())) > 0


def month_is_closed(username: str, month: str) -> bool:
    return month_is_closed_cached(username, parse_month_to_canonical(month))


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def list_users_cached():
    return s_data(s_select("usuaris", "username, language, created_at, last_login").order("username").execute())


def list_users():
    return list_users_cached()


def latest_month_from_months(months: List[str]):
    valid = [m for m in months if re.match(r"^\d{4}-\d{2}$", str(m))]
    return max(valid) if valid else None


def group_tars_by_br(tars):
    grouped = {}
    for tar in tars:
        grouped.setdefault(tar.get("id_br"), []).append(tar)
    return grouped

# ============================================================
# DATA MUTATIONS
# ============================================================


def close_month(username, month):
    supabase.table("mesos_tancats").upsert({"username": username, "mes": parse_month_to_canonical(month), "closed_at": now_iso()}).execute()
    clear_data_cache()


def unlock_month(username, month):
    aliases = month_aliases(month)
    query = supabase.table("mesos_tancats").delete().eq("username", username)
    query = query.in_("mes", aliases) if len(aliases) > 1 else query.eq("mes", aliases[0])
    query.execute()
    clear_data_cache()


def get_existing_br_in_month(username, month, br_name):
    aliases = month_aliases(month)
    query = s_select("big_rocks", "id, nom, notes_progres").eq("username", username).eq("nom", br_name)
    query = query.in_("mes", aliases) if len(aliases) > 1 else query.eq("mes", aliases[0])
    data = s_data(query.limit(1).execute())
    return data[0] if data else None


def create_next_month_from_pending(username, month, reset_recurrent_map=None):
    reset_recurrent_map = reset_recurrent_map or {}
    source_month = parse_month_to_canonical(month)
    target_month = next_month(source_month)
    brs = get_brs(username, source_month)
    all_tars = get_all_tars_for_brs([br["id"] for br in brs])
    tars_by_br = group_tars_by_br(all_tars)
    created_brs = 0
    created_tars = 0

    for br in brs:
        br_id = br["id"]
        recurrent = br_is_recurrent(br.get("notes_progres"))
        br_tars = tars_by_br.get(br_id, [])
        carry_tars = []
        for tar in br_tars:
            prog = int(tar.get("progres") or 0)
            if recurrent or prog < 100:
                carry_tars.append(tar)
        if not carry_tars:
            continue

        existing = get_existing_br_in_month(username, target_month, br.get("nom") or "")
        if existing:
            new_br_id = existing["id"]
        else:
            br_notes, tar_notes, meta = unpack_notes(br.get("notes_progres"))
            res = supabase.table("big_rocks").insert({
                "username": username,
                "mes": target_month,
                "nom": br.get("nom") or "",
                "persones": br.get("persones") or "",
                "reunions": br.get("reunions") or "",
                "notes_progres": pack_notes(br_notes, {}, meta),
                "pregunta": br.get("pregunta") or "",
                "passos": br.get("passos") or "",
                "created_at": now_iso(),
                "updated_at": now_iso(),
            }).execute()
            data = s_data(res)
            if not data:
                continue
            new_br_id = data[0]["id"]
            created_brs += 1

        existing_tars = get_all_tars_for_brs([new_br_id])
        existing_desc = {str(x.get("descripcio") or "").strip().lower() for x in existing_tars}
        rows = []
        reset_this = bool(reset_recurrent_map.get(str(br_id), False))
        for idx, tar in enumerate(carry_tars, start=1):
            desc = str(tar.get("descripcio") or "").strip()
            if not desc or desc.lower() in existing_desc:
                continue
            progress = 0 if reset_this else int(tar.get("progres") or 0)
            rows.append({
                "id_br": new_br_id,
                "num": f"TAR {len(existing_tars) + len(rows) + 1}",
                "descripcio": desc,
                "progres": progress,
                "estat": "Actiu",
                "created_at": now_iso(),
                "updated_at": now_iso(),
            })
        if rows:
            supabase.table("tars").insert(rows).execute()
            created_tars += len(rows)
    clear_data_cache()
    return target_month, created_brs, created_tars


def close_month_and_open_next(username, month, reset_recurrent_map=None):
    close_month(username, month)
    return create_next_month_from_pending(username, month, reset_recurrent_map)


def delete_month(username, month):
    canonical = parse_month_to_canonical(month)
    brs = get_brs(username, canonical)
    br_ids = [br["id"] for br in brs]
    if br_ids:
        supabase.table("tars").delete().in_("id_br", br_ids).execute()
    aliases = month_aliases(canonical)
    q = supabase.table("big_rocks").delete().eq("username", username)
    q = q.in_("mes", aliases) if len(aliases) > 1 else q.eq("mes", aliases[0])
    q.execute()
    q2 = supabase.table("mesos_tancats").delete().eq("username", username)
    q2 = q2.in_("mes", aliases) if len(aliases) > 1 else q2.eq("mes", aliases[0])
    q2.execute()
    clear_data_cache()


def delete_bigrock(br_id):
    supabase.table("tars").delete().eq("id_br", br_id).execute()
    supabase.table("big_rocks").delete().eq("id", br_id).execute()
    clear_data_cache()


def renumber_tars(br_id):
    rows = get_all_tars_for_brs([br_id])
    for idx, tar in enumerate(rows, start=1):
        supabase.table("tars").update({"num": f"TAR {idx}", "updated_at": now_iso()}).eq("id", tar["id"]).execute()
    clear_data_cache()


def add_tar_to_bigrock(br_id, current_tars, desc):
    desc = str(desc or "").strip()
    if not desc:
        return None
    if len(current_tars) >= MAX_TARS_PER_BIGROCK:
        raise ValueError(t("max_tars_warning"))
    res = supabase.table("tars").insert({
        "id_br": br_id,
        "num": f"TAR {len(current_tars) + 1}",
        "descripcio": desc,
        "progres": 0,
        "estat": "Actiu",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }).execute()
    clear_data_cache()
    data = s_data(res)
    return data[0]["id"] if data else None


def delete_tar_from_bigrock(br_id, tar_id, current_tars):
    if len(current_tars) <= 1:
        raise ValueError(t("min_one_tar_delete"))
    supabase.table("tars").delete().eq("id", tar_id).execute()
    clear_data_cache()
    renumber_tars(br_id)


def update_bigrock_details(br_id, nom, persones, reunions, raw_notes, br_notes, pregunta, passos, recurrent):
    _, tar_notes, meta = unpack_notes(raw_notes)
    meta["recurrent"] = bool(recurrent)
    supabase.table("big_rocks").update({
        "nom": nom,
        "persones": persones,
        "reunions": reunions,
        "notes_progres": pack_notes(br_notes, tar_notes, meta),
        "pregunta": pregunta,
        "passos": passos,
        "updated_at": now_iso(),
    }).eq("id", br_id).execute()
    clear_data_cache()


def duplicate_bigrock(username, month, br, br_tars):
    br_notes, _, meta = unpack_notes(br.get("notes_progres"))
    res = supabase.table("big_rocks").insert({
        "username": username,
        "mes": parse_month_to_canonical(month),
        "nom": f"{br.get('nom') or ''} copia".strip(),
        "persones": br.get("persones") or "",
        "reunions": br.get("reunions") or "",
        "notes_progres": pack_notes(br_notes, {}, meta),
        "pregunta": br.get("pregunta") or "",
        "passos": br.get("passos") or "",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }).execute()
    data = s_data(res)
    if not data:
        return None
    new_br_id = data[0]["id"]
    rows = []
    for idx, tar in enumerate(br_tars, start=1):
        rows.append({
            "id_br": new_br_id,
            "num": f"TAR {idx}",
            "descripcio": tar.get("descripcio") or "",
            "progres": 0,
            "estat": "Actiu",
            "created_at": now_iso(),
            "updated_at": now_iso(),
        })
    if rows:
        supabase.table("tars").insert(rows).execute()
    clear_data_cache()
    return new_br_id


def create_bigrock(username, month, nom, persones, reunions, tar_descs, br_notes, pregunta, passos, recurrent=False):
    clean_tars = [str(desc).strip() for desc in tar_descs if str(desc).strip()]
    if not clean_tars:
        raise ValueError(t("min_one_tar"))
    if len(clean_tars) > MAX_TARS_PER_BIGROCK:
        raise ValueError(t("max_tars_warning"))
    res = supabase.table("big_rocks").insert({
        "username": username,
        "mes": parse_month_to_canonical(month),
        "nom": nom,
        "persones": persones,
        "reunions": reunions,
        "notes_progres": pack_notes(br_notes, {}, {"recurrent": bool(recurrent)}),
        "pregunta": pregunta,
        "passos": passos,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }).execute()
    data = s_data(res)
    if not data:
        return None
    br_id = data[0]["id"]
    rows = [
        {"id_br": br_id, "num": f"TAR {i}", "descripcio": desc, "progres": 0, "estat": "Actiu", "created_at": now_iso(), "updated_at": now_iso()}
        for i, desc in enumerate(clean_tars, start=1)
    ]
    supabase.table("tars").insert(rows).execute()
    clear_data_cache()
    return br_id

# ============================================================
# STATS + UI HELPERS
# ============================================================


def stats_from_tars(tars):
    total = len(tars)
    completed = sum(1 for tar in tars if int(tar.get("progres") or 0) == 100)
    in_progress = sum(1 for tar in tars if 0 < int(tar.get("progres") or 0) < 100)
    pending = sum(1 for tar in tars if int(tar.get("progres") or 0) == 0)
    avg = int(sum(int(tar.get("progres") or 0) for tar in tars) / total) if total else 0
    return {"total": total, "completed": completed, "in_progress": in_progress, "pending": pending, "avg": avg}


def compliance_label(percent, lang=None):
    lang = lang or st.session_state.get("idioma", "ca")
    percent = int(percent or 0)
    if lang == "es":
        if percent < 40:
            return "🔴", "cumplimiento bajo", "el mes requiere revisión y foco adicional en las Big Rocks con menor avance."
        if percent < 70:
            return "🟡", "progreso parcial", "el mes muestra avance, pero todavía queda por debajo del nivel deseable para un cierre sólido."
        if percent < 90:
            return "🔵", "buen resultado", "el mes presenta un buen resultado global y las tareas pendientes deben mantenerse en seguimiento en el siguiente periodo."
        return "🟢", "resultado excelente", "el mes presenta un cumplimiento muy alto; si este nivel se repite siempre, conviene revisar si los objetivos son suficientemente ambiciosos."
    if percent < 40:
        return "🔴", "compliment baix", "el mes requereix revisió i més focus en les Big Rocks amb menor avanç."
    if percent < 70:
        return "🟡", "progrés parcial", "el mes mostra avanç, però encara queda per sota del nivell desitjable per a un tancament sòlid."
    if percent < 90:
        return "🔵", "bon resultat", "el mes presenta un bon resultat global i les tasques pendents s'han de mantenir en seguiment al període següent."
    return "🟢", "resultat excel·lent", "el mes presenta un compliment molt alt; si aquest nivell es repeteix sempre, convé revisar si els objectius són prou ambiciosos."


def build_month_evaluation_summary(brs, tars_by_br, all_stats):
    avg = int(all_stats.get("avg", 0))
    icon, label, conclusion = compliance_label(avg, st.session_state.get("idioma", "ca"))
    lines = []
    for br in brs:
        stats = stats_from_tars(tars_by_br.get(br["id"], []))
        lines.append(f"<li><b>{safe_html(br.get('nom'))}</b>: {stats['avg']}% · {stats['completed']}/{stats['total']} TARs</li>")
    detail = "".join(lines) if lines else ""
    return f"""
<div class='report-card'>
  <h3>{t('auto_analysis_title')}</h3>
  <p><b>{icon} {safe_html(label.capitalize())}</b></p>
  <p><b>{t('global_comp')}:</b> {avg}%</p>
  <p><b>{t('conclusion')}:</b> {t('according_to')}, {safe_html(conclusion)}</p>
  <ul>{detail}</ul>
</div>
"""


def compact_month_evaluation_text(all_stats):
    avg = int(all_stats.get("avg", 0))
    icon, label, conclusion = compliance_label(avg, st.session_state.get("idioma", "ca"))
    return f"{icon} {label.capitalize()} · {t('global_comp')}: {avg}%. {t('conclusion')}: {conclusion}"


def progress_bar(progress, label=None):
    progress = max(0, min(100, int(progress or 0)))
    label_text = label or f"{progress}%"
    st.markdown(
        f"""
<div class='small-muted'><b>{safe_html(label_text)}</b></div>
<div class='br-progress-wrap'><div class='br-progress-fill' style='--w:{progress}%;'></div></div>
""",
        unsafe_allow_html=True,
    )


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


def logo_for_login():
    return "<div class='sidebar-logo' style='color:#009CDE;text-align:center;font-size:2.5rem;'>sorigué</div>"


def logo_for_sidebar():
    return "<div class='sidebar-logo'>sorigué</div>"


def kpi_card(label, value):
    st.markdown(f"<div class='kpi-card'><div class='kpi-label'>{safe_html(label)}</div><div class='kpi-value'>{safe_html(value)}</div></div>", unsafe_allow_html=True)

# ============================================================
# AUTOSAVE CALLBACKS
# ============================================================


def auto_save_tar(tar_id, desc_key=None, progress_value=None):
    payload = {"updated_at": now_iso()}
    if desc_key is not None:
        payload["descripcio"] = st.session_state.get(desc_key, "")
    if progress_value is not None:
        payload["progres"] = int(progress_value)
    supabase.table("tars").update(payload).eq("id", tar_id).execute()
    clear_data_cache()


def auto_save_tar_from_select_slider(tar_id, prog_key):
    value = int(st.session_state.get(prog_key, 0))
    auto_save_tar(tar_id, progress_value=value)


def toggle_tar_edit(tar_id):
    key = f"editing_tar_{tar_id}"
    st.session_state[key] = not st.session_state.get(key, False)


def toggle_br_edit(br_id):
    key = f"editing_br_{br_id}"
    st.session_state[key] = not st.session_state.get(key, False)


def auto_save_tar_note(br_id, raw_current_notes, tar_id, note_key):
    br_notes_value, existing_tar_notes, meta = unpack_notes(raw_current_notes)
    existing_tar_notes[str(tar_id)] = st.session_state.get(note_key, "") or ""
    supabase.table("big_rocks").update({"notes_progres": pack_notes(br_notes_value, existing_tar_notes, meta), "updated_at": now_iso()}).eq("id", br_id).execute()
    clear_data_cache()


def render_tar_select_slider(tar_id, prog_key, current_progress, disabled=False):
    current_progress = int(current_progress or 0)
    if current_progress not in PROGRESS_OPTIONS:
        current_progress = 0
    st.select_slider(
        t("state"),
        options=PROGRESS_OPTIONS,
        value=current_progress,
        key=prog_key,
        label_visibility="collapsed",
        disabled=disabled,
        on_change=auto_save_tar_from_select_slider,
        args=(tar_id, prog_key),
    )
    now_value = int(st.session_state.get(prog_key, current_progress))
    st.markdown(f"<div class='small-muted'>{status_dot(now_value)} <b>{now_value}%</b></div>", unsafe_allow_html=True)

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
            clear_data_cache()
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


def remembered_user_from_query():
    try:
        value = st.query_params.get("last_user")
        if isinstance(value, list):
            value = value[0]
        return str(value or "")
    except Exception:
        return ""


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
if "month_close_prompt" not in st.session_state:
    st.session_state.month_close_prompt = None
if "month_selector_nonce" not in st.session_state:
    st.session_state.month_selector_nonce = 0
if "new_br_tar_count" not in st.session_state:
    st.session_state.new_br_tar_count = INITIAL_TARS_ON_CREATE

# ============================================================
# LOGIN
# ============================================================

if st.session_state.usuari_actual is None:
    left, center, right = st.columns([1, 1.35, 1])
    with center:
        st.markdown(logo_for_login(), unsafe_allow_html=True)
        st.title(t("login_title"))
        st.caption(t("login_subtitle"))
        st.selectbox(t("lang_login"), options=["ca", "es"], index=0 if st.session_state.idioma == "ca" else 1, format_func=lang_label, key="login_lang_selector", on_change=change_login_language)
        st.subheader(t("legacy_login"))
        tab1, tab2 = st.tabs([t("login_tab"), t("reg_tab")])
        with tab1:
            with st.form("legacy_login_form"):
                default_user = remembered_user_from_query() or st.session_state.get("last_user_login", "")
                usuari = st.text_input(t("email_user"), value=default_user, placeholder="usuario@sorigue.com")
                recordar = st.checkbox(t("remember_user"), value=bool(default_user))
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
                            st.session_state.last_user_login = username_clean
                            if recordar:
                                try:
                                    st.query_params["last_user"] = username_clean
                                except Exception:
                                    pass
                            else:
                                try:
                                    if "last_user" in st.query_params:
                                        del st.query_params["last_user"]
                                except Exception:
                                    pass
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
                submitted_reg = st.form_submit_button(t("register"), type="primary", use_container_width=True)
            if submitted_reg:
                username_new = nou_usuari.strip().lower()
                if not username_new or not nova_contra.strip():
                    st.error(t("required_fields"))
                elif not username_new.endswith(ALLOWED_EMAIL_DOMAIN):
                    st.error(t("corp_email_required"))
                else:
                    try:
                        ok = create_user(username_new, nova_contra, nou_idioma)
                        st.success(t("succ_reg")) if ok else st.error(t("err_reg"))
                    except Exception as e:
                        st.error(db_error_message(e))
    st.stop()

# ============================================================
# SIDEBAR
# ============================================================

USUARI = st.session_state.usuari_actual


def admin_users():
    raw = str(get_secret_value("ADMIN_USERS", "marc.llopis@sorigue.com,xavier.llopis@sorigue.com,marc.llopis,Xavier.llopis"))
    return [x.strip().lower() for x in raw.split(",") if x.strip()]


def is_admin_user(username):
    return str(username or "").strip().lower() in admin_users()


IS_ADMIN = is_admin_user(USUARI)

with st.sidebar:
    st.markdown(logo_for_sidebar(), unsafe_allow_html=True)
    st.markdown("<div class='sidebar-title'>BIG ROCKS</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='small-muted' style='color:white'>{safe_html(t('login_subtitle'))}</div>", unsafe_allow_html=True)
    badge = t("admin_badge") if IS_ADMIN else "Persona"
    st.markdown(f"<div class='user-card'><b>{safe_html(t('conn_as'))}</b><br>{safe_html(USUARI)}<br><small>{safe_html(badge)}</small></div>", unsafe_allow_html=True)
    st.selectbox(t("lang"), ["ca", "es"], index=0 if st.session_state.idioma == "ca" else 1, format_func=lang_label, key="idioma_selector", on_change=change_language)

    months = get_months(USUARI)
    if st.session_state.mes_actual not in months:
        months = [st.session_state.mes_actual] + months
    months = sorted(list(dict.fromkeys(months)), reverse=True)
    selected_month = st.selectbox(
        t("nav_months"),
        months,
        index=months.index(st.session_state.mes_actual) if st.session_state.mes_actual in months else 0,
        format_func=lambda m: month_display(m, st.session_state.idioma),
        key=f"mes_selector_{st.session_state.month_selector_nonce}",
    )
    if selected_month != st.session_state.mes_actual:
        st.session_state.mes_actual = selected_month
        st.session_state.open_br_id = None
        st.session_state.mostrar_formulari_br = False
        st.rerun()

    if st.button(t("eval_no_close"), use_container_width=True):
        st.session_state.pantalla = "informe"
        st.rerun()
    if st.button(t("eval_close"), type="primary", use_container_width=True):
        st.session_state.pantalla = "resum"
        st.rerun()
    if st.button(t("collapse_all"), use_container_width=True):
        st.session_state.open_br_id = None
        st.rerun()
    if IS_ADMIN and st.button(t("admin_panel"), use_container_width=True):
        st.session_state.pantalla = "admin"
        st.rerun()
    if st.button(t("logout"), use_container_width=True):
        st.session_state.usuari_actual = None
        st.rerun()
    st.caption(t("cache_note"))

# ============================================================
# RENDER FUNCTIONS
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
    if st.button(t("force_migration"), type="primary"):
        for email in USER_EMAIL_MIGRATION:
            for old_username in USER_EMAIL_MIGRATION[email]:
                for table, payload in [("big_rocks", {"username": email, "updated_at": now_iso()}), ("mesos_tancats", {"username": email}), ("usuaris", {"username": email, "last_login": now_iso()})]:
                    try:
                        supabase.table(table).update(payload).eq("username", old_username).execute()
                    except Exception:
                        pass
        clear_data_cache()
        st.success(t("migration_ok"))
    if st.button(t("back")):
        st.session_state.pantalla = "dashboard"
        st.rerun()


def render_report(title, allow_close=False):
    st.title(f"{title} · {month_display(MES)}")
    brs = get_brs(USUARI, MES)
    tars = get_all_tars_for_brs([br["id"] for br in brs])
    tars_by_br = group_tars_by_br(tars)
    all_stats = stats_from_tars(tars)
    progress_bar(all_stats["avg"], f"{all_stats['avg']}%")
    st.markdown(build_month_evaluation_summary(brs, tars_by_br, all_stats), unsafe_allow_html=True)

    for br in brs:
        br_tars = tars_by_br.get(br["id"], [])
        stats = stats_from_tars(br_tars)
        with st.container(border=True):
            st.subheader(br.get("nom") or "Big Rock")
            progress_bar(stats["avg"], f"{stats['avg']}%")
            for tar in br_tars:
                st.write(f"- {tar.get('descripcio') or ''} ({int(tar.get('progres') or 0)}%)")

    if not allow_close:
        if st.button(t("back")):
            st.session_state.pantalla = "dashboard"
            st.rerun()
        return

    recurrent_brs = [br for br in brs if br_is_recurrent(br.get("notes_progres"))]
    reset_map = {}
    if recurrent_brs:
        st.warning(t("recurrent_detected"))
        st.caption(t("reset_recurrent_hint"))
        for br in recurrent_brs:
            reset_map[str(br["id"])] = st.checkbox(f"{br.get('nom')} → 0%", value=True, key=f"reset_recurrent_{br['id']}")

    c1, c2 = st.columns(2)
    if c1.button(t("confirm_close"), type="primary", use_container_width=True):
        target_month, created_brs, created_tars = close_month_and_open_next(USUARI, MES, reset_map)
        st.session_state.mes_actual = target_month
        st.session_state.month_selector_nonce += 1
        st.session_state.pantalla = "dashboard"
        st.session_state.open_br_id = None
        st.session_state.month_close_prompt = {
            "month": target_month,
            "created_brs": created_brs,
            "created_tars": created_tars,
            "summary": compact_month_evaluation_text(all_stats),
        }
        st.session_state.mostrar_formulari_br = created_brs == 0
        st.session_state.new_br_tar_count = INITIAL_TARS_ON_CREATE
        st.rerun()
    if c2.button(t("back"), use_container_width=True):
        st.session_state.pantalla = "dashboard"
        st.rerun()


def render_create_bigrock(MES):
    st.subheader(t("config_br"))
    if st.session_state.new_br_tar_count < MAX_TARS_PER_BIGROCK:
        c_add, c_msg = st.columns([1.2, 3])
        with c_add:
            if st.button(t("add_tar"), key="add_new_br_tar_field", use_container_width=True):
                st.session_state.new_br_tar_count = min(MAX_TARS_PER_BIGROCK, st.session_state.new_br_tar_count + 1)
                st.rerun()
        with c_msg:
            st.caption(f"{st.session_state.new_br_tar_count}/{MAX_TARS_PER_BIGROCK} TARs")
    else:
        st.warning(t("max_tars_warning"))

    try:
        nova_form = st.form("form_nova_br", enter_to_submit=False)
    except TypeError:
        nova_form = st.form("form_nova_br")
    with nova_form:
        nou_nom = st.text_input(t("title_br"), placeholder=t("title_placeholder"), key="new_br_title")
        c1, c2 = st.columns(2)
        persones = c1.text_input(t("key_ppl"), placeholder=t("people_placeholder"), key="new_br_people")
        reunions = c2.text_input(t("key_meet"), placeholder=t("meetings_placeholder"), key="new_br_meetings")
        recurrent_new = st.checkbox(t("br_recurrent"), value=False, key="new_br_recurrent")
        with st.expander(t("details"), expanded=True):
            br_notes_new = st.text_area(t("prog"), placeholder=t("prog"), key="new_br_notes")
            pregunta_new = st.text_input(t("need"), placeholder=t("need"), key="new_br_need")
            passos_new = st.text_input(t("next_steps"), placeholder=t("next_steps"), key="new_br_next_steps")
        st.markdown("### TARs")
        st.caption(t("max_tars_warning"))
        new_tars = []
        for i in range(1, st.session_state.new_br_tar_count + 1):
            new_tars.append(st.text_input(f"TAR {i}", placeholder=t("tar_placeholder"), key=f"new_br_tar_{i}"))
        submitted = st.form_submit_button(t("save"), type="primary", use_container_width=True)
    if submitted:
        if not nou_nom.strip():
            st.error(t("title_br"))
        elif not any(x.strip() for x in new_tars):
            st.error(t("min_one_tar"))
        else:
            try:
                new_id = create_bigrock(USUARI, MES, nou_nom.strip(), persones.strip(), reunions.strip(), new_tars, br_notes_new, pregunta_new, passos_new, recurrent_new)
                st.session_state.mostrar_formulari_br = False
                st.session_state.new_br_tar_count = INITIAL_TARS_ON_CREATE
                for key in ["new_br_title", "new_br_people", "new_br_meetings", "new_br_recurrent", "new_br_notes", "new_br_need", "new_br_next_steps"] + [f"new_br_tar_{i}" for i in range(1, MAX_TARS_PER_BIGROCK + 1)]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state.open_br_id = str(new_id)
                st.rerun()
            except Exception as e:
                st.error(db_error_message(e))


def render_bigrock_card(br, br_tars, es_tancat):
    br_id = br["id"]
    is_open = st.session_state.get("open_br_id") == str(br_id)
    stats = stats_from_tars(br_tars)
    icon = "▼" if is_open else "▶"
    title = br.get("nom") or "Big Rock"

    with st.container():
        st.markdown("<div class='br-card'>", unsafe_allow_html=True)
        c1, c2 = st.columns([5, 1])
        with c1:
            if st.button(f"{icon} {title}", key=f"open_br_{br_id}", use_container_width=True):
                toggle_bigrock(br_id)
                st.rerun()
            st.markdown(f"<div class='br-meta'>{stats['total']} TARs · {stats['completed']} completades · {stats['pending'] + stats['in_progress']} pendents</div>", unsafe_allow_html=True)
            progress_bar(stats["avg"], f"{stats['avg']}%")
        with c2:
            st.metric("", f"{stats['avg']}%")
        st.markdown("</div>", unsafe_allow_html=True)

    if not is_open:
        return

    br_notes, tar_notes, meta = unpack_notes(br.get("notes_progres"))

    with st.expander(t("details"), expanded=False):
        notes_key = f"br_notes_{br_id}"
        preg_key = f"br_preg_{br_id}"
        passos_key = f"br_passos_{br_id}"
        st.text_area(t("prog"), value=br_notes, key=notes_key, disabled=es_tancat)
        st.text_input(t("need"), value=br.get("pregunta") or "", key=preg_key, disabled=es_tancat)
        st.text_input(t("next_steps"), value=br.get("passos") or "", key=passos_key, disabled=es_tancat)
        if not es_tancat and st.button(t("saved"), key=f"save_details_{br_id}"):
            _, existing_tar_notes, meta2 = unpack_notes(br.get("notes_progres"))
            supabase.table("big_rocks").update({
                "notes_progres": pack_notes(st.session_state.get(notes_key, ""), existing_tar_notes, meta2),
                "pregunta": st.session_state.get(preg_key, ""),
                "passos": st.session_state.get(passos_key, ""),
                "updated_at": now_iso(),
            }).eq("id", br_id).execute()
            clear_data_cache()
            st.rerun()

    if not es_tancat:
        cols = st.columns(3)
        if cols[0].button(t("edit_br"), key=f"editbr_toggle_{br_id}", use_container_width=True):
            toggle_br_edit(br_id)
            st.rerun()
        if cols[1].button(t("duplicate_br"), key=f"dupbr_{br_id}", use_container_width=True):
            new_id = duplicate_bigrock(USUARI, MES, br, br_tars)
            st.session_state.open_br_id = str(new_id) if new_id else None
            st.success(t("br_duplicated"))
            st.rerun()
        if cols[2].button(t("delete_br"), key=f"deletebr_toggle_{br_id}", use_container_width=True):
            st.session_state[f"confirm_delete_br_show_{br_id}"] = not st.session_state.get(f"confirm_delete_br_show_{br_id}", False)
            st.rerun()

        if st.session_state.get(f"confirm_delete_br_show_{br_id}", False):
            confirm = st.checkbox(t("confirm_delete_br"), key=f"confirm_delete_br_{br_id}")
            if st.button(t("delete_br"), type="primary", key=f"deletebr_confirm_{br_id}", disabled=not confirm):
                delete_bigrock(br_id)
                st.session_state.open_br_id = None
                st.success(t("br_deleted"))
                st.rerun()

        if st.session_state.get(f"editing_br_{br_id}", False):
            with st.form(f"edit_br_form_{br_id}"):
                edit_nom = st.text_input(t("title_br"), value=br.get("nom") or "")
                edit_persones = st.text_input(t("key_ppl"), value=br.get("persones") or "")
                edit_reunions = st.text_input(t("key_meet"), value=br.get("reunions") or "")
                edit_recurrent = st.checkbox(t("br_recurrent"), value=br_is_recurrent(br.get("notes_progres")))
                edit_notes = st.text_area(t("prog"), value=br_notes)
                edit_preg = st.text_input(t("need"), value=br.get("pregunta") or "")
                edit_passos = st.text_input(t("next_steps"), value=br.get("passos") or "")
                if st.form_submit_button(t("save_br_changes"), type="primary"):
                    update_bigrock_details(br_id, edit_nom, edit_persones, edit_reunions, br.get("notes_progres"), edit_notes, edit_preg, edit_passos, edit_recurrent)
                    st.session_state[f"editing_br_{br_id}"] = False
                    st.rerun()

        if len(br_tars) < MAX_TARS_PER_BIGROCK:
            with st.expander(t("add_tar"), expanded=False):
                new_tar_desc = st.text_input(t("new_tar"), key=f"new_tar_desc_{br_id}")
                if st.button(t("add_tar"), key=f"add_tar_{br_id}"):
                    try:
                        add_tar_to_bigrock(br_id, br_tars, new_tar_desc)
                        st.success(t("tar_added"))
                        st.rerun()
                    except Exception as e:
                        st.error(db_error_message(e))
        else:
            st.warning(t("max_tars_warning"))

    for tar in br_tars:
        tar_id = tar["id"]
        desc = tar.get("descripcio") or tar.get("num") or "TAR"
        progress = int(tar.get("progres") or 0)
        st.markdown("<div class='tar-card'><div class='tar-inner'><div class='tar-side'></div><div class='tar-content'>", unsafe_allow_html=True)
        tc1, tc2, tc3 = st.columns([6, 1.2, .7])
        with tc1:
            st.markdown(f"<div class='tar-title'>{safe_html(tar.get('num') or '')} · {safe_html(desc)}</div>", unsafe_allow_html=True)
        with tc2:
            st.markdown(f"<div class='tar-progress-value'>{status_dot(progress)} {progress}%</div>", unsafe_allow_html=True)
        with tc3:
            if not es_tancat and st.button("✏️", key=f"edit_tar_{tar_id}"):
                toggle_tar_edit(tar_id)
                st.rerun()
        if st.session_state.get(f"editing_tar_{tar_id}", False):
            desc_key = f"desc_tar_{tar_id}"
            st.text_input("", value=desc, key=desc_key, label_visibility="collapsed", disabled=es_tancat, on_change=auto_save_tar, args=(tar_id, desc_key, None))
        prog_key = f"tar_prog_{tar_id}"
        render_tar_select_slider(tar_id, prog_key, progress, disabled=es_tancat)
        with st.expander(t("tar_notes"), expanded=False):
            note_key = f"tar_note_{tar_id}"
            st.text_area("", value=tar_notes.get(str(tar_id), ""), key=note_key, label_visibility="collapsed", placeholder=t("tar_notes_placeholder"), disabled=es_tancat, on_change=auto_save_tar_note, args=(br_id, br.get("notes_progres"), tar_id, note_key))
            if not es_tancat:
                if st.checkbox(t("confirm_delete_tar"), key=f"confirm_delete_tar_{tar_id}"):
                    if st.button(t("delete_tar"), key=f"delete_tar_{tar_id}"):
                        try:
                            delete_tar_from_bigrock(br_id, tar_id, br_tars)
                            st.success(t("tar_deleted"))
                            st.rerun()
                        except Exception as e:
                            st.error(db_error_message(e))
        st.markdown("</div></div></div>", unsafe_allow_html=True)

# ============================================================
# MAIN
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
    st.title(f"Big Rocks · {month_display(MES)}")
    st.caption(t("cache_note"))
    if es_tancat:
        st.warning(t("closed_month"))
        if st.button(t("unlock"), type="primary"):
            unlock_month(USUARI, MES)
            st.rerun()
    else:
        st.success(t("open_month"))

    if st.session_state.month_close_prompt:
        prompt = st.session_state.month_close_prompt
        with st.container(border=True):
            st.subheader(t("close_prompt_title"))
            st.write(prompt.get("summary", ""))
            st.write(f"{t('close_prompt_transfer')}: {prompt.get('created_brs', 0)} Big Rocks · {prompt.get('created_tars', 0)} TARs")
            st.write(t("close_prompt_question"))
            c1, c2 = st.columns(2)
            if c1.button(t("create_br"), type="primary", use_container_width=True):
                st.session_state.mostrar_formulari_br = True
                st.session_state.month_close_prompt = None
                st.session_state.new_br_tar_count = INITIAL_TARS_ON_CREATE
                st.rerun()
            if c2.button(t("continue"), use_container_width=True):
                st.session_state.month_close_prompt = None
                st.rerun()

    brs = get_brs(USUARI, MES)
    all_tars = get_all_tars_for_brs([br["id"] for br in brs])
    tars_by_br = group_tars_by_br(all_tars)
    all_stats = stats_from_tars(all_tars)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        kpi_card(t("active_brs"), len(brs))
    with k2:
        kpi_card(t("avg_progress"), f"{all_stats['avg']}%")
    with k3:
        kpi_card(t("completed_tars"), all_stats["completed"])
    with k4:
        kpi_card(t("pending_tars"), all_stats["pending"] + all_stats["in_progress"])

    st.write("")
    if st.button(t("create_br"), type="primary"):
        st.session_state.mostrar_formulari_br = not st.session_state.mostrar_formulari_br
        if st.session_state.mostrar_formulari_br:
            st.session_state.new_br_tar_count = INITIAL_TARS_ON_CREATE
        st.rerun()

    if st.session_state.mostrar_formulari_br and not es_tancat:
        render_create_bigrock(MES)

    months_available = get_months(USUARI)
    latest = latest_month_from_months(months_available)
    if latest and latest == parse_month_to_canonical(MES):
        with st.expander(t("delete_last_month"), expanded=False):
            confirm_delete = st.checkbox(t("confirm_delete_last_month"), key="confirm_delete_latest_month_local")
            if st.button(t("delete_last_month"), type="primary", disabled=not confirm_delete):
                delete_month(USUARI, MES)
                remaining = [m for m in get_months(USUARI) if m != parse_month_to_canonical(MES)]
                st.session_state.mes_actual = max(remaining) if remaining else get_month_key()
                st.session_state.month_selector_nonce += 1
                st.session_state.open_br_id = None
                st.success(t("deleted_last_month"))
                st.rerun()

    if not brs:
        st.markdown(f"<div class='empty-state'><h3>{t('no_br_title')}</h3><p>{t('no_br_body')}</p></div>", unsafe_allow_html=True)
    else:
        st.info(t("help_body"))
        for br in brs:
            render_bigrock_card(br, tars_by_br.get(br["id"], []), es_tancat)
