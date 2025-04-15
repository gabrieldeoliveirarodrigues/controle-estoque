
import streamlit as st
import pandas as pd
import sqlite3
import datetime

st.set_page_config(layout="wide")
st.title("📦 Controle de Estoque")

# Conexão com o banco de dados
def conectar():
    return sqlite3.connect("usuarios.db", check_same_thread=False)

# Inicializar banco
def inicializar_banco():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS estoque (nome TEXT, unidade TEXT, saldo INTEGER)")
    conn.commit()
    conn.close()

inicializar_banco()

# Upload do Excel
uploaded_file = st.file_uploader("Importar arquivo de estoque (Excel)", type=["xlsx"])

if uploaded_file is not None:
    try:
        df_importado = pd.read_excel(uploaded_file)
        df_importado.columns = df_importado.columns.str.strip().str.lower()

        colunas_esperadas = {
            "nome": ["nome", "produto", "item"],
            "unidade": ["unidade", "und", "uni"],
            "saldo": ["saldo", "quantidade", "qtd"]
        }

        col_map = {}
        for padrao, alternativas in colunas_esperadas.items():
            for alt in alternativas:
                if alt in df_importado.columns:
                    col_map[padrao] = alt
                    break

        if set(col_map.keys()) != set(colunas_esperadas.keys()):
            st.error("Erro: O arquivo Excel precisa conter colunas de nome, unidade e saldo.")
        else:
            df_importado = df_importado.rename(columns={v: k for k, v in col_map.items()})
            df_importado["saldo"] = pd.to_numeric(df_importado["saldo"], errors="coerce").fillna(0).astype(int)

            conn = conectar()
            df_importado.to_sql("estoque", conn, if_exists="replace", index=False)
            st.success("Arquivo importado com sucesso e estoque substituído.")
    except Exception as e:
        st.error(f"Erro ao importar o arquivo: {e}")

# Mostrar estoque atual
st.subheader("📋 Estoque Atual")
conn = conectar()
df_estoque = pd.read_sql_query("SELECT * FROM estoque", conn)
conn.close()
st.dataframe(df_estoque)
