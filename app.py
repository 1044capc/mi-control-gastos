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

ARCHIVO_GASTOS = "gastos.csv"
ARCHIVO_USUARIOS = "usuarios.csv"

# -------------------------------------------------------------
# Funciones de Manejo de Usuarios y Seguridad
# -------------------------------------------------------------
def encriptar_clave(password):
    """Convierte la contraseña en un hash seguro encriptado."""
    return hashlib.sha256(str(password).encode()).hexdigest()

def cargar_usuarios():
    """Carga los usuarios registrados desde el archivo CSV."""
    if os.path.exists(ARCHIVO_USUARIOS):
        df = pd.read_csv(ARCHIVO_USUARIOS, dtype={"Usuario": str})
        return df
    else:
        # Crear usuario por defecto la primera vez
        df_inicial = pd.DataFrame([
            {"Usuario": "12345", "Clave_Hash": encriptar_clave("1234"), "Nombre": "Administrador", "Correo": "admin@mail.com", "Telefono": ""}
        ])
        df_inicial.to_csv(ARCHIVO_USUARIOS, index=False)
        return df_inicial

def guardar_usuario(usuario, clave, nombre, correo, telefono):
    """Guarda un nuevo usuario en el archivo CSV."""
    df_users = cargar_usuarios()
    nuevo_user = pd.DataFrame([{
        "Usuario": str(usuario).strip(),
        "Clave_Hash": encriptar_clave(clave),
        "Nombre": nombre.strip(),
        "Correo": correo.strip(),
        "Telefono": str(telefono).strip()
    }])
    df_actualizado = pd.concat([df_users, nuevo_user], ignore_index=True)
    df_actualizado.to_csv(ARCHIVO_USUARIOS, index=False)

def cargar_gastos():
    """Carga los gastos registrados desde el archivo CSV."""
    if os.path.exists(ARCHIVO_GASTOS):
        df = pd.read_csv(ARCHIVO_GASTOS, dtype={"Usuario": str})
        if not df.empty and "Fecha" in df.columns:
            df["Fecha"] = pd.to_datetime(df["Fecha"]).dt.date
        return df
    else:
        return pd.DataFrame(columns=["Usuario", "Fecha", "Concepto", "Categoría", "Monto"])

def guardar_gastos(df):
    """Guarda la tabla de gastos en el archivo CSV."""
    df.to_csv(ARCHIVO_GASTOS, index=False)

# -------------------------------------------------------------
# Control de Sesión (Login y Registro)
# -------------------------------------------------------------
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = ""
if "nombre_actual" not in st.session_state:
    st.session_state.nombre_actual = ""

if not st.session_state.autenticado:
    st.title("🔐 Acceso al Sistema de Gastos")
    
    tab_login, tab_registro = st.tabs(["🔑 Iniciar Sesión", "📝 Registrar Nueva Cuenta"])
    
    # ---------------------------------------------------------
    # TAB 1: INICIAR SESIÓN
    # ---------------------------------------------------------
    with tab_login:
        with st.form("form_login"):
            user_input = st.text_input("Usuario o ID (pueden ser números)", help="Ejemplo: 12345 o tu documento")
            pass_input = st.text_input("Contraseña", type="password")
            btn_login = st.form_submit_button("Ingresar")
            
            if btn_login:
                user_clean = str(user_input).strip()
                pass_clean = str(pass_input).strip()
                
                if not user_clean or not pass_clean:
                    st.error("Por favor completa el usuario y la contraseña.")
                else:
                    df_users = cargar_usuarios()
                    user_match = df_users[df_users["Usuario"] == user_clean]
                    
                    if not user_match.empty:
                        hash_guardado = user_match.iloc[0]["Clave_Hash"]
                        if hash_guardado == encriptar_clave(pass_clean):
                            st.session_state.autenticado = True
                            st.session_state.usuario_actual = user_clean
                            st.session_state.nombre_actual = user_match.iloc[0]["Nombre"] if pd.notna(user_match.iloc[0]["Nombre"]) and user_match.iloc[0]["Nombre"] != "" else user_clean
                            st.success(f"¡Bienvenido/a, {st.session_state.nombre_actual}!")
                            st.rerun()
                        else:
                            st.error("Contraseña incorrecta.")
                    else:
                        st.error("El usuario ingresado no existe. Regístrate en la pestaña adyacente.")

    # ---------------------------------------------------------
    # TAB 2: REGISTRARSE
    # ---------------------------------------------------------
    with tab_registro:
        st.subheader("Crea tu cuenta de usuario")
        with st.form("form_registro", clear_on_submit=True):
            reg_usuario = st.text_input("Usuario o N° de Identificación (Obligatorio)*", help="Puedes usar un número como tu cédula o ID")
            reg_clave = st.text_input("Contraseña (Obligatorio)*", type="password")
            
            st.markdown("---")
            st.caption("📌 **Campos Opcionales:**")
            reg_nombre = st.text_input("Nombre y Apellido (Opcional)")
            reg_correo = st.text_input("Correo electrónico (Opcional)")
            reg_telefono = st.text_input("Número de Teléfono (Opcional)")
            
            btn_registro = st.form_submit_button("Crear Cuenta")
            
            if btn_registro:
                user_clean = str(reg_usuario).strip()
                clave_clean = str(reg_clave).strip()
                
                if not user_clean or not clave_clean:
                    st.error("El Usuario y la Contraseña son obligatorios.")
                else:
                    df_users = cargar_usuarios()
                    if user_clean in df_users["Usuario"].values:
                        st.error("Este usuario o ID ya se encuentra registrado. Intenta con otro o inicia sesión.")
                    else:
                        guardar_usuario(user_clean, clave_clean, reg_nombre, reg_correo, reg_telefono)
                        st.success("🎉 ¡Cuenta creada con éxito! Ahora puedes iniciar sesión desde la pestaña 'Iniciar Sesión'.")

else:
    # -------------------------------------------------------------
    # PANEL PRINCIPAL (USUARIO CONECTADO)
    # -------------------------------------------------------------
    col_titulo, col_logout = st.columns([4, 1])
    with col_titulo:
        st.title(f"💰 Control de Gastos — {st.session_state.nombre_actual}")
        st.caption(f"ID Usuario: `{st.session_state.usuario_actual}`")
    with col_logout:
        if st.button("🔴 Cerrar Sesión"):
            st.session_state.autenticado = False
            st.session_state.usuario_actual = ""
            st.session_state.nombre_actual = ""
            st.rerun()

    st.markdown("---")

    df_todos = cargar_gastos()
    df_usuario = df_todos[df_todos["Usuario"] == str(st.session_state.usuario_actual)]

    col_form, col_reporte = st.columns([1, 2])

    # FORMULARIO DE REGISTRO DE GASTOS
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
                        str(st.session_state.usuario_actual), 
                        fecha, 
                        concepto, 
                        categoria, 
                        monto
                    ]], columns=df_todos.columns)
                    
                    df_actualizado = pd.concat([df_todos, nuevo_gasto], ignore_index=True)
                    guardar_gastos(df_actualizado)
                    st.success("✅ Gasto guardado exitosamente")
                    st.rerun()

    # REPORTE Y HISTORIAL DEL USUARIO
    with col_reporte:
        st.header("📊 Reporte General")
        
        if df_usuario.empty:
            st.info("Aún no has registrado ningún gasto en esta cuenta.")
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