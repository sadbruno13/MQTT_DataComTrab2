import streamlit as st
from utils import MQTTClient
import time
from asyncio import run
from streamlit_modal import Modal


st.set_page_config(
    page_title="DataCom Trabalho 2",
    layout="wide",
    page_icon="👋"
)

@st.cache_resource
def connection():
    mqtt_client = MQTTClient(client_id="", username="datacomtrabalho",
                            password="Datacomtrab2",
                            broker_host="d27767a919604e57ae1b5d3324277e66.s2.eu.hivemq.cloud",
                            broker_port=8883)
    topic = "DadosSensor"
    mqtt_client.subscribe_topic(topic)
    return mqtt_client

@st.cache_data(persist="disk")
def get_data(data):
    data = data
    dados_umidade_temperatura = [(elemento["Umidade"], elemento["Temperatura"]) for elemento in data]
    return data, dados_umidade_temperatura

if __name__ == '__main__':
    st.title("Gráfico de Temperatura e Umidade")

    mqtt_client = connection()

    # Continuously update the visualization
    placeholder = st.empty()
    while True:

        # Check if there are new messages
        data, dados_umidade_temperatura = get_data(mqtt_client.data_list)

        # Check if there are new messages
        if data:
            with placeholder.container():
                # Re-render the visualization
                st.write("Tabela Valores Temperatura e Umidade")
                st.line_chart(dados_umidade_temperatura)
                        
            time.sleep(1)

