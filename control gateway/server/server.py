import middleware
import json
import re

from flask import Flask
from flask import Flask, send_from_directory, jsonify, request, Response,  make_response
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


@app.before_request
def basic_authentication():
    if request.method.lower() == 'options':
        return Response()


@app.route('/')
def hello():
    return ""


@app.route('/api/login', methods=['POST'])
def login():
    '''
    Check the credentials and return the TOKEN to the user
    '''
    request_json = request.get_json()
    status = middleware.login(request_json["username"],
                              request_json["password"],
                              request_json["cheri_on"])
    make_response()
    response_data = {
        "status":  "Success" if status == "1" else "Fail",
        "TOKEN": "abcdefadsadsadsadsadsad"
    }
    response_status = 200 if status == "1" else 401
    return make_response(response_data,  response_status)


@app.route('/api/devices_entities/<user_id>')
def get_devices(user_id):
    '''
    List available devices
    '''
    user_id = "person." + user_id
    access_token = request.headers['Authorization'].split(" ")[1]
    if _auth_token(access_token, user_id):
        return middleware.get_permissible_areas_and_entities_by_user(user_id)
    else:
        return {}


@app.route('/api/camera/<entity_id>')
def camera(entity_id):
    '''
    Go find the camera token and return the jpeg to user
    '''

    res_temp = middleware.get_camera_picture(entity_id)
    return make_response(res_temp.content, "200")


@app.route('/api/devices_entities/<entity_id>', methods=['POST'])
def modify_device(entity_id):
    '''
    Modify the device
    '''
    return middleware.modify_device(entity_id, request.data)


def _auth_token(access_token, user_id):
    return True


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
