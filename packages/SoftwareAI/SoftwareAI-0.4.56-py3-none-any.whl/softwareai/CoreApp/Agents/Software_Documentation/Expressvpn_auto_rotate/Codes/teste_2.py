from ui.Expressvpn_Auto_Rotatemain_window_ui import Ui_MainWindow
from ui.Expressvpn_Auto_Rotatebenchmark_window_ui import Ui_BenchmarkWindow
from ui.Expressvpn_Auto_Rotateglobal_benchmark_window_ui import Ui_GlobalBenchmarkWindow

from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QProgressBar, QLabel, QCheckBox, QSpinBox, QLineEdit, QWidget
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from os import path
from subprocess import check_output,DEVNULL
from bs4 import BeautifulSoup
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from firebase_admin import credentials, initialize_app, storage, db, delete_app

import platform
import subprocess
import psutil
import re
import time
import urllib
import requests
import json
import ctypes
import firebase_admin
import hashlib
import uuid
import json
from firebase_admin import credentials, db, initialize_app
import hashlib
import os
import random
import random
import sys
import threading
import os
import platform
import subprocess
import psutil
import re
import time
import urllib
import requests
import json
from datetime import datetime, timedelta
import firebase_admin

cred = {
  "type": "service_account",
  "project_id": "expressvpnautorotate",
  "private_key_id": "490bd3fcef3250b546342b9b470508e9dab4a6ab",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCsieoKUgVPr2wG\nAeR2uHo0njOXkD7rxQMU4wiRyJi6aP73+ibj1J7qpaRQAX11enu45R5wkjUmEBM4\noCw79OyjythZTrRmoqFgEMJgGysmWmLDEFEmtgFpS+P7h5ucdSrOLw4dLiBe/O8E\nDCfxLlN4ogsczbWBu23taiqmHSkX4HejWyKF/MDN6YQDKLl+WHFrww+ntkBDPbaV\n7e57V/j4yj76FGCLmezIhtKswMnIDOibRi2ImfZBIGFBy01FxkKvqbk/eEEusvsX\nTv5FWU3VOo6R130U0UGTUxdRk2YGCrtohcELF/9re8i0UQnp6HudLs/zZiZ0vOjX\nK9bfJmWhAgMBAAECggEADXTEvHZQyg9VKOjH38cbvMkjyUEWLylnx/QRjIZs/DNz\nwx+OyJD3WIx/kpUd1ZDZClP6z5kPgmmZiNPbxKH251VKvI2p/cvW3cOg19b2mAtP\njYVTFuZLQ4zdecCbOb9c4xoCC0ji0cBUhxJy9lkrEwrsO/GtI1zcl2StcSlwCte1\ndzqlbS4qdQyaeHbhmoz/LRiUgjQuwrWLDpGoZPH4K66gxJzH+T/NIy5ThfFa1M23\n525Ompn8cveR86kciz8YTL3pAlHWFPLZzYFHUpwPaTaYxrD0OrTPVNT4JVmLPGEj\ny7tIEnnW5RH6tSAl6BmNBFLbzWv8a5ys5uqF4SqyGQKBgQDXvgi75S/Od8an0oMo\nkLZnL3e06/5brkegC5rzhCIRnQ9edtFjSf/AoNwPk6FLtyHQtq0FQQX5EvA0YlZv\npnqmHhbmSXy4jxYlOz9EHAsZyO1ARF/zyZcnFLpXTH53GdF8uKaT2HoG/oDjZWA3\nCOcA6wObpyYE/+Opji5The7qbQKBgQDMvA2srsL/Ya2U8E9QXKce6IDu7LwpDjBG\nbxutrVtLuVF0uRxGyjlk/t15A+R6F81/oZJzzl9v/TpOHmMMvFJjPHl8Bj5Loynu\n05nh6zqvbjqXPTGrc/7OwbsV3mFpNEd17Av2sNj8reG0fnAu+9iLY65mOnJxKf9+\n7piuw5AnhQKBgCORtDTuS1x6COmgXnlwqnIGtHDCu9P3vt1XLHvbnBZVU7RaWJlL\nGPx0SPPUfjJShiO4CnykRMzU339zexa7VttOeK4NDaAMDzWiOAMNsJLWuq7u1vcF\nlIMf+rzr4qnWOuCaPPSBK1U93pgfHabVM+jF1nlyLGWEns9UnrSsj0BdAoGAKK1Q\nVjfevFjO4SGh0IioF6cAPvhAJjQQeV4H9MjVs8TdH0DMEnCJWLyeijWwxmVGSg5z\nB5lAMwLv+6dj7JraD6drR64B4ItJgI8AKvfOkB5pe7UH0lXYkYHCRwUI+5sMe6xr\ncBcQ9ZsilfbtGRimnIMwmlUQedVrUu/a3BY05PUCgYEAxQFuh+e2ywKA0kam9UEH\nics32qnANkO+5DYplNuK7cx8ShcmyYID/1xb8Du5SsBy9N6J54a5rRJgSrFoXWUG\nbfHOF2oM/RwLCfpD63fAQweOeciYGMjMHxtvfHAdCiZpi0KrCKLpMr6eGh8xJCTh\nD0z9YIjbAH0rZbmexbGuQKA=\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-2hqgy@expressvpnautorotate.iam.gserviceaccount.com",
  "client_id": "108465600689493101885",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-2hqgy%40expressvpnautorotate.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
cred = credentials.Certificate(cred)
app1 = initialize_app(cred, {
        'storageBucket': 'expressvpnautorotate.appspot.com',
        'databaseURL': 'https://expressvpnautorotate-default-rtdb.firebaseio.com'
        })
bucket = storage.bucket(app=app1)


SELLIX_API_KEY = 'arcCshGGEckT8B0lYt94GxGmdz8jKX4CwnJjxHW7Dj4sRJxIBGh6YmG3ZNzvTCZq'
SELLIX_BASE_URL = 'https://dev.sellix.io/v1/'


ref1 = db.reference(f'Controle_de_versao')
data1 = ref1.get()                         
controle_das_funcao2 = "Controle_config_1"
controle_das_funcao_info_2 = {
"versao": 'atualizando_expressvpnautorotate_config_1.zip',
}
ref1.child(controle_das_funcao2).set(controle_das_funcao_info_2)
    

# import requests
# def get_disk_serial_number():
#     kernel32 = ctypes.windll.kernel32
#     volume_serial_number = ctypes.c_ulonglong(0)
#     filesystem_flags = ctypes.c_ulong(0)
#     max_component_length = ctypes.c_ulong(0)
#     file_system_name_buffer = ctypes.create_unicode_buffer(256)

#     drive = 'C:\\'

#     result = kernel32.GetVolumeInformationW(
#         ctypes.create_unicode_buffer(drive),
#         None,
#         0,
#         ctypes.pointer(volume_serial_number),
#         ctypes.pointer(max_component_length),
#         ctypes.pointer(filesystem_flags),
#         file_system_name_buffer,
#         ctypes.sizeof(file_system_name_buffer)
#     )

#     if result:
#         serial = volume_serial_number.value
#         return serial
#     return None

# def get_machine_info():
#     system_info = platform.uname()
#     machine = system_info.machine
#     return machine

# def get_cpu_info():
#     system_info = platform.uname()
#     cpu_info = {
#         "system": system_info.system,
#         "node": system_info.node,
#         "release": system_info.release,
#         "version": system_info.version,
#         "machine": system_info.machine,
#         "processor": system_info.processor
#     }
#     return str(cpu_info)

# def get_computer_id():
#     """
#     Gera um ID único para o computador atual baseado nas informações da CPU e do disco.
#     """
#     cpu_info = get_cpu_info()
#     disk_serial = get_disk_serial_number()
#     if cpu_info and disk_serial:
#         computer_id = hashlib.sha256(f"{cpu_info}{disk_serial}".encode()).hexdigest()
#         return computer_id
#     return None

# def set_hardware_id(license_key, hardware_id):
#     url = "https://dev.sellix.io/v1/products/licensing/hardware_id"

#     payload = {
#         "product_id": "666e049aa6efd",
#         "key": license_key,
#         "hardware_id": hardware_id
#     }
#     headers = {
#         "Authorization": f"{SELLIX_API_KEY}",
#         "Content-Type": "application/json"
#     }

#     response = requests.request("PUT", url, json=payload, headers=headers)

#     return response

# def check_license(license_key, hardware_id):
#     url = "https://dev.sellix.io/v1/products/licensing/check"

#     payload = {
#         "product_id": "666e049aa6efd",
#         "key": license_key,
#         "hardware_id": hardware_id
#     }
#     headers = {
#         "Authorization": f"{SELLIX_API_KEY}",
#         "Content-Type": "application/json"
#     }

#     response = requests.request("POST", url, json=payload, headers=headers)

#     return response

# def check_license_time(license_key, hardware_id):
#     url = "https://dev.sellix.io/v1/products/licensing/check"

#     payload = {
#         "product_id": "666e049aa6efd",
#         "key": license_key,
#         "hardware_id": hardware_id
#     }
#     headers = {
#         "Authorization": f"{SELLIX_API_KEY}",
#         "Content-Type": "application/json"
#     }

#     response = requests.request("POST", url, json=payload, headers=headers)
#     json_data= response.json()
#     created_at = json_data['data']['license']['created_at']
#     created_at_dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
#     created_at_iso = created_at_dt.isoformat()
#     return created_at_iso

# # license_key = 'NVAR-IHHYJDQZQLCTEPMM'


# # hardware_id = get_computer_id()
# # set_hardware_id(license_key, hardware_id)

# # resposta = check_license_time(license_key, hardware_id)
# # print(resposta)
# import requests
# import json
# import requests
# import json

# def get_expressvpn_servers_location_and_region(location, region=None):
#     try:
#         serverlist = requests.get("https://api.expressvpn.com/v1/servers?limit=10000").content
#         site_json = json.loads(serverlist)
#         filtered_servers = {'windows_names': [], 'linux_names': []}

#         for specific_dict in site_json:
#             try:
#                 locations = specific_dict.get('locations', [])
#                 for loc in locations:
#                     country_info = loc.get('country', {})
#                     country = country_info.get('name', '')
#                     city_info = country_info.get('city', {})
#                     city = city_info.get('name', '')

#                     if isinstance(country, str) and location.lower() in country.lower():
#                         if region:
#                             if isinstance(city, str) and region.lower() in city.lower():
#                                 print(f"Found match for location: {location} and region: {region} in city: {city}")  # Debug message
#                                 groups = specific_dict.get('groups', [])
#                                 for group in groups:
#                                     if group['title'] == 'Standard VPN servers':
#                                         filtered_servers['windows_names'].append(specific_dict['name'])
#                                         filtered_servers['linux_names'].append(specific_dict['domain'].split('.')[0])
#                                         print(f"Added server: {specific_dict['name']}")  # Debug message
#                                         break  # Exit the group loop if you find the desired category
#                         else:
#                             print(f"Found match for location: {location}")  # Debug message
#                             groups = specific_dict.get('groups', [])
#                             for group in groups:
#                                 if group['title'] == 'Standard VPN servers':
#                                     filtered_servers['windows_names'].append(specific_dict['name'])
#                                     filtered_servers['linux_names'].append(specific_dict['domain'].split('.')[0])
#                                     print(f"Added server: {specific_dict['name']}")  # Debug message
#                                     break  # Exit the group loop if you find the desired category
#             except KeyError as e:
#                 print(f"KeyError: {e}")  # Debug message

#         return filtered_servers
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return None

# # Exemplo de uso
# location = "United States"
# region = "Salt Lake City"
# servers = get_expressvpn_servers_location_and_region(location, region)
# print(servers)

# def get_expressvpn_servers_location(location):
#     try:
#         serverlist = requests.get("https://api.expressvpn.com/v1/servers?limit=10000").content
#         site_json = json.loads(serverlist)
#         filtered_servers = {'windows_names': [], 'linux_names': []}

#         for specific_dict in site_json:
#             try:
#                 locations = specific_dict.get('locations', [])
#                 for loc in locations:
#                     country_info = loc.get('country', {})
#                     country = country_info.get('name', '')
#                     if isinstance(country, str):
#                         print(f"Checking server in country: {country}")  # Debug message
#                         if location.lower() in country.lower():
#                             print(f"Found match for location: {location} in country: {country}")  # Debug message
#                             groups = specific_dict.get('groups', [])
#                             for group in groups:
#                                 if group['title'] == 'Standard VPN servers':
#                                     filtered_servers['windows_names'].append(specific_dict['name'])
#                                     filtered_servers['linux_names'].append(specific_dict['domain'].split('.')[0])
#                                     print(f"Added server: {specific_dict['name']}")  # Debug message
#                                     break  # Exit the group loop if you find the desired category
#                             break  # Exit the location loop if you find the desired country
#             except KeyError as e:
#                 print(f"KeyError: {e}")  # Debug message

#         return filtered_servers
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return None

# # # Exemplo de uso
# # location = "Chicago"
# # servers = get_expressvpn_servers_location(location)
# # print(servers)
