import streamlit as st  # Biblioteca para criar interfaces interativas
import pandas as pd  # Para manipular os dados em tabelas
import plotly.express as px  # Para criar gráficos interativos
import requests  # Para acessar a API de clima
from datetime import datetime  # Para trabalhar com datas
import os  # Para verificar se a planilha existe

# Configurações iniciais do app
st.set_page_config(page_title="Gerenciamento de Resíduos", layout="wide")  # Sem configuração dinâmica do menu lateral

# Função para aplicar o CSS que deixa a sidebar fixa
def fix_sidebar():
    st.markdown(
        """
        <style>
        /* Fixa a sidebar e a deixa sempre visível */
        .css-1d391kg { 
            position: fixed;
            top: 0;
            left: 0;
            bottom: 0;
            width: 300px;
            z-index: 100;
        }
        /* Cria um espaçamento para não sobrepor conteúdo principal */
        .css-18e3th9 {
            margin-left: 300px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

fix_sidebar()  # Aplica o CSS para fixar a sidebar

PLANILHA = "residuos.xlsx"  # Nome do arquivo onde os dados serão salvos

# Funções auxiliares

def carregar_dados():
    """Verifica se o arquivo existe e carrega os dados. Se o arquivo não existir, cria uma tabela vazia."""
    if os.path.exists(PLANILHA):
        return pd.read_excel(PLANILHA)  # Lê os dados do Excel
    else:
        return pd.DataFrame(columns=["Tipo", "Volume (kg)", "Local", "Data", "Nível de Perigo", "Responsável", "Status", "Data de Coleta", "Tipo de Resíduo"])  # Estrutura padrão

def salvar_dados(df):
    """Salva os dados na planilha Excel."""
    df.to_excel(PLANILHA, index=False)  # Salva o DataFrame no arquivo

def consultar_clima(local):
    """Usa a API WeatherAPI para buscar informações do clima com base no local informado."""
    try:
        api_key = "d8777af35566497aaaa23344240312"  # Minha chave de API
        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={local}&lang=pt"  # URL para buscar o clima
        response = requests.get(url).json()  # Faz a requisição para a API e transforma o resultado em JSON
        if "current" in response:  # Verifica se a resposta contém dados
            temperatura = response['current']['temp_c']
            condicao = response['current']['condition']['text']
            umidade = response['current']['humidity']
            vento = response['current']['wind_kph']
            
            # Lógica para alerta de temperatura
            alerta_temperatura = ""
            if temperatura > 30:
                alerta_temperatura = "⚠️ Temperatura muito alta!"
            elif temperatura < 10:
                alerta_temperatura = "⚠️ Temperatura muito baixa!"
            
            return {
                "Temperatura": f"{temperatura} °C",
                "Condição": condicao,
                "Umidade": f"{umidade}%",
                "Velocidade do Vento": f"{vento} km/h",
                "Alerta Temperatura": alerta_temperatura
            }
        else:
            return {"Erro": response.get("error", {}).get("message", "Erro desconhecido")}  # Retorna o erro da API
    except Exception as e:
        return {"Erro": str(e)}  # Caso aconteça algum erro inesperado

# Carrega os dados da planilha
df = carregar_dados()

# Sidebar para o menu de navegação
st.sidebar.title("📊 Gerenciamento de Resíduos")  # Título do menu
menu = st.sidebar.radio("Navegação", ["Cadastro", "Dashboard", "Clima e Alertas"])  # Opções de navegação

# Página de Cadastro
if menu == "Cadastro":
    st.title("📋 Cadastro de Resíduos")  # Cabeçalho da página
    with st.form("cadastro_form"):
        tipo = st.selectbox("Tipo de Resíduo", ["Químico", "Biológico", "Outros"])  # Escolhe o tipo
        volume = st.number_input("Volume (kg)", min_value=0.1, step=0.1)  # Insere o volume
        local = st.text_input("Local")  # Informa o local
        data = st.date_input("Data", datetime.now())  # Insere a data
        nivel_perigo = st.selectbox("Nível de Perigo", ["Baixo", "Médio", "Alto"])  # Define o nível de perigo
        responsavel = st.text_input("Responsável")  # Nome do responsável
        status = st.selectbox("Status", ["Coletado", "Aguardando", "Em Andamento"])  # Status do resíduo
        data_coleta = st.date_input("Data de Coleta")  # Data de coleta
        tipo_residuo = st.selectbox("Tipo de Resíduo", ["Perigoso", "Não Perigoso"])  # Tipo de resíduo
        submit = st.form_submit_button("Cadastrar")  # Botão para salvar
        if submit:
            # Adiciona os dados ao DataFrame
            novo_residuo = {"Tipo": tipo, "Volume (kg)": volume, "Local": local, "Data": data, 
                            "Nível de Perigo": nivel_perigo, "Responsável": responsavel, 
                            "Status": status, "Data de Coleta": data_coleta, "Tipo de Resíduo": tipo_residuo}
            # Usando pd.concat em vez de append
            df = pd.concat([df, pd.DataFrame([novo_residuo])], ignore_index=True)  # Adiciona os novos dados
            salvar_dados(df)  # Salva na planilha
            st.success("✅ Resíduo cadastrado com sucesso!")  # Mensagem de confirmação

# Página de Dashboard
elif menu == "Dashboard":
    st.title("📊 Painel de Gerenciamento de Resíduos")  # Título da página
    
    if df.empty:  # Verifica se existem dados
        st.warning("⚠️ Nenhum dado encontrado. Cadastre resíduos na aba 'Cadastro'.")  # Mensagem se não houver dados
    else:
        # Gráficos principais
        col1, col2 = st.columns(2)  # Divide a página em duas colunas
        
        with col1:
            fig1 = px.bar(df, x="Local", y="Volume (kg)", color="Tipo", title="Volume de Resíduos por Local", color_discrete_sequence=px.colors.sequential.Viridis)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = px.pie(df, names="Nível de Perigo", values="Volume (kg)", title="Distribuição por Nível de Perigo", color_discrete_sequence=px.colors.sequential.Teal)
            st.plotly_chart(fig2, use_container_width=True)
        
        # Gráfico de Responsáveis
        fig5 = px.bar(df, x="Responsável", y="Volume (kg)", title="Volume de Resíduos por Responsável", color="Tipo")
        st.plotly_chart(fig5, use_container_width=True)
        
        # Status dos resíduos por local
        fig6 = px.bar(df, x="Local", y="Volume (kg)", color="Status", title="Status dos Resíduos por Local")
        st.plotly_chart(fig6, use_container_width=True)
        
        st.subheader("📜 Tabela de Dados")
        st.dataframe(df)  # Exibe os dados na tabela

# Página de Clima e Alertas
elif menu == "Clima e Alertas":
    st.title("🌦️ Informações Climáticas e Alertas")  # Cabeçalho da página
    
    local = st.text_input("Digite o local para consulta climática")  # Campo para o usuário inserir o local
    if st.button("Consultar Clima"):  # Botão para buscar o clima
        if local:  # Verifica se o local foi preenchido
            clima = consultar_clima(local)  # Faz a consulta
            if "Erro" in clima:
                st.error(clima["Erro"])  # Exibe erro se houver
            else:
                # Exibe os dados do clima em formato de métrica
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("🌡️ Temperatura", clima["Temperatura"])
                col2.metric("☁️ Condição", clima["Condição"])
                col3.metric("💧 Umidade", clima["Umidade"])
                col4.metric("💨 Velocidade do Vento", clima["Velocidade do Vento"])
                
                # Alerta de temperatura
                if clima["Alerta Temperatura"]:
                    st.warning(clima["Alerta Temperatura"])  # Exibe alerta se houver
