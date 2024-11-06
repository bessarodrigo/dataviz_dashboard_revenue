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
    # Configura a string de conexão ao banco 'telemedicina'
    postgres_str = f'postgresql+pg8000://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    engine = create_engine(postgres_str)

    # Consultar a tabela "recebimentos"
    query = "SELECT * FROM telemedicina.recebimentos" 
    with engine.connect() as connection:
        df = pd.read_sql(query, connection)
    
    return df

# Configurando o título da página e outros elementos
st.set_page_config(
    page_title="Dashboard de Variação Percentual de Recebimento",
    layout="centered",  # para aumentar a área útil dos gráficos - antes era "centered"
    initial_sidebar_state="expanded"  # Sidebar expandida inicialmente com opção de fechamento
)

# Lendo e preparando dados
dados = get_data()
dados['DATA'] = pd.to_datetime(dados['DATA'], errors='coerce')  # Convertendo a coluna 'DATA' para o tipo datetime

# Simplificação no layout - Logo em fundo claro e menor
st.image("CV_FamiliaSaude1.png", width=100)

# Configuração simplificada da sidebar - escondendo seção de cabeçalho e filtrando ano/mês com opções diretas
st.sidebar.title("Filtros")

# Define os valores padrão do filtro de meses com base na data atual do sistema
mes_referencia = datetime.now().month
ano_referencia = datetime.now().year

# Configuração padrão: Mês atual é mês_referencia - 1, mês anterior é mês_referencia - 2
mes_padrao_atual = mes_referencia - 1 if mes_referencia > 1 else 12
ano_padrao_atual = ano_referencia if mes_referencia > 1 else ano_referencia - 1

mes_padrao_anterior = mes_padrao_atual - 1 if mes_padrao_atual > 1 else 12
ano_padrao_anterior = ano_padrao_atual if mes_padrao_atual > 1 else ano_padrao_atual - 1

# Filtro de categoria com "Todos" como opção
lista_categorias = ["Todos"] + sorted(dados['CATEGORIA'].str.title().unique())
filtro_categoria = st.sidebar.selectbox("Categoria:", options=lista_categorias, key="filtro_categoria")

# Configuração dos seletores de ano e mês para o mês atual e anterior
st.sidebar.subheader("Período de Referência")
filtro_ano_atual = st.sidebar.selectbox("Ano:", options=sorted(dados['DATA'].dt.year.unique()), 
                                        index=sorted(dados['DATA'].dt.year.unique()).index(ano_padrao_atual), key="filtro_ano_atual")
filtro_mes_atual = st.sidebar.selectbox("Mês:", options=list(range(1, 13)),
                                        format_func=lambda x: calendar.month_name[x].capitalize(),
                                        index=mes_padrao_atual - 1, key="filtro_mes_atual")

st.sidebar.subheader("Período Anterior")
filtro_ano_anterior = st.sidebar.selectbox("Ano:", options=sorted(dados['DATA'].dt.year.unique()),
                                           index=sorted(dados['DATA'].dt.year.unique()).index(ano_padrao_anterior), key="filtro_ano_anterior")
filtro_mes_anterior = st.sidebar.selectbox("Mês:", options=list(range(1, 13)),
                                           format_func=lambda x: calendar.month_name[x].capitalize(),
                                           index=mes_padrao_anterior - 1, key="filtro_mes_anterior")


# Validação para garantir que o mês anterior não seja mais recente do que o mês atual
data_atual = datetime(filtro_ano_atual, filtro_mes_atual, 1)
data_anterior = datetime(filtro_ano_anterior, filtro_mes_anterior, 1)

if data_anterior >= data_atual:
    st.error("Atenção: o mês anterior selecionado não pode ser mais recente ou igual ao mês de referência. Ajuste o filtro.")
    # Corrige automaticamente para o mês anterior correto
    filtro_mes_anterior = filtro_mes_atual - 1 if filtro_mes_atual > 1 else 12
    filtro_ano_anterior = filtro_ano_atual if filtro_mes_atual > 1 else filtro_ano_atual - 1

# Filtra os dados pela categoria selecionada
if filtro_categoria == "Todos":
    dados_filtrados = dados
else:
    dados_filtrados = dados[dados['CATEGORIA'].str.title() == filtro_categoria]

# Cabeçalho minimalista
with st.container():
    st.title("Dashboard de Variação Percentual")
    st.caption("Análise mensal de recebimento por categoria e produto")
    st.markdown("<hr style='border-color: lightgray;'>", unsafe_allow_html=True)

# Calcular valores totais e variação percentual
recebimento_mes_atual = dados[(dados['DATA'].dt.year == ano_padrao_atual) & (dados['DATA'].dt.month == filtro_mes_atual)]['TOTAL_RECEBIDO'].sum()
recebimento_mes_anterior = dados[(dados['DATA'].dt.year == filtro_ano_anterior) & (dados['DATA'].dt.month == filtro_mes_anterior)]['TOTAL_RECEBIDO'].sum()
variacao_percentual = ((recebimento_mes_atual - recebimento_mes_anterior) / recebimento_mes_anterior * 100) if recebimento_mes_anterior else 0

# Usando locale.format_string para formatar em português
valor_formatado_mes_atual = locale.format_string("R$ %.2f", recebimento_mes_atual, grouping=True)
valor_formatado_mes_anterior = locale.format_string("R$ %.2f", recebimento_mes_anterior, grouping=True)

# Adicionando cartões de visão geral
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label=f"Recebimento em {calendar.month_name[filtro_mes_anterior]}/{filtro_ano_anterior}", value=valor_formatado_mes_anterior)
with col2:
    st.metric(label=f"Recebimento em {calendar.month_name[filtro_mes_atual]}/{filtro_ano_atual}", value=valor_formatado_mes_atual)
with col3:
    st.metric(label="Variação Percentual", value=f"{variacao_percentual:.2f}%")

# Configuração de cores para os gráficos
cores_graficos = plt.get_cmap('Pastel1').colors
ciclo_cores = cycler('color', cores_graficos)
plt.rc('axes', prop_cycle=ciclo_cores)

# Gráfico 1: Variação Percentual por Categoria
st.write('---')
st.markdown("<h2 style='color: gray; font-size: 20px;'>Variação Percentual por Categoria</h2>", unsafe_allow_html=True)

# Filtrando dados e calculando variação por categoria
dados_mes_anterior_categoria = dados_filtrados[(dados['DATA'].dt.year == filtro_ano_anterior) & (dados['DATA'].dt.month == filtro_mes_anterior)]
dados_mes_atual_categoria = dados_filtrados[(dados['DATA'].dt.year == filtro_ano_atual) & (dados['DATA'].dt.month == filtro_mes_atual)]

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

dados_mes_anterior_produto = dados_filtrados[(dados['DATA'].dt.year == filtro_ano_anterior) & (dados['DATA'].dt.month == filtro_mes_anterior)]
dados_mes_atual_produto = dados_filtrados[(dados['DATA'].dt.year == filtro_ano_atual) & (dados['DATA'].dt.month == filtro_mes_atual)]

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

# Exportar gráficos para PDF diretamente ao clicar no botão
def gerar_pdf():
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    
    # Adicionar textos e gráficos no PDF
    c.drawString(100, 800, f"Recebimento mês atual ({filtro_mes_atual}/{filtro_ano_atual}): {valor_formatado_mes_atual}")
    c.drawString(100, 780, f"Recebimento mês anterior ({filtro_mes_anterior}/{filtro_ano_anterior}): {valor_formatado_mes_anterior}")
    c.drawString(100, 760, f"Variação percentual: {variacao_percentual:.2f}%")
    
    # Salvar PDF no buffer
    c.save()
    buffer.seek(0)
    return buffer

# Botão único para gerar e baixar o PDF
buffer = gerar_pdf()
st.download_button(label="Exportar para PDF", data=buffer, file_name="dashboard_variacao.pdf", mime="application/pdf")