
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Controle de Estoque", layout="wide")
st.title("📦 Sistema de Controle de Estoque")

# Sessão de dados
if "dados" not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=["nome", "unidade", "saldo"])

menu = st.sidebar.selectbox("Menu", ["Estoque Atual", "Entrada", "Saída", "Importar Excel"])

def salvar_csv():
    st.session_state.dados.to_csv("estoque.csv", index=False)

if menu == "Estoque Atual":
    st.subheader("📋 Estoque Atual")
    df = st.session_state.dados.copy()
    df["alerta"] = df["saldo"].apply(lambda x: "⚠️" if x < 0 else "")
    st.dataframe(df, use_container_width=True)

elif menu == "Entrada":
    st.subheader("📥 Entrada de Equipamentos")
    nome = st.text_input("Nome do Produto")
    unidade = st.text_input("Unidade", value="un")
    quantidade = st.number_input("Quantidade", step=1)
    if st.button("Registrar Entrada"):
        if nome:
            if nome in st.session_state.dados["nome"].values:
                st.session_state.dados.loc[st.session_state.dados["nome"] == nome, "saldo"] += quantidade
            else:
                st.session_state.dados.loc[len(st.session_state.dados)] = [nome, unidade, quantidade]
            salvar_csv()
            st.success("Entrada registrada.")

elif menu == "Saída":
    st.subheader("📤 Saída de Equipamentos")
    nomes_produtos = st.session_state.dados["nome"].tolist()
    if nomes_produtos:
        nome = st.selectbox("Selecione o Produto", nomes_produtos)
        quantidade = st.number_input("Quantidade", step=1)
        if st.button("Registrar Saída"):
            st.session_state.dados.loc[st.session_state.dados["nome"] == nome, "saldo"] -= quantidade
            salvar_csv()
            st.success("Saída registrada.")
    else:
        st.info("Nenhum produto no estoque.")

elif menu == "Importar Excel":
    st.subheader("📁 Importar Arquivo de Estoque")
    uploaded_file = st.file_uploader("Escolha o arquivo Excel", type=["xlsx"])
    if uploaded_file is not None:
        df_importado = pd.read_excel(uploaded_file)
        df_importado["saldo"] = df_importado["saldo"].astype(int)
        st.session_state.dados = df_importado
        salvar_csv()
        st.success("Importado com sucesso!")
