import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO

# =========================
# CONFIG
# =========================
BATCH_SIZE = 25
RESULT_FILE = "resultats.csv"
MAX_IMG_SIZE = (600, 600)  # Taille max Pillow
DISPLAY_WIDTH = 400       # Largeur max pour l'affichage

# =========================
# FONCTIONS UTILES
# =========================
def preprocess_csv(df):
    """Nettoie et prépare le fichier CSV selon tes règles"""
    # Colonnes à supprimer
    cols_to_drop = [
        "Index", "Index Sum", "Assigned To", "Duplicate",
        "name", "level_one", "level_two", "address", "haversine", "score"
    ]
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors="ignore")

    # Renommer no_2 en unique_ref_2
    if "no_2" in df.columns:
        df = df.rename(columns={"no_2": "unique_ref_2"})

    # Créer colonne concat
    if "unique_ref_1" in df.columns and "unique_ref_2" in df.columns:
        df["pair_id"] = df["unique_ref_1"].astype(str) + " - " + df["unique_ref_2"].astype(str)

    return df


def load_results():
    """Charge les résultats existants ou crée un DataFrame vide"""
    if st.session_state.get("results_df") is not None:
        return st.session_state.results_df
    try:
        df = pd.read_csv(RESULT_FILE)
    except:
        df = pd.DataFrame(columns=["pair_id", "decision"])
    st.session_state.results_df = df
    return df


def save_results(results_df):
    """Sauvegarde les décisions dans CSV"""
    
    results_df.to_csv(RESULT_FILE, index=False)
    st.session_state.results_df = results_df


@st.cache_data(show_spinner=False)
def load_image_cached(url):
    """Télécharge une image depuis URL et redimensionne"""
    try:
        if isinstance(url, str) and url.strip() != "":
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                img.thumbnail(MAX_IMG_SIZE)
                return img
    except:
        pass
    return None


# =========================
# APPLICATION STREAMLIT
# =========================
st.set_page_config(page_title="Comparaison PDV", layout="wide")
st.title("🖼️ Comparaison des Points de Vente (PDV)")

# Upload CSV
uploaded_file = st.file_uploader("Chargez le fichier CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df = preprocess_csv(df)
    results_df = load_results()

    # Pagination
    total_rows = len(df)
    total_pages = (total_rows // BATCH_SIZE) + (1 if total_rows % BATCH_SIZE != 0 else 0)
    page = st.number_input("Page", min_value=1, max_value=total_pages, step=1)

    start_idx = (page - 1) * BATCH_SIZE
    end_idx = min(start_idx + BATCH_SIZE, total_rows)
    st.write(f"Affichage des lignes {start_idx+1} à {end_idx} sur {total_rows}")

    # Affichage batch
    for i, row in df.iloc[start_idx:end_idx].iterrows():
        pair_id = row["pair_id"]
        st.markdown(f"### Paire: {pair_id}")
        col1, col2 = st.columns(2)

        # -----------------------
        # PDV1
        # -----------------------
        with col1:
            st.subheader(f"PDV1: {row['outlet_name_1']}")

            # Infos complémentaires
            st.text(f"- 📍 Niveau 1 : {row.get('level_one_1', '')}")
            st.text(f"- 🏢 Niveau 2 : {row.get('level_two_1', '')}")
            st.text(f"- 🏢 Addresse : {row.get('address_1', '')}")
            st.text(f"- ☎️ Téléphone : {row.get('Telephone_1', '')}")

            img_in1 = load_image_cached(row.get('Picture Inside_1', None))
            if img_in1:
                st.image(img_in1, caption="Intérieur", width=DISPLAY_WIDTH)
            else:
                st.text("No img")

            img_out1 = load_image_cached(row.get('Picture Outside_1', None))
            if img_out1:
                st.image(img_out1, caption="Extérieur", width=DISPLAY_WIDTH)
            else:
                st.text("No img")

        # -----------------------
        # PDV2
        # -----------------------
        with col2:
            st.subheader(f"PDV2: {row['outlet_name_2']}")

            # Infos complémentaires
            st.text(f"- 📍 Niveau 1 : {row.get('level_one_2', '')}")
            st.text(f"- 🏢 Niveau 2 : {row.get('level_two_2', '')}")
            st.text(f"- 🏢 Addresse : {row.get('address_2', '')}")
            st.text(f"- ☎️ Téléphone : {row.get('Telephone_2', '')}")

            img_in2 = load_image_cached(row.get('Picture Inside_2', None))
            if img_in2:
                st.image(img_in2, caption="Intérieur", width=DISPLAY_WIDTH)
            else:
                st.text("No img")

            img_out2 = load_image_cached(row.get('Picture Outside_2', None))
            if img_out2:
                st.image(img_out2, caption="Extérieur", width=DISPLAY_WIDTH)
            else:
                st.text("No img")

        # -----------------------
        # Choix utilisateur
        # -----------------------
        previous_decision = None
        if pair_id in results_df["pair_id"].values:
            previous_decision = results_df.loc[results_df["pair_id"] == pair_id, "decision"].values[0]

        # key unique = pair_id + index i
        decision_key = f"decision_{pair_id}_{i}"

        decision = st.radio(
            f"Décision pour la paire {pair_id}:",
            ["Non évalué", "Yes", "No", "Not Sure"],
            index=["Non évalué", "Yes", "No", "Not Sure"].index(previous_decision)
            if previous_decision in ["Non évalué", "Yes", "No", "Not Sure"] else 0,
            key=decision_key
        )

        # Sauvegarde immédiate
        if pair_id in results_df["pair_id"].values:
            results_df.loc[results_df["pair_id"] == pair_id, "decision"] = decision
        else:
            results_df = pd.concat(
                [results_df, pd.DataFrame([{"pair_id": pair_id, "decision": decision}])],
                ignore_index=True
            )

        st.markdown("---")
        #st.write("### Résumé des décisions prises jusqu'à présent:")

    # Sauvegarde finale
    save_results(results_df)
    st.success("Toutes vos décisions sont sauvegardées automatiquement dans resultats.csv ✅")

    # Bouton pour télécharger le fichier des décisions
    st.download_button(
        label="📥 Télécharger les décisions",
        data=results_df.to_csv(index=False).encode("utf-8"),
        file_name="decisions.csv",
        mime="text/csv"
    )
