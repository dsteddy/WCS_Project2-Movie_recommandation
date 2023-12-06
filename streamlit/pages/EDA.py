import os
import sys

sys.path.append(os.path.abspath(".."))
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plot import (
    movies_by_decades,
    movies_duration_by_decades_boxplot,
    movies_top_x,
    actors_top_1_by_decades,
    actors_top_10_by_genres,
    actors_top_by_movies,
    actors_top_10_by_votes,
    note_per_cuts,
    actors_top_10_by_notes,
    notes_by_genres,
    movies_top_votes
)
from tools_app import (
    remove_full_screen
)

import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="EDA Projet 2",
    page_icon="📈",
    initial_sidebar_state="collapsed",
    layout="wide",
)

remove_full_screen()

link = "datasets/movies.parquet"
movies = pd.read_parquet(link)
link2 = "datasets/movies_cleaned.parquet"
movies_cleaned = pd.read_parquet(link2)
link3 = "datasets/directors_movies.parquet"
directors = pd.read_parquet(link3)
link = "datasets/actors_movies.parquet"
actors = pd.read_parquet(link)


st.markdown(
    """
        <div style="text-align: center; font-size: 64px;"><strong>Projet 2

    """,
    unsafe_allow_html=True
)
st.markdown(
    """
        <div style="text-align: center; font-size: 64px;"><strong>Digital Dreamers

    """,
    unsafe_allow_html=True
)

st.title("Sujet")
st.markdown(
    """
        <div style="font-size: 24px;">Développer un moteur de recommandations pour un cinéma en difficulté dans la Creuse, utilisant une base de données IMDb et TMDb sans historique de préférences clients. L'approche consiste à analyser les tendances globales des films, en se concentrant sur leur popularité, pour offrir une recommandation diversifiée et contribuer à la revitalisation du cinéma par des moyens numériques.

    """,
    unsafe_allow_html=True
)

st.title("Étude")
st.markdown(
    """
        <div style="font-size: 24px;">
            La base de données initiale contenait beaucoup d'éléments, on a donc fait une présélection
            avant d'étudier les données présentes.<br>
            En phase finale, des algorithmes de machine learning perfectionnent les recommandations.<br>
            L'objectif est d'enrichir l'expérience cinématographique.
    """,
    unsafe_allow_html=True
)

# Axe d'amélioration : login pour enregistrer données des clients
# Récupérer les données des films qui ont été le plus visualisé sur l'application

st.title("Analyse de données exploratoire", anchor=False)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    """
        <div style="font-size: 24px;">
            On a gardé uniquement les films et on a retiré les films pour adultes, en cours de production et ceux n'ayant pas été adapté en français.<br><br>
    """,
    unsafe_allow_html=True
)

# Etude démographique + sondage VOST vs VF
col1, col2 = st.columns([1,2])
with col1:
    st.write("Etude démographique de la Creuse")
    st.image(
        "https://image.noelshack.com/fichiers/2023/48/1/1701096598-etudedemographique.png"
    )
with col2:
    st.markdown(
        """<a href="https://fr.statista.com/statistiques/498200/preference-films-etrangers-vo-vf-france/" rel="nofollow"><img src="https://fr.statista.com/graphique/1/498200/preference-films-etrangers-vo-vf-france.jpg" alt="Statistique: Préférez-vous plutôt voir les films étrangers en version française ou en version originale sous-titrée ? | Statista" style="width: 100%; height: auto !important; max-width:1000px;-ms-interpolation-mode: bicubic;"/></a>""",
        unsafe_allow_html=True,
    )
# Affichage des data sur les films avant filtrage année, notes et votes
st.subheader(
    "Analyse des films présents dans le dataset après premier nettoyage"
)
fig = movies_by_decades(movies)
note_per_decennie = note_per_cuts(movies)

col1, col2 = st.columns(2)
with col1:
    fig[0]
    note_per_decennie
    fig[5]
    fig[4]
with col2:
    fig[1]
    fig[2]
    fig[3]

# Affichage des mêmes data après filtrage
st.subheader(
    """
    Filtrage des films en fonction des paramètres suivants :\n
    - Date de sortie (>1960)
    - Note moyenne (>6.2)
    - Nombre de votes (>4390)
    - Durée des films (>3h30 et <60mn) (Film le plus long de la base de données : Ambiancé 720h)
    """
)

figs = movies_by_decades(movies_cleaned)
note_per_decennie = note_per_cuts(movies_cleaned)
note_per_genre = notes_by_genres(movies_cleaned)
movies_top_10_notes = movies_top_x(movies_cleaned, 10)
movie_duration_decades = movies_duration_by_decades_boxplot(movies_cleaned)
movies_votes = movies_top_votes(movies_cleaned)

col1, col2 = st.columns(2)
with col1:
    figs[0]
    note_per_decennie
    figs[5]
    figs[4]
with col2:
    figs[1]
    figs[2]
    figs[3]

durée, top10_movies = st.columns(2)
with durée:
    note_per_genre
with top10_movies:
    movie_duration_decades
col1, col2 = st.columns(2)
with col1:
    movies_top_10_notes
with col2:
    movies_votes

# Acteurs
st.subheader("Acteurs")
top_actor_decades = actors_top_1_by_decades(actors)
actor_most_movies = actors_top_by_movies(actors, 10)
top_actor_by_genres = actors_top_10_by_genres(actors, 10)
top_actor_by_votes = actors_top_10_by_votes(actors, 10)
top_actor_per_note = actors_top_10_by_notes(actors)
col1, col2 = st.columns(2)
with col1:
    top_actor_decades
    top_actor_by_votes
with col2:
    actor_most_movies
    top_actor_per_note
top_actor_by_genres

# Réalisateurs
st.subheader("Réalisateurs")
top_director_decades = actors_top_1_by_decades(directors, False)
director_most_movies = actors_top_by_movies(directors, 10, False)
top_directors_by_genres = actors_top_10_by_genres(directors, 10, False)
top_directors_by_votes = actors_top_10_by_votes(directors, 10, False)
top_directors_per_note = actors_top_10_by_notes(directors, 10, False)

col1, col2 = st.columns(2)
with col1:
    top_director_decades
    top_directors_by_votes
    top_directors_by_genres
with col2:
    director_most_movies
    top_directors_per_note

cmt = (
    "Alors avec toutes ces informations nous pouvons en déduire que le film le plus populaire serait un téléfilm indien d'une durée " +
    "de 2h réalisé par Christopher Nolan avec comme acteur Brad Pitt et Leonardo Dicaprio"
)
cmt += ""

st.markdown(cmt)
from tools_app import (
    round_corners
)
round_corners()

col1, col2, col3 = st.columns([2, 3, 1])

with col2:
    image = "pages/image.png"
    st.image(image, width=300)
