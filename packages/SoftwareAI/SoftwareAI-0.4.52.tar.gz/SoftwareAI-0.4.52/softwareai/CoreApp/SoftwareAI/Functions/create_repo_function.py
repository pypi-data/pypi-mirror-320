
#########################################
# IMPORT SoftwareAI Libs 
from softwareai.CoreApp._init_libs_ import *
#########################################


def create_repo(repo_name: str, 
                description:str,
                token: str
                ):
    repo_url = f"https://api.github.com/orgs/A-I-O-R-G/repos"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    repo_data = {
        "name": repo_name,
        "description": description,
        "private": False
    }
    response = requests.post(repo_url, json=repo_data, headers=headers)
    if response.status_code == 201:
        print(f"Repositório {repo_name} criado com sucesso na organização A-I-O-R-G!")

        lista = [
                "DallasEquipeDeSolucoes",
                "BobGerenteDeProjeto",
                "QuantummCore",
                "SignalMaster727",
                "NexGenCoder756",
                "TigraoEscritor",
                "CloudArchitectt"
            ]

        for list in lista:
            # Adicionando colaboradores com permissões de administrador
            collaborator_url = f"https://api.github.com/repos/{repo_name}/collaborators/{list}"
            collaborator_data = {
                "permission": "admin"
            }
            collaborator_response = requests.put(collaborator_url, headers=headers, json=collaborator_data)
            if collaborator_response.status_code == 201 or collaborator_response.status_code == 204:
                print(f"Colaborador '{list}' adicionado com sucesso com permissões de administrador.")
            else:
                print(f"Falha ao adicionar colaborador. Status: {collaborator_response.status_code}, Resposta: {collaborator_response.json()}")

        return {"status": "sucess", "message": f"Repositório {repo_name} criado com sucesso na organização A-I-O-R-G!"}

    else:
        print(f"Falha ao criar o repositório. Status: {response.status_code}, Resposta: {response.json()}")
        return {"status": "error", "message": response.json()}

