# 📦 Sistema de Controle de Estoque Web

Este é um sistema web simples e robusto de controle de estoque desenvolvido em Python com Streamlit.

## Funcionalidades

- Importação de planilha Excel (`.xlsx`) com os campos `ESTRUTURAS` e `ESTOQUE`
- Transformação automática dos dados para formato técnico
- Registro de movimentações (entradas e saídas)
- Histórico detalhado de alterações
- Visualização do estoque em tempo real

## Como executar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Como hospedar gratuitamente

Você pode usar o [Streamlit Cloud](https://streamlit.io/cloud):

1. Suba os arquivos (`app.py`, `requirements.txt`, etc.) em um repositório GitHub
2. Vá até [streamlit.io/cloud](https://streamlit.io/cloud)
3. Conecte sua conta GitHub e selecione o repositório
4. Clique em "Deploy"

Pronto! Seu app estará online.

---
Desenvolvido com ❤️ por ChatGPT para automação de processos empresariais.