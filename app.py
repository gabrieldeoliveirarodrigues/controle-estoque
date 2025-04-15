
import os
import sqlite3
import bcrypt
import streamlit as st

def inicializar_banco():
    conn = sqlite3.connect("usuarios.db", check_same_thread=False)
    cursor = conn.cursor()

    # Verifica se a tabela já existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
    if cursor.fetchone():
        # Verifica se a coluna 'senha' existe
        cursor.execute("PRAGMA table_info(usuarios)")
        colunas = [info[1] for info in cursor.fetchall()]
        if "senha" not in colunas:
            cursor.execute("DROP TABLE usuarios")

    # Cria a tabela correta se necessário
    cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (usuario TEXT PRIMARY KEY, senha TEXT)")
    usuarios_iniciais = [
        ("Gabriel Rodrigues", bcrypt.hashpw("051020".encode(), bcrypt.gensalt()).decode()),
        ("Priscilla Lyra", bcrypt.hashpw("051020".encode(), bcrypt.gensalt()).decode())
    ]
    for usuario, senha in usuarios_iniciais:
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ?", (usuario,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (usuario, senha))
    conn.commit()
    conn.close()

def autenticar(usuario, senha):
    conn = sqlite3.connect("usuarios.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT senha FROM usuarios WHERE usuario = ?", (usuario,))
    resultado = cursor.fetchone()
    conn.close()
    if resultado:
        return bcrypt.checkpw(senha.encode(), resultado[0].encode())
    return False

inicializar_banco()
st.set_page_config(page_title="Controle de Estoque", layout="wide")
st.title("🔐 Login - Controle de Estoque")

usuario = st.text_input("Usuário")
senha = st.text_input("Senha", type="password")

if st.button("Entrar"):
    if autenticar(usuario, senha):
        st.success(f"Bem-vindo(a), {usuario}!")
        st.stop()
    else:
        st.error("Usuário ou senha incorretos.")
