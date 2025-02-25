from flask import Flask
from routes.sensor_routes import sensor_bp
import paho.mqtt.client as mqtt
import json
from services.sensor_service import add_sensor_mqtt

app = Flask(__name__)

# MQTT Configuration
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
TOPIC = "/home/sensor/dht"

# Initialize MQTT client
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    data = msg.payload.decode("utf-8")
    data = json.loads(data)
    return add_sensor_mqtt(data)

# Configure MQTT client callbacks
client.on_connect = on_connect
client.on_message = on_message

# Connect and start MQTT loop
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

# Register Blueprints
app.register_blueprint(sensor_bp)

if __name__ == "__main__":
    app.run(debug=True)
