#include <WiFi.h>
#include <NTPClient.h>
#include <TimeLib.h>
#include "DHTesp.h"
#include <ArduinoJson.h>
#include <PubSubClient.h>
#include <WiFiClientSecure.h>

/**** DHT11 sensor Settings *******/
#define DHTpin 2   //Set DHT pin as GPIO2
DHTesp dht;

/**** LED Settings *******/
const int led = 5; //Set LED pin as GPIO5

/****** WiFi Connection Details *******/
const char* ssid = "BRUNO";
const char* password = "showdebola";

/******* MQTT Broker Connection Details *******/
const char* mqtt_server = "d27767a919604e57ae1b5d3324277e66.s2.eu.hivemq.cloud";
const char* mqtt_username = "datacomtrabalho";
const char* mqtt_password = "Datacomtrab2";
const int mqtt_port = 8883;

/**** Secure WiFi Connectivity Initialisation *****/
WiFiClientSecure espClient;

/**** MQTT Client Initialisation Using WiFi Connection *****/
PubSubClient client(espClient);

unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE (50)
char msg[MSG_BUFFER_SIZE];

/************* Connect to WiFi ***********/
void setup_wifi() {
  delay(10);
  Serial.print("\nConnecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  randomSeed(micros());
  Serial.println("\nWiFi connected\nIP address: ");
  Serial.println(WiFi.localIP());
}

/************* Connect to MQTT Broker ***********/
void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP8266Client-";   // Create a random client ID
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str(), mqtt_username, mqtt_password)) {
      Serial.println("connected");

      client.subscribe("led_state");   // subscribe the topics here

    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");   // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

/***** Call back Method for Receiving MQTT messages and Switching LED ****/
void callback(char* topic, byte* payload, unsigned int length) {
  String incommingMessage = "";
  for (int i = 0; i < length; i++) incommingMessage+=(char)payload[i];

  Serial.println("Message arrived ["+String(topic)+"]"+incommingMessage);

  //--- check the incomming message
    if( strcmp(topic,"led_state") == 0){
     if (incommingMessage.equals("1")) digitalWrite(led, HIGH);   // Turn the LED on
     else digitalWrite(led, LOW);  // Turn the LED off
  }
}

/**** Method for Publishing MQTT Messages **********/
void publishMessage(const char* topic, String payload , boolean retained){
  if (client.publish(topic, payload.c_str(), true))
      Serial.println("Message publised ["+String(topic)+"]: "+payload);
}

const char *ntpServer = "pool.ntp.org";
const long gmtOffset_sec = -10800;
const int daylightOffset_sec = 0;
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, ntpServer, gmtOffset_sec, daylightOffset_sec);


/**** Application Initialisation Function******/
void setup() {

  dht.setup(DHTpin, DHTesp::DHT11); //Set up DHT11 sensor
  pinMode(led, OUTPUT); //set up LED
  Serial.begin(9600);
  while (!Serial) delay(1);
  setup_wifi();

  
  espClient.setInsecure();
  
  //espClient.setCACert(root_ca);

  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  timeClient.begin();
}

/******** Main Function *************/
void loop() {
  if (!client.connected()) 
    reconnect();
  client.loop();

  // Obtenha a data e hora atual do NTP
  timeClient.update();
  time_t rawTime = timeClient.getEpochTime();
  struct tm *timeinfo;
  timeinfo = localtime(&rawTime);
  
  // Obtenha a data e hora formatadas
  String formattedDate = String(timeinfo->tm_mday) + "/" +
                         String(timeinfo->tm_mon + 1) + "/" +
                         String(timeinfo->tm_year % 100); // Pegue os dois últimos dígitos do ano
  String formattedTime = timeClient.getFormattedTime();

  // Leia a umidade e temperatura do sensor DHT11
  delay(dht.getMinimumSamplingPeriod());
  float humidity = dht.getHumidity();
  float temperature = dht.getTemperature();

  // Crie um objeto JSON e adicione os dados
  DynamicJsonDocument doc(1024);

  doc["Data"] = formattedDate;
  doc["Hora"] = formattedTime;
  doc["deviceId"] = "ESP32/DHT11";
  doc["Umidade"] = humidity;
  doc["Temperatura"] = temperature;

  // Converta o JSON para uma string
  char mqtt_message[128];
  serializeJson(doc, mqtt_message);

  // Publique a mensagem MQTT
  publishMessage("DadosSensor", mqtt_message, true);

  delay(1000);
}