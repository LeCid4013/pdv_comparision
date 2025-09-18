import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO

# --------- CONFIG ----------
DECISIONS = ["Not Evaluated", "Yes", "No", "Not Sure"]
BATCH_SIZE = 20
# ----------------------------

# --------- LOGIN ----------
def login():
    st.title("🔑 Connexion")

    creds = pd.read_csv("cred.csv")  # doit contenir user_id,password
    user = st.text_input("Identifiant")
    pwd = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        user_data = creds[(creds["user_id"] == user) & (creds["password"] == pwd)]
        if not user_data.empty:
            st.session_state["user"] = user
            st.success(f"Bienvenue {user} ✅")
            st.rerun()
        else:
            st.error("❌ Identifiant ou mot de passe incorrect")
# ----------------------------

# --------- IMAGE LOADER ----------
@st.cache_data
def load_and_resize_img(url, max_size=(400, 400)):
    if not url or pd.isna(url) or url.strip() == "":
        return None
    try:
        response = requests.get(url, timeout=10)
        img = Image.open(BytesIO(response.content))
        img.thumbnail(max_size)
        return img
    except Exception:
        return None
# ----------------------------

# --------- MAIN APP ----------
def app(user):
    st.title("📸 Comparaison des PDV")

    # bouton de déconnexion
    if st.button("🚪 Déconnexion"):
        del st.session_state["user"]
        st.rerun()

    # Upload du CSV principal
    uploaded_file = st.file_uploader("📂 Charger le fichier CSV", type="csv")
    if uploaded_file is None:
        st.info("Veuillez charger un fichier CSV pour continuer.")
        return

    df = pd.read_csv(uploaded_file)

    # Pré-traitement
    cols_to_drop = [
        "Index", "Index Sum", "Assigned To", "Duplicate", "name",
        "level_one", "level_two", "address", "haversine", "score"
    ]
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors="ignore")

    if "no_2" in df.columns:
        df = df.rename(columns={"no_2": "unique_ref_2"})

    df["pair_id"] = df["unique_ref_1"].astype(str) + " - " + df["unique_ref_2"].astype(str)

    # Initialiser les décisions si pas déjà fait
    if "results_df" not in st.session_state:
        st.session_state["results_df"] = pd.DataFrame({
            "pair_id": df["pair_id"],
            "decision": ["Not Evaluated"] * len(df)
        })

    results_df = st.session_state["results_df"]

    # --------- PROGRESSION ----------
    total_pairs = len(df)
    done = (results_df["decision"] != "Not Evaluated").sum()
    st.markdown(f"### ✅ Progression : {done} / {total_pairs}")
    st.progress(done / total_pairs if total_pairs > 0 else 0)
    # --------------------------------

    # --------- PAGINATION ----------
    total_pages = (total_pairs - 1) // BATCH_SIZE + 1
    if "page" not in st.session_state:
        st.session_state["page"] = 1

    page_top = st.number_input(
        "Page",
        min_value=1, max_value=total_pages,
        value=st.session_state["page"],
        key="page_top"
    )
    if page_top != st.session_state["page"]:
        st.session_state["page"] = page_top
        st.rerun()

    start_idx = (st.session_state["page"] - 1) * BATCH_SIZE
    end_idx = min(start_idx + BATCH_SIZE, total_pairs)
    # --------------------------------

    # --------- AFFICHAGE DES PAIRES ----------
    for i in range(start_idx, end_idx):
        row = df.iloc[i]

        st.subheader(f"🔹 Paire {i+1}/{total_pairs} — {row['pair_id']}")

        col1, col2 = st.columns(2)

        # ------ Colonne 1 ------
        with col1:
            st.markdown(f"**Outlet 01**")
            st.write(f"**{row['outlet_name_1']}**")
            st.write(f"{row['level_one_1']} - {row['level_two_1']}")
            st.write(f"📞 {row['Telephone_1']}")

            st.write("🏪 Picture Outside")
            img_out = load_and_resize_img(row.get("Picture Outside_1", ""))
            if img_out is not None:
                st.image(img_out, caption="Outside", use_container_width=True)
            else:
                st.text("No img")

            st.write("🏠 Picture Inside")
            img_in = load_and_resize_img(row.get("Picture Inside_1", ""))
            if img_in is not None:
                st.image(img_in, caption="Inside", use_container_width=True)
            else:
                st.text("No img")

        # ------ Colonne 2 ------
        with col2:
            st.markdown(f"**Outlet 02**")
            st.write(f"**{row['outlet_name_2']}**")
            st.write(f"{row['level_one_2']} - {row['level_two_2']}")
            st.write(f"📞 {row['Telephone_2']}")

            st.write("🏪 Picture Outside")
            img_out = load_and_resize_img(row.get("Picture Outside_2", ""))
            if img_out is not None:
                st.image(img_out, caption="Outside", use_container_width=True)
            else:
                st.text("No img")

            st.write("🏠 Picture Inside")
            img_in = load_and_resize_img(row.get("Picture Inside_2", ""))
            if img_in is not None:
                st.image(img_in, caption="Inside", use_container_width=True)
            else:
                st.text("No img")

        # ------ Décision ------
        key = f"decision_{row['pair_id']}_{user}"
        current_decision = results_df.loc[results_df["pair_id"] == row["pair_id"], "decision"].values[0]

        decision = st.radio(
            "Votre décision :", DECISIONS, index=DECISIONS.index(current_decision),
            key=key, horizontal=True
        )
        results_df.loc[results_df["pair_id"] == row["pair_id"], "decision"] = decision

        st.markdown("---")

    # --------- PAGINATION EN BAS ----------
    page_bottom = st.number_input(
        "Page (bas)",
        min_value=1, max_value=total_pages,
        value=st.session_state["page"],
        key="page_bottom"
    )
    if page_bottom != st.session_state["page"]:
        st.session_state["page"] = page_bottom
        st.rerun()
    # --------------------------------------

    # Export
    csv_export = results_df.to_csv(index=False).encode("utf-8")
    st.download_button("💾 Télécharger les décisions", data=csv_export,
                       file_name=f"decisions_{user}.csv", mime="text/csv")
# ----------------------------

# --------- ROUTAGE ----------
if "user" not in st.session_state:
    login()
else:
    app(st.session_state["user"])
