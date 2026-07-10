import streamlit as st
import pandas as pd

# 1. Configuració de la pàgina
st.set_page_config(page_title="Sistema Big Rocks", layout="wide", page_icon="🪨")

st.title("🪨 Dashboard Big Rocks")
st.subheader("Juliol 2026")

# 2. Inicialització de dades simulades (La teva futura Base de Dades)
if 'tars' not in st.session_state:
    st.session_state.tars = [
        {"id": 1, "big_rock": "FACTURAR ABANS DE VACANCES", "tasca": "Bimsa - Via Favència", "progres": 40, "estat": "Actiu"},
        {"id": 2, "big_rock": "FACTURAR ABANS DE VACANCES", "tasca": "Aura", "progres": 100, "estat": "Actiu"},
        {"id": 3, "big_rock": "REVISAR GEOS", "tasca": "AMB Hotel Entitats", "progres": 10, "estat": "Actiu"},
        {"id": 4, "big_rock": "REVISAR GEOS", "tasca": "Engestur Montcada", "progres": 80, "estat": "Actiu"}
    ]

# Funció per arxivar un TAR
def arxivar_tar(tar_id):
    for tar in st.session_state.tars:
        if tar['id'] == tar_id:
            tar['estat'] = "Arxivat"

# 3. Visualització de les Big Rocks (Les Targetes)
tars_actius = [tar for tar in st.session_state.tars if tar['estat'] == "Actiu"]
df_tars = pd.DataFrame(tars_actius)

if not df_tars.empty:
    big_rocks_uniques = df_tars['big_rock'].unique()

    for br in big_rocks_uniques:
        # Creem una "targeta" visual per a cada Big Rock
        with st.container():
            st.markdown(f"### 🎯 {br}")
            st.markdown("---")
            
            tars_br = df_tars[df_tars['big_rock'] == br]
            
            for index, row in tars_br.iterrows():
                col1, col2, col3, col4 = st.columns([4, 4, 1, 1])
                
                with col1:
                    st.write(f"**{row['tasca']}**")
                
                with col2:
                    # Slider per controlar l'avenç
                    nou_progres = st.slider(
                        "Progrés", 
                        min_value=0, max_value=100, 
                        value=row['progres'], 
                        step=10, 
                        key=f"slider_{row['id']}",
                        label_visibility="collapsed"
                    )
                    
                    # Actualitzem el progrés a la memòria
                    for tar in st.session_state.tars:
                        if tar['id'] == row['id']:
                            tar['progres'] = nou_progres
                
                with col3:
                    # Indicador visual de colors mitjançant emojis
                    if nou_progres == 100:
                        st.success("Completat ✅")
                    elif nou_progres >= 70:
                        st.info("Avançant 🟡")
                    else:
                        st.error("Aturat 🔴")
                
                with col4:
                    # Botó d'arxivar (s'esborra visualment)
                    st.button("🗑️ Arxivar", key=f"btn_{row['id']}", on_click=arxivar_tar, args=(row['id'],))
            
            # Espai per a notes
            st.text_input("Preguntes o Necessitats:", key=f"preg_{br}")
            st.text_input("Pròxims Passos:", key=f"passos_{br}")
            st.write("") # Espaiat
else:
    st.info("No hi ha cap Big Rock activa aquest mes.")

# 4. Lògica de Tancament de Mes
st.sidebar.title("Accions de Mes")
st.sidebar.markdown("Quan acabi el mes, fes clic aquí per traspassar.")

if st.sidebar.button("Avaluar i Tancar Mes", type="primary"):
    st.sidebar.markdown("### Resum del traspàs a Agost:")
    tars_a_traspassar = []
    
    for tar in st.session_state.tars:
        if tar['estat'] == "Actiu":
            if tar['progres'] == 100:
                st.sidebar.write(f"✅ {tar['tasca']} (No es traspassa)")
            else:
                st.sidebar.write(f"➡️ {tar['tasca']} (Es traspassa al {tar['progres']}%)")
                tars_a_traspassar.append(tar)
    
    if st.sidebar.button("Crear Agost 2026"):
        # Aquí aniria la connexió a la base de dades per guardar el nou mes
        st.toast('Mes d\'Agost creat amb èxit!', icon='🚀')