import threading
import time
import subprocess
import firebase_admin
import importlib.util
import os
import zipfile
import shutil
import pyautogui
import datetime
from firebase_admin import credentials, storage, db
import psutil
import firebase_admin
import time
import threading
import zipfile
import tempfile
import socket
from firebase_admin import credentials, initialize_app, storage, db, delete_app


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

diretorio_script = os.path.dirname(os.path.abspath(__file__))



def fazendo_o_download_da_nova_versao(bucket):

    try:

        nome_da_versao_dentro_do_buckt = f'atualizando_expressvpnautorotate_att.zip'
        diretorio_script = os.path.dirname(os.path.abspath(__file__)) 
        extract_dir = os.path.join(diretorio_script)
        
        #extract_dir = f'Arquivos/Versionamento_do_protocolo/Versao_{nova_versao}'
        os.makedirs(extract_dir, exist_ok=True)

        with tempfile.NamedTemporaryFile(delete=False) as temp_zip_file:
            temp_zip_filename = temp_zip_file.name
            blob = bucket.blob(nome_da_versao_dentro_do_buckt)
            blob.download_to_filename(temp_zip_filename)

        with zipfile.ZipFile(temp_zip_filename, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        os.remove(temp_zip_filename)

    except Exception as eroo1:
        print(f"{eroo1}erro ao att ")


fazendo_o_download_da_nova_versao(bucket)
