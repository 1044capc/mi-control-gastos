import streamlit as st
import pandas as pd
import os

# Configuración de la página (Título de la pestaña e icono)
st.set_page_config(
    page_title="Gestor de Gastos Personales",
    page_icon="💰",
    layout="wide"
)

NOMBRE_ARCHIVO = "gastos.csv"

# Cargar los datos desde el archivo CSV
def cargar_datos():
    if os.path.exists(NOMBRE_ARCHIVO):
        datos = pd.read_csv(NOMBRE_ARCHIVO)
        datos["Fecha"] = pd.to_datetime(datos["Fecha"]).dt.date
        return datos
    else:
        return pd.DataFrame(columns=["Fecha", "Descripción", "Categoría", "Monto"])

# Guardar los datos en el archivo CSV
def guardar_datos(datos):
    datos.to_csv(NOMBRE_ARCHIVO, index=False)

# Cargar la información al iniciar
df_gastos = cargar_datos()

# Encabezado principal
st.title("💰 Mis Gastos Mensuales")
st.caption("App para controlar tus gastos mensuales")
st.markdown("---")

# Layout de dos columnas
col_formulario, col_reporte = st.columns([1, 2])

# =============================================================
# COLUMNA 1: Formulario para ingresar gastos
# =============================================================
with col_formulario:
    st.header("➕ Registrar Nuevo Gasto")
    
    with st.form("formulario_gastos", clear_on_submit=True):
        fecha = st.date_input("Fecha del gasto")
        descripcion = st.text_input("Descripción del gasto", placeholder="Ej. Compras del supermercado")
        categoria = st.selectbox(
            "Categoría",
            [
                "Alimentación",
                "Transporte",
                "Vivienda y Servicios",
                "Entretenimiento",
                "Salud y Bienestar",
                "Educación",
                "Otros Gastos"
            ]
        )
        monto = st.number_input("Valor del gasto: ($)", min_value=0.0, format="%.2f", step=100.0)
        
        boton_guardar = st.form_submit_button("💾 Guardar Gasto")
        
        if boton_guardar:
            if descripcion.strip() == "":
                st.error("Por favor, escribe una descripción para el gasto.")
            elif monto <= 0:
                st.error("El monto ingresado debe ser mayor a cero.")
            else:
                nuevo_registro = pd.DataFrame(
                    [[fecha, descripcion, categoria, monto]], 
                    columns=df_gastos.columns
                )
                df_gastos = pd.concat([df_gastos, nuevo_registro], ignore_index=True)
                guardar_datos(df_gastos)
                st.success("✅ ¡Gasto registrado exitosamente!")
                st.rerun()

# =============================================================
# COLUMNA 2: Reporte General e Historial
# =============================================================
with col_reporte:
    st.header("📊 Resumen y Reporte General")
    
    if df_gastos.empty:
        st.info("Aún no tienes gastos registrados. Utiliza el formulario de la izquierda para agregar tu primer gasto.")
    else:
        # Métricas resumidas
        total_acumulado = df_gastos["Monto"].sum()
        total_movimientos = len(df_gastos)
        promedio_por_gasto = df_gastos["Monto"].mean()
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Gastado", f"${total_acumulado:,.2f}")
        m2.metric("Promedio por Registro", f"${promedio_por_gasto:,.2f}")
        m3.metric("N° de Gastos", total_movimientos)
        
        st.markdown("---")
        
        # Gráfico por Categoría
        st.subheader("📈 Gastos acumulados por Categoría")
        gastos_categoria = df_gastos.groupby("Categoría")["Monto"].sum().reset_index()
        st.bar_chart(data=gastos_categoria, x="Categoría", y="Monto")
        
        # Tabla del Historial
        st.subheader("📋 Historial Completo de Movimientos")
        st.dataframe(df_gastos, use_container_width=True)