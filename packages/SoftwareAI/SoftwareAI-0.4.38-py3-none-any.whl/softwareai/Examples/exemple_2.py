#########################################
# IMPORT SoftwareAI Agents
from softwareai.CoreApp._init_agents_ import AgentInitializer
#########################################
# IMPORT SoftwareAI Libs 
from softwareai.CoreApp._init_libs_ import *
#########################################

byte_manager = AgentInitializer.get_agent('ByteManager') 
mensagem = "solicito uma atualização do repositorio https://github.com/A-I-O-R-G/trontechnicalanalysistool"
owner_response = byte_manager.AI_1_ByteManager_Company_Owners(mensagem)
print(owner_response)
