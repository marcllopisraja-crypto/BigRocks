import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Sistema Big Rocks", layout="wide", page_icon="🪨")

# 1. Variables d'estat inicials
if 'mes_actual' not in st.session_state:
    st.session_state.mes_actual = "Juliol 2026"

# Aquesta variable controlarà si estem veient el Dashboard o la Pantalla de Resum
if 'pantalla' not in st.session_state:
    st.session_state.pantalla = 'dashboard'

if 'mostrar_formulari_br' not in st.session_state:
    st.session_state.mostrar_formulari_br = False

if 'big_rocks' not in st.session_state:
    st.session_state.big_rocks = [
        {
            "id": 1,
            "nom": "FACTURAR ABANS DE VACANCES",
            "persones": "Coordinadors",
            "reunions": "Coordinadors",
            "tars": [
                {"id_tar": 11, "num": "TAR 1", "desc": "Bimsa - Via Favència (277k€)", "progres": 40, "estat": "Actiu"},
                {"id_tar": 12, "num": "TAR 2", "desc": "Aura (141k€)", "progres": 100, "estat": "Actiu"},
                {"id_tar": 13, "num": "TAR 3", "desc": "Bimsa - Xavier Benguerel (66k€)", "progres": 0, "estat": "Actiu"},
                {"id_tar": 14, "num": "TAR 4", "desc": "Bimsa - Locals Entença (23k€)", "progres": 0, "estat": "Actiu"}
            ],
            "notes_progres": "He hecho reuniones con todos los implicados (Eloi, Marisol,...)",
            "pregunta": "Necesitamos un técnico responsable de RRHH central...",
            "passos": "Definir fechas y formaciones de operarios 2026."
        },
        {
            "id": 2,
            "nom": "REVISAR GEOS",
            "persones": "Montse + David D.",
            "reunions": "Montse + David D.",
            "tars": [
                {"id_tar": 21, "num": "TAR 1", "desc": "AMB Hotel Entitats", "progres": 30, "estat": "Actiu"},
                {"id_tar": 22, "num": "TAR 2", "desc": "Engestur Montcada", "progres": 10, "estat": "Actiu"},
                {"id_tar": 23, "num": "TAR 3", "desc": "Palamós", "progres": 0, "estat": "Actiu"}
            ],
            "notes_progres": "He hecho reuniones con todos los implicados...",
            "pregunta": "Preguntar a Paco sobre como está la incorporación...",
            "passos": "Programar 2das reuniones para concretar los avances."
        }
    ]

# --- FUNCIONS DE LÒGICA ---

def arxivar_tar(br_id, tar_id):
    for br in st.session_state.big_rocks:
        if br['id'] == br_id:
            for tar in br['tars']:
                if tar['id_tar'] == tar_id:
                    tar['estat'] = "Arxivat"

def executar_traspas():
    noves_big_rocks = []
    
    for br in st.session_state.big_rocks:
        tars_pendents = [t for t in br['tars'] if t['estat'] == 'Actiu' and t['progres'] < 100]
        
        if tars_pendents:
            nova_br = br.copy()
            nova_br['tars'] = tars_pendents
            nova_br['notes_progres'] = "" 
            nova_br['pregunta'] = ""
            nova_br['passos'] = ""
            noves_big_rocks.append(nova_br)
            
    st.session_state.big_rocks = noves_big_rocks
    
    if "Juliol" in st.session_state.mes_actual:
        st.session_state.mes_actual = "Agost 2026"
    else:
        st.session_state.mes_actual = "Setembre 2026"
        
    st.session_state.pantalla = 'dashboard' # Tornem a la pantalla principal

def anar_a_resum():
    st.session_state.pantalla = 'resum'

def tornar_a_dashboard():
    st.session_state.pantalla = 'dashboard'

def afegir_nova_br(nom, persones, reunions, nom_tars):
    nou_id = random.randint(100, 9999)
    tars_nous = []
    
    for i, desc_tar in enumerate(nom_tars):
        if desc_tar.strip() != "":
            tars_nous.append({
                "id_tar": random.randint(10000, 99999), 
                "num": f"TAR {i+1}", 
                "desc": desc_tar, 
                "progres": 0, 
                "estat": "Actiu"
            })
            
    nova_br = {
        "id": nou_id,
        "nom": nom,
        "persones": persones,
        "reunions": reunions,
        "tars": tars_nous,
        "notes_progres": "",
        "pregunta": "",
        "passos": ""
    }
    
    st.session_state.big_rocks.append(nova_br)
    st.session_state.mostrar_formulari_br = False


# ==========================================
# PANTALLA 1: DASHBOARD PRINCIPAL
# ==========================================
if st.session_state.pantalla == 'dashboard':
    
    col_titol, col_boto = st.columns([3, 1])
    with col_titol:
        st.title("🪨 Dashboard Big Rocks")
        st.subheader(st.session_state.mes_actual)
    with col_boto:
        st.write("<br>", unsafe_allow_html=True)
        st.button("📊 Avaluar i Tancar Mes", type="primary", use_container_width=True, on_click=anar_a_resum)

    st.markdown("---")

    if not st.session_state.big_rocks:
        st.info("Totes les Big Rocks s'han completat! 🎉 Afegeix-ne de noves a sota.")
    else:
        for br in st.session_state.big_rocks:
            with st.container():
                st.markdown(f"## 🎯 {br['nom']}")
                st.caption(f"👥 **Persones clau:** {br['persones']} | 📅 **Reunions:** {br['reunions']}")
                
                tars_actius = [t for t in br['tars'] if t['estat'] == 'Actiu']
                progres_mitja = int(sum(t['progres'] for t in tars_actius) / len(tars_actius)) if tars_actius else 0
                
                st.progress(progres_mitja / 100, text=f"Avenç global de la Big Rock: {progres_mitja}%")
                st.markdown("---")
                
                for tar in tars_actius:
                    col1, col2, col3, col4 = st.columns([1, 4, 3, 1])
                    
                    with col1:
                        st.write(f"**{tar['num']}**")
                    with col2:
                        tar['desc'] = st.text_input("Descripció del TAR", value=tar['desc'], key=f"desc_{tar['id_tar']}", label_visibility="collapsed")
                    with col3:
                        tar['progres'] = st.slider("Progrés TAR", min_value=0, max_value=100, value=tar['progres'], step=10, key=f"slider_{tar['id_tar']}", label_visibility="collapsed")
                    with col4:
                        st.button("🗑️", key=f"btn_{tar['id_tar']}", on_click=arxivar_tar, args=(br['id'], tar['id_tar'],), help="Arxivar aquest TAR")
                
                with st.expander("📝 Detalls, Preguntes i Pròxims Passos", expanded=False):
                    br['notes_progres'] = st.text_area("Progreso en esta Big Rock:", value=br['notes_progres'], key=f"prog_text_{br['id']}")
                    br['pregunta'] = st.text_input("Pregunta o necesidad:", value=br['pregunta'], key=f"preg_{br['id']}")
                    br['passos'] = st.text_input("Próximos pasos:", value=br['passos'], key=f"passos_{br['id']}")
                
                st.write("<br>", unsafe_allow_html=True)

    # ZONA DE CREACIÓ DE NOVES BIG ROCKS
    st.markdown("---")
    if st.button("➕ Crear Nova Big Rock"):
        st.session_state.mostrar_formulari_br = not st.session_state.mostrar_formulari_br

    if st.session_state.mostrar_formulari_br:
        with st.form("form_nova_br"):
            st.subheader("Configura la teva nova Big Rock")
            
            nou_nom = st.text_input("Títol de la Big Rock (Ex. DEPORTE Y MENTE SANA)")
            col_pers, col_reunions = st.columns(2)
            amb_persones = col_pers.text_input("Persones clau a prioritzar")
            amb_reunions = col_reunions.text_input("Reunions clau a prioritzar")
            
            st.markdown("#### Defineix els TARs inicials")
            nou_tar1 = st.text_input("TAR 1")
            nou_tar2 = st.text_input("TAR 2")
            nou_tar3 = st.text_input("TAR 3")
            nou_tar4 = st.text_input("TAR 4")
            
            btn_guardar = st.form_submit_button("Guardar Big Rock", type="primary")
            
            if btn_guardar:
                if nou_nom.strip() == "":
                    st.error("Has d'escriure un títol per a la Big Rock.")
                else:
                    afegir_nova_br(nou_nom, amb_persones, amb_reunions, [nou_tar1, nou_tar2, nou_tar3, nou_tar4])
                    st.rerun()


# ==========================================
# PANTALLA 2: RESUM DEL MES I TANCAMENT
# ==========================================
elif st.session_state.pantalla == 'resum':
    
    st.title(f"📊 Resum de Tancament - {st.session_state.mes_actual}")
    st.markdown("Abans de generar el mes següent, revisem com ha anat:")
    
    # Recollim estadístiques
    tars_completats = []
    tars_pendents = []
    totes_persones = set()
    totes_reunions = set()
    
    for br in st.session_state.big_rocks:
        if br['persones']: totes_persones.add(br['persones'])
        if br['reunions']: totes_reunions.add(br['reunions'])
        
        for t in br['tars']:
            if t['estat'] == 'Actiu':
                if t['progres'] == 100:
                    tars_completats.append(f"{br['nom']} ➡️ {t['desc']}")
                else:
                    tars_pendents.append(f"{br['nom']} ➡️ {t['desc']} ({t['progres']}%)")
                    
    # Blocs visuals clau inspirats en la teva imatge
    st.markdown("<br>", unsafe_allow_html=True)
    col_p, col_r = st.columns(2)
    
    with col_p:
        st.info(f"### 👥 PERSONAS CLAVES A PRIORIZAR\n" + "\n".join([f"- {p}" for p in totes_persones if p]))
    
    with col_r:
        st.info(f"### 📅 REUNIONES CLAVE A PRIORIZAR\n" + "\n".join([f"- {r}" for r in totes_reunions if r]))
        
    st.markdown("---")
    
    # Resum d'èxits i traspassos
    col_exit, col_traspas = st.columns(2)
    
    with col_exit:
        st.success("#### ✅ Èxits del mes (Es tanquen)")
        if tars_completats:
            for t in tars_completats:
                st.write(f"- {t}")
        else:
            st.write("Cap TAR completat al 100% encara.")
            
    with col_traspas:
        st.warning("#### 🔄 Es traspassen al mes següent")
        if tars_pendents:
            for t in tars_pendents:
                st.write(f"- {t}")
        else:
            st.write("No queda res pendent!")

    st.markdown("---")
    
    # Botons finals de decisió
    col_b1, col_b2, col_b3 = st.columns([1, 1, 1])
    with col_b1:
        st.button("⬅️ Cancel·lar i tornar", on_click=tornar_a_dashboard, use_container_width=True)
    with col_b3:
        st.button("🚀 Confirmar i Crear Mes Següent", on_click=executar_traspas, type="primary", use_container_width=True)