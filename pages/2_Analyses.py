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
    page_title="📈 Analyses Incendies",
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
    
    .chart-container {
        background: rgba(255, 107, 53, 0.05);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(255,107,53,0.15);
        margin-bottom: 20px;
    }
    
    .insight-box {
        background: linear-gradient(135deg, rgba(255,107,53,0.1), rgba(255,204,0,0.05));
        border-left: 4px solid #ff6b35;
        border-radius: 10px;
        padding: 15px 20px;
        margin: 15px 0;
    }
    
    .insight-box p {
        color: #e8d8c8;
        margin: 0;
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

noms_mois_emoji = {
    1: "🌨️ Janvier", 2: "❄️ Février", 3: "🌱 Mars", 4: "🌷 Avril", 
    5: "🌸 Mai", 6: "☀️ Juin", 7: "🔥 Juillet", 8: "🔥 Août", 
    9: "🍂 Septembre", 10: "🍁 Octobre", 11: "🌧️ Novembre", 12: "⛄ Décembre"
}

# =====================
# SIDEBAR
# =====================
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <span style="font-size: 3rem;">🔥</span>
            <h2 style="margin: 10px 0; font-size: 1.5rem;">PyroViz PACA</h2>
            <p style="color: #b0a090; font-size: 0.8rem;">Analyses Temporelles</p>
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
    
    st.markdown("### 🗺️ Filtres")
    
    if len(df) > 0:
        selected_dep = st.selectbox(
            "Département",
            ["Tous"] + sorted(df["departement"].dropna().unique().tolist()),
            format_func=lambda x: "🌍 Toute la région PACA" if x == "Tous" else f"📍 {x} - {DEPT_NOMS.get(x, x)}"
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
                📊 Période analysée<br>
                <strong>1973 - 2022</strong><br>
                <span style="font-size: 0.75rem; color: #b0a090;">50 années de données</span>
            </p>
        </div>
    """, unsafe_allow_html=True)

# =====================
# FILTRAGE
# =====================
df_filtered = df.copy()
if len(df) > 0 and selected_dep != "Tous":
    df_filtered = df_filtered[df_filtered["departement"] == selected_dep]

# =====================
# TITRE
# =====================
st.markdown("""
    <div class="main-title">
        <h1>📈 Analyses Temporelles des Incendies</h1>
        <p style="color: #b0a090;">Évolution sur 50 ans • Tendances • Saisonnalité</p>
    </div>
""", unsafe_allow_html=True)

if len(df) > 0:
    dep_label = "Région PACA" if selected_dep == "Tous" else f"{selected_dep} - {DEPT_NOMS.get(selected_dep, selected_dep)}"
    st.markdown(f"""
        <div style="
            background: linear-gradient(90deg, rgba(255,107,53,0.15) 0%, rgba(247,147,30,0.15) 100%);
            border-radius: 15px;
            padding: 15px 25px;
            border: 1px solid rgba(255,107,53,0.2);
            margin-bottom: 20px;
            text-align: center;
        ">
            <span style="color: #e8d8c8;">📍 <strong style="color: #ff6b35;">{dep_label}</strong> | 
            📅 <strong style="color: #ff6b35;">1973 - 2022</strong> |
            🔥 <strong style="color: #ff6b35;">{len(df_filtered):,}</strong> incendies</span>
        </div>
    """, unsafe_allow_html=True)

# =====================
# GRAPHIQUE 1: ÉVOLUTION ANNUELLE DU NOMBRE D'INCENDIES
# =====================
st.markdown("### 🔥 Évolution Annuelle du Nombre d'Incendies")

if len(df_filtered) > 0:
    incendies_annuels = df_filtered.groupby("annee").size().reset_index(name="nb_incendies")
    
    fig_nb = px.area(
        incendies_annuels,
        x="annee",
        y="nb_incendies",
        labels={"annee": "Année", "nb_incendies": "Nombre d'incendies"}
    )
    
    fig_nb.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8d8c8"),
        xaxis=dict(gridcolor="rgba(255,107,53,0.1)", title_font=dict(color="#ff6b35")),
        yaxis=dict(gridcolor="rgba(255,107,53,0.1)", title_font=dict(color="#ff6b35")),
        hovermode="x unified",
        height=400
    )
    
    fig_nb.update_traces(
        fill='tozeroy',
        fillcolor='rgba(255,107,53,0.3)',
        line=dict(color='#ff6b35', width=2)
    )
    
    # Annotation pour le pic
    max_row = incendies_annuels.loc[incendies_annuels["nb_incendies"].idxmax()]
    fig_nb.add_annotation(
        x=max_row["annee"],
        y=max_row["nb_incendies"],
        text=f"Pic: {int(max_row['annee'])}",
        showarrow=True,
        arrowhead=2,
        arrowcolor="#ffcc00",
        font=dict(color="#ffcc00")
    )
    
    st.plotly_chart(fig_nb, use_container_width=True)

st.markdown("""
    <div class="insight-box">
        <p>💡 <strong>Observation :</strong> On observe une tendance globale à la diminution du nombre d'incendies 
        depuis les pics historiques de la fin des années 1970-1980. Les années 1978, 1979 et 1985 se distinguent 
        par un volume d'incendies dépassant les 3 500 événements par an.</p>
    </div>
""", unsafe_allow_html=True)

# =====================
# GRAPHIQUE 2: ÉVOLUTION DES SURFACES BRÛLÉES
# =====================
st.markdown("### 🌲 Évolution Annuelle des Surfaces Brûlées")

if len(df_filtered) > 0:
    surface_annuelle = df_filtered.groupby("annee")["surface_brulee"].sum().reset_index()
    
    fig_surface = go.Figure()
    
    fig_surface.add_trace(go.Bar(
        x=surface_annuelle["annee"],
        y=surface_annuelle["surface_brulee"],
        marker=dict(
            color=surface_annuelle["surface_brulee"],
            colorscale=[[0, "#ffcc00"], [0.3, "#ff9900"], [0.5, "#ff6b35"], [0.7, "#cc0000"], [1, "#660000"]],
            showscale=True,
            colorbar=dict(title="Hectares", tickfont=dict(color="#e8d8c8"))
        ),
        hovertemplate="Année: %{x}<br>Surface: %{y:,.0f} ha<extra></extra>"
    ))
    
    fig_surface.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8d8c8"),
        xaxis=dict(title="Année", gridcolor="rgba(255,107,53,0.1)", title_font=dict(color="#ff6b35")),
        yaxis=dict(title="Surface brûlée (ha)", gridcolor="rgba(255,107,53,0.1)", title_font=dict(color="#ff6b35")),
        height=400
    )
    
    # Annotation 2003
    if 2003 in surface_annuelle["annee"].values:
        val_2003 = surface_annuelle[surface_annuelle["annee"] == 2003]["surface_brulee"].values[0]
        fig_surface.add_annotation(
            x=2003,
            y=val_2003,
            text="🔥 2003: Canicule",
            showarrow=True,
            arrowhead=2,
            arrowcolor="#ffcc00",
            font=dict(color="#ffcc00", size=12),
            ay=-40
        )
    
    st.plotly_chart(fig_surface, use_container_width=True)

st.markdown("""
    <div class="insight-box">
        <p>💡 <strong>Observation :</strong> L'année 2003 marque le sommet de la période étudiée avec plus de 
        60 000 hectares parcourus par les flammes lors de la canicule exceptionnelle. Les années 1989 et 1991 
        sont également marquées par des surfaces brûlées importantes.</p>
    </div>
""", unsafe_allow_html=True)

# =====================
# GRAPHIQUE 3: SAISONNALITÉ
# =====================
st.markdown("### 📅 Répartition Saisonnière des Incendies")

col1, col2 = st.columns(2)

if len(df_filtered) > 0:
    with col1:
        mensuel_nb = df_filtered.groupby("mois").size().reset_index(name="nb_incendies")
        mensuel_nb["mois_nom"] = mensuel_nb["mois"].map(noms_mois)
        
        fig_mois_nb = px.bar(
            mensuel_nb,
            x="mois_nom",
            y="nb_incendies",
            labels={"mois_nom": "Mois", "nb_incendies": "Nombre d'incendies"},
            color="nb_incendies",
            color_continuous_scale=[[0, "#ffcc00"], [0.5, "#ff6b35"], [1, "#cc0000"]]
        )
        
        fig_mois_nb.update_layout(
            title=dict(text="Nombre d'incendies par mois", font=dict(color="#ff6b35")),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e8d8c8"),
            xaxis=dict(gridcolor="rgba(255,107,53,0.1)", tickangle=45),
            yaxis=dict(gridcolor="rgba(255,107,53,0.1)"),
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig_mois_nb, use_container_width=True)

    with col2:
        mensuel_surface = df_filtered.groupby("mois")["surface_brulee"].sum().reset_index()
        mensuel_surface["mois_nom"] = mensuel_surface["mois"].map(noms_mois)
        
        fig_mois_surface = px.bar(
            mensuel_surface,
            x="mois_nom",
            y="surface_brulee",
            labels={"mois_nom": "Mois", "surface_brulee": "Surface brûlée (ha)"},
            color="surface_brulee",
            color_continuous_scale=[[0, "#ffcc00"], [0.5, "#ff6b35"], [1, "#cc0000"]]
        )
        
        fig_mois_surface.update_layout(
            title=dict(text="Surfaces brûlées par mois", font=dict(color="#ff6b35")),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e8d8c8"),
            xaxis=dict(gridcolor="rgba(255,107,53,0.1)", tickangle=45),
            yaxis=dict(gridcolor="rgba(255,107,53,0.1)"),
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig_mois_surface, use_container_width=True)

st.markdown("""
    <div class="insight-box">
        <p>💡 <strong>Observation :</strong> La saisonnalité suit un cycle bimodal : 
        <strong>pic estival majeur</strong> (juillet-août) lié à la sécheresse et la fréquentation touristique, 
        et un <strong>pic secondaire en mars</strong> lié aux brûlages agricoles et à la végétation sèche après l'hiver.</p>
    </div>
""", unsafe_allow_html=True)

# =====================
# GRAPHIQUE 4: HEATMAP
# =====================
st.markdown("### 🗓️ Carte de Chaleur : Incendies par Mois et Année")

if len(df_filtered) > 0:
    heatmap_data = df_filtered.groupby(["annee", "mois"]).size().reset_index(name="nb_incendies")
    heatmap_pivot = heatmap_data.pivot(index="mois", columns="annee", values="nb_incendies").fillna(0)
    
    fig_heatmap = px.imshow(
        heatmap_pivot,
        labels=dict(x="Année", y="Mois", color="Incendies"),
        x=heatmap_pivot.columns,
        y=[noms_mois.get(m, m) for m in heatmap_pivot.index],
        color_continuous_scale=[[0, "#1a0a0a"], [0.2, "#ff9900"], [0.5, "#ff6b35"], [0.8, "#cc0000"], [1, "#ffcc00"]],
        aspect="auto"
    )
    
    fig_heatmap.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8d8c8"),
        height=500
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)

# =====================
# TOP 10
# =====================
st.markdown("### 🏆 Top 10 des Années les Plus Touchées")

col1, col2 = st.columns(2)

if len(df_filtered) > 0:
    with col1:
        top_nb = incendies_annuels.nlargest(10, "nb_incendies").sort_values("nb_incendies", ascending=True)
        
        fig_top_nb = px.bar(
            top_nb,
            x="nb_incendies",
            y="annee",
            orientation="h",
            labels={"annee": "Année", "nb_incendies": "Nombre d'incendies"},
            color="nb_incendies",
            color_continuous_scale=[[0, "#ff9900"], [1, "#cc0000"]]
        )
        
        fig_top_nb.update_layout(
            title=dict(text="Top 10 - Nombre d'incendies", font=dict(color="#ff6b35")),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e8d8c8"),
            xaxis=dict(gridcolor="rgba(255,107,53,0.1)"),
            yaxis=dict(gridcolor="rgba(255,107,53,0.1)", type='category'),
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig_top_nb, use_container_width=True)

    with col2:
        top_surface = surface_annuelle.nlargest(10, "surface_brulee").sort_values("surface_brulee", ascending=True)
        
        fig_top_surface = px.bar(
            top_surface,
            x="surface_brulee",
            y="annee",
            orientation="h",
            labels={"annee": "Année", "surface_brulee": "Surface brûlée (ha)"},
            color="surface_brulee",
            color_continuous_scale=[[0, "#ff9900"], [1, "#cc0000"]]
        )
        
        fig_top_surface.update_layout(
            title=dict(text="Top 10 - Surfaces brûlées", font=dict(color="#ff6b35")),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e8d8c8"),
            xaxis=dict(gridcolor="rgba(255,107,53,0.1)"),
            yaxis=dict(gridcolor="rgba(255,107,53,0.1)", type='category'),
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig_top_surface, use_container_width=True)

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
            📈 Visualisation : <strong>Plotly</strong> | 
            🎓 Master 2 GMS |
            👩‍💻 <strong style="color: #ff6b35;">Alia AL MOBARIK</strong>
        </p>
    </div>
""", unsafe_allow_html=True)
