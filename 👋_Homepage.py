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

if __name__ == '__main__':
    st.title("Página Inicial do Trabalho 2 de Comunicação de Dados")
    st.subheader("Aquisição de dados de temperatura e umidade utilizando MQTT")

    mqtt_client = MQTTClient(client_id="", username="datacomtrabalho",
                               password="Datacomtrab2",
                               broker_host="d27767a919604e57ae1b5d3324277e66.s2.eu.hivemq.cloud",
                               broker_port=8883)
    topic = "DadosSensor"
    mqtt_client.subscribe_topic(topic)

    # Continuously update the visualization
    placeholder = st.empty()
    while True:

        # Check if there are new messages
        data = mqtt_client.data_list

        # Check if there are new messages
        if data:
            with placeholder.container():
                col1, col2, col3 = st.columns(3)
                with col1:
                        ult_temp = round(data[-1]["Temperatura"], 2)
                        ult_umi = data[-1]["Umidade"]
                        dif_temp = 0
                        dif_umi = 0
                        if(len(data)>1): 
                            pen_temp= data[-2]["Temperatura"]
                            pen_umi = data[-2]["Umidade"]
                            dif_temp = round(ult_temp - pen_temp, 2)
                            dif_umi = ult_umi - pen_umi

                        ult_data = data[-1]["Data"]
                        ult_hora = data[-1]["Hora"]
                        st.metric("Última atualização", "🕒 "+str(ult_data)+" "+str(ult_hora))
                        st.metric("Dispositivo", "🔌 " + str(data[-1]["deviceId"]))
                        st.metric("Temperatura", "🌡️ " + str(ult_temp) + " °C", delta = str(dif_temp)+" °C")
                        error_container = st.empty()
                        if(ult_temp > 30):
                            error_container.error("Cuidado, temperatura alta", icon="🚨")
                        st.metric("Umidade", "💧 "+str(ult_umi)+"%", delta = str(dif_umi)+"%")
                with col2:
                    # Re-render the visualization
                    st.write("Tabela Valores Temperatura e Umidade")
                    st.dataframe(data, height=800, width=400)
                with col3:
                        # Supondo que 'dados' é a sua lista de elementos
                    temperaturas = list(map(lambda elemento: elemento["Temperatura"], data))
                    umidades = list(map(lambda elemento: elemento["Umidade"], data))
                    st.write("Gráfico Temperatura")
                    st.line_chart(temperaturas, height=350)
                    st.write("Gráfico Umidade")
                    st.line_chart(umidades, height=350)
                        

            time.sleep(1)

