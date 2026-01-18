import streamlit as st
import os

# =====================
# CONFIGURATION PAGE D'ACCUEIL
# =====================
st.set_page_config(
    page_title="🔥 Incendies PACA Dashboard",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS moderne - Thème Feu (Orange/Rouge)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');
    
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #1a0a0a 0%, #2d1810 50%, #3d1a0a 100%);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #3d1a0a 0%, #1a0a0a 100%);
        border-right: 1px solid rgba(255,107,53,0.2);
    }
    
    h1, h2, h3 {
        font-family: 'Montserrat', sans-serif !important;
        background: linear-gradient(90deg, #ff6b35, #f7931e, #ffcc00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
    }
    
    .welcome-box {
        text-align: center;
        padding: 60px 40px;
        background: linear-gradient(135deg, rgba(255,107,53,0.1) 0%, rgba(247,147,30,0.1) 100%);
        border-radius: 30px;
        border: 1px solid rgba(255,107,53,0.3);
        margin: 40px 0;
        box-shadow: 0 0 60px rgba(255,107,53,0.1);
    }
    
    .welcome-box h1 {
        font-size: 3.5rem !important;
        margin-bottom: 20px !important;
    }
    
    .feature-card {
        background: rgba(255, 107, 53, 0.08);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 107, 53, 0.2);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(255, 107, 53, 0.25);
        border-color: rgba(255, 107, 53, 0.5);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 15px;
    }
    
    .feature-title {
        color: #ff6b35;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 10px;
    }
    
    .feature-desc {
        color: #b0a090;
        font-size: 0.95rem;
    }
    
    .stat-box {
        text-align: center;
        padding: 25px;
        background: rgba(255,107,53,0.1);
        border-radius: 15px;
        border: 1px solid rgba(255,107,53,0.2);
        transition: all 0.3s ease;
    }
    
    .stat-box:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 30px rgba(255,107,53,0.2);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #ff6b35, #ffcc00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stat-label {
        color: #b0a090;
        font-size: 0.9rem;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# =====================
# SIDEBAR
# =====================
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <span style="font-size: 4rem;">🔥</span>
            <h2 style="margin: 15px 0; font-size: 1.8rem;">PyroViz PACA</h2>
            <p style="color: #b0a090; font-size: 0.9rem;">Observatoire des Incendies de Forêt</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
        <p style="color: #ff6b35; font-size: 0.9rem; margin-bottom: 15px; padding-left: 10px;">🧭 Navigation</p>
    """, unsafe_allow_html=True)
    
    st.page_link("app.py", label="🏠 Accueil", icon=None)
    st.page_link("pages/1_Carte.py", label="🗺️ Carte des Incendies", icon=None)
    st.page_link("pages/2_Analyses.py", label="📈 Analyses Temporelles", icon=None)
    st.page_link("pages/3_Comparaison.py", label="🔄 Comparaison Départements", icon=None)

# =====================
# CONTENU PRINCIPAL
# =====================

# Titre de bienvenue
st.markdown("""
    <div class="welcome-box">
        <h1>🔥 PyroViz PACA</h1>
        <p style="color: #b0a090; font-size: 1.3rem; margin: 0;">
            Observatoire des Incendies de Forêt en Provence-Alpes-Côte d'Azur
        </p>
        <p style="color: #8a7a6a; font-size: 1rem; margin-top: 15px;">
            Analyse spatio-temporelle • Période 1973-2022 • 50 ans de données
        </p>
    </div>
""", unsafe_allow_html=True)

# Statistiques clés
st.markdown("### 📊 Chiffres Clés (1973-2022)")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
        <div class="stat-box">
            <div class="stat-number">50</div>
            <div class="stat-label">Années d'étude</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="stat-box">
            <div class="stat-number">6</div>
            <div class="stat-label">Départements PACA</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="stat-box">
            <div class="stat-number">118k+</div>
            <div class="stat-label">Incendies recensés</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
        <div class="stat-box">
            <div class="stat-number">~400k ha</div>
            <div class="stat-label">Surfaces brûlées</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Fonctionnalités
st.markdown("### 🚀 Fonctionnalités du Dashboard")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🗺️</div>
            <div class="feature-title">Carte Interactive</div>
            <div class="feature-desc">
                Visualisation spatiale des incendies par commune et département.
                Heatmaps de densité, zones à risque et surfaces brûlées.
                Filtres dynamiques par période et territoire.
            </div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📈</div>
            <div class="feature-title">Analyses Temporelles</div>
            <div class="feature-desc">
                Évolution annuelle du nombre d'incendies et des surfaces brûlées.
                Saisonnalité et identification des périodes critiques.
                Tendances sur 50 ans et événements majeurs.
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔄</div>
            <div class="feature-title">Comparaison Territoriale</div>
            <div class="feature-desc">
                Analyse comparative entre les 6 départements de la région PACA.
                Identification des zones les plus vulnérables.
                Gradient littoral-montagne et facteurs de risque.
            </div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Aide à la Décision</div>
            <div class="feature-desc">
                Outils de prévention et de sensibilisation.
                Identification des pics historiques (2003, 1989, 1979).
                Support pour les politiques de gestion forestière.
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Zone d'étude
st.markdown("### 🌍 Zone d'Étude : Région PACA")

col_info1, col_info2 = st.columns(2)

with col_info1:
    st.markdown("""
        <div style="
            background: rgba(255,107,53,0.08);
            border-radius: 20px;
            padding: 25px;
            border: 1px solid rgba(255,107,53,0.2);
        ">
            <h4 style="color: #ff6b35; margin-bottom: 15px;">📍 6 Départements</h4>
            <ul style="color: #b0a090; line-height: 2;">
                <li><strong style="color: #ffcc00;">04</strong> - Alpes-de-Haute-Provence</li>
                <li><strong style="color: #ffcc00;">05</strong> - Hautes-Alpes</li>
                <li><strong style="color: #ffcc00;">06</strong> - Alpes-Maritimes</li>
                <li><strong style="color: #ffcc00;">13</strong> - Bouches-du-Rhône</li>
                <li><strong style="color: #ffcc00;">83</strong> - Var (le plus touché)</li>
                <li><strong style="color: #ffcc00;">84</strong> - Vaucluse</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with col_info2:
    st.markdown("""
        <div style="
            background: rgba(255,107,53,0.08);
            border-radius: 20px;
            padding: 25px;
            border: 1px solid rgba(255,107,53,0.2);
        ">
            <h4 style="color: #ff6b35; margin-bottom: 15px;">🌡️ Facteurs de Risque</h4>
            <ul style="color: #b0a090; line-height: 2;">
                <li>🔥 Climat méditerranéen sec</li>
                <li>💨 Vents violents (Mistral)</li>
                <li>🌲 Végétation inflammable</li>
                <li>👥 Forte pression anthropique</li>
                <li>☀️ Étés chauds et prolongés</li>
                <li>🏖️ Fréquentation touristique</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style="
        text-align: center;
        padding: 25px;
        background: rgba(255,107,53,0.05);
        border-radius: 15px;
        border: 1px solid rgba(255,107,53,0.1);
    ">
        <p style="color: #8a7a6a; margin: 0; font-size: 0.9rem;">
            🎓 <strong>Projet M2 GMS</strong> | 
            📊 Données <strong>1973-2022</strong> | 
            🛠️ Streamlit, Folium, Plotly |
            👩‍💻 <strong style="color: #ff6b35;">Alia AL MOBARIK</strong>
        </p>
    </div>
""", unsafe_allow_html=True)
