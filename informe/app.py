import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import NOMBRES_MESES_VENTANA, cargar_datos

st.set_page_config(page_title="Golazo - Informe GrowUP", page_icon="⚽", layout="wide")

st.markdown(
    """
    <style>
    .main > div { padding-top: 2rem; }
    h1, h2, h3 { font-weight: 600; color: #1B2A4A; }
    [data-testid="stMetricValue"] { color: #2E6E9E; }
    hr { margin: 1.5rem 0; }
    .tarjeta-kpi {
        background-color: #F2F4F7;
        border-radius: 0.5rem;
        padding: 0.75rem 1rem;
        height: 100%;
    }
    .tarjeta-kpi .etiqueta {
        font-size: 0.8rem;
        color: #5A6472;
        margin-bottom: 0.25rem;
    }
    .tarjeta-kpi .valor {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2E6E9E;
        line-height: 1.3;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

COLOR_PRIMARIO = "#2E6E9E"
COLOR_ACENTO = "#F2A65A"
COLOR_ALERTA = "#B23A2E"
COLOR_NEUTRO = "#C9CDD4"

DIAS_ES_MINUSCULA = {
    "Monday": "lunes",
    "Tuesday": "martes",
    "Wednesday": "miércoles",
    "Thursday": "jueves",
    "Friday": "viernes",
    "Saturday": "sábado",
    "Sunday": "domingo",
}


def dias_es_lista(dias_ingles):
    """Traduce una lista de dias de la semana (ingles) a espanol, en minuscula y con tildes."""
    return [DIAS_ES_MINUSCULA.get(d, d) for d in dias_ingles]


def scroll_arriba():
    """Desplaza la vista al inicio de la pagina (usado al cambiar de seccion)."""
    st.iframe(
        """
        <script>
            var contenedores = window.parent.document.querySelectorAll(
                'section[data-testid="stMain"], .main, div[data-testid="stAppViewContainer"]'
            );
            contenedores.forEach(function (el) { el.scrollTo({top: 0, behavior: "instant"}); });
        </script>
        """,
        height=1,
    )


def seccion_portada(datos):
    canal = datos["canal"].iloc[0]
    video = datos["video"]
    evolucion = datos["evolucion"]

    st.title("⚽ Golazo - Informe estratégico")
    st.caption("Preparado por GrowUP")
    st.divider()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Suscriptores", f"{canal['suscriptores']:,}".replace(",", "."))
    col2.metric("Vídeos publicados", f"{canal['total_videos']}")
    col3.metric("Vistas (30 días)", f"{evolucion['views'].sum():,}".replace(",", "."))
    col4.metric("Suscriptores ganados (30 días)", f"+{evolucion['subscribers_gained'].sum()}")

    dias_fuertes_es = ", ".join(dias_es_lista(datos["dias_fuertes"]))
    with col5:
        st.markdown(
            f"""
            <div class="tarjeta-kpi">
                <div class="etiqueta">Días de mayor audiencia</div>
                <div class="valor">{dias_fuertes_es}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    st.subheader("Evolución de audiencia (últimos 30 días)")
    fig = px.line(
        evolucion.sort_values("fecha"), x="fecha", y="views",
        labels={"fecha": "", "views": "Vistas"},
        color_discrete_sequence=[COLOR_PRIMARIO],
    )
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", margin=dict(l=0, r=0, t=10, b=0), height=320)
    fig.update_traces(line=dict(width=2.5))
    st.plotly_chart(fig, width="stretch")

    st.divider()
    st.markdown(
        """
        ### Contenido de este informe

        Usa el menú de la izquierda para navegar por cada bloque del análisis:

        1. **Opinión post-partido** - ¿existe relación con los días de partido?
        2. **Seguimiento del club** - ranking de categorías, día fuerte vs. resto
        3. **Curiosidades vs. Afición** - la oportunidad de crecimiento del canal
        4. **Vídeos virales** - listado para revisión cualitativa
        5. **Fichajes en ventana de mercado** - comparativa con el resto de categorías
        6. **Categorías débiles** - ranking para decisiones de producción
        7. **Top por retención** - la palanca económica real
        """
    )


def seccion_opinion(datos):
    video = datos["video"]

    st.title("🗣️ Opinión post-partido: ¿existe relación con los días de partido?")
    dias_fuertes_es = ", ".join(dias_es_lista(datos["dias_fuertes"]))
    st.caption(f"Días de partido considerados: {dias_fuertes_es}, martes y miércoles")

    opinion_shorts = video[(video["categoria"] == "Opinión post-partido") & (video["formato"] == "Short")]
    comparativa = opinion_shorts.groupby("dia_relevante_partido")[
        ["views_totales", "ratio_likes_vista", "ratio_comentarios_vista", "retencion_media"]
    ].mean()
    comparativa.index = comparativa.index.map({True: "Día de partido", False: "Resto de días"})
    comparativa.index.name = "grupo"

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Vistas medias")
        fig = px.bar(
            comparativa.reset_index(), x="grupo", y="views_totales", color="grupo",
            color_discrete_map={"Día de partido": COLOR_PRIMARIO, "Resto de días": COLOR_NEUTRO},
            labels={"grupo": "", "views_totales": "Vistas medias"},
        )
        fig.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=10))
        st.plotly_chart(fig, width="stretch")
    with col2:
        st.subheader("Comentarios por vista (%)")
        fig2 = px.bar(
            comparativa.reset_index(), x="grupo", y="ratio_comentarios_vista", color="grupo",
            color_discrete_map={"Día de partido": COLOR_PRIMARIO, "Resto de días": COLOR_NEUTRO},
            labels={"grupo": "", "ratio_comentarios_vista": "Comentarios / vista"},
        )
        fig2.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=10))
        fig2.update_yaxes(tickformat=".2%")
        st.plotly_chart(fig2, width="stretch")

    st.subheader("Retención media")
    fig3 = px.bar(
        comparativa.reset_index(), x="grupo", y="retencion_media", color="grupo",
        color_discrete_map={"Día de partido": COLOR_PRIMARIO, "Resto de días": COLOR_NEUTRO},
        labels={"grupo": "", "retencion_media": "Retención media"},
    )
    fig3.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=10), height=300)
    fig3.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig3, width="stretch")

    st.divider()
    mejora_views = (comparativa.loc["Día de partido", "views_totales"] / comparativa.loc["Resto de días", "views_totales"] - 1) * 100
    mejora_comentarios = (comparativa.loc["Día de partido", "ratio_comentarios_vista"] / comparativa.loc["Resto de días", "ratio_comentarios_vista"] - 1) * 100
    mejora_retencion = (comparativa.loc["Día de partido", "retencion_media"] - comparativa.loc["Resto de días", "retencion_media"]) * 100

    st.success(
        f"**Conclusión:** los Shorts de Opinión post-partido publicados en día de partido obtienen "
        f"**{mejora_views:+.0f} % más vistas**, **{mejora_comentarios:+.0f} % más comentarios por vista** "
        f"y **{mejora_retencion:+.1f} puntos más de retención** que el resto de días."
    )
    with st.expander("Ver tabla de datos"):
        st.dataframe(comparativa.round(4), width="stretch")


def seccion_seguimiento(datos):
    video = datos["video"]

    st.title("📅 Seguimiento del club: ranking de categorías (largo)")
    dias_fuertes_es = ", ".join(dias_es_lista(datos["dias_fuertes"]))
    st.caption(f"Día fuerte de audiencia: {dias_fuertes_es}")

    largos = video[video["formato"] == "Largo"]
    ranking_dia_fuerte = largos[largos["es_dia_fuerte"]].groupby("categoria")["views_totales"].mean().sort_values(ascending=False)
    ranking_resto = largos[~largos["es_dia_fuerte"]].groupby("categoria")["views_totales"].mean().sort_values(ascending=False)

    top_fuerte = ranking_dia_fuerte.idxmax()
    top_resto = ranking_resto.idxmax()

    col1, col2 = st.columns(2)
    col1.metric("Categoría líder en día fuerte", top_fuerte)
    col2.metric("Categoría líder en resto de la semana", top_resto)

    st.divider()
    df_plot = pd.DataFrame({"Día fuerte": ranking_dia_fuerte, "Resto de la semana": ranking_resto}).sort_values(
        "Día fuerte", ascending=True
    )
    fig = go.Figure()
    fig.add_trace(go.Bar(y=df_plot.index, x=df_plot["Día fuerte"], name="Día fuerte", orientation="h", marker_color=COLOR_ACENTO))
    fig.add_trace(go.Bar(y=df_plot.index, x=df_plot["Resto de la semana"], name="Resto de la semana", orientation="h", marker_color=COLOR_PRIMARIO))
    fig.update_layout(
        barmode="group", plot_bgcolor="white", paper_bgcolor="white",
        xaxis_title="Vistas medias", legend=dict(orientation="h", y=-0.15), margin=dict(t=10), height=420,
    )
    st.plotly_chart(fig, width="stretch")

    st.divider()
    if top_fuerte == "Seguimiento del club" and top_resto == "Seguimiento del club":
        st.success(
            "**Confirmado:** Seguimiento del club es la categoría líder tanto en día fuerte como en el "
            "resto de la semana. Es el formato de referencia para sostener audiencia de forma constante."
        )
    else:
        st.warning(
            f"**A tener en cuenta:** Seguimiento del club no lidera en ambas ventanas "
            f"(lidera {top_fuerte} en día fuerte y {top_resto} en el resto)."
        )

    with st.expander("Ver tablas de datos"):
        c1, c2 = st.columns(2)
        c1.write("**Día fuerte**")
        c1.dataframe(ranking_dia_fuerte.round(0), width="stretch")
        c2.write("**Resto de la semana**")
        c2.dataframe(ranking_resto.round(0), width="stretch")


def seccion_curiosidades(datos):
    video = datos["video"]

    st.title("🌟 Curiosidades de fútbol vs. afición")
    st.caption("La oportunidad de crecimiento del canal: contenido que no depende de ser aficionado del equipo")

    curiosidades = video[video["categoria"] == "Curiosidades de fútbol"]
    aficion = video[video["categoria"] == "Afición"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Vídeos de curiosidades", len(curiosidades))
    col2.metric("Vídeos de afición", len(aficion), delta=f"{len(curiosidades) - len(aficion)} de diferencia")
    ranking_categorias = video.groupby("categoria")["views_totales"].mean().sort_values(ascending=False)
    posicion_curiosidades = list(ranking_categorias.index).index("Curiosidades de fútbol") + 1
    col3.metric("Posición de curiosidades por vistas", f"{posicion_curiosidades}.º de {len(ranking_categorias)}")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Ranking de categorías por vistas medias")
        colores = [
            COLOR_ACENTO if c == "Curiosidades de fútbol" else (COLOR_ALERTA if c == "Afición" else COLOR_NEUTRO)
            for c in ranking_categorias.index
        ]
        fig = px.bar(
            ranking_categorias.reset_index(), x="views_totales", y="categoria", orientation="h",
            labels={"views_totales": "Vistas medias", "categoria": ""},
        )
        fig.update_traces(marker_color=colores)
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=10), height=350)
        fig.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig, width="stretch")

    with col2:
        st.subheader("Curiosidades vs. afición vs. media del canal")
        metricas = ["views_totales", "likes", "comentarios", "retencion_media"]
        etiquetas = ["Vistas", "Likes", "Comentarios", "Retención"]
        comp_cur = curiosidades[metricas].mean() / video[metricas].mean() * 100
        comp_af = aficion[metricas].mean() / video[metricas].mean() * 100
        df_comp = pd.DataFrame({
            "Métrica": etiquetas * 2,
            "% sobre la media del canal": list(comp_cur.values) + list(comp_af.values),
            "Categoría": ["Curiosidades"] * 4 + ["Afición"] * 4,
        })
        fig2 = px.bar(
            df_comp, x="Métrica", y="% sobre la media del canal", color="Categoría", barmode="group",
            color_discrete_map={"Curiosidades": COLOR_ACENTO, "Afición": COLOR_ALERTA},
        )
        fig2.add_hline(y=100, line_dash="dot", line_color="#888")
        fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=10), height=350)
        st.plotly_chart(fig2, width="stretch")

    st.divider()
    st.subheader("Antigüedad media por categoría")
    antiguedad_media = video.groupby("categoria")["antiguedad_dias"].mean().sort_values()
    fig3 = px.bar(
        antiguedad_media.reset_index(), x="antiguedad_dias", y="categoria", orientation="h",
        labels={"antiguedad_dias": "Antigüedad media (días)", "categoria": ""},
        color_discrete_sequence=[COLOR_PRIMARIO],
    )
    fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=10), height=300)
    fig3.update_yaxes(categoryorder="total descending")
    st.plotly_chart(fig3, width="stretch")

    st.divider()
    st.success(
        f"**Conclusión:** Curiosidades de fútbol ocupa la posición **{posicion_curiosidades}.ª** en vistas "
        f"medias del canal, con solo **{abs(len(curiosidades) - len(aficion))} vídeos** de diferencia "
        f"respecto a Afición, que es la categoría con menos vistas medias. Es una categoría a explotar: "
        f"atrae audiencia que no tiene por qué ser aficionada del equipo, y es contenido fácilmente "
        f"adaptable a formato Short."
    )


def seccion_virales(datos):
    video = datos["video"]

    st.title("🔥 Vídeos virales: listado para revisión cualitativa")
    st.caption(
        "Vídeos con vistas anormalmente altas para su categoría y formato, ordenados de más reciente a "
        "más antiguo. Es el listado recomendado para que el equipo de contenido estudie qué se hizo bien."
    )

    picos_virales = video[video["z_views_categoria_formato"] > 2].sort_values("antiguedad_dias")

    col1, col2, col3 = st.columns(3)
    col1.metric("Vídeos virales detectados", len(picos_virales))
    col2.metric("Shorts", int((picos_virales["formato"] == "Short").sum()))
    col3.metric("Vídeos largos", int((picos_virales["formato"] == "Largo").sum()))

    st.divider()
    tabla = picos_virales[[
        "titulo", "categoria", "formato", "fecha_publicacion", "dia_semana_publicacion",
        "antiguedad_dias", "views_totales", "retencion_media",
    ]].copy()
    tabla["dia_semana_publicacion"] = tabla["dia_semana_publicacion"].map(DIAS_ES_MINUSCULA)
    tabla["retencion_media"] = (tabla["retencion_media"] * 100).round(1)
    tabla.columns = [
        "Título", "Categoría", "Formato", "Fecha de publicación", "Día de la semana",
        "Antigüedad (días)", "Vistas totales", "Retención (%)",
    ]
    st.dataframe(tabla, width="stretch", hide_index=True)
    st.download_button(
        "Descargar listado (CSV)", tabla.to_csv(index=False).encode("utf-8"),
        file_name="golazo_videos_virales.csv", mime="text/csv",
    )


def seccion_fichajes(datos):
    video = datos["video"]

    st.title("💼 Fichajes en ventana de mercado vs. resto de categorías")
    st.caption(f"Ventana de mercado considerada: {NOMBRES_MESES_VENTANA}")

    en_ventana = video[video["en_ventana_fichajes"]].copy()
    en_ventana["es_fichajes"] = en_ventana["categoria"] == "Fichajes"

    col1, col2 = st.columns(2)
    col1.metric("Vídeos publicados en ventana", len(en_ventana))
    col2.metric("De ellos, Fichajes", int(en_ventana["es_fichajes"].sum()))

    st.divider()
    st.subheader("Dentro de la ventana de mercado: Fichajes vs. resto de categorías")
    comparativa = en_ventana.groupby("es_fichajes")[
        ["views_totales", "ratio_likes_vista", "ratio_comentarios_vista", "retencion_media"]
    ].mean()
    comparativa.index = comparativa.index.map({True: "Fichajes", False: "Resto de categorías"})
    comparativa.index.name = "grupo"

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            comparativa.reset_index(), x="grupo", y="views_totales", color="grupo",
            color_discrete_map={"Fichajes": COLOR_PRIMARIO, "Resto de categorías": COLOR_NEUTRO},
            labels={"grupo": "", "views_totales": "Vistas medias"},
        )
        fig.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=10))
        st.plotly_chart(fig, width="stretch")
    with col2:
        fig2 = px.bar(
            comparativa.reset_index(), x="grupo", y="retencion_media", color="grupo",
            color_discrete_map={"Fichajes": COLOR_PRIMARIO, "Resto de categorías": COLOR_NEUTRO},
            labels={"grupo": "", "retencion_media": "Retención media"},
        )
        fig2.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=10))
        fig2.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig2, width="stretch")

    diferencia_views = (comparativa.loc["Fichajes", "views_totales"] / comparativa.loc["Resto de categorías", "views_totales"] - 1) * 100
    if diferencia_views > 0:
        st.success(f"**Dentro de la ventana de mercado, Fichajes supera al resto en un {diferencia_views:+.0f} %** de vistas medias.")
    else:
        st.warning(f"**Fichajes no supera al resto de categorías dentro de la ventana** ({diferencia_views:+.0f} %).")

    st.divider()
    st.subheader("Fichajes dentro vs. fuera de la ventana")
    fichajes = video[video["categoria"] == "Fichajes"]
    comparativa_interna = fichajes.groupby("en_ventana_fichajes")["views_totales"].mean()
    comparativa_interna.index = comparativa_interna.index.map({True: "En ventana", False: "Fuera de ventana"})
    st.bar_chart(comparativa_interna)

    with st.expander("Ver tabla de datos"):
        st.dataframe(comparativa.round(4), width="stretch")


def seccion_categorias_debiles(datos):
    video = datos["video"]

    st.title("📊 Categorías débiles: ¿rellenar huecos o descartar?")
    st.info(
        "Esta pregunta no es comprobable empíricamente solo con datos históricos: es una decisión de "
        "capacidad de producción. El análisis aporta un ranking objetivo para apoyar la decisión.",
        icon="ℹ️",
    )

    ranking = video.groupby("categoria").agg(
        n_videos=("video_id", "count"),
        views_medias=("views_totales", "mean"),
        retencion_media=("retencion_media", "mean"),
    ).sort_values("views_medias")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Vistas medias por categoría")
        fig = px.bar(
            ranking.reset_index(), x="views_medias", y="categoria", orientation="h",
            labels={"views_medias": "Vistas medias", "categoria": ""},
            color_discrete_sequence=[COLOR_PRIMARIO],
        )
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=10), height=350)
        fig.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig, width="stretch")
    with col2:
        st.subheader("Retención media por categoría")
        fig2 = px.bar(
            ranking.sort_values("retencion_media").reset_index(), x="retencion_media", y="categoria", orientation="h",
            labels={"retencion_media": "Retención media", "categoria": ""},
            color_discrete_sequence=[COLOR_ACENTO],
        )
        fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=10), height=350)
        fig2.update_xaxes(tickformat=".0%")
        fig2.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig2, width="stretch")

    st.divider()
    st.subheader("Ranking completo (de más débil a más fuerte)")
    tabla = ranking.copy()
    tabla["views_medias"] = tabla["views_medias"].round(0)
    tabla["retencion_media"] = (tabla["retencion_media"] * 100).round(1)
    tabla.columns = ["N.º de vídeos", "Vistas medias", "Retención media (%)"]
    st.dataframe(tabla, width="stretch")

    categoria_mas_debil = ranking.index[0]
    st.warning(
        f"**{categoria_mas_debil}** es la categoría más débil del canal en vistas medias. Es la primera "
        f"candidata a usarse como relleno de bajo coste (formato Short) o a descartarse si la capacidad "
        f"de producción es limitada."
    )


def seccion_retencion(datos):
    video = datos["video"]

    st.title("🏆 Top por retención: la palanca económica real")
    st.caption(
        "No solo importa la vista o la viralidad: la retención es la métrica que más condiciona la "
        "monetización efectiva y la recomendación del algoritmo de YouTube."
    )

    tab_short, tab_largo = st.tabs(["Shorts", "Vídeos largos"])
    for tab, formato, color in [(tab_short, "Short", COLOR_ALERTA), (tab_largo, "Largo", COLOR_PRIMARIO)]:
        with tab:
            top10 = video[video["formato"] == formato].sort_values("retencion_media", ascending=False).head(10)
            fig = px.bar(
                top10, x="retencion_media", y="titulo", orientation="h",
                labels={"retencion_media": "Retención media", "titulo": ""},
                hover_data=["categoria", "views_totales"],
                color_discrete_sequence=[color],
            )
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=10), height=420)
            fig.update_xaxes(tickformat=".0%")
            fig.update_yaxes(categoryorder="total ascending")
            st.plotly_chart(fig, width="stretch")

            categoria_dominante = top10["categoria"].mode().iloc[0]
            n_dominante = (top10["categoria"] == categoria_dominante).sum()
            nombre_formato = "shorts" if formato == "Short" else "vídeos largos"
            st.success(
                f"**Categoría más representada en el top 10 de {nombre_formato} por retención:** "
                f"{categoria_dominante} ({n_dominante} de 10)."
            )
            with st.expander("Ver tabla completa"):
                tabla = top10[["titulo", "categoria", "duracion_segundos", "views_totales", "retencion_media"]].copy()
                tabla["retencion_media"] = (tabla["retencion_media"] * 100).round(1)
                tabla.columns = ["Título", "Categoría", "Duración (s)", "Vistas totales", "Retención (%)"]
                st.dataframe(tabla, width="stretch", hide_index=True)


SECCIONES = {
    "Portada": seccion_portada,
    "1. Opinión post-partido": seccion_opinion,
    "2. Seguimiento del club": seccion_seguimiento,
    "3. Curiosidades vs. Afición": seccion_curiosidades,
    "4. Vídeos virales": seccion_virales,
    "5. Fichajes en ventana": seccion_fichajes,
    "6. Categorías débiles": seccion_categorias_debiles,
    "7. Top por retención": seccion_retencion,
}

st.sidebar.title("⚽ Golazo")
st.sidebar.caption("Informe GrowUP")
seleccion = st.sidebar.radio("Ir a:", list(SECCIONES.keys()), label_visibility="collapsed")

if "seccion_anterior" not in st.session_state:
    st.session_state.seccion_anterior = seleccion

if seleccion != st.session_state.seccion_anterior:
    st.session_state.seccion_anterior = seleccion
    scroll_arriba()

datos = cargar_datos()
SECCIONES[seleccion](datos)
