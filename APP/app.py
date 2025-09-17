import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from math import radians, cos, sin, asin, sqrt

from function import get_best_match, get_best_match_, get_best_match_t5

#st.write("Hello World!")
#st.write({"key" : "value"})
header = st.header("🛒 Outil de Matching - Points de Vente")
#st.title("Matching de points de vente par comparaison de photos")

menu = st.sidebar
menu.title("Selection des fichiers CSV")

# Selection du fichier Extract for Mapping
menu.markdown("---")
menu.markdown("#### Extract For Mapping.")
uploaded_file1 = menu.file_uploader("Choisissez un fichier CSV", type=["csv"], key="efm_uploader")
if uploaded_file1 is not None:
    df_efm = pd.read_csv(uploaded_file1)
    efm_loaded = True
else:
    efm_loaded = False
    df_efm = pd.DataFrame()

menu.markdown("---")
menu.markdown("#### Coverage Checking.")
uploaded_file2 = menu.file_uploader("Choisissez un fichier CSV", type=["csv"], key="cc_uploader")
if uploaded_file2 is not None:
    df_cc = pd.read_csv(uploaded_file2)
    cc_loaded = True
else:
    cc_loaded = False
    df_cc = pd.DataFrame()

#Création des onglets
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["Apperçu des fichiers CSV", "Map - Coverafe Checking", "Recherche matching Point RA", "Recherche matching Point TC", "Matching RA par Batch", "Part 06", "Part 07", "Part 08"])
with tab1:
    if not efm_loaded:
        st.write("Aucun fichier Extract For Mapping chargé.")
        st.warning("Veuillez télécharger un fichier CSV pour continuer.")
        st.markdown("---")
    else:
        st.markdown("### Apperçu - Extract For Mapping")
        st.write("Le fichier CSV a été chargé avec succès.")
        # Affichage des 5 premières lignes du DataFrame
        st.dataframe(df_efm.head())
        # Affichage des informations sur le DataFrame
        st.write("Informations sur le DataFrame :")
        st.write(df_efm.info())
        # Affichage de la taille du DataFrame
        st.write(f"Taille du DataFrame : {df_efm.shape[0]} lignes et {df_efm.shape[1]} colonnes")
        # Affichage des colonnes du DataFrame
        st.write("Colonnes du DataFrame :")
        st.write(df_efm.columns.tolist())
        st.markdown("---")

    if not cc_loaded:
        st.write("Aucun fichier Coverage Checking chargé.")
        st.warning("Veuillez télécharger un fichier CSV pour continuer.")
    else:
        st.markdown("### Apperçu - Coverage Checking")
        st.write("Le fichier CSV a été chargé avec succès.")
        # Affichage des 5 premières lignes du DataFrame
        st.dataframe(df_cc.head())
        # Affichage des informations sur le DataFrame
        st.write("Informations sur le DataFrame :")
        st.write(df_cc.info())
        # Affichage de la taille du DataFrame
        st.write(f"Taille du DataFrame : {df_cc.shape[0]} lignes et {df_cc.shape[1]} colonnes")
        # Affichage des colonnes du DataFrame
        st.write("Colonnes du DataFrame :")
        st.write(df_cc.columns.tolist())
        

# with tab2:
#     def haversine(lon1, lat1, lon2, lat2):
#         lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
#         dlon = lon2 - lon1 
#         dlat = lat2 - lat1 
#         a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
#         c = 2 * asin(sqrt(a)) 
#         km = 6371 * c
#         return km * 1000  # Conversion en mètres


#     if cc_loaded:
#         df_ra = df_cc[df_cc['Source'] == 'TC'].copy()
#         df_tc = df_cc[df_cc['Source'] == 'RA'].copy()

#         # Initialisation des états
#         if 'selected_tc_name' not in st.session_state:
#             st.session_state.selected_tc_name = df_tc['Outlet Name'].iloc[0]
#         if 'radius_m' not in st.session_state:
#             st.session_state.radius_m = 500
#         if 'show_map' not in st.session_state:
#             st.session_state.show_map = False

#         st.title("Carte des Points de Vente RA & TC")

#         # Filtres au-dessus de la carte
#         col1, col2, col3 = st.columns([2, 1, 1])
#         with col1:
#             tc_names = df_tc['Outlet Name'].unique().tolist()
#             selected_tc = st.selectbox("Choisir un point RA", tc_names, index=tc_names.index(st.session_state.selected_tc_name))
#         with col2:
#             selected_radius = st.slider("Rayon (en mètres)", 100, 5000, value=st.session_state.radius_m, step=50)
#         with col3:
#             update = st.button("Mettre à jour la carte")

#         # Si bouton cliqué, on met à jour les valeurs stockées
#         if update:
#             st.session_state.selected_tc_name = selected_tc
#             st.session_state.radius_m = selected_radius
#             st.session_state.show_map = True

#         # Affichage de la carte uniquement si demandé
#         if st.session_state.show_map:
#             selected_tc_row = df_tc[df_tc['Outlet Name'] == st.session_state.selected_tc_name].iloc[0]
#             tc_lat, tc_lon = selected_tc_row['Latitude'], selected_tc_row['Longitude']

#             # Filtrage des RA proches
#             df_ra['distance_m'] = df_ra.apply(lambda row: haversine(tc_lon, tc_lat, row['Longitude'], row['Latitude']), axis=1)
#             df_ra_nearby = df_ra[df_ra['distance_m'] <= st.session_state.radius_m]

#             # Création de la carte
#             m = folium.Map(location=[tc_lat, tc_lon], zoom_start=15)
#             tc_cluster = MarkerCluster(name="Points TC").add_to(m)
#             ra_cluster = MarkerCluster(name="Points RA").add_to(m)

#             # Ajout du point TC sélectionné
#             folium.Marker(
#                 location=[tc_lat, tc_lon],
#                 popup=folium.Popup(f"<b>{selected_tc_row['Outlet Name']}</b><br><img src='{selected_tc_row['Picture Outside']}' width='200'>", max_width=250),
#                 icon=folium.Icon(color='blue', icon='info-sign')
#             ).add_to(tc_cluster)

#             # Ajout des points RA dans le rayon spécifié
#             for _, row in df_ra_nearby.iterrows():
#                 folium.Marker(
#                     location=[row['Latitude'], row['Longitude']],
#                     popup=folium.Popup(f"<b>{row['Outlet Name']}</b><br><img src='{row['Picture Outside']}' width='200'>", max_width=250),
#                     icon=folium.Icon(color='green', icon='ok-sign')
#                 ).add_to(ra_cluster)

#             st_folium(m, use_container_width=True, height=300, key="map RA for TC")

#     else:
#         st.info("Veuillez téléverser un fichier CSV contenant les colonnes requises : Source, idOutlet, Outlet Name, Latitude, Longitude, Picture Outisde")

#########################################################################################
#########################################################################################

with tab3:
    # Fonction de calcul de distance entre deux points GPS (Haversine)
    def haversine(lon1, lat1, lon2, lat2):
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        km = 6371 * c
        return km * 1000  # Conversion en mètres

    if cc_loaded:
        df_ra_ = df_cc[df_cc['Source'] == 'TC'].copy()
        df_tc_ = df_cc[df_cc['Source'] == 'RA'].copy()

        # Retirer les points sans coordonnées valides
        df_tc_ = df_tc_.dropna(subset=["Latitude", "Longitude"])
        df_ra_ = df_ra_.dropna(subset=["Latitude", "Longitude"])

        df_ra_["Outlet Name + Id"] = df_ra_["Outlet Name"].str.strip() + " - Id Outlet : " + df_ra_["idOutlet"].astype(str)

        # Initialisation des états
        if 'selected_tc_name_t3' not in st.session_state:
            st.session_state.selected_tc_name_t3 = df_tc_['idOutlet'].iloc[0]
        if 'temp_selected_tc_name_t3' not in st.session_state:
            st.session_state.temp_selected_tc_name_t3 = st.session_state.selected_tc_name_t3
        if 'radius_m' not in st.session_state:
            st.session_state.radius_m = 500
        if 'update_map' not in st.session_state:
            st.session_state.update_map = False

        st.title("Recherche de Matching - Points RA")

        # Filtres au-dessus de la carte
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            tc_names = df_tc_['idOutlet'].unique().tolist()
            if st.session_state.temp_selected_tc_name_t3 not in tc_names:
                st.session_state.temp_selected_tc_name_t3 = tc_names[0]
            st.session_state.temp_selected_tc_name_t3 = st.selectbox(
                "Choisir un point RA (Avec l'ID Outlet)",
                tc_names,
                index=tc_names.index(st.session_state.temp_selected_tc_name_t3),
                key="temp_selectbox_t3"
            )

        with col2:
            temp_radius = st.slider("Rayon (en mètres)", min_value=100, max_value=5000, value=st.session_state.radius_m, step=50, key="temp_radius_slider")

        with col3:
            if st.button("Lancer la recherche", key="update_map_button_t3"):
                st.session_state.selected_tc_name_t3 = st.session_state.temp_selected_tc_name_t3
                st.session_state.radius_m = temp_radius
                st.session_state.update_map = True

        if st.session_state.update_map:
            selected_tc = df_tc_[df_tc_['idOutlet'] == st.session_state.selected_tc_name_t3].iloc[0]
            tc_lat, tc_lon = selected_tc['Latitude'], selected_tc['Longitude']

            # Filtrage des RA proches
            df_ra_['distance_m'] = df_ra_.apply(lambda row: haversine(tc_lon, tc_lat, row['Longitude'], row['Latitude']), axis=1)
            df_ra_nearby = df_ra_[df_ra_['distance_m'] <= st.session_state.radius_m]

            #Une ligne de code pour trier les points RA par distance
            df_ra_nearby = df_ra_nearby.sort_values(by='distance_m')

            # Création de la carte
            m = folium.Map(location=[tc_lat, tc_lon], zoom_start=15)
            tc_cluster = MarkerCluster(name="Points TC").add_to(m)
            ra_cluster = MarkerCluster(name="Points RA").add_to(m)

            # Ajout du point TC sélectionné
            image_url_tc_outside = selected_tc['Picture Outside'] if pd.notna(selected_tc['Picture Outside']) else ""
            image_url_tc_inside = selected_tc['Picture Inside'] if pd.notna(selected_tc['Picture Inside']) else ""
            folium.Marker(
                location=[tc_lat, tc_lon],
                popup=folium.Popup(f"<b>{selected_tc['Outlet Name']}</b><br><img src='{image_url_tc_outside}' width='200'>", max_width=250),
                #popup_inside=folium.Popup(f"<b>{selected_tc['Outlet Name']}</b><br><img src='{image_url_tc_outside}' width='200'>", max_width=250),
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(tc_cluster)

            # Ajout des points RA dans le rayon spécifié
            for _, row in df_ra_nearby.iterrows():
                image_url_ra = row['Picture Outside'] if pd.notna(row['Picture Outside']) else ""
                folium.Marker(
                    location=[row['Latitude'], row['Longitude']],
                    popup=folium.Popup(f"<b>{row['Outlet Name']}</b><br><img src='{image_url_ra}' width='200'>", max_width=250),
                    icon=folium.Icon(color='green', icon='ok-sign')
                ).add_to(ra_cluster)

            # Affichage carte dans Streamlit
            st_folium(m, use_container_width=True, height=300, key="map RA for TC_")

            # Suggestion automatique du meilleur match
            #best_match = get_best_match(selected_tc['Outlet Name'], df_ra_nearby, st.session_state.radius_m)
            best_match_ = get_best_match_(selected_tc, df_ra_nearby, st.session_state.radius_m) 
            best_match = best_match_[0] if best_match_[0] is not None else None 

            if best_match:
                st.markdown(f"###### Point RA sélectionné : {selected_tc['Outlet Name']}")
                col1_, col2_ = st.columns([1, 1])
                
                with col1_:
                    if pd.notna(selected_tc['Picture Outside']):
                        st.image(selected_tc['Picture Outside'], width=200, caption="Photo extérieure du point RA")
                    else:
                        st.warning("Aucune photo extérieure disponible pour ce point RA.")

                with col2_:
                    if pd.notna(selected_tc['Picture Inside']):
                        st.image(selected_tc['Picture Inside'], width=200, caption="Photo intérieure du point RA")
                    else:
                        st.warning("Aucune photo intérieure disponible pour ce point RA.")

                st.success(f"Meilleur match TC suggéré : {best_match}") 
                st.markdown(f"Confiance : {best_match_[1]:.2f}%")
                picture_inside = df_ra_[df_ra_['Outlet Name + Id'] == best_match]['Picture Inside'].values[0] if pd.notna(df_ra_[df_ra_['Outlet Name + Id'] == best_match]['Picture Inside'].values[0]) else None
                picture_outside = df_ra_[df_ra_['Outlet Name + Id'] == best_match]['Picture Outside'].values[0] if pd.notna(df_ra_[df_ra_['Outlet Name + Id'] == best_match]['Picture Outside'].values[0]) else None


                # Affichage des photos du meilleur match RA suggéré
                st.markdown("###### Photos du meilleur match TC suggéré :")
                col_outs, col_ins = st.columns([1, 1])

                with col_outs:
                    if picture_outside:
                        st.image(picture_outside, width=200, caption="Photo extérieure du point TC suggéré")
                    else:
                        st.warning("Aucune photo extérieure disponible pour le point TC suggéré.")

                with col_ins:
                    if picture_inside:
                        st.image(picture_inside, width=200, caption="Photo intérieure du point TC suggéré")
                    else:
                        st.warning("Aucune photo intérieure disponible pour le point TC suggéré.")
                
            else :
                st.warning("Aucun match TC à suggerer dans le rayon spécifié.")

            # Section de sélection manuelle dans un expander
            with st.expander("Sélectionner le meilleur match TC pour ce point RA"):


                st.markdown(f"#### Point RA sélectionné : {selected_tc['Outlet Name']}")

                # Filtres au-dessus de la carte
                col1_, col2_ = st.columns([1, 1])

                with col1_:
                    if pd.notna(selected_tc['Picture Outside']):
                        st.image(selected_tc['Picture Outside'], width=200, caption="Photo extérieure du point RA")
                    else:
                        st.warning("Aucune photo extérieure disponible pour ce point RA.")

                with col2_:
                    if pd.notna(selected_tc['Picture Inside']):
                        st.image(selected_tc['Picture Inside'], width=200, caption="Photo intérieure du point RA")
                    else:
                        st.warning("Aucune photo intérieure disponible pour ce point RA.")

                #if pd.notna(selected_tc['Picture Inside']):
                #    st.image(selected_tc['Picture Inside'], width=300, caption="Photo du point TC")

                st.markdown("#### Candidats TC proches :")
                for _, ra_row in df_ra_nearby.iterrows():

                    st.markdown(f"###### {ra_row['Outlet Name']} - Id : {ra_row['idOutlet']}  - Distance : {ra_row['distance_m']:.2f} m")
                    col1, col2 = st.columns([1, 1])

                    with col1:
                        if pd.notna(ra_row['Picture Outside']):
                            st.image(ra_row['Picture Outside'], width=200, caption="Image extérieure")
                        else:
                            st.warning("Aucune photo extérieure disponible pour ce point TC.")

                    with col2:
                        if pd.notna(ra_row['Picture Inside']):
                            st.image(ra_row['Picture Inside'], width=200, caption="Image intérieure", )
                        else:
                            st.warning("Aucune photo intérieure disponible pour ce point TC.")


                    #if pd.notna(ra_row['Picture Inside']):
                    #    st.image(ra_row['Picture Inside'], width=200, caption=ra_row['Outlet Name'])

                match_choice = st.selectbox(
                    "Quel point TC correspond le mieux ?",
                    options=[''] + df_ra_nearby["Outlet Name + Id"].tolist()
                )
                if best_match:
                    st.markdown(f" Meilleur match TC suggéré : {best_match} <br>Confiance : {best_match_[1]:.2f}%", unsafe_allow_html=True)
                st.success(f"Vous avez sélectionné : {match_choice}")


            # Reset de l'état pour éviter boucle
            #st.session_state.update_map = False

    else:
        st.info("Veuillez téléverser un fichier CSV contenant les colonnes requises : Source, idOutlet, Outlet Name, Latitude, Longitude, Picture Outisde")


############################################################################################
############################################################################################

with tab4:
    # Fonction de calcul de distance entre deux points GPS (Haversine)
    def haversine(lon1, lat1, lon2, lat2):
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        km = 6371 * c
        return km * 1000  # Conversion en mètres

    if cc_loaded:
        df_ra_t4 = df_cc[df_cc['Source'] == 'RA'].copy()
        df_tc_t4 = df_cc[df_cc['Source'] == 'TC'].copy()

	# Retirer les points sans coordonnées valides
        df_tc_t4 = df_tc_t4.dropna(subset=["Latitude", "Longitude"])
        df_ra_t4 = df_ra_t4.dropna(subset=["Latitude", "Longitude"])

        df_ra_t4["Outlet Name + Id"] = df_ra_t4["Outlet Name"].str.strip() + " - Id Outlet : " + df_ra_t4["idOutlet"].astype(str)

        # Initialisation des états
        if 'selected_tc_name_t4' not in st.session_state:
            st.session_state.selected_tc_name_t4 = df_tc_t4['idOutlet'].iloc[0]
        if 'temp_selected_tc_name_t4' not in st.session_state:
            st.session_state.temp_selected_tc_name_t4 = st.session_state.selected_tc_name_t4
        if 'radius_m' not in st.session_state:
            st.session_state.radius_m = 500
        if 'update_map' not in st.session_state:
            st.session_state.update_map = False

        st.title("Recherche de Matching - Points TC")

        # Filtres au-dessus de la carte
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            tc_names = df_tc_t4['idOutlet'].unique().tolist()
            if st.session_state.temp_selected_tc_name_t4 not in tc_names:
                st.session_state.temp_selected_tc_name_t4 = tc_names[0]
            st.session_state.temp_selected_tc_name_t4 = st.selectbox(
                "Choisir un point TC (Avec l'ID Outlet)",
                tc_names,
                index=tc_names.index(st.session_state.temp_selected_tc_name_t4),
                key="temp_selectbox_t4"
            )

        with col2:
            temp_radius = st.slider("Rayon (en mètres)", min_value=50, max_value=5000, value=st.session_state.radius_m, step=50, key="temp_radius_slider_t4")

        with col3:
            if st.button("Mettre à jour la carte", key="update_map_button_t4"):
                st.session_state.selected_tc_name_t4 = st.session_state.temp_selected_tc_name_t4
                st.session_state.radius_m = temp_radius
                st.session_state.update_map = True

        if st.session_state.update_map:
            #selected_tc = df_tc_t4[df_tc_t4['Outlet Name'] == st.session_state.selected_tc_name_t4].iloc[0]
            filtered_tc = df_tc_t4[df_tc_t4['idOutlet'] == st.session_state.selected_tc_name_t4]
            if filtered_tc.empty:
                st.error("Le point TC sélectionné n'existe plus. Veuillez en choisir un autre.")
                st.stop()
            selected_tc = filtered_tc.iloc[0]
            tc_lat, tc_lon = selected_tc['Latitude'], selected_tc['Longitude']

            # Filtrage des RA proches
            df_ra_t4['distance_m'] = df_ra_t4.apply(lambda row: haversine(tc_lon, tc_lat, row['Longitude'], row['Latitude']), axis=1)
            df_ra_nearby = df_ra_t4[df_ra_t4['distance_m'] <= st.session_state.radius_m]

            #Une ligne de code pour trier les points RA par distance
            df_ra_nearby = df_ra_nearby.sort_values(by='distance_m')

            # Création de la carte
            m = folium.Map(location=[tc_lat, tc_lon], zoom_start=15)
            tc_cluster = MarkerCluster(name="Points TC").add_to(m)
            ra_cluster = MarkerCluster(name="Points RA").add_to(m)

            # Ajout du point TC sélectionné
            image_url_tc_outside = selected_tc['Picture Outside'] if pd.notna(selected_tc['Picture Outside']) else ""
            image_url_tc_inside = selected_tc['Picture Inside'] if pd.notna(selected_tc['Picture Inside']) else ""
            folium.Marker(
                location=[tc_lat, tc_lon],
                popup=folium.Popup(f"<b>{selected_tc['Outlet Name']}</b><br><img src='{image_url_tc_outside}' width='200'>", max_width=250),
                #popup_inside=folium.Popup(f"<b>{selected_tc['Outlet Name']}</b><br><img src='{image_url_tc_outside}' width='200'>", max_width=250),
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(tc_cluster)

            # Ajout des points RA dans le rayon spécifié
            for _, row in df_ra_nearby.iterrows():
                image_url_ra = row['Picture Outside'] if pd.notna(row['Picture Outside']) else ""
                folium.Marker(
                    location=[row['Latitude'], row['Longitude']],
                    popup=folium.Popup(f"<b>{row['Outlet Name']}</b><br><img src='{image_url_ra}' width='200'>", max_width=250),
                    icon=folium.Icon(color='green', icon='ok-sign')
                ).add_to(ra_cluster)

            # Affichage carte dans Streamlit
            st_folium(m, use_container_width=True, height=300)

            # Suggestion automatique du meilleur match
            #best_match = get_best_match(selected_tc['Outlet Name'], df_ra_nearby, st.session_state.radius_m)
            best_match_ = get_best_match_(selected_tc, df_ra_nearby, st.session_state.radius_m) 
            best_match = best_match_[0] if best_match_[0] is not None else None 

            if best_match:
                st.markdown(f"###### Point TC sélectionné : {selected_tc['Outlet Name']}")
                col1_, col2_ = st.columns([1, 1])
                
                with col1_:
                    if pd.notna(selected_tc['Picture Outside']):
                        st.image(selected_tc['Picture Outside'], width=200, caption="Photo extérieure du point TC")
                    else:
                        st.warning("Aucune photo extérieure disponible pour ce point TC.")

                with col2_:
                    if pd.notna(selected_tc['Picture Inside']):
                        st.image(selected_tc['Picture Inside'], width=200, caption="Photo intérieure du point TC")
                    else:
                        st.warning("Aucune photo intérieure disponible pour ce point TC.")

                st.success(f"Meilleur match RA suggéré : {best_match} \n Confiance : {best_match_[1]:.2f}%") 
                picture_inside = df_ra_t4[df_ra_t4['Outlet Name + Id'] == best_match]['Picture Inside'].values[0] if pd.notna(df_ra_t4[df_ra_t4['Outlet Name + Id'] == best_match]['Picture Inside'].values[0]) else None
                picture_outside = df_ra_t4[df_ra_t4['Outlet Name + Id'] == best_match]['Picture Outside'].values[0] if pd.notna(df_ra_t4[df_ra_t4['Outlet Name + Id'] == best_match]['Picture Outside'].values[0]) else None


                # Affichage des photos du meilleur match RA suggéré
                st.markdown("###### Photos du meilleur match RA suggéré :")
                col_outs, col_ins = st.columns([1, 1])

                with col_outs:
                    if picture_outside:
                        st.image(picture_outside, width=200, caption="Photo extérieure du point RA suggéré")
                    else:
                        st.warning("Aucune photo extérieure disponible pour le point RA suggéré.")

                with col_ins:
                    if picture_inside:
                        st.image(picture_inside, width=200, caption="Photo intérieure du point RA suggéré")
                    else:
                        st.warning("Aucune photo intérieure disponible pour le point RA suggéré.")   
                
            else :
                st.warning("Aucun match RA à suggerer dans le rayon spécifié.")

            # Section de sélection manuelle dans un expander
            with st.expander("Sélectionner le meilleur match RA pour ce point TC"):


                st.markdown(f"#### Point TC sélectionné : {selected_tc['Outlet Name']}")

                # Filtres au-dessus de la carte
                col1_, col2_ = st.columns([1, 1])

                with col1_:
                    if pd.notna(selected_tc['Picture Outside']):
                        st.image(selected_tc['Picture Outside'], width=200, caption="Photo extérieure du point TC")
                    else:
                        st.warning("Aucune photo extérieure disponible pour ce point TC.")

                with col2_:
                    if pd.notna(selected_tc['Picture Inside']):
                        st.image(selected_tc['Picture Inside'], width=200, caption="Photo intérieure du point TC")
                    else:
                        st.warning("Aucune photo intérieure disponible pour ce point TC.")

                #if pd.notna(selected_tc['Picture Inside']):
                #    st.image(selected_tc['Picture Inside'], width=300, caption="Photo du point TC")

                st.markdown("#### Candidats RA proches :")
                for _, ra_row in df_ra_nearby.iterrows():

                    st.markdown(f"###### {ra_row['Outlet Name']} - Id : {ra_row['idOutlet']}")
                    col1, col2 = st.columns([1, 1])

                    with col1:
                        if pd.notna(ra_row['Picture Outside']):
                            st.image(ra_row['Picture Outside'], width=200, caption="Image extérieure")
                        else:
                            st.warning("Aucune photo extérieure disponible pour ce point RA.")

                    with col2:
                        if pd.notna(ra_row['Picture Inside']):
                            st.image(ra_row['Picture Inside'], width=200, caption="Image intérieure", )
                        else:
                            st.warning("Aucune photo intérieure disponible pour ce point RA.")


                    #if pd.notna(ra_row['Picture Inside']):
                    #    st.image(ra_row['Picture Inside'], width=200, caption=ra_row['Outlet Name'])

                match_choice = st.selectbox(
                    "Quel point RA correspond le mieux ?",
                    options=[''] + df_ra_nearby["Outlet Name + Id"].tolist()
                )
                if best_match:
                    st.markdown(f" Meilleur match RA suggéré : {best_match} <br>Confiance : {best_match_[1]:.2f}%", unsafe_allow_html=True)
                else:
                    st.warning("Aucun match RA à suggérer.")
                st.success(f"Vous avez sélectionné : {match_choice}")


            # Reset de l'état pour éviter boucle
            #st.session_state.update_map = False

    else:
        st.info("Veuillez téléverser un fichier CSV contenant les colonnes requises : Source, idOutlet, Outlet Name, Latitude, Longitude, Picture Outisde")


###############################################################################################
###############################################################################################
with tab5:
    # Fonction de calcul de distance entre deux points GPS (Haversine)
    def haversine(lon1, lat1, lon2, lat2):
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * asin(sqrt(a))
        km = 6371 * c
        return km * 1000  # en mètres


    radius_m = st.slider("Rayon de recherche (en mètres)", 100, 5000, 500, step=100)
    batch_size = 50

    if cc_loaded:
        df_ra_t5 = df_cc[df_cc['Source'] == 'TC'].copy()
        df_tc_t5 = df_cc[df_cc['Source'] == 'RA'].copy()

	# Retirer les points sans coordonnées valides
        df_tc_t5 = df_tc_t5.dropna(subset=["Latitude", "Longitude"])
        df_ra_t5 = df_ra_t5.dropna(subset=["Latitude", "Longitude"])

        df_ra_t5["Outlet Name + Id"] = df_ra_t5["Outlet Name"].str.strip() + " - Id Outlet : " + df_ra_t5["idOutlet"].astype(str)

        st.title("Matching des points RA avec les TC")

        if 'selections' not in st.session_state:
            st.session_state.selections = {}
        if 'current_batch' not in st.session_state:
            st.session_state.current_batch = 0

        total_batches = (len(df_tc_t5) - 1) // batch_size + 1

        st.subheader(f"Batch {st.session_state.current_batch + 1} sur {total_batches}")

        col1, col3, col4, col2 = st.columns([1, 1, 1, 1])
        with col3:
            if st.button("⬅️ Précédent") and st.session_state.current_batch > 0:
                st.session_state.current_batch -= 1
        with col4:
            if st.button("Suivant ➡️") and st.session_state.current_batch < total_batches - 1:
                st.session_state.current_batch += 1

        start_idx = st.session_state.current_batch * batch_size
        end_idx = start_idx + batch_size
        df_tc_batch = df_tc_t5.iloc[start_idx:end_idx]

        for idx, (_, tc_row) in enumerate(df_tc_batch.iterrows()):
            tc_lat, tc_lon = tc_row['Latitude'], tc_row['Longitude']
            if pd.isna(tc_lat) or pd.isna(tc_lon):
                continue

            df_ra_t5['distance_m'] = df_ra_t5.apply(lambda row: haversine(tc_lon, tc_lat, row['Longitude'], row['Latitude']), axis=1)
            df_ra_nearby = df_ra_t5[df_ra_t5['distance_m'] <= radius_m].copy()

            #Une ligne de code pour trier les points RA par distance
            df_ra_nearby = df_ra_nearby.sort_values(by='distance_m')

            best_match_row, best_score = get_best_match_t5(tc_row, df_ra_nearby, radius_m)

            is_selected = tc_row['idOutlet'] in st.session_state.selections and st.session_state.selections[tc_row['idOutlet']] != ""
            expander_label = f"RA : {tc_row['Outlet Name']} ({tc_row['idOutlet']})"
            if is_selected:
                expander_label = f"✅ {expander_label}"

            #with st.expander(expander_label, expanded=is_selected):
            with st.expander(expander_label):
                with st.form(key=f"form_{tc_row['idOutlet']}"):
                    st.markdown(f"**Photo du point RA : {tc_row['Outlet Name']} | Visité(e) par : Enum**")
                    col1, col2 = st.columns([1, 1])

                    with col1:
                        #st.markdown(f"**Point TC : {tc_row['Outlet Name']} (id: {tc_row['idOutlet']})**")
                        if pd.notna(tc_row['Picture Outside']):
                            st.image(tc_row['Picture Outside'], width=200, caption="Photo extérieure du point RA")
                        else:
                            st.warning("Aucune photo extérieure disponible pour ce point RA.")
                    
                    with col2:
                        #st.markdown("**Photo extérieure du point TC**") 
                        if pd.notna(tc_row['Picture Inside']):
                            st.image(tc_row['Picture Inside'], width=200, caption="Photo intérieure du point RA")  
                        else:
                            st.warning("Aucune photo intérieure disponible pour ce point RA.")
                            #st.markdown("---")

                    
                    #if best_match_row is not None and tc_row['idOutlet'] not in st.session_state.selections:
                    if best_match_row is not None :
                        #st.session_state.selections[tc_row['idOutlet']] = best_match_row['Outlet Name']
                        st.session_state.selections[tc_row['idOutlet']] = best_match_row['Outlet Name + Id']
                        st.info(f"**Meilleur match TC suggéré : {best_match_row['Outlet Name']} (Confiance = {round(best_score, 1)}%)**")

                        # Affichage de la photo du meilleur match
                        col1, col2 = st.columns([1, 1])
                        st.markdown("---")
                        with col1:
                            if pd.notna(best_match_row['Picture Outside']):
                                st.image(best_match_row['Picture Outside'], width=200, caption="Photo extérieure du meilleur match TC")
                            else:
                                st.warning("Aucune photo extérieure disponible pour le meilleur match TC.")

                        with col2:
                            if pd.notna(best_match_row['Picture Inside']):
                                st.image(best_match_row['Picture Inside'], width=200, caption="Photo intérieure du meilleur match TC")
                            else:
                                st.warning("Aucune photo intérieure disponible pour le meilleur match TC.")
                    else:
                        st.warning("Aucun match TC suggéré dans le rayon spécifié.")
                        st.markdown("---")

                    #st.markdown("---")
                    
                    match_names = []
                    for _, ra_row in df_ra_nearby.iterrows():
                        name = ra_row['Outlet Name + Id']
                        match_names.append(name)

                    # Affichage du boutton de sélection du meilleur match
                    previous_selection = st.session_state.selections.get(tc_row['idOutlet'], "")
                    if previous_selection in match_names:
                        default_index = match_names.index(previous_selection) + 1
                    elif best_match_row is not None and best_match_row['Outlet Name + Id'] in match_names:
                        default_index = match_names.index(best_match_row['Outlet Name + Id']) + 1
                    else:
                        default_index = 0

                    selection = st.selectbox(
                        f"Sélectionner le meilleur match TC pour pour le point de vente : {tc_row['Outlet Name']}",
                        options=[""] + match_names,
                        index=default_index,
                        key=f"selectbox_{tc_row['idOutlet']}"
                    )

                    submit = st.form_submit_button("✅ Valider ce match")
                    if submit:
                        st.session_state.selections[tc_row['idOutlet']] = selection
                        st.success(f"Match enregistré pour {tc_row['Outlet Name']}")
                    
                    st.markdown("---")

                    # Affichage des points RA proches
                    st.markdown("**Points RA Candidats :**")
                    for _, ra_row in df_ra_nearby.iterrows():
                        name = ra_row['Outlet Name']
                        #match_names.append(name)

                        st.markdown(f"###### {name} (Id : {ra_row['idOutlet']}) - Distance : {ra_row['distance_m']:.1f} m")
                        col1, col2 = st.columns([1, 1]) 

                        with col1:
                            if pd.notna(ra_row['Picture Outside']):
                                st.image(ra_row['Picture Outside'], width=200, caption="Photo extérieure")
                            else:
                                st.warning("Aucune photo extérieure disponible pour ce point RA.")

                        with col2:
                            if pd.notna(ra_row['Picture Inside']):
                                st.image(ra_row['Picture Inside'], width=200, caption="Photo intérieure")
                            else:
                                st.warning("Aucune photo intérieure disponible pour ce point RA.")


        if st.button("Générer le fichier de sortie"):
            output = []
            for _, tc_row in df_tc_t5.iterrows():
                selected_name = st.session_state.selections.get(tc_row['idOutlet'], "")
                if selected_name:
                    match_row = df_ra_t5[df_ra_t5['Outlet Name + Id'] == selected_name]
                    selected_id = match_row['idOutlet'].values[0] if not match_row.empty else ""
                    output.append({
                        'idOutlet_TC': tc_row['idOutlet'],
                        'Outlet Name_TC': tc_row['Outlet Name'],
                        'Selected idOutlet_RA': selected_id,
                        'Selected Name_RA': selected_name,
                    })

            if output:
                output_df = pd.DataFrame(output)
                csv = output_df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Télécharger le fichier de correspondances", csv, "matches_tc_ra.csv", "text/csv")
            else:
                st.info("Aucune correspondance sélectionnée.")
    else:
        st.info("Veuillez téléverser un fichier CSV contenant les colonnes requises : Source, idOutlet, Outlet Name, Latitude, Longitude, Picture Outside")