import streamlit as st
import pandas as pd
import hashlib
import os

# -------------------------------------------------------------
# Configuración inicial de la página
# -------------------------------------------------------------
st.set_page_config(
    page_title="Control de Gastos Personal",
    page_icon="💰",
    layout="wide"
)

ARCHIVO_DATOS = "gastos.csv"

# -------------------------------------------------------------
# Funciones de Seguridad y Manejo de Datos
# -------------------------------------------------------------
def encriptar_clave(password):
    """Convierte la contraseña en un hash seguro encriptado."""
    return hashlib.sha256(password.encode()).hexdigest()

# Usuarios registrados (Usuario: Contraseña encriptada)
# Usuarios registrados (Usuario: Contraseña encriptada)
USUARIOS = {
    "admin": encriptar_clave("1234"),
    "usuario1": encriptar_clave("mi_clave_123"),
    "carlos": encriptar_clave("mi_clave_secreta_2026")  # <-- Puedes agregar nuevos así
}

def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        df = pd.read_csv(ARCHIVO_DATOS)
        df["Fecha"] = pd.to_datetime(df["Fecha"]).dt.date
        return df
    else:
        return pd.DataFrame(columns=["Usuario", "Fecha", "Concepto", "Categoría", "Monto"])

def guardar_datos(df):
    df.to_csv(ARCHIVO_DATOS, index=False)

# -------------------------------------------------------------
# Control de Sesión (Login)
# -------------------------------------------------------------
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = ""

if not st.session_state.autenticado:
    st.title("🔒 Iniciar Sesión")
    
    with st.form("form_login"):
        user_input = st.text_input("Usuario")
        pass_input = st.text_input("Contraseña", type="password")
        btn_login = st.form_submit_button("Ingresar")
        
        if btn_login:
            if user_input in USUARIOS and USUARIOS[user_input] == encriptar_clave(pass_input):
                st.session_state.autenticado = True
                st.session_state.usuario_actual = user_input
                st.success(f"Bienvenido, {user_input}!")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
else:
    # -------------------------------------------------------------
    # Panel Principal (Usuario Autenticado)
    # -------------------------------------------------------------
    # Botón de Salir (Logout)
    col_titulo, col_logout = st.columns([4, 1])
    with col_titulo:
        st.title(f"💰 Control de Gastos — ({st.session_state.usuario_actual})")
    with col_logout:
        if st.button("🔴 Cerrar Sesión"):
            st.session_state.autenticado = False
            st.session_state.usuario_actual = ""
            st.rerun()

    st.markdown("---")

    # Cargar todos los datos y filtrar por el usuario actual
    df_todos = cargar_datos()
    df_usuario = df_todos[df_todos["Usuario"] == st.session_state.usuario_actual]

    col_form, col_reporte = st.columns([1, 2])

    # FORMULARIO DE REGISTRO
    with col_form:
        st.header("➕ Registrar Nuevo Gasto")
        
        with st.form("formulario_gasto", clear_on_submit=True):
            fecha = st.date_input("Fecha")
            concepto = st.text_input("Concepto / Descripción")
            categoria = st.selectbox(
                "Categoría",
                ["Comida", "Transporte", "Servicios", "Entretenimiento", "Salud", "Educación", "Otros"]
            )
            monto = st.number_input("Monto ($)", min_value=0.0, format="%.2f", step=1.0)
            
            if st.form_submit_button("Guardar Gasto"):
                if concepto.strip() == "":
                    st.error("Por favor ingresa un concepto.")
                elif monto <= 0:
                    st.error("El monto debe ser mayor a 0.")
                else:
                    nuevo_gasto = pd.DataFrame([[
                        st.session_state.usuario_actual, 
                        fecha, 
                        concepto, 
                        categoria, 
                        monto
                    ]], columns=df_todos.columns)
                    
                    df_actualizado = pd.concat([df_todos, nuevo_gasto], ignore_index=True)
                    guardar_datos(df_actualizado)
                    st.success("✅ Gasto guardado exitosamente")
                    st.rerun()

    # REPORTE Y HISTORIAL (Solo datos del usuario activo)
    with col_reporte:
        st.header("📊 Reporte General")
        
        if df_usuario.empty:
            st.info("Aún no has registrado ningún gasto con este usuario.")
        else:
            total_gastado = df_usuario["Monto"].sum()
            total_registros = len(df_usuario)
            promedio_gasto = df_usuario["Monto"].mean()
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Gastado", f"${total_gastado:,.2f}")
            m2.metric("Promedio por Gasto", f"${promedio_gasto:,.2f}")
            m3.metric("Total Registros", total_registros)
            
            st.markdown("---")
            
            st.subheader("📈 Gastos por Categoría")
            gastos_cat = df_usuario.groupby("Categoría")["Monto"].sum().reset_index()
            st.bar_chart(data=gastos_cat, x="Categoría", y="Monto")
            
            st.subheader("📋 Tu Historial")
            st.dataframe(df_usuario[["Fecha", "Concepto", "Categoría", "Monto"]], use_container_width=True)