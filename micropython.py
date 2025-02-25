import network
import time
import dht
import ujson
from machine import Pin, time_pulse_us
from umqtt.simple import MQTTClient

# WiFi Configuration
WIFI_SSID = "ISP 1 R-Server"
WIFI_PASS = "smktibazma"

# MQTT Configuration
UBIDOTS_BROKER = "industrial.api.ubidots.com"
UBIDOTS_CLIENT_ID = "esp8266"
UBIDOTS_TOKEN = "BBUS-wme7Wa6aT9obp709Cki2ymTKiWwE1o"
UBIDOTS_TOPIC = "/v1.6/devices/esp8266"

EMQX_BROKER = "broker.emqx.io"
EMQX_PORT = 1883
EMQX_TOPIC = "/home/sensor/dht"

# Inisialisasi sensor & perangkat
dht_sensor = dht.DHT11(Pin(4))
led = Pin(2, Pin.OUT)
trigger = Pin(5, Pin.OUT)
echo = Pin(18, Pin.IN)

# Koneksi WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)

    for _ in range(10):
        if wlan.isconnected():
            print("Connected to WiFi:", wlan.ifconfig())
            return True
        time.sleep(1)

    print("Failed to connect to WiFi")
    return False

# Koneksi MQTT ke broker
def connect_mqtt(broker, client_id, user=None, password=None):
    try:
        client = MQTTClient(client_id, broker, user=user, password=password)
        client.connect()
        print(f"Connected to MQTT broker: {broker}")
        return client
    except Exception as e:
        print(f"MQTT connection failed ({broker}): {e}")
        return None

# Mengukur jarak dengan sensor ultrasonik
def get_distance():
    trigger.off()
    time.sleep_us(2)
    trigger.on()
    time.sleep_us(10)
    trigger.off()

    duration = time_pulse_us(echo, 1, 30000)
    if duration < 0:
        return None  # Timeout

    return round((duration * 0.0343) / 2, 2)

# Mengirim data ke broker secara bergantian
def send_data(client, topic, key, value):
    if client:
        try:
            payload = ujson.dumps({key: value})
            client.publish(topic, payload)
            print(f"Data {key}: {value} terkirim ke {topic}")
        except Exception as e:
            print(f"[ERROR] Gagal mengirim ke {topic}: {e}")

# Koneksi WiFi & MQTT
if connect_wifi():
    ubidots_client = connect_mqtt(UBIDOTS_BROKER, UBIDOTS_CLIENT_ID, user=UBIDOTS_TOKEN, password="")
    emqx_client = connect_mqtt(EMQX_BROKER, "esp8266-client")
else:
    print("Tidak bisa tersambung ke WiFi, cek kembali konfigurasi.")
    ubidots_client = emqx_client = None

mqtt_clients = [ubidots_client, emqx_client]
current_client_index = 0

# Loop utama
while True:
    try:
        distance = get_distance()
        dht_sensor.measure()
        temp, hum = dht_sensor.temperature(), dht_sensor.humidity()
        print(f"Suhu: {temp}°C, Kelembaban: {hum}%, Jarak: {distance}cm")

        # Mengambil client secara bergantian
        client = mqtt_clients[current_client_index]

        # Kirim data ke broker yang sedang aktif
        send_data(client, UBIDOTS_TOPIC if current_client_index == 0 else EMQX_TOPIC, "temperature", temp)
        send_data(client, UBIDOTS_TOPIC if current_client_index == 0 else EMQX_TOPIC, "humidity", hum)
        send_data(client, UBIDOTS_TOPIC if current_client_index == 0 else EMQX_TOPIC, "distance", distance)

        # Ganti client untuk pengiriman berikutnya
        current_client_index = (current_client_index + 1) % 2

        time.sleep(1)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(2)