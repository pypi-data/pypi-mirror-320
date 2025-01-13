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
import json
import ssl
import time
from fake_useragent import UserAgent

from bs4 import BeautifulSoup
cred = {
  "type": "service_account",
  "project_id": "multivpnautorotate-7509d",
  "private_key_id": "7078eaf7e08477731165b6a3b928f9c15bc2efff",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCZkOSp4kQs1oSL\npmakrwxfg4h4N6eOr3zlqKz2aJwtg33myT4E90L2mNHpqUzA68rDSFIWSXFl0q/i\nX4vyWs3idDtYSfvK3lv8hepNkuB8ROYSwucHSyzjmOAFOSUk8dEnx3g0bzIB6NwJ\nCHnS/tA2ozEfBZTYzrfQYWmy/y+btH4HzuEJykFtT993WTkqOR8T8+YaiY8h5K5a\n19nFwvK9jTzf4+CGf1Z/5J8mTEEZ3H36OMalv7sITNPYs7+hUIeksXSp9bJGsj7b\nlRySLyTG7bZE3JdE94NDhRzEWX16+nhZbScjtAe+mMxLcBLE1yEEoROjMvtRYQy+\nEZ/dGBanAgMBAAECggEAKkCjqdqHx45+ia4PL+C6Fs2qDunBQJEoXEg8zs+ZqSw0\nx/s3BUbDNfZ2S0Q5yhsWfwS3EUrD2LBPlImVh+lUHKq+aVxx2y+zP5fZD98JxSdv\n5lmaF3ensjet68H9Zlzin39So5q0t7HKWPHsExHpWB8utMpkWgMGsF8dJhLwlnZ1\nz/wzJU/lnN73HbhHlvWYJm9nD8YP1X0TkUc8YSTyE1TqItmOzlMIx25YehWwC00v\nvliGwheUBmpZ/D0Q+rGinHKtP+VlL88m+/1rpRf1+QzvfnIwFnnWnBBxcY/WbY9m\nf2lD9DibT4tjZpH11EdnSmUIalQhRM8W+znLiMP3gQKBgQDL4hcgG5/BI27WYXgO\nOyWMuES1ZA13GkYOr4tocrWS0NNooZRfw5c8JNuagu812hdCnEOwfpAt3T0xcIlA\nWGX/3kH1NZ+7l9KKFBfY6ZIFJIulN5DHHXLnmWe//PYxw3ETbruIEwiDdiEU6dqJ\n5o5faS0kM9TYiEgNWb1fvCS/FQKBgQDA0hjuHLBdlIwGLfdaa15RONKpV5N+/h+E\nby1bK/adI17G9VeoLIGOgjs4Tx3AgIxJg4wR6eDevoFuhdKhBTATulJI5shgPBnC\ntFiVn+5JanZjktZlf0jolcxN/EvJJEJ3GxScmiVG1h1+yugKteP2vDcEy94VtgMG\nD10DcV6NywKBgDdr+ytQNwoSbrO6BR+hNmDdSlggnYRt0PN3Bqda3z7Mo1tC6Qlr\nKrY/sq56vzndUgtaXRAiJ2FATb0dwUGLhhaavUVB0Wz2JVZBhgYB4B6jw44i36kw\nuSZ5zfkjc20tmpRUuoeP3PWXbAC6XRy1XqhS9+FqcYZ27VcruM3IYBjNAoGBAKPg\nK+X7Jf1yqYr6+BW12OQo6gmYb7fnnLu+jYrGE4O7supfS8+Xe8i1cEVMIFoiJpi4\nH4x9/Gry+CgJvlixgwnROevRkI0Rp0cuZXdNBIUK4XGBM4vxoPJjlc7V1Ucu9Por\nXto1u+a3RTwkkQ/BROzHS+9coPRMy8cTuZaafKT/AoGAJGqOHxBSELTyVtkFsMRC\nijUDg7HbEA9S9Ag/AHsCfgjtWiiNhbTWegYEnTBCTmc6knCjcTWAM608VLVbPWp1\nFX/TyHn3K7V0+WH9WzveRUh+09NIMm+RNI7kOf7G7p/xx4h4CAYISfrQ6rPLxiCQ\nXqVTwzCnLg6fDW+49Velz4g=\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-l34eb@multivpnautorotate-7509d.iam.gserviceaccount.com",
  "client_id": "105265205905412292942",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-l34eb%40multivpnautorotate-7509d.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
cred = credentials.Certificate(cred)
app1 = initialize_app(cred, {
        'storageBucket': 'multivpnautorotate-7509d.appspot.com',
        'databaseURL': 'https://multivpnautorotate-7509d-default-rtdb.europe-west1.firebasedatabase.app'
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
            "product_id": "667bfba7c9123",
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
            "product_id": "667bfba7c9123",
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
            "product_id": "667bfba7c9123",
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
            "product_id": '667bfba7c9123',
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
            "product_id": "667bfba7c9123",
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

def get_ip():
  while True:
    try:
        headers = set_headers(user_agent_rotator)
        ip_check_websites = ['http://ip4only.me/api/','https://api64.ipify.org/',
                            'https://ipinfo.io/json', 'https://api.ipify.org?format=json',
                            'https://ifconfig.me/all.json', 'https://api.myip.com', 'https://ip.seeip.org/jsonip']
        website_pick = random.choice(ip_check_websites)
        request_currentip = urllib.request.Request(url=website_pick, headers=headers)
        ip_response = urllib.request.urlopen(request_currentip).read().decode('utf-8')
        if website_pick == 'http://ip4only.me/api/':
            ip = re.search("IPv4,(.*?),", ip_response).group(1)
            return  ip
        if website_pick == 'https://api64.ipify.org/':
            ip = ip_response.split(',')[0]
            return  ip
        if website_pick == 'https://ipinfo.io/json':
            ip_response_json = json.loads(ip_response)
            ip = ip_response_json["ip"]
            return  ip
        if website_pick == 'https://api.ipify.org?format=json':
            ip_response_json = json.loads(ip_response)
            ip = ip_response_json["ip"]
            return  ip
        if website_pick == 'https://ifconfig.me/all.json':
            ip_response_json = json.loads(ip_response)
            ip = ip_response_json["ip_addr"]
            return  ip
        if website_pick == 'https://api.myip.com':
            ip_response_json = json.loads(ip_response)
            ip = ip_response_json["ip"]
            return  ip
        if website_pick == 'https://ip.seeip.org/jsonip':
            ip_response_json = json.loads(ip_response)
            ip = ip_response_json["ip"]
            return  ip
        #return False
    except Exception as erro:
        print(erro)

        disconnect_mullvad()
        time.sleep(2)  

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


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin(cmd, cwd=None):
    params = " ".join([f'"{c}"' for c in cmd])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", f"/c {params}", None, 1)

def additional_settings_linux(additional_settings):
    try:
        additional_setting_execute = str(check_output(additional_settings))
    except:
        additional_setting_execute = "error"
    else:
        pass

    if "successfully" in additional_setting_execute:
        settings_input_message = "\nDone! Anything else?\n"
    elif additional_setting_execute == "error":
        settings_input_message = "\n\x1b[93mSomething went wrong. Please consult some examples by typing 'help'\x1b[0m\n"
    elif "already" in additional_setting_execute:
        settings_input_message = "\nThis setting has already been executed! Anything else?\n"
    else:
        settings_input_message = "\n\x1b[93mNordVPN throws an unexpected message, namely:\n" + additional_setting_execute + "\nTry something different.\x1b[0m\n"
    return settings_input_message

def saved_settings_check():
    print("\33[33mTrying to load saved settings...\33[0m")
    try:
        instructions = json.load(open("settings_nordvpn.txt"))
    except FileNotFoundError:
        raise Exception("\n\nSaved settings not found.\n"
                        "Run initialize_VPN() first and save the settings on your hard drive or store it into a Python variable.")
    else:
        print("\33[33mSaved settings loaded!\n\33[0m")
    return instructions

def get_nordvpn_servers():
    serverlist =  BeautifulSoup(requests.get("https://api.nordvpn.com/v1/servers").content,"html.parser")
    site_json=json.loads(serverlist.text)
    filtered_servers = {'windows_names': [], 'linux_names': []}
    
    for specific_dict in site_json:
        try:
            groups = specific_dict.get('groups', [])  # Verifica se 'groups' está presente
            for group in groups:
                if group['title'] == 'Standard VPN servers':
                    filtered_servers['windows_names'].append(specific_dict['name'])
                    filtered_servers['linux_names'].append(specific_dict['domain'].split('.')[0])
                    break  # Exit the group loop if you find the desired category
        except KeyError:
            pass  # Ignore dictionaries that do not have the 'groups' or 'title' key

    return filtered_servers


def windscribe_rotation_by_usa(action, location):
    windscribe_cli_path = r"C:\\Program Files\\Windscribe\\windscribe-cli.exe"
    if location is None:
        command = f'"{windscribe_cli_path}" {action}'
    else:
        command = f'"{windscribe_cli_path}" {action} {location}'
    try:

        subprocess.run(command, creationflags=subprocess.CREATE_NO_WINDOW)
    except:
        os.system(command)
  
    return True

def lists_rotate_windscribe(area_input):

  if 'complete_rotate_in_usa' in area_input:
    list = [
    'US East',
    'US Central',
    'US West'
    ]
    location = random.choice(list)      
    return location

  if 'complete_rotate_in_canada' in area_input:
    list = [
    'Canada East',
    'Canada West'
    ]
    location = random.choice(list)      
    return location
  

  if 'rotate_in_canada' in area_input:
    list_canaada = [ 
    "Montreal Bagel Poutine", "Montreal Expo 67",
    "Toronto Comfort Zone", "Toronto Mansbridge",
    "Toronto The 6", "Vancouver Granville",
    "Vancouver Stanley", "Vancouver Vansterdam"
    ]
    location = random.choice(list_canaada)      
    return location
  
  if 'rotate_in_los_angeles' in area_input:
    list = [
    "Las Vegas Casino", "Los Angeles Cube",
    "Los Angeles Dogg", "Los Angeles Eazy",
    "Los Angeles Lamar", "Los Angeles Pac"
    ]
    location = random.choice(list)      
    return location

  if 'complete_rotate' in area_input:
    connect_list = [  
    'Canada East',
    'Canada West',    
    'US East',
    'US Central',
    'US West', "Atlanta Mountain", "Atlanta Piedmont", "Dallas Ammo", "Dallas BBQ", "Dallas Ranch",
    "Dallas Trinity", "Denver Barley", "Kansas City Glinda", "Boston Harvard", "Boston MIT",
    "Boston Bill", "Charlotte Earnhardt", "Chicago Cub", "Chicago The L",
    "Chicago Wrigley", "Cleveland Brown", "Detroit Coney Dog", "Miami Florida Man",
    "Miami Snow", "Miami Vice", "Orlando Tofu Driver",
    "Philadelphia Fresh Prince", "Philadelphia Sunny", "South Bend Hawkins", "Tampa Cuban Sandwich",
    "Washington DC Precedent", "Bend Oregon Trail",
    "Phoenix Floatie", "San Francisco Sanitation",
    "Seattle Cobain", "Seattle Cornell", "Seattle Hendrix", "Halifax Crosby",
    "Montreal Bagel Poutine", "Montreal Expo 67", "Toronto Comfort Zone", "Toronto Mansbridge",
    "Toronto The 6", "Vancouver Granville", "Vancouver Stanley", "Vancouver Vansterdam"
    ]
    
    location = random.choice(connect_list)      
    return location
  
def disconnect_WINDSCRIBE(action):
    windscribe_cli_path = r"C:\\Program Files\\Windscribe\\windscribe-cli.exe"
    command = f'"{windscribe_cli_path}" {action}'
    try:

        subprocess.run(command, creationflags=subprocess.CREATE_NO_WINDOW)
    except:
        os.system(command)
    return True


def express_rotation(location):

    command = f'ExpressVPN.CLI.exe connect {location}'
    diretorio = r'C:\\Program Files (x86)\\ExpressVPN\\services'
    os.chdir(diretorio)
    #subprocess.Popen(["ExpressVPN.CLI.exe", "connect", f'{location}'],shell=True,cwd=diretorio,stdout=DEVNULL)
    os.system(command)

    return True

def lists_rotate_express_vpn(area_input):

  if 'complete_rotate_in_usa' in area_input:
    list = [
    '"USA - New York"',
    '"USA - Miami"',
    '"USA - Miami - 2"',
    '"USA - Dallas"',
    '"USA - Phoenix"',
    '"USA - Atlanta"',
    '"USA - Los Angeles - 3"',
    '"USA - Los Angeles - 2"',
    '"USA - Los Angeles - 1"',
    '"USA - Los Angeles - 5"',
    '"USA - São Francisco"',
    '"USA - Denver"',
    '"USA - Dallas - 2"',
    '"USA - Nova Jersey - 1"',
    '"USA - Nova Jersey - 3"',
    '"USA - Nova Jersey - 2"',
    '"USA - Chicago"',
    '"USA - Washington DC"',
    '"USA - Seattle"',
    '"USA - Salt Lake City"',
    '"USA - Tampa - 1"',
    '"USA - Albuquerque"',
    '"USA - Lincoln Park"',
    '"USA - Santa Mônica"'

    ]
    location = random.choice(list)      
    return location

  if 'complete_rotate_in_canada' in area_input:
    list = [
    '"Canada - Toronto - 2"',
    '"Canada - Toronto"',
    '"Canada - Vancouver"',
    '"Canada - Montreal"'

    ]
    location = random.choice(list)      
    return location
  

  if 'complete_rotate' in area_input:
    connect_list = [  
    '"USA - New York"',
    '"USA - Miami"',
    '"USA - Miami - 2"',
    '"USA - Dallas"',
    '"USA - Phoenix"',
    '"USA - Atlanta"',
    '"USA - Los Angeles - 3"',
    '"USA - Los Angeles - 2"',
    '"USA - Los Angeles - 1"',
    '"USA - Los Angeles - 5"',
    '"USA - São Francisco"',
    '"USA - Denver"',
    '"USA - Dallas - 2"',
    '"USA - Nova Jersey - 1"',
    '"USA - Nova Jersey - 3"',
    '"USA - Nova Jersey - 2"',
    '"USA - Chicago"',
    '"USA - Washington DC"',
    '"USA - Seattle"',
    '"USA - Salt Lake City"',
    '"USA - Tampa - 1"',
    '"USA - Albuquerque"',
    '"USA - Lincoln Park"',
    '"USA - Santa Mônica"',
    '"Canada - Toronto - 2"',
    '"Canada - Toronto"',
    '"Canada - Vancouver"',
    '"Canada - Montreal"'


    ]
    
    location = random.choice(connect_list)      
    return location

def disconnect_express():
    
    command = 'ExpressVPN.CLI.exe disconnect'
    diretorio = r'C:\\Program Files (x86)\\ExpressVPN\\services'
    teste = '"C:\\Program Files (x86)\\ExpressVPN\\services" ExpressVPN.CLI.exe disconnect'
    subprocess.Popen(["ExpressVPN.CLI.exe", "disconnect"],shell=True,cwd=diretorio,stdout=DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
    os.chdir(diretorio)
    os.system(command)
    return True


def mullvad_rotation(location):
    mullvad_path = r'C:\Program Files\Mullvad VPN'
    os.chdir(mullvad_path)

    command_relay = rf'mullvad relay set location {location}'
    try:

        subprocess.run(command_relay, creationflags=subprocess.CREATE_NO_WINDOW)
    except:
        os.system(command_relay)


    command_connect = rf'mullvad connect'
    try:

        subprocess.run(command_connect, creationflags=subprocess.CREATE_NO_WINDOW)
    except:
        os.system(command_connect)
    return True

def lists_rotate_mullvad(area_input):

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
    try:

        subprocess.run(command, creationflags=subprocess.CREATE_NO_WINDOW)
    except:
        os.system(command)
    return True


def pia_rotation(location):
    pia_path = r'C:\Program Files\Private Internet Access'
    os.chdir(pia_path)

    command_relay = rf'piactl set region {location}'
    #os.system(command_relay)
    try:

        subprocess.run(command_relay, creationflags=subprocess.CREATE_NO_WINDOW)
    except:
        os.system(command_relay)
    command_connect = rf'piactl connect'
    #os.system(command_connect)
    try:

        subprocess.run(command_connect, creationflags=subprocess.CREATE_NO_WINDOW)
    except:
        os.system(command_connect)
    return True

def lists_rotate_pia(area_input):

  if 'complete_rotate_in_usa' in area_input:
    list = [
    'us-florida',
    'us-west-virginia',
    'us-alabama',
    'us-connecticut',
    'us-massachusetts',
    'us-pennsylvania',
    'us-idaho',
    'us-virginia',
    'us-new-hampshire',
    'us-wilmington',
    'us-atlanta',
    'us-kentucky',
    'us-north-carolina',
    'us-baltimore',
    'us-montana',
    'us-louisiana',
    'us-south-carolina',
    'us-ohio',
    'us-rhode-island',
    'us-east-streaming-optimized',
    'us-houston',
    'us-maine',
    'us-mississippi',
    'us-tennessee',
    'us-indiana',
    'us-chicago',
    'us-kansas',
    'us-texas',
    'us-michigan',
    'us-vermont',
    'us-wisconsin',
    'us-iowa',
    'us-new-york',
    'us-wyoming',
    'us-missouri',
    'us-alaska',
    'us-arkansas',
    'us-east',
    'us-washington-dc',
    'us-west',
    'us-minnesota',
    'us-nebraska',
    'us-denver',
    'us-oregon',
    'us-new-mexico',
    'us-north-dakota',
    'us-oklahoma',
    'us-las-vegas',
    'us-south-dakota',
    'us-california',
    'us-salt-lake-city',
    'us-west-streaming-optimized',
    'us-honolulu',
    'us-seattle',
    'us-silicon-valley'
    ]
    location = random.choice(list)      
    location = random.choice(list)   
    location = random.choice(list)   
    return location

  if 'complete_rotate_in_canada' in area_input:
    list = [
    'ca-montreal',
    'ca-ontario',
    'ca-ontario-streaming-optimized',
    'ca-toronto',
    'ca-vancouver'

    ]
    location = random.choice(list)      
    return location
  
  if 'complete_rotate' in area_input:
    connect_list = [  
    'us-florida',
    'us-west-virginia',
    'us-alabama',
    'us-connecticut',
    'us-massachusetts',
    'us-pennsylvania',
    'us-idaho',
    'us-virginia',
    'us-new-hampshire',
    'us-wilmington',
    'us-atlanta',
    'us-kentucky',
    'us-north-carolina',
    'us-baltimore',
    'us-montana',
    'us-louisiana',
    'us-south-carolina',
    'us-ohio',
    'us-rhode-island',
    'us-east-streaming-optimized',
    'us-houston',
    'us-maine',
    'us-mississippi',
    'us-tennessee',
    'us-indiana',
    'us-chicago',
    'us-kansas',
    'us-texas',
    'us-michigan',
    'us-vermont',
    'us-wisconsin',
    'us-iowa',
    'us-new-york',
    'us-wyoming',
    'us-missouri',
    'us-alaska',
    'us-arkansas',
    'us-east',
    'us-washington-dc',
    'us-west',
    'us-minnesota',
    'us-nebraska',
    'us-denver',
    'us-oregon',
    'us-new-mexico',
    'us-north-dakota',
    'us-oklahoma',
    'us-las-vegas',
    'us-south-dakota',
    'us-california',
    'us-salt-lake-city',
    'us-west-streaming-optimized',
    'us-honolulu',
    'us-seattle',
    'us-silicon-valley',
    'ca-montreal',
    'ca-ontario',
    'ca-ontario-streaming-optimized',
    'ca-toronto',
    'ca-vancouver'
    ]
    location = random.choice(connect_list)      
    return location

def pia_disconnect():
    pia_path = r'C:\Program Files\Private Internet Access'
    os.chdir(pia_path)
    command = rf'piactl disconnect'
    try:

        subprocess.run(command, creationflags=subprocess.CREATE_NO_WINDOW)
    except:
        os.system(command)
    return True


def ivpn_rotation(location):
    ivpn_path = r'C:\Program Files\IVPN Client\cli'
    os.chdir(ivpn_path)
    
    command = rf'ivpn connect {location}'
    try:

        subprocess.run(command, creationflags=subprocess.CREATE_NO_WINDOW)
    except:
        os.system(command)
    return True

def lists_rotateivpn(area_input):

    if 'complete_rotate_in_usa' in area_input:
        list = [
        'us-ca.wg.ivpn.net',
        'us-ga.wg.ivpn.net',
        'us-il.wg.ivpn.net',
        'us-ny.wg.ivpn.net',
        'us-tx.wg.ivpn.net',
        'us-az.wg.ivpn.net',
        'us-co.wg.ivpn.net',
        'us-fl.wg.ivpn.net',
        'us-nj.wg.ivpn.net',
        'us-nv.wg.ivpn.net',
        'us-ut.wg.ivpn.net',
        'us-va.wg.ivpn.net',
        'us-wa.wg.ivpn.net',
        'us-az.gw.ivpn.net',
        'us-ca.gw.ivpn.net',
        'us-co.gw.ivpn.net',
        'us-fl.gw.ivpn.net',
        'us-ga.gw.ivpn.net',
        'us-il.gw.ivpn.net',
        'us-nj.gw.ivpn.net',
        'us-nv.gw.ivpn.net',
        'us-ny.gw.ivpn.net',
        'us-tx.gw.ivpn.net',
        'us-ut.gw.ivpn.net',
        'us-va.gw.ivpn.net',
        'us-wa.gw.ivpn.net'
        ]
        location = random.choice(list)      
        return location

    if 'complete_rotate_in_canada' in area_input:
        list = [
        'ca-qc.wg.ivpn.net',
        'ca-bc.wg.ivpn.net',
        'ca-on.wg.ivpn.net',
        'ca-qc.gw.ivpn.net',
        'ca-bc.gw.ivpn.net',
        'ca-on.gw.ivpn.net'

        ]
        location = random.choice(list)      
        return location
    
    if 'mix_rotate' in area_input:
        connect_list = [  
        'us-ca.wg.ivpn.net',
        'us-ga.wg.ivpn.net',
        'us-il.wg.ivpn.net',
        'us-ny.wg.ivpn.net',
        'us-tx.wg.ivpn.net',
        'us-az.wg.ivpn.net',
        'us-co.wg.ivpn.net',
        'us-fl.wg.ivpn.net',
        'us-nj.wg.ivpn.net',
        'us-nv.wg.ivpn.net',
        'us-ut.wg.ivpn.net',
        'us-va.wg.ivpn.net',
        'us-wa.wg.ivpn.net',
        'us-az.gw.ivpn.net',
        'us-ca.gw.ivpn.net',
        'us-co.gw.ivpn.net',
        'us-fl.gw.ivpn.net',
        'us-ga.gw.ivpn.net',
        'us-il.gw.ivpn.net',
        'us-nj.gw.ivpn.net',
        'us-nv.gw.ivpn.net',
        'us-ny.gw.ivpn.net',
        'us-tx.gw.ivpn.net',
        'us-ut.gw.ivpn.net',
        'us-va.gw.ivpn.net',
        'us-wa.gw.ivpn.net',
        'ca-qc.wg.ivpn.net',
        'ca-bc.wg.ivpn.net',
        'ca-on.wg.ivpn.net',
        'ca-qc.gw.ivpn.net',
        'ca-bc.gw.ivpn.net',
        'ca-on.gw.ivpn.net'

        ]
        location = random.choice(connect_list)      
        return location
    
    if 'complete_rotate' in area_input:
        locations = [
            "ca-qc.wg.ivpn.net",
            "ch.wg.ivpn.net",
            "de.wg.ivpn.net",
            "gb.wg.ivpn.net",
            "nl.wg.ivpn.net",
            "se.wg.ivpn.net",
            "sg.wg.ivpn.net",
            "us-ca.wg.ivpn.net",
            "us-ga.wg.ivpn.net",
            "us-il.wg.ivpn.net",
            "us-ny.wg.ivpn.net",
            "us-tx.wg.ivpn.net",
            "at.wg.ivpn.net",
            "au-nsw.wg.ivpn.net",
            "be.wg.ivpn.net",
            "bg.wg.ivpn.net",
            "br.wg.ivpn.net",
            "ca-bc.wg.ivpn.net",
            "ca-on.wg.ivpn.net",
            "cz.wg.ivpn.net",
            "dk.wg.ivpn.net",
            "es.wg.ivpn.net",
            "fi.wg.ivpn.net",
            "fr.wg.ivpn.net",
            "gb-man.wg.ivpn.net",
            "gr.wg.ivpn.net",
            "hk.wg.ivpn.net",
            "hu.wg.ivpn.net",
            "il.wg.ivpn.net",
            "is.wg.ivpn.net",
            "it.wg.ivpn.net",
            "jp.wg.ivpn.net",
            "lu.wg.ivpn.net",
            "mx.wg.ivpn.net",
            "my.wg.ivpn.net",
            "no.wg.ivpn.net",
            "pl.wg.ivpn.net",
            "pt.wg.ivpn.net",
            "ro.wg.ivpn.net",
            "rs.wg.ivpn.net",
            "sk.wg.ivpn.net",
            "tw.wg.ivpn.net",
            "ua.wg.ivpn.net",
            "us-az.wg.ivpn.net",
            "us-co.wg.ivpn.net",
            "us-fl.wg.ivpn.net",
            "us-nj.wg.ivpn.net",
            "us-nv.wg.ivpn.net",
            "us-ut.wg.ivpn.net",
            "us-va.wg.ivpn.net",
            "us-wa.wg.ivpn.net",
            "za.wg.ivpn.net",
            "at.gw.ivpn.net",
            "au-nsw.gw.ivpn.net",
            "be.gw.ivpn.net",
            "bg.gw.ivpn.net",
            "br.gw.ivpn.net",
            "ca-bc.gw.ivpn.net",
            "ca-on.gw.ivpn.net",
            "ca-qc.gw.ivpn.net",
            "ch.gw.ivpn.net",
            "cz.gw.ivpn.net",
            "de.gw.ivpn.net",
            "dk.gw.ivpn.net",
            "es.gw.ivpn.net",
            "fi.gw.ivpn.net",
            "fr.gw.ivpn.net",
            "gb-man.gw.ivpn.net",
            "gb.gw.ivpn.net",
            "gr.gw.ivpn.net",
            "hk.gw.ivpn.net",
            "hu.gw.ivpn.net",
            "il.gw.ivpn.net",
            "is.gw.ivpn.net",
            "it.gw.ivpn.net",
            "jp.gw.ivpn.net",
            "lu.gw.ivpn.net",
            "mx.gw.ivpn.net",
            "my.gw.ivpn.net",
            "nl.gw.ivpn.net",
            "no.gw.ivpn.net",
            "pl.gw.ivpn.net",
            "pt.gw.ivpn.net",
            "ro.gw.ivpn.net",
            "rs.gw.ivpn.net",
            "se.gw.ivpn.net",
            "sg.gw.ivpn.net",
            "sk.gw.ivpn.net",
            "tw.gw.ivpn.net",
            "ua.gw.ivpn.net",
            "us-az.gw.ivpn.net",
            "us-ca.gw.ivpn.net",
            "us-co.gw.ivpn.net",
            "us-fl.gw.ivpn.net",
            "us-ga.gw.ivpn.net",
            "us-il.gw.ivpn.net",
            "us-nj.gw.ivpn.net",
            "us-nv.gw.ivpn.net",
            "us-ny.gw.ivpn.net",
            "us-tx.gw.ivpn.net",
            "us-ut.gw.ivpn.net",
            "us-va.gw.ivpn.net",
            "us-wa.gw.ivpn.net",
            "za.gw.ivpn.net"
        ]
        location = random.choice(locations)      
        return location
        
def ivpndisconnect():
    ivpn_path = r'C:\Program Files\IVPN Client\cli'
    command = rf'ivpn disconnect'
    os.chdir(ivpn_path)
    os.system(command)
 
    return True



diretorio_script = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(diretorio_script,'config', 'user_config.json')
BENCHMARK_FILE = os.path.join(diretorio_script,'ui', 'benchmark_data.json')

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

def desativar_todas_vpns():
    ivpndisconnect()

    disconnectx_mullvad = disconnect_mullvad()
    if disconnectx_mullvad == True:
        print("VPN Mullvad DISCONNECT") 

    express_disconect = disconnect_express()    
    if express_disconect == True:
        print(F"VPN EXPRESS DISCONNECT")

    WINDSCRIBE_disconect = disconnect_WINDSCRIBE('disconnect')    
    if WINDSCRIBE_disconect == True:
        print(F"VPN WINDSCRIBE DISCONNECT")
            
    pia__disconect = pia_disconnect()    
    if pia__disconect == True:
        print(F"VPN PIA DISCONNECT")

    try:
        option_1_path = 'C:/Program Files/NordVPN'
        subprocess.Popen(["nordvpn", "-d"],shell=True,cwd=option_1_path,stdout=DEVNULL)
        print("VPN NORD DISCONNECT")    
    except:
        pass 

    return True

desativar_todas_vpns()

class RotateVpnThread(QThread):
    progress = pyqtSignal(int)
    location = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, rotation_count, interval, rotate_in_usa, rotate_in_canada, rotate_in_complete, nvar_key, rotation_count_per_vpn, vpnpia, vpnwinds, vpnexpress, vpnnord, vpnmullvad, IVPNcheckBox):
        super().__init__()
        self.rotation_count = rotation_count
        self.interval = interval
        self.rotate_in_usa = rotate_in_usa
        self.rotate_in_canada = rotate_in_canada
        self.rotate_complete = rotate_in_complete
        self.nvar_keyy = nvar_key
        self.benchmark_data = self.load_benchmark_data()
        self._is_running = True
        self.rotation_count_per_vpn = rotation_count_per_vpn
        self.vpnpia = vpnpia
        self.vpnwinds = vpnwinds
        self.vpnexpress = vpnexpress
        self.vpnnord = vpnnord
        self.vpnmullvad = vpnmullvad
        self.IVPNcheckBox = IVPNcheckBox
    
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

    def save_benchmark_data(self):
        try:
            security = Security(app1=app1)
            respostaname_machine = security.get_machine_info()
            ref = db.reference(f'benchmark_data_users/{respostaname_machine}')
            ref.set(self.benchmark_data)
        except Exception as e:
            print(f"Error saving data: {e}")

    def save_benchmark_dataglobal(self):
        try:
            security = Security(app1=app1)
            respostaname_machine = security.get_machine_info()
            ref = db.reference(f'benchmark_data_users/{respostaname_machine}')
            ref.set(self.benchmark_data)
        except Exception as e:
            print(f"Error saving data: {e}")

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
                    area_input_vpn = 'complete_rotate_in_usa'

                    def rotate_ip_mullvad(area_input):
                        
                        #time.sleep(5)
                        LISTA = []
                        lista_de_server = []
                        for i in range(12):
                            try:
                                original_ip, cidade, regiao, pais, fuso_horario, organizacao = get_monitor()
                                
                                LISTA.append(original_ip)
                            except ConnectionAbortedError:
                                time.sleep(1)
                                continue
                            else:
                                break
                        for i in range(12):
                            try:
                                time.sleep(5)
                                location = lists_rotate_mullvad(area_input)
                                #lista_de_server.append(location)
                                #location_flag_teste = lista_de_server.pop(0)
                                self.location.emit(f"Mullvad Connect in: {location}")
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
                                        
                                        self.location.emit(f"Mullvad New ip: {t2}, Region: {regiao}")
                            
                                        return True
                            except Exception as e:
                                print(e)
                                time.sleep(5)
                                #break
                    
                    def rotate_ip_windscribe(area_input):
                        
                        #time.sleep(5)
                        LISTA = []
                        lista_de_server = []
                        for i in range(12):
                            try:
                                original_ip, cidade, regiao, pais, fuso_horario, organizacao = get_monitor()
                                
                                LISTA.append(original_ip)
                            except ConnectionAbortedError:
                                time.sleep(1)
                                continue
                            else:
                                break
                        for i in range(12):
                            try:
                                time.sleep(5)
                                location = lists_rotate_windscribe(area_input)
                                #lista_de_server.append(location)
                                #location_flag_teste = lista_de_server.pop(0)
                                self.location.emit(f"Windscribe Connect in: {location}")
                                vpn2 = windscribe_rotation_by_usa("connect", location)
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
                                        
                                        self.location.emit(f"Windscribe New ip: {t2}, Region: {regiao}")
                            
                                        return True
                            except Exception as e:
                                print(e)
                                time.sleep(5)
                                #break
                    
                    def rotate_ip_express(area_input):
                        
                        #time.sleep(5)
                        LISTA = []
                        lista_de_server = []
                        for i in range(12):
                            try:
                                original_ip, cidade, regiao, pais, fuso_horario, organizacao = get_monitor()
                                
                                LISTA.append(original_ip)
                            except ConnectionAbortedError:
                                time.sleep(1)
                                continue
                            else:
                                break
                        for i in range(12):
                            try:
                                time.sleep(5)
                                location = lists_rotate_express_vpn(area_input)
                                #lista_de_server.append(location)
                                #location_flag_teste = lista_de_server.pop(0)
                                self.location.emit(f"Express Connect in: {location}")
                                vpn2 = express_rotation(location)
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
                                        
                                        self.location.emit(f"Express Retrying.")
                                        continue
                                    else:
                                        #server = lista_de_server.pop(0)
                                        
                                        self.location.emit(f"Express New ip: {t2}, Region: {regiao}")
                            
                                        return True
                            except Exception as e:
                                print(e)
                                time.sleep(5)
                                #break
                    
                    def rotate_ip_pia(area_input):
                        
                        #time.sleep(5)
                        LISTA = []
                        lista_de_server = []
                        for i in range(12):
                            try:
                                original_ip, cidade, regiao, pais, fuso_horario, organizacao = get_monitor()
                                
                                LISTA.append(original_ip)
                            except ConnectionAbortedError:
                                time.sleep(1)
                                continue
                            else:
                                break
                        for i in range(12):
                            try:
                                time.sleep(5)
                                location = lists_rotate_pia(area_input)
                                #lista_de_server.append(location)
                                #location_flag_teste = lista_de_server.pop(0)
                                self.location.emit(f"PIA Connect in: {location}")
                                vpn2 = pia_rotation(location)
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
                                        
                                        self.location.emit(f"PIA Retrying.")
                                        continue
                                    else:
                                        #server = lista_de_server.pop(0)
                                        
                                        self.location.emit(f"PIA New ip: {t2}, Region: {regiao}")
                            
                                        return True
                            except Exception as e:
                                print(e)
                                time.sleep(5)
                                #break
                    
                    def rotate_ip_ivpn(area_input):
                        
                        #time.sleep(5)
                        LISTA = []
                        lista_de_server = []
                        for i in range(12):
                            try:
                                original_ip, cidade, regiao, pais, fuso_horario, organizacao = get_monitor()
                                self.location.emit(f"i-v-a-r init")
                                LISTA.append(original_ip)
                            except ConnectionAbortedError:
                                time.sleep(1)
                                continue
                            else:
                                break
                        for i in range(12):
                            try:
                                time.sleep(5)
                                location = lists_rotateivpn(area_input)
                                #lista_de_server.append(location)
                                #location_flag_teste = lista_de_server.pop(0)
                                self.location.emit(f"Connect in: {location}")
                                vpn2 = ivpn_rotation(location)
                                if not self._is_running:
                                    ivpndisconnect()
                                    self.location.emit(f"I-V-A-R Stop")
                                    break

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

                    vpn_options = {
                        "America/New_York": ["New York,Manassas"],
                        "America/Chicago": ["Chicago,Saint Louis"],
                        "America/Denver": ["Denver,Chicago"],
                        "America/Los_Angeles": ["Los Angeles,Phoenix"],
                        "America/Seattle": ["Seattle,Chicago"],
                        "America/Salt_Lake_City": ["Chicago,Denver"],
                        "America/San_Francisco": ["San Francisco,Los Angeles"],
                        "America/Dallas": ["Dallas,Chicago"],
                        "America/Kansas_City": ["Chicago,Saint Louis"],
                        "America/Saint_Louis": ["Saint Louis,Dallas"],
                        "America/Atlanta": ["Atlanta,Charlotte"],
                        "America/Charlotte": ["Charlotte,Manassas,New York"],
                        "America/Miami": ["Miami,Atlanta,Charlotte"],
                        "America/Manassas": ["Manassas,New York"],
                        "America/Buffalo": ["Buffalo,New York"],
                        "America/Phoenix": ["Phoenix,Los Angeles"],
                        "America/Toronto": ["Toronto,Buffalo"],
                        "America/Vancouver": ["Atlanta,Seattle"],
                        "Europe/Paris": ["Miami,Buffalo"],
                        "North_America/Ottawa": ["Salt Lake City,New York,Phoenix"],
                        "North_America/Havana": ["Phoenix,Seattle"],
                    }

                    def initialize_VPN(area_input):
                        stored_settings = 0
                        save = 0
                        skip_settings = 0

                        ###load stored settings if needed and set input_needed variables to zero if settings are provided###
                        windows_pause = 3
                        additional_settings_needed = 1
                        additional_settings_list = list()

                        input_needed = 2
                        windows_pause = 8
            

                        ###performing system check###
                        opsys = platform.system()

                        ##windows##
                        if opsys == "Windows":
                            # print("\33[33mYou're using Windows.\n"
                            #       "Performing system check...\n"
                            #       "###########################\n\33[0m")
                            #diretorio_script = os.path.dirname(os.path.abspath(__file__))
                            #option_2_path = os.path.join(diretorio_script, 'NordVPN')
                            #option_1_path = os.path.join(diretorio_script, 'NordVPN')
                            option_1_path = 'C:/Program Files/NordVPN'
                            option_2_path = 'C:/Program Files (x86)/NordVPN'
                            custom_path = str()
                            if path.exists(option_1_path) == True:
                                cwd_path = option_1_path
                            elif path.exists(option_2_path) == True:
                                cwd_path = option_2_path
                            else:
                                custom_path = input("\x1b[93mIt looks like you've installed NordVPN in an uncommon folder. Would you mind telling me which folder? (e.g. D:/customfolder/nordvpn)\x1b[0m")
                                while path.exists(custom_path) == False:
                                    custom_path = input("\x1b[93mI'm sorry, but this folder doesn't exist. Please double-check your input.\x1b[0m")
                                while os.path.isfile(custom_path+"/NordVPN.exe") == False:
                                    custom_path = input("\x1b[93mI'm sorry, but the NordVPN application is not located in this folder. Please double-check your input.\x1b[0m")
                                cwd_path = custom_path
                            #print("NordVPN installation check: \33[92m\N{check mark}\33[0m")

                            #check if nordvpn service is already running in the background
                            check_service = "nordvpn-service.exe" in (p.name() for p in psutil.process_iter())
                            if check_service is False:
                                raise Exception("NordVPN service hasn't been initialized, please start this service in [task manager] --> [services] and restart your script")
                            #print("NordVPN service check: \33[92m\N{check mark}\33[0m")

                            # start NordVPN app and disconnect from VPN service if necessary#
                            #print("Opening NordVPN app and disconnecting if necessary...")
                            open_nord_win = subprocess.Popen(["nordvpn", "-d"],shell=True,cwd=cwd_path,stdout=DEVNULL)
                            while ("NordVPN.exe" in (p.name() for p in psutil.process_iter())) == False:
                                time.sleep(windows_pause)
                            open_nord_win.kill()
                            #print(": \33[92m\N{check mark}\33[0m")
                            #print("#####################################")
                            self.location.emit(f"NordVPN app launched.")

                        else:
                            raise Exception("I'm sorry, NordVPN switcher only works for Windows and Linux machines.")

                        diretorio_script = os.path.dirname(os.path.abspath(__file__))

                        file_path = os.path.join(diretorio_script,'config', 'countrylist.txt')

                        with open(file_path, 'r') as file:
                            areas_list = file.read().split('\n')
                            country_dict = {'countries':areas_list[0:60],'europe': areas_list[0:36], 'americas': areas_list[36:44],
                                            'africa east india': areas_list[49:60],'asia pacific': areas_list[49:60],
                                            'regions australia': areas_list[60:65],'regions canada': areas_list[65:68],
                                            'regions germany': areas_list[68:70], 'regions india': areas_list[70:72],
                                            'regions united states': areas_list[72:87],'special groups':areas_list[87:len(areas_list)]}

                        ##provide input if needed##
                        flag = False
                        while input_needed > 0:
                            if input_needed == 2:
                                self.location.emit(f"You've entered a list of connection options. Checking list...")
                
                                try:
                                    settings_servers = [area.lower() for area in area_input]
                                    settings_servers = ",".join(settings_servers)
                                except TypeError:
                                    raise Exception("I expected a list here. Are you sure you've not entered a string or some other object?\n ")

                            else:
                                if area_input == 'complete rotation':
                                    settings_servers = 'complete rotation'
                                
                            if opsys == "Windows":
                                nordvpn_command = ["nordvpn", "-c"]
                            if opsys == "Linux":
                                nordvpn_command = ["nordvpn", "c"]
                            #create sample of regions from input.#
                            #1. if quick connect#
                            if settings_servers == "quick":
                                if input_needed == 1:
                                    quickconnect_check = input("\nYou are choosing for the quick connect option. Are you sure? (y/n)\n")
                                    if 'y' in quickconnect_check:
                                        sample_countries = [""]
                                        input_needed = 0
                                        pass
                                if input_needed == 2:
                                    sample_countries = [""]
                                    input_needed = 0
                                else:
                                    print("\nYou are choosing for the quick connect option.\n")
                            #2. if completely random rotation
                            elif settings_servers == 'complete rotation':
                                print("\nFetching list of all current NordVPN servers...\n")
                                for i in range(120):
                                    try:
                                        filtered_servers = get_nordvpn_servers()
                                        if opsys == "Windows":
                                            nordvpn_command.append("-n")
                                            sample_countries = filtered_servers['windows_names']
                                        else:
                                            sample_countries = filtered_servers['linux_names']
                                    except:
                                        time.sleep(0.5)
                                        continue
                                    else:
                                        input_needed = 0
                                        break
                                else:
                                    raise Exception("\nI'm unable to fetch the current NordVPN serverlist. Check your internet connection.\n")
                            
                            #3. if provided specific servers. Notation differs for Windows and Linux machines, so two options are checked (first is Windows, second is Linux#
                            elif "#" in settings_servers or re.compile(r'^[a-zA-Z]+[0-9]+').search(settings_servers.split(',')[0]) is not None:
                                if opsys == "Windows":
                                    nordvpn_command.append("-n")
                                sample_countries = [area.strip() for area in settings_servers.split(',')]
                                input_needed = 0
                            else:
                                #3. If connecting to some specific group of servers#
                                if opsys == "Windows":
                                    nordvpn_command.append("-g")
                                #3.1 if asked for random sample, pull a sample.#
                                if "random" in settings_servers:
                                    #determine sample size#
                                    samplesize = int(re.sub("[^0-9]", "", settings_servers).strip())
                                    #3.1.1 if asked for random regions within country (e.g. random regions from United States,Australia,...)#
                                    if "regions" in settings_servers:
                                        try:
                                            sample_countries = country_dict[re.sub("random", "", settings_servers).rstrip('0123456789.- ').lower().strip()]
                                            input_needed = 0
                                        except:
                                            input("\n\nThere are no specific regions available in this country, please try again.\nPress enter to continue.\n")
                                            if input_needed == 2:
                                                input_needed = 1
                                                continue
                                        if re.compile(r'[^0-9]').search(settings_servers.strip()):
                                            sample_countries = random.sample(sample_countries, samplesize)
                                    #3.1.2 if asked for random countries within larger region#
                                    elif any(re.findall(r'europe|americas|africa east india|asia pacific', settings_servers)):
                                        larger_region = country_dict[re.sub("random|countries", "", settings_servers).rstrip('0123456789.- ').lower().strip()]
                                        sample_countries = random.sample(larger_region,samplesize)
                                        input_needed = 0
                                    #3.1.3 if asked for random countries globally#
                                    else:
                                        if re.compile(r'[^0-9]').search(settings_servers.strip()):
                                            sample_countries = random.sample(country_dict['countries'], samplesize)
                                            input_needed = 0
                                        else:
                                            sample_countries = country_dict['countries']
                                            input_needed = 0
                                #4. If asked for specific region (e.g. europe)#
                                elif settings_servers in country_dict.keys():
                                    sample_countries = country_dict[settings_servers]
                                    input_needed = 0
                                #5. If asked for specific countries or regions (e.g.netherlands)#
                                else:
                                    #check for empty input first.#
                                    if settings_servers == "":
                                        input("\n\nYou must provide some kind of input.\nPress enter to continue and then type 'help' to view the available options.\n")
                                        if input_needed == 2:
                                            input_needed = 1
                                            continue
                                    else:
                                        sample_countries = [area.strip() for area in settings_servers.split(',')] #take into account possible superfluous spaces#
                                        approved_regions = 0
                                        for region in sample_countries:
                                            if region in [area.lower() for area in areas_list]:
                                                approved_regions = approved_regions + 1
                                                pass
                                            else:
                                                #input("\n\nThe region/group " + region + " is not available. Please check for spelling errors.\nPress enter to continue.\n")
                                                if input_needed == 2:
                                                    input_needed = 1
                                                    continue
                                        if approved_regions == len(sample_countries):
                                            input_needed = 0

                        ##fetch current ip to prevent ip leakage when rotating VPN##
                        for i in range(59):
                            if flag == True:
                                break
                            try:
                                og_ip = get_ip()
                            except ConnectionAbortedError:
                                time.sleep(1)
                                continue
                            else:
                                break
                        else:
                            raise Exception("Can't fetch current ip, even after retrying... Check your internet connection.")

                        ##if user does not use preloaded settings##
                        if "instructions" not in locals():
                            #1.add underscore if spaces are present on Linux os#
                            for number,element in enumerate(sample_countries):
                                if element.count(" ") > 0 and opsys == "Linux":
                                        sample_countries[number] = re.sub(" ","_",element)
                            else:
                                pass
                            #2.create instructions dict object#
                            instructions = {'opsys':opsys,'command':nordvpn_command,'settings':sample_countries,'original_ip':og_ip}
                            if opsys == "Windows":
                                instructions['cwd_path'] = cwd_path

                            #3.save the settings if requested into .txt file in project folder#
                            if save == 1:
                                print("\nSaving settings in project folder...\n")
                                try:
                                    os.remove("settings_nordvpn.txt")
                                except FileNotFoundError:
                                    pass
                                instructions_write = json.dumps(instructions)
                                f = open("settings_nordvpn.txt", "w")
                                f.write(instructions_write)
                                f.close()

                        self.location.emit(f"Nord Done!")
                        return instructions

                    def rotate_ip_nord(vpn_instruction):

                        instructions = vpn_instruction
                        google_check = 0
                        if instructions is None:
                            instructions = saved_settings_check()

                        opsys = instructions['opsys']
                        command = instructions['command']
                        settings = instructions['settings']
                        og_ip = instructions['original_ip']

                        if opsys == "Windows":
                            cwd_path = instructions['cwd_path']

                        for i in range(2):
                            try:
                                current_ip = new_ip = get_ip()
                            except urllib.error.URLError:
                                self.location.emit(f"Nord Can't fetch current ip. Retrying...")
                            
                                time.sleep(10)
                                continue
                            else:
                                self.location.emit(f"Nord Your current ip-address is: {current_ip}")

                                time.sleep(2)
                                break
                        else:
                            self.location.emit(f"Nord Can't fetch current ip, even after retrying... Check your internet connection.")
                            

                        for i in range(5):
                            if len(settings) > 1:
                                settings_pick = list([random.choice(settings)])
                            else:
                                settings_pick = settings

                            input = command + settings_pick

                            if settings[0] == "":
                                print("\nConnecting you to the best possible server (quick connect option)...")
                            else:
                                self.location.emit(f"Nord Connecting: {settings_pick[0]}")
                                    

                
                            try:
                                if opsys == "Windows":
                                    new_connection = subprocess.Popen(input, shell=True, cwd=cwd_path)
                                    new_connection.wait(220)
                                else:
                                    new_connection = check_output(input)
                                    print("Found a server! You're now on "+re.search('(?<=You are connected to )(.*)(?=\()', str(new_connection))[0].strip())
                            except:
                                self.location.emit(f"An unknown error occurred")

                                

                            for i in range(12):
                                try:
                                    new_ip = get_ip()
                                except:
                                    time.sleep(5)
                                    continue
                                else:
                                    if new_ip in [current_ip,og_ip]:
                                        time.sleep(5)
                                        continue
                                    else:
                                        break
                            else:
                                pass

                            if new_ip in [current_ip,og_ip]:
                                self.location.emit("Nord ip-address hasn't changed. Retrying...\n")
                                time.sleep(10)
                                continue
                            else:
                                self.location.emit(f"Nord Conected! Enjoy your new server.")
                                time.sleep(3)


                            if google_check == 1:
                                print("\n\33[33mPerforming captcha-check on Google search and Youtube...\n"
                                    "---------------------------\33[0m")
                                try:
                                    google_search_check = BeautifulSoup(
                                        requests.get("https://www.google.be/search?q=why+is+python+so+hard").content,"html.parser")
                                    youtube_video_check = BeautifulSoup(
                                        requests.get("https://www.youtube.com/watch?v=dQw4w9WgXcQ").content,"html.parser")

                                    google_captcha = google_search_check.find('div',id="recaptcha")
                                    youtube_captcha = youtube_video_check.find('div', id = "recaptcha")

                                    if None not in (google_captcha,youtube_captcha):
                                        print("Google throws a captcha. I'll pick a different server...")
                                        time.sleep(5)
                                        continue
                                except:
                                    print("Can't load Google page. I'll pick a different server...")
                                    time.sleep(5)
                                    continue
                                else:
                                    print("Google and YouTube don't throw any Captcha's: \33[92m\N{check mark}\33[0m")
                                    break
                            else:
                                break


                    if self.vpnwinds:
                        windsarg = 'windscribe'
                    else:
                        windsarg = 'none'

                    if self.vpnnord:
                        nordarg = 'nord_vpn'
                    else:
                        nordarg = 'none'

                    if self.vpnpia:
                        piaarg = 'pia_vpn'
                    else:
                        piaarg = 'none'

                    if self.vpnexpress:
                        expressarg = 'express_vpn' 
                    else:
                        expressarg = 'none'

                    if self.vpnmullvad:
                        mullvadarg = 'mullvad'
                    else:
                        mullvadarg = 'none'

                    if self.IVPNcheckBox:
                        ivpnarg = 'ivpn'
                    else:
                        ivpnarg = 'none'

                    vpns_de_exscolha = [
                        windsarg,
                        nordarg,
                        expressarg, 
                        mullvadarg,
                        piaarg,
                        ivpnarg
                    ]
                    selecionador = Balanceamento_de_vpn(vpns_de_exscolha)


                    vpn_selecionada = selecionador.selecionar()

                    if vpn_selecionada == 'windscribe':
                        print(F"Rotacionar com a Windscribe")    
                        disconnectx_mullvad = disconnect_mullvad()
                        if disconnectx_mullvad == True:
                            print("VPN Mullvad DISCONNECT") 

                        express_disconect = disconnect_express()    
                        if express_disconect == True:
                            print(F"VPN EXPRESS DISCONNECT")
                                
                        pia__disconect = pia_disconnect()    
                        if pia__disconect == True:
                            print(F"VPN PIA DISCONNECT")

                        try:
                            option_1_path = 'C:/Program Files/NordVPN'
                            subprocess.Popen(["nordvpn", "-d"],shell=True,cwd=option_1_path,stdout=DEVNULL)
                            print("VPN NORD DISCONNECT")    
                        except:
                            pass 
                        
                        time.sleep(5)
                        for _ in range(self.rotation_count_per_vpn):
                                        
                            location = area_input_vpn   
                            vpn2 = rotate_ip_windscribe(location)
                            if vpn2 == True:
                                self.benchmark_data['time_spent'] += time.time() - start_time
                                self.update_benchmark_data()
                                
                    if vpn_selecionada == 'nord_vpn':
                        print(F"Rotacionar com a nord")   

                        disconnectx_mullvad = disconnect_mullvad()
                        if disconnectx_mullvad == True:
                            print("VPN Mullvad DISCONNECT") 

                        express_disconect = disconnect_express()    
                        if express_disconect == True:
                            print(F"VPN EXPRESS DISCONNECT")

                        WINDSCRIBE_disconect = disconnect_WINDSCRIBE('disconnect')    
                        if WINDSCRIBE_disconect == True:
                            print(F"VPN WINDSCRIBE DISCONNECT")
                                
                        pia__disconect = pia_disconnect()    
                        if pia__disconect == True:
                            print(F"VPN PIA DISCONNECT")


                        
                        time.sleep(15)
                        for _ in range(self.rotation_count_per_vpn):
                                    
                            timezone = random.choice(list(vpn_options.keys()))
                            vpn_options_for_timezone = vpn_options.get(timezone, [])
                            vpn_option = random.choice(vpn_options_for_timezone)
                            print(vpn_options_for_timezone)
                            print(vpn_option)
                            self.location.emit(f'{[vpn_option]}')
                            vpn_instruction = initialize_VPN(area_input=[vpn_option])
                            rotate_ip_nord(vpn_instruction)
                            self.benchmark_data['time_spent'] += time.time() - start_time
                            self.update_benchmark_data()
                    
                    if vpn_selecionada == 'mullvad':

                        print(F"Rotacionar com a mullvad") 

                        express_disconect = disconnect_express()    
                        if express_disconect == True:
                            print(F"VPN EXPRESS DISCONNECT")

                        WINDSCRIBE_disconect = disconnect_WINDSCRIBE('disconnect')    
                        if WINDSCRIBE_disconect == True:
                            print(F"VPN WINDSCRIBE DISCONNECT")
                                
                        pia__disconect = pia_disconnect()    
                        if pia__disconect == True:
                            print(F"VPN PIA DISCONNECT")

                        try:
                            option_1_path = 'C:/Program Files/NordVPN'
                            subprocess.Popen(["nordvpn", "-d"],shell=True,cwd=option_1_path,stdout=DEVNULL)
                            print("VPN NORD DISCONNECT")    
                        except:
                            pass 


                        time.sleep(5)
                        for _ in range(self.rotation_count_per_vpn):
                                    
                            location = area_input_vpn  
                            vpn2 = rotate_ip_mullvad(location)
                            if vpn2 == True:
                                self.benchmark_data['time_spent'] += time.time() - start_time
                                self.update_benchmark_data()
                                    
                    if vpn_selecionada == 'pia_vpn':

                        print(F"Rotacionar com a pia") 

                        disconnectx_mullvad = disconnect_mullvad()
                        if disconnectx_mullvad == True:
                            print("VPN Mullvad DISCONNECT") 

                        express_disconect = disconnect_express()    
                        if express_disconect == True:
                            print(F"VPN EXPRESS DISCONNECT")

                        WINDSCRIBE_disconect = disconnect_WINDSCRIBE('disconnect')    
                        if WINDSCRIBE_disconect == True:
                            print(F"VPN WINDSCRIBE DISCONNECT")
                                
                        try:
                            option_1_path = 'C:/Program Files/NordVPN'
                            subprocess.Popen(["nordvpn", "-d"],shell=True,cwd=option_1_path,stdout=DEVNULL)
                            print("VPN NORD DISCONNECT")    
                        except:
                            pass 

                        time.sleep(5)
                        for _ in range(self.rotation_count_per_vpn):
                                
                            location = area_input_vpn
                            vpn2 = rotate_ip_pia(location)
                            if vpn2 == True:
                                self.benchmark_data['time_spent'] += time.time() - start_time
                                self.update_benchmark_data()

                    if vpn_selecionada == 'express_vpn':

                        print(F"Rotacionar com a Express") 

                        disconnectx_mullvad = disconnect_mullvad()
                        if disconnectx_mullvad == True:
                            print("VPN Mullvad DISCONNECT") 

                        WINDSCRIBE_disconect = disconnect_WINDSCRIBE('disconnect')    
                        if WINDSCRIBE_disconect == True:
                            print(F"VPN WINDSCRIBE DISCONNECT")
                                
                        pia__disconect = pia_disconnect()    
                        if pia__disconect == True:
                            print(F"VPN PIA DISCONNECT")

                        try:
                            option_1_path = 'C:/Program Files/NordVPN'
                            subprocess.Popen(["nordvpn", "-d"],shell=True,cwd=option_1_path,stdout=DEVNULL)
                            print("VPN NORD DISCONNECT")    
                        except:
                            pass 
                        for _ in range(self.rotation_count_per_vpn):
                                    
                            location = area_input_vpn        
                            rotate_ip_express2 = rotate_ip_express(location)        
                            if rotate_ip_express2 == True:    
                                self.benchmark_data['time_spent'] += time.time() - start_time
                                self.update_benchmark_data()
                    
                    if vpn_selecionada == 'ivpn':

                        print(F"Rotacionar com a ivpn") 

                        express_disconect = disconnect_express()    
                        if express_disconect == True:
                            print(F"VPN EXPRESS DISCONNECT")

                        disconnectx_mullvad = disconnect_mullvad()
                        if disconnectx_mullvad == True:
                            print("VPN Mullvad DISCONNECT") 

                        WINDSCRIBE_disconect = disconnect_WINDSCRIBE('disconnect')    
                        if WINDSCRIBE_disconect == True:
                            print(F"VPN WINDSCRIBE DISCONNECT")
                                
                        pia__disconect = pia_disconnect()    
                        if pia__disconect == True:
                            print(F"VPN PIA DISCONNECT")

                        try:
                            option_1_path = 'C:/Program Files/NordVPN'
                            subprocess.Popen(["nordvpn", "-d"],shell=True,cwd=option_1_path,stdout=DEVNULL)
                            print("VPN NORD DISCONNECT")    
                        except:
                            pass 
                        for _ in range(self.rotation_count_per_vpn):
                                    
                            location = area_input_vpn        
                            rrotate_ip_ivpn2 = rotate_ip_ivpn(location)        
                            if rrotate_ip_ivpn2 == True:    
                                self.benchmark_data['time_spent'] += time.time() - start_time
                                self.update_benchmark_data()
                        

                    for _ in range(self.interval):
                        if not self._is_running:
                            desativar_todas_vpns()
                            self.location.emit(f"M-T-V-A-R Stop")
                            break
                        time.sleep(1)




                if self.rotate_complete:    
                    area_input_vpn = 'complete_rotate'

                    def rotate_ip_mullvad(area_input):
                        
                        #time.sleep(5)
                        LISTA = []
                        lista_de_server = []
                        for i in range(12):
                            try:
                                original_ip, cidade, regiao, pais, fuso_horario, organizacao = get_monitor()
                                
                                LISTA.append(original_ip)
                            except ConnectionAbortedError:
                                time.sleep(1)
                                continue
                            else:
                                break
                        for i in range(12):
                            try:
                                time.sleep(5)
                                location = lists_rotate_mullvad(area_input)
                                #lista_de_server.append(location)
                                #location_flag_teste = lista_de_server.pop(0)
                                self.location.emit(f"Mullvad Connect in: {location}")
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
                                        
                                        self.location.emit(f"Mullvad New ip: {t2}, Region: {regiao}")
                            
                                        return True
                            except Exception as e:
                                print(e)
                                time.sleep(5)
                                #break
                    
                    def rotate_ip_windscribe(area_input):
                        
                        #time.sleep(5)
                        LISTA = []
                        lista_de_server = []
                        for i in range(12):
                            try:
                                original_ip, cidade, regiao, pais, fuso_horario, organizacao = get_monitor()
                                
                                LISTA.append(original_ip)
                            except ConnectionAbortedError:
                                time.sleep(1)
                                continue
                            else:
                                break
                        for i in range(12):
                            try:
                                time.sleep(5)
                                location = lists_rotate_windscribe(area_input)
                                #lista_de_server.append(location)
                                #location_flag_teste = lista_de_server.pop(0)
                                self.location.emit(f"Windscribe Connect in: {location}")
                                vpn2 = windscribe_rotation_by_usa("connect", location)
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
                                        
                                        self.location.emit(f"Windscribe New ip: {t2}, Region: {regiao}")
                            
                                        return True
                            except Exception as e:
                                print(e)
                                time.sleep(5)
                                #break
                    
                    def rotate_ip_express(area_input):
                        
                        #time.sleep(5)
                        LISTA = []
                        lista_de_server = []
                        for i in range(12):
                            try:
                                original_ip, cidade, regiao, pais, fuso_horario, organizacao = get_monitor()
                                
                                LISTA.append(original_ip)
                            except ConnectionAbortedError:
                                time.sleep(1)
                                continue
                            else:
                                break
                        for i in range(12):
                            try:
                                time.sleep(5)
                                location = lists_rotate_express_vpn(area_input)
                                #lista_de_server.append(location)
                                #location_flag_teste = lista_de_server.pop(0)
                                self.location.emit(f"Express Connect in: {location}")
                                vpn2 = express_rotation(location)
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
                                        
                                        self.location.emit(f"Express Retrying.")
                                        continue
                                    else:
                                        #server = lista_de_server.pop(0)
                                        
                                        self.location.emit(f"Express New ip: {t2}, Region: {regiao}")
                            
                                        return True
                            except Exception as e:
                                print(e)
                                time.sleep(5)
                                #break
                    
                    def rotate_ip_pia(area_input):
                        
                        #time.sleep(5)
                        LISTA = []
                        lista_de_server = []
                        for i in range(12):
                            try:
                                original_ip, cidade, regiao, pais, fuso_horario, organizacao = get_monitor()
                                
                                LISTA.append(original_ip)
                            except ConnectionAbortedError:
                                time.sleep(1)
                                continue
                            else:
                                break
                        for i in range(12):
                            try:
                                time.sleep(5)
                                location = lists_rotate_pia(area_input)
                                #lista_de_server.append(location)
                                #location_flag_teste = lista_de_server.pop(0)
                                self.location.emit(f"PIA Connect in: {location}")
                                vpn2 = pia_rotation(location)
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
                                        
                                        self.location.emit(f"PIA Retrying.")
                                        continue
                                    else:
                                        #server = lista_de_server.pop(0)
                                        
                                        self.location.emit(f"PIA New ip: {t2}, Region: {regiao}")
                            
                                        return True
                            except Exception as e:
                                print(e)
                                time.sleep(5)
                                #break
                    
                    def rotate_ip_ivpn(area_input):
                        
                        #time.sleep(5)
                        LISTA = []
                        lista_de_server = []
                        for i in range(12):
                            try:
                                original_ip, cidade, regiao, pais, fuso_horario, organizacao = get_monitor()
                                self.location.emit(f"i-v-a-r init")
                                LISTA.append(original_ip)
                            except ConnectionAbortedError:
                                time.sleep(1)
                                continue
                            else:
                                break
                        for i in range(12):
                            try:
                                time.sleep(5)
                                location = lists_rotateivpn(area_input)
                                #lista_de_server.append(location)
                                #location_flag_teste = lista_de_server.pop(0)
                                self.location.emit(f"Connect in: {location}")
                                vpn2 = ivpn_rotation(location)
                                if not self._is_running:
                                    ivpndisconnect()
                                    self.location.emit(f"I-V-A-R Stop")
                                    break

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

                    vpn_options = {
                        "America/New_York": ["New York,Manassas"],
                        "America/Chicago": ["Chicago,Saint Louis"],
                        "America/Denver": ["Denver,Chicago"],
                        "America/Los_Angeles": ["Los Angeles,Phoenix"],
                        "America/Seattle": ["Seattle,Chicago"],
                        "America/Salt_Lake_City": ["Chicago,Denver"],
                        "America/San_Francisco": ["San Francisco,Los Angeles"],
                        "America/Dallas": ["Dallas,Chicago"],
                        "America/Kansas_City": ["Chicago,Saint Louis"],
                        "America/Saint_Louis": ["Saint Louis,Dallas"],
                        "America/Atlanta": ["Atlanta,Charlotte"],
                        "America/Charlotte": ["Charlotte,Manassas,New York"],
                        "America/Miami": ["Miami,Atlanta,Charlotte"],
                        "America/Manassas": ["Manassas,New York"],
                        "America/Buffalo": ["Buffalo,New York"],
                        "America/Phoenix": ["Phoenix,Los Angeles"],
                        "America/Toronto": ["Toronto,Buffalo"],
                        "America/Vancouver": ["Atlanta,Seattle"],
                        "Europe/Paris": ["Miami,Buffalo"],
                        "North_America/Ottawa": ["Salt Lake City,New York,Phoenix"],
                        "North_America/Havana": ["Phoenix,Seattle"],
                    }

                    def initialize_VPN(area_input):
                        stored_settings = 0
                        save = 0
                        skip_settings = 0

                        ###load stored settings if needed and set input_needed variables to zero if settings are provided###
                        windows_pause = 3
                        additional_settings_needed = 1
                        additional_settings_list = list()

                        input_needed = 2
                        windows_pause = 8
            

                        ###performing system check###
                        opsys = platform.system()

                        ##windows##
                        if opsys == "Windows":
                            # print("\33[33mYou're using Windows.\n"
                            #       "Performing system check...\n"
                            #       "###########################\n\33[0m")
                            #diretorio_script = os.path.dirname(os.path.abspath(__file__))
                            #option_2_path = os.path.join(diretorio_script, 'NordVPN')
                            #option_1_path = os.path.join(diretorio_script, 'NordVPN')
                            option_1_path = 'C:/Program Files/NordVPN'
                            option_2_path = 'C:/Program Files (x86)/NordVPN'
                            custom_path = str()
                            if path.exists(option_1_path) == True:
                                cwd_path = option_1_path
                            elif path.exists(option_2_path) == True:
                                cwd_path = option_2_path
                            else:
                                custom_path = input("\x1b[93mIt looks like you've installed NordVPN in an uncommon folder. Would you mind telling me which folder? (e.g. D:/customfolder/nordvpn)\x1b[0m")
                                while path.exists(custom_path) == False:
                                    custom_path = input("\x1b[93mI'm sorry, but this folder doesn't exist. Please double-check your input.\x1b[0m")
                                while os.path.isfile(custom_path+"/NordVPN.exe") == False:
                                    custom_path = input("\x1b[93mI'm sorry, but the NordVPN application is not located in this folder. Please double-check your input.\x1b[0m")
                                cwd_path = custom_path
                            #print("NordVPN installation check: \33[92m\N{check mark}\33[0m")

                            #check if nordvpn service is already running in the background
                            check_service = "nordvpn-service.exe" in (p.name() for p in psutil.process_iter())
                            if check_service is False:
                                raise Exception("NordVPN service hasn't been initialized, please start this service in [task manager] --> [services] and restart your script")
                            #print("NordVPN service check: \33[92m\N{check mark}\33[0m")

                            # start NordVPN app and disconnect from VPN service if necessary#
                            #print("Opening NordVPN app and disconnecting if necessary...")
                            open_nord_win = subprocess.Popen(["nordvpn", "-d"],shell=True,cwd=cwd_path,stdout=DEVNULL)
                            while ("NordVPN.exe" in (p.name() for p in psutil.process_iter())) == False:
                                time.sleep(windows_pause)
                            open_nord_win.kill()
                            #print(": \33[92m\N{check mark}\33[0m")
                            #print("#####################################")
                            self.location.emit(f"NordVPN app launched.")

                        else:
                            raise Exception("I'm sorry, NordVPN switcher only works for Windows and Linux machines.")

                        diretorio_script = os.path.dirname(os.path.abspath(__file__))

                        file_path = os.path.join(diretorio_script,'config', 'countrylist.txt')

                        with open(file_path, 'r') as file:
                            areas_list = file.read().split('\n')
                            country_dict = {'countries':areas_list[0:60],'europe': areas_list[0:36], 'americas': areas_list[36:44],
                                            'africa east india': areas_list[49:60],'asia pacific': areas_list[49:60],
                                            'regions australia': areas_list[60:65],'regions canada': areas_list[65:68],
                                            'regions germany': areas_list[68:70], 'regions india': areas_list[70:72],
                                            'regions united states': areas_list[72:87],'special groups':areas_list[87:len(areas_list)]}

                        ##provide input if needed##
                        flag = False
                        while input_needed > 0:
                            if input_needed == 2:
                                self.location.emit(f"You've entered a list of connection options. Checking list...")
                
                                try:
                                    settings_servers = [area.lower() for area in area_input]
                                    settings_servers = ",".join(settings_servers)
                                except TypeError:
                                    raise Exception("I expected a list here. Are you sure you've not entered a string or some other object?\n ")

                            else:
                                if area_input == 'complete rotation':
                                    settings_servers = 'complete rotation'
                                
                            if opsys == "Windows":
                                nordvpn_command = ["nordvpn", "-c"]
                            if opsys == "Linux":
                                nordvpn_command = ["nordvpn", "c"]
                            #create sample of regions from input.#
                            #1. if quick connect#
                            if settings_servers == "quick":
                                if input_needed == 1:
                                    quickconnect_check = input("\nYou are choosing for the quick connect option. Are you sure? (y/n)\n")
                                    if 'y' in quickconnect_check:
                                        sample_countries = [""]
                                        input_needed = 0
                                        pass
                                if input_needed == 2:
                                    sample_countries = [""]
                                    input_needed = 0
                                else:
                                    print("\nYou are choosing for the quick connect option.\n")
                            #2. if completely random rotation
                            elif settings_servers == 'complete rotation':
                                print("\nFetching list of all current NordVPN servers...\n")
                                for i in range(120):
                                    try:
                                        filtered_servers = get_nordvpn_servers()
                                        if opsys == "Windows":
                                            nordvpn_command.append("-n")
                                            sample_countries = filtered_servers['windows_names']
                                        else:
                                            sample_countries = filtered_servers['linux_names']
                                    except:
                                        time.sleep(0.5)
                                        continue
                                    else:
                                        input_needed = 0
                                        break
                                else:
                                    raise Exception("\nI'm unable to fetch the current NordVPN serverlist. Check your internet connection.\n")
                            
                            #3. if provided specific servers. Notation differs for Windows and Linux machines, so two options are checked (first is Windows, second is Linux#
                            elif "#" in settings_servers or re.compile(r'^[a-zA-Z]+[0-9]+').search(settings_servers.split(',')[0]) is not None:
                                if opsys == "Windows":
                                    nordvpn_command.append("-n")
                                sample_countries = [area.strip() for area in settings_servers.split(',')]
                                input_needed = 0
                            else:
                                #3. If connecting to some specific group of servers#
                                if opsys == "Windows":
                                    nordvpn_command.append("-g")
                                #3.1 if asked for random sample, pull a sample.#
                                if "random" in settings_servers:
                                    #determine sample size#
                                    samplesize = int(re.sub("[^0-9]", "", settings_servers).strip())
                                    #3.1.1 if asked for random regions within country (e.g. random regions from United States,Australia,...)#
                                    if "regions" in settings_servers:
                                        try:
                                            sample_countries = country_dict[re.sub("random", "", settings_servers).rstrip('0123456789.- ').lower().strip()]
                                            input_needed = 0
                                        except:
                                            input("\n\nThere are no specific regions available in this country, please try again.\nPress enter to continue.\n")
                                            if input_needed == 2:
                                                input_needed = 1
                                                continue
                                        if re.compile(r'[^0-9]').search(settings_servers.strip()):
                                            sample_countries = random.sample(sample_countries, samplesize)
                                    #3.1.2 if asked for random countries within larger region#
                                    elif any(re.findall(r'europe|americas|africa east india|asia pacific', settings_servers)):
                                        larger_region = country_dict[re.sub("random|countries", "", settings_servers).rstrip('0123456789.- ').lower().strip()]
                                        sample_countries = random.sample(larger_region,samplesize)
                                        input_needed = 0
                                    #3.1.3 if asked for random countries globally#
                                    else:
                                        if re.compile(r'[^0-9]').search(settings_servers.strip()):
                                            sample_countries = random.sample(country_dict['countries'], samplesize)
                                            input_needed = 0
                                        else:
                                            sample_countries = country_dict['countries']
                                            input_needed = 0
                                #4. If asked for specific region (e.g. europe)#
                                elif settings_servers in country_dict.keys():
                                    sample_countries = country_dict[settings_servers]
                                    input_needed = 0
                                #5. If asked for specific countries or regions (e.g.netherlands)#
                                else:
                                    #check for empty input first.#
                                    if settings_servers == "":
                                        input("\n\nYou must provide some kind of input.\nPress enter to continue and then type 'help' to view the available options.\n")
                                        if input_needed == 2:
                                            input_needed = 1
                                            continue
                                    else:
                                        sample_countries = [area.strip() for area in settings_servers.split(',')] #take into account possible superfluous spaces#
                                        approved_regions = 0
                                        for region in sample_countries:
                                            if region in [area.lower() for area in areas_list]:
                                                approved_regions = approved_regions + 1
                                                pass
                                            else:
                                                #input("\n\nThe region/group " + region + " is not available. Please check for spelling errors.\nPress enter to continue.\n")
                                                if input_needed == 2:
                                                    input_needed = 1
                                                    continue
                                        if approved_regions == len(sample_countries):
                                            input_needed = 0

                        ##fetch current ip to prevent ip leakage when rotating VPN##
                        for i in range(59):
                            if flag == True:
                                break
                            try:
                                og_ip = get_ip()
                            except ConnectionAbortedError:
                                time.sleep(1)
                                continue
                            else:
                                break
                        else:
                            raise Exception("Can't fetch current ip, even after retrying... Check your internet connection.")

                        ##if user does not use preloaded settings##
                        if "instructions" not in locals():
                            #1.add underscore if spaces are present on Linux os#
                            for number,element in enumerate(sample_countries):
                                if element.count(" ") > 0 and opsys == "Linux":
                                        sample_countries[number] = re.sub(" ","_",element)
                            else:
                                pass
                            #2.create instructions dict object#
                            instructions = {'opsys':opsys,'command':nordvpn_command,'settings':sample_countries,'original_ip':og_ip}
                            if opsys == "Windows":
                                instructions['cwd_path'] = cwd_path

                            #3.save the settings if requested into .txt file in project folder#
                            if save == 1:
                                print("\nSaving settings in project folder...\n")
                                try:
                                    os.remove("settings_nordvpn.txt")
                                except FileNotFoundError:
                                    pass
                                instructions_write = json.dumps(instructions)
                                f = open("settings_nordvpn.txt", "w")
                                f.write(instructions_write)
                                f.close()

                        self.location.emit(f"Nord Done!")
                        return instructions

                    def rotate_ip_nord(vpn_instruction):

                        instructions = vpn_instruction
                        google_check = 0
                        if instructions is None:
                            instructions = saved_settings_check()

                        opsys = instructions['opsys']
                        command = instructions['command']
                        settings = instructions['settings']
                        og_ip = instructions['original_ip']

                        if opsys == "Windows":
                            cwd_path = instructions['cwd_path']

                        for i in range(2):
                            try:
                                current_ip = new_ip = get_ip()
                            except urllib.error.URLError:
                                self.location.emit(f"Nord Can't fetch current ip. Retrying...")
                            
                                time.sleep(10)
                                continue
                            else:
                                self.location.emit(f"Nord Your current ip-address is: {current_ip}")

                                time.sleep(2)
                                break
                        else:
                            self.location.emit(f"Nord Can't fetch current ip, even after retrying... Check your internet connection.")
                            

                        for i in range(5):
                            if len(settings) > 1:
                                settings_pick = list([random.choice(settings)])
                            else:
                                settings_pick = settings

                            input = command + settings_pick

                            if settings[0] == "":
                                print("\nConnecting you to the best possible server (quick connect option)...")
                            else:
                                self.location.emit(f"Nord Connecting: {settings_pick[0]}")
                                    

                
                            try:
                                if opsys == "Windows":
                                    new_connection = subprocess.Popen(input, shell=True, cwd=cwd_path)
                                    new_connection.wait(220)
                                else:
                                    new_connection = check_output(input)
                                    print("Found a server! You're now on "+re.search('(?<=You are connected to )(.*)(?=\()', str(new_connection))[0].strip())
                            except:
                                self.location.emit(f"An unknown error occurred")

                                

                            for i in range(12):
                                try:
                                    new_ip = get_ip()
                                except:
                                    time.sleep(5)
                                    continue
                                else:
                                    if new_ip in [current_ip,og_ip]:
                                        time.sleep(5)
                                        continue
                                    else:
                                        break
                            else:
                                pass

                            if new_ip in [current_ip,og_ip]:
                                self.location.emit("Nord ip-address hasn't changed. Retrying...\n")
                                time.sleep(10)
                                continue
                            else:
                                self.location.emit(f"Nord Conected! Enjoy your new server.")
                                time.sleep(3)


                            if google_check == 1:
                                print("\n\33[33mPerforming captcha-check on Google search and Youtube...\n"
                                    "---------------------------\33[0m")
                                try:
                                    google_search_check = BeautifulSoup(
                                        requests.get("https://www.google.be/search?q=why+is+python+so+hard").content,"html.parser")
                                    youtube_video_check = BeautifulSoup(
                                        requests.get("https://www.youtube.com/watch?v=dQw4w9WgXcQ").content,"html.parser")

                                    google_captcha = google_search_check.find('div',id="recaptcha")
                                    youtube_captcha = youtube_video_check.find('div', id = "recaptcha")

                                    if None not in (google_captcha,youtube_captcha):
                                        print("Google throws a captcha. I'll pick a different server...")
                                        time.sleep(5)
                                        continue
                                except:
                                    print("Can't load Google page. I'll pick a different server...")
                                    time.sleep(5)
                                    continue
                                else:
                                    print("Google and YouTube don't throw any Captcha's: \33[92m\N{check mark}\33[0m")
                                    break
                            else:
                                break


                    if self.vpnwinds:
                        windsarg = 'windscribe'
                    else:
                        windsarg = 'none'

                    if self.vpnnord:
                        nordarg = 'nord_vpn'
                    else:
                        nordarg = 'none'

                    if self.vpnpia:
                        piaarg = 'pia_vpn'
                    else:
                        piaarg = 'none'

                    if self.vpnexpress:
                        expressarg = 'express_vpn' 
                    else:
                        expressarg = 'none'

                    if self.vpnmullvad:
                        mullvadarg = 'mullvad'
                    else:
                        mullvadarg = 'none'

                    if self.IVPNcheckBox:
                        ivpnarg = 'ivpn'
                    else:
                        ivpnarg = 'none'

                    vpns_de_exscolha = [
                        windsarg,
                        nordarg,
                        expressarg, 
                        mullvadarg,
                        piaarg,
                        ivpnarg
                    ]
                    selecionador = Balanceamento_de_vpn(vpns_de_exscolha)


                    vpn_selecionada = selecionador.selecionar()

                    if vpn_selecionada == 'windscribe':
                        print(F"Rotacionar com a Windscribe")    
                        disconnectx_mullvad = disconnect_mullvad()
                        if disconnectx_mullvad == True:
                            print("VPN Mullvad DISCONNECT") 

                        express_disconect = disconnect_express()    
                        if express_disconect == True:
                            print(F"VPN EXPRESS DISCONNECT")
                                
                        pia__disconect = pia_disconnect()    
                        if pia__disconect == True:
                            print(F"VPN PIA DISCONNECT")

                        try:
                            option_1_path = 'C:/Program Files/NordVPN'
                            subprocess.Popen(["nordvpn", "-d"],shell=True,cwd=option_1_path,stdout=DEVNULL)
                            print("VPN NORD DISCONNECT")    
                        except:
                            pass 
                        
                        time.sleep(5)
                        for _ in range(self.rotation_count_per_vpn):
                                        
                            location = area_input_vpn   
                            vpn2 = rotate_ip_windscribe(location)
                            if vpn2 == True:
                                self.benchmark_data['time_spent'] += time.time() - start_time
                                self.update_benchmark_data()
                                
                    if vpn_selecionada == 'nord_vpn':
                        print(F"Rotacionar com a nord")   

                        disconnectx_mullvad = disconnect_mullvad()
                        if disconnectx_mullvad == True:
                            print("VPN Mullvad DISCONNECT") 

                        express_disconect = disconnect_express()    
                        if express_disconect == True:
                            print(F"VPN EXPRESS DISCONNECT")

                        WINDSCRIBE_disconect = disconnect_WINDSCRIBE('disconnect')    
                        if WINDSCRIBE_disconect == True:
                            print(F"VPN WINDSCRIBE DISCONNECT")
                                
                        pia__disconect = pia_disconnect()    
                        if pia__disconect == True:
                            print(F"VPN PIA DISCONNECT")


                        
                        time.sleep(15)
                        for _ in range(self.rotation_count_per_vpn):
                                    
                            timezone = random.choice(list(vpn_options.keys()))
                            vpn_options_for_timezone = vpn_options.get(timezone, [])
                            vpn_option = random.choice(vpn_options_for_timezone)
                            print(vpn_options_for_timezone)
                            print(vpn_option)
                            self.location.emit(f'{[vpn_option]}')
                            vpn_instruction = initialize_VPN(area_input=[vpn_option])
                            rotate_ip_nord(vpn_instruction)
                            self.benchmark_data['time_spent'] += time.time() - start_time
                            self.update_benchmark_data()
                    
                    if vpn_selecionada == 'mullvad':

                        print(F"Rotacionar com a mullvad") 

                        express_disconect = disconnect_express()    
                        if express_disconect == True:
                            print(F"VPN EXPRESS DISCONNECT")

                        WINDSCRIBE_disconect = disconnect_WINDSCRIBE('disconnect')    
                        if WINDSCRIBE_disconect == True:
                            print(F"VPN WINDSCRIBE DISCONNECT")
                                
                        pia__disconect = pia_disconnect()    
                        if pia__disconect == True:
                            print(F"VPN PIA DISCONNECT")

                        try:
                            option_1_path = 'C:/Program Files/NordVPN'
                            subprocess.Popen(["nordvpn", "-d"],shell=True,cwd=option_1_path,stdout=DEVNULL)
                            print("VPN NORD DISCONNECT")    
                        except:
                            pass 


                        time.sleep(5)
                        for _ in range(self.rotation_count_per_vpn):
                                    
                            location = area_input_vpn  
                            vpn2 = rotate_ip_mullvad(location)
                            if vpn2 == True:
                                self.benchmark_data['time_spent'] += time.time() - start_time
                                self.update_benchmark_data()
                                    
                    if vpn_selecionada == 'pia_vpn':

                        print(F"Rotacionar com a pia") 

                        disconnectx_mullvad = disconnect_mullvad()
                        if disconnectx_mullvad == True:
                            print("VPN Mullvad DISCONNECT") 

                        express_disconect = disconnect_express()    
                        if express_disconect == True:
                            print(F"VPN EXPRESS DISCONNECT")

                        WINDSCRIBE_disconect = disconnect_WINDSCRIBE('disconnect')    
                        if WINDSCRIBE_disconect == True:
                            print(F"VPN WINDSCRIBE DISCONNECT")
                                
                        try:
                            option_1_path = 'C:/Program Files/NordVPN'
                            subprocess.Popen(["nordvpn", "-d"],shell=True,cwd=option_1_path,stdout=DEVNULL)
                            print("VPN NORD DISCONNECT")    
                        except:
                            pass 

                        time.sleep(5)
                        for _ in range(self.rotation_count_per_vpn):
                                
                            location = area_input_vpn
                            vpn2 = rotate_ip_pia(location)
                            if vpn2 == True:
                                self.benchmark_data['time_spent'] += time.time() - start_time
                                self.update_benchmark_data()

                    if vpn_selecionada == 'express_vpn':

                        print(F"Rotacionar com a Express") 

                        disconnectx_mullvad = disconnect_mullvad()
                        if disconnectx_mullvad == True:
                            print("VPN Mullvad DISCONNECT") 

                        WINDSCRIBE_disconect = disconnect_WINDSCRIBE('disconnect')    
                        if WINDSCRIBE_disconect == True:
                            print(F"VPN WINDSCRIBE DISCONNECT")
                                
                        pia__disconect = pia_disconnect()    
                        if pia__disconect == True:
                            print(F"VPN PIA DISCONNECT")

                        try:
                            option_1_path = 'C:/Program Files/NordVPN'
                            subprocess.Popen(["nordvpn", "-d"],shell=True,cwd=option_1_path,stdout=DEVNULL)
                            print("VPN NORD DISCONNECT")    
                        except:
                            pass 
                        for _ in range(self.rotation_count_per_vpn):
                                    
                            location = area_input_vpn        
                            rotate_ip_express2 = rotate_ip_express(location)        
                            if rotate_ip_express2 == True:    
                                self.benchmark_data['time_spent'] += time.time() - start_time
                                self.update_benchmark_data()
                    
                    if vpn_selecionada == 'ivpn':

                        print(F"Rotacionar com a ivpn") 

                        express_disconect = disconnect_express()    
                        if express_disconect == True:
                            print(F"VPN EXPRESS DISCONNECT")

                        disconnectx_mullvad = disconnect_mullvad()
                        if disconnectx_mullvad == True:
                            print("VPN Mullvad DISCONNECT") 

                        WINDSCRIBE_disconect = disconnect_WINDSCRIBE('disconnect')    
                        if WINDSCRIBE_disconect == True:
                            print(F"VPN WINDSCRIBE DISCONNECT")
                                
                        pia__disconect = pia_disconnect()    
                        if pia__disconect == True:
                            print(F"VPN PIA DISCONNECT")

                        try:
                            option_1_path = 'C:/Program Files/NordVPN'
                            subprocess.Popen(["nordvpn", "-d"],shell=True,cwd=option_1_path,stdout=DEVNULL)
                            print("VPN NORD DISCONNECT")    
                        except:
                            pass 
                        for _ in range(self.rotation_count_per_vpn):
                                    
                            location = area_input_vpn        
                            rrotate_ip_ivpn2 = rotate_ip_ivpn(location)        
                            if rrotate_ip_ivpn2 == True:    
                                self.benchmark_data['time_spent'] += time.time() - start_time
                                self.update_benchmark_data()
                        


                    for _ in range(self.interval):
                        if not self._is_running:
                            desativar_todas_vpns()
                            self.location.emit(f"M-T-V-A-R Stop")
                            break
                        time.sleep(1)



                if self.rotate_in_canada:    
                    area_input_vpn = 'complete_rotate_in_canada'

                    def rotate_ip_mullvad(area_input):
                        
                        #time.sleep(5)
                        LISTA = []
                        lista_de_server = []
                        for i in range(12):
                            try:
                                original_ip, cidade, regiao, pais, fuso_horario, organizacao = get_monitor()
                                
                                LISTA.append(original_ip)
                            except ConnectionAbortedError:
                                time.sleep(1)
                                continue
                            else:
                                break
                        for i in range(12):
                            try:
                                time.sleep(5)
                                location = lists_rotate_mullvad(area_input)
                                #lista_de_server.append(location)
                                #location_flag_teste = lista_de_server.pop(0)
                                self.location.emit(f"Mullvad Connect in: {location}")
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
                                        
                                        self.location.emit(f"Mullvad New ip: {t2}, Region: {regiao}")
                            
                                        return True
                            except Exception as e:
                                print(e)
                                time.sleep(5)
                                #break
                    
                    def rotate_ip_windscribe(area_input):
                        
                        #time.sleep(5)
                        LISTA = []
                        lista_de_server = []
                        for i in range(12):
                            try:
                                original_ip, cidade, regiao, pais, fuso_horario, organizacao = get_monitor()
                                
                                LISTA.append(original_ip)
                            except ConnectionAbortedError:
                                time.sleep(1)
                                continue
                            else:
                                break
                        for i in range(12):
                            try:
                                time.sleep(5)
                                location = lists_rotate_windscribe(area_input)
                                #lista_de_server.append(location)
                                #location_flag_teste = lista_de_server.pop(0)
                                self.location.emit(f"Windscribe Connect in: {location}")
                                vpn2 = windscribe_rotation_by_usa("connect", location)
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
                                        
                                        self.location.emit(f"Windscribe New ip: {t2}, Region: {regiao}")
                            
                                        return True
                            except Exception as e:
                                print(e)
                                time.sleep(5)
                                #break
                    
                    def rotate_ip_express(area_input):
                        
                        #time.sleep(5)
                        LISTA = []
                        lista_de_server = []
                        for i in range(12):
                            try:
                                original_ip, cidade, regiao, pais, fuso_horario, organizacao = get_monitor()
                                
                                LISTA.append(original_ip)
                            except ConnectionAbortedError:
                                time.sleep(1)
                                continue
                            else:
                                break
                        for i in range(12):
                            try:
                                time.sleep(5)
                                location = lists_rotate_express_vpn(area_input)
                                #lista_de_server.append(location)
                                #location_flag_teste = lista_de_server.pop(0)
                                self.location.emit(f"Express Connect in: {location}")
                                vpn2 = express_rotation(location)
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
                                        
                                        self.location.emit(f"Express Retrying.")
                                        continue
                                    else:
                                        #server = lista_de_server.pop(0)
                                        
                                        self.location.emit(f"Express New ip: {t2}, Region: {regiao}")
                            
                                        return True
                            except Exception as e:
                                print(e)
                                time.sleep(5)
                                #break
                    
                    def rotate_ip_pia(area_input):
                        
                        #time.sleep(5)
                        LISTA = []
                        lista_de_server = []
                        for i in range(12):
                            try:
                                original_ip, cidade, regiao, pais, fuso_horario, organizacao = get_monitor()
                                
                                LISTA.append(original_ip)
                            except ConnectionAbortedError:
                                time.sleep(1)
                                continue
                            else:
                                break
                        for i in range(12):
                            try:
                                time.sleep(5)
                                location = lists_rotate_pia(area_input)
                                #lista_de_server.append(location)
                                #location_flag_teste = lista_de_server.pop(0)
                                self.location.emit(f"PIA Connect in: {location}")
                                vpn2 = pia_rotation(location)
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
                                        
                                        self.location.emit(f"PIA Retrying.")
                                        continue
                                    else:
                                        #server = lista_de_server.pop(0)
                                        
                                        self.location.emit(f"PIA New ip: {t2}, Region: {regiao}")
                            
                                        return True
                            except Exception as e:
                                print(e)
                                time.sleep(5)
                                #break
                    
                    def rotate_ip_ivpn(area_input):
                        
                        #time.sleep(5)
                        LISTA = []
                        lista_de_server = []
                        for i in range(12):
                            try:
                                original_ip, cidade, regiao, pais, fuso_horario, organizacao = get_monitor()
                                self.location.emit(f"i-v-a-r init")
                                LISTA.append(original_ip)
                            except ConnectionAbortedError:
                                time.sleep(1)
                                continue
                            else:
                                break
                        for i in range(12):
                            try:
                                time.sleep(5)
                                location = lists_rotateivpn(area_input)
                                #lista_de_server.append(location)
                                #location_flag_teste = lista_de_server.pop(0)
                                self.location.emit(f"Connect in: {location}")
                                vpn2 = ivpn_rotation(location)
                                if not self._is_running:
                                    ivpndisconnect()
                                    self.location.emit(f"I-V-A-R Stop")
                                    break

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

                    vpn_options = {
                        "America/New_York": ["New York,Manassas"],
                        "America/Chicago": ["Chicago,Saint Louis"],
                        "America/Denver": ["Denver,Chicago"],
                        "America/Los_Angeles": ["Los Angeles,Phoenix"],
                        "America/Seattle": ["Seattle,Chicago"],
                        "America/Salt_Lake_City": ["Chicago,Denver"],
                        "America/San_Francisco": ["San Francisco,Los Angeles"],
                        "America/Dallas": ["Dallas,Chicago"],
                        "America/Kansas_City": ["Chicago,Saint Louis"],
                        "America/Saint_Louis": ["Saint Louis,Dallas"],
                        "America/Atlanta": ["Atlanta,Charlotte"],
                        "America/Charlotte": ["Charlotte,Manassas,New York"],
                        "America/Miami": ["Miami,Atlanta,Charlotte"],
                        "America/Manassas": ["Manassas,New York"],
                        "America/Buffalo": ["Buffalo,New York"],
                        "America/Phoenix": ["Phoenix,Los Angeles"],
                        "America/Toronto": ["Toronto,Buffalo"],
                        "America/Vancouver": ["Atlanta,Seattle"],
                        "Europe/Paris": ["Miami,Buffalo"],
                        "North_America/Ottawa": ["Salt Lake City,New York,Phoenix"],
                        "North_America/Havana": ["Phoenix,Seattle"],
                    }

                    def initialize_VPN(area_input):
                        stored_settings = 0
                        save = 0
                        skip_settings = 0

                        ###load stored settings if needed and set input_needed variables to zero if settings are provided###
                        windows_pause = 3
                        additional_settings_needed = 1
                        additional_settings_list = list()

                        input_needed = 2
                        windows_pause = 8
            

                        ###performing system check###
                        opsys = platform.system()

                        ##windows##
                        if opsys == "Windows":
                            # print("\33[33mYou're using Windows.\n"
                            #       "Performing system check...\n"
                            #       "###########################\n\33[0m")
                            #diretorio_script = os.path.dirname(os.path.abspath(__file__))
                            #option_2_path = os.path.join(diretorio_script, 'NordVPN')
                            #option_1_path = os.path.join(diretorio_script, 'NordVPN')
                            option_1_path = 'C:/Program Files/NordVPN'
                            option_2_path = 'C:/Program Files (x86)/NordVPN'
                            custom_path = str()
                            if path.exists(option_1_path) == True:
                                cwd_path = option_1_path
                            elif path.exists(option_2_path) == True:
                                cwd_path = option_2_path
                            else:
                                custom_path = input("\x1b[93mIt looks like you've installed NordVPN in an uncommon folder. Would you mind telling me which folder? (e.g. D:/customfolder/nordvpn)\x1b[0m")
                                while path.exists(custom_path) == False:
                                    custom_path = input("\x1b[93mI'm sorry, but this folder doesn't exist. Please double-check your input.\x1b[0m")
                                while os.path.isfile(custom_path+"/NordVPN.exe") == False:
                                    custom_path = input("\x1b[93mI'm sorry, but the NordVPN application is not located in this folder. Please double-check your input.\x1b[0m")
                                cwd_path = custom_path
                            #print("NordVPN installation check: \33[92m\N{check mark}\33[0m")

                            #check if nordvpn service is already running in the background
                            check_service = "nordvpn-service.exe" in (p.name() for p in psutil.process_iter())
                            if check_service is False:
                                raise Exception("NordVPN service hasn't been initialized, please start this service in [task manager] --> [services] and restart your script")
                            #print("NordVPN service check: \33[92m\N{check mark}\33[0m")

                            # start NordVPN app and disconnect from VPN service if necessary#
                            #print("Opening NordVPN app and disconnecting if necessary...")
                            open_nord_win = subprocess.Popen(["nordvpn", "-d"],shell=True,cwd=cwd_path,stdout=DEVNULL)
                            while ("NordVPN.exe" in (p.name() for p in psutil.process_iter())) == False:
                                time.sleep(windows_pause)
                            open_nord_win.kill()
                            #print(": \33[92m\N{check mark}\33[0m")
                            #print("#####################################")
                            self.location.emit(f"NordVPN app launched.")

                        else:
                            raise Exception("I'm sorry, NordVPN switcher only works for Windows and Linux machines.")

                        diretorio_script = os.path.dirname(os.path.abspath(__file__))

                        file_path = os.path.join(diretorio_script,'config', 'countrylist.txt')

                        with open(file_path, 'r') as file:
                            areas_list = file.read().split('\n')
                            country_dict = {'countries':areas_list[0:60],'europe': areas_list[0:36], 'americas': areas_list[36:44],
                                            'africa east india': areas_list[49:60],'asia pacific': areas_list[49:60],
                                            'regions australia': areas_list[60:65],'regions canada': areas_list[65:68],
                                            'regions germany': areas_list[68:70], 'regions india': areas_list[70:72],
                                            'regions united states': areas_list[72:87],'special groups':areas_list[87:len(areas_list)]}

                        ##provide input if needed##
                        flag = False
                        while input_needed > 0:
                            if input_needed == 2:
                                self.location.emit(f"You've entered a list of connection options. Checking list...")
                
                                try:
                                    settings_servers = [area.lower() for area in area_input]
                                    settings_servers = ",".join(settings_servers)
                                except TypeError:
                                    raise Exception("I expected a list here. Are you sure you've not entered a string or some other object?\n ")

                            else:
                                if area_input == 'complete rotation':
                                    settings_servers = 'complete rotation'
                                
                            if opsys == "Windows":
                                nordvpn_command = ["nordvpn", "-c"]
                            if opsys == "Linux":
                                nordvpn_command = ["nordvpn", "c"]
                            #create sample of regions from input.#
                            #1. if quick connect#
                            if settings_servers == "quick":
                                if input_needed == 1:
                                    quickconnect_check = input("\nYou are choosing for the quick connect option. Are you sure? (y/n)\n")
                                    if 'y' in quickconnect_check:
                                        sample_countries = [""]
                                        input_needed = 0
                                        pass
                                if input_needed == 2:
                                    sample_countries = [""]
                                    input_needed = 0
                                else:
                                    print("\nYou are choosing for the quick connect option.\n")
                            #2. if completely random rotation
                            elif settings_servers == 'complete rotation':
                                print("\nFetching list of all current NordVPN servers...\n")
                                for i in range(120):
                                    try:
                                        filtered_servers = get_nordvpn_servers()
                                        if opsys == "Windows":
                                            nordvpn_command.append("-n")
                                            sample_countries = filtered_servers['windows_names']
                                        else:
                                            sample_countries = filtered_servers['linux_names']
                                    except:
                                        time.sleep(0.5)
                                        continue
                                    else:
                                        input_needed = 0
                                        break
                                else:
                                    raise Exception("\nI'm unable to fetch the current NordVPN serverlist. Check your internet connection.\n")
                            
                            #3. if provided specific servers. Notation differs for Windows and Linux machines, so two options are checked (first is Windows, second is Linux#
                            elif "#" in settings_servers or re.compile(r'^[a-zA-Z]+[0-9]+').search(settings_servers.split(',')[0]) is not None:
                                if opsys == "Windows":
                                    nordvpn_command.append("-n")
                                sample_countries = [area.strip() for area in settings_servers.split(',')]
                                input_needed = 0
                            else:
                                #3. If connecting to some specific group of servers#
                                if opsys == "Windows":
                                    nordvpn_command.append("-g")
                                #3.1 if asked for random sample, pull a sample.#
                                if "random" in settings_servers:
                                    #determine sample size#
                                    samplesize = int(re.sub("[^0-9]", "", settings_servers).strip())
                                    #3.1.1 if asked for random regions within country (e.g. random regions from United States,Australia,...)#
                                    if "regions" in settings_servers:
                                        try:
                                            sample_countries = country_dict[re.sub("random", "", settings_servers).rstrip('0123456789.- ').lower().strip()]
                                            input_needed = 0
                                        except:
                                            input("\n\nThere are no specific regions available in this country, please try again.\nPress enter to continue.\n")
                                            if input_needed == 2:
                                                input_needed = 1
                                                continue
                                        if re.compile(r'[^0-9]').search(settings_servers.strip()):
                                            sample_countries = random.sample(sample_countries, samplesize)
                                    #3.1.2 if asked for random countries within larger region#
                                    elif any(re.findall(r'europe|americas|africa east india|asia pacific', settings_servers)):
                                        larger_region = country_dict[re.sub("random|countries", "", settings_servers).rstrip('0123456789.- ').lower().strip()]
                                        sample_countries = random.sample(larger_region,samplesize)
                                        input_needed = 0
                                    #3.1.3 if asked for random countries globally#
                                    else:
                                        if re.compile(r'[^0-9]').search(settings_servers.strip()):
                                            sample_countries = random.sample(country_dict['countries'], samplesize)
                                            input_needed = 0
                                        else:
                                            sample_countries = country_dict['countries']
                                            input_needed = 0
                                #4. If asked for specific region (e.g. europe)#
                                elif settings_servers in country_dict.keys():
                                    sample_countries = country_dict[settings_servers]
                                    input_needed = 0
                                #5. If asked for specific countries or regions (e.g.netherlands)#
                                else:
                                    #check for empty input first.#
                                    if settings_servers == "":
                                        input("\n\nYou must provide some kind of input.\nPress enter to continue and then type 'help' to view the available options.\n")
                                        if input_needed == 2:
                                            input_needed = 1
                                            continue
                                    else:
                                        sample_countries = [area.strip() for area in settings_servers.split(',')] #take into account possible superfluous spaces#
                                        approved_regions = 0
                                        for region in sample_countries:
                                            if region in [area.lower() for area in areas_list]:
                                                approved_regions = approved_regions + 1
                                                pass
                                            else:
                                                #input("\n\nThe region/group " + region + " is not available. Please check for spelling errors.\nPress enter to continue.\n")
                                                if input_needed == 2:
                                                    input_needed = 1
                                                    continue
                                        if approved_regions == len(sample_countries):
                                            input_needed = 0

                        ##fetch current ip to prevent ip leakage when rotating VPN##
                        for i in range(59):
                            if flag == True:
                                break
                            try:
                                og_ip = get_ip()
                            except ConnectionAbortedError:
                                time.sleep(1)
                                continue
                            else:
                                break
                        else:
                            raise Exception("Can't fetch current ip, even after retrying... Check your internet connection.")

                        ##if user does not use preloaded settings##
                        if "instructions" not in locals():
                            #1.add underscore if spaces are present on Linux os#
                            for number,element in enumerate(sample_countries):
                                if element.count(" ") > 0 and opsys == "Linux":
                                        sample_countries[number] = re.sub(" ","_",element)
                            else:
                                pass
                            #2.create instructions dict object#
                            instructions = {'opsys':opsys,'command':nordvpn_command,'settings':sample_countries,'original_ip':og_ip}
                            if opsys == "Windows":
                                instructions['cwd_path'] = cwd_path

                            #3.save the settings if requested into .txt file in project folder#
                            if save == 1:
                                print("\nSaving settings in project folder...\n")
                                try:
                                    os.remove("settings_nordvpn.txt")
                                except FileNotFoundError:
                                    pass
                                instructions_write = json.dumps(instructions)
                                f = open("settings_nordvpn.txt", "w")
                                f.write(instructions_write)
                                f.close()

                        self.location.emit(f"Nord Done!")
                        return instructions

                    def rotate_ip_nord(vpn_instruction):

                        instructions = vpn_instruction
                        google_check = 0
                        if instructions is None:
                            instructions = saved_settings_check()

                        opsys = instructions['opsys']
                        command = instructions['command']
                        settings = instructions['settings']
                        og_ip = instructions['original_ip']

                        if opsys == "Windows":
                            cwd_path = instructions['cwd_path']

                        for i in range(2):
                            try:
                                current_ip = new_ip = get_ip()
                            except urllib.error.URLError:
                                self.location.emit(f"Nord Can't fetch current ip. Retrying...")
                            
                                time.sleep(10)
                                continue
                            else:
                                self.location.emit(f"Nord Your current ip-address is: {current_ip}")

                                time.sleep(2)
                                break
                        else:
                            self.location.emit(f"Nord Can't fetch current ip, even after retrying... Check your internet connection.")
                            

                        for i in range(5):
                            if len(settings) > 1:
                                settings_pick = list([random.choice(settings)])
                            else:
                                settings_pick = settings

                            input = command + settings_pick

                            if settings[0] == "":
                                print("\nConnecting you to the best possible server (quick connect option)...")
                            else:
                                self.location.emit(f"Nord Connecting: {settings_pick[0]}")
                                    

                
                            try:
                                if opsys == "Windows":
                                    new_connection = subprocess.Popen(input, shell=True, cwd=cwd_path)
                                    new_connection.wait(220)
                                else:
                                    new_connection = check_output(input)
                                    print("Found a server! You're now on "+re.search('(?<=You are connected to )(.*)(?=\()', str(new_connection))[0].strip())
                            except:
                                self.location.emit(f"An unknown error occurred")

                                

                            for i in range(12):
                                try:
                                    new_ip = get_ip()
                                except:
                                    time.sleep(5)
                                    continue
                                else:
                                    if new_ip in [current_ip,og_ip]:
                                        time.sleep(5)
                                        continue
                                    else:
                                        break
                            else:
                                pass

                            if new_ip in [current_ip,og_ip]:
                                self.location.emit("Nord ip-address hasn't changed. Retrying...\n")
                                time.sleep(10)
                                continue
                            else:
                                self.location.emit(f"Nord Conected! Enjoy your new server.")
                                time.sleep(3)


                            if google_check == 1:
                                print("\n\33[33mPerforming captcha-check on Google search and Youtube...\n"
                                    "---------------------------\33[0m")
                                try:
                                    google_search_check = BeautifulSoup(
                                        requests.get("https://www.google.be/search?q=why+is+python+so+hard").content,"html.parser")
                                    youtube_video_check = BeautifulSoup(
                                        requests.get("https://www.youtube.com/watch?v=dQw4w9WgXcQ").content,"html.parser")

                                    google_captcha = google_search_check.find('div',id="recaptcha")
                                    youtube_captcha = youtube_video_check.find('div', id = "recaptcha")

                                    if None not in (google_captcha,youtube_captcha):
                                        print("Google throws a captcha. I'll pick a different server...")
                                        time.sleep(5)
                                        continue
                                except:
                                    print("Can't load Google page. I'll pick a different server...")
                                    time.sleep(5)
                                    continue
                                else:
                                    print("Google and YouTube don't throw any Captcha's: \33[92m\N{check mark}\33[0m")
                                    break
                            else:
                                break


                    if self.vpnwinds:
                        windsarg = 'windscribe'
                    else:
                        windsarg = 'none'

                    if self.vpnnord:
                        nordarg = 'nord_vpn'
                    else:
                        nordarg = 'none'

                    if self.vpnpia:
                        piaarg = 'pia_vpn'
                    else:
                        piaarg = 'none'

                    if self.vpnexpress:
                        expressarg = 'express_vpn' 
                    else:
                        expressarg = 'none'

                    if self.vpnmullvad:
                        mullvadarg = 'mullvad'
                    else:
                        mullvadarg = 'none'

                    if self.IVPNcheckBox:
                        ivpnarg = 'ivpn'
                    else:
                        ivpnarg = 'none'

                    vpns_de_exscolha = [
                        windsarg,
                        nordarg,
                        expressarg, 
                        mullvadarg,
                        piaarg,
                        ivpnarg
                    ]
                    selecionador = Balanceamento_de_vpn(vpns_de_exscolha)


                    vpn_selecionada = selecionador.selecionar()

                    if vpn_selecionada == 'windscribe':
                        print(F"Rotacionar com a Windscribe")    
                        disconnectx_mullvad = disconnect_mullvad()
                        if disconnectx_mullvad == True:
                            print("VPN Mullvad DISCONNECT") 

                        express_disconect = disconnect_express()    
                        if express_disconect == True:
                            print(F"VPN EXPRESS DISCONNECT")
                                
                        pia__disconect = pia_disconnect()    
                        if pia__disconect == True:
                            print(F"VPN PIA DISCONNECT")

                        try:
                            option_1_path = 'C:/Program Files/NordVPN'
                            subprocess.Popen(["nordvpn", "-d"],shell=True,cwd=option_1_path,stdout=DEVNULL)
                            print("VPN NORD DISCONNECT")    
                        except:
                            pass 
                        
                        time.sleep(5)
                        for _ in range(self.rotation_count_per_vpn):
                                        
                            location = area_input_vpn   
                            vpn2 = rotate_ip_windscribe(location)
                            if vpn2 == True:
                                self.benchmark_data['time_spent'] += time.time() - start_time
                                self.update_benchmark_data()
                                
                    if vpn_selecionada == 'nord_vpn':
                        print(F"Rotacionar com a nord")   

                        disconnectx_mullvad = disconnect_mullvad()
                        if disconnectx_mullvad == True:
                            print("VPN Mullvad DISCONNECT") 

                        express_disconect = disconnect_express()    
                        if express_disconect == True:
                            print(F"VPN EXPRESS DISCONNECT")

                        WINDSCRIBE_disconect = disconnect_WINDSCRIBE('disconnect')    
                        if WINDSCRIBE_disconect == True:
                            print(F"VPN WINDSCRIBE DISCONNECT")
                                
                        pia__disconect = pia_disconnect()    
                        if pia__disconect == True:
                            print(F"VPN PIA DISCONNECT")


                        
                        time.sleep(15)
                        for _ in range(self.rotation_count_per_vpn):
                                    
                            timezone = random.choice(list(vpn_options.keys()))
                            vpn_options_for_timezone = vpn_options.get(timezone, [])
                            vpn_option = random.choice(vpn_options_for_timezone)
                            print(vpn_options_for_timezone)
                            print(vpn_option)
                            self.location.emit(f'{[vpn_option]}')
                            vpn_instruction = initialize_VPN(area_input=[vpn_option])
                            rotate_ip_nord(vpn_instruction)
                            self.benchmark_data['time_spent'] += time.time() - start_time
                            self.update_benchmark_data()
                    
                    if vpn_selecionada == 'mullvad':

                        print(F"Rotacionar com a mullvad") 

                        express_disconect = disconnect_express()    
                        if express_disconect == True:
                            print(F"VPN EXPRESS DISCONNECT")

                        WINDSCRIBE_disconect = disconnect_WINDSCRIBE('disconnect')    
                        if WINDSCRIBE_disconect == True:
                            print(F"VPN WINDSCRIBE DISCONNECT")
                                
                        pia__disconect = pia_disconnect()    
                        if pia__disconect == True:
                            print(F"VPN PIA DISCONNECT")

                        try:
                            option_1_path = 'C:/Program Files/NordVPN'
                            subprocess.Popen(["nordvpn", "-d"],shell=True,cwd=option_1_path,stdout=DEVNULL)
                            print("VPN NORD DISCONNECT")    
                        except:
                            pass 


                        time.sleep(5)
                        for _ in range(self.rotation_count_per_vpn):
                                    
                            location = area_input_vpn  
                            vpn2 = rotate_ip_mullvad(location)
                            if vpn2 == True:
                                self.benchmark_data['time_spent'] += time.time() - start_time
                                self.update_benchmark_data()
                                    
                    if vpn_selecionada == 'pia_vpn':

                        print(F"Rotacionar com a pia") 

                        disconnectx_mullvad = disconnect_mullvad()
                        if disconnectx_mullvad == True:
                            print("VPN Mullvad DISCONNECT") 

                        express_disconect = disconnect_express()    
                        if express_disconect == True:
                            print(F"VPN EXPRESS DISCONNECT")

                        WINDSCRIBE_disconect = disconnect_WINDSCRIBE('disconnect')    
                        if WINDSCRIBE_disconect == True:
                            print(F"VPN WINDSCRIBE DISCONNECT")
                                
                        try:
                            option_1_path = 'C:/Program Files/NordVPN'
                            subprocess.Popen(["nordvpn", "-d"],shell=True,cwd=option_1_path,stdout=DEVNULL)
                            print("VPN NORD DISCONNECT")    
                        except:
                            pass 

                        time.sleep(5)
                        for _ in range(self.rotation_count_per_vpn):
                                
                            location = area_input_vpn
                            vpn2 = rotate_ip_pia(location)
                            if vpn2 == True:
                                self.benchmark_data['time_spent'] += time.time() - start_time
                                self.update_benchmark_data()

                    if vpn_selecionada == 'express_vpn':

                        print(F"Rotacionar com a Express") 

                        disconnectx_mullvad = disconnect_mullvad()
                        if disconnectx_mullvad == True:
                            print("VPN Mullvad DISCONNECT") 

                        WINDSCRIBE_disconect = disconnect_WINDSCRIBE('disconnect')    
                        if WINDSCRIBE_disconect == True:
                            print(F"VPN WINDSCRIBE DISCONNECT")
                                
                        pia__disconect = pia_disconnect()    
                        if pia__disconect == True:
                            print(F"VPN PIA DISCONNECT")

                        try:
                            option_1_path = 'C:/Program Files/NordVPN'
                            subprocess.Popen(["nordvpn", "-d"],shell=True,cwd=option_1_path,stdout=DEVNULL)
                            print("VPN NORD DISCONNECT")    
                        except:
                            pass 
                        for _ in range(self.rotation_count_per_vpn):
                                    
                            location = area_input_vpn        
                            rotate_ip_express2 = rotate_ip_express(location)        
                            if rotate_ip_express2 == True:    
                                self.benchmark_data['time_spent'] += time.time() - start_time
                                self.update_benchmark_data()
                    
                    if vpn_selecionada == 'ivpn':

                        print(F"Rotacionar com a ivpn") 

                        express_disconect = disconnect_express()    
                        if express_disconect == True:
                            print(F"VPN EXPRESS DISCONNECT")

                        disconnectx_mullvad = disconnect_mullvad()
                        if disconnectx_mullvad == True:
                            print("VPN Mullvad DISCONNECT") 

                        WINDSCRIBE_disconect = disconnect_WINDSCRIBE('disconnect')    
                        if WINDSCRIBE_disconect == True:
                            print(F"VPN WINDSCRIBE DISCONNECT")
                                
                        pia__disconect = pia_disconnect()    
                        if pia__disconect == True:
                            print(F"VPN PIA DISCONNECT")

                        try:
                            option_1_path = 'C:/Program Files/NordVPN'
                            subprocess.Popen(["nordvpn", "-d"],shell=True,cwd=option_1_path,stdout=DEVNULL)
                            print("VPN NORD DISCONNECT")    
                        except:
                            pass 
                        for _ in range(self.rotation_count_per_vpn):
                                    
                            location = area_input_vpn        
                            rrotate_ip_ivpn2 = rotate_ip_ivpn(location)        
                            if rrotate_ip_ivpn2 == True:    
                                self.benchmark_data['time_spent'] += time.time() - start_time
                                self.update_benchmark_data()
                        


                    for _ in range(self.interval):
                        if not self._is_running:
                            desativar_todas_vpns()
                            self.location.emit(f"M-T-V-A-R Stop")
                            break
                        time.sleep(1)



            self.progress.emit(100)
            self.finished.emit()


        elif is_valid == False:
            self.progress.emit(0)
            self.location.emit(f"YOU KEY IS Expired.")
            time.sleep(2)
        else:
            # Registra o computador para o serial
            try:
                security.register_computer(serial, computer_id, start_date, order_id)
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
        self.setWindowTitle('Multi Vpn Auto Rotate')
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


        self.stackedWidget = self.findChild(QWidget, 'stackedWidget')
        
        self.pushButton = self.findChild(QPushButton, 'pushButton')
        self.pushButton.clicked.connect(self.click_home)
 
        self.pushButton_2 = self.findChild(QPushButton, 'pushButton_2')
        self.pushButton_2.clicked.connect(self.click_config)
 
        self.pushButtonkey = self.findChild(QPushButton, 'pushButtonkey')
        self.pushButtonkey.clicked.connect(self.click_key)


        # Conectando o botão de parada
        self.stopButton = self.findChild(QPushButton, 'stopButton')

        self.stopButton.clicked.connect(self.on_stop_button_clicked)

        # Barra de progresso
        self.progressBar = self.findChild(QProgressBar, 'progressBar')

        # Label de localização
        self.locationLabel = self.findChild(QLabel, 'locationLabel')

        self.vpnpia = self.findChild(QCheckBox, 'vpnpia')
        self.vpnwindsc = self.findChild(QCheckBox, 'vpnwindsc')
        self.vpnexpress = self.findChild(QCheckBox, 'vpnexpress')
        self.vpnNord = self.findChild(QCheckBox, 'vpnNord')
        self.vpnmullvad = self.findChild(QCheckBox, 'vpnmullvad')
        self.IVPNcheckBox = self.findChild(QCheckBox, 'IVPNcheckBox')





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
        rotation_count_per_vpn = self.rotationCountSpinBox_2.value()

        vpnpia = self.vpnpia.isChecked()
        vpnwinds = self.vpnwindsc.isChecked()
        vpnexpress = self.vpnexpress.isChecked()
        vpnnord = self.vpnNord.isChecked()
        vpnmullvad = self.vpnmullvad.isChecked()
        IVPNcheckBox = self.IVPNcheckBox.isChecked()

        self.thread = RotateVpnThread(rotation_count, interval, rotate_in_usa, rotate_in_canada, rotate_in_complete, nvar_key, rotation_count_per_vpn, vpnpia, vpnwinds, vpnexpress, vpnnord, vpnmullvad, IVPNcheckBox)
        self.thread.progress.connect(self.update_progress)
        self.thread.location.connect(self.update_location)
        self.thread.finished.connect(self.on_rotation_finished)
        self.thread.start()

    def click_key(self):
        indicePaginainicio = 1
        self.stackedWidget.setCurrentIndex(indicePaginainicio)

    def click_config(self):
        indicePaginainicio = 2
        self.stackedWidget.setCurrentIndex(indicePaginainicio)

    def click_home(self):
        indicePaginainicio = 0
        self.stackedWidget.setCurrentIndex(indicePaginainicio)

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


            vpnpia = data1["vpnpia"]
            vpnexpress = data1["vpnexpress"]
            vpnwinds = data1["vpnwinds"]
            vpnmullvad = data1["vpnmullvad"]
            vpnnord = data1["vpnnord"]
            vpni = data1["vpni"]


            def str_to_bool(s):
                return s.lower() in ['true', '1', 't', 'y', 'yes']

            #config = json.load(ref1)
            self.rotationCountSpinBox.setValue(int(rotation_count))
            self.intervalSpinBox.setValue(int(interval))
            self.usaCheckBox.setChecked(str_to_bool(rotate_in_usa))
            self.canadacheckBox.setChecked(str_to_bool(rotate_in_canada))
            self.completecheckBox.setChecked(str_to_bool(rotate_complete))

            self.vpnpia.setChecked(str_to_bool(vpnpia))
            self.vpnexpress.setChecked(str_to_bool(vpnexpress))
            self.vpnNord.setChecked(str_to_bool(vpnnord))
            self.vpnwindsc.setChecked(str_to_bool(vpnwinds))
            self.vpnmullvad.setChecked(str_to_bool(vpnmullvad))
            self.IVPNcheckBox.setChecked(str_to_bool(vpni))

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
            
            "vpnpia": f"{self.vpnpia.isChecked()}",
            "vpnexpress": f"{self.vpnexpress.isChecked()}",
            "vpnwinds": f"{self.vpnwindsc.isChecked()}",
            "vpnmullvad": f"{self.vpnmullvad.isChecked()}",
            "vpnnord": f"{self.vpnNord.isChecked()}",
            "vpni": f"{self.IVPNcheckBox.isChecked()}",

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
    
        "vpnpia": f"{self.vpnpia.isChecked()}",
        "vpnexpress": f"{self.vpnexpress.isChecked()}",
        "vpnwinds": f"{self.vpnwindsc.isChecked()}",
        "vpnmullvad": f"{self.vpnmullvad.isChecked()}",
        "vpnnord": f"{self.vpnNord.isChecked()}",
        "vpni": f"{self.IVPNcheckBox.isChecked()}",
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