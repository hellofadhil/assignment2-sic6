import network
from machine import Pin
import time
import dht
import ujson
from umqtt.simple import MQTTClient

# WiFi & MQTT Configuration
WIFI_SSID = "ISP 2 R-Server"
WIFI_PASS = "smktibazma	"
MQTT_BROKER = "broker.emqx.io"
MQTT_CLIENT_ID = "Fadhil_dev"
TOPIC_PUB = "home/sensor/dht"
TOPIC_SUB = "home/sensor/led"

client = None

# Inisialisasi perangkat
dht_sensor = dht.DHT11(Pin(4))
led = Pin(2, Pin.OUT)

# Variabel penyimpanan nilai sebelumnya
prev_temp = None
prev_hum = None

# Koneksi ke WiFi dengan timeout
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)

    timeout = 10  # Maksimal waktu tunggu 10 detik
    while not wlan.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1

    if wlan.isconnected():
        print("Connected:", wlan.ifconfig())
        return True  # Koneksi berhasil
    else:
        print("Failed to connect to WiFi")
        return False  # Koneksi gagal

# Callback untuk pesan MQTT masuk
def mqtt_callback(topic, msg):
    print(f"Pesan diterima: {msg}")
    try:
        data = ujson.loads(msg)  # Parsing JSON
        if "led" in data:
            if data["led"] == "ON":
                led.on()
                print("LED ON")
            elif data["led"] == "OFF":
                led.off()
                print("LED OFF")
    except ValueError:
        print("Pesan bukan JSON yang valid")

# Koneksi ke MQTT dengan retry
def connect_mqtt():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
        client.set_callback(mqtt_callback)
        client.connect()
        client.subscribe(TOPIC_SUB)
        print("Connected to MQTT Broker")
        return client
    except Exception as e:
        print(f"MQTT connection failed: {e}")
        return None

# Inisialisasi WiFi & MQTT
if connect_wifi():
    client = connect_mqtt()
    if client is None:
        print("Gagal menyambung ke MQTT")
else:
    print("Tidak bisa tersambung ke WiFi, cek kembali konfigurasi.")

# Loop utama
while True:
    try:
        dht_sensor.measure()
        temp, hum = dht_sensor.temperature(), dht_sensor.humidity()

        # Hanya kirim data jika ada perubahan
        if temp != prev_temp or hum != prev_hum:
            print(f"Data berubah: Suhu: {temp}°C, Kelembaban: {hum}%")
            payload = ujson.dumps({"suhu": temp, "kelembaban": hum})
            if client:
                client.publish(TOPIC_PUB, payload)
            prev_temp, prev_hum = temp, hum 

        if client:
            client.check_msg() 

        time.sleep(1.5)

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(2)
