-- ============================================================
-- Fase 6 - Esquema de base de datos para el proyecto Golazo/GrowUP
-- Motor objetivo: PostgreSQL 14+
--
-- Refleja exactamente el diagrama entidad-relación de la Fase 5:
-- CANAL (1) --- (N) VIDEO --- (N) VIDEO_TAG
--                       \--- (N) RETENCION_AUDIENCIA
-- CANAL (1) --- (N) EVOLUCION_DIARIA
-- CANAL (1) --- (N) DEMOGRAFIA
-- CANAL (1) --- (N) TRAFICO
-- CANAL (1) --- (N) INGRESOS
-- ============================================================

-- Orden de creación: primero CANAL (no depende de nadie), luego
-- todo lo que la referencia. Los DROP van en orden inverso a los
-- CREATE para poder relanzar el script sin errores de dependencias.

DROP TABLE IF EXISTS ingresos;
DROP TABLE IF EXISTS trafico;
DROP TABLE IF EXISTS demografia;
DROP TABLE IF EXISTS evolucion_diaria;
DROP TABLE IF EXISTS retencion_audiencia;
DROP TABLE IF EXISTS video_tag;
DROP TABLE IF EXISTS video;
DROP TABLE IF EXISTS canal;


-- ------------------------------------------------------------
-- CANAL — metadatos y estadísticas públicas (Data API v3)
-- ------------------------------------------------------------
CREATE TABLE canal (
    channel_id      VARCHAR(32)  PRIMARY KEY,
    titulo          VARCHAR(150) NOT NULL,
    descripcion     TEXT,
    custom_url      VARCHAR(100),
    pais            VARCHAR(2),
    fecha_creacion  DATE         NOT NULL,
    suscriptores    INTEGER      NOT NULL CHECK (suscriptores >= 0),
    total_videos    INTEGER      NOT NULL CHECK (total_videos >= 0),
    vistas_totales  BIGINT       NOT NULL CHECK (vistas_totales >= 0)
);


-- ------------------------------------------------------------
-- VIDEO — catálogo de vídeos del canal (Data API v3)
-- ------------------------------------------------------------
CREATE TABLE video (
    video_id           VARCHAR(32)  PRIMARY KEY,
    channel_id         VARCHAR(32)  NOT NULL
                        REFERENCES canal(channel_id) ON DELETE CASCADE,
    titulo             VARCHAR(200) NOT NULL,
    categoria          VARCHAR(50),
    fecha_publicacion  DATE         NOT NULL,
    duracion_segundos  INTEGER      NOT NULL CHECK (duracion_segundos > 0),
    views_totales      BIGINT       NOT NULL CHECK (views_totales >= 0),
    likes              INTEGER      NOT NULL CHECK (likes >= 0),
    comentarios        INTEGER      NOT NULL CHECK (comentarios >= 0)
);

CREATE INDEX idx_video_channel_id ON video(channel_id);
CREATE INDEX idx_video_fecha_publicacion ON video(fecha_publicacion);


-- ------------------------------------------------------------
-- VIDEO_TAG — tags de cada vídeo (relación 1:N, tags es una
-- lista de longitud variable, no encaja como columna plana)
-- ------------------------------------------------------------
CREATE TABLE video_tag (
    video_id  VARCHAR(32) NOT NULL
              REFERENCES video(video_id) ON DELETE CASCADE,
    tag       VARCHAR(50) NOT NULL,
    PRIMARY KEY (video_id, tag)
);


-- ------------------------------------------------------------
-- RETENCION_AUDIENCIA — curva de retención por vídeo
-- (Analytics API: dimensión elapsedVideoTimeRatio)
-- ------------------------------------------------------------
CREATE TABLE retencion_audiencia (
    video_id                        VARCHAR(32)   NOT NULL
                                     REFERENCES video(video_id) ON DELETE CASCADE,
    elapsed_video_time_ratio        NUMERIC(4,3)  NOT NULL
                                     CHECK (elapsed_video_time_ratio BETWEEN 0 AND 1),
    audience_watch_ratio            NUMERIC(5,4)  NOT NULL CHECK (audience_watch_ratio >= 0),
    relative_retention_performance  NUMERIC(5,3),
    PRIMARY KEY (video_id, elapsed_video_time_ratio)
);


-- ------------------------------------------------------------
-- EVOLUCION_DIARIA — serie temporal a nivel de canal
-- (Analytics API: dimensión day)
-- ------------------------------------------------------------
CREATE TABLE evolucion_diaria (
    channel_id                 VARCHAR(32)   NOT NULL
                                REFERENCES canal(channel_id) ON DELETE CASCADE,
    fecha                       DATE          NOT NULL,
    views                       BIGINT        NOT NULL CHECK (views >= 0),
    estimated_minutes_watched   BIGINT        NOT NULL CHECK (estimated_minutes_watched >= 0),
    average_view_duration       NUMERIC(8,2)  NOT NULL CHECK (average_view_duration >= 0),
    subscribers_gained          INTEGER       NOT NULL CHECK (subscribers_gained >= 0),
    subscribers_lost            INTEGER       NOT NULL CHECK (subscribers_lost >= 0),
    PRIMARY KEY (channel_id, fecha)
);


-- ------------------------------------------------------------
-- DEMOGRAFIA — reparto de audiencia por edad y género
-- (Analytics API: dimensiones ageGroup, gender)
-- ------------------------------------------------------------
CREATE TABLE demografia (
    channel_id         VARCHAR(32)  NOT NULL
                        REFERENCES canal(channel_id) ON DELETE CASCADE,
    age_group          VARCHAR(10)  NOT NULL,
    gender             VARCHAR(10)  NOT NULL,
    viewer_percentage  NUMERIC(5,2) NOT NULL CHECK (viewer_percentage BETWEEN 0 AND 100),
    PRIMARY KEY (channel_id, age_group, gender)
);


-- ------------------------------------------------------------
-- TRAFICO — vistas por fuente de tráfico
-- (Analytics API: dimensión insightTrafficSourceType)
-- ------------------------------------------------------------
CREATE TABLE trafico (
    channel_id                 VARCHAR(32)  NOT NULL
                                REFERENCES canal(channel_id) ON DELETE CASCADE,
    traffic_source_type        VARCHAR(30)  NOT NULL,
    views                       BIGINT       NOT NULL CHECK (views >= 0),
    estimated_minutes_watched   BIGINT       NOT NULL CHECK (estimated_minutes_watched >= 0),
    PRIMARY KEY (channel_id, traffic_source_type)
);


-- ------------------------------------------------------------
-- INGRESOS — ingresos estimados diarios
-- (Analytics API monetaria: dimensión day)
-- ------------------------------------------------------------
CREATE TABLE ingresos (
    channel_id           VARCHAR(32)   NOT NULL
                          REFERENCES canal(channel_id) ON DELETE CASCADE,
    fecha                 DATE          NOT NULL,
    estimated_revenue     NUMERIC(10,2) NOT NULL CHECK (estimated_revenue >= 0),
    estimated_ad_revenue  NUMERIC(10,2) NOT NULL CHECK (estimated_ad_revenue >= 0),
    cpm                   NUMERIC(8,2)  NOT NULL CHECK (cpm >= 0),
    playback_based_cpm    NUMERIC(8,2)  NOT NULL CHECK (playback_based_cpm >= 0),
    PRIMARY KEY (channel_id, fecha)
);
