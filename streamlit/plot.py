import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

notes = "#ff9934"
nombre_films = "royalblue"
votes = "#d9423e"


def movies_by_decades(df: pd.DataFrame):
    """
    Affiche trois graphiques interactifs Plotly : un histogramme de la distribution des notes moyennes,
    un graphique à barres du total de films par décennie et un graphique à barres du total de votes par décennie.

    Paramètres
    ----------
    df : pd.DataFrame
        DataFrame contenant les données à visualiser. Doit contenir les colonnes 'rating_avg', 'cuts' et 'rating_votes'.

    Retourne
    -------
    None
        Cette fonction ne retourne rien mais affiche trois graphiques interactifs.

    """
    # Distribution des notes
    fig1 = go.Figure()
    fig1.add_trace(
        go.Histogram(
            x=df["rating_avg"],
            marker=dict(
                color=f"{notes}", line=dict(color="black", width=1)
            ),
            name="Fréquence",
            showlegend=False,
        )
    )
    median = df["rating_avg"].median()
    max_ = df["rating_avg"].value_counts().max()
    fig1.add_shape(
        go.layout.Shape(
            type="line",
            x0=median,
            x1=median,
            y0=0,
            y1=1,
            yref="paper",
            line=dict(color="red", width=2, dash="dash"),
        )
    )
    fig1.add_annotation(
        x=median,
        y=max_ + 100,
        text=str(median),
        name="Median",
        showarrow=False,
        xshift=15,
        font=dict(color="red"),
    )

    fig1.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="lines",
            line=dict(color="red", width=2, dash="dash"),
            name=f"Médiane",
        )
    )

    fig1.update_layout(
        title="Distribution des Notes",
        xaxis_title="Note",
        yaxis_title="Fréquence",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0.01,
        ),
    )
    # Nombre de films par décennie
    total_films = (
        df.groupby("cuts", observed=True)
        .size()
        .reset_index(name="total_films")
    )
    fig2 = go.Figure()
    fig2.add_trace(
        go.Bar(
            x=total_films["cuts"],
            y=total_films["total_films"],
            showlegend=False,
            marker=dict(
                color=f"{nombre_films}", line=dict(color="black", width=1)
            ),
            name="Quantité de films produits",
        )
    )
    median = total_films["total_films"].median()
    fig2.add_shape(
        go.layout.Shape(
            type="line",
            x0=0,
            x1=1,
            y0=median,
            y1=median,
            xref="paper",
            line=dict(color="red", width=2, dash="dash"),
        )
    )
    fig2.add_annotation(
        x=-0.99,
        y=median,
        text=str(median),
        showarrow=False,
        yshift=10,
        font=dict(color="red"),
    )
    fig2.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="lines",
            line=dict(color="red", width=2, dash="dash"),
            name=f"Médiane",
        )
    )
    fig2.update_layout(
        title="Nombre de films par décennie",
        xaxis_title="Décennie",
        yaxis_title="Nombre de films",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0.01,
        ),
    )
    # Nombre de votes par décennie
    rating_votes = (
        df.groupby("cuts", observed=True)["rating_votes"]
        .mean()
        .reset_index(name="votes")
    )
    fig3 = go.Figure()
    fig3.add_trace(
        go.Bar(
            x=rating_votes["cuts"],
            y=rating_votes["votes"],
            showlegend=False,
            marker=dict(
                color=f"{votes}", line=dict(color="black", width=1)
            ),
            name="Nombre de votes",
        )
    )
    quantiles = rating_votes["votes"].quantile([0.25, 0.5, 0.75]).values
    colors = [("#065535", "1"), ("#ff0000", "2"), ("#b37400", "3")]
    for q, color in zip(quantiles, colors):
        fig3.add_shape(
            go.layout.Shape(
                type="line",
                x0=0,
                x1=1,
                y0=q,
                y1=q,
                xref="paper",
                line=dict(color=color[0], width=2, dash="dash"),
            )
        )
        fig3.add_annotation(
            x=-0.99,
            y=q,
            text=str(round(q)),
            showarrow=False,
            yshift=10,
            font=dict(color=color[0]),
        )
        fig3.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="lines",
                line=dict(color=color[0], width=2, dash="dash"),
                name=f"Quantile {color[1]}",
            )
        )
    fig3.update_layout(
        title="Nombre de votes total par décennie",
        xaxis_title="Décennie",
        yaxis_title="Nombre de Votes",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0.01,
        ),
    )
    # Nombre de film par genre
    total_genres = df.explode("titre_genres")[
        "titre_genres"
    ].value_counts()[::-1]
    fig4 = go.Figure()
    fig4.add_trace(
        go.Bar(
            x=total_genres.values,
            y=total_genres.index,
            orientation="h",
            showlegend=False,
            marker=dict(
                color=f"{nombre_films}", line=dict(color="black", width=1)
            ),
        )
    )
    fig4.update_layout(
        title="Nombre de films par genres",
        xaxis_title="Nombre de films",
        yaxis_title="Genres",
        autosize=True,
        height=1000,
    )
    # Nombre de film et note moyenne par pays
    top10_country = df.explode("production_countries")[
        "production_countries"
    ].value_counts()[:10].reset_index()
    top10_country.reset_index()
    top10_country.rename(
        {
            "production_countries" : "nombre",
            "index" : "production_countries"
        }, inplace=True, axis=1
    )
    fig6 = go.Figure()
    fig6.add_trace(
        go.Bar(
            x=top10_country["production_countries"],
            y=top10_country["nombre"],
            showlegend=False,
            marker=dict(
                color=f"{nombre_films}", line=dict(color="black", width=1)
            ),
        )
    )
    fig6.update_layout(
        title="Nombre de films par pays",
        xaxis_title="Pays",
        yaxis_title="Nombre de films",
        autosize=True,
        height=400
    )
    note_per_country = (
    df.explode("production_countries")
    .groupby("production_countries", observed=True)["rating_avg"]
    .mean()
    .reset_index(name="notes")
    )
    top10_notes = pd.merge(
        left=top10_country,
        right= note_per_country,
        how="left",
        on="production_countries"
    )
    fig5 = go.Figure()
    fig5.add_trace(
        go.Bar(
            x=top10_notes["production_countries"],
            y=round(top10_notes["notes"],1),
            showlegend=False,
            marker=dict(
                color=f"{notes}", line=dict(color="black", width=1)
            ),
        )
    )
    fig5.update_layout(
        title="Note moyenne des films par pays",
        xaxis_title="Pays",
        yaxis_title="Note moyenne",
        autosize=True,
        height=400,
        )

    return [fig1, fig2, fig3, fig4, fig5, fig6]


def movies_duration_by_decades_boxplot(df: pd.DataFrame):
    """
    Génère un graphique en boîte représentant la durée des films par décennies.

    Cette fonction prend en entrée un DataFrame, catégorise les films par
    décennies (stockées dans la colonne 'cuts'), et trace leur durée
    (stockée dans la colonne 'titre_duree'). Le graphique est affiché sans
    points de données et sans légende.

    Parameters
    ----------
    df : pd.DataFrame
        Un DataFrame contenant au moins deux colonnes : 'cuts' pour les
        décennies et 'titre_duree' pour la durée des films.

    Returns
    -------
    None
        Affiche un graphique en boîte de la durée des films par décennies.
        Aucune valeur de retour.
    """
    df["cuts"] = df["cuts"].astype(str)
    df.sort_values("cuts", inplace=True)

    fig = px.box(
        data_frame=df,
        x="cuts",
        y="titre_duree",
        color="cuts",
        points=False,
    )
    fig.update_layout(
        title="Durée des Films par Décénnie",
        xaxis_title="Décénnie",
        yaxis_title="Durée des Films",
        showlegend=False
        # legend=dict(
        #     yanchor="top",
        #     y=0.99,
        #     xanchor="left",
        #     x=0.01
        # )
    )
    return fig


def movies_top_x(df: pd.DataFrame, top: int = 10):
    """ """
    df_filtre = df[df["rating_votes"] > df["rating_votes"].quantile(0.75)]

    grouped_films = (
        df_filtre.groupby("titre_str")["rating_avg"]
        .mean()
        .reset_index()
        .sort_values("rating_avg", ascending=False)
        .head(top)
    )

    fig = go.Figure(
        go.Bar(
            x=grouped_films["rating_avg"],
            y=grouped_films["titre_str"],
            orientation="h",
            marker=dict(color=f"{notes}"),
            marker_line=dict(color="black", width=1),
        )
    )

    fig.update_layout(
        title=f"Films les mieux notés",
        xaxis_title="Note Moyenne",
        yaxis_title="Films",
        yaxis=dict(autorange="reversed"),
        height=400,
    )

    return fig


def actors_top_1_by_decades(df: pd.DataFrame, actors:bool = True):
    if actors:
        job = "Acteurs"
    else:
        job = "Réalisateurs"
    grouped_df = (
        df.groupby(["cuts", "person_name"], observed=True)
        .size()
        .reset_index(name="total_film_acteurs")
        .sort_values(by="total_film_acteurs")
    )

    top_acteurs_decennie = (
        grouped_df.groupby("cuts", observed=True)
        .apply(lambda x: x.nlargest(1, "total_film_acteurs"))
        .reset_index(drop=True)
    )

    decennies = top_acteurs_decennie["cuts"]
    noms_acteurs = top_acteurs_decennie["person_name"]
    nombre_films = top_acteurs_decennie["total_film_acteurs"]

    fig = go.Figure(
        data=[
            go.Bar(
                x=nombre_films,
                y=decennies,
                orientation="h",
                marker=dict(
                    color="#66cdaa", line=dict(color="black", width=1)
                ),
                text=noms_acteurs,
                textposition="auto",
                width=1,
                textfont=dict(size=14, color="black"),
            )
        ]
    )

    fig.update_layout(
        title=f"{job} ayant joués dans le plus de films par décennies",
        xaxis_title="Nombre de Films Joués",
        yaxis_title="Décennie",
    )
    # fig.show()
    return fig


def actors_top_10_by_genres(df: pd.DataFrame, top: int = 10, actors:bool= True):
    if actors:
        job = "Acteurs"
    else:
        job = "Réalisateurs"
    actors_by_genre = (
        df.explode("titre_genres")
        .groupby(["person_name", "titre_genres"])
        .size()
        .reset_index(name="count")
    )

    top_actors_by_genre = actors_by_genre.sort_values(
        "count", ascending=False
    ).drop_duplicates("titre_genres")[:top][::-1]

    fig = go.Figure(
        data=[
            go.Bar(
                x=top_actors_by_genre["count"],
                y=top_actors_by_genre["titre_genres"],
                orientation="h",
                marker=dict(
                    color="#66cdaa", line=dict(color="black", width=1)
                ),
                text=top_actors_by_genre["person_name"],
                textposition="auto",
                width=1,
                textfont=dict(size=14, color="black"),
            )
        ]
    )

    fig.update_layout(
        title=f"{job} les plus fréquemment associés aux top {top} des genres",
        xaxis_title="Nombre de Films",
        yaxis_title="Genres",
    )

    # fig.show()
    return fig


def actors_top_by_movies(df: pd.DataFrame, top: int = 10, actors: bool = True):
    if actors:
        job = "Acteurs"
    else:
        job = "Réalisateurs"
    actors_film_count = (
        df.groupby("person_name").size().reset_index(name="film_count")
    )

    top_actors_film_count = actors_film_count.sort_values(
        "film_count", ascending=False
    ).head(top)[::-1]

    fig = go.Figure(
        data=[
            go.Bar(
                x=top_actors_film_count["film_count"],
                y=top_actors_film_count["person_name"],
                orientation="h",
                marker=dict(
                    color="#66cdaa", line=dict(color="black", width=1)
                ),
                text=top_actors_film_count["film_count"],
                textposition="inside",
                width=1,
                textfont=dict(size=14, color="black"),
            )
        ]
    )

    fig.update_layout(
        title=f"{job} ayant joués dans le plus de films",
        xaxis_title="Nombre de Films",
        yaxis_title=f"{job}",
    )

    # fig.show()
    return fig


def actors_top_10_by_votes(df: pd.DataFrame, top: int = 10, actors:bool = True):
    if actors:
        job = "Acteurs"
    else:
        job = "Réalisateurs"
    actors_by_votes = (
        df.groupby("person_name")["rating_votes"].sum().reset_index()
    )

    top_actors_by_votes = actors_by_votes.sort_values(
        "rating_votes", ascending=False
    ).head(top)[::-1]

    fig = go.Figure(
        data=[
            go.Bar(
                x=top_actors_by_votes["rating_votes"],
                y=top_actors_by_votes["person_name"],
                orientation="h",
                marker=dict(
                    color=f"{votes}", line=dict(color="black", width=1)
                ),
                text=top_actors_by_votes["rating_votes"],
                textposition="auto",
                width=1,
                textfont=dict(size=14, color="black"),
            )
        ]
    )

    fig.update_layout(
        title=f"Total de votes par {job}",
        xaxis_title="Total des votes",
        yaxis_title=f"{job}",
    )
    return fig


def note_per_cuts(df: pd.DataFrame):
    average_note = (
    df.groupby("cuts", observed=True)["rating_avg"]
    .mean()
    .reset_index(name="Notes")
    )
    fig1 = go.Figure()
    fig1.add_trace(
        go.Bar(
            x=average_note["cuts"],
            y=round(average_note["Notes"],1),
            showlegend=False,
            marker=dict(
                color=f"{notes}", line=dict(color="black", width=1)
            ),
            name="Notes moyennes"
        )
    )
    fig1.update_layout(
        title="Notes moyennes par décennie",
        xaxis_title="Décennie",
        yaxis_title="Note moyenne",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0.01,
        ),
    )
    return fig1


def actors_top_10_by_notes(df: pd.DataFrame, top: int = 10, actors: bool = True):
    if actors:
        job = "Acteurs"
    else:
        job = "Réalisateurs"
    actors_by_votes = (
    df.groupby("person_name")["rating_votes"].sum().reset_index()
    )
    top_actors_by_votes = actors_by_votes.sort_values(
        "rating_votes", ascending=False
    ).head(top)[::-1]
    actors_by_notes = (
        df.groupby("person_name")["rating_avg"]
        .mean()
        .reset_index()
    )
    actors_by_votes_notes = pd.merge(
        left = top_actors_by_votes,
        right = actors_by_notes,
        how = "left",
        on = "person_name"
        )
    fig = go.Figure(
        data=[
            go.Bar(
                y=actors_by_votes_notes["person_name"],
                x=round(actors_by_votes_notes["rating_avg"],1),
                orientation="h",
                marker=dict(
                    color=f"{notes}", line=dict(color="black", width=1)
                ),
                text=round(actors_by_votes_notes["rating_avg"],1),
                # textposition="auto",
                width=1,
                textfont=dict(size=14, color="black"),
            )
        ]
    )
    fig.update_layout(
        title=f"Note moyenne des {job}",
        xaxis_title="Note moyenne",
        yaxis_title=f"{job}",
    )
    return fig


def notes_by_genres(df: pd.DataFrame):
    total_genres = (
        df.explode("titre_genres")
        .groupby("titre_genres")["rating_avg"]
        .mean()
        .reset_index()
    )
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=total_genres["titre_genres"],
            y=round(total_genres["rating_avg"],1),
            showlegend=False,
            marker=dict(
                color=f"{notes}", line=dict(color="black", width=1)
            ),
        )
    )
    fig.update_layout(
        title=f"Note moyenne par genre",
        xaxis_title="Genres",
        yaxis_title=f"Note moyenne",
    )
    return fig


def movies_top_votes(df: pd.DataFrame):
    df_filtre = df[df["rating_votes"] > df["rating_votes"].quantile(0.75)]

    grouped_films = (
        df_filtre.groupby("titre_str")["rating_votes"]
        .mean()
        .reset_index()
        .sort_values("rating_votes", ascending=False)
        .head(10)
    )

    fig = go.Figure(
        go.Bar(
            x=grouped_films["rating_votes"],
            y=grouped_films["titre_str"],
            orientation="h",
            marker=dict(color=f"{votes}"),
            marker_line=dict(color="black", width=1),
        )
    )

    fig.update_layout(
        title=f"Films avec le plus de votes",
        xaxis_title="Nombre de votes",
        yaxis_title="Films",
        yaxis=dict(autorange="reversed"),
        height=400,
    )

    return fig