from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import time
import re
import os

def extrair_codigo(texto):
    padrao = r'```python\n(.*?)\n```'  # Expressão regular para capturar código entre as tags
    resultado = re.search(padrao, texto, re.DOTALL)  # re.DOTALL permite que o "." capture quebras de linha
    if resultado:
        return resultado.group(1)  # Retorna o código encontrado
    return None


# tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/deepseek-coder-1.3b-instruct", trust_remote_code=True)
# model = AutoModelForCausalLM.from_pretrained("deepseek-ai/deepseek-coder-1.3b-instruct", trust_remote_code=True, torch_dtype=torch.bfloat16).cuda()
# messages=[
#     { 'role': 'user', 'content': f'{content_}'}
# ]
# inputs = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt").to(model.device)
# # tokenizer.eos_token_id is the id of <|EOT|> token
# outputs = model.generate(inputs, max_new_tokens=512, do_sample=False, top_k=50, top_p=0.95, num_return_sequences=1, eos_token_id=tokenizer.eos_token_id)
# response = tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)
import shutil
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
    
class CloudMd:
    def __init__(self,       
                appfb,
                client,          
                Logger: Optional[bool] = True,
                DebugTokens: Optional[bool] = True,
                lang: Optional[str] = "pt"
            ):
        self.appfb = appfb
        self.client = client
        self.Logger = Logger
        self.DebugTokens = DebugTokens
        self.lang = lang
        self.countNumberTokensTotal = 0
        self.key = "CloudMd"
        self.nameassistant = "Cloud Md"
        self.model_select = "gpt-4o-mini-2024-07-18"

        self.instruction = '''

        ## Objectives
        Create comprehensive and high-quality technical documentation from Python source code, transforming comments, docstrings, and code into a structured and readable Markdown document.

        ### 1. Structure Example

        ```markdown
        # Module Title

        ## Overview
        Detailed description...

        ## Installation
        Installation instructions...

        ## Usage
        Usage examples...
        ```


        ### 2. Rules 
            #### 4.1 Headers
            - Use `#` for titles and subtitles
            - Clear and consistent hierarchy
            - Maximum of 3 depth levels

            #### 4.2 Code Blocks
            - Use triple backticks with language identification
            - Example: 
            ````markdown
            ```python
            def example():
                return "code"
            ```
            ````

            #### 4.3 Emphasis
            - *Italics* for technical terms
            - **Bold** for important highlights
            - `Inline code` for code references


        '''
        
        self.tools = [
        {
            "type": "function",
            "function": {
                "name": "autosave",
                "description": "Salva um codigo python em um caminho",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "codigo"
                        },
                        "path": {
                            "type": "string",
                            "description": "Caminho do codigo"
                        }
                    },
                    "required": ["code","path"]
                }
            }
        }
        ]
        

    def GenDocsMdInGPU(
        mensagem,
        model_name = "Qwen/Qwen2.5-Coder-1.5B-Instruct", #"Qwen/Qwen2.5-Coder-3B-Instruct"#"Qwen/Qwen2.5-Coder-0.5B-Instruct"#
        cache_dir = "D:\LLMModels",
        max_new_tokens=2900
        ):

        start_time = time.perf_counter()

        instruction = '''

        ## Objectives
        Create comprehensive and high-quality technical documentation from Python source code, transforming comments, docstrings, and code into a structured and readable Markdown document.

        ### 1. Structure Example

        ```markdown
        # Module Title

        ## Overview
        Detailed description...

        ## Installation
        Installation instructions...

        ## Usage
        Usage examples...
        ```


        ### 2. Rules 
            #### 4.1 Headers
            - Use `#` for titles and subtitles
            - Clear and consistent hierarchy
            - Maximum of 3 depth levels

            #### 4.2 Code Blocks
            - Use triple backticks with language identification
            - Example: 
            ````markdown
            ```python
            def example():
                return "code"
            ```
            ````

            #### 4.3 Emphasis
            - *Italics* for technical terms
            - **Bold** for important highlights
            - `Inline code` for code references


        '''

        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map="auto",
            cache_dir=cache_dir
            
        )
        tokenizer = AutoTokenizer.from_pretrained(model_name,cache_dir=cache_dir)

        messages = [
            {"role": "system", "content": f"{instruction}"},
            {"role": "user", "content": f"Create comprehensive and high-quality technical documentation from Python source code: {mensagem}"}
        ]
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=max_new_tokens
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]



        end_time = time.perf_counter()
        print(end_time - start_time)
        #print(response)
        # docstring = extrair_codigo(response) 
        # print(docstring)
        # docstring = extrair_docstring(docstring)
        return response

    def CloudMdCreateContent(self, filepath, nameforenv):
        """
        Gera documentação técnica em formato Markdown a partir de código Python,
        utilizando um agente de IA autenticado.
        """
        try:
            if self.Logger:
                if self.lang == "eng":
                    cprint(f'🔐 Authenticating AI agent for documentation generation...', 'blue', attrs=['bold'])
                else:
                    cprint(f'🔐 Autenticando agente de IA para geração de documentação...', 'blue', attrs=['bold'])

            # Autenticação do agente de IA
            AI, instructionsassistant, nameassistant, model_select = AutenticateAgent.create_or_auth_AI(
                self.appfb, self.client, self.key, self.instruction, self.nameassistant, self.model_select, self.tools
            )

            if self.Logger:
                if self.lang == "eng":
                    cprint(f'✅ AI agent authenticated: {nameassistant} using model {model_select}', 'green')
                else:
                    cprint(f'✅ Agente de IA autenticado: {nameassistant} usando o modelo {model_select}', 'green')

            if self.Logger:
                if self.lang == "eng":
                    cprint('📤 Uploading files to the vector store...', 'yellow', attrs=['bold'])
                elif self.lang == "pt":
                    cprint('📤 Enviando arquivos para o repositório de vetores...', 'yellow', attrs=['bold'])

            AI = Agent_files_update.del_all_and_upload_files_in_vectorstore(self.appfb, self.client, AI, "CloudMd_Work_Environment", [filepath])

            if self.Logger:
                if self.lang == "eng":
                    cprint(f'✅ Files uploaded to vector store. AI updated: {AI}', 'yellow', attrs=['bold'])
                elif self.lang == "pt":
                    cprint(f'✅ Arquivos enviados para o repositório de vetores. AI atualizado: {AI}', 'yellow', attrs=['bold'])

            if self.lang == "eng":
                mensagem_final = f"""
                Create comprehensive and high-quality technical documentation from Python source code stored in `CloudMd_Work_Environment`
                Save the final file in `.md` format (using autosave) in the following path:
                **D:\\Company Apps\\Projetos de codigo aberto\\SoftwareAI\\softwareai\\CoreApp\\Agents\\Software_Documentation\\{nameforenv}\\Docs\\(NameBasedInSourceCode.md)**
                """
            else:
                mensagem_final = f"""
                Crie a documentação técnica abrangente e de alta qualidade a partir do código-fonte Python armazenado em `CloudMd_Work_Environment`
                Salve o arquivo final no formato `.md` (usando salvamento automático) no seguinte caminho:
                **D:\\Company Apps\\Projetos de codigo aberto\\SoftwareAI\\softwareai\\CoreApp\\Agents\\Software_Documentation\\{nameforenv}\\Docs\\(NameBasedInSourceCode.md)**
                """

            if self.Logger:
                if self.lang == "eng":
                    cprint(f'📝 Prepared prompt for documentation:\n{mensagem_final}', 'yellow')
                else:
                    cprint(f'📝 Prompt preparado para documentação:\n{mensagem_final}', 'yellow')

            adxitional_instructions = ""

            if self.Logger:
                if self.lang == "eng":
                    cprint(f'📤 Sending request to AI for documentation generation...', 'cyan')
                else:
                    cprint(f'📤 Enviando solicitação para IA gerar a documentação...', 'cyan')

            # Envio da mensagem para o agente de IA
            response, total_tokens, prompt_tokens, completion_tokens = ResponseAgent.ResponseAgent_message_with_assistants(
                mensagem=mensagem_final,
                agent_id=AI,
                key=self.key,
                app1=self.appfb,
                client=self.client,
                tools=self.tools,
                model_select=model_select,
                aditional_instructions=adxitional_instructions
            )

            if self.Logger:
                if self.lang == "eng":
                    cprint(f'📥 AI response received. Total tokens used: {total_tokens}', 'green')
                    cprint(f'🗒️ Documentation generated and saved for environment: {nameforenv}', 'green')
                else:
                    cprint(f'📥 Resposta da IA recebida. Total de tokens usados: {total_tokens}', 'green')
                    cprint(f'🗒️ Documentação gerada e salva para o ambiente: {nameforenv}', 'green')

            if self.DebugTokens:
                self.countNumberTokensTotal += total_tokens
                valor_min, valor_max = ResponseAgent.calculate_dollar_value(self.countNumberTokensTotal)
                if self.lang == "eng":
                    cprint(f'📜 Total Tokens Consumed: {self.countNumberTokensTotal} 💸${valor_min:.4f} and 💸${valor_max:.4f}', 'yellow', attrs=['bold'])
                elif self.lang == "pt":
                    cprint(f'📜 Total de Tokens Consumidos: {self.countNumberTokensTotal} 💸${valor_min:.4f} e 💸${valor_max:.4f}', 'yellow', attrs=['bold'])
                
        except Exception as e:
            if self.Logger:
                if self.lang == "eng":
                    cprint(f'❌ Error during documentation generation: {e}', 'red', attrs=['bold'])
                else:
                    cprint(f'❌ Erro durante a geração da documentação: {e}', 'red', attrs=['bold'])
            raise

    def Execute(self, softwarepath, nameforenv):
        """
        Executa o processo de cópia de arquivos .py e .MD de um diretório de software para diretórios específicos,
        e gera documentos Markdown a partir do conteúdo dos arquivos copiados.
        """
        try:
            # Caminho de destino para os códigos
            destpath = os.path.join(os.path.dirname(__file__), f"{nameforenv}", f"Codes")
            os.makedirs(destpath, exist_ok=True)
            
            if self.Logger:
                if self.lang == "eng":
                    cprint(f'📁 Created or confirmed existence of directory: {destpath}', 'green', attrs=['bold'])
                else:
                    cprint(f'📁 Diretório criado ou já existente: {destpath}', 'green', attrs=['bold'])
            
            # Caminho de destino para documentos
            nome_do_md = os.path.join(os.path.dirname(__file__), f"{nameforenv}", f"Docs") 
            os.makedirs(nome_do_md, exist_ok=True)
            
            if self.Logger:
                if self.lang == "eng":
                    cprint(f'📁 Created or confirmed existence of directory: {nome_do_md}', 'green', attrs=['bold'])
                else:
                    cprint(f'📁 Diretório criado ou já existente: {nome_do_md}', 'green', attrs=['bold'])

            # Listar arquivos .py e .MD no caminho do software
            listpy = [f for f in os.listdir(softwarepath) if f.endswith(('.py', '.MD'))]
            
            if self.Logger:
                if self.lang == "eng":
                    cprint(f'📄 Files to copy: {listpy}', 'cyan')
                else:
                    cprint(f'📄 Arquivos para copiar: {listpy}', 'cyan')

            # Copiar arquivos para o diretório de códigos
            for file in listpy:
                src_file = os.path.join(softwarepath, file)
                dest_file = os.path.join(destpath, file)
                shutil.copy(src_file, dest_file)
                
                if self.Logger:
                    if self.lang == "eng":
                        cprint(f'✅ Copied {file} to {dest_file}', 'green')
                    else:
                        cprint(f'✅ Arquivo {file} copiado para {dest_file}', 'green')

            # Listar novamente os arquivos copiados
            listpy = [f for f in os.listdir(destpath) if f.endswith(('.py', '.MD'))]
            
            # Processar cada arquivo copiado
            for py in listpy:
                nome_do_arquivo = os.path.join(destpath, py)
                nome_do_md = os.path.join(os.path.dirname(__file__), f"{nameforenv}", f"Docs", 
                                        f"{os.path.basename(nome_do_arquivo).replace('.md', '').replace('.MD', '').replace('.txt', '').replace('.py', '')}.md")

                if self.Logger:
                    if self.lang == "eng":
                        cprint(f'📖 Processing file: {nome_do_arquivo}', 'blue')
                    else:
                        cprint(f'📖 Processando arquivo: {nome_do_arquivo}', 'blue')

                with open(nome_do_arquivo, 'r+', encoding='utf-8') as file:
                    content = file.read()

                if self.Logger:
                    if self.lang == "eng":
                        cprint(f'🛠️ Generating Markdown from: {py}', 'yellow')
                    else:
                        cprint(f'🛠️ Gerando Markdown de: {py}', 'yellow')

                # Chamada para a função de geração de Markdown
                self.CloudMdCreateContent(nome_do_arquivo, nameforenv)

                if self.Logger:
                    if self.lang == "eng":
                        cprint(f'📄 Markdown generated for {py}', 'green')
                    else:
                        cprint(f'📄 Markdown gerado para {py}', 'green')

        except Exception as e:
            if self.Logger:
                if self.lang == "eng":
                    cprint(f'❌ Error during execution: {e}', 'red', attrs=['bold'])
                else:
                    cprint(f'❌ Erro durante a execução: {e}', 'red', attrs=['bold'])
            raise

CloudMdclass = CloudMd(appfb, client)
CloudMdclass.Execute(r"D:\Company Apps\Saas\Franquia Auto Rotate\Ivpnautorotate",  "Expressvpn_auto_rotate")