import streamlit as st
import folium
import pandas as pd
from folium import plugins
from streamlit_folium import st_folium
from geopy.distance import geodesic

# Pour test rapide : Exemple fictif
client_df = pd.DataFrame({
    "Nom_PDV": ["Alpha Store", "Bravo Market", "Charlie Shop"],
    "Latitude_PDV": [5.3599517, 5.3600017, 5.3600517],
    "Longitude_PDV": [-4.0082563, -4.0083063, -4.0083563],
    "Nom_PDV_TC": ["Alpha Terrain", "Bravo Terrain", "Charlie Terrain"],
    "Latitude_PDV_TC": [5.3600000, 5.3600500, 5.3601000],
    "Longitude_PDV_TC": [-4.0082500, -4.0083000, -4.0083500],
    "Distance_m": [100, 80, 90],
    "Similarite_nom": [95, 92, 90],
    "Match_OK": ["Oui", "Oui", "Non"]
})

# ✅ Mettre la page en mode "largeur maximale"
st.set_page_config(layout="wide")

# Titre
st.title("🗺️ Visualisation Matching PDV Client <> Terrain")

# Choisir un PDV
pdv_selectionne = st.selectbox(
    "Choisissez un Point de Vente (PDV) Client :",
    client_df["Nom_PDV"].unique()
)

# Filtrer les données
row = client_df[client_df["Nom_PDV"] == pdv_selectionne].iloc[0]

# Créer la carte
carte = folium.Map(location=[row["Latitude_PDV"], row["Longitude_PDV"]], zoom_start=16)

# Ajouter le PDV Client
folium.Marker(
    location=[row["Latitude_PDV"], row["Longitude_PDV"]],
    popup=f"Client: {row['Nom_PDV']}",
    icon=folium.Icon(color="blue", icon="user")
).add_to(carte)

# Cercle 500m
folium.Circle(
    radius=100,
    location=[row["Latitude_PDV"], row["Longitude_PDV"]],
    color='blue',
    fill=True,
    fill_opacity=0.05
).add_to(carte)

# Ajouter le PDV Terrain
if pd.notnull(row["Latitude_PDV_TC"]) and pd.notnull(row["Longitude_PDV_TC"]):
    color_line = "green" if row["Match_OK"] == "Oui" else "red"
    
    folium.Marker(
        location=[row["Latitude_PDV_TC"], row["Longitude_PDV_TC"]],
        popup=f"Terrain: {row['Nom_PDV_TC']}",
        icon=folium.Icon(color="green", icon="shopping-cart")
    ).add_to(carte)

    folium.PolyLine(
        locations=[
            [row["Latitude_PDV"], row["Longitude_PDV"]],
            [row["Latitude_PDV_TC"], row["Longitude_PDV_TC"]]
        ],
        color=color_line,
        weight=3,
        opacity=0.8,
        tooltip=f"Distance: {round(row['Distance_m'],1)}m | Similarité: {row['Similarite_nom']}%"
    ).add_to(carte)

# Afficher la carte dans Streamlit
st_data = st_folium(carte, width=200, height=200)