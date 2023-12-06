import pandas as pd
from tools_app import (
    afficher_details_film,
    afficher_top_genres,
    auto_scroll,
    clean_dup,
    get_clicked,
    get_info,
    infos_button,
    knn_algo,
    del_sidebar,
    remove_full_screen,
    round_corners,
)
import streamlit as st
from streamlit_extras.switch_page_button import switch_page

# Configuration de la page
st.set_page_config(
    page_title="DigitalDreamers Recommandation System",
    page_icon="📽️",
    initial_sidebar_state="collapsed",
    layout="wide",
)
# st.markdown(
#     """
#     <style>
#     img {
#         cursor: pointer;
#         transition: all .2s ease-in-out;
#     }
#     img:hover {
#         transform: scale(1.1);
#     }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )


del_sidebar()
remove_full_screen()
round_corners()

# Importation des dataframes nécessaires.
machine_learning = "datasets/machine_learning_final.parquet"
site_web = "datasets/site_web.parquet"
df_ml = pd.read_parquet(machine_learning)
df_ml = clean_dup(df_ml)
df_sw = pd.read_parquet(site_web)
condi = df_sw["titre_str"].duplicated(keep=False)
df_sw = clean_dup(df_sw)

df_c: pd.DataFrame = df_sw[condi]
df_c.index = df_c["tmdb_id"]
dup_mov_dict = df_c["titre_str"].to_dict()

# Création de la liste des films pour la sélection.
default_message = "Entrez ou sélectionnez le nom d'un film..."
movies = df_sw["titre_str"]
movies_list = [default_message] + list(sorted(movies))
selectvalue = default_message

movies_ids = df_sw["tmdb_id"].to_list()

# Instanciation des session_state.
if "index_movie_selected" not in st.session_state:
    st.session_state["index_movie_selected"] = movies_list.index(
        selectvalue
    )
if "clicked" not in st.session_state:
    st.session_state["clicked"] = None
if "clicked2" not in st.session_state:
    st.session_state["clicked2"] = False
if "counter" not in st.session_state:
    st.session_state["counter"] = 1
if "movie_list" not in st.session_state:
    st.session_state["movie_list"] = movies_list
if "clickedhome" not in st.session_state:
    st.session_state["clickedhome"] = False
if "default_message" not in st.session_state:
    st.session_state["default_message"] = default_message
if "dup_mov_dict" not in st.session_state:
    st.session_state["dup_movie_dict"] = dup_mov_dict


# Début de la page.
st.session_state["clickedhome"] = False
st.session_state["clicked"] = None
st.session_state["clicked2"] = False
# home, titre = st.columns([1,23])
# with home:
if st.button("🏠"):
    st.session_state["index_movie_selected"] = movies_list.index(
        default_message
    )
# with titre:
st.header("DigitalDreamers Recommandation System", anchor=False)
# Barre de sélection
selectvalue = st.selectbox(
    label="Choisissez un film ⤵️",
    options=movies_list,
    placeholder=default_message,
    index=st.session_state["index_movie_selected"],
)
if selectvalue != default_message:
    selected_movie = df_sw[df_sw["titre_str"] == selectvalue]
    if (
        selectvalue
        != movies_list[st.session_state["index_movie_selected"]]
    ):
        st.session_state["index_movie_selected"] = movies_list.index(
            selectvalue
        )
        st.session_state["counter"] += 1
        auto_scroll()
        st.rerun()
    afficher_details_film(selected_movie, movies_ids)
    synop, recom = st.columns([3, 4])
    with synop:
        st.subheader("**Synopsis**", anchor=False, divider=True)
        st.markdown(get_info(selected_movie, "overview"))
    with recom:
        st.subheader("**Films Similaires**", anchor=False, divider=True)
        recommended = knn_algo(df_ml, selectvalue, 6)
        cols = st.columns(6)
        for i, col in enumerate(cols):
            with col:
                index, clicked = get_clicked(df_sw, recommended, i)
                if clicked:
                    st.session_state["clicked"] = index
        if st.session_state["clicked"] is not None:
            infos_button(df_sw, movies_list, st.session_state["clicked"])
            st.session_state["counter"] += 1
            auto_scroll()
            st.rerun()
    auto_scroll()
else:
    genres_list = [
        "Drame",
        "Comédie",
        "Animation",
        "Action",
        "Romance",
        "Crime",
    ]
    for genre in genres_list:
        genre_df = afficher_top_genres(df_sw, genre)
        titres = genre_df["titre_str"].head(10).tolist()
        st.header(f"Top 10 {genre}", anchor=False)
        cols = st.columns(10)
        for i, col in enumerate(cols):
            with col:
                index, clicked = get_clicked(
                    genre_df, titres, i, genre, True
                )
                if clicked:
                    st.session_state["clicked"] = index
        if st.session_state["clicked"] is not None:
            infos_button(df_sw, movies_list, st.session_state["clicked"])
            st.session_state["counter"] += 1
            auto_scroll()
            st.rerun()
    auto_scroll()

st.write(
    "App développée par [Morgan](https://github.com/Morgan-DCL) et [Teddy](https://github.com/dsteddy)"
)
