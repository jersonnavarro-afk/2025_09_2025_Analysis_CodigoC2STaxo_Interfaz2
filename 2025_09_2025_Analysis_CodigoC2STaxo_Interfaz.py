import pandas as pd
import streamlit as st
from io import BytesIO

# Tu función original con lógica completa
def calcular_fees(valor, modelo, departamento):
    departamentos_con_descuento = {
        "Bebes", "Despensa", "Ferreteria", "Cocina y Hogar",
        "moda y accesorios mujer", "Libros y Revistas", "Mascotas",
        "Oficina y Papeleria", "Peliculas", "moda y accesorios hombre",
        "Belleza y Cuidado Personal", "Temporada", "Cervezas Vinos y Licores"
    }

    for min_kg, max_kg, fulfillment_pct, shipping_pct, costo_base in rangos_tarifas:
        if min_kg <= valor <= max_kg:
            if departamento in departamentos_con_descuento:
                costo_base /= 2

            if modelo == "MKP Drop":
                return costo_base, 0, costo_base
            elif modelo in {"1P", "MKP SOS"}:
                return costo_base, 0, 0
            else:
                return costo_base, costo_base * fulfillment_pct, costo_base * shipping_pct

    return None, None, None

# Rangos de tarifas
rangos_tarifas = [
    (0, 0.99, 0.5667, 0.4333, 63.00),
    (1, 1.99, 0.4861, 0.5139, 76.00),
    (2, 2.99, 0.4186, 0.5814, 91.00),
    (3, 4.99, 0.4318, 0.5682, 95.00),
    (5, 6.99, 0.4375, 0.5625, 110.01),
    (7, 8.99, 0.4445, 0.5555, 128.00),
    (9, 11.99, 0.4320, 0.5680, 150.00),
    (12, 14.99, 0.4196, 0.5804, 173.00),
    (15, 19.99, 0.4118, 0.5882, 202.00),
    (20, 29.99, 0.4585, 0.5415, 262.00),
    (30, 39.99, 0.4983, 0.5017, 316.00),
    (40, 49.99, 0.4314, 0.5686, 408.00),
    (50, 59.99, 0.3916, 0.6084, 466.00),
    (60, 66.99, 0.3648, 0.6352, 589.00),
    (67, 74.99, 0.2439, 0.7561, 820.00),
    (75, 79.99, 0.2444, 0.7556, 900.00),
    (80, 99.99, 0.2573, 0.7427, 900.80),
    (100, 119.99, 0.2501, 0.7499, 927.00),
    (120, 149.99, 0.2445, 0.7555, 1300.07),
    (150, 179.99, 0.2800, 0.7200, 1574.10),
    (180, 209.99, 0.2448, 0.7552, 1800.80),
    (210, 239.99, 0.2445, 0.7555, 2200.00),
    (240, float("inf"), 0.2445, 0.7555, 2500.08)
]

# Interfaz Streamlit
st.title("Calculadora de Fees C2S")

# Cargar archivo Excel desde el uploader
archivo = st.file_uploader("Sube tu archivo base con fees", type=["xlsx"])
if archivo:
    base = pd.read_excel(archivo)

    # Crear dropdowns para filtrar
    agrupadores = ['Todos'] + sorted(base['Agrupador'].dropna().unique().tolist())
    departamentos = ['Todos'] + sorted(base['Departamento'].dropna().unique().tolist())
    familias = ['Todos'] + sorted(base['Familia'].dropna().unique().tolist())

    agrupador_sel = st.selectbox("Filtrar por Agrupador", agrupadores)
    departamento_sel = st.selectbox("Filtrar por Departamento", departamentos)
    familia_sel = st.selectbox("Filtrar por Familia", familias)

    # Aplicar filtros
    df_filtrado = base.copy()
    if agrupador_sel != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Agrupador'] == agrupador_sel]
    if departamento_sel != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Departamento'] == departamento_sel]
    if familia_sel != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Familia'] == familia_sel]

    # Verificar si hay datos después del filtro
    if not df_filtrado.empty:
        df_filtrado[['Costo_Base', 'Fulfillment_Fee', 'Shipping_Recovery_Fee']] = df_filtrado.apply(
            lambda row: pd.Series(calcular_fees(row['max_pv_pr'], row['Modelo'], row['Departamento'])),
            axis=1
        )

        # Calcular porcentaje de participación basado en Costo_Base
        total_costo_base = df_filtrado['Costo_Base'].sum()
        df_filtrado['Porcentaje_Participacion'] = df_filtrado['Costo_Base'] / total_costo_base * 100

        # Mostrar primeros 50 registros
        df_subset = df_filtrado.head(50)
        st.dataframe(df_subset)

        # Preparar archivo para descarga
        output = BytesIO()
        df_subset.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)

        st.download_button(
            label="Descargar Excel con Fees",
            data=output,
            file_name="base_con_fees_50.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("No hay datos que coincidan con los filtros seleccionados.")