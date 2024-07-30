from flask import Flask, jsonify, request

#Simple RestAPI for gathering data 
# Some of the readings start at -50, so if the collector picks them up it knows to stop and wait for the next try.
# If it really is -50 where you are then you have a lot more to worry about than this script. 


# You can see what is in the Data logger by using this command:
# curl  -H "Content-Type: application/json"  -X GET http://localhost:5000/sensors


sensors = [
    {
        'id': 'bucket_tips',
        'sensor_value': 0
    },
    {
        'id': 'probe_temp',
        'sensor_value': -50
    },
    {
        'id': 'humidity',
        'sensor_value': -50
    },
    {
        'id': 'backup_temp',
        'sensor_value': -50
    },
    {
        'id': 'barometric_pressure',
        'sensor_value': -50
    },
    {
        'id': 'LUX',
        'sensor_value': 0
    },
    {
        'id': 'UV',
        'sensor_value': 0
    },
    {
        'id': 'sun_temp',
        'sensor_value': -50
    },
    {
        'id': 'wind_speed',
        'sensor_value': 0
    },
    {
        'id': 'wind_gusts',
        'sensor_value': 0
    },
    {
        'id': 'wind_direction',
        'sensor_value': 0
    }

]


app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'These are not the droids you are looking for'

@app.route('/sensors', methods=['GET'])
def get_sensors():
    return jsonify({'sensors': sensors})

@app.route('/sensors/<string:sensor_id>', methods=['GET'])
def get_sensor(sensor_id):
    sensor = [sensor for sensor in sensors if sensor['id'] == sensor_id]
    if len(sensor) == 0:
        return jsonify({'error': 'Sensor not found'})
    return jsonify({'sensor': sensor[0]})


@app.route('/sensors/<string:sensor_id>', methods=['PUT'])
def update_sensors(sensor_id):
    sensor = [sensor for sensor in sensors if sensor['id'] == sensor_id]
    if len(sensor) == 0:
        return jsonify({'error': 'Sensor not found'})
#    sensor[0]['title'] = request.json.get('title', sensor[0]['title'])
    sensor[0]['sensor_value'] = request.json.get('sensor_value', sensor[0]['sensor_value'])
    return jsonify({'sensor': sensor[0]})



# A new endpoint to increment the sensor_value by 1

@app.route('/sensors/<string:sensor_id>/increment', methods=['PUT'])
def increment_sensor_value(sensor_id):
    sensor = [sensor for sensor in sensors if sensor['id'] == sensor_id]
    if len(sensor) == 0:
        return jsonify({'error': 'Sensor not found'})

    sensor[0]['sensor_value'] = int(sensor[0]['sensor_value']) + 1  
    return jsonify({'sensor': sensor[0]})




if __name__ == '__main__':
   # app.run(debug=False, port=5000)
   app.run(host='0.0.0.0',debug=False, port=5000) # Allow connections on external interfaces - Handy when using ESP32
