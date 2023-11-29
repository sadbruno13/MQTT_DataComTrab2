import paho.mqtt.client as paho
from paho import mqtt
import streamlit as st
import json

class MQTTClient:
    def __init__(self, client_id="", username="", password="", broker_host="", broker_port=8883):
        self.client = paho.Client(client_id=client_id)
        self.client.on_connect = self.on_connect
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish
        self.flag_connected = 0

        # enable TLS for secure connection
        self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        # set username and password
        self.client.username_pw_set(username, password)
        
        # Connect to the MQTT broker
        self.client.connect(broker_host, broker_port)
        # Start the MQTT loop in a separate thread
        self.client.loop_start()

        # Lista para armazenar os dados recebidos
        self.data_list = []

    def on_connect(self, client, userdata, flags, rc, properties=None):
        print("CONNACK received with code %s." % rc)
        # Mostrar o último dado recebido após a conexão
        if rc == 0:
            self.flag_connected = 1
            print("Sucesso ao conectar ao Broker")
        else:
            print("Tente conectar novamente")

    def on_subscribe(self, client, userdata, mid, granted_qos, properties=None):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
        # Decodificar o payload do JSON e adicionar à lista
        data = json.loads(msg.payload)
        self.data_list.append(data)
        print("Essa é a lista: ", self.data_list)

    def on_publish(self, client, userdata, mid, properties=None):
        print("mid: " + str(mid))

    def subscribe_topic(self, topic, qos=1):
        self.client.subscribe(topic, qos=qos)
