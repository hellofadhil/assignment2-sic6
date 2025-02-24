from flask import Blueprint, request, jsonify
from services.sensor_service import (
     get_sensor_dht
)

sensor_bp = Blueprint("sensor", __name__, url_prefix="/sensors")

@sensor_bp.route("/dht", methods=["GET"])
def retrieve_sensors():
    """API endpoint to get all sensors."""
    response, status_code = get_sensor_dht()
    return jsonify(response), status_code

