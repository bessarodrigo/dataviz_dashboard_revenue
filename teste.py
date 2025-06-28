import pandas as pd
from sqlalchemy import create_engine
import streamlit as st
import matplotlib.pyplot as plt
from cycler import cycler
import locale
import os
from dotenv import load_dotenv
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from babel.numbers import format_currency
import calendar

# Carregar variáveis do arquivo .env
load_dotenv()

# Credenciais do banco de dados do .env
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

# Definir localização brasileira para formatação de valores
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    print("A localidade pt_BR.UTF-8 não está disponível no sistema.")

# Função para formatar valores monetários brasileiros
def format_currency_br(value):
    return format_currency(value, 'BRL', locale='pt_BR')

# Defina a função de conexão e obtenção de dados
@st.cache_data
def get_data():
    postgres_str = f'postgresql+pg8000://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    engine = create_engine(postgres_str)
    query = "SELECT * FROM telemedicina.recebimentos"
    with engine.connect() as connection:
        df = pd.read_sql(query, connection)
    return df

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Variação Percentual de Recebimento",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Obter dados
dados = get_data()
dados['DATA'] = pd.to_datetime(dados['DATA'], errors='coerce')
dados = dados.dropna(subset=['DATA'])

# Logo
st.image("../images/CV_FamiliaSaude1.png", width=100)

# Sidebar - filtros
st.sidebar.title("Filtros")

# Data atual para referência
mes_referencia = datetime.now().month
ano_referencia = datetime.now().year

anos_disponiveis = sorted(dados['DATA'].dt.year.dropna().unique())

ano_padrao_atual = ano_referencia if ano_referencia in anos_disponiveis else anos_disponiveis[-1]
ano_padrao_anterior = ano_padrao_atual - 1 if (ano_padrao_atual - 1) in anos_disponiveis else anos_disponiveis[0]

mes_padrao_atual = mes_referencia - 1 if mes_referencia > 1 else 12
mes_padrao_anterior = mes_padrao_atual - 1 if mes_padrao_atual > 1 else 12

# Filtro categoria
lista_categorias = ["Todos"] + sorted(dados['CATEGORIA'].str.title().unique())
filtro_categoria = st.sidebar.selectbox("Categoria:", options=lista_categorias, key="filtro_categoria")

# Seletores de ano e mês
st.sidebar.subheader("Período de Referência")
index_ano_atual = anos_disponiveis.index(ano_padrao_atual)
index_ano_anterior = anos_disponiveis.index(ano_padrao_anterior)

filtro_ano_atual = st.sidebar.selectbox("Ano (Atual):", options=anos_disponiveis, index=index_ano_atual, key="filtro_ano_atual")
filtro_mes_atual = st.sidebar.selectbox(
    "Mês (Atual):",
    options=list(range(1, 13)),
    format_func=lambda x: calendar.month_name[x].capitalize(),
    index=mes_padrao_atual - 1,
    key="filtro_mes_atual"
)

st.sidebar.subheader("Período Anterior")
filtro_ano_anterior = st.sidebar.selectbox("Ano (Anterior):", options=anos_disponiveis, index=index_ano_anterior, key="filtro_ano_anterior")
filtro_mes_anterior = st.sidebar.selectbox(
    "Mês (Anterior):",
    options=list(range(1, 13)),
    format_func=lambda x: calendar.month_name[x].capitalize(),
    index=mes_padrao_anterior - 1,
    key="filtro_mes_anterior"
)

# Validação de datas para garantir mês anterior < mês atual
data_atual = datetime(filtro_ano_atual, filtro_mes_atual, 1)
data_anterior = datetime(filtro_ano_anterior, filtro_mes_anterior, 1)

if data_anterior >= data_atual:
    st.error("Atenção: o mês anterior não pode ser maior ou igual ao mês atual. Ajuste os filtros.")
    st.stop()

# Filtrar por categoria
if filtro_categoria == "Todos":
    dados_filtrados = dados
else:
    dados_filtrados = dados[dados['CATEGORIA'].str.title() == filtro_categoria]

# Cabeçalho
st.title("Dashboard de Variação Percentual")
st.caption("Análise mensal de recebimento por categoria e produto")
st.markdown("<hr style='border-color: lightgray;'>", unsafe_allow_html=True)

# Cálculo totais e variação percentual usando dados_filtrados
recebimento_mes_atual = dados_filtrados[
    (dados_filtrados['DATA'].dt.year == filtro_ano_atual) & (dados_filtrados['DATA'].dt.month == filtro_mes_atual)
]['TOTAL_RECEBIDO'].sum()

recebimento_mes_anterior = dados_filtrados[
    (dados_filtrados['DATA'].dt.year == filtro_ano_anterior) & (dados_filtrados['DATA'].dt.month == filtro_mes_anterior)
]['TOTAL_RECEBIDO'].sum()

variacao_percentual = ((recebimento_mes_atual - recebimento_mes_anterior) / recebimento_mes_anterior * 100) if recebimento_mes_anterior else 0

valor_formatado_mes_atual = locale.format_string("R$ %.2f", recebimento_mes_atual, grouping=True)
valor_formatado_mes_anterior = locale.format_string("R$ %.2f", recebimento_mes_anterior, grouping=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label=f"Recebimento em {calendar.month_name[filtro_mes_anterior]}/{filtro_ano_anterior}", value=valor_formatado_mes_anterior)
with col2:
    st.metric(label=f"Recebimento em {calendar.month_name[filtro_mes_atual]}/{filtro_ano_atual}", value=valor_formatado_mes_atual)
with col3:
    st.metric(label="Variação Percentual", value=f"{variacao_percentual:.2f}%")

# Configuração das cores
cores_graficos = plt.get_cmap('Pastel1').colors
ciclo_cores = cycler('color', cores_graficos)
plt.rc('axes', prop_cycle=ciclo_cores)

# Gráfico 1: Variação Percentual por Categoria
st.write('---')
st.markdown("<h2 style='color: gray; font-size: 20px;'>Variação Percentual por Categoria</h2>", unsafe_allow_html=True)

dados_mes_anterior_categoria = dados_filtrados[
    (dados_filtrados['DATA'].dt.year == filtro_ano_anterior) & (dados_filtrados['DATA'].dt.month == filtro_mes_anterior)
]

dados_mes_atual_categoria = dados_filtrados[
    (dados_filtrados['DATA'].dt.year == filtro_ano_atual) & (dados_filtrados['DATA'].dt.month == filtro_mes_atual)
]

recebimento_categoria_mes_anterior = dados_mes_anterior_categoria.groupby('CATEGORIA')['TOTAL_RECEBIDO'].sum()
recebimento_categoria_mes_atual = dados_mes_atual_categoria.groupby('CATEGORIA')['TOTAL_RECEBIDO'].sum()

porcentagem_categoria = (recebimento_categoria_mes_atual - recebimento_categoria_mes_anterior) / recebimento_categoria_mes_anterior * 100
dados_porcentagem_categoria = porcentagem_categoria.reset_index()
dados_porcentagem_categoria.columns = ['CATEGORIA', 'VARIACAO_PERCENTUAL']
dados_porcentagem_categoria['VARIACAO_PERCENTUAL'] = pd.to_numeric(dados_porcentagem_categoria['VARIACAO_PERCENTUAL'], errors='coerce')

fig_categoria, ax_categoria = plt.subplots(figsize=(12, 7))
barras_categoria = ax_categoria.bar(dados_porcentagem_categoria['CATEGORIA'], dados_porcentagem_categoria['VARIACAO_PERCENTUAL'])

ax_categoria.bar_label(barras_categoria, labels=[f"{var:.2f}%" for var in dados_porcentagem_categoria['VARIACAO_PERCENTUAL']], padding=3)
for i, var in enumerate(dados_porcentagem_categoria['VARIACAO_PERCENTUAL']):
    barras_categoria[i].set_color(cores_graficos[0] if var < 0 else cores_graficos[2])

plt.box(False)
ax_categoria.tick_params(axis='x', rotation=45, labelsize=10, pad=20, length=0)
ax_categoria.set_yticks([])

st.pyplot(fig_categoria)

# Gráfico 2: Variação Percentual por Produto
st.write('---')
st.markdown("<h2 style='color: gray; font-size: 20px;'>Variação Percentual por Produto</h2>", unsafe_allow_html=True)

dados_mes_anterior_produto = dados_filtrados[
    (dados_filtrados['DATA'].dt.year == filtro_ano_anterior) & (dados_filtrados['DATA'].dt.month == filtro_mes_anterior)
]

dados_mes_atual_produto = dados_filtrados[
    (dados_filtrados['DATA'].dt.year == filtro_ano_atual) & (dados_filtrados['DATA'].dt.month == filtro_mes_atual)
]

recebimento_produto_mes_anterior = dados_mes_anterior_produto.groupby('ITEM_PCG')['TOTAL_RECEBIDO'].sum()
recebimento_produto_mes_atual = dados_mes_atual_produto.groupby('ITEM_PCG')['TOTAL_RECEBIDO'].sum()

porcentagem_produto = (recebimento_produto_mes_atual - recebimento_produto_mes_anterior) / recebimento_produto_mes_anterior * 100
dados_porcentagem_produto = porcentagem_produto.reset_index()
dados_porcentagem_produto.columns = ['ITEM_PCG', 'VARIACAO_PERCENTUAL']
dados_porcentagem_produto['VARIACAO_PERCENTUAL'] = pd.to_numeric(dados_porcentagem_produto['VARIACAO_PERCENTUAL'], errors='coerce')

fig_produto, ax_produto = plt.subplots(figsize=(12, 7))
barras_produto = ax_produto.barh(dados_porcentagem_produto['ITEM_PCG'], dados_porcentagem_produto['VARIACAO_PERCENTUAL'])

ax_produto.bar_label(barras_produto, labels=[f"{var:.2f}%" for var in dados_porcentagem_produto['VARIACAO_PERCENTUAL']], padding=3)
for i, var in enumerate(dados_porcentagem_produto['VARIACAO_PERCENTUAL']):
    barras_produto[i].set_color(cores_graficos[0] if var < 0 else cores_graficos[2])

plt.box(False)
ax_produto.tick_params(axis='y', labelsize=10, pad=30, length=0)
ax_produto.set_xticks([])

st.pyplot(fig_produto)

# Função para gerar PDF (simplificado)
def gerar_pdf():
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.drawString(100, 800, f"Recebimento mês atual ({filtro_mes_atual}/{filtro_ano_atual}): {valor_formatado_mes_atual}")
    c.drawString(100, 780, f"Recebimento mês anterior ({filtro_mes_anterior}/{filtro_ano_anterior}): {valor_formatado_mes_anterior}")
    c.drawString(100, 760, f"Variação percentual: {variacao_percentual:.2f}%")
    c.save()
    buffer.seek(0)
    return buffer

buffer = gerar_pdf()
st.download_button(label="Exportar para PDF", data=buffer, file_name="dashboard_variacao.pdf", mime="application/pdf")
