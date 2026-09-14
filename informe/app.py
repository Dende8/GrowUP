import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import NOMBRES_MESES_VENTANA, cargar_datos, dia_es

st.set_page_config(page_title="Golazo - Informe GrowUP", page_icon="⚽", layout="wide")

st.markdown(
    """
    <style>
    .main > div { padding-top: 2rem; }
    h1, h2, h3 { font-weight: 600; color: #1B2A4A; }
    [data-testid="stMetricValue"] { color: #2E6E9E; }
    hr { margin: 1.5rem 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

COLOR_PRIMARIO = "#2E6E9E"
COLOR_ACENTO = "#F2A65A"
COLOR_ALERTA = "#B23A2E"
COLOR_NEUTRO = "#C9CDD4"


# ---------------------------------------------------------------------------
# Secciones
# ---------------------------------------------------------------------------

def seccion_portada(datos):
    canal = datos["canal"].iloc[0]
    video = datos["video"]
    evolucion = datos["evolucion"]

    st.title("⚽ Golazo - Informe estrategico")
    st.caption("Preparado por GrowUP - Analisis basado en datos reales y sinteticos del canal")
    st.divider()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Suscriptores", f"{canal['suscriptores']:,}".replace(",", "."))
    col2.metric("Videos publicados", f"{canal['total_videos']}")
    col3.metric("Vistas (30 dias)", f"{evolucion['views'].sum():,}".replace(",", "."))
    col4.metric("Suscriptores ganados (30 dias)", f"+{evolucion['subscribers_gained'].sum()}")
    dias_fuertes_es = ", ".join(dia_es(d) for d in datos["dias_fuertes"])
    col5.metric("Dias de mayor audiencia", dias_fuertes_es)

    st.divider()

    st.subheader("Evolucion de audiencia (ultimos 30 dias)")
    fig = px.line(
        evolucion.sort_values("fecha"), x="fecha", y="views",
        labels={"fecha": "", "views": "Vistas"},
        color_discrete_sequence=[COLOR_PRIMARIO],
    )
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", margin=dict(l=0, r=0, t=10, b=0), height=320)
    fig.update_traces(line=dict(width=2.5))
    st.plotly_chart(fig, width='stretch')

    st.divider()
    st.markdown(
        """
        ### Contenido de este informe

        Usa el menu de la izquierda para navegar por cada bloque del analisis:

        1. **Opinion post-partido** - existe relacion con los dias de partido?
        2. **Seguimiento del club** - ranking de categorias, dia fuerte vs. resto
        3. **Curiosidades vs. Aficion** - la oportunidad de crecimiento del canal
        4. **Videos virales** - listado para revision cualitativa
        5. **Fichajes en ventana de mercado** - comparativa con el resto de categorias
        6. **Categorias debiles** - ranking para decisiones de produccion
        7. **Top por retencion** - la palanca economica real
        """
    )


def seccion_opinion(datos):
    video = datos["video"]

    st.title("🗣️ Opinion post-partido: relacion con los dias de partido")
    st.info(
        "**Limitacion de datos:** no se dispone de la hora exacta de publicacion ni de un calendario "
        "real de partidos. Se aproxima 'dia de partido' como los dias de mayor audiencia del canal "
        "(findes) mas martes/miercoles (proxy estandar de competicion europea entre semana).",
        icon="ℹ️",
    )
    dias_fuertes_es = ", ".join(dia_es(d) for d in datos["dias_fuertes"])
    st.caption(f"Dias de partido asumidos: {dias_fuertes_es}, Martes y Miercoles")

    opinion_shorts = video[(video["categoria"] == "Opinión post-partido") & (video["formato"] == "Short")]
    comparativa = opinion_shorts.groupby("dia_relevante_partido")[
        ["views_totales", "ratio_likes_vista", "ratio_comentarios_vista", "retencion_media"]
    ].mean()
    comparativa.index = comparativa.index.map({True: "Dia de partido", False: "Resto de dias"})
    comparativa.index.name = "grupo"

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Vistas medias")
        fig = px.bar(
            comparativa.reset_index(), x="grupo", y="views_totales", color="grupo",
            color_discrete_map={"Dia de partido": COLOR_PRIMARIO, "Resto de dias": COLOR_NEUTRO},
            labels={"grupo": "", "views_totales": "Vistas medias"},
        )
        fig.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=10))
        st.plotly_chart(fig, width='stretch')
    with col2:
        st.subheader("Comentarios por vista (%)")
        fig2 = px.bar(
            comparativa.reset_index(), x="grupo", y="ratio_comentarios_vista", color="grupo",
            color_discrete_map={"Dia de partido": COLOR_PRIMARIO, "Resto de dias": COLOR_NEUTRO},
            labels={"grupo": "", "ratio_comentarios_vista": "Comentarios / vista"},
        )
        fig2.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=10))
        fig2.update_yaxes(tickformat=".2%")
        st.plotly_chart(fig2, width='stretch')

    st.subheader("Retencion media")
    fig3 = px.bar(
        comparativa.reset_index(), x="grupo", y="retencion_media", color="grupo",
        color_discrete_map={"Dia de partido": COLOR_PRIMARIO, "Resto de dias": COLOR_NEUTRO},
        labels={"grupo": "", "retencion_media": "Retencion media"},
    )
    fig3.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=10), height=300)
    fig3.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig3, width='stretch')

    st.divider()
    mejora_views = (comparativa.loc["Dia de partido", "views_totales"] / comparativa.loc["Resto de dias", "views_totales"] - 1) * 100
    mejora_comentarios = (comparativa.loc["Dia de partido", "ratio_comentarios_vista"] / comparativa.loc["Resto de dias", "ratio_comentarios_vista"] - 1) * 100
    mejora_retencion = (comparativa.loc["Dia de partido", "retencion_media"] - comparativa.loc["Resto de dias", "retencion_media"]) * 100

    st.success(
        f"**Conclusion:** los Shorts de Opinion post-partido publicados en dia de partido obtienen "
        f"**{mejora_views:+.0f}% mas vistas**, **{mejora_comentarios:+.0f}% mas comentarios por vista** "
        f"y **{mejora_retencion:+.1f} puntos mas de retencion** que el resto de dias."
    )
    with st.expander("Ver tabla de datos"):
        st.dataframe(comparativa.round(4), width='stretch')


def seccion_seguimiento(datos):
    video = datos["video"]

    st.title("📅 Seguimiento del club: ranking de categorias (Largo)")
    dias_fuertes_es = ", ".join(dia_es(d) for d in datos["dias_fuertes"])
    st.caption(f"Dia fuerte de audiencia: {dias_fuertes_es}")

    largos = video[video["formato"] == "Largo"]
    ranking_dia_fuerte = largos[largos["es_dia_fuerte"]].groupby("categoria")["views_totales"].mean().sort_values(ascending=False)
    ranking_resto = largos[~largos["es_dia_fuerte"]].groupby("categoria")["views_totales"].mean().sort_values(ascending=False)

    top_fuerte = ranking_dia_fuerte.idxmax()
    top_resto = ranking_resto.idxmax()

    col1, col2 = st.columns(2)
    col1.metric("Categoria lider en dia fuerte", top_fuerte)
    col2.metric("Categoria lider en resto de la semana", top_resto)

    st.divider()
    df_plot = pd.DataFrame({"Dia fuerte": ranking_dia_fuerte, "Resto de la semana": ranking_resto}).sort_values(
        "Dia fuerte", ascending=True
    )
    fig = go.Figure()
    fig.add_trace(go.Bar(y=df_plot.index, x=df_plot["Dia fuerte"], name="Dia fuerte", orientation="h", marker_color=COLOR_ACENTO))
    fig.add_trace(go.Bar(y=df_plot.index, x=df_plot["Resto de la semana"], name="Resto de la semana", orientation="h", marker_color=COLOR_PRIMARIO))
    fig.update_layout(
        barmode="group", plot_bgcolor="white", paper_bgcolor="white",
        xaxis_title="Vistas medias", legend=dict(orientation="h", y=-0.15), margin=dict(t=10), height=420,
    )
    st.plotly_chart(fig, width='stretch')

    st.divider()
    if top_fuerte == "Seguimiento del club" and top_resto == "Seguimiento del club":
        st.success(
            "**Confirmado:** Seguimiento del club es la categoria lider tanto en dia fuerte como en el "
            "resto de la semana - es el formato de referencia para sostener audiencia de forma constante."
        )
    else:
        st.warning(
            f"**A tener en cuenta:** Seguimiento del club no lidera en ambas ventanas con los datos "
            f"actuales (lidera {top_fuerte} en dia fuerte y {top_resto} en el resto)."
        )

    with st.expander("Ver tablas de datos"):
        c1, c2 = st.columns(2)
        c1.write("**Dia fuerte**")
        c1.dataframe(ranking_dia_fuerte.round(0), width='stretch')
        c2.write("**Resto de la semana**")
        c2.dataframe(ranking_resto.round(0), width='stretch')


def seccion_curiosidades(datos):
    video = datos["video"]

    st.title("🌟 Curiosidades de futbol vs. Aficion")
    st.caption("La oportunidad de crecimiento del canal: contenido que no depende de ser aficionado del equipo")

    curiosidades = video[video["categoria"] == "Curiosidades de fútbol"]
    aficion = video[video["categoria"] == "Afición"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Videos de Curiosidades", len(curiosidades))
    col2.metric("Videos de Aficion", len(aficion), delta=f"{len(curiosidades) - len(aficion)} de diferencia")
    ranking_categorias = video.groupby("categoria")["views_totales"].mean().sort_values(ascending=False)
    posicion_curiosidades = list(ranking_categorias.index).index("Curiosidades de fútbol") + 1
    col3.metric("Posicion de Curiosidades por vistas", f"{posicion_curiosidades}o de {len(ranking_categorias)}")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Ranking de categorias por vistas medias")
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
        st.plotly_chart(fig, width='stretch')

    with col2:
        st.subheader("Curiosidades vs. Aficion vs. media del canal")
        metricas = ["views_totales", "likes", "comentarios", "retencion_media"]
        etiquetas = ["Vistas", "Likes", "Comentarios", "Retencion"]
        comp_cur = curiosidades[metricas].mean() / video[metricas].mean() * 100
        comp_af = aficion[metricas].mean() / video[metricas].mean() * 100
        df_comp = pd.DataFrame({
            "Metrica": etiquetas * 2,
            "% sobre la media del canal": list(comp_cur.values) + list(comp_af.values),
            "Categoria": ["Curiosidades"] * 4 + ["Aficion"] * 4,
        })
        fig2 = px.bar(
            df_comp, x="Metrica", y="% sobre la media del canal", color="Categoria", barmode="group",
            color_discrete_map={"Curiosidades": COLOR_ACENTO, "Aficion": COLOR_ALERTA},
        )
        fig2.add_hline(y=100, line_dash="dot", line_color="#888")
        fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=10), height=350)
        st.plotly_chart(fig2, width='stretch')

    st.divider()
    st.subheader("Antiguedad media por categoria (es un formato reciente en la produccion?)")
    antiguedad_media = video.groupby("categoria")["antiguedad_dias"].mean().sort_values()
    fig3 = px.bar(
        antiguedad_media.reset_index(), x="antiguedad_dias", y="categoria", orientation="h",
        labels={"antiguedad_dias": "Antiguedad media (dias)", "categoria": ""},
        color_discrete_sequence=[COLOR_PRIMARIO],
    )
    fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=10), height=300)
    fig3.update_yaxes(categoryorder="total descending")
    st.plotly_chart(fig3, width='stretch')

    st.divider()
    st.success(
        f"**Conclusion:** Curiosidades de futbol ocupa la posicion **{posicion_curiosidades}a** en vistas "
        f"medias del canal, con solo **{abs(len(curiosidades) - len(aficion))} videos** de diferencia "
        f"respecto a Aficion, que es la categoria con menos vistas medias. Es una categoria a explotar: "
        f"atrae audiencia que no tiene por que ser aficionada del equipo, y es contenido facilmente "
        f"adaptable a formato Short."
    )


def seccion_virales(datos):
    video = datos["video"]

    st.title("🔥 Videos virales: listado para revision cualitativa")
    st.caption(
        "Videos con vistas anormalmente altas para su categoria y formato, ordenados de mas reciente a "
        "mas antiguo - el listado recomendado para que el equipo de contenido estudie que se hizo bien."
    )

    picos_virales = video[video["z_views_categoria_formato"] > 2].sort_values("antiguedad_dias")

    col1, col2, col3 = st.columns(3)
    col1.metric("Videos virales detectados", len(picos_virales))
    col2.metric("Shorts", int((picos_virales["formato"] == "Short").sum()))
    col3.metric("Largos", int((picos_virales["formato"] == "Largo").sum()))

    st.divider()
    tabla = picos_virales[[
        "titulo", "categoria", "formato", "fecha_publicacion", "dia_semana_publicacion",
        "antiguedad_dias", "views_totales", "retencion_media",
    ]].copy()
    tabla["dia_semana_publicacion"] = tabla["dia_semana_publicacion"].apply(dia_es)
    tabla["retencion_media"] = (tabla["retencion_media"] * 100).round(1)
    tabla.columns = [
        "Titulo", "Categoria", "Formato", "Fecha publicacion", "Dia de la semana",
        "Antiguedad (dias)", "Vistas totales", "Retencion (%)",
    ]
    st.dataframe(tabla, width='stretch', hide_index=True)
    st.download_button(
        "Descargar listado (CSV)", tabla.to_csv(index=False).encode("utf-8"),
        file_name="golazo_videos_virales.csv", mime="text/csv",
    )


def seccion_fichajes(datos):
    video = datos["video"]

    st.title("💼 Fichajes en ventana de mercado vs. resto de categorias")
    st.caption(f"Ventana de mercado asumida: {NOMBRES_MESES_VENTANA} (supuesto de dominio).")

    en_ventana = video[video["en_ventana_fichajes"]].copy()
    en_ventana["es_fichajes"] = en_ventana["categoria"] == "Fichajes"

    col1, col2 = st.columns(2)
    col1.metric("Videos publicados en ventana", len(en_ventana))
    col2.metric("De ellos, Fichajes", int(en_ventana["es_fichajes"].sum()))

    st.divider()
    st.subheader("Dentro de la ventana de mercado: Fichajes vs. resto de categorias")
    comparativa = en_ventana.groupby("es_fichajes")[
        ["views_totales", "ratio_likes_vista", "ratio_comentarios_vista", "retencion_media"]
    ].mean()
    comparativa.index = comparativa.index.map({True: "Fichajes", False: "Resto de categorias"})
    comparativa.index.name = "grupo"

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            comparativa.reset_index(), x="grupo", y="views_totales", color="grupo",
            color_discrete_map={"Fichajes": COLOR_PRIMARIO, "Resto de categorias": COLOR_NEUTRO},
            labels={"grupo": "", "views_totales": "Vistas medias"},
        )
        fig.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=10))
        st.plotly_chart(fig, width='stretch')
    with col2:
        fig2 = px.bar(
            comparativa.reset_index(), x="grupo", y="retencion_media", color="grupo",
            color_discrete_map={"Fichajes": COLOR_PRIMARIO, "Resto de categorias": COLOR_NEUTRO},
            labels={"grupo": "", "retencion_media": "Retencion media"},
        )
        fig2.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=10))
        fig2.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig2, width='stretch')

    diferencia_views = (comparativa.loc["Fichajes", "views_totales"] / comparativa.loc["Resto de categorias", "views_totales"] - 1) * 100
    if diferencia_views > 0:
        st.success(f"**Dentro de la ventana de mercado, Fichajes supera al resto en un {diferencia_views:+.0f}%** de vistas medias.")
    else:
        st.warning(f"**Con los datos actuales, Fichajes no supera al resto dentro de la ventana** ({diferencia_views:+.0f}%).")

    st.divider()
    st.subheader("Contexto adicional: Fichajes dentro vs. fuera de la ventana")
    fichajes = video[video["categoria"] == "Fichajes"]
    comparativa_interna = fichajes.groupby("en_ventana_fichajes")["views_totales"].mean()
    comparativa_interna.index = comparativa_interna.index.map({True: "En ventana", False: "Fuera de ventana"})
    st.bar_chart(comparativa_interna)

    with st.expander("Ver tabla de datos"):
        st.dataframe(comparativa.round(4), width='stretch')


def seccion_categorias_debiles(datos):
    video = datos["video"]

    st.title("📊 Categorias debiles: rellenar huecos o descartar?")
    st.info(
        "Esta pregunta no es comprobable empiricamente con datos historicos - es una decision de "
        "capacidad de produccion. El analisis aporta un ranking objetivo para apoyar la decision.",
        icon="ℹ️",
    )

    ranking = video.groupby("categoria").agg(
        n_videos=("video_id", "count"),
        views_medias=("views_totales", "mean"),
        retencion_media=("retencion_media", "mean"),
    ).sort_values("views_medias")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Vistas medias por categoria")
        fig = px.bar(
            ranking.reset_index(), x="views_medias", y="categoria", orientation="h",
            labels={"views_medias": "Vistas medias", "categoria": ""},
            color_discrete_sequence=[COLOR_PRIMARIO],
        )
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=10), height=350)
        fig.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig, width='stretch')
    with col2:
        st.subheader("Retencion media por categoria")
        fig2 = px.bar(
            ranking.sort_values("retencion_media").reset_index(), x="retencion_media", y="categoria", orientation="h",
            labels={"retencion_media": "Retencion media", "categoria": ""},
            color_discrete_sequence=[COLOR_ACENTO],
        )
        fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=10), height=350)
        fig2.update_xaxes(tickformat=".0%")
        fig2.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig2, width='stretch')

    st.divider()
    st.subheader("Ranking completo (de mas debil a mas fuerte)")
    tabla = ranking.copy()
    tabla["views_medias"] = tabla["views_medias"].round(0)
    tabla["retencion_media"] = (tabla["retencion_media"] * 100).round(1)
    tabla.columns = ["No de videos", "Vistas medias", "Retencion media (%)"]
    st.dataframe(tabla, width='stretch')

    categoria_mas_debil = ranking.index[0]
    st.warning(
        f"**{categoria_mas_debil}** es la categoria mas debil del canal en vistas medias. Es la primera "
        f"candidata a usarse como relleno de bajo coste (formato Short) o a descartarse si la capacidad "
        f"de produccion es limitada."
    )


def seccion_retencion(datos):
    video = datos["video"]

    st.title("🏆 Top por retencion - la palanca economica real")
    st.caption(
        "No solo importa la vista o la viralidad: la retencion es la metrica que mas condiciona la "
        "monetizacion efectiva y la recomendacion del algoritmo de YouTube."
    )

    tab_short, tab_largo = st.tabs(["Shorts", "Videos largos"])
    for tab, formato, color in [(tab_short, "Short", COLOR_ALERTA), (tab_largo, "Largo", COLOR_PRIMARIO)]:
        with tab:
            top10 = video[video["formato"] == formato].sort_values("retencion_media", ascending=False).head(10)
            fig = px.bar(
                top10, x="retencion_media", y="titulo", orientation="h",
                labels={"retencion_media": "Retencion media", "titulo": ""},
                hover_data=["categoria", "views_totales"],
                color_discrete_sequence=[color],
            )
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=10), height=420)
            fig.update_xaxes(tickformat=".0%")
            fig.update_yaxes(categoryorder="total ascending")
            st.plotly_chart(fig, width='stretch')

            categoria_dominante = top10["categoria"].mode().iloc[0]
            n_dominante = (top10["categoria"] == categoria_dominante).sum()
            st.success(
                f"**Categoria mas representada en el Top 10 de {formato.lower()}s por retencion:** "
                f"{categoria_dominante} ({n_dominante} de 10)."
            )
            with st.expander("Ver tabla completa"):
                tabla = top10[["titulo", "categoria", "duracion_segundos", "views_totales", "retencion_media"]].copy()
                tabla["retencion_media"] = (tabla["retencion_media"] * 100).round(1)
                tabla.columns = ["Titulo", "Categoria", "Duracion (s)", "Vistas totales", "Retencion (%)"]
                st.dataframe(tabla, width='stretch', hide_index=True)


# ---------------------------------------------------------------------------
# Navegacion (menu lateral, una unica pagina de codigo)
# ---------------------------------------------------------------------------

SECCIONES = {
    "Portada": seccion_portada,
    "1. Opinion post-partido": seccion_opinion,
    "2. Seguimiento del club": seccion_seguimiento,
    "3. Curiosidades vs. Aficion": seccion_curiosidades,
    "4. Videos virales": seccion_virales,
    "5. Fichajes en ventana": seccion_fichajes,
    "6. Categorias debiles": seccion_categorias_debiles,
    "7. Top por retencion": seccion_retencion,
}

st.sidebar.title("⚽ Golazo")
st.sidebar.caption("Informe GrowUP")
seleccion = st.sidebar.radio("Ir a:", list(SECCIONES.keys()), label_visibility="collapsed")

datos = cargar_datos()
SECCIONES[seleccion](datos)
