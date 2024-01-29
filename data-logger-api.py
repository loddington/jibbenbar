from flask import Flask, jsonify, request


#Simple RestAPI for gathering data - Really needs to have a basic security model added to it. Thats a job for tomorrow.

sensors = [
    {
        'id': 'bucket_tips',
        'sensor_value': 0
    },
    {
        'id': 'probe_temp',
        'sensor_value': 0
    },
    {
        'id': 'humidity',
        'sensor_value': 0
    },
    {
        'id': 'backup_temp',
        'sensor_value': 0
    },
    {
        'id': 'barometer',
        'sensor_value': 0
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
        'sensor_value': 0
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
    app.run(debug=False)
