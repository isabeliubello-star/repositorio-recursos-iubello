import streamlit as st
import pandas as pd
import os
from pathlib import Path

# ============================================================
# CONFIGURACION DE PAGINA
# ============================================================
st.set_page_config(
    page_title="Repositorio de Recursos Digitales - IUBello",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# COLORES IUBELLO
# ============================================================
AZUL_OSCURO = "#1a3a5c"
AZUL_CLARO = "#5B9BD5"
ROJO_IU = "#C8102E"
GRIS_TEXTO = "#666666"
GRIS_FONDO = "#f4f6f8"
VERDE_GRATIS = "#27ae60"
BLANCO = "#ffffff"
NEGRO = "#2c3e50"

# ============================================================
# CSS PERSONALIZADO
# ============================================================
st.markdown(f"""
<style>
    html, body, [class*="css"] {{ font-family: 'Segoe UI', sans-serif; }}

    .iu-header {{
        display: flex; align-items: center; gap: 16px; margin-bottom: 8px;
    }}
    .iu-header-icon {{ font-size: 2.5rem; }}
    .iu-header-title {{
        font-size: 1.9rem; font-weight: 700; color: {NEGRO}; margin: 0; letter-spacing: -0.5px;
    }}
    .iu-header-sub {{
        font-size: 0.95rem; color: {GRIS_TEXTO}; margin: 4px 0 0 0;
    }}

    .metric-box {{ text-align: center; padding: 16px 8px; }}
    .metric-num {{ font-size: 2.2rem; font-weight: 700; color: {NEGRO}; line-height: 1; }}
    .metric-label {{
        font-size: 0.8rem; color: {GRIS_TEXTO}; margin-top: 4px;
        text-transform: uppercase; letter-spacing: 0.5px;
    }}
    .metric-divider {{ border-right: 1px solid #e0e0e0; }}

    .resource-card {{
        background: {BLANCO}; border: 1px solid #e8e8e8; border-radius: 12px;
        padding: 20px; height: 100%;
        transition: box-shadow 0.2s, transform 0.15s;
    }}
    .resource-card:hover {{
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transform: translateY(-2px); border-color: {AZUL_CLARO};
    }}
    .card-title {{
        font-size: 1.05rem; font-weight: 600; color: {AZUL_OSCURO};
        margin: 0 0 8px 0; line-height: 1.3;
    }}
    .card-tag {{
        display: inline-block; background: {VERDE_GRATIS}; color: white;
        font-size: 0.65rem; font-weight: 700; padding: 3px 10px;
        border-radius: 20px; text-transform: uppercase; letter-spacing: 0.5px;
        margin-left: 8px; vertical-align: middle;
    }}
    .card-tag-suscripcion {{ background: #e74c3c; }}
    .card-tag-libre {{ background: {AZUL_CLARO}; }}
    .card-meta {{ font-size: 0.82rem; color: {GRIS_TEXTO}; margin-bottom: 10px; }}
    .card-desc {{
        font-size: 0.88rem; color: #555; line-height: 1.5; margin-bottom: 14px;
    }}

    .sidebar-title {{
        font-size: 0.9rem; font-weight: 600; color: {NEGRO};
        margin-bottom: 8px; display: flex; align-items: center; gap: 6px;
    }}

    div[data-testid="stButton"] > button {{
        background: {AZUL_OSCURO}; color: white; border: none;
        border-radius: 8px; font-weight: 600;
    }}
    div[data-testid="stButton"] > button:hover {{
        background: {AZUL_CLARO}; color: white;
    }}

    .success-box {{
        background: #d4edda; border-left: 4px solid {VERDE_GRATIS};
        padding: 16px; border-radius: 8px; color: #155724;
    }}
    .cloud-notice {{
        background: #fff3cd; border: 1px solid #ffc107;
        border-radius: 8px; padding: 12px 16px;
        font-size: 0.85rem; color: #856404; margin-bottom: 16px;
    }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    /* Ocultar boton de colapsar/expandir sidebar */
    [data-testid="collapsedControl"] {{display: none;}}
    button[kind="header"] {{display: none;}}
    .css-1rs6os {{display: none;}}
    .css-17es36v {{display: none;}}
</style>
""", unsafe_allow_html=True)

# ============================================================
# RUTAS Y CONSTANTES
# ============================================================
CSV_PATH = "recursos.csv"

COLUMNAS = ['id', 'nombre', 'tipo', 'area', 'subarea', 'descripcion', 
            'institucion', 'pais', 'idioma', 'acceso', 'url', 'recursos_disp', 'estado']

# ============================================================
# FUNCIONES
# ============================================================

def cargar_csv_inicial():
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH, encoding='utf-8-sig')
        for col in COLUMNAS:
            if col not in df.columns:
                df[col] = ""
        df = df[COLUMNAS]
    else:
        df = pd.DataFrame(columns=COLUMNAS)
    for col in COLUMNAS:
        df[col] = df[col].fillna('').astype(str)
        df[col] = df[col].replace('nan', '').replace('NaN', '')
    df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(0).astype(int)
    return df


def siguiente_id(df):
    if df.empty or df['id'].max() == 0:
        return 1
    return int(df['id'].max()) + 1


def tag_acceso(acceso):
    x = str(acceso).lower().strip()
    if 'freemium' in x:
        return 'Freemium'
    elif 'gratuito' in x:
        return 'Gratuito'
    elif 'suscrip' in x:
        return 'Suscripcion'
    else:
        return 'Otro'


def tag_class(tag):
    if tag == 'Gratuito':
        return 'card-tag'
    elif tag == 'Libre':
        return 'card-tag card-tag-libre'
    else:
        return 'card-tag card-tag-suscripcion'


# ============================================================
# INICIALIZAR SESSION STATE
# ============================================================
if 'df_recursos' not in st.session_state:
    st.session_state.df_recursos = cargar_csv_inicial()

if 'vista' not in st.session_state:
    st.session_state.vista = 'tarjetas'

# ============================================================
# SIDEBAR - SIEMPRE VISIBLE
# ============================================================
with st.sidebar:
    # Logo
    logo_path = Path(__file__).parent / "logo.png"
    if logo_path.exists():
        st.image(str(logo_path), use_container_width=True)
    else:
        st.markdown(f"""
        <div style="text-align:center; margin-bottom:24px;">
            <div style="font-size:2rem; margin-bottom:4px;">📚</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="text-align:center; margin-bottom:24px;">
        <div style="font-size:0.75rem; color:{GRIS_TEXTO};">Recursos Digitales</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Navegacion con radio (mas estable que botones)
    st.markdown(f"<div class='sidebar-title'>🧭 Menu</div>", unsafe_allow_html=True)
    pagina = st.radio(
        "",
        ["🏠 Inicio", "➕ Agregar recurso", "📊 Estadisticas"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Filtros (solo en inicio)
    if pagina == "🏠 Inicio":
        st.markdown(f"<div class='sidebar-title'>🔎 Filtros</div>", unsafe_allow_html=True)

        df_side = st.session_state.df_recursos

        buscar_texto = st.text_input("Buscar por nombre o descripcion", placeholder="Escribe aqui...", key="busq")

        tipos = ['Todos'] + sorted([t for t in df_side['tipo'].unique() if t.strip()])
        filtro_tipo = st.selectbox("Tipo de recurso", tipos, key="tipo_f")

        areas = ['Todos'] + sorted([a for a in df_side['area'].unique() if a.strip()])
        filtro_area = st.selectbox("Area de conocimiento", areas, key="area_f")

        idiomas = ['Todos'] + sorted([i for i in df_side['idioma'].unique() if i.strip()])
        filtro_idioma = st.selectbox("Idioma", idiomas, key="idioma_f")

        paises = ['Todos'] + sorted([p for p in df_side['pais'].unique() if p.strip()])
        filtro_pais = st.selectbox("Pais / Institucion de origen", paises, key="pais_f")

        st.session_state.filtros = {
            'texto': buscar_texto,
            'tipo': filtro_tipo,
            'area': filtro_area,
            'idioma': filtro_idioma,
            'pais': filtro_pais
        }

    st.markdown("---")
    st.markdown(f"""
    <div style="font-size:0.75rem; color:{GRIS_TEXTO}; text-align:center;">
        Institucion Universitaria<br>
        <strong style="color:{AZUL_OSCURO};">Publica de Bello</strong>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# PAGINA: INICIO
# ============================================================
if pagina == "🏠 Inicio":
    df = st.session_state.df_recursos.copy()
    filtros = st.session_state.get('filtros', {})

    # Header
    st.markdown(f"""
    <div class="iu-header">
        <div class="iu-header-icon">📚</div>
        <div>
            <div class="iu-header-title">Repositorio de Recursos Digitales</div>
            <div class="iu-header-sub">Catalogo institucional IUBello de bibliotecas, repositorios, plataformas, simuladores y herramientas educativas de acceso gratuito.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Aplicar filtros
    df_filtrado = df.copy()

    if filtros.get('texto'):
        txt = filtros['texto'].lower()
        mask = (
            df_filtrado['nombre'].str.lower().str.contains(txt, na=False) |
            df_filtrado['descripcion'].str.lower().str.contains(txt, na=False) |
            df_filtrado['institucion'].str.lower().str.contains(txt, na=False)
        )
        df_filtrado = df_filtrado[mask]

    if filtros.get('tipo') and filtros['tipo'] != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['tipo'] == filtros['tipo']]
    if filtros.get('area') and filtros['area'] != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['area'] == filtros['area']]
    if filtros.get('idioma') and filtros['idioma'] != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['idioma'] == filtros['idioma']]
    if filtros.get('pais') and filtros['pais'] != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['pais'] == filtros['pais']]

    # Ordenar alfabeticamente
    df_filtrado = df_filtrado.sort_values('nombre', ascending=True).reset_index(drop=True)

    # Metricas
    total = len(df)
    mostrados = len(df_filtrado)
    gratuitos = len(df[df['acceso'].str.contains('Gratuito|Libre', case=False, na=False)])
    tipos_distintos = df['tipo'].replace('', pd.NA).dropna().nunique()

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-box metric-divider"><div class="metric-num">{mostrados}</div><div class="metric-label">Recursos mostrados</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-box metric-divider"><div class="metric-num">{total}</div><div class="metric-label">Total en catalogo</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-box metric-divider"><div class="metric-num">{gratuitos}</div><div class="metric-label">100% gratuitos</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-box"><div class="metric-num">{tipos_distintos}</div><div class="metric-label">Tipos distintos</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # Toggle vista
    col_toggle, _ = st.columns([2, 4])
    with col_toggle:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔴 Tarjetas", use_container_width=True,
                        type="primary" if st.session_state.vista == 'tarjetas' else "secondary"):
                st.session_state.vista = 'tarjetas'
                st.rerun()
        with c2:
            if st.button("⚪ Tabla", use_container_width=True,
                        type="primary" if st.session_state.vista == 'tabla' else "secondary"):
                st.session_state.vista = 'tabla'
                st.rerun()

    # VISTA TARJETAS
    if st.session_state.vista == 'tarjetas':
        if df_filtrado.empty:
            st.info("No se encontraron recursos con los filtros seleccionados.")
        else:
            for i in range(0, len(df_filtrado), 2):
                cols = st.columns(2)
                for j in range(2):
                    idx = i + j
                    if idx < len(df_filtrado):
                        row = df_filtrado.iloc[idx]
                        with cols[j]:
                            tag = tag_acceso(row['acceso'])
                            tag_cls = tag_class(tag)
                            meta_parts = [p for p in [row['tipo'], row['area'], row['idioma']] if p.strip()]
                            meta = ' · '.join(meta_parts) if meta_parts else '—'
                            desc = str(row['descripcion'])[:200]
                            if len(str(row['descripcion'])) > 200:
                                desc += '...'

                            st.markdown(f"""
                            <div class="resource-card">
                                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                                    <div class="card-title">{row['nombre']}</div>
                                    <span class="{tag_cls}">{tag}</span>
                                </div>
                                <div class="card-meta">{meta}</div>
                                <div class="card-desc">{desc}</div>
                            </div>
                            """, unsafe_allow_html=True)

                            url = str(row['url']).strip()
                            if url.startswith('http'):
                                st.link_button("🔗 Visitar recurso", url, use_container_width=True)
                            else:
                                st.button("🔗 Sin enlace", disabled=True, use_container_width=True)

    # VISTA TABLA
    else:
        if df_filtrado.empty:
            st.info("No se encontraron recursos.")
        else:
            st.dataframe(
                df_filtrado[['nombre', 'tipo', 'area', 'idioma', 'acceso', 'institucion', 'pais']],
                use_container_width=True, hide_index=True,
                column_config={
                    'nombre': 'Nombre', 'tipo': 'Tipo', 'area': 'Area',
                    'idioma': 'Idioma', 'acceso': 'Acceso',
                    'institucion': 'Institucion', 'pais': 'Pais'
                }
            )


# ============================================================
# PAGINA: AGREGAR RECURSO
# ============================================================
elif pagina == "➕ Agregar recurso":
    st.markdown(f'<div class="iu-header-title" style="margin-bottom:4px;">➕ Agregar Nuevo Recurso</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="iu-header-sub" style="margin-bottom:24px;">Completa el formulario para registrar un nuevo recurso en el catalogo IUBello.</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="cloud-notice">
        <strong>⚠️ Importante:</strong> En Streamlit Cloud los cambios se guardan solo durante la sesion.
        Al finalizar, descarga el CSV actualizado y subelo a tu repositorio de GitHub para persistir los datos.
    </div>
    """, unsafe_allow_html=True)

    # Valores dinamicos del CSV
    df_vals = st.session_state.df_recursos
    tipos_unicos = sorted([t for t in df_vals['tipo'].unique() if t.strip()]) + ["Otro (nuevo)"]
    areas_unicas = sorted([a for a in df_vals['area'].unique() if a.strip()]) + ["Otro (nuevo)"]
    idiomas_unicos = sorted([i for i in df_vals['idioma'].unique() if i.strip()]) + ["Otro (nuevo)"]
    accesos_unicos = sorted([a for a in df_vals['acceso'].unique() if a.strip()]) + ["Otro (nuevo)"]

    with st.form("form_agregar", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre del recurso *", placeholder="Ej: Khan Academy")
            tipo_sel = st.selectbox("Tipo *", [""] + tipos_unicos)
            tipo = st.text_input("Tipo (personalizado)", placeholder="Escribe el tipo si seleccionaste 'Otro'",
                                 value="" if tipo_sel != "Otro (nuevo)" else "") if tipo_sel == "Otro (nuevo)" else tipo_sel

            area_sel = st.selectbox("Area de conocimiento", [""] + areas_unicas)
            area = st.text_input("Area (personalizada)", placeholder="Escribe el area si seleccionaste 'Otro'",
                                value="" if area_sel != "Otro (nuevo)" else "") if area_sel == "Otro (nuevo)" else area_sel

            subarea = st.text_input("Sub area", placeholder="Ej: Algebra, Historia...")

        with col2:
            institucion = st.text_input("Institucion responsable", placeholder="Ej: Fundacion Carlos Slim")
            pais = st.text_input("Pais", placeholder="Ej: Colombia")

            idioma_sel = st.selectbox("Idioma", [""] + idiomas_unicos)
            idioma = st.text_input("Idioma (personalizado)", placeholder="Escribe el idioma si seleccionaste 'Otro'",
                                  value="" if idioma_sel != "Otro (nuevo)" else "") if idioma_sel == "Otro (nuevo)" else idioma_sel

            acceso_sel = st.selectbox("Tipo de acceso *", [""] + accesos_unicos)
            acceso = st.text_input("Acceso (personalizado)", placeholder="Escribe el acceso si seleccionaste 'Otro'",
                                  value="" if acceso_sel != "Otro (nuevo)" else "") if acceso_sel == "Otro (nuevo)" else acceso_sel

        descripcion = st.text_area("Descripcion", placeholder="Describe el recurso...", height=100)
        url = st.text_input("URL *", placeholder="https://...")
        recursos_disp = st.text_input("Recursos disponibles", placeholder="Ej: Libros, videos, cursos, simuladores...")
        estado = st.selectbox("Estado de revision", ["Pendiente", "Revisado", "Validado"])

        st.markdown("---")
        enviado = st.form_submit_button("💾 Guardar recurso", use_container_width=True)

        if enviado:
            if not nombre or not tipo or not url:
                st.error("⚠️ Completa los campos obligatorios marcados con *")
            else:
                df = st.session_state.df_recursos
                nuevo_id = siguiente_id(df)
                nuevo = pd.DataFrame([{
                    'id': nuevo_id, 'nombre': nombre, 'tipo': tipo, 'area': area,
                    'subarea': subarea, 'descripcion': descripcion,
                    'institucion': institucion, 'pais': pais, 'idioma': idioma,
                    'acceso': acceso, 'url': url, 'recursos_disp': recursos_disp,
                    'estado': estado
                }])
                st.session_state.df_recursos = pd.concat([df, nuevo], ignore_index=True)
                st.success(f"✅ Recurso guardado: **{nombre}** (ID: {nuevo_id})")
                st.balloons()

    st.markdown("---")
    st.subheader("📥 Descargar datos actualizados")
    csv_data = st.session_state.df_recursos.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="Descargar recursos.csv actualizado",
        data=csv_data, file_name="recursos.csv", mime="text/csv",
        use_container_width=True
    )
    st.info("Sube este archivo a tu repositorio de GitHub para que los cambios persistan.")


# ============================================================
# PAGINA: BUSCAR
# ============================================================
elif pagina == "🔍 Buscar":
    st.markdown(f'<div class="iu-header-title" style="margin-bottom:4px;">🔍 Busqueda Avanzada</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="iu-header-sub" style="margin-bottom:24px;">Busca recursos por palabra clave en cualquier campo.</div>', unsafe_allow_html=True)

    busqueda = st.text_input("Escribe para buscar:", placeholder="Ej: biblioteca, Colombia, matematicas, juegos...")

    if busqueda:
        df = st.session_state.df_recursos
        txt = busqueda.lower()
        mask = (
            df['nombre'].str.lower().str.contains(txt, na=False) |
            df['descripcion'].str.lower().str.contains(txt, na=False) |
            df['institucion'].str.lower().str.contains(txt, na=False) |
            df['pais'].str.lower().str.contains(txt, na=False) |
            df['tipo'].str.lower().str.contains(txt, na=False) |
            df['area'].str.lower().str.contains(txt, na=False)
        )
        resultados = df[mask]

        st.markdown(f"**{len(resultados)} resultado(s) encontrado(s):**")

        for _, row in resultados.iterrows():
            tag = tag_acceso(row['acceso'])
            tag_cls = tag_class(tag)
            meta_parts = [p for p in [row['tipo'], row['area'], row['idioma']] if p.strip()]
            meta = ' · '.join(meta_parts) if meta_parts else '—'

            with st.container():
                st.markdown(f"""
                <div class="resource-card">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div class="card-title">{row['nombre']}</div>
                        <span class="{tag_cls}">{tag}</span>
                    </div>
                    <div class="card-meta">{meta}</div>
                    <div class="card-desc">{str(row['descripcion'])[:250]}{'...' if len(str(row['descripcion'])) > 250 else ''}</div>
                    <div style="font-size:0.8rem; color:{GRIS_TEXTO}; margin-top:8px;">
                        🏛️ {row['institucion'] or '—'} | 🌍 {row['pais'] or '—'}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                url = str(row['url']).strip()
                if url.startswith('http'):
                    st.link_button("🔗 Visitar recurso", url)
    else:
        st.info("Escribe algo arriba para comenzar la busqueda.")


# ============================================================
# PAGINA: ESTADISTICAS
# ============================================================
elif pagina == "📊 Estadisticas":
    st.markdown(f'<div class="iu-header-title" style="margin-bottom:4px;">📊 Estadisticas del Repositorio</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="iu-header-sub" style="margin-bottom:24px;">Visualizacion de datos del catalogo IUBello.</div>', unsafe_allow_html=True)

    df = st.session_state.df_recursos

    if df.empty or len(df) == 0:
        st.info("No hay datos para mostrar.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📊 Por tipo de recurso")
            tc = df[df['tipo'] != '']['tipo'].value_counts()
            if not tc.empty:
                st.bar_chart(tc, color=AZUL_OSCURO)
            else:
                st.info("Sin datos.")
        with c2:
            st.subheader("🔓 Por tipo de acceso")
            ac = df[df['acceso'] != '']['acceso'].value_counts()
            if not ac.empty:
                st.bar_chart(ac, color=AZUL_CLARO)
            else:
                st.info("Sin datos.")

        c3, c4 = st.columns(2)
        with c3:
            st.subheader("🌍 Por pais")
            pc = df[df['pais'] != '']['pais'].value_counts()
            if not pc.empty:
                st.dataframe(pc.reset_index().rename(columns={'index':'Pais','pais':'Cantidad'}),
                           use_container_width=True, hide_index=True)
            else:
                st.info("Sin datos.")
        with c4:
            st.subheader("🗣️ Por idioma")
            ic = df[df['idioma'] != '']['idioma'].value_counts()
            if not ic.empty:
                st.dataframe(ic.reset_index().rename(columns={'index':'Idioma','idioma':'Cantidad'}),
                           use_container_width=True, hide_index=True)
            else:
                st.info("Sin datos.")

        st.markdown("---")
        st.subheader("📋 Tabla completa")
        st.dataframe(df, use_container_width=True, hide_index=True)
