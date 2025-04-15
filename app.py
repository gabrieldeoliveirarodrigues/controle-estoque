import streamlit as st
import pandas as pd
import datetime
import sqlite3
import bcrypt

st.set_page_config(page_title="Sistema de Controle de Estoque", layout="wide")

# Banco de dados de usuários
def conectar():
    return sqlite3.connect("usuarios.db")

def verificar_usuario(usuario, senha):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nome, senha_hash, permissao FROM usuarios WHERE usuario = ?", (usuario,))
    row = cursor.fetchone()
    conn.close()
    if row and bcrypt.checkpw(senha.encode(), row[1]):
        return {"nome": row[0], "usuario": usuario, "permissao": row[2]}
    return None

def cadastrar_usuario(nome, usuario, senha, permissao):
    conn = conectar()
    cursor = conn.cursor()
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())
    try:
        cursor.execute("INSERT INTO usuarios (nome, usuario, senha_hash, permissao) VALUES (?, ?, ?, ?)",
                       (nome, usuario, senha_hash, permissao))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# Autenticação
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if not st.session_state.usuario_logado:
    st.title("🔐 Login")
    with st.form("login_form"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")
        if submitted:
            user = verificar_usuario(usuario, senha)
            if user:
                st.session_state.usuario_logado = user
                st.success("Login realizado com sucesso. Recarregando...")
                st.stop()
            else:
                st.error("Usuário ou senha inválidos.")
    st.stop()

# Sistema principal
usuario_atual = st.session_state.usuario_logado
st.sidebar.success(f"Logado como: {usuario_atual['nome']} ({usuario_atual['permissao']})")
if st.sidebar.button("Sair"):
    st.session_state.usuario_logado = None
    st.stop()

st.title("📦 Sistema de Controle de Estoque")

# Sessões de dados
if "estoque" not in st.session_state:
    st.session_state.estoque = pd.DataFrame(columns=[
        "Produto Técnico", "Tipo", "Medida", "Marca/Grupo", "Quantidade", "Unidade"])

if "historico" not in st.session_state:
    st.session_state.historico = []

# Cadastro de novos usuários (somente admin)
if usuario_atual["permissao"] == "admin":
    st.sidebar.markdown("---")
    st.sidebar.subheader("👥 Cadastrar Novo Usuário")
    with st.sidebar.form("form_cadastro"):
        nome_novo = st.text_input("Nome completo")
        usuario_novo = st.text_input("Novo usuário")
        senha_novo = st.text_input("Senha", type="password")
        permissao_novo = st.selectbox("Permissão", ["usuario", "admin"])
        cadastrar = st.form_submit_button("Cadastrar")
        if cadastrar:
            sucesso = cadastrar_usuario(nome_novo, usuario_novo, senha_novo, permissao_novo)
            if sucesso:
                st.sidebar.success("Usuário cadastrado com sucesso.")
            else:
                st.sidebar.error("Usuário já existe.")

# Importar planilha
st.sidebar.markdown("---")
st.sidebar.header("📁 Importar Base de Dados")
arquivo = st.sidebar.file_uploader("Selecione um arquivo Excel (.xlsx)", type=["xlsx"])
if arquivo:
    df_importado = pd.read_excel(arquivo)

    import re
    def processar_estrutura(row):
        descricao = row['ESTRUTURAS']
        estoque_raw = row['ESTOQUE']
        match_qtd = re.match(r"(\d+)\s+(\w+)", str(estoque_raw))
        qtd = int(match_qtd.group(1)) if match_qtd else None
        unid = match_qtd.group(2) if match_qtd else None
        produto = descricao.upper().strip()
        tipo = medida = marca = "-"
        if "TRILHO" in produto:
            tipo = "Trilho"
            medida_search = re.search(r"(\d+[,.]?\d*)", produto)
            if medida_search:
                medida = medida_search.group(1).replace(",", ".") + " m"
        elif "PARAFUSO" in produto:
            tipo = "Parafuso Estrutural"
            medida_search = re.search(r"(M\d+\s?X\s?\d+)", produto.replace(" ", "").upper())
            if medida_search:
                medida = medida_search.group(1).replace("X", " x ")
        elif "GANCHO" in produto:
            tipo = "Gancho"
        elif "FIM DE CURSO" in produto:
            tipo = "Fim de Curso"
        elif "INTERMEDIARIO" in produto:
            tipo = "Intermediário"
        elif "JUNÇÃO" in produto:
            tipo = "JUNÇÃO"
        elif "TELHA" in produto:
            tipo = "L de Fixação"
        else:
            tipo = "Componente"
        if "2P" in produto:
            marca = "2P GROUP"
        elif "IZI" in produto:
            marca = "IZI"
        elif "SOLAR GROUP" in produto or "THUNDER" in produto:
            marca = "SOLAR GROUP"
        elif "MADEIRA" in produto:
            marca = "2P MADEIRA"
        elif "METAL" in produto:
            marca = "2P METAL"
        return pd.Series({
            "Produto Técnico": produto.title(),
            "Tipo": tipo,
            "Medida": medida,
            "Marca/Grupo": marca,
            "Quantidade": qtd,
            "Unidade": unid
        })

    st.session_state.estoque = df_importado.apply(processar_estrutura, axis=1)
    st.success("Dados importados com sucesso!")

# Mostrar estoque atual
st.subheader("📊 Estoque Atual")
if not st.session_state.estoque.empty:
    st.dataframe(st.session_state.estoque, use_container_width=True)
else:
    st.info("Nenhum dado de estoque disponível. Importe uma planilha para começar.")

# Registrar movimentação
st.markdown("---")
st.subheader("➕➖ Registrar Movimentação")

if st.session_state.estoque.empty:
    st.warning("Importe dados primeiro para registrar movimentações.")
else:
    produto = st.selectbox("Produto", st.session_state.estoque["Produto Técnico"])
    tipo = st.radio("Tipo de Movimentação", ["Entrada", "Saída"])
    quantidade = st.number_input("Quantidade", min_value=1, step=1)
    data_mov = st.date_input("Data", value=datetime.date.today())
    obs = st.text_input("Observação (opcional)")

    if st.button("Registrar"):
        idx = st.session_state.estoque[st.session_state.estoque["Produto Técnico"] == produto].index[0]
        if tipo == "Entrada":
            st.session_state.estoque.at[idx, "Quantidade"] += quantidade
        else:
            if st.session_state.estoque.at[idx, "Quantidade"] >= quantidade:
                st.session_state.estoque.at[idx, "Quantidade"] -= quantidade
            else:
                st.error("Quantidade insuficiente em estoque.")
                st.stop()

        st.session_state.historico.append({
            "Data": data_mov,
            "Produto": produto,
            "Tipo": tipo,
            "Quantidade": quantidade,
            "Usuário": usuario_atual['nome'],
            "Observação": obs
        })
        st.success("Movimentação registrada com sucesso!")

# Histórico
st.markdown("---")
st.subheader("📜 Histórico de Movimentações")

if st.session_state.historico:
    hist_df = pd.DataFrame(st.session_state.historico)
    st.dataframe(hist_df.sort_values(by="Data", ascending=False), use_container_width=True)
else:
    st.info("Nenhuma movimentação registrada ainda.")


# ============================
# ABA: Sugerir Melhorias
# ============================
elif menu == "Sugerir Melhorias":
    st.subheader("🧠 Sugerir Melhorias ou Ensinar o Sistema")
    sugestao = st.text_area("Digite aqui sua sugestão ou melhoria para o sistema:")

    if st.button("Enviar Sugestão"):
        if sugestao.strip() != "":
            with open("sugestoes.txt", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {usuario}: {sugestao}\n")
            st.success("Sugestão registrada com sucesso! Obrigado por contribuir.")
        else:
            st.warning("Por favor, digite uma sugestão antes de enviar.")

# ============================
# ALERTA DE BAIXO ESTOQUE (na aba principal)
# ============================
if menu == "Controle de Estoque":
    st.subheader("📦 Estoque Atual")
    df_display = df.copy()

    # Verifica e sinaliza baixo estoque (limite <= 5)
    df_display["Alerta"] = df_display["Quantidade"].apply(lambda x: "⚠️" if x <= 5 else "")
    df_display = df_display[["Produto", "Quantidade", "Unidade", "Alerta"]]
    st.dataframe(df_display)

    # Destacar alertas
    baixo_estoque = df_display[df_display["Alerta"] == "⚠️"]
    if not baixo_estoque.empty:
        st.error("🚨 ATENÇÃO: Há itens com baixo estoque!")
        st.dataframe(baixo_estoque)
