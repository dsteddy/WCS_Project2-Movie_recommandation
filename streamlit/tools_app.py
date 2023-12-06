import asyncio

import aiohttp
import numpy as np
import pandas as pd
import requests
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.neighbors import NearestNeighbors
from st_click_detector import click_detector

import streamlit as st
import streamlit.components.v1 as components
from streamlit_extras.switch_page_button import switch_page


async def fetch_infos(
    ss: object,
    TMdb_id: int,
):
    params = {
        "api_key": "fe4a6f12753fa6c12b0fc0253b5e667f",
        "include_adult": "False",
        "language": "fr-FR",
        "append_to_response": "combined_credits",
    }
    base_url = "https://api.themoviedb.org/3/person/"
    url = f"{base_url}{TMdb_id}"
    async with ss.get(url, params=params) as rsp:
        return await rsp.json()


async def fetch_persons_bio(
    people_list: list, movies_ids: list, director: bool = False
) -> list:
    url_image = "https://image.tmdb.org/t/p/w300_and_h450_bestv2"
    async with aiohttp.ClientSession() as ss:
        taches = []
        for id in people_list:
            tache = asyncio.create_task(fetch_infos(ss, id))
            taches.append(tache)
        datas = await asyncio.gather(*taches)
        full = []
        for data in datas:
            # 99: Documentaire, 16: Animation, 10402: Musique
            exclude = [99, 10402] if director else [99, 10402]
            if director:
                top_credits = sorted(
                    (
                        n
                        for n in data["combined_credits"]["crew"]
                        if n["media_type"] == "movie"
                        and n["id"] in movies_ids
                        and n["job"] == "Director"
                        and all(
                            genre not in n["genre_ids"]
                            for genre in exclude
                        )
                    ),
                    key=lambda x: (
                        -x["popularity"],
                        -x["vote_average"],
                        -x["vote_count"],
                    ),
                )[:8]
                data["director"] = True
            else:
                top_credits = sorted(
                    (
                        n
                        for n in data["combined_credits"]["cast"]
                        if n["media_type"] == "movie"
                        and n["id"] in movies_ids
                        and n["order"] <= 3
                        and all(
                            genre not in n["genre_ids"]
                            for genre in exclude
                        )
                    ),
                    key=lambda x: (
                        -x["popularity"],
                        -x["vote_average"],
                        -x["vote_count"],
                    ),
                )[:8]
                data["director"] = False
                data["character"] = [n["character"] for n in top_credits]

            cmt = "https://images.assetsdelivery.com/compings_v2/2nix/2nix1408/2nix140800145.jpg"
            data["image"] = (
                f"{url_image}{data['profile_path']}"
                if data["profile_path"]
                else cmt
            )

            data["top_5"] = [n["title"] for n in top_credits]
            data["top_5_images"] = [
                f"{url_image}{n['poster_path']}" for n in top_credits
            ]
            data["top_5_movies_ids"] = [n["id"] for n in top_credits]
            to_pop = (
                "adult",
                "also_known_as",
                "homepage",
                "profile_path",
                "combined_credits",
                "known_for_department",
            )
            for tp in to_pop:
                data.pop(tp)
            full.append(data)
    return full


async def fetch_infos_movies(
    ss: object,
    TMdb_id: int,
):
    params = {
        "api_key": "fe4a6f12753fa6c12b0fc0253b5e667f",
        "include_adult": "False",
        "language": "fr-FR",
        "append_to_response": "keywords,credits,videos",
    }
    base_url = "https://api.themoviedb.org/3/movie/"
    url = f"{base_url}{TMdb_id}"
    async with ss.get(url, params=params) as rsp:
        return await rsp.json()


async def fetch_persons_movies(ids: int, people_list: list) -> list:
    async with aiohttp.ClientSession() as ss:
        taches = []
        for id in [ids]:
            tache = asyncio.create_task(fetch_infos_movies(ss, id))
            taches.append(tache)
            await asyncio.sleep(0.02)
        datas = await asyncio.gather(*taches)
        for data in datas:
            test = data["credits"]["cast"]
            data["characters"] = {
                n["id"]: n["character"]
                for n in test
                if n["id"] in people_list
            }
    return data["characters"]


def clean_dup(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie les doublons dans une colonne spécifique d'un DataFrame en ajoutant
    la date entre parenthèses.

    Parameters
    ----------
    df : pd.DataFrame
        Le DataFrame à nettoyer.

    Returns
    -------
    pd.DataFrame
        DataFrame avec les doublons nettoyés.
    """
    condi = df["titre_str"].duplicated(keep=False)
    df.loc[condi, "titre_str"] = (
        df.loc[condi, "titre_str"]
        + " "
        + "("
        + df.loc[condi, "date"].astype(str)
        + ")"
    )
    return df


def auto_scroll():
    """
    Déclenche un défilement automatique de la fenêtre dans un contexte Streamlit.

    Cette fonction ne prend aucun paramètre et ne retourne rien.
    Elle utilise un script HTML pour réinitialiser le défilement de la fenêtre.
    """
    components.html(
        f"""
            <p>{st.session_state["counter"]}</p>
            <script>
                window.parent.document.querySelector('section.main').scrollTo(0, 0);
            </script>
        """,
        height=0,
    )


def get_info(df: pd.DataFrame, info_type: str):
    """
    Extrait une information spécifique du premier élément d'une colonne d'un DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame source.
    info_type : str
        Le nom de la colonne dont on extrait l'information.

    Returns
    -------
    Any
        Information extraite de la première ligne de la colonne spécifiée.
    """
    info = df[info_type].iloc[0]
    return info


def get_titre_from_index(df: pd.DataFrame, idx: int) -> str:
    """
    Récupère le titre correspondant à un index donné dans un DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame contenant les titres.
    idx : int
        Index du titre à récupérer.

    Returns
    -------
    str
        Titre correspondant à l'index fourni.
    """
    return df[df.index == idx]["titre_str"].values[0]


def get_index_from_titre(df: pd.DataFrame, titre: str) -> int:
    """
    Trouve l'index correspondant à un titre donné dans un DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame contenant les titres.
    titre : str
        Le titre dont on cherche l'index.

    Returns
    -------
    int
        Index du titre dans le DataFrame.
    """
    return df[df.titre_str == titre].index[0]


def knn_algo(df: pd.DataFrame, titre: str, top: int = 5) -> list:
    """
    Implémente l'algorithme KNN pour recommander des titres similaires.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame contenant les données pour le modèle KNN.
    titre : str
        Titre à partir duquel les recommandations sont faites.

    Returns
    -------
    List[str]
        Liste de titres recommandés.
    """
    # df["all_for_one"] = df["date"].astype(str)+" "+df["one_for_all"]

    index = df[df["titre_str"] == titre].index[0]
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(
        # df["all_for_one"]
        df["one_for_all"]
    )
    knn_model = NearestNeighbors(
        metric="cosine",
        algorithm="brute",
        n_jobs=-1,
    ).fit(count_matrix)
    _, indices = knn_model.kneighbors(
        count_matrix[index], n_neighbors=top + 1
    )
    result = []
    for idx in indices.flatten()[1:]:
        recommandations = get_titre_from_index(df, idx)
        result.append(recommandations)
    return result


def infos_button(df: pd.DataFrame, movie_list: list, idx: int):
    """
    Met à jour une variable de session Streamlit en fonction de l'index du film sélectionné.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame contenant les informations des films.
    movie_list : list
        Liste des titres de films.
    idx : int
        Index du film sélectionné.

    Cette fonction ne retourne rien mais met à jour la variable de session "index_movie_selected".
    """
    titre = get_titre_from_index(df, idx)
    st.session_state["index_movie_selected"] = movie_list.index(titre)

@st.cache_data
def afficher_top_genres(df: pd.DataFrame, genres: str) -> pd.DataFrame:
    """
    Affiche les films les mieux classés d'un genre spécifique, excluant "Animation" sauf si spécifié.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame contenant les films.
    genres : str
        Genre de films à afficher.

    Returns
    -------
    pd.DataFrame
        DataFrame des films triés par popularité, note moyenne, et nombre de votes.
    """
    sort_by = ["date", "popularity", "rating_avg", "rating_vote"]
    ascending_ = [False for i in range(len(sort_by))]
    condi = (
        (
            df["titre_genres"].str.contains(genres)
            & ~df["titre_genres"].str.contains("Animation")
        )
        if genres != "Animation"
        else df["titre_genres"].str.contains(genres)
    )
    return df[condi].sort_values(by=sort_by, ascending=ascending_)


def get_clicked(
    df: pd.DataFrame,
    titres_list: list,
    nb: int,
    genre: str = "Drame",
    key_: bool = False,
):
    """
    Génère un élément cliquable pour un film et renvoie son index et un détecteur de clic.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame contenant les films.
    titres_list : list
        Liste des titres de films.
    nb : int
        Numéro du film dans la liste.
    genre : str, optional
        Genre du film, par défaut à "Drame".
    key_ : bool, optional
        Si vrai, génère une clé unique pour le détecteur de clic, par défaut à False.

    Returns
    -------
    Tuple[int, Any]
        Index du film et l'objet du détecteur de clic.
    """
    index = int(get_index_from_titre(df, titres_list[nb]))
    movie = df[df["titre_str"] == titres_list[nb]]
    image_link = get_info(movie, "image")
    titre_str = get_info(movie, "titre_str")
    # content = f"""
    #     <div style="text-align: center;">
    #         <a href="#" id="{titres_list[nb]}">
    #             <img width="125px" heigth="180px" src="{image_link}"
    #                 style="object-fit: cover; border-radius: 5%; margin-bottom: 15px;">
    #         </a>
    #         <p style="margin: 0;">{titre_str}</p>
    # """
    content = f"""
        <div style="text-align: center;">
            <a href="#" id="{titres_list[nb]}">
                <img width="125px" height="180px" src="{image_link}"
                    style="object-fit: cover; border-radius: 5%; margin-bottom: 15px; cursor: pointer; transition: filter .2s ease-in-out, transform .2s ease-in-out;"
                    onmouseover="this.style.filter='brightness(70%)'; this.style.transform='scale(1.1)'"
                    onmouseout="this.style.filter='brightness(100%)'; this.style.transform='scale(1)'">
            </a>
            <p style="margin: 0;">{titre_str}</p>
        </div>
    """

    if key_:
        unique_key = f"click_detector_{genre}_{index}"
        return index, click_detector(content, key=unique_key)
    else:
        return index, click_detector(content)


def get_clicked_act_dirct(api_list: list, character: dict, nb: int):
    peo = api_list[nb]
    width = 130
    height = 190
    name = ""
    for k, v in character.items():
        if peo["id"] == k:
            name = v

    # content = f"""
    #     <div style="text-align: center;">
    #         <a href="#" id="{api_list[nb]}">
    #             <img width="{str(width)}px" height="{str(height)}px" src="{peo['image']}"
    #                 style="object-fit: cover; border-radius: 5%; margin-bottom: 15px;">
    #         </a>
    #         <p style="margin: 0;"><strong>{peo['name']}</strong></p>
    #         <p style="margin: 0;"><em style="opacity: 0.7;">{name}</em></p>
    # """
    content = f"""
    <div style="text-align: center;">
        <a href="#" id="{api_list[nb]}">
            <img width="{str(width)}px" height="{str(height)}px" src="{peo['image']}"
                style="object-fit: cover; border-radius: 5%; margin-bottom: 15px; cursor: pointer; transition: filter .2s ease-in-out, transform .2s ease-in-out;"
                onmouseover="this.style.filter='brightness(70%)'; this.style.transform='scale(1.05)'"
                onmouseout="this.style.filter='brightness(100%)'; this.style.transform='scale(1)'">
        </a>
        <p style="margin: 0;"><strong>{peo['name']}</strong></p>
        <p style="margin: 0;"><em style="opacity: 0.7;">{name}</em></p>
    </div>
    """

    unique_key = f"click_detector_{nb}_{peo['name']}"
    return peo, click_detector(content, key=unique_key)


def get_clicked_bio(api_list: list, dup_ids: dict, nb: int):
    peo = api_list
    image = [n for n in api_list["top_5_images"]][nb]
    nom_film = [n for n in api_list["top_5"]][nb]
    nom_ids = [n for n in api_list["top_5_movies_ids"]][nb]

    nom_ = dup_ids.get(nom_ids, nom_film)

    character = (
        [n for n in api_list["character"]][nb]
        if not peo["director"]
        else ""
    )

    width = 130
    height = 190
    # content = f"""
    #     <div style="text-align: center;">
    #         <a href="#" id="{nb}" class="layer">
    #             <img width="{str(width)}px" height="{str(height)}px" src="{image}"
    #                 style="object-fit: cover; border-radius: 5%; margin-bottom: 15px;">
    #         </a>
    #         <p style="margin: 0;"><strong>{nom_}</strong></p>
    #         <p style="margin: 0;"><em style="opacity: 0.7;">{character}</em></p>
    # """
    content = f"""
        <div style="text-align: center;">
            <a href="#" id="{nb}" class="layer">
                <img width="{str(width)}px" height="{str(height)}px" src="{image}"
                    style="object-fit: cover; border-radius: 5%; margin-bottom: 15px; cursor: pointer; transition: filter .2s ease-in-out, transform .2s ease-in-out;"
                    onmouseover="this.style.filter='brightness(70%)'; this.style.transform='scale(1.05)'"
                    onmouseout="this.style.filter='brightness(100%)'; this.style.transform='scale(1)'">
            </a>
            <p style="margin: 0;"><strong>{nom_}</strong></p>
            <p style="margin: 0;"><em style="opacity: 0.7;">{character}</em></p>
        </div>
    """
    unique_key = f"bio_{nb}_{peo['name']}"
    return nom_, click_detector(content, key=unique_key)


# @st.cache_data
def afficher_details_film(df: pd.DataFrame, movies_ids: list):
    infos = {
        "id": get_info(df, "tmdb_id"),
        "date": get_info(df, "date"),
        "image": get_info(df, "image"),
        "titre_str": get_info(df, "titre_str"),
        "titre_genres": get_info(df, "titre_genres"),
        "rating_avg": round(get_info(df, "rating_avg"), 1),
        "rating_vote": get_info(df, "rating_vote"),
        "popularity": get_info(df, "popularity"),
        "runtime": get_info(df, "runtime"),
        "synopsis": get_info(df, "overview"),
        "tagline": get_info(df, "tagline"),
        "youtube": get_info(df, "youtube"),
    }
    film_str: str = infos["titre_str"]
    name_film = film_str[:-7] if film_str.endswith(")") else film_str
    runtime = infos["runtime"]
    actors_list = [a for a in get_actors_dict(df).values()]
    director_list = [d for d in get_directors_dict(df).values()]
    director = asyncio.run(
        fetch_persons_bio(director_list, movies_ids, True)
    )
    actors = asyncio.run(fetch_persons_bio(actors_list, movies_ids))

    col1, col2, cols3 = st.columns([1, 2, 1])
    with col1:
        st.image(infos["image"], use_column_width=True)
    with col2:
        st.header(
            f"{name_film} - ({infos['date']})", anchor=False, divider=True
        )

        st.caption(
            f"<p style='font-size: 16px;'>{infos['titre_genres']} • {f'{runtime // 60}h {runtime % 60}m'}</p>",
            unsafe_allow_html=True,
        )
        texte_fondu = (
            f'<span style="color: #555;">*"{infos["tagline"]}"*</span>'
        )
        st.write(texte_fondu, unsafe_allow_html=True)
        color_rating = (
            "#198c19"
            if infos["rating_avg"] >= 7
            else "#F4D03F"
            if infos["rating_avg"] >= 5
            else "#E74C3C"
        )
        txt_color = "#F2F2F2" if infos["rating_avg"] >= 7 else "#191919"

        gap = 0.1

        elements_html = f"""
            <div style="display: flex; flex-direction: column; align-items: center; gap: {gap}px;">
                <p>Notes</p>
                <div style="background-color: {color_rating}; border-radius: 50%; width: 60px; height: 60px;">
                    <h2 style="text-align: center; color: {txt_color}; font-size: 22px;">{round(infos["rating_avg"], 2)}</h2>
                </div>
            </div>
        """
        st.markdown(
            f"<div style='display: flex; justify-content: start; gap: 20px;'>{elements_html}</div>",
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        full_perso = director + actors
        cols = st.columns(len(full_perso))
        actors_ids = [n["id"] for n in actors]
        character = asyncio.run(
            fetch_persons_movies(infos["id"], actors_ids)
        )

        for i, col in enumerate(cols):
            # st.session_state["person_id"] = full_perso[i]["id"]

            with col:
                if i < 1:
                    st.subheader(
                        "**Réalisation**", anchor=False, divider=True
                    )
                elif i == len(director):
                    st.subheader("**Casting**", anchor=False, divider=True)
                else:
                    st.markdown("<br><br>", unsafe_allow_html=True)
                prso_dict, clicked2 = get_clicked_act_dirct(
                    full_perso, character, i
                )
                if clicked2:
                    st.session_state["clicked2"] = True
                    st.session_state["actor"] = prso_dict
        if st.session_state["clicked2"]:
            switch_page("full_bio")
            st.session_state["counter"] += 1
            auto_scroll()
            st.rerun()

    with cols3:
        st.header("**Bande Annonce** ", anchor=False, divider=True)
        youtube_url = (
            str(infos["youtube"]).replace("watch?v=", "embed/")
            + "?autoplay=0&mute=1"
        )
        yout = f"""
            <div style="margin-top: 20px;">
                <iframe width="100%" height="315" src="{youtube_url}" frameborder="0" allowfullscreen></iframe>
            </div>
        """
        # st.video(infos["youtube"])
        st.markdown(yout, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def get_actors_dict(df: pd.DataFrame) -> dict:
    """
    Extrait un dictionnaire d'acteurs depuis un DataFrame.

    Cette fonction parcourt un DataFrame et construit un dictionnaire où les
    clés sont les noms des acteurs et les valeurs sont leurs identifiants.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame contenant deux colonnes : 'actors' et 'actors_ids'.
        'actors' est une chaîne de caractères avec des noms d'acteurs séparés
        par des virgules, et 'actors_ids' sont les identifiants correspondants.

    Returns
    -------
    dict
        Dictionnaire où les clés sont les noms des acteurs et les valeurs
        sont les identifiants correspondants.
    """
    actors_dict = {}
    for actors, ids in zip(df.actors, df.actors_ids):
        actors_list = actors.split(", ")
        actor_id_pairs = zip(actors_list, ids)
        actors_dict.update(actor_id_pairs)
    return actors_dict


def get_directors_dict(df: pd.DataFrame) -> dict:
    """
    Extrait un dictionnaire de réalisateurs depuis un DataFrame.

    Cette fonction parcourt un DataFrame et construit un dictionnaire où les
    clés sont les noms des réalisateurs et les valeurs sont leurs identifiants.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame contenant deux colonnes : 'director' et 'director_ids'.
        'director' est une chaîne de caractères avec des noms de réalisateurs
        séparés par des virgules, et 'director_ids' sont les identifiants
        correspondants.

    Returns
    -------
    dict
        Dictionnaire où les clés sont les noms des réalisateurs et les valeurs
        sont les identifiants correspondants.
    """
    directors_dict = {}
    for directors, ids in zip(df.director, df.director_ids):
        directors_list = directors.split(", ")
        directors_id_pairs = zip(directors_list, ids)
        directors_dict.update(directors_id_pairs)
    return directors_dict


def get_clicked_home():
    # index = movies_list.index(default_message)
    image_link = "https://cdn-icons-png.flaticon.com/512/4849/4849108.png"
    content = f"""
            <a href="#" id="Home">
                <img width="20px" heigth="20px" src="{image_link}"
                    style="object-fit: cover; border-radius: 5%; margin-bottom: 15px;">
            </a>
    """
    return click_detector(content)


def del_sidebar():
    """
    Supprime le bouton de la sidebar sur la page.
    """
    delete_sidebar = """
                    <style>
                        [data-testid="collapsedControl"] {
                            display: none
                        }
                    </style>
                    """
    st.markdown(delete_sidebar, unsafe_allow_html=True)


def remove_full_screen():
    """
    Supprime le bouton fullscreen des images de la page.
    """
    hide_img_fs = """
    <style>
        button[title="View fullscreen"]{
            visibility: hidden;
        }
    </style>
    """
    st.markdown(hide_img_fs, unsafe_allow_html=True)


def round_corners():
    """
    Arrondi les coins des images de la page.
    """
    round_corners = """
    <style>
        .st-emotion-cache-1v0mbdj > img{
            border-radius:2%;
        }
    </style>
    """
    st.markdown(round_corners, unsafe_allow_html=True)
