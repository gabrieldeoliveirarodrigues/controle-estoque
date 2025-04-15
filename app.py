
import streamlit as st
import pandas as pd
import bcrypt
import sqlite3
import os

# Conexão com banco de dados de usuários
conn = sqlite3.connect("usuarios.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (usuario TEXT, senha TEXT)''')
conn.commit()

# Usuários fixos
usuarios = [("GABRIEL RODRIGUES", bcrypt.hashpw("051020".encode(), bcrypt.gensalt())),
            ("PRISCILLA LYRA", bcrypt.hashpw("051020".encode(), bcrypt.gensalt()))]

for usuario, senha in usuarios:
    cursor.execute("SELECT * FROM usuarios WHERE usuario = ?", (usuario,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (usuario, senha.decode()))
        conn.commit()

# Autenticação
def autenticar(usuario, senha):
    cursor.execute("SELECT senha FROM usuarios WHERE usuario = ?", (usuario,))
    resultado = cursor.fetchone()
    if resultado and bcrypt.checkpw(senha.encode(), resultado[0].encode()):
        return True
    return False

# Login
if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if autenticar(usuario, senha):
            st.session_state.logado = True
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos")
else:
    st.sidebar.title("📦 Menu")
    menu = st.sidebar.selectbox("Menu", ["Controle de Estoque", "Histórico", "Importar Dados", "Sugerir Melhorias"])

    if "dados" not in st.session_state:
        st.session_state.dados = pd.DataFrame(columns=["Item", "Quantidade", "Unidade", "Tipo", "Movimentação"])

    if menu == "Controle de Estoque":
        st.title("📦 Controle de Estoque")
        item = st.text_input("Nome do item")
        quantidade = st.number_input("Quantidade", min_value=0, step=1)
        unidade = st.selectbox("Unidade", ["un", "kg", "g", "l", "ml", "caixa", "pacote"])
        tipo = st.selectbox("Tipo de movimentação", ["Entrada", "Saída"])

        if st.button("Registrar"):
            nova_entrada = pd.DataFrame([[item, quantidade, unidade, tipo, pd.Timestamp.now()]],
                                        columns=["Item", "Quantidade", "Unidade", "Tipo", "Movimentação"])
            st.session_state.dados = pd.concat([st.session_state.dados, nova_entrada], ignore_index=True)
            st.success(f"{tipo} registrada com sucesso!")

        st.subheader("📋 Estoque Atual")
        estoque = st.session_state.dados.copy()
        for i, row in estoque.iterrows():
            if row["Tipo"] == "Saída":
                estoque.at[i, "Quantidade"] *= -1
        resumo = estoque.groupby(["Item", "Unidade"])["Quantidade"].sum().reset_index()
        for i, row in resumo.iterrows():
            if row["Quantidade"] <= 20:
                st.warning(f'⚠️ {row["Item"]} está com baixo estoque: {row["Quantidade"]} {row["Unidade"]}')
        st.dataframe(resumo)

    elif menu == "Histórico":
        st.title("📜 Histórico de Movimentações")
        st.dataframe(st.session_state.dados)

        st.download_button("📥 Exportar para Excel", data=st.session_state.dados.to_csv(index=False).encode("utf-8"),
                           file_name="historico.csv", mime="text/csv")

    elif menu == "Importar Dados":
        st.title("📁 Importar Base de Dados")
        arquivo = st.file_uploader("Escolha um arquivo Excel", type=["xlsx"])
        if arquivo:
            df = pd.read_excel(arquivo)
            df["Movimentação"] = "Importado"
            st.session_state.dados = pd.concat([st.session_state.dados, df], ignore_index=True)
            st.success("Base importada com sucesso!")
            st.dataframe(df)

    elif menu == "Sugerir Melhorias":
        st.title("💡 Sugerir Melhorias")
        sugestao = st.text_area("Descreva sua sugestão:")
        if st.button("Enviar Sugestão"):
            with open("melhorias.txt", "a", encoding="utf-8") as f:
                f.write(sugestao + "\n")
            st.success("Sugestão enviada com sucesso!")
