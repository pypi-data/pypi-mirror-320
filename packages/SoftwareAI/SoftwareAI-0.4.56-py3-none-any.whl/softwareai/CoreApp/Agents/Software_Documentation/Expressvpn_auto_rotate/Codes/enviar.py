
from firebase_admin import credentials, initialize_app, storage, db, delete_app


import os
import time
import zipfile
import subprocess
import shutil
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

time.sleep(3)

start_time = time.time()




start_time = time.time()
lista = ['main.py']
for list in lista: #   "-e", "30",  
    subprocess.run(["pyarmor-8", "gen", "--assert-import", "--assert-call", "--enable-themida",  "--enable-jit",  "--mix-str",  "--obf-code", "2", f"{list}"])



time.sleep(3)

def buscar_arquivo(nome_arquivo):
    blob = bucket.blob(nome_arquivo)
    if blob.exists():
        return blob
    else:
        print(f"O arquivo '{nome_arquivo}' não foi encontrado no bucket.")
        return None


diretorio_script = os.path.dirname(os.path.abspath(__file__))

ref1 = db.reference(f'Controle_de_versao/Controle_1')
data1 = ref1.get()
x = data1["versao"]

nome_arquivo = f"{x}"
blob_arquivo = buscar_arquivo(nome_arquivo)
if blob_arquivo:
    print(f"O arquivo '{nome_arquivo}' foi encontrado no bucket criando nova versao.")
    numero_versao_atual = int(nome_arquivo.split("_")[-1].split(".")[0])
    nova_versao = numero_versao_atual + 1
    folder_to_zip = "dist"
    zip_folder_name = "atualizando_expressvpnautorotate"    
    zip_file_name = zip_folder_name + f"_{nova_versao}" + ".zip"

    with zipfile.ZipFile(zip_file_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        for foldername, subfolders, filenames in os.walk(folder_to_zip):
            for filename in filenames:
                filepath = os.path.join(foldername, filename)
                arcname = os.path.relpath(filepath, folder_to_zip)
                zipf.write(filepath, arcname)


    blob = bucket.blob(zip_file_name)
    blob.upload_from_filename(zip_file_name)
    print("ZIPADO E ENVIADO PARA FIREBASE COM sucesso !")

    time.sleep(3)
    os.remove(zip_file_name)
    

    time.sleep(3)
    try:
        shutil.rmtree(folder_to_zip)
        print(f"A pasta '{folder_to_zip}' foi excluída com sucesso.")
    except Exception as e:
        print(f"Erro ao excluir a pasta '{folder_to_zip}': {str(e)}")

    ref1 = db.reference(f'Controle_de_versao')
    data1 = ref1.get()                         
    controle_das_funcao = "Controle_1"
    controle_das_funcao_info_ = {
    "versao": zip_file_name,
    }
    ref1.child(controle_das_funcao).set(controle_das_funcao_info_)
    
    ref1 = db.reference(f'Controle_de_versao')
    data1 = ref1.get()                         
    controle_das_funcao2 = "Controle_2"
    controle_das_funcao_info_2 = {
    "versao": nome_arquivo,
    }
    ref1.child(controle_das_funcao2).set(controle_das_funcao_info_2)
    

else:
    print("Não foi possível encontrar o arquivo.")




def buscar_arquivo(nome_arquivo):
    blob = bucket.blob(nome_arquivo)
    if blob.exists():
        return blob
    else:
        print(f"O arquivo '{nome_arquivo}' não foi encontrado no bucket.")
        return None


diretorio_script = os.path.dirname(os.path.abspath(__file__))

ref1 = db.reference(f'Controle_de_versao/Controle_config_1')
data1 = ref1.get()
x = data1["versao"]

nome_arquivo = f"{x}"
blob_arquivo = buscar_arquivo(nome_arquivo)
if blob_arquivo:
    print(f"O arquivo '{nome_arquivo}' foi encontrado no bucket criando nova versao.")
    numero_versao_atual = int(nome_arquivo.split("_")[-1].split(".")[0])
    nova_versao = numero_versao_atual + 1
    folder_to_zip = "config"
    zip_folder_name = f"atualizando_expressvpnautorotate_config"    
    zip_file_name = zip_folder_name + f"_{nova_versao}" + ".zip"

    with zipfile.ZipFile(zip_file_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        for foldername, subfolders, filenames in os.walk(folder_to_zip):
            for filename in filenames:
                filepath = os.path.join(foldername, filename)
                arcname = os.path.relpath(filepath, folder_to_zip)
                zipf.write(filepath, arcname)


    blob = bucket.blob(zip_file_name)
    blob.upload_from_filename(zip_file_name)
    print("ZIPADO E ENVIADO PARA FIREBASE COM sucesso !")

    ref1 = db.reference(f'Controle_de_versao')
    data1 = ref1.get()                         
    controle_das_funcao = "Controle_config_1"
    controle_das_funcao_info_ = {
    "versao": zip_file_name,
    }
    ref1.child(controle_das_funcao).set(controle_das_funcao_info_)
    
    ref1 = db.reference(f'Controle_de_versao')
    data1 = ref1.get()                         
    controle_das_funcao2 = "Controle_config_2"
    controle_das_funcao_info_2 = {
    "versao": nome_arquivo,
    }
    ref1.child(controle_das_funcao2).set(controle_das_funcao_info_2)
    
    os.remove(zip_file_name)


else:
    print("Não foi possível encontrar o arquivo.")







start_time = time.time()
lista = ['ui/benchmark_window_ui.py', 'ui/global_benchmark_window_ui.py', 'ui/main_window_ui.py']
for list in lista: #   "-e", "30", "--assert-import", "--assert-call", "--enable-themida",  "--enable-jit", 
    subprocess.run(["pyarmor-8", "gen", "--assert-import", "--assert-call", "--enable-themida",  "--enable-jit",  "--mix-str",  "--obf-code", "2", f"{list}"])

time.sleep(3)
shutil.copy('ui/logo.png', 'dist')
shutil.copy('ui/style.qss', 'dist')
shutil.copy('ui/icone_usa.png', 'dist')
shutil.copy('ui/icone_canada.png', 'dist')

def buscar_arquivo(nome_arquivo):
    blob = bucket.blob(nome_arquivo)
    if blob.exists():
        return blob
    else:
        print(f"O arquivo '{nome_arquivo}' não foi encontrado no bucket.")
        return None


diretorio_script = os.path.dirname(os.path.abspath(__file__))

ref1 = db.reference(f'Controle_de_versao/Controle_ui_1')
data1 = ref1.get()
x = data1["versao"]

nome_arquivo = f"{x}"
blob_arquivo = buscar_arquivo(nome_arquivo)
if blob_arquivo:
    print(f"O arquivo '{nome_arquivo}' foi encontrado no bucket criando nova versao.")
    numero_versao_atual = int(nome_arquivo.split("_")[-1].split(".")[0])
    nova_versao = numero_versao_atual + 1
    folder_to_zip = "dist"
    zip_folder_name = f"atualizando_expressvpnautorotate_ui"    
    zip_file_name = zip_folder_name + f"_{nova_versao}" + ".zip"

    with zipfile.ZipFile(zip_file_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        for foldername, subfolders, filenames in os.walk(folder_to_zip):
            for filename in filenames:
                filepath = os.path.join(foldername, filename)
                arcname = os.path.relpath(filepath, folder_to_zip)
                zipf.write(filepath, arcname)


    blob = bucket.blob(zip_file_name)
    blob.upload_from_filename(zip_file_name)
    print("ZIPADO E ENVIADO PARA FIREBASE COM sucesso !")
    ref1 = db.reference(f'Controle_de_versao')
    data1 = ref1.get()                         
    controle_das_funcao = "Controle_ui_1"
    controle_das_funcao_info_ = {
    "versao": zip_file_name,
    }
    ref1.child(controle_das_funcao).set(controle_das_funcao_info_)
    
    ref1 = db.reference(f'Controle_de_versao')
    data1 = ref1.get()                         
    controle_das_funcao2 = "Controle_ui_2"
    controle_das_funcao_info_2 = {
    "versao": nome_arquivo,
    }
    ref1.child(controle_das_funcao2).set(controle_das_funcao_info_2)

    time.sleep(3)
    os.remove(zip_file_name)
    
    try:
        shutil.rmtree(folder_to_zip)
        print(f"A pasta '{folder_to_zip}' foi excluída com sucesso.")
    except Exception as e:
        print(f"Erro ao excluir a pasta '{folder_to_zip}': {str(e)}")


else:
    print("Não foi possível encontrar o arquivo.")


lista = ['att.py']
for list in lista: #   "-e", "30", "--assert-import", "--assert-call", "--enable-themida",  "--enable-jit", 
    subprocess.run(["pyarmor-8", "gen", "--assert-import", "--assert-call", "--enable-themida",  "--enable-jit",  "--mix-str",  "--obf-code", "2", f"{list}"])



time.sleep(3)

folder_to_zip = "dist"
zip_folder_name = f"atualizando_expressvpnautorotate_att"    
zip_file_name = zip_folder_name + ".zip"

with zipfile.ZipFile(zip_file_name, "w", zipfile.ZIP_DEFLATED) as zipf:
    for foldername, subfolders, filenames in os.walk(folder_to_zip):
        for filename in filenames:
            filepath = os.path.join(foldername, filename)
            arcname = os.path.relpath(filepath, folder_to_zip)
            zipf.write(filepath, arcname)


blob = bucket.blob(zip_file_name)
blob.upload_from_filename(zip_file_name)
print("ZIPADO E ENVIADO PARA FIREBASE COM sucesso !")

time.sleep(3)
os.remove(zip_file_name)

try:
    shutil.rmtree(folder_to_zip)
    print(f"A pasta '{folder_to_zip}' foi excluída com sucesso.")
except Exception as e:
    print(f"Erro ao excluir a pasta '{folder_to_zip}': {str(e)}")



ende = time.time()
segundos = ende - start_time
minutos = segundos / 60

print(f"Segundos: {segundos}")
print(f"Minutos: {minutos}")
