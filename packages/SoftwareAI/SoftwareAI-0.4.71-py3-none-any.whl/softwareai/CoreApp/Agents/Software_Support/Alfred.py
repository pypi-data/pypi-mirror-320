

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



class OpenAIKeysteste:
    def keys():
        companyname = "teste"
        str_key = "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"
        return str_key
    


            
key_openai = OpenAIKeysteste.keys()
name_app = "appx"
appfb = FirebaseKeysinit._init_app_(name_app)
client = OpenAIKeysinit._init_client_(key_openai)
    
TOKEN = "6926043018:AAHc7NioJXC-K2pxgiQuhbMkagJ0OPIJ_f8"
CHANNEL_ID = '-2234291162'

# class AlfredSupport_NordVPN_Auto_Rotate:
#     def __init__(self,
#                 appfb,
#                 client
#             ):
#         appfb = appfb
#         client = client

user_threads = {}
emojis = ['😊', '🤖', '🚀', '💡', '🎉']


instruction = """
    ### Instruções para Assistente de Suporte: NordVPN Auto Rotate

    ## Objetivo
    Oferecer suporte completo aos usuários do **NordVPN Auto Rotate**, garantindo a resolução rápida de problemas e fornecendo informações claras sobre o uso e funcionamento do software.

    ## Diretrizes de Atendimento

    ### 1. **Boas-vindas e Agradecimento**
    - Agradeça ao cliente por escolher o NordVPN Auto Rotate.
    - Envie a seguinte mensagem padrão de boas-vindas:

    **Mensagem de Boas-vindas:**

    "Obrigado por escolher o **NordVPN Auto Rotate**. Aproveite todos os benefícios de segurança e privacidade que nosso aplicativo oferece.

    📥 **Download do Aplicativo:** [Clique aqui para baixar](https://www.mediafire.com/file/e8803j54knyj23p/Nord_Auto_Rotate.rar/file)

    📺 **Tutorial no YouTube:** [Assista ao vídeo](https://www.youtube.com/watch?v=E4fbZUVMMEI)

    📞 **Suporte via Telegram:** [Acesse o grupo de suporte](https://t.me/+dpGofyMuGUszY2Rh)"

    ### 2. **Solução de Problemas**

    #### Problemas Comuns e Soluções:

    - **Erro: Não conecta ao servidor**  
    🔎 *Causa:* Falha de conexão com o NordVPN.  
    ✅ *Solução:* Verifique se o NordVPN está ativo e com assinatura válida.

    - **Erro: Licença inválida**  
    🔎 *Causa:* Serial incorreto ou vencido.  
    ✅ *Solução:* Confirme o serial usado e informe que a licença tem validade de 30 dias. Oriente sobre a renovação.

    - **Erro: Aplicativo não inicia**  
    🔎 *Causa:* Requisitos do sistema não atendidos.  
    ✅ *Solução:* Verifique se o Python 3.x está instalado e se o NordVPN está atualizado.

    ### 3. **Informações Técnicas**

    - **Licenciamento:**
    - A licença permite instalação em até **2 dispositivos**.
    - O serial é gerado automaticamente após a compra e vinculado ao hardware (CPU e disco).
    - A licença tem validade de **30 dias**.

    - **Funcionalidades Principais:**
    - Rotação automática de servidores NordVPN.
    - Configuração de intervalos personalizados.
    - Geração de relatórios de servidores utilizados.

    ### 4. **Passo a Passo para Uso do Aplicativo**

    1. **Instalação:**
    - Baixe o aplicativo pelo link fornecido.
    - Execute o instalador e siga as instruções.

    2. **Ativação:**
    - Insira o serial enviado após a compra.
    - O aplicativo validará o serial com o hardware.

    3. **Iniciar Rotação:**
    - Clique no botão "Iniciar" para ativar a rotação automática.
    
    4. **Parar Rotação:**
    - Clique em "Parar" quando desejar encerrar a rotação.

    5. **Visualizar Relatório:**
    - Acesse o histórico de servidores clicando em "Visualizar Relatório".

    ### 5. **Termos de Serviço**

    - A licença é exclusiva e não pode ser compartilhada.
    - O uso indevido resultará no cancelamento da licença.
    - A garantia de suporte técnico é limitada a 12 horas após a compra.

    ### 6. **Contatos de Suporte**

    - 📧 **Email:** blocodesense@gmail.com  
    - 📞 **Telegram:** [Grupo de Suporte](https://t.me/+dpGofyMuGUszY2Rh)  
    - 🕘 **Horário de Atendimento:** Segunda a Sexta, das 09h às 18h

    ## Procedimento em Caso de Reclamações

    1. **Ouvir atentamente o problema.**
    2. **Coletar informações relevantes:** Serial, sistema operacional e descrição do erro.
    3. **Sugerir soluções conforme o erro identificado.**
    4. **Encaminhar para nível avançado, se necessário.**

    ## Atualizações

    - Atualizações menores a cada 3 meses.
    - Licença renovável após 30 dias de uso.

    ### **Mensagem de Encerramento**
    "Estamos à disposição para ajudá-lo a aproveitar ao máximo o **NordVPN Auto Rotate**. Qualquer dúvida, entre em contato pelo nosso suporte. Boa navegação!"

"""
tools_Alfred = None
adxitional_instructions_Alfred = ""
key = "AI_Alfred"
nameassistant = "Alfred"
model_select = "gpt-4o-mini-2024-07-18"
Upload_1_file_in_thread = None
Upload_1_file_in_message = None
Upload_1_image_for_vision_in_thread = None
Upload_list_for_code_interpreter_in_thread = None
vectorstore_in_Thread = None
vectorstore_in_agent = None


def Alfred(mensagem, user_id):
    print(user_id)
    AI, instructionsassistant, nameassistant, model_select = AutenticateAgent.create_or_auth_AI(appfb, client, key, instruction, nameassistant, model_select, tools_Alfred, vectorstore_in_agent)
    print(AI)
    response, total_tokens, prompt_tokens, completion_tokens = ResponseAgent.ResponseAgent_message_with_assistants(
                                                            mensagem=mensagem,
                                                            agent_id=AI, 
                                                            key=key,
                                                            user_id=user_id,
                                                            app1=appfb,
                                                            client=client,
                                                            tools=tools_Alfred,
                                                            model_select=model_select,
                                                            aditional_instructions=adxitional_instructions_Alfred,
                                                            AgentDestilation=True
                                                            )
                                            
                
    return response, total_tokens, prompt_tokens, completion_tokens



def start(update, context):
    user_id = update.message.from_user.id
    update.message.reply_text('Olá! Como posso ajudar você hoje?')

def reply_message(update, context):
    user_message = update.message.text
    user_id = update.message.from_user.id
    
    print(user_message)
    Alfred_response, total_tokens, prompt_tokens, completion_tokens = Alfred(user_message, user_id)
    print(Alfred_response)
    update.message.reply_text(Alfred_response)



def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, reply_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()