import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
from pathlib import Path

# =====================
# CONFIGURATION PAGE
# =====================
st.set_page_config(
    page_title="🔄 Comparaison Départements",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS moderne - Thème Feu
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
    
    .main-title {
        text-align: center;
        padding: 30px;
        background: linear-gradient(135deg, rgba(255,107,53,0.1) 0%, rgba(247,147,30,0.1) 100%);
        border-radius: 20px;
        border: 1px solid rgba(255,107,53,0.2);
        margin-bottom: 30px;
    }
    
    .dept-card {
        background: linear-gradient(135deg, rgba(255,107,53,0.1), rgba(255,204,0,0.05));
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255,107,53,0.2);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .dept-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(255,107,53,0.2);
    }
    
    .insight-box {
        background: linear-gradient(135deg, rgba(255,107,53,0.1), rgba(255,204,0,0.05));
        border-left: 4px solid #ff6b35;
        border-radius: 10px;
        padding: 15px 20px;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# =====================
# CHEMINS RELATIFS
# =====================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# =====================
# CHARGEMENT DONNÉES
# =====================
@st.cache_data
def load_incendie_data():
    data_path = DATA_DIR / "incendies" / "incendies.parquet"
    
    if data_path.exists():
        df = pd.read_parquet(data_path)
        df = df.rename(columns={
            'Année': 'annee',
            'Département': 'departement',
            'Code INSEE': 'code_insee',
            'Commune': 'commune',
            'mois': 'mois',
            'surf_ha': 'surface_brulee'
        })
        # Nettoyer les données
        df = df.dropna(subset=['annee', 'departement'])
        df['annee'] = df['annee'].astype(int)
        df['mois'] = df['mois'].fillna(1).astype(int)
        df['surface_brulee'] = df['surface_brulee'].fillna(0)
        deps_paca = ['04', '05', '06', '13', '83', '84']
        df = df[df['departement'].astype(str).isin(deps_paca)]
        df['departement'] = df['departement'].astype(str).str.zfill(2)
        return df
    return pd.DataFrame()

df = load_incendie_data()

# Dictionnaires
DEPT_NOMS = {
    "04": "Alpes-de-Haute-Provence",
    "05": "Hautes-Alpes",
    "06": "Alpes-Maritimes",
    "13": "Bouches-du-Rhône",
    "83": "Var",
    "84": "Vaucluse"
}

noms_mois = {
    1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril", 
    5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août", 
    9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
}

# Couleurs par département
dept_colors = {
    "04": "#ffcc00",
    "05": "#66ccff",
    "06": "#ff9966",
    "13": "#ff6b35",
    "83": "#cc0000",
    "84": "#ff9933"
}

# =====================
# SIDEBAR
# =====================
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <span style="font-size: 3rem;">🔥</span>
            <h2 style="margin: 10px 0; font-size: 1.5rem;">PyroViz PACA</h2>
            <p style="color: #b0a090; font-size: 0.8rem;">Comparaison Départements</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
        <p style="color: #ff6b35; font-size: 0.9rem; margin-bottom: 15px; padding-left: 5px;">🧭 Navigation</p>
    """, unsafe_allow_html=True)
    
    st.page_link("app.py", label="🏠 Accueil")
    st.page_link("pages/1_Carte.py", label="🗺️ Carte des Incendies")
    st.page_link("pages/2_Analyses.py", label="📈 Analyses Temporelles")
    st.page_link("pages/3_Comparaison.py", label="🔄 Comparaison Départements")
    
    st.markdown("---")
    
    st.markdown("### 📍 Départements à comparer")
    
    if len(df) > 0:
        all_deps = sorted(df["departement"].dropna().unique().tolist())
        selected_deps = st.multiselect(
            "Sélectionner les départements",
            options=all_deps,
            default=all_deps,
            format_func=lambda x: f"📍 {x} - {DEPT_NOMS.get(x, x)}"
        )
        
        st.markdown("---")
        
        st.markdown("### 📅 Période")
        
        annees = sorted(df["annee"].dropna().unique().astype(int))
        year_range = st.slider(
            "Plage d'années",
            min_value=int(min(annees)),
            max_value=int(max(annees)),
            value=(1973, 2022),
            step=1
        )
    
    st.markdown("---")
    
    st.markdown("""
        <div style="
            background: rgba(255,107,53,0.1);
            border-radius: 15px;
            padding: 15px;
            border: 1px solid rgba(255,107,53,0.2);
            text-align: center;
        ">
            <p style="color: #ff6b35; margin: 0; font-size: 0.85rem;">
                🔥 Département le plus touché :<br>
                <strong style="font-size: 1.1rem;">Le Var (83)</strong>
            </p>
        </div>
    """, unsafe_allow_html=True)

# =====================
# FILTRAGE
# =====================
if len(df) > 0:
    df_filtered = df[
        (df["annee"] >= year_range[0]) & 
        (df["annee"] <= year_range[1]) &
        (df["departement"].isin(selected_deps))
    ]
else:
    df_filtered = df

# =====================
# TITRE
# =====================
st.markdown("""
    <div class="main-title">
        <h1>🔄 Comparaison Inter-Départementale</h1>
        <p style="color: #b0a090;">Analyse comparative • Gradient littoral-montagne • Disparités territoriales</p>
    </div>
""", unsafe_allow_html=True)

if len(df) > 0:
    deps_label = ", ".join(selected_deps) if len(selected_deps) <= 3 else f"{len(selected_deps)} départements"
    st.markdown(f"""
        <div style="
            background: linear-gradient(90deg, rgba(255,107,53,0.15) 0%, rgba(247,147,30,0.15) 100%);
            border-radius: 15px;
            padding: 15px 25px;
            border: 1px solid rgba(255,107,53,0.2);
            margin-bottom: 20px;
            text-align: center;
        ">
            <span style="color: #e8d8c8;">📍 <strong style="color: #ff6b35;">{deps_label}</strong> | 
            📅 <strong style="color: #ff6b35;">{year_range[0]} - {year_range[1]}</strong></span>
        </div>
    """, unsafe_allow_html=True)

# =====================
# CARTES DE SYNTHÈSE PAR DÉPARTEMENT
# =====================
st.markdown("### 📊 Bilan par Département")

if len(df_filtered) > 0:
    dept_stats = df_filtered.groupby("departement").agg({
        "surface_brulee": "sum"
    }).reset_index()
    dept_stats["nb_incendies"] = df_filtered.groupby("departement").size().values
    dept_stats["nom"] = dept_stats["departement"].map(DEPT_NOMS)
    
    cols = st.columns(min(len(selected_deps), 6))
    
    for i, dep in enumerate(selected_deps[:6]):
        with cols[i % len(cols)]:
            dep_data = dept_stats[dept_stats["departement"] == dep]
            if len(dep_data) > 0:
                nb = int(dep_data["nb_incendies"].values[0])
                surface = dep_data["surface_brulee"].values[0]
                nom = DEPT_NOMS.get(dep, dep)
                
                st.markdown(f"""
                    <div class="dept-card">
                        <p style="font-size: 2rem; margin: 0;">🔥</p>
                        <h4 style="color: #ff6b35; margin: 10px 0;">{dep} - {nom}</h4>
                        <p style="color: #ffcc00; font-size: 1.8rem; font-weight: 700; margin: 5px 0;">{nb:,}</p>
                        <p style="color: #b0a090; font-size: 0.8rem; margin: 0;">incendies</p>
                        <p style="color: #ff9933; font-size: 1.4rem; font-weight: 600; margin: 10px 0 5px 0;">{surface:,.0f} ha</p>
                        <p style="color: #b0a090; font-size: 0.8rem; margin: 0;">surfaces brûlées</p>
                    </div>
                """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================
# GRAPHIQUE 1: COMPARAISON SURFACES BRÛLÉES
# =====================
st.markdown("### 🌲 Surfaces Brûlées Cumulées par Département")

if len(df_filtered) > 0:
    dept_stats_sorted = dept_stats.sort_values("surface_brulee", ascending=True)
    
    fig_surface = px.bar(
        dept_stats_sorted,
        x="surface_brulee",
        y="departement",
        orientation="h",
        labels={"surface_brulee": "Surface brûlée (ha)", "departement": "Département"},
        color="surface_brulee",
        color_continuous_scale=[[0, "#ffcc00"], [0.3, "#ff9900"], [0.6, "#ff6b35"], [1, "#cc0000"]],
        text="surface_brulee"
    )
    
    fig_surface.update_traces(
        texttemplate='%{text:,.0f} ha',
        textposition='outside',
        textfont=dict(color="#e8d8c8")
    )
    
    fig_surface.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8d8c8"),
        xaxis=dict(gridcolor="rgba(255,107,53,0.1)", title_font=dict(color="#ff6b35")),
        yaxis=dict(gridcolor="rgba(255,107,53,0.1)", title_font=dict(color="#ff6b35")),
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig_surface, use_container_width=True)

st.markdown("""
    <div class="insight-box">
        <p>💡 <strong>Observation :</strong> Le <strong>Var (83)</strong> est le département le plus sévèrement touché 
        avec plus de 140 000 hectares brûlés sur la période. Les <strong>Bouches-du-Rhône (13)</strong> suivent, 
        confirmant la forte pression incendiaire sur la frange méditerranéenne littorale.</p>
    </div>
""", unsafe_allow_html=True)

# =====================
# GRAPHIQUE 2: ÉVOLUTION COMPARÉE
# =====================
st.markdown("### 📈 Évolution Comparée du Nombre d'Incendies")

if len(df_filtered) > 0:
    evolution = df_filtered.groupby(["annee", "departement"]).size().reset_index(name="nb_incendies")
    
    fig_evolution = px.line(
        evolution,
        x="annee",
        y="nb_incendies",
        color="departement",
        labels={"annee": "Année", "nb_incendies": "Nombre d'incendies", "departement": "Département"},
        color_discrete_map=dept_colors
    )
    
    fig_evolution.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8d8c8"),
        xaxis=dict(gridcolor="rgba(255,107,53,0.1)", title_font=dict(color="#ff6b35")),
        yaxis=dict(gridcolor="rgba(255,107,53,0.1)", title_font=dict(color="#ff6b35")),
        legend=dict(
            bgcolor="rgba(0,0,0,0.3)",
            bordercolor="rgba(255,107,53,0.3)",
            borderwidth=1
        ),
        height=450
    )
    
    fig_evolution.update_traces(line=dict(width=2))
    
    st.plotly_chart(fig_evolution, use_container_width=True)

# =====================
# GRAPHIQUE 3: COMPARAISON SAISONNALITÉ
# =====================
st.markdown("### 📅 Profil Saisonnier par Département")

if len(df_filtered) > 0:
    saisonnalite = df_filtered.groupby(["mois", "departement"]).size().reset_index(name="nb_incendies")
    saisonnalite["mois_nom"] = saisonnalite["mois"].map(noms_mois)
    
    fig_saison = px.bar(
        saisonnalite,
        x="mois_nom",
        y="nb_incendies",
        color="departement",
        barmode="group",
        labels={"mois_nom": "Mois", "nb_incendies": "Nombre d'incendies", "departement": "Département"},
        color_discrete_map=dept_colors
    )
    
    fig_saison.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8d8c8"),
        xaxis=dict(gridcolor="rgba(255,107,53,0.1)", tickangle=45),
        yaxis=dict(gridcolor="rgba(255,107,53,0.1)"),
        legend=dict(
            bgcolor="rgba(0,0,0,0.3)",
            bordercolor="rgba(255,107,53,0.3)",
            borderwidth=1
        ),
        height=450
    )
    
    st.plotly_chart(fig_saison, use_container_width=True)

# =====================
# GRAPHIQUE 4: RADAR COMPARATIF
# =====================
st.markdown("### 🎯 Profil de Risque par Département")

if len(df_filtered) > 0 and len(selected_deps) >= 2:
    dept_profile = df_filtered.groupby("departement").agg({
        "surface_brulee": ["sum", "mean"]
    }).reset_index()
    dept_profile.columns = ["departement", "total_surface", "moy_surface"]
    dept_profile["nb_incendies"] = df_filtered.groupby("departement").size().values
    dept_profile["moy_incendies"] = dept_profile["nb_incendies"] / (year_range[1] - year_range[0] + 1)
    
    # Normalisation
    for col in ["nb_incendies", "moy_incendies", "total_surface", "moy_surface"]:
        max_val = dept_profile[col].max()
        dept_profile[f"{col}_norm"] = dept_profile[col] / max_val if max_val > 0 else 0
    
    fig_radar = go.Figure()
    
    categories = ['Total Incendies', 'Moy. Incendies/an', 'Total Surface', 'Moy. Surface/inc.']
    
    for dep in selected_deps[:4]:
        dep_data = dept_profile[dept_profile["departement"] == dep]
        if len(dep_data) > 0:
            values = [
                dep_data["nb_incendies_norm"].values[0],
                dep_data["moy_incendies_norm"].values[0],
                dep_data["total_surface_norm"].values[0],
                dep_data["moy_surface_norm"].values[0]
            ]
            values.append(values[0])
            
            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=categories + [categories[0]],
                fill='toself',
                name=f"{dep} - {DEPT_NOMS.get(dep, dep)}",
                line=dict(color=dept_colors.get(dep, "#ff6b35"))
            ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                gridcolor="rgba(255,107,53,0.2)",
                linecolor="rgba(255,107,53,0.3)"
            ),
            angularaxis=dict(
                gridcolor="rgba(255,107,53,0.2)",
                linecolor="rgba(255,107,53,0.3)"
            ),
            bgcolor="rgba(0,0,0,0)"
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8d8c8"),
        legend=dict(
            bgcolor="rgba(0,0,0,0.3)",
            bordercolor="rgba(255,107,53,0.3)",
            borderwidth=1
        ),
        height=500
    )
    
    st.plotly_chart(fig_radar, use_container_width=True)

st.markdown("""
    <div class="insight-box">
        <p>💡 <strong>Gradient Littoral-Montagne :</strong> On observe un gradient net avec les départements 
        montagnards comme les <strong>Hautes-Alpes (05)</strong> qui présentent les surfaces brûlées les plus faibles, 
        tandis que les départements littoraux méditerranéens sont les plus exposés.</p>
    </div>
""", unsafe_allow_html=True)

# =====================
# TABLEAU RÉCAPITULATIF
# =====================
st.markdown("### 📋 Tableau Récapitulatif")

if len(df_filtered) > 0:
    recap_table = dept_stats.copy()
    recap_table = recap_table[["departement", "nom", "nb_incendies", "surface_brulee"]]
    recap_table.columns = ["Code", "Département", "Nombre d'Incendies", "Surface Brûlée (ha)"]
    recap_table = recap_table.sort_values("Surface Brûlée (ha)", ascending=False)
    recap_table["Surface Brûlée (ha)"] = recap_table["Surface Brûlée (ha)"].round(2)
    
    st.dataframe(
        recap_table,
        width="stretch",
        hide_index=True
    )

# =====================
# FOOTER
# =====================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
    <div style="
        text-align: center;
        padding: 20px;
        background: rgba(255,107,53,0.05);
        border-radius: 15px;
        border: 1px solid rgba(255,107,53,0.1);
    ">
        <p style="color: #8a7a6a; margin: 0; font-size: 0.85rem;">
            📊 Données : <strong>1973-2022</strong> | 
            🔄 Comparaison : <strong>6 départements PACA</strong> | 
            🎓 Master 2 GMS |
            👩‍💻 <strong style="color: #ff6b35;">Alia AL MOBARIK</strong>
        </p>
    </div>
""", unsafe_allow_html=True)
