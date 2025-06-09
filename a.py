# app.py
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")

# Charger les données nettoyées
df = pd.read_csv("subventions_clean.csv")

st.title("📊 Analyse Interactive des Subventions")

# ----------------------------------------
# 🧩 SIDEBAR - Filtres
# ----------------------------------------
st.sidebar.header("🔍 Filtres")

# Filtre Année
annees = sorted(df['annee_budgetaire'].dropna().unique())
annee_selection = st.sidebar.multiselect("Années budgétaires", annees, default=annees)

# Filtre Secteur
secteurs = sorted(df['secteurs_d_activites_definies_par_l_association'].dropna().unique())
secteur_selection = st.sidebar.multiselect("Secteurs d'activité", secteurs, default=secteurs)

# Filtre Direction
directions = sorted(df['direction'].dropna().unique())
direction_selection = st.sidebar.multiselect("Directions", directions, default=directions)

# Filtre Montant minimal
montant_min = st.sidebar.slider("Montant minimal voté (€)", 0, int(df['montant_vote'].max()), 1000, step=500)

# Appliquer les filtres
filtered_df = df[
    (df['annee_budgetaire'].isin(annee_selection)) &
    (df['secteurs_d_activites_definies_par_l_association'].isin(secteur_selection)) &
    (df['direction'].isin(direction_selection)) &
    (df['montant_vote'] >= montant_min)
]

st.markdown(f"**{len(filtered_df)} lignes affichées après filtrage.**")

if filtered_df.empty:
    st.warning("⚠️ Aucun résultat pour les filtres sélectionnés. Veuillez ajuster vos filtres.")
else:
    # ----------------------------------------
    # 📈 1. Top 10 secteurs
    # ----------------------------------------
    st.subheader("🏆 Top 10 secteurs financés")
    top_secteurs = filtered_df.groupby('secteurs_d_activites_definies_par_l_association')['montant_vote'] \
        .sum().sort_values(ascending=False).head(10)

    fig1, ax1 = plt.subplots(figsize=(10, 5))
    top_secteurs.plot(kind='barh', color='steelblue', ax=ax1)
    ax1.set_title("Top 10 des secteurs les plus financés")
    ax1.set_xlabel("Montant total (€)")
    st.pyplot(fig1)

    # ----------------------------------------
    # 📊 2. Évolution annuelle
    # ----------------------------------------
    st.subheader("📅 Évolution annuelle des subventions")
    evolution = filtered_df.groupby('annee_budgetaire')['montant_vote'].sum()

    fig2, ax2 = plt.subplots(figsize=(10, 4))
    evolution.plot(marker='o', color='darkgreen', ax=ax2)
    if 2018 in evolution.index:
        ax2.axvline(x=2018, color='red', linestyle='--', alpha=0.5)
        ax2.text(2018 + 0.1, max(evolution)*0.9, "Fusion 2018", color='red')
    ax2.set_title("Évolution des subventions")
    ax2.set_xlabel("Année")
    ax2.set_ylabel("Montant (€)")
    st.pyplot(fig2)

    # ----------------------------------------
    # 🔥 3. Top bénéficiaires
    # ----------------------------------------
    st.subheader("🎯 Top 10 des bénéficiaires")
    top_benef = filtered_df.groupby('nom_beneficiaire')['montant_vote'].sum().nlargest(10)
    st.dataframe(top_benef.reset_index().rename(columns={'montant_vote': 'Montant Total (€)'}))

    # ----------------------------------------
    # 📊 6. Analyses complémentaires : Durée de financement
    # ----------------------------------------
    st.subheader("📊 6. Analyses complémentaires : Durée de financement")

    duree = filtered_df.groupby('nom_beneficiaire')['annee_budgetaire'].agg(['min', 'max'])
    duree['duree_ans'] = duree['max'] - duree['min'] + 1

    if duree.empty:
        st.info("ℹ️ Pas de données disponibles pour analyser la durée de financement.")
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.histplot(data=duree, x='duree_ans',
                     bins=range(1, int(duree['duree_ans'].max())+2),
                     kde=True, color='purple', ax=ax)
        ax.set_title("Distribution de la durée de financement des associations", pad=15)
        ax.set_xlabel("Nombre d'années de financement continu")
        ax.set_ylabel("Nombre d'associations")
        ax.grid(True, linestyle='--', alpha=0.3)
        st.pyplot(fig)

# ----------------------------------------
# 📥 Télécharger les données filtrées
# ----------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("📥 Télécharger les données filtrées")
st.sidebar.download_button(
    label="📄 Télécharger CSV",
    data=filtered_df.to_csv(index=False),
    file_name="subventions_filtrees.csv",
    mime="text/csv"
)
