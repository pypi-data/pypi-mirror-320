from ui.Expressvpn_Auto_Rotatemain_window_ui import Ui_MainWindow
from ui.Expressvpn_Auto_Rotatebenchmark_window_ui import Ui_BenchmarkWindow
from ui.Expressvpn_Auto_Rotateglobal_benchmark_window_ui import Ui_GlobalBenchmarkWindow

from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QProgressBar, QLabel, QCheckBox, QSpinBox, QWidget
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from os import path
from subprocess import check_output,DEVNULL
from bs4 import BeautifulSoup
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from firebase_admin import credentials, initialize_app, storage, db, delete_app


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
import ctypes
import firebase_admin
import hashlib
import uuid
import json
from firebase_admin import credentials, db, initialize_app
import hashlib
import os
import random
from datetime import datetime, timedelta

# import time
# cred = {
#   "type": "service_account",
#   "project_id": "nordautorotate",
#   "private_key_id": "d10278e01e5cbbf4860a88e3eb70eb0eb20ea988",
#   "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDWuBWXzaTLQaYi\nouJQJIdxbkx6BLIZdEUYrV/o8X7jVrDuNf/lOswKfONsnY+BCsq/6ueorccFFuHN\nqrLDIPF/OXciGsIOv0AgOQVglqgkIr0UuFYdxD09dPtGSgg2yRDWMtNwt6mFdIX9\nA5ORiq11Qjn2Stkx3QmLyZs9oWI30yY8CUneKW0hb6juX9Sfieh47GLjbF5VSu8x\nUsHilulSaFsuSwJ6Scm1vZi+HrNzAmMSX9tENxxVW1KSby9yxHMEEM0DA22QcDjC\n2M5cyaV9wymByBt/xree5dqepXWuHEHkz5g7xsHm1bRHMAILy5Vs2fcbCdyme1hw\ngY3y4+klAgMBAAECggEAAzr4q25y0DoFyPYjqsjDDJt4Ffusb4JQkBf7FQI2DpDR\nD4fUfqwE5u8D7WDm48act7+K0HJlCsRkk52E2QajBWLccJ6mlLVoULzur6i57KBM\ngHblaAQkuMS3SExpEmqA+455Ae5JcEMbjEcYI8Lo5hA4OE4nQb8l1Wd7e0GHbWXK\nbF2gq0Wgi7VfLxZGJUXgorKTkrva9PAunWmulXS8hcNvESqFEXpqi3ZFCuKtDcKX\nbd5uobKk9ltdYsYb44VWuW45sKjBM9ccnaO02xo0n4i6K3QcH58Uy0KpKyoczrgz\n/8orAhE6NiY/zyyyhXqUYoa9PEGu26G3QQKj3bZTKwKBgQDw86d7fv+VgcUoxSR3\nmlqF5fASO9i0GyyjaP+viZU428xx0uqXbiV1e5PT7yfXlX2EJfCGLeNjEctIf4n6\nx7+Xt9hkHmq3KPClgshiO9R1Z+K0NpD6FeRhXheF5GXmYbMnEwvyciXp5LckUNBT\n96fAgsRwuvZe2pMJm24/r1guvwKBgQDkIQVVfdd3RYFhseA5fJbdCyHOYe5igJGU\n2mEIBm6HHlxkl7CS9WC9NAxGC3QSNW6BPyXnOz+BGDRGBvvue1WUFgx8mAXdn16R\no7hDVy0IURIO/D+6ZlA+JDbDIft3hFReka0P1uIPDA7I0AtG0cNXpz5kyjqOYzDr\ncTvarOLFGwKBgQCTY+hKcegz8zrAcr+Y7fF7wKj27mbj3U+T8hGdtiJysnlAE03v\nLbB6SgqmdL/Bby9lW7Pi0EUs/+CCy4mCvxdi3lHfBIAw5Dk4dWTQOlr/KnoR1OMg\nJ64ZJW5sN8dhgtgNCeif+NVaWs7wxwJ4qqCR8Svq7WLxqPCSyuJI0KC3jwKBgQCW\n2yc105PKcZIPUpseKL9yyMvAOI51YOPkdUy5C9fHTlJ2ysCfTdh9BZAgOa6149OB\ncIrWEB38dk8LB89Ncw2ycaosMjOezKay1HsjPOCwoTu54SEbWFEz5qq3+x7ZeA56\nwwaYdNbkcGrObJUobcopipT9/aUfR4SwDR8xiiYjhQKBgQDKXk7m0mgoCIHrKDOE\nlnKt5YP6gowOwhpm2BfSdnlbCq4HlLKPK2pzBbED37Of5dxBB75Wt5EXdKPI4PX4\n+WI462V7dPXs6tiM88HP0OtV0GXnCiPzhcex9THcallFTMT9Sk9o4/HYyNSAbpxc\nVqnTCwidv6vSAgKtkx7T4QQfMQ==\n-----END PRIVATE KEY-----\n",
#   "client_email": "firebase-adminsdk-g3x1w@nordautorotate.iam.gserviceaccount.com",
#   "client_id": "111074944143599369254",
#   "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#   "token_uri": "https://oauth2.googleapis.com/token",
#   "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#   "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-g3x1w%40nordautorotate.iam.gserviceaccount.com",
#   "universe_domain": "googleapis.com"
# }
# cred = credentials.Certificate(cred)
# app1 = initialize_app(cred, {
#         'storageBucket': 'nordautorotate.appspot.com',
#         'databaseURL': 'https://nordautorotate-default-rtdb.firebaseio.com'
#         })
# bucket = storage.bucket(app=app1)
# ref1 = db.reference(f'Controle_de_versao', app=app1)
# data1 = ref1.get()                         
# controle_das_funcao2 = f"Controle_2"
# controle_das_funcao_info_2 = {
# "versao": f"atualizando_nordvpnautorotate_2.zip"
# }
# ref1.child(controle_das_funcao2).set(controle_das_funcao_info_2)
def run_command(command):
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,  shell=True)
    return list([str(v).replace('\\t', ' ').replace('\\n', ' ').replace('b\'', '').replace('\'', '')
                .replace('b"', '')
                 for v in iter(p.stdout.readline, b'')])

def express_rotation(location):
    command = f'ExpressVPN.CLI.exe disconnect'
    diretorio = r'C:\\Program Files (x86)\\ExpressVPN\\services'
    os.chdir(diretorio)
    #try:
    #subprocess.run(command, creationflags=subprocess.CREATE_NO_WINDOW)
    #except Exception as erro:
    run_command(command) 
    time.sleep(1)
    command = f'ExpressVPN.CLI.exe connect {location}'
    diretorio = r'C:\\Program Files (x86)\\ExpressVPN\\services'
    #os.chdir(diretorio)
    #try:
    #subprocess.run(command, creationflags=subprocess.CREATE_NO_WINDOW)
    #except Exception as erro:
    #os.system(command)       
    teste = run_command(command)
    print(teste)
    return True


def lists_rotate(area_input):

  if 'complete_rotate_in_usa' in area_input:
    list = [
    '"USA - New York"',  
    '"USA - Houston"',
    
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
    #pyuac.runAsAdmin()
    command = f'ExpressVPN.CLI.exe disconnect'
    diretorio = r'C:\\Program Files (x86)\\ExpressVPN\\services'
    os.chdir(diretorio)
    run_command(command)
    #try:
    #subprocess.run(command, creationflags=subprocess.CREATE_NO_WINDOW)
    #except Exception as erro:
    #    os.system(command)     
    return True

#location = lists_rotate(area_input)
#lista_de_server.append(location)
#location_flag_teste = lista_de_server.pop(0)

for _ in range(1):
  time.sleep(1)
  
  location = lists_rotate('complete_rotate_in_usa')
  print(location)
  express_rotation(location)