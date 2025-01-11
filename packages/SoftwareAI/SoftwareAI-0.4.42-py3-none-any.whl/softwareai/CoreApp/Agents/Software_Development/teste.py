import requests


#########################################
# IMPORT SoftwareAI Core
from softwareai.CoreApp._init_core_ import * 
#########################################
# IMPORT SoftwareAI Libs 
from softwareai.CoreApp._init_libs_ import *
#########################################
# IMPORT SoftwareAI All Paths 
from softwareai.CoreApp._init_paths_ import *
#########################################
# IMPORT SoftwareAI Instructions
from softwareai.CoreApp.SoftwareAI.Instructions._init_Instructions_ import *
#########################################
# IMPORT SoftwareAI Tools
from softwareai.CoreApp.SoftwareAI.Tools._init_tools_ import *
#########################################
# IMPORT SoftwareAI keys
from softwareai.CoreApp._init_keys_ import *
#########################################
# IMPORT SoftwareAI _init_environment_
from softwareai.CoreApp._init_environment_ import load_env, load_chagelog



# Substitua pelos valores apropriados
github_token = "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"
repo_name = "A-I-O-R-G/trontechnicalanalysistool" 
branch_name = "main"  # Substitua pelo branch correto, se necessário

headers = {
    "Authorization": f"token {github_token}",
    "Accept": "application/vnd.github.v3+json"
}

def get_file_content(repo_name, file_path, branch_name):
    file_url = f"https://api.github.com/repos/{repo_name}/contents/{file_path}?ref={branch_name}"
    response = requests.get(file_url, headers=headers)
    
    if response.status_code == 200:
        file_data = response.json()
        import base64
        content = base64.b64decode(file_data['content']).decode('utf-8')
        return content
    else:
        print(f"Erro ao acessar {file_path}. Status: {response.status_code}")
        return None

AnalysisRequirements = get_file_content(repo_name, "AppMap/Analisys/AnalysisRequirements.txt", branch_name)
PreProject = get_file_content(repo_name, "AppMap/PreProject/doc.txt", branch_name)
RoadMap = get_file_content(repo_name, "AppMap/RoadMap/Roadmap.txt", branch_name)
Schedule = get_file_content(repo_name, "AppMap/SpreadsheetAndTimeline/Schedule.txt", branch_name)
Spreadsheet = get_file_content(repo_name, "AppMap/SpreadsheetAndTimeline/Spreadsheet.txt", branch_name)
