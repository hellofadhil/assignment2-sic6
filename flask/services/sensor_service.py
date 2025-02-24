from bson.objectid import ObjectId
from database import db

# Get the IoT collection
iot_collection = db["iot"]

def format_sensor(sensor):
    """Helper function to format a sensor document."""
    return {
        "id": str(sensor["_id"]),
        "temperature": sensor["temperature"],
        "humidity": sensor["humidity"]
    }

def get_sensor_dht():
    """Retrieve all sensor data."""
    sensors = [format_sensor(sensor) for sensor in iot_collection.find()]
    return sensors, 200

def add_sensor_mqtt(data):
    try:
        inserted_id = iot_collection.insert_one({
            "temperature": data.get("suhu"),
            "humidity": data.get("kelembaban")
        }).inserted_id

        return print(f"Success: Data added to MongoDB with ID {inserted_id}")
         
    except Exception as e:
        print(f"Error inserting data into MongoDB: {e}")
        return False

