from bson.objectid import ObjectId
from database import db

# Get the IoT collection
dht_collection = db["dht"]
distance_collection = db["distance"]

def format_sensor(sensor):
    """Helper function to format a sensor document."""
    return {
        "id": str(sensor["_id"]),
        "temperature": sensor["temperature"] ,
        "humidity": sensor["humidity"]
    }

def get_sensor_dht():
    """Retrieve all sensor data."""
    sensors = [format_sensor(sensor) for sensor in dht_collection.find()]
    return sensors, 200

def add_sensor_mqtt(data):
    try:
        print("Received data:", data)  

        if 'distance' in data:
            distance_collection.insert_one({"distance": data['distance']})
            print("Success: Distance data added to MongoDB distance")
        else:
            dht_collection.insert_one({
                "temperature": data.get('temperature', 0),  
                "humidity": data.get('humidity', 0)       
            })
            print("Success: Sensor data added to MongoDB temperature and humidity")


        return True
    except Exception as e:
        print(f"Error inserting data into MongoDB: {e}")
        return False
