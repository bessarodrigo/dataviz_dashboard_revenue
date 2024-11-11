# Dashboard de Variação de Faturamento Mensal

## Descrição do Projeto
<p align="left">O projeto consiste em um painel de calcula a variação mensal de faturamento de uma empresa de Telemedicina (dados fictícios). O painel consiste em uma seção de dados gerais do faturamento mensal e dois gráficos: <strong>variação por categoria</strong> e <strong>variação por produtos</strong>. Na parte de filtros, é possível filtrar o ano e mês de análise e o painel calculará a variação do mês selecionado imediatamente com o mês anterior.</p>

<h2>Tabela de Conteúdos</h2>
<ul>
  <li><a href="#explicacao-das-pastas">Explicação das Pastas</a></li>
  <li><a href="#status-do-projeto">Status do Projeto</a></li>
  <li><a href="#descricao-dos-scripts">Descrição dos Scripts</a></li>
  <li><a href="#features">Features</a></li>
  <li><a href="#deploy">Deploy</a></li>
  <li><a href="#tecnologias-utilizadas">Tecnologias Utilizadas</a></li>
  <li><a href="#autor">Autor</a></li>
</ul>

## Explicação das Pastas

- **`.devcontainer/`**: Arquivo de configuração para o ambiente de desenvolvimento no Docker
- **`.streamlit/`**: Contém o arquivo `config.toml` para definir o tema e as configurações do painel no Streamlit
- **`images/`**: Contém imagens que ilustram o projeto ou que são usadas no dashboard.
- **`notebooks/`**: Notebooks Jupyter para análise exploratória e scripts de conexão e manipulação do banco de dados
- **`src/`**: Código principal do projeto
- **`.gitignore`**: Define arquivos e pastas a serem ignorados pelo Git, como o `.env` (contendo variáveis sensíveis) e arquivos temporários
- **`requirements.txt`**: Especifica as bibliotecas Python necessárias para rodar o projeto

## Status do Projeto
<h4 align="left"> 🚧 Em construção... 🚧 </h4> <p>O projeto ainda está em desenvolvimento. Algumas funcionalidades estão implementadas, enquanto outras estão em progresso ou planejadas para futuras versões.</p>

<h2 id="descricao-dos-scripts">Descrição dos Scripts</h2>
<ul>
  <li>
    <strong>eda_matplotlib_pandas.ipynb</strong> - Análise Exploratória dos Dados (EDA) utilizando as bibliotecas <code>matplotlib</code> e <code>pandas</code>. A ideia geral deste notebook foi pensar em um formato interessante para os gráficos do dashboard.
  </li>
  <li>
    <strong>telemedicina_bd_conexao.ipynb</strong> - Notebook dedicado à conexão e manipulação do banco de dados.
  </li>
  <li>
    <strong>app.py</strong> - Script para construir o dashboard com o <code>streamlit</code>.
  </li>
</ul>

## Features
<ul> <li>✅ Painel de Faturamento Mensal com visualização de dados gerais</li> <li>✅ Gráfico de Variação de Faturamento por Categoria</li> <li>✅ Gráfico de Variação de Faturamento por Produto</li> <li>✅ Filtros avançados para comparação de múltiplos períodos</li> <li>✅ Exportação de relatórios em PDF</li> </ul>

## Deploy

<p><i>Em breve</i>: O deploy do projeto está em fase de planejamento. Detalhes de acesso e link para o painel online serão disponibilizados assim que concluídos.</p>

## Tecnologias Utilizadas

<ul> <li><b>Python</b>: para manipulação de dados e geração dos cálculos de variação mensal</li> <li><b>Streamlit</b>: para criação do painel interativo e visualização dos gráficos</li> <li><b>Pandas</b>: para análise e transformação de dados.</li> <li><b>Matplotlib</b>: para geração de gráficos de variação de faturamento.</li> <li><b>SQLAlchemy</b>: para conexão com o banco de dados onde os dados de faturamento estão armazenados.</li> </ul>

## Autor

<p>Desenvolvido por <b>Rodrigo Bessa</b>. Entre em contato:</p> <ul> <li><a href="https://linkedin.com/in/rodrigo-bessa">LinkedIn</a></li> <li><a href="mailto:reisrodri@gmail.com">Email</a></li> </ul>

## Restrições de Uso e Propriedade Intelectual

Este projeto e seu conteúdo estão protegidos pela Lei de Direitos Autorais (Lei nº 9.610/1998) e outras leis de propriedade intelectual aplicáveis no Brasil. Todo o código, documentação, e dados disponibilizados neste repositório são de propriedade exclusiva do autor, exceto quando especificado de outra forma.

### Termos de Uso
- Uso Comercial: é proibido o uso do conteúdo deste repositório para fins comerciais sem autorização expressa e por escrito do autor
- Redistribuição: a redistribuição do código ou de qualquer outro material aqui presente deve conter os devidos créditos ao autor e ser acompanhada desta mesma nota de direitos autorais e termos de uso
  
### Licença
O uso deste repositório está permitido exclusivamente para fins educacionais e de estudo. Para outros tipos de licença (como MIT ou GPL) ou para uso comercial, consulte o autor para autorização formal.
