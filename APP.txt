import streamlit as st
import sqlite3
import pandas as pd

# ==========================================
# 0. CONFIGURACIÓ I DISSENY CORPORATIU
# ==========================================
st.set_page_config(page_title="Big Rocks - Sorigué", layout="wide", page_icon="🪨")

st.markdown("""
    <style>
    /* 1. AMAGAR ELEMENTS DE STREAMLIT (SENSE TREURE EL BOTÓ D'OBRIR LA BARRA) */
    
    /* Amagar el menú d'opcions de la dreta (tres ratlles) */
    [data-testid="stHeader"] .st-emotion-cache-18ni7ap {
        display: none !important;
    }
    
    /* Amagar el botó de "Manage app" (Github) si existeix */
    .st-emotion-cache-16idej2 {
        display: none !important;
    }

    /* Amagar el peu de pàgina "Made with Streamlit" */
    footer {visibility: hidden;}

    /* Fer el fons de la capçalera transparent */
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* FORÇAR EL BOTÓ D'OBRIR LA BARRA LATERAL A SER NEGRE I VISIBLE */
    button[kind="header"] svg {
        fill: #000000 !important;
        stroke: #000000 !important;
    }

    /* Fons general suau per fer destacar les targetes blanques */
    .stApp {
        background-color: #f8f9fa;
    }

    /* 2. BARRA LATERAL BLAU CORPORATIU */
    [data-testid="stSidebar"] {
        background-color: #009FE3 !important;
    }
    
    /* Text blanc a la barra lateral (Específic per no afectar elements externs) */
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] h1 {
        color: white !important;
    }

    /* Convertir el logotip a blanc a la barra lateral */
    [data-testid="stSidebar"] img {
        filter: brightness(0) invert(1);
        margin-bottom: 20px;
    }

    /* Botó de tancar sessió a la barra */
    [data-testid="stSidebar"] button {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        color: white !important;
        border-radius: 8px;
        transition: all 0.3s;
    }
    [data-testid="stSidebar"] button:hover {
        background-color: rgba(255, 255, 255, 0.25) !important;
    }

    /* Excepcions a la barra: fons blanc per als selectors de mes/idioma i text fosc a dins */
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: white !important;
        border-radius: 6px;
        border: none !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] * {
        color: #333 !important;
    }

    /* 3. DISSENY TARGETES (CARDS) PER A LES BIG ROCKS */
    div[data-testid="stVerticalBlock"] > div > div > div[data-testid="stVerticalBlock"] {
        background-color: white;
        border-radius: 12px;
        padding: 25px 30px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #f0f0f0;
    }

    /* Títols */
    h1, h2, h3 {
        color: #333 !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
    }
    h2 { margin-bottom: 5px !important; }

    /* Botons principals (Blau Sorigué) */
    .stButton>button[kind="primary"] {
        background-color: #009FE3 !important;
        color: white !important;
        border-color: #009FE3 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s;
    }
    .stButton>button[kind="primary"]:hover {
        background-color: #0088c4 !important;
        box-shadow: 0 4px 8px rgba(0, 159, 227, 0.3);
    }

    /* Botó d'esborrar (Paperera) */
    button[key^="btn_"] {
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        padding: 0 !important;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: transparent !important;
        border: 1px solid #ddd !important;
        color: #666 !important;
    }
    button[key^="btn_"]:hover {
        background-color: #ffeaea !important;
        border-color: #ff4b4b !important;
        color: #ff4b4b !important;
    }

    /* Inputs més nets i amb text fosc sempre */
    input {
        border-radius: 6px !important;
        border: 1px solid #ddd !important;
        background-color: #fafafa !important;
        color: #333 !important;
    }
    input:focus {
        border-color: #009FE3 !important;
        box-shadow: 0 0 0 1px #009FE3 !important;
    }

    /* Text areas i altres components de text */
    textarea {
        color: #333 !important;
    }

    /* Radio buttons centrats */
    div[role="radiogroup"] { 
        margin-top: 8px; 
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. DICCIONARI DE TRADUCCIONS
# ==========================================
TRANS = {
    'ca': {
        'login_title': "Accés a la Plataforma", 'login_tab': "Iniciar Sessió", 'reg_tab': "Registrar Nou Usuari",
        'usr': "Nom d'usuari", 'pwd': "Contrasenya", 'new_usr': "Nou nom d'usuari",
        'lang_reg': "Idioma per defecte",
        'enter': "Entrar", 'register': "Registrar",
        'err_login': "Usuari o contrasenya incorrectes.",
        'succ_reg': "Usuari creat correctament! Ara pots iniciar sessió.",
        'err_reg': "Aquest nom d'usuari ja existeix.",
        'conn_as': "Connectat com:", 'lang': "Idioma",
        'nav_months': "Navegar pels mesos", 'closed_month': "🔒 Aquest mes està TANCAT.",
        'unlock': "🔓 Desbloquejar Mes", 'open_month': "✏️ Mes Obert (Editable)",
        'logout': "Tancar Sessió",
        'eval_close': "Avaluar i Tancar Mes", 'no_br': "No hi ha cap Big Rock activa. Afegeix-ne de noves a sota.",
        'key_ppl': "👥 **Persones clau:**", 'key_meet': "📅 **Reunions:**",
        'global_prog': "Assoliment global:", 'state': "Estat", 'desc': "Descripció de la tasca",
        'details': "Detalls, Preguntes i Pròxims Passos", 'prog': "Progrés:", 'need': "Pregunta o necessitat:",
        'next_steps': "Pròxims passos:", 'save_notes': "Guardar Notes",
        'create_br': "➕ Crear Nova Big Rock", 'config_br': "Configura la teva nova Big Rock",
        'title_br': "Títol de la Big Rock", 'save': "Guardar Big Rock",
        'summary': "Resum de Tancament", 'global_comp': "Grau de Compliment Global",
        'successes': "Èxits (100%)", 'carry_over': "Es traspassen",
        'cancel': "Cancel·lar i tornar", 'confirm_close': "Confirmar Tancament i Crear Mes Següent",
        'months': ["Gener", "Febrer", "Març", "Abril", "Maig", "Juny", "Juliol", "Agost", "Setembre", "Octubre", "Novembre", "Desembre"]
    },
    'es': {
        'login_title': "Acceso a la Plataforma", 'login_tab': "Iniciar Sesión", 'reg_tab': "Registrar Nuevo Usuario",
        'usr': "Nombre de usuario", 'pwd': "Contraseña", 'new_usr': "Nuevo nombre de usuario",
        'lang_reg': "Idioma por defecto",
        'enter': "Entrar", 'register': "Registrar",
        'err_login': "Usuario o contraseña incorrectos.",
        'succ_reg': "¡Usuario creado correctamente! Ahora puedes iniciar sesión.",
        'err_reg': "Este nombre de usuario ya existe.",
        'conn_as': "Conectado como:", 'lang': "Idioma",
        'nav_months': "Navegar por los meses", 'closed_month': "🔒 Este mes está CERRADO.",
        'unlock': "🔓 Desbloquear Mes", 'open_month': "✏️ Mes Abierto (Editable)",
        'logout': "Cerrar Sesión",
        'eval_close': "Evaluar y Cerrar Mes", 'no_br': "No hay ninguna Big Rock activa. Añade nuevas abajo.",
        'key_ppl': "👥 **Personas clave:**", 'key_meet': "📅 **Reuniones:**",
        'global_prog': "Avance global:", 'state': "Estado", 'desc': "Descripción de la tarea",
        'details': "Detalles, Preguntas y Próximos Pasos", 'prog': "Progreso:", 'need': "Pregunta o necesidad:",
        'next_steps': "Próximos pasos:", 'save_notes': "Guardar Notas",
        'create_br': "➕ Crear Nueva Big Rock", 'config_br': "Configura tu nueva Big Rock",
        'title_br': "Título de la Big Rock", 'save': "Guardar Big Rock",
        'summary': "Resumen de Cierre", 'global_comp': "Grado de Cumplimiento Global",
        'successes': "Éxitos (100%)", 'carry_over': "Se traspasan",
        'cancel': "Cancelar y volver", 'confirm_close': "Confirmar Cierre y Crear Mes Siguiente",
        'months': ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    }
}

def t(key):
    lang = st.session_state.get('idioma', 'ca')
    return TRANS[lang].get(key, key)

# ==========================================
# 2. BASE DE DADES
# ==========================================
def init_db():
    conn = sqlite3.connect('bigrocks.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuaris (username TEXT PRIMARY KEY, password TEXT)''')
    try:
        c.execute("ALTER TABLE usuaris ADD COLUMN language TEXT DEFAULT 'ca'")
    except sqlite3.OperationalError:
        pass
    c.execute('''CREATE TABLE IF NOT EXISTS big_rocks (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, mes TEXT, nom TEXT, persones TEXT, reunions TEXT, notes_progres TEXT, pregunta TEXT, passos TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tars (id INTEGER PRIMARY KEY AUTOINCREMENT, id_br INTEGER, num TEXT, descripcio TEXT, progres INTEGER, estat TEXT, FOREIGN KEY(id_br) REFERENCES big_rocks(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS mesos_tancats (username TEXT, mes TEXT, PRIMARY KEY(username, mes))''') 
    conn.commit()
    conn.close()

init_db()

def run_query(query, params=()):
    conn = sqlite3.connect('bigrocks.db')
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()
    return c

def fetch_query(query, params=()):
    conn = sqlite3.connect('bigrocks.db')
    c = conn.cursor()
    c.execute(query, params)
    data = c.fetchall()
    conn.close()
    return data

# ==========================================
# 3. FUNCIONS VISUALS I CALLBACKS
# ==========================================
def progress_bar_colorida(progres, is_global=False):
    if progres <= 25: color = "#FF4B4B"
    elif progres <= 50: color = "#FFA500"
    elif progres <= 99: color = "#FFD700"
    else: color = "#00C851"
        
    height = "32px" if is_global else "36px"
    margin = "5px 0 15px 0" if is_global else "4px 0 0 0"
    text = f"{t('global_prog')} {progres}%" if is_global else f"{progres}%"
    text_color = "#333" if progres == 0 or (is_global and 25 < progres <= 99) else "white"
    
    html = f"""
    <div style="width: 100%; background-color: #eaedf2; border-radius: 8px; height: {height}; position: relative; margin: {margin}; overflow: hidden;">
        <div style="width: {progres}%; background-color: {color}; height: 100%; border-radius: 8px; transition: width 0.4s ease-in-out;"></div>
        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-family: sans-serif; font-size: 13px; font-weight: bold; color: {text_color}; text-shadow: {'1px 1px 2px rgba(0,0,0,0.3)' if text_color == 'white' else 'none'};">
            {text}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def update_db_val(table, field, val, uid): run_query(f"UPDATE {table} SET {field}=? WHERE id=?", (val, uid))
def arxivar_tar(id_tar): run_query("UPDATE tars SET estat='Arxivat' WHERE id=?", (id_tar,))
def canviar_idioma(): run_query("UPDATE usuaris SET language=? WHERE username=?", (st.session_state.idioma_selector, st.session_state.usuari_actual))

# ==========================================
# 4. SISTEMA DE LOGIN
# ==========================================
if 'usuari_actual' not in st.session_state: st.session_state.usuari_actual = None

if st.session_state.usuari_actual is None:
    st.write("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try: st.image("sorigue_logo_RGB-positivo.png", width=250)
        except: st.title("Sorigué")
        
        # Assegurem que el títol del login sempre estigui en el seu idioma preferit
        st.write("### ", t('login_title'))
        tab1, tab2 = st.tabs([t('login_tab'), t('reg_tab')])
        
        with tab1:
            with st.form("login_form"):
                usuari = st.text_input(t('usr'))
                contrasenya = st.text_input(t('pwd'), type="password")
                if st.form_submit_button(t('enter'), type="primary", use_container_width=True):
                    user_data = fetch_query("SELECT language FROM usuaris WHERE username=? AND password=?", (usuari, contrasenya))
                    if user_data:
                        st.session_state.usuari_actual = usuari
                        st.session_state.idioma = user_data[0][0] if user_data[0][0] else 'ca'
                        st.session_state.mes_actual = "Juliol 2026" if st.session_state.idioma == 'ca' else "Julio 2026"
                        st.session_state.pantalla = 'dashboard'
                        st.rerun()
                    else:
                        st.error(t('err_login'))
        with tab2:
            with st.form("register_form"):
                nou_usuari = st.text_input(t('new_usr'))
                nova_contra = st.text_input(t('pwd'), type="password")
                
                # Afegim el selector d'idioma en el moment del registre
                nou_idioma = st.selectbox("Idioma / Language", options=["ca", "es"], format_func=lambda x: "Català" if x == "ca" else "Español")
                
                if st.form_submit_button(t('register'), type="primary", use_container_width=True):
                    try:
                        run_query("INSERT INTO usuaris (username, password, language) VALUES (?, ?, ?)", (nou_usuari, nova_contra, nou_idioma))
                        st.success(t('succ_reg'))
                    except sqlite3.IntegrityError:
                        st.error(t('err_reg'))
    st.stop()

# ==========================================
# 5. SIDEBAR (LOGOTIP BLANC, NAVEGACIÓ)
# ==========================================
USUARI = st.session_state.usuari_actual

try: st.sidebar.image("sorigue_logo_RGB-positivo.png", use_container_width=True)
except: st.sidebar.markdown("<h1>Sorigué</h1>", unsafe_allow_html=True)

st.sidebar.write(f"👤 {t('conn_as')} **{USUARI}**")
st.sidebar.markdown("<br>", unsafe_allow_html=True)

lang_idx = 0 if st.session_state.idioma == 'ca' else 1
idioma_triat = st.sidebar.selectbox(t('lang'), ['ca', 'es'], index=lang_idx, format_func=lambda x: "Català" if x=='ca' else "Castellano", key="idioma_selector", on_change=canviar_idioma)
st.session_state.idioma = idioma_triat

mesos_disponibles = [row[0] for row in fetch_query("SELECT DISTINCT mes FROM big_rocks WHERE username=?", (USUARI,))]
mes_ini = "Juliol 2026" if st.session_state.idioma == 'ca' else "Julio 2026"
if mes_ini not in mesos_disponibles: mesos_disponibles.insert(0, mes_ini)

mes_seleccionat = st.sidebar.selectbox(t('nav_months'), mesos_disponibles, index=mesos_disponibles.index(st.session_state.mes_actual) if st.session_state.mes_actual in mesos_disponibles else 0)
st.session_state.mes_actual = mes_seleccionat
MES = st.session_state.mes_actual

mes_tancat_db = fetch_query("SELECT * FROM mesos_tancats WHERE username=? AND mes=?", (USUARI, MES))
es_tancat = len(mes_tancat_db) > 0

if es_tancat:
    st.sidebar.error(t('closed_month'))
    if st.sidebar.button(t('unlock'), use_container_width=True):
        run_query("DELETE FROM mesos_tancats WHERE username=? AND mes=?", (USUARI, MES))
        st.rerun()
else:
    st.sidebar.success(t('open_month'))

st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
if st.sidebar.button(t('logout'), use_container_width=True):
    st.session_state.usuari_actual = None
    st.rerun()

# ==========================================
# 6. PANTALLA PRINCIPAL: DASHBOARD
# ==========================================
if 'pantalla' not in st.session_state: st.session_state.pantalla = 'dashboard'
if 'mostrar_formulari_br' not in st.session_state: st.session_state.mostrar_formulari_br = False

if st.session_state.pantalla == 'dashboard':
    st.write("<br>", unsafe_allow_html=True)
        
    col_titol, col_boto = st.columns([3, 1])
    with col_titol: 
        st.title(f"Dashboard · {MES}")
    with col_boto:
        st.write("<br>", unsafe_allow_html=True)
        if not es_tancat:
            st.button(t('eval_close'), type="primary", use_container_width=True, on_click=lambda: st.session_state.update(pantalla='resum'))
    
    st.write("<br>", unsafe_allow_html=True)

    brs = fetch_query("SELECT id, nom, persones, reunions, notes_progres, pregunta, passos FROM big_rocks WHERE username=? AND mes=?", (USUARI, MES))

    if not brs:
        st.info(t('no_br'))
    else:
        for br in brs:
            br_id = br[0]
            with st.container():
                st.markdown(f"## {br[1]}")
                st.caption(f"{t('key_ppl')} {br[2]} &nbsp;&nbsp;|&nbsp;&nbsp; {t('key_meet')} {br[3]}")
                
                tars = fetch_query("SELECT id, num, descripcio, progres FROM tars WHERE id_br=? AND estat='Actiu'", (br_id,))
                progres_mitja = int(sum(t[3] for t in tars) / len(tars)) if tars else 0
                
                progress_bar_colorida(progres_mitja, is_global=True)
                st.write("") 
                
                for tar in tars:
                    tar_id, num, desc, progres = tar
                    if progres not in [0, 50, 100]: progres = 0
                    
                    col1, col2, col3, col4, col5 = st.columns([1, 4, 3, 2, 0.5])
                    with col1: 
                        st.markdown(f"<div style='margin-top:10px; font-weight:bold; color:#666;'>{num}</div>", unsafe_allow_html=True)
                    with col2:
                        k_desc = f"desc_{tar_id}"
                        st.text_input(t('desc'), value=desc, key=k_desc, label_visibility="collapsed", disabled=es_tancat, placeholder=t('desc'),
                                      on_change=lambda tid=tar_id, k=k_desc: update_db_val("tars", "descripcio", st.session_state[k], tid))
                    with col3:
                        k_radio = f"radio_{tar_id}"
                        st.radio(t('state'), options=[0, 50, 100], format_func=lambda x: f"{x}%", 
                                 index=[0, 50, 100].index(progres), horizontal=True, key=k_radio, 
                                 label_visibility="collapsed", disabled=es_tancat,
                                 on_change=lambda tid=tar_id, k=k_radio: update_db_val("tars", "progres", st.session_state[k], tid))
                    with col4: progress_bar_colorida(progres, is_global=False)
                    with col5: st.button("🗑️", key=f"btn_{tar_id}", on_click=arxivar_tar, args=(tar_id,), disabled=es_tancat, help="Eliminar")
                
                st.write("<br>", unsafe_allow_html=True)
                with st.expander(f"➕ {t('details')}", expanded=False):
                    notes = st.text_area(t('prog'), value=br[4], key=f"notes_{br_id}", disabled=es_tancat)
                    preg = st.text_input(t('need'), value=br[5], key=f"preg_{br_id}", disabled=es_tancat)
                    passos = st.text_input(t('next_steps'), value=br[6], key=f"passos_{br_id}", disabled=es_tancat)
                    if not es_tancat:
                        st.button(t('save_notes'), key=f"save_{br_id}", on_click=lambda bid=br_id, n=notes, p=preg, ps=passos: run_query("UPDATE big_rocks SET notes_progres=?, pregunta=?, passos=? WHERE id=?", (n, p, ps, bid)))

    if not es_tancat:
        st.write("<br>", unsafe_allow_html=True)
        if st.button(t('create_br'), type="primary"):
            st.session_state.mostrar_formulari_br = not st.session_state.mostrar_formulari_br

        if st.session_state.mostrar_formulari_br:
            with st.container():
                with st.form("form_nova_br"):
                    st.subheader(t('config_br'))
                    nou_nom = st.text_input(t('title_br'))
                    c1, c2 = st.columns(2)
                    persones = c1.text_input(t('key_ppl').replace('*', '').strip())
                    reunions = c2.text_input(t('key_meet').replace('*', '').strip())
                    st.markdown("#### TARs")
                    t1, t2, t3, t4 = st.text_input("TAR 1"), st.text_input("TAR 2"), st.text_input("TAR 3"), st.text_input("TAR 4")
                    
                    if st.form_submit_button(t('save'), type="primary"):
                        if nou_nom:
                            c = run_query("INSERT INTO big_rocks (username, mes, nom, persones, reunions, notes_progres, pregunta, passos) VALUES (?, ?, ?, ?, ?, '', '', '')", (USUARI, MES, nou_nom, persones, reunions))
                            for i, desc_tar in enumerate([t1, t2, t3, t4]):
                                if desc_tar.strip():
                                    run_query("INSERT INTO tars (id_br, num, descripcio, progres, estat) VALUES (?, ?, ?, ?, 'Actiu')", (c.lastrowid, f"TAR {i+1}", desc_tar, 0))
                            st.session_state.mostrar_formulari_br = False
                            st.rerun()

# ==========================================
# 7. PANTALLA DE RESUM (TANCAMENT)
# ==========================================
elif st.session_state.pantalla == 'resum':
    st.write("<br>", unsafe_allow_html=True)
    st.title(f"{t('summary')} · {MES}")
    
    brs = fetch_query("SELECT id, nom, persones, reunions FROM big_rocks WHERE username=? AND mes=?", (USUARI, MES))
    tars_completats, tars_pendents = [], []
    sumatori_progres, total_tars = 0, 0
    
    for br in brs:
        tars = fetch_query("SELECT descripcio, progres FROM tars WHERE id_br=? AND estat='Actiu'", (br[0],))
        for t_val in tars:
            sumatori_progres += t_val[1]
            total_tars += 1
            if t_val[1] == 100: tars_completats.append(f"**{br[1]}** ➡️ {t_val[0]}")
            else: tars_pendents.append(f"**{br[1]}** ➡️ {t_val[0]} ({t_val[1]}%)")
    
    compliment_global = int(sumatori_progres / total_tars) if total_tars > 0 else 0
    
    with st.container():
        st.markdown(f"### {t('global_comp')}")
        progress_bar_colorida(compliment_global, is_global=True)
        st.write("<br>", unsafe_allow_html=True)
        
        ce, ct = st.columns(2)
        with ce:
            st.success(f"#### ✅ {t('successes')}")
            for t_val in tars_completats: st.markdown(f"- {t_val}")
        with ct:
            st.warning(f"#### 🔄 {t('carry_over')}")
            for t_val in tars_pendents: st.markdown(f"- {t_val}")
        
        st.write("<br>", unsafe_allow_html=True)

    def confirmar_tancament():
        run_query("INSERT OR IGNORE INTO mesos_tancats (username, mes) VALUES (?, ?)", (USUARI, MES))
        
        mesos_idioma = t('months')
        parts = MES.split(" ")
        mes_actual_nom, any_actual = parts[0], int(parts[1])
        
        idx = -1
        for idi in ['ca', 'es']:
            if mes_actual_nom in TRANS[idi]['months']:
                idx = TRANS[idi]['months'].index(mes_actual_nom)
                break
                
        if idx != -1:
            if idx == 11: nou_mes = f"{mesos_idioma[0]} {any_actual + 1}"
            else: nou_mes = f"{mesos_idioma[idx+1]} {any_actual}"
        else:
            nou_mes = f"Next {any_actual}"
            
        brs_actuals = fetch_query("SELECT id, nom, persones, reunions FROM big_rocks WHERE username=? AND mes=?", (USUARI, MES))
        for br in brs_actuals:
            tars_pendents_db = fetch_query("SELECT num, descripcio, progres FROM tars WHERE id_br=? AND estat='Actiu' AND progres < 100", (br[0],))
            if tars_pendents_db:
                c = run_query("INSERT INTO big_rocks (username, mes, nom, persones, reunions, notes_progres, pregunta, passos) VALUES (?, ?, ?, ?, ?, '', '', '')", (USUARI, nou_mes, br[1], br[2], br[3]))
                for tar in tars_pendents_db:
                    run_query("INSERT INTO tars (id_br, num, descripcio, progres, estat) VALUES (?, ?, ?, ?, 'Actiu')", (c.lastrowid, tar[0], tar[1], tar[2]))
        
        st.session_state.mes_actual = nou_mes
        st.session_state.pantalla = 'dashboard'

    cb1, cb2, cb3 = st.columns([1, 2, 1])
    with cb1:
        st.button(t('cancel'), on_click=lambda: st.session_state.update(pantalla='dashboard'), use_container_width=True)
    with cb2:
        st.button(t('confirm_close'), on_click=confirmar_tancament, type="primary", use_container_width=True)