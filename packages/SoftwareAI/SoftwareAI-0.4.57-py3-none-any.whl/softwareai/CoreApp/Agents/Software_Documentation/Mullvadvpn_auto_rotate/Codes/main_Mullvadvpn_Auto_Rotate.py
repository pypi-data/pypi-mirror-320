from ui.main_window_ui import Ui_MainWindow
from ui.benchmark_window_ui import Ui_BenchmarkWindow
from ui.global_benchmark_window_ui import Ui_GlobalBenchmarkWindow

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
import ssl
import time
from fake_useragent import UserAgent
from PyQt5 import QtCore, QtGui, QtWidgets
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
import requests
import ssl
import time
from fake_useragent import UserAgent

from bs4 import BeautifulSoup
cred = {
  "type": "service_account",
  "project_id": "mullvadautorotate",
  "private_key_id": "58219b3dddf925ce8ded7ef206fb1e9fcf1d8bcd",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDKIE9tmBU72Dja\naZg8NTVauyx0GjZ0f6oqG0yEJmPd2b6Ipv+L6kRpHess4wtbIzPFPemXVu5n6vwQ\nudF9gOMXJZVVbhaNtRMrFVojZMhvfvZ3yD+dJVkDdR9JqrCeTUKUqlb25ZnS1fxl\n03ZT0O0yzg9cGy6uVY8vYF1UrsOmNRjb4W2hZxidifrCVTyposvF48MxaucSGAjF\nQRHi3pVNGro4Do5vl89rmQUQzcCufTPAcNgVIK146BBukmQQlOhNBGGa9davr3Ge\n7BXf8SlUeVdc0NiQSnJ5dbTGh3t8BVnAftavE0Ip9F/XAnW+aPCgGFY6gUBL0fCU\nwsrURYDJAgMBAAECggEAE56uRxOXoA79ecn9Mn7xtmRrzLtMpONNh7fNphg54muD\n8KzRKmoriM6UKO/DBu40VMWNOpkAHEs1e4Ql/xo3MOR/ieLdQpUcjraMYNokEJqQ\n3xCriBv7d3fzeQmeCkeymk6skVu5IjuOO+4aUsl5dNCGsiibT+XTN8SRWqp6KFRb\nz5WDrq2VMqBE8FlfAzbjMwxqHWQuSqRVK9B2sR+HQDNASVZeWI+PfCQ+cwIdnvZN\nGlAVmOorjSL9JX9/tuA2CcLwdptcubUSfuPIlWlIeeL4Y3VOkxRXuIKdINrj8eLh\ngp84w7bHC7DU24OlaWUPhe0rtnTg+ErZX3kwj5mcBwKBgQD2X1DFreX4unuZbHF7\nl5Nmtkrotn20HqztzwKo2mhQiEyftnRXbtIMjFeTjTWLovP+fzG+zA095dgx7YMW\nBw53QngNIqAdZe5a/mCWQH/8RsqGi4lobPqMWz5QdSc4tmcbIweL+cqoU+qKz4Ac\nFFFYwwdMWdsdNkug2+t/H3tAOwKBgQDSBlxpPwxY11jYd6kREYAyYOv3hczWR80P\n46/P7bZWzuK6Z5RkerrakQkzkkKbavP83wIOHkmu+899lOSuD1KxlzH1EwhOBSEo\nfwMUNXhNqa73MPJdbhCqoEPr9H8dS6Gb5WjUUYq6dB0/PAE8jDGDLfxO7YXTW42b\n07M3okWWywKBgEhOXQRHLzE6eb/jZcLiD26bnYyC0o2kWxhIIv2va+IGvoY5JBfs\n/FSWc7VoQgjDQFy2s8DNXi2GYVb13/z9AS/bICSqvtch7TxjX7F5KJa/p/yowyEU\nqsu6k6VFXMd2MPhz5WkdXG7egf1PPMgA5oboZiHwVTBTmQqSwKDEeoW1AoGAe5+i\n5ZBnBCQ996z3p0RV4VGLk7b+S2MYITI0Wn/hxFcivfYaMsrLEbwtXl3JNxJNa5sY\n6paJaKZwC8uIj6wVUNNeZJM/YC1Ex0F73nlaxtwKURZOkxAmX0jWshzIdcX+6nSu\nr8sPjZCrZn07fRhITJ7U1OCa1T4erIqAA09RBuECgYBbjiJv0ITlToSzVRogfU8f\nGv4WzDOFj0hMu5MzMnuq8rg+4GE+So1kYJOF7X4rtUtJ/YtQSlJTcS3CKhQ74nfk\njh5A/aX+z7t6l43AQDy7qTrtB75SmjQp1GJQ2293vH1ShtPoI/hWIydkLQjah3bA\nfVa1HF3Tz5oWbE2ZOQ3RUQ==\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-7u159@mullvadautorotate.iam.gserviceaccount.com",
  "client_id": "112482516000982960007",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-7u159%40mullvadautorotate.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
cred = credentials.Certificate(cred)
app1 = initialize_app(cred, {
        'storageBucket': 'mullvadautorotate.appspot.com',
        'databaseURL': 'https://mullvadautorotate-default-rtdb.firebaseio.com'
        })
bucket = storage.bucket(app=app1)

SELLIX_API_KEY = 'arcCshGGEckT8B0lYt94GxGmdz8jKX4CwnJjxHW7Dj4sRJxIBGh6YmG3ZNzvTCZq'
SELLIX_BASE_URL = 'https://dev.sellix.io/v1/'


software_names = ["chrome"]
operating_systems = ["windows", "linux"]
user_agent_rotator = UserAgent()

class Security:
    def __init__(self, app1):
        self.app1 = app1
        self.serial_ref = db.reference('seriais', app=app1)
        self.session_ref = db.reference('sessions', app=app1)


    def get_machine_info(self):
        system_info = platform.uname()
        machine = system_info.node
        return machine
    
    def get_disk_serial_number(self):
        kernel32 = ctypes.windll.kernel32
        volume_serial_number = ctypes.c_ulonglong(0)
        filesystem_flags = ctypes.c_ulong(0)
        max_component_length = ctypes.c_ulong(0)
        file_system_name_buffer = ctypes.create_unicode_buffer(256)

        drive = 'C:\\'

        result = kernel32.GetVolumeInformationW(
            ctypes.create_unicode_buffer(drive),
            None,
            0,
            ctypes.pointer(volume_serial_number),
            ctypes.pointer(max_component_length),
            ctypes.pointer(filesystem_flags),
            file_system_name_buffer,
            ctypes.sizeof(file_system_name_buffer)
        )

        if result:
            serial = volume_serial_number.value
            return serial
        return None

    def get_cpu_info(self):
        system_info = platform.uname()
        cpu_info = {
            "system": system_info.system,
            "node": system_info.node,
            "release": system_info.release,
            "version": system_info.version,
            "machine": system_info.machine,
            "processor": system_info.processor
        }
        return str(cpu_info)

    def generate_serial(self, order_id, cpu_info):
        """
        Gera um serial único baseado no order_id e nas informações da CPU.
        """
        session_token = hashlib.sha256(f"{order_id}{cpu_info}".encode()).hexdigest()
        return session_token

    def register_computer(self, serial, computer_id, start_date, order_id):
        """
        Registra um computador para um serial.
        """
        serial_data = self.serial_ref.child(serial).get()

        if serial_data:
            registered_computers = serial_data.get('computers', [])
            if len(registered_computers) >= 2:
                raise Exception("Serial já foi usado em dois computadores diferentes.")
            if computer_id not in registered_computers:
                registered_computers.append(computer_id)
                self.serial_ref.child(serial).update({'computers': registered_computers})
        else:
            expiration_date = (datetime.fromisoformat(start_date) + timedelta(days=30)).isoformat()
            self.serial_ref.child(serial).set({
                'computers': [computer_id],
                'order_id_hash': serial,
                'order_id': order_id,
                'start_date': start_date,
                'expiration_date': expiration_date
            })

    def check_serial(self, serial, computer_id, start_date, order_id):
        """
        Verifica se o serial é válido para o computador.
        """
        serial_data = self.serial_ref.child(serial).get()

        if not serial_data:
            self.register_computer(serial, computer_id, start_date, order_id)
            serial_data = self.serial_ref.child(serial).get()

        start_date = serial_data.get('start_date')
        expiration_date = serial_data.get('expiration_date')
        if start_date and expiration_date:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S')
            expiration_date_obj = datetime.strptime(expiration_date, '%Y-%m-%dT%H:%M:%S')
            if expiration_date_obj <= start_date_obj:
                if expiration_date_obj <= datetime.now():
                    return False

        registered_computers = serial_data.get('computers', [])
        return computer_id in registered_computers or len(registered_computers) < 2

    def get_computer_id(self):
        """
        Gera um ID único para o computador atual baseado nas informações da CPU e do disco.
        """
        cpu_info = self.get_cpu_info()
        disk_serial = self.get_disk_serial_number()
        if cpu_info and disk_serial:
            computer_id = hashlib.sha256(f"{cpu_info}{disk_serial}".encode()).hexdigest()
            return computer_id
        return None

    def get_existing_session_token(self, order_id):
        session_data = self.session_ref.child(order_id).get()
        if session_data:
            return session_data.get('session_token')
        return None

    def create_session(self, order_id, key):
        """
        Cria uma nova sessão com as informações fornecidas.
        """
        session_data = f"{order_id}"
        session_token = hashlib.sha256(session_data.encode()).hexdigest()
        self.session_ref.child(order_id).set({
            'session_token': session_token,
            'order_id': order_id,
            'key': key
        })
        return session_token

    def get_or_create_session(self, order_id, key):
        """
        Obtém uma sessão existente ou cria uma nova.
        """
        session_token = self.get_existing_session_token(order_id)
        if session_token:
            return session_token
        session_token = self.create_session(order_id, key)
        return session_token

    def set_hardware_id(self, license_key, hardware_id):
        url = "https://dev.sellix.io/v1/products/licensing/hardware_id"

        payload = {
            "product_id": "667a0c20b2389",
            "key": license_key,
            "hardware_id": hardware_id
        }
        headers = {
            "Authorization": f"{SELLIX_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.request("PUT", url, json=payload, headers=headers)

        return response
    
    def check_license(self, license_key, hardware_id):
        url = "https://dev.sellix.io/v1/products/licensing/check"

        payload = {
            "product_id": "667a0c20b2389",
            "key": license_key,
            "hardware_id": hardware_id
        }
        headers = {
            "Authorization": f"{SELLIX_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.request("POST", url, json=payload, headers=headers)

        return response

    def check_license_time(self, license_key, hardware_id):
        url = "https://dev.sellix.io/v1/products/licensing/check"

        payload = {
            "product_id": "667a0c20b2389",
            "key": license_key,
            "hardware_id": hardware_id
        }
        headers = {
            "Authorization": f"{SELLIX_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.request("POST", url, json=payload, headers=headers)
        json_data= response.json()
        created_at = json_data['data']['license']['created_at']
        created_at_dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
        created_at_iso = created_at_dt.isoformat()
        return created_at_iso

    def get_order_id_by_serial(self, serial, hardware_id):
        headers = {
            'Authorization': f'Bearer {SELLIX_API_KEY}',
            'Content-Type': 'application/json'
        }
        payload = {
            "product_id": '667a0c20b2389',
            "key": serial,
            "hardware_id": hardware_id
        }
        
        response = requests.post('https://dev.sellix.io/v1/products/licensing/check', json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data and 'data' in data and 'license' in data['data']:
                return data['data']['license']['invoice_id']
            else:
                return "Invalid response structure or no data found."
        else:
            return f"Error: {response.status_code}, {response.text}"

    def set_hardware_id(self, license_key, hardware_id):
        url = "https://dev.sellix.io/v1/products/licensing/hardware_id"

        payload = {
            "product_id": "667a0c20b2389",
            "key": license_key,
            "hardware_id": hardware_id
        }
        headers = {
            "Authorization": f"{SELLIX_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.request("PUT", url, json=payload, headers=headers)

        return response

class Balanceamento_de_vpn:
  def __init__(self, items):
    self.items = items
    self.counter = [0] * len(items)

  def selecionar(self):
    min_count = min(self.counter)
    candidatos = [i for i, count in enumerate(self.counter) if count == min_count]
    selecionado = random.choice(candidatos)
    self.counter[selecionado] += 1
    return self.items[selecionado]

def set_headers(user_agent_rotator):
    useragent_pick = user_agent_rotator.random
    headers = {
        'User-Agent': useragent_pick,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'
    }
    return headers

def get_monitor():
    while True:

        ip_check_websites = [
        
            'https://ipinfo.io/json',
            'http://ipapi.co/json',
            'https://ipwhois.app/json',
            'https://get.geojs.io/v1/ip/geo.json', 
            'http://ip-api.com/json/',


        ]
        random.shuffle(ip_check_websites)  
        headers = set_headers(user_agent_rotator)
        for website_pick in ip_check_websites:
            try:
                request_currentip = urllib.request.Request(url=website_pick, headers=headers)
                context = ssl._create_unverified_context()  # Bypass SSL verification temporarily
                response = urllib.request.urlopen(request_currentip, context=context)
                data = json.loads(response.read().decode('utf-8'))

                ip = data.get('ip')
                cidade = data.get('city')
                regiao = data.get('region')
                pais = data.get('country')
                organizacao = data.get('org')
                codigo_postal = data.get('postal')
                fuso_horario = data.get('timezone')
                return ip, cidade, regiao, pais, fuso_horario, organizacao
            except Exception as error:
                print(f"Error retrieving {website_pick} monitor info: {error}")



def mullvad_rotation(location):
  mullvad_path = r'C:\Program Files\Mullvad VPN'
  os.chdir(mullvad_path)

  command_relay = rf'mullvad relay set location {location}'
  subprocess.run(command_relay, creationflags=subprocess.CREATE_NO_WINDOW)

  command_connect = rf'mullvad connect'
  subprocess.run(command_connect, creationflags=subprocess.CREATE_NO_WINDOW)

  return True

def lists_rotate(area_input):

  if 'complete_rotate_in_usa' in area_input:
    list = [
    'us sea',
    'us uyk',
    'us sjc',
    'us slc',
    'us rag',
    'us phx',
    'us nyc',
    'us mia',
    'us txc',
    'us lax',
    'us hou',
    'us det',
    'us den',
    'us dal',
    'us chi',
    'us bos',
    'us atl',
    'us qas'
    ]
    location = random.choice(list)      
    return location

  if 'complete_rotate_in_canada' in area_input:
    list = [
    'ca yyc',
    'ca mtr',
    'ca tor',
    'ca van'

    ]
    location = random.choice(list)      
    return location
  
  if 'complete_rotate' in area_input:
    connect_list = [  
    'us sea',
    'us uyk',
    'us sjc',
    'us slc',
    'us rag',
    'us phx',
    'us nyc',
    'us mia',
    'us txc',
    'us lax',
    'us hou',
    'us det',
    'us den',
    'us dal',
    'us chi',
    'us bos',
    'us atl',
    'us qas',
    'ca yyc',
    'ca mtr',
    'ca tor',
    'ca van'
    ]
    location = random.choice(connect_list)      
    return location

def status_mullvad():
  mullvad_path = r'C:\Program Files\Mullvad VPN'
  command = rf'mullvad status'
  os.chdir(mullvad_path)
  subprocess.run(command, creationflags=subprocess.CREATE_NO_WINDOW)
  return True

def disconnect_mullvad():
  mullvad_path = r'C:\Program Files\Mullvad VPN'
  command = rf'mullvad disconnect'
  os.chdir(mullvad_path)
  subprocess.run(command, creationflags=subprocess.CREATE_NO_WINDOW)
  return True


disconnect_mullvad()

diretorio_script = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(diretorio_script,'config', 'user_config.json')
BENCHMARK_FILE = os.path.join(diretorio_script,'config', 'benchmark_data.json')

class RotateVpnThread(QThread):
    progress = pyqtSignal(int)
    location = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, rotation_count, interval, rotate_in_usa, rotate_in_canada, rotate_in_complete, nvar_key):
        super().__init__()
        self.rotation_count = rotation_count
        self.interval = interval
        self.rotate_in_usa = rotate_in_usa
        self.rotate_in_canada = rotate_in_canada
        self.rotate_complete = rotate_in_complete
        self.nvar_keyy = nvar_key
        self.benchmark_data = self.load_benchmark_data()
        self._is_running = True



    def load_benchmark_data(self):
        try:
            security = Security(app1=app1)
            respostaname_machine = security.get_machine_info()
            ref = db.reference(f'benchmark_data_users/{respostaname_machine}')
            data = ref.get()
            if data:
                data['total_rotations'] = int(data.get('total_rotations', 0))  # Garantir que é um inteiro
                data['time_spent'] = float(data.get('time_spent', 0))  # Garantir que é um float
                if isinstance(data['locations_used'], str):  # Verificar se locations_used é uma string JSON
                    try:
                        data['locations_used'] = json.loads(data['locations_used'])
                    except json.JSONDecodeError:
                        data['locations_used'] = {}
                return data
            else:
                return {
                    'total_rotations': 0,
                    'time_spent': 0,
                    'locations_used': {}
                }
        except Exception as e:
            print(f"Error loading data: {e}")
            return {
                'total_rotations': 0,
                'time_spent': 0,
                'locations_used': {}
            }
    
    
    def update_benchmark_data(self):
        security = Security(app1=app1)
        respostaname_machine = security.get_machine_info()
        
        # Carregar dados existentes
        ref1 = db.reference(f'benchmark_data_users/{respostaname_machine}')
        existing_data = ref1.get() or {
            'total_rotations': 0,
            'time_spent': 0,
            'locations_used': {}
        }
        
        # Atualizar dados existentes
        self.benchmark_data['total_rotations'] = int(existing_data.get('total_rotations', 0)) + 1
        self.benchmark_data['time_spent'] += float(existing_data.get('time_spent', 0))
        
        ip, cidade, regiao, pais, fuso_horario, organizacao = get_monitor()
        self.benchmark_data['locations_used'][regiao] = self.benchmark_data['locations_used'].get(regiao, 0) + 1
        
        # Salvar dados atualizados
        ref1.set(self.benchmark_data)
        
        # Atualizar global_benchmark
        global_ref = db.reference('global_benchmark')
        global_data = global_ref.child(respostaname_machine).get() or {
            'total_rotations': 0,
            'time_spent': 0,
            'locations_used': {}
        }

        global_data['total_rotations'] = int(global_data.get('total_rotations', 0)) + 1
        global_data['time_spent'] += float(global_data.get('time_spent', 0))

        for location, count in self.benchmark_data['locations_used'].items():
            global_data['locations_used'][location] = global_data['locations_used'].get(location, 0) + count

        global_ref.child(respostaname_machine).set(global_data)

    def run(self):
        self.progress.emit(10)
        security = Security(app1=app1)
        key = self.nvar_keyy
        hardware_id = security.get_computer_id()
        order_id = security.get_order_id_by_serial(key, hardware_id)
        security.set_hardware_id(order_id, hardware_id)
        session_token = security.get_or_create_session(order_id, key)
        cpu_info = security.get_cpu_info()
        serial = security.generate_serial(session_token, cpu_info)
        computer_id = security.get_computer_id()
        start_date = security.check_license_time(key, computer_id)
        is_valid = security.check_serial(serial, computer_id, start_date, order_id)
        
        self.location.emit(f"CHECK YOU KEY WAIT.")
        self.progress.emit(20)
        time.sleep(1)
        self.progress.emit(26)
        self.location.emit(f"CHECK YOU KEY WAIT..")
        self.progress.emit(35)
        time.sleep(1)
        self.progress.emit(46)
        self.location.emit(f"CHECK YOU KEY WAIT...")
        self.progress.emit(56)
        time.sleep(1)
        self.progress.emit(67)
        self.location.emit(f"CHECK YOU KEY WAIT....")
        self.progress.emit(86)
        if is_valid == True:
            self.progress.emit(96)
            self.location.emit(f"YOU KEY IS VALID.")
            self.progress.emit(98)
            time.sleep(2)
            self.progress.emit(100)

            start_time = time.time()

    
            for i in range(self.rotation_count):
                #if not self._is_running:
                    # disconnect_WINDSCRIBE('disconnect')
                    # self.location.emit(f"W-V-A-R Stop")

                self.progress.emit(int(100 * i / self.rotation_count))
                
                if self.rotate_in_usa:
                    area_input = 'complete_rotate_in_usa'

                    def rotate_ip_mullvad(area_input):
                        
                        #time.sleep(5)
                        LISTA = []
                        lista_de_server = []
                        for i in range(12):
                            try:
                                original_ip, cidade, regiao, pais, fuso_horario, organizacao = get_monitor()
                                self.location.emit(f"YOU ip: {original_ip}")
                                LISTA.append(original_ip)
                            except ConnectionAbortedError:
                                time.sleep(1)
                                continue
                            else:
                                break
                        for i in range(12):
                            try:
                                time.sleep(5)
                                location = lists_rotate(area_input)
                                #lista_de_server.append(location)
                                #location_flag_teste = lista_de_server.pop(0)
                                self.location.emit(f"Connect in: {location}")
                                vpn2 = mullvad_rotation(location)
                                if vpn2 == True:
                                    time.sleep(15)
                                    for i in range(12):
                                        try:
                                            new_ip, cidade, regiao, pais, fuso_horario, organizacao = get_monitor()
                                            break
                                        except ConnectionAbortedError:
                                            time.sleep(1)
                                            continue
                                        
                                    t = f'{LISTA[0]}'
                                    t2 = f'{new_ip}'
                                    if t2 == t:
                                        
                                        self.location.emit(f"Retrying.")
                                        continue
                                    else:
                                        #server = lista_de_server.pop(0)
                                        
                                        self.location.emit(f"New ip: {t2}, Region: {regiao}")
                            
                                        return True
                            except Exception as e:
                                print(e)
                                time.sleep(5)
                                #break
                    rotate_ip_mullvad(area_input)            
                    self.benchmark_data['time_spent'] += time.time() - start_time
                    self.update_benchmark_data()
                if self.rotate_complete:    
                    area_input = 'complete_rotate'

                    def rotate_ip_mullvad(area_input):
                        
                        #time.sleep(5)
                        LISTA = []
                        lista_de_server = []
                        for i in range(12):
                            try:
                                original_ip, cidade, regiao, pais, fuso_horario, organizacao = get_monitor()
                                self.location.emit(f"YOU ip: {original_ip}")
                                LISTA.append(original_ip)
                            except ConnectionAbortedError:
                                time.sleep(1)
                                continue
                            else:
                                break
                        for i in range(12):
                            try:
                                time.sleep(5)
                                location = lists_rotate(area_input)
                                #lista_de_server.append(location)
                                #location_flag_teste = lista_de_server.pop(0)
                                self.location.emit(f"Connect in: {location}")
                                vpn2 = mullvad_rotation(location)
                                if vpn2 == True:
                                    time.sleep(15)
                                    for i in range(12):
                                        try:
                                            new_ip, cidade, regiao, pais, fuso_horario, organizacao = get_monitor()
                                            break
                                        except ConnectionAbortedError:
                                            time.sleep(1)
                                            continue
                                        
                                    t = f'{LISTA[0]}'
                                    t2 = f'{new_ip}'
                                    if t2 == t:
                                        
                                        self.location.emit(f"Retrying.")
                                        continue
                                    else:
                                        #server = lista_de_server.pop(0)
                                        
                                        self.location.emit(f"New ip: {t2}, Region: {regiao}")
                            
                                        return True
                            except Exception as e:
                                print(e)
                                time.sleep(5)
                                #break
                    rotate_ip_mullvad(area_input)            
                            
                    self.benchmark_data['time_spent'] += time.time() - start_time
                    self.update_benchmark_data()
                if self.rotate_in_canada:    
                    area_input = 'complete_rotate_in_canada'

                    def rotate_ip_mullvad(area_input):
                        
                        #time.sleep(5)
                        LISTA = []
                        lista_de_server = []
                        for i in range(12):
                            try:
                                original_ip, cidade, regiao, pais, fuso_horario, organizacao = get_monitor()
                                self.location.emit(f"YOU ip: {original_ip}")
                                LISTA.append(original_ip)
                            except ConnectionAbortedError:
                                time.sleep(1)
                                continue
                            else:
                                break
                        for i in range(12):
                            try:
                                time.sleep(5)
                                location = lists_rotate(area_input)
                                #lista_de_server.append(location)
                                #location_flag_teste = lista_de_server.pop(0)
                                self.location.emit(f"Connect in: {location}")
                                vpn2 = mullvad_rotation(location)
                                if vpn2 == True:
                                    time.sleep(15)
                                    for i in range(12):
                                        try:
                                            new_ip, cidade, regiao, pais, fuso_horario, organizacao = get_monitor()
                                            break
                                        except ConnectionAbortedError:
                                            time.sleep(1)
                                            continue
                                        
                                    t = f'{LISTA[0]}'
                                    t2 = f'{new_ip}'
                                    if t2 == t:
                                        
                                        self.location.emit(f"Retrying.")
                                        continue
                                    else:
                                        #server = lista_de_server.pop(0)
                                        
                                        self.location.emit(f"New ip: {t2}, Region: {regiao}")
                            
                                        return True
                            except Exception as e:
                                print(e)
                                time.sleep(5)
                                #break
                    rotate_ip_mullvad(area_input)            
                    self.benchmark_data['time_spent'] += time.time() - start_time
                    self.update_benchmark_data()
                        
                for _ in range(self.interval):
                    if not self._is_running:
                        disconnect_mullvad()
                        self.location.emit(f"M-V-A-R Stop")
                        break
                    time.sleep(1)
                    
            self.location.emit(f"M-V-A-R Finish")    
            self.progress.emit(100)
            self.finished.emit()


        elif is_valid == False:
            self.progress.emit(0)
            self.location.emit(f"YOU KEY IS Expired.")
            time.sleep(2)
        else:
            # Registra o computador para o serial
            try:
                security.register_computer(serial, computer_id, start_date)
                self.location.emit(f"YOU KEY IS Registred. Please try new")
                time.sleep(2)
            except Exception as e:
                print(f"Erro: {e}")

    def stop(self):
        self._is_running = False


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Mullvad Vpn Auto Rotate')
        logo_FILE = os.path.join(diretorio_script, 'ui', 'logo.png')
        style_FILE = os.path.join(diretorio_script, 'ui', 'style.qss')

        # Definindo o ícone da janela
        self.setWindowIcon(QIcon(logo_FILE))

        # Carregando o estilo Nord
        with open(style_FILE, 'r') as f:
            self.setStyleSheet(f.read())

        # Configurando a logo
        self.logoLabel = self.findChild(QLabel, 'logoLabel')
        #self.logoLabel.setPixmap(QPixmap(logo_FILE).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # Conectando o botão à função de rotação
        self.rotateButton = self.findChild(QPushButton, 'rotateButton')
        self.rotateButton.clicked.connect(self.on_rotate_button_clicked)
        self.rotateButton.clicked.connect(self.save_config)

        # Conectando o botão de parada
        self.stopButton = self.findChild(QPushButton, 'stopButton')
        self.stopButton.clicked.connect(self.on_stop_button_clicked)

        # Barra de progresso
        self.progressBar = self.findChild(QProgressBar, 'progressBar')

        # Label de localização
        self.locationLabel = self.findChild(QLabel, 'locationLabel')

        # Check box de rotação nos EUA
        self.usaCheckBox = self.findChild(QCheckBox, 'usaCheckBox')

        # Check box de rotação nos canada
        self.canadacheckBox = self.findChild(QCheckBox, 'canadacheckBox')

        # Check box de rotação nos complete
        self.completecheckBox = self.findChild(QCheckBox, 'completecheckBox')

        # Campo de entrada para chave Nvar
        self.lineEdit = self.findChild(QLineEdit, 'lineEdit')

        # Spin box para contagem de rotações
        self.rotationCountSpinBox = self.findChild(QSpinBox, 'rotationCountSpinBox')

        # Spin box para intervalo de tempo
        self.intervalSpinBox = self.findChild(QSpinBox, 'intervalSpinBox')

        # Botão de benchmark
        self.benchmarkButton = self.findChild(QPushButton, 'benchmarkButton')
        self.benchmarkButton.clicked.connect(self.on_benchmark_button_clicked)

        # Botão de benchmark global
        self.globalBenchmarkButton = self.findChild(QPushButton, 'globalBenchmarkButton')
        self.globalBenchmarkButton.clicked.connect(self.on_global_benchmark_button_clicked)
        # Verificando se os checkboxes foram encontrados
    
        self.usaCheckBox.stateChanged.connect(self.update_checkboxes)
    
        self.canadacheckBox.stateChanged.connect(self.update_checkboxes)
    
        self.completecheckBox.stateChanged.connect(self.update_checkboxes)



        #self.save_config()
        self.load_config()

    def update_checkboxes(self):
        flagcanadacheckBox = self.canadacheckBox.isChecked()
        flagusaCheckBox = self.usaCheckBox.isChecked()
        flagcompletecheckBox= self.completecheckBox.isChecked()

        if flagcanadacheckBox == True:
            
            self.usaCheckBox.setChecked(False)
            self.completecheckBox.setChecked(False)

        if flagusaCheckBox == True:
            self.canadacheckBox.setChecked(False)
            self.completecheckBox.setChecked(False)

        if flagcompletecheckBox == True:
            self.canadacheckBox.setChecked(False)
            self.usaCheckBox.setChecked(False)


    def on_rotate_button_clicked(self):
        rotation_count = self.rotationCountSpinBox.value()
        interval = self.intervalSpinBox.value()
        rotate_in_usa = self.usaCheckBox.isChecked()
        rotate_in_canada = self.canadacheckBox.isChecked()
        rotate_in_complete = self.completecheckBox.isChecked()
        nvar_key = self.lineEdit.text()




        # security = Security(app1=app1)

        # # Verificação de licença com a API da Sellix
        # license_key = nvar_key
        # hardware_id = security.get_computer_id()
        # response = security.check_license(license_key, hardware_id)

        self.thread = RotateVpnThread(rotation_count, interval, rotate_in_usa, rotate_in_canada, rotate_in_complete, nvar_key)
        self.thread.progress.connect(self.update_progress)
        self.thread.location.connect(self.update_location)
        self.thread.finished.connect(self.on_rotation_finished)
        self.thread.start()


    def on_stop_button_clicked(self):
        if hasattr(self, 'thread') and self.thread.isRunning():
            self.thread.stop()
            self.thread.wait()
            self.on_rotation_finished()

    def on_benchmark_button_clicked(self):
        self.benchmarkWindow = BenchmarkWindow()
        self.benchmarkWindow.show()

    def on_global_benchmark_button_clicked(self):
        self.globalBenchmarkWindow = GlobalBenchmarkWindow()
        self.globalBenchmarkWindow.show()

    def update_progress(self, value):
        self.progressBar.setValue(value)

    def update_location(self, location):
        self.locationLabel.setText(location)

    def on_rotation_finished(self):
        self.rotateButton.setEnabled(True)
        self.stopButton.setEnabled(False)

    def resizeEvent(self, event):
        # Detecta a rotação da janela
        if self.width() > self.height():
            print('Landscape Mode')
        else:
            print('Portrait Mode')
        super(MainWindow, self).resizeEvent(event)

    def load_config(self):
        try:
            security = Security(app1=app1)
            respostaname_machine = security.get_machine_info()
            ref1 = db.reference(f'save_settings_users/{respostaname_machine}', app=app1)
            data1 = ref1.get()                         
            rotation_count = data1["rotation_count"]
            interval = data1["interval"]
            rotate_in_usa = data1["rotate_in_usa"]
            rotate_in_canada = data1["rotate_in_canada"]
            key_save = data1["key_save"]
            rotate_complete = data1["rotate_complete"]

            def str_to_bool(s):
                return s.lower() in ['true', '1', 't', 'y', 'yes']

            #config = json.load(ref1)
            self.rotationCountSpinBox.setValue(int(rotation_count))
            self.intervalSpinBox.setValue(int(interval))
            self.usaCheckBox.setChecked(str_to_bool(rotate_in_usa))
            self.canadacheckBox.setChecked(str_to_bool(rotate_in_canada))
            self.completecheckBox.setChecked(str_to_bool(rotate_complete))
            self.lineEdit.setText(str(key_save))
        except Exception as e:
            security = Security(app1=app1)
            respostaname_machine = security.get_machine_info()
            ref1 = db.reference(f'save_settings_users', app=app1)
            data1 = ref1.get()                         
            controle_das_funcao2 = f"{respostaname_machine}"
            controle_das_funcao_info_2 = {
            "rotation_count": f"{self.rotationCountSpinBox.value()}",
            "interval": f"{self.intervalSpinBox.value()}",
            "rotate_in_usa": f"{self.usaCheckBox.isChecked()}",
            "rotate_in_canada": f"{self.canadacheckBox.isChecked()}",
            "key_save": f"{self.lineEdit.text()}",
            "rotate_complete": f"{self.completecheckBox.isChecked()}",
            

            }
            ref1.child(controle_das_funcao2).set(controle_das_funcao_info_2)


    def save_config(self):
        security = Security(app1=app1)
        respostaname_machine = security.get_machine_info()
        ref1 = db.reference(f'save_settings_users', app=app1)
        data1 = ref1.get()                         
        controle_das_funcao2 = f"{respostaname_machine}"
        controle_das_funcao_info_2 = {
        "rotation_count": f"{self.rotationCountSpinBox.value()}",
        "interval": f"{self.intervalSpinBox.value()}",
        "rotate_in_usa": f"{self.usaCheckBox.isChecked()}",
        "rotate_in_canada": f"{self.canadacheckBox.isChecked()}",
        "key_save": f"{self.lineEdit.text()}",
        "rotate_complete": f"{self.completecheckBox.isChecked()}",
        

        }
        ref1.child(controle_das_funcao2).set(controle_das_funcao_info_2)

    def closeEvent(self, event):
        self.save_config()
        event.accept()


class BenchmarkWindow(QtWidgets.QWidget, Ui_BenchmarkWindow):
    def __init__(self):
        super(BenchmarkWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Benchmark Information')
        self.load_benchmark_data()

    def load_benchmark_data(self):
        try:
            security = Security(app1=app1)
            respostaname_machine = security.get_machine_info()
            ref = db.reference(f'benchmark_data_users/{respostaname_machine}')
            data = ref.get()
            if data:
                self.totalRotationsLabel.setText(f"Total Rotations: {data.get('total_rotations', 0)}")
                self.timeSpentLabel.setText(f"Time Spent in Application: {data.get('time_spent', 0)} seconds")
                locations = data.get('locations_used', {})
                self.update_most_used_locations(locations)
        except Exception as e:
            print(f"Error loading benchmark data: {e}")

class GlobalBenchmarkWindow(QWidget, Ui_GlobalBenchmarkWindow):
    def __init__(self):
        super(GlobalBenchmarkWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Global Benchmark Information')
        self.load_global_benchmark_data()
        
    def load_global_benchmark_data(self):
        ref = db.reference('global_benchmark')
        keys = ref.get(shallow=True)

        total_rotations = 0
        total_time_spent = 0.0
        locations_count = {}

        for key in keys:
            user_data = ref.child(key).get()
            total_rotations += int(user_data.get('total_rotations', 0))
            
            time_spent = user_data.get('time_spent', 0)
            if isinstance(time_spent, str):
                time_spent = float(time_spent.replace(' seconds', ''))
            total_time_spent += time_spent

            user_locations = user_data.get('locations_used', {})
            if isinstance(user_locations, dict):
                for location, count in user_locations.items():
                    locations_count[location] = locations_count.get(location, 0) + int(count)

        self.findChild(QLabel, 'totalRotationsLabel').setText(f"Total Rotations (Global): {total_rotations}")
        self.findChild(QLabel, 'timeSpentLabel').setText(f"Time Spent in Application (Global): {total_time_spent:.2f} seconds")
        
        self.update_most_used_locations(locations_count)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())