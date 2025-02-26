import json
import re
import os
from requests import get, post
import subprocess
import ctypes


HOMEASSISTANT_ACCESS_TOKEN = os.environ["HOMEASSISTANT_TOKEN"]
HOMEASSISTANT_HOST = "http://" + os.environ["HOMEASSISTANT_HOST"]

headers = {
        "Authorization": "Bearer " + HOMEASSISTANT_ACCESS_TOKEN,
        "content-type": "application/json",
}


def get_area_entities(area_name="flat_1"):
    url = HOMEASSISTANT_HOST + "/api/template"
    area_name_quoted = "'"+area_name+"'"
    data = '{"template": "{{ area_entities(' + area_name_quoted + ') }}"}'
    response = post(url, data, headers=headers)
    return json.loads(re.sub(r"\'", '"', response.text))


def get_entity_details(entity_id):
    url = HOMEASSISTANT_HOST + "/api/states/" + entity_id
    response = get(url, headers=headers)
    return response.json()


def _get_permissible_areas_by_user(user_id):
    f = open("permissions.json")
    permissions = json.load(f)
    f.close()
    return permissions[user_id]


def get_permissible_areas_and_entities_by_user(user_id):
    areas = _get_permissible_areas_by_user(user_id)
    areas_entities = []
    for area in areas:
        area_entities = get_area_entities(area)
        if user_id in area_entities:
            area_entities.remove(user_id)
        area_entities_details = []
        for entity in area_entities:
            area_entities_details.append(get_entity_details(entity))

        areas_entities.append({
                                "area_name": area,
                                "entities": area_entities_details
                               })

    return areas_entities


def get_camera_picture(entity_id):
    entity_details = get_entity_details(entity_id)
    entity_picture = entity_details["attributes"]["entity_picture"]
    url = HOMEASSISTANT_HOST+entity_picture
    response = get(url)
    return response


def modify_device(entity_id, state):
    url = HOMEASSISTANT_HOST + "/api/states/"+entity_id
    response = post(url, state, headers=headers)
    print(response.text)
    return modify_device_via_service(entity_id, state)


def modify_device_via_service(entity_id, state):
    if entity_id.startswith("input_button"):
        return press_button(entity_id)
    else:
        url = HOMEASSISTANT_HOST + "/api/services/homeassistant/"
        print("state", state)
        print("state json", json.loads(state.decode('utf8'))["state"])
        if json.loads(state.decode('utf8'))["state"] == "on":
            url += "turn_on"
        else:
            url += "turn_off"

        print("url", url)
        response = post(url,
                        '{"entity_id":"' + entity_id + '"}',
                        headers=headers)

        print(response.text)
        return json.loads(re.sub(r"\'", '"', response.text))


def press_button(entity_id):
    url = HOMEASSISTANT_HOST + "/api/services/input_button/press"
    response = post(url,
                    '{"entity_id":"' + entity_id + '"}',
                    headers=headers)
    print(response.text)
    return json.loads(re.sub(r"\'", '"', response.text))


def login_old(username, password):
    lib = ctypes.CDLL('./mwauth.so')
    lib.check_password.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    lib.check_password.restype = ctypes.c_int
    return lib.check_password(bytes(password, "ascii"),
                              bytes(username, "ascii"))


def login(username, password, cheri_on):
    if cheri_on:
        executable = "./mwauth_cheri.o"
    else:
        executable = "./mwauth_noncheri.o"
    params = [password, username]
    process = subprocess.Popen([executable] + params, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode("utf-8")
