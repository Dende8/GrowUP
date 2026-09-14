# Informe GrowUP - Golazo

App de Streamlit de una sola pagina (`app.py`), con navegacion por menu lateral,
para acompanar la presentacion al cliente. Se conecta directamente a la base de
datos `golazo_growup`.

## Ubicacion

Esta carpeta (`informe/`) va en la raiz del proyecto, junto a `src/`, `sql/`, `notebooks/`:

```
golazo_growup/
├── informe/      <- esta carpeta
├── src/
├── sql/
├── notebooks/
└── ...
```

## Requisitos previos

1. Base de datos `golazo_growup` ya creada y cargada:
   ```
   python -m src.generador_sintetico
   python -m src.cargar_datos
   ```
2. Un `.env` en la raiz del proyecto con las credenciales de conexion (el mismo
   que usan los notebooks).
3. Dependencias instaladas (con el venv activado):
   ```
   pip install -r requirements.txt
   ```

## Como arrancarlo

Desde la **raiz del proyecto**:

```
streamlit run informe/app.py
```

o, si el comando `streamlit` no se reconoce en tu terminal:

```
python -m streamlit run informe/app.py
```

Se abre en `http://localhost:8501`. La navegacion entre secciones esta en el
menu lateral izquierdo (todo corre en una unica pagina, sin URLs distintas por
seccion).

## Estructura

```
informe/
├── app.py       # Unico archivo con las 8 secciones + navegacion por sidebar
├── utils.py     # Conexion a BD y columnas derivadas (compartido)
└── .streamlit/
    └── config.toml   # Tema visual
```

## Notas

- Los datos se cachean 10 minutos (`@st.cache_data(ttl=600)`). Si regeneras los
  datos y quieres verlos reflejados al momento, usa el menu (⋮ → Rerun) o
  reinicia la app.
- Cada seccion muestra el veredicto que corresponda segun los datos reales de tu
  base de datos - si algun resultado no confirma la hipotesis esperada, se
  indica con un aviso en vez de forzar una conclusion falsa.
