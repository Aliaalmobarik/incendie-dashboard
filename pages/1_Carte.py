import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import os
from pathlib import Path

# =====================
# CONFIGURATION PAGE & CSS
# =====================
st.set_page_config(
    page_title="🗺️ Carte des Incendies",
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
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e8d8c8;
    }
    
    h1, h2, h3 {
        font-family: 'Montserrat', sans-serif !important;
        background: linear-gradient(90deg, #ff6b35, #f7931e, #ffcc00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetric"] {
        background: rgba(255, 107, 53, 0.08);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 107, 53, 0.2);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(255, 107, 53, 0.25);
        border-color: rgba(255, 107, 53, 0.5);
    }
    
    [data-testid="stMetricLabel"] {
        color: #b0a090 !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        background: linear-gradient(90deg, #ff6b35, #ffcc00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .main-title {
        text-align: center;
        padding: 30px;
        background: linear-gradient(135deg, rgba(255,107,53,0.1) 0%, rgba(247,147,30,0.1) 100%);
        border-radius: 20px;
        border: 1px solid rgba(255,107,53,0.2);
        margin-bottom: 30px;
    }
    
    .main-title h1 {
        font-size: 2.8rem !important;
        margin: 0 !important;
    }
    
    .stats-banner {
        background: linear-gradient(90deg, rgba(255,107,53,0.15) 0%, rgba(247,147,30,0.15) 100%);
        border-radius: 15px;
        padding: 15px 25px;
        border: 1px solid rgba(255,107,53,0.2);
        margin-bottom: 20px;
        display: flex;
        justify-content: center;
        gap: 30px;
    }
    
    .stats-banner span {
        color: #e8d8c8;
        font-size: 1rem;
    }
    
    .stats-banner strong {
        color: #ff6b35;
    }
    
    .map-container {
        border-radius: 20px;
        overflow: hidden;
        border: 2px solid rgba(255,107,53,0.3);
        box-shadow: 0 10px 40px rgba(255, 107, 53, 0.15);
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
    """Charge les données d'incendies depuis le fichier Parquet"""
    data_path = DATA_DIR / "incendies" / "incendies.parquet"
    
    if data_path.exists():
        df = pd.read_parquet(data_path)
        # Renommer les colonnes pour simplifier
        df = df.rename(columns={
            'Année': 'annee',
            'Département': 'departement',
            'Code INSEE': 'code_insee',
            'Commune': 'commune',
            'mois': 'mois',
            'surf_ha': 'surface_brulee',
            'Surface parcourue (m2)': 'surface_m2'
        })
        # Nettoyer les données
        df = df.dropna(subset=['annee', 'departement'])
        df['annee'] = df['annee'].astype(int)
        df['mois'] = df['mois'].fillna(1).astype(int)
        df['surface_brulee'] = df['surface_brulee'].fillna(0)
        # Filtrer uniquement PACA (04, 05, 06, 13, 83, 84)
        deps_paca = ['04', '05', '06', '13', '83', '84']
        df = df[df['departement'].astype(str).isin(deps_paca)]
        df['departement'] = df['departement'].astype(str).str.zfill(2)
        return df
    else:
        st.error(f"Fichier non trouvé: {data_path}")
        return pd.DataFrame()

@st.cache_data
def load_shp_departements():
    """Charge le shapefile des départements"""
    shp_path = DATA_DIR / "SHP_meteo.shp"
    
    if shp_path.exists():
        gdf = gpd.read_file(shp_path)
        if gdf.crs != "EPSG:4326":
            gdf = gdf.to_crs(epsg=4326)
        return gdf
    return None

# Charger les données
df = load_incendie_data()
gdf_dept = load_shp_departements()

# Dictionnaire des départements
DEPT_NOMS = {
    "04": "Alpes-de-Haute-Provence",
    "05": "Hautes-Alpes",
    "06": "Alpes-Maritimes",
    "13": "Bouches-du-Rhône",
    "83": "Var",
    "84": "Vaucluse"
}

# Coordonnées des départements PACA
DEPT_COORDS = {
    "04": {"lat": 44.0, "lon": 6.2},
    "05": {"lat": 44.6, "lon": 6.3},
    "06": {"lat": 43.9, "lon": 7.2},
    "13": {"lat": 43.5, "lon": 5.1},
    "83": {"lat": 43.4, "lon": 6.2},
    "84": {"lat": 44.0, "lon": 5.2}
}

# Dictionnaire des mois
noms_mois = {
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
            <p style="color: #b0a090; font-size: 0.8rem;">Carte des Incendies</p>
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
    
    # Filtres
    st.markdown("### 📅 Période d'analyse")
    
    if len(df) > 0:
        annees = sorted(df["annee"].dropna().unique().astype(int))
        
        year_range = st.slider(
            "Plage d'années",
            min_value=int(min(annees)),
            max_value=int(max(annees)),
            value=(2000, 2022),
            step=1
        )
        
        mois_options = ["Tous"] + list(range(1, 13))
        month = st.selectbox(
            "Mois",
            options=mois_options,
            index=0,
            format_func=lambda x: "📆 Tous les mois" if x == "Tous" else noms_mois.get(x, str(x))
        )
        
        st.markdown("---")
        st.markdown("### 🗺️ Zone géographique")
        
        deps_list = sorted(df["departement"].dropna().unique())
        selected_dep = st.selectbox(
            "Département",
            ["Tous"] + list(deps_list),
            format_func=lambda x: "🌍 Toute la région PACA" if x == "Tous" else f"📍 {x} - {DEPT_NOMS.get(x, x)}"
        )
    
    st.markdown("---")
    
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(255,0,0,0.2), rgba(255,107,53,0.2));
            border-radius: 15px;
            padding: 15px;
            border: 1px solid rgba(255,107,53,0.3);
            text-align: center;
        ">
            <p style="color: #ff6b35; margin: 0; font-size: 0.85rem;">
                ⚠️ Période à haut risque :<br><strong>Juillet - Août</strong>
            </p>
        </div>
    """, unsafe_allow_html=True)

# =====================
# FILTRAGE DES DONNÉES
# =====================
if len(df) > 0:
    df_filtered = df[(df["annee"] >= year_range[0]) & (df["annee"] <= year_range[1])]
    
    if month != "Tous":
        df_filtered = df_filtered[df_filtered["mois"] == month]
    
    if selected_dep != "Tous":
        df_filtered = df_filtered[df_filtered["departement"] == selected_dep]
else:
    df_filtered = df

# =====================
# PAGE PRINCIPALE
# =====================
st.markdown("""
    <div class="main-title">
        <h1>🗺️ Cartographie des Incendies en PACA</h1>
        <p style="color: #b0a090;">Analyse spatiale • Zones à risque • Surfaces brûlées</p>
    </div>
""", unsafe_allow_html=True)

# Bannière de contexte
if len(df) > 0:
    mois_label = "Tous les mois" if month == "Tous" else noms_mois.get(month, str(month))
    dep_label = "Région PACA" if selected_dep == "Tous" else f"{selected_dep} - {DEPT_NOMS.get(selected_dep, selected_dep)}"

    st.markdown(f"""
        <div class="stats-banner">
            <span>📍 <strong>{dep_label}</strong></span>
            <span>📅 <strong>{year_range[0]} - {year_range[1]}</strong></span>
            <span>🗓️ <strong>{mois_label}</strong></span>
        </div>
    """, unsafe_allow_html=True)

# =====================
# KPIs
# =====================
st.markdown("### 📊 Indicateurs Clés")

if len(df_filtered) > 0:
    k1, k2, k3, k4 = st.columns(4)
    
    total_incendies = len(df_filtered)
    total_surface = df_filtered["surface_brulee"].sum()
    moy_surface = df_filtered["surface_brulee"].mean()
    
    # Année avec le plus de surface brûlée
    surface_par_annee = df_filtered.groupby("annee")["surface_brulee"].sum()
    annee_max = int(surface_par_annee.idxmax()) if len(surface_par_annee) > 0 else "N/A"
    
    with k1:
        st.metric("🔥 Total Incendies", f"{total_incendies:,}")
    with k2:
        st.metric("🌲 Surface Brûlée", f"{total_surface:,.0f} ha")
    with k3:
        st.metric("📏 Moyenne/Incendie", f"{moy_surface:.2f} ha")
    with k4:
        st.metric("⚠️ Année Record", str(annee_max))

st.markdown("<br>", unsafe_allow_html=True)

# =====================
# CARTE INTERACTIVE
# =====================
st.markdown("### 🗺️ Carte Interactive des Incendies")

# Agrégation par département pour la carte
if len(df_filtered) > 0:
    dept_stats = df_filtered.groupby("departement").agg({
        "surface_brulee": ["sum", "count"]
    }).reset_index()
    dept_stats.columns = ["departement", "surface_totale", "nb_incendies"]
    
    # Ajouter les coordonnées
    dept_stats["lat"] = dept_stats["departement"].apply(lambda x: DEPT_COORDS.get(x, {}).get("lat", 43.5))
    dept_stats["lon"] = dept_stats["departement"].apply(lambda x: DEPT_COORDS.get(x, {}).get("lon", 6.0))
    dept_stats["nom"] = dept_stats["departement"].map(DEPT_NOMS)

# Centre de la carte (PACA)
if selected_dep != "Tous" and selected_dep in DEPT_COORDS:
    center = [DEPT_COORDS[selected_dep]["lat"], DEPT_COORDS[selected_dep]["lon"]]
    zoom = 9
else:
    center = [43.8, 6.0]
    zoom = 7

# Créer la carte avec style sombre
m = folium.Map(
    location=center,
    zoom_start=zoom,
    tiles="CartoDB dark_matter",
    control_scale=True
)

# Couche GeoJSON des départements si disponible
if gdf_dept is not None:
    gdf_map = gdf_dept.copy()
    # Filtrer par département si nécessaire
    if selected_dep != "Tous" and "dep" in gdf_map.columns:
        gdf_map = gdf_map[gdf_map["dep"] == selected_dep]
    
    folium.GeoJson(
        gdf_map,
        name="🗺️ Départements",
        style_function=lambda x: {
            "fillColor": "#ff6b35",
            "fillOpacity": 0.1,
            "color": "#ff6b35",
            "weight": 2,
        },
        highlight_function=lambda x: {
            "fillColor": "#ffcc00",
            "fillOpacity": 0.3,
            "color": "#ffffff",
            "weight": 3,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["nom", "dep"] if "nom" in gdf_map.columns and "dep" in gdf_map.columns else [],
            aliases=["📍 Département:", "🔢 Code:"],
            style="background-color: rgba(0,0,0,0.8); color: white; border-radius: 10px; padding: 10px;"
        )
    ).add_to(m)

# Heatmap basée sur les données agrégées par département
if len(df_filtered) > 0:
    # Créer des points pour la heatmap (plusieurs points par département selon l'intensité)
    heat_points = []
    for _, row in dept_stats.iterrows():
        # Ajouter des points proportionnels au nombre d'incendies
        intensity = min(row["nb_incendies"] / 100, 1.0)  # Normaliser
        heat_points.append([row["lat"], row["lon"], intensity])
    
    if len(heat_points) > 0:
        h1 = folium.FeatureGroup(name="🔥 Densité Incendies", show=True)
        HeatMap(
            heat_points,
            radius=40,
            blur=25,
            gradient={0.2: "#ffcc00", 0.4: "#ff9900", 0.6: "#ff6b35", 0.8: "#ff3300", 1: "#cc0000"}
        ).add_to(h1)
        h1.add_to(m)
    
    # Ajouter des marqueurs pour chaque département
    for _, row in dept_stats.iterrows():
        popup_html = f"""
        <div style="font-family: Arial; min-width: 200px;">
            <h4 style="color: #ff6b35; margin: 0 0 10px 0;">🔥 {row['nom']}</h4>
            <p style="margin: 5px 0;"><strong>Code:</strong> {row['departement']}</p>
            <p style="margin: 5px 0;"><strong>Incendies:</strong> {int(row['nb_incendies']):,}</p>
            <p style="margin: 5px 0;"><strong>Surface brûlée:</strong> {row['surface_totale']:,.0f} ha</p>
        </div>
        """
        
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=max(8, min(30, row["nb_incendies"] / 500)),
            popup=folium.Popup(popup_html, max_width=300),
            color="#ff6b35",
            fill=True,
            fill_color="#ff6b35",
            fill_opacity=0.7,
            weight=2
        ).add_to(m)

# Contrôle des couches
folium.LayerControl(collapsed=False).add_to(m)

# Afficher la carte
st.markdown('<div class="map-container">', unsafe_allow_html=True)
st_folium(m, width="100%", height=600)
st.markdown('</div>', unsafe_allow_html=True)

# =====================
# TABLEAU RÉCAPITULATIF PAR DÉPARTEMENT
# =====================
st.markdown("### 📋 Bilan par Département")

if len(df_filtered) > 0:
    recap = df_filtered.groupby("departement").agg({
        "surface_brulee": "sum"
    }).reset_index()
    recap["nb_incendies"] = df_filtered.groupby("departement").size().values
    recap["nom_departement"] = recap["departement"].map(DEPT_NOMS)
    
    recap = recap[["departement", "nom_departement", "nb_incendies", "surface_brulee"]]
    recap.columns = ["Code", "Département", "Nombre d'Incendies", "Surface Brûlée (ha)"]
    recap = recap.sort_values("Surface Brûlée (ha)", ascending=False)
    recap["Surface Brûlée (ha)"] = recap["Surface Brûlée (ha)"].round(2)
    
    st.dataframe(
        recap,
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
            🗺️ Cartographie : <strong>Folium & Leaflet</strong> | 
            🎓 Master 2 GMS |
            👩‍💻 <strong style="color: #ff6b35;">Alia AL MOBARIK</strong>
        </p>
    </div>
""", unsafe_allow_html=True)
