import network
from machine import Pin
import time
import dht
import ujson
from umqtt.simple import MQTTClient

# WiFi & Ubidots MQTT Configuration
WIFI_SSID = "ISP 1 R-Server"
WIFI_PASS = "smktibazma"

UBIDOTS_BROKER = "industrial.api.ubidots.com"
UBIDOTS_CLIENT_ID = "esp8266"
UBIDOTS_TOKEN = "BBUS-wme7Wa6aT9obp709Cki2ymTKiWwE1o"
DEVICE_LABEL = "esp8266"
TOPIC_PUB = f"/v1.6/devices/{DEVICE_LABEL}"
TOPIC_SUB = f"/v1.6/devices/{DEVICE_LABEL}/led/lv"

client = None

# Inisialisasi perangkat
dht_sensor = dht.DHT11(Pin(4))
led = Pin(2, Pin.OUT)

TRIG_PIN = 14  
ECHO_PIN = 12 

# Koneksi ke WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)

    timeout = 10
    while not wlan.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1

    if wlan.isconnected():
        print("Connected:", wlan.ifconfig())
        return True
    else:
        print("Failed to connect to WiFi")
        return False

# Callback untuk pesan MQTT masuk (mengontrol LED)
def mqtt_callback(topic, msg):
    print(f"Pesan diterima: {msg}")

    try:
        value = float(msg)  # Konversi langsung ke float

        if value == 1.0:
            led.on()
        elif value == 0.0:
            led.off()

    except ValueError:
        print("Pesan bukan angka yang valid")


# Koneksi ke MQTT Ubidots
def connect_mqtt():
    try:
        client = MQTTClient(
            UBIDOTS_CLIENT_ID,  # Client ID
            UBIDOTS_BROKER,  # Broker MQTT Ubidots
            user=UBIDOTS_TOKEN,  # API Key sebagai username
            password=""  # Password dikosongkan
        )
        client.set_callback(mqtt_callback)  # Set callback untuk menerima data
        client.connect()
        client.subscribe(TOPIC_SUB)  # Berlangganan topik untuk mengontrol LED
        print("Connected to Ubidots MQTT")
        return client
    except Exception as e:
        print(f"MQTT connection failed: {e}")
        return None

# Inisialisasi WiFi & MQTT
if connect_wifi():
    client = connect_mqtt()
    if client is None:
        print("Gagal menyambung ke MQTT Ubidots")
else:
    print("Tidak bisa tersambung ke WiFi, cek kembali konfigurasi.")

def get_distance():
    # Kirim sinyal trigger
    trig.off()
    time.sleep_us(2)
    trig.on()
    time.sleep_us(10)
    trig.off()
    
    # Tunggu sampai Echo high
    while echo.value() == 0:
        pass
    start_time = time.ticks_us()
    
    while echo.value() == 1:
        pass
    end_time = time.ticks_us()
    
    # Hitung selisih waktu
    duration = end_time - start_time
    distance = (duration * 0.0343) / 2  # Kecepatan suara di udara 343m/s
    
    return round(distance, 2)

# Loop utama
while True:
    try:
        distance = get_distance()
            print(f"Jarak: {distance} cm")
            
        dht_sensor.measure()
        temp, hum = dht_sensor.temperature(), dht_sensor.humidity()

        print(f"Data: Suhu: {temp}°C, Kelembaban: {hum}%")

        payload = ujson.dumps({
            "temperature": temp,
            "humidity": hum
        })

        if client:
            client.publish(TOPIC_PUB, payload)  # Kirim data ke Ubidots
            print("Data terkirim ke Ubidots:", payload)

            client.check_msg()  # Cek apakah ada pesan masuk untuk LED

        time.sleep(5)

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(2)
