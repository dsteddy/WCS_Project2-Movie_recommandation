import os
import sys

sys.path.append(os.path.abspath(".."))

import pandas as pd
import streamlit as st
from streamlit_extras.switch_page_button import switch_page

from datetime import datetime
from tools_app import (
    clean_dup,
    auto_scroll,
    get_clicked_bio,
    get_index_from_titre,
    infos_button,
    remove_full_screen,
    round_corners,
    del_sidebar,
)

df_sw = pd.read_parquet("datasets/site_web.parquet")
df_sw = clean_dup(df_sw)

pdict = st.session_state["actor"]
mov_dup_dict: dict = st.session_state["dup_movie_dict"]

# Configuration de la page
st.set_page_config(
    page_title=f"{pdict['name']}",
    page_icon="👤",
    initial_sidebar_state="collapsed",
    layout="wide",
)


del_sidebar()
remove_full_screen()
round_corners()

st.session_state["clicked"] = None
st.session_state["clicked2"] = None
st.session_state["clicked3"] = None


home, retour, vide = st.columns([1, 2, 20])
with home:
    if st.button("🏠"):
        default_message = st.session_state["default_message"]
        movies_list = st.session_state["movie_list"]
        st.session_state["index_movie_selected"] = movies_list.index(
            default_message
        )
        switch_page("DDMRS")
with retour:
    if st.button("Retour"):
        switch_page("DDMRS")
col1, col2 = st.columns([1, 4])
with col1:
    st.image(pdict["image"], use_column_width=True)
with col2:
    name, title = st.columns([1, 2])
    with name:
        st.header(f"{pdict['name']}", anchor=False, divider=True)
    birth = (
        datetime.strptime(pdict["birthday"], "%Y-%m-%d")
        if pdict["birthday"]
        else "Unknow"
    )
    end_date = (
        datetime.strptime(pdict["deathday"], "%Y-%m-%d")
        if pdict["deathday"]
        else datetime.now()
    )
    age = (end_date - birth).days // 365 if pdict["birthday"] else 0
    add_death = f" - {pdict['deathday']}" if pdict["deathday"] else ""

    st.caption(
        f"<p style='font-size: 16px;'>{birth.strftime('%d-%m-%Y') if pdict['birthday'] else 'Unknow'}{add_death} • {age} ans</p>",
        unsafe_allow_html=True,
    )
    len_ml = len(pdict["top_5_movies_ids"])
    cmt = "Films emblématiques" if len_ml > 1 else "Film emblématique"
    titre = "Réalisation" if pdict["director"] else f"{cmt}"
    st.subheader(f"**{titre}**", anchor=False, divider=True)
    cols = st.columns(len_ml)

    for i, col in enumerate(cols):
        with col:
            nom_film, clicked3 = get_clicked_bio(pdict, mov_dup_dict, i)
            if clicked3:
                st.session_state["clicked3"] = True
                infos_button(
                    df_sw,
                    st.session_state["movie_list"],
                    get_index_from_titre(df_sw, nom_film),
                )
    if st.session_state["clicked3"]:
        switch_page("DDMRS")
if len(pdict["biography"]) > 1:
    st.subheader("**Biographie**", anchor=False, divider=True)
    st.markdown(pdict["biography"])
