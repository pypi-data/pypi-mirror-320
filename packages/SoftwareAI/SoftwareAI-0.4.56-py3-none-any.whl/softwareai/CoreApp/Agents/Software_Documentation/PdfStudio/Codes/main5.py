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

from CoreApp.instruction import *
from CoreApp.toolspdf import *

class PdfStudio():
    """
    lang: Optional[str] = "pt"
    lang: Optional[str] = "eng" 
    """
    def __init__(self,
                NamePdf,
                Theme,
                Pages,
                Debug: Optional[bool] = True,
                DebugTokens: Optional[bool] = True,
                lang: Optional[str] = "pt"
                ):
        self.Pages = Pages
        self.Theme = Theme
        self.Debug = Debug
        self.DebugTokens = DebugTokens
        self.lang = lang
        self.NamePdf = NamePdf
        self.key = "ArchitectPDF"
        self.nameassistant = "Architect PDF"
        self.model_select = "ft:gpt-4o-mini-2024-07-18:personal:pdfcontent:Aoc3G92Y"
        self.Upload_1_file_in_thread = None
        self.Upload_1_file_in_message = None
        self.Upload_1_image_for_vision_in_thread = None
        self.Upload_list_for_code_interpreter_in_thread = None
        self.vectorstore_in_assistant = None
        self.vectorstore_in_Thread = None
        self.load_keys()
        self.key_openai = os.getenv("openai")
        self.name_app = "appx"

        if self.Debug:
            if self.lang == "eng":
                cprint(f'🔧 Initializing {self.nameassistant} with PDF name: {NamePdf}', 'yellow', attrs=['bold'])
            elif self.lang == "pt":
                cprint(f'🔧 Inicializando {self.nameassistant} com o nome do PDF: {NamePdf}', 'yellow', attrs=['bold'])
        
        self.appfb = FirebaseKeysinit._init_app_(self.name_app)
        self.client = OpenAIKeysinit._init_client_(self.key_openai)
        
        # Verificar a ativação do debug e mostrar a linguagem configurada
        if self.Debug:
            if self.lang == "eng":
                cprint(f'🌐 Language set to: {self.lang}', 'yellow', attrs=['bold'])
            elif self.lang == "pt":
                cprint(f'🌐 Linguagem definida como: {self.lang}', 'yellow', attrs=['bold'])

        
        self.TITLE_COLOR_MAP = {
            "Introdução": colors.blue,
            "Widgets": colors.green,
            "Layouts": colors.orange,
            "Conclusão": colors.red,
        }

        self.style_code = ParagraphStyle(
            'CodeStyle',
            fontName='Courier',
            fontSize=10,
            textColor=colors.black,
            backColor=colors.lightgrey,
            borderWidth=0.5,
            borderColor=colors.black,
            spaceAfter=6,
            spaceBefore=6,
        )
        
        self.style_title = ParagraphStyle(
            name='TitleStyle',
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=colors.white,
            backColor=colors.darkblue,
            alignment=1,
        )
        
        self.style_paragraph = ParagraphStyle(
            name='ParagraphStyle',
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.black,
            backColor=colors.white,
            spaceAfter=6,
            spaceBefore=6,
        )

        # Carregar variáveis de ambiente
        self.load_envwork()

    def load_keys(self):
        """
        Method to load the .env file located in the two folders above the script.
        """
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "keys.env"))
        if self.Debug:
            if self.lang == "eng":
                cprint(f'🔑 Loading .env file from: {env_path}', 'yellow', attrs=['bold'])
            elif self.lang == "pt":
                cprint(f'🔑 Carregando arquivo .env de: {env_path}', 'yellow', attrs=['bold'])
                
        if os.path.exists(env_path):
            load_dotenv(env_path)
            if self.Debug:
                if self.lang == "eng":
                    cprint(f'.env file loaded from: {env_path}', 'yellow', attrs=['bold'])
                elif self.lang == "pt":
                    cprint(f'.env carregado de: {env_path}', 'yellow', attrs=['bold'])
        else:
            if self.Debug:
                if self.lang == "eng":
                    cprint(f'❌ Error: .env file not found at {env_path}', 'red', attrs=['bold'])
                elif self.lang == "pt":
                    cprint(f'❌ Erro: Arquivo .env não encontrado em {env_path}', 'red', attrs=['bold'])

    def load_envwork(self):
        """
        Method to load the .env file located in the two folders above the script.
        """
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "envwork.env"))
        if self.Debug:
            if self.lang == "eng":
                cprint(f'🔑 Loading .env work file from: {env_path}', 'yellow', attrs=['bold'])
            elif self.lang == "pt":
                cprint(f'🔑 Carregando arquivo .env de trabalho de: {env_path}', 'yellow', attrs=['bold'])

        if os.path.exists(env_path):
            load_dotenv(env_path)
            if self.Debug:
                if self.lang == "eng":
                    cprint(f'.env work file loaded from: {env_path}', 'yellow', attrs=['bold'])
                elif self.lang == "pt":
                    cprint(f'.env de trabalho carregado de: {env_path}', 'yellow', attrs=['bold'])
        else:
            if self.Debug:
                if self.lang == "eng":
                    cprint(f'❌ Error: .env work file not found at {env_path}', 'red', attrs=['bold'])
                elif self.lang == "pt":
                    cprint(f'❌ Erro: Arquivo .env de trabalho não encontrado em {env_path}', 'red', attrs=['bold'])

    def save_TXT(self, string, filename, mode):
        """
        Saves a string to a file with the given mode.
        """
        if self.Debug:
            if self.lang == "eng":
                cprint(f'💾 Saving to file: {filename} with mode: {mode}', 'yellow', attrs=['bold'])
            elif self.lang == "pt":
                cprint(f'💾 Salvando no arquivo: {filename} com o modo: {mode}', 'yellow', attrs=['bold'])
        
        with open(filename, mode, encoding="utf-8") as file:
            file.write(f'{string}\n')

    def create_table(self, data):
        """
        Creates a table with the given data.
        """
        if self.Debug:
            if self.lang == "eng":
                cprint(f'📊 Creating table with {len(data)} rows of data', 'yellow', attrs=['bold'])
            elif self.lang == "pt":
                cprint(f'📊 Criando tabela com {len(data)} linhas de dados', 'yellow', attrs=['bold'])
        
        table = Table(data, colWidths=[100, 300])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),  
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        return table
    
    def process_text_with_styles(self, content):
        # Processar estilos inline
        content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', content)
        content = re.sub(r'\_(.*?)\_', r'<i>\1</i>', content)
        content = re.sub(r'\~\~(.*?)\~\~', r'<strike>\1</strike>', content)
        
        # Corrigir a ordem de fechamento para <font> e <b>
        content = re.sub(r'(?<=###)(.*)', r'<font name="Helvetica-Bold" color="darkblue">\1</font>', content)
        content = re.sub(r'(?<=##)(.*)', r'<font name="Helvetica-Bold" color="darkblue">\1</font>', content)
        content = re.sub(r'(?<=\*)(.*?)\*', r'<b>\1</b>', content)

        # Processar marcadores de lista
        if content.strip().startswith('- '):
            content = '• ' + content[2:]

        # Outros ajustes de estilo
        content = content.replace("###", "").replace("##", "")

        return content

    def get_contrasting_color(self, bg_color):
        """
        Retorna uma cor contrastante (preto ou branco) com base na luminosidade da cor de fundo.
        """
        # Fórmula para luminosidade perceptiva
        luminosity = (0.299 * bg_color.red + 0.587 * bg_color.green + 0.114 * bg_color.blue)
        
        if self.Debug:
            if self.lang == "eng":
                cprint(f'🌈 Calculating contrast color for background color: {bg_color}', 'yellow', attrs=['bold'])
                cprint(f'   Luminosity calculated: {luminosity}', 'yellow', attrs=['bold'])
            elif self.lang == "pt":
                cprint(f'🌈 Calculando cor de contraste para a cor de fundo: {bg_color}', 'yellow', attrs=['bold'])
                cprint(f'   Luminosidade calculada: {luminosity}', 'yellow', attrs=['bold'])
        
        # Retornar preto ou branco com base na luminosidade
        contrast_color = black if luminosity > 0.5 else white
        
        if self.Debug:
            if self.lang == "eng":
                cprint(f'✔️ Contrast color chosen: {contrast_color}', 'yellow', attrs=['bold'])
            elif self.lang == "pt":
                cprint(f'✔️ Cor de contraste escolhida: {contrast_color}', 'yellow', attrs=['bold'])
        
        return contrast_color

    def set_background_and_text(self, canvas_obj, doc, bg_color):
        """
        Define o fundo e ajusta a cor do texto para contraste.
        """
        # Configurar fundo
        # width, height = A4
        # canvas_obj.setFillColor(bg_color)
        # canvas_obj.rect(0, 0, width, height, fill=1)

        # Obter cor do texto contrastante
        # text_color = get_contrasting_color(bg_color)
        # canvas_obj.setFillColor(text_color)
        canvas_obj.setFont("Helvetica-Bold", 12)

    def add_page_number(self, canvas_obj, doc):
        """
        Adiciona o número da página no canto inferior esquerdo ou direito, ignorando certas páginas
        e reiniciando a contagem a partir da página 3.
        """
        page_number = canvas_obj.getPageNumber()

        # Log sobre o número da página e a verificação das páginas a serem ignoradas
        if self.Debug:
            if self.lang == "eng":
                cprint(f'📄 Page number: {page_number}. Checking if it should be skipped...', 'yellow', attrs=['bold'])
            elif self.lang == "pt":
                cprint(f'📄 Número da página: {page_number}. Verificando se deve ser ignorada...', 'yellow', attrs=['bold'])

        # Ignorar a página do índice (1) e do autor (2)
        if page_number in [1, 2]:
            if self.Debug:
                if self.lang == "eng":
                    cprint(f'❌ Skipping page {page_number} (index or author page)', 'yellow', attrs=['bold'])
                elif self.lang == "pt":
                    cprint(f'❌ Ignorando a página {page_number} (índice ou página do autor)', 'yellow', attrs=['bold'])
            return

        # Ajustar a contagem para iniciar do 1 na página 3
        relative_page_number = page_number - 2

        # Configurar posição: esquerda ou direita
        width, height = A4
        x_position = random.choice([50, width - 75])
        y_position = 30  # Margem inferior

        # Log sobre a posição e o número da página
        if self.Debug:
            if self.lang == "eng":
                cprint(f'🖋️ Placing page number {relative_page_number} at position ({x_position}, {y_position})', 'yellow', attrs=['bold'])
            elif self.lang == "pt":
                cprint(f'🖋️ Colocando o número da página {relative_page_number} na posição ({x_position}, {y_position})', 'yellow', attrs=['bold'])

        # Configurar fonte em negrito e tamanho
        canvas_obj.setFont("Helvetica-Bold", 10)

        # Adicionar o número da página ajustado
        canvas_obj.drawString(x_position, y_position, f"Página {relative_page_number}")

        if self.Debug:
            if self.lang == "eng":
                cprint(f'✔️ Page number {relative_page_number} added successfully.', 'yellow', attrs=['bold'])
            elif self.lang == "pt":
                cprint(f'✔️ Número da página {relative_page_number} adicionado com sucesso.', 'yellow', attrs=['bold'])

    def on_page(self, canvas, doc):
        """
        Função de callback chamada para cada página do documento.
        Adiciona margens coloridas e números de página.
        """
        title = getattr(doc, 'current_title', '')
        
        # Log sobre o título atual
        if self.Debug:
            if self.lang == "eng":
                cprint(f'📚 Current page title: {title}', 'yellow', attrs=['bold'])
            elif self.lang == "pt":
                cprint(f'📚 Título da página atual: {title}', 'yellow', attrs=['bold'])

        # Escolher a cor da margem com base no título (exemplo de cor baseada no título)
        if title.startswith("Introdução"):
            canvas.setStrokeColorRGB(0.8, 0.2, 0.2)  # Cor vermelha
            margin_color = 'red'
        else:
            canvas.setStrokeColorRGB(0.2, 0.2, 0.8)  # Cor azul
            margin_color = 'blue'

        # Log sobre a cor da margem
        if self.Debug:
            if self.lang == "eng":
                cprint(f'🎨 Set page margin color to {margin_color}', 'yellow', attrs=['bold'])
            elif self.lang == "pt":
                cprint(f'🎨 Cor da margem da página definida para {margin_color}', 'yellow', attrs=['bold'])

        # Desenhar a borda da página (margem colorida)
        width, height = A4
        canvas.setLineWidth(5)
        canvas.rect(10, 10, width - 20, height - 20)

        # Definir cor de fundo
        self.set_background_and_text(canvas, doc, bg_color=Color(0.5, 0.7, 0.9))    

        # Adicionar o número da página no canto inferior esquerdo ou direito de forma aleatória
        self.add_page_number(canvas, doc)

    def get_color_by_title(self, title):
        """
        Retorna a cor correspondente ao título. Caso o título não esteja no mapa, retorna uma cor padrão.
        """
        if self.Debug:
            if self.lang == "eng":
                cprint(f'🎨 Getting color for title: {title}', 'yellow', attrs=['bold'])
            elif self.lang == "pt":
                cprint(f'🎨 Obtendo a cor para o título: {title}', 'yellow', attrs=['bold'])

        for key in self.TITLE_COLOR_MAP:
            if key in title:
                if self.Debug:
                    if self.lang == "eng":
                        cprint(f'✔️ Found matching color for title: {key}', 'yellow', attrs=['bold'])
                    elif self.lang == "pt":
                        cprint(f'✔️ Cor correspondente ao título encontrada: {key}', 'yellow', attrs=['bold'])
                return self.TITLE_COLOR_MAP[key]

        # Cor padrão
        if self.Debug:
            if self.lang == "eng":
                cprint(f'⚠️ No specific color found for title, returning default color.', 'yellow', attrs=['bold'])
            elif self.lang == "pt":
                cprint(f'⚠️ Nenhuma cor específica encontrada para o título, retornando cor padrão.', 'yellow', attrs=['bold'])

        return colors.grey  # Cor padrão
    
    def draw_colored_margins(self, canvas, doc, color):
        """
        Desenha margens coloridas no PDF com base na cor fornecida.
        """
        if self.Debug:
            if self.lang == "eng":
                cprint(f'🎨 Drawing colored margins with color: {color}', 'yellow', attrs=['bold'])
            elif self.lang == "pt":
                cprint(f'🎨 Desenhando margens coloridas com a cor: {color}', 'yellow', attrs=['bold'])

        canvas.saveState()
        margin_width = 10  # Largura da margem
        page_width, page_height = A4
        
        # Desenhar margens coloridas
        canvas.setFillColor(color)
        canvas.rect(0, 0, margin_width, page_height, fill=True)  # Margem esquerda
        canvas.rect(page_width - margin_width, 0, margin_width, page_height, fill=True)  # Margem direita
        canvas.rect(0, page_height - margin_width, page_width, margin_width, fill=True)  # Margem superior
        canvas.rect(0, 0, page_width, margin_width, fill=True)  # Margem inferior
        
        canvas.restoreState()

        if self.Debug:
            if self.lang == "eng":
                cprint(f'✔️ Colored margins drawn successfully.', 'yellow', attrs=['bold'])
            elif self.lang == "pt":
                cprint(f'✔️ Margens coloridas desenhadas com sucesso.', 'yellow', attrs=['bold'])
    
    def create_section(self, doc, title, section_id):
        # Estilo da seção
        styles = getSampleStyleSheet()
        section_style = ParagraphStyle(
            'SectionStyle',
            parent=styles['Heading2'],
            fontSize=12,
            leading=14,
            spaceBefore=12,
            spaceAfter=6
        )

        # Criando a seção com o ID de navegação
        section = Paragraph(f'<a name="section_{section_id}"/>{title}', section_style)
        doc.build([section])
        
    def create_contents_page(self, doc, titles):
        if self.Debug:
            if self.lang == "eng":
                cprint(f'📑 Creating contents page with {len(titles)} titles...', 'yellow', attrs=['bold'])
            elif self.lang == "pt":
                cprint(f'📑 Criando a página de índice com {len(titles)} títulos...', 'yellow', attrs=['bold'])

        styles = getSampleStyleSheet()

        # Estilo para o título do índice
        title_style = ParagraphStyle(
            'ContentsTitle',
            parent=styles['Heading1'],
            fontSize=14,
            leading=16,
            textColor=colors.darkblue,
            spaceAfter=12,
            alignment=1  # Centraliza o título
        )

        # Estilo para os itens do índice
        entry_style = ParagraphStyle(
            'ContentsEntry',
            parent=styles['BodyText'],
            fontSize=10,
            leading=12,
            leftIndent=20,
            textColor=colors.blue,
            spaceBefore=6
        )

        elements = []

        # Título do Índice
        elements.append(Paragraph("Índice", title_style))
        elements.append(Spacer(1, 18))

        # Adicionar entradas do índice com links clicáveis
        for idx, title in enumerate(titles, 1):
            entry_text = f'{idx}. <link color="blue" href="#section_{idx}">{title}</link>'
            entry = Paragraph(entry_text, entry_style)
            elements.append(entry)
            elements.append(Spacer(1, 6))

        elements.append(PageBreak())

        if self.Debug:
            if self.lang == "eng":
                cprint(f'✔️ Contents page created successfully.', 'yellow', attrs=['bold'])
            elif self.lang == "pt":
                cprint(f'✔️ Página de índice criada com sucesso.', 'yellow', attrs=['bold'])

        return elements
    def get_random_image(self, image_folder):
        """Seleciona uma imagem aleatória da pasta fornecida."""
        if self.Debug:
            if self.lang == "eng":
                cprint(f'📸 Selecting a random image from folder: {image_folder}', 'yellow', attrs=['bold'])
            elif self.lang == "pt":
                cprint(f'📸 Selecionando uma imagem aleatória da pasta: {image_folder}', 'yellow', attrs=['bold'])

        images = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
        selected_image = random.choice(images) if images else None

        if selected_image:
            if self.Debug:
                if self.lang == "eng":
                    cprint(f'✔️ Image selected: {selected_image}', 'yellow', attrs=['bold'])
                elif self.lang == "pt":
                    cprint(f'✔️ Imagem selecionada: {selected_image}', 'yellow', attrs=['bold'])
        else:
            if self.Debug:
                if self.lang == "eng":
                    cprint(f'⚠️ No images found in folder: {image_folder}', 'yellow', attrs=['bold'])
                elif self.lang == "pt":
                    cprint(f'⚠️ Nenhuma imagem encontrada na pasta: {image_folder}', 'yellow', attrs=['bold'])

        return selected_image

    def create_pdf(self, content, filename, image_folder=None):
        if self.Debug:
            if self.lang == "eng":
                cprint(f'📋 Creating PDF: {filename}', 'yellow', attrs=['bold'])
            elif self.lang == "pt":
                cprint(f'📋 Criando PDF: {filename}', 'yellow', attrs=['bold'])

        # Step 1: Set up document and page template
        if self.Debug:
            if self.lang == "eng":
                cprint('📝 Setting up the document and page template...', 'yellow', attrs=['bold'])
            elif self.lang == "pt":
                cprint('📝 Configurando o documento e o template da página...', 'yellow', attrs=['bold'])

        doc = BaseDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=90,
            leftMargin=90,
            topMargin=70,
            bottomMargin=90,
        )

        frame = Frame(
            doc.leftMargin,
            doc.bottomMargin,
            doc.width,
            doc.height,
            id='normal'
        )
        doc.addPageTemplates([PageTemplate(id='Main', frames=frame, onPage=self.on_page)])

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=11,
            textColor=colors.darkblue,
            spaceAfter=5,
            spaceBefore=5
        )

        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=9,
            leading=11,
            spaceAfter=4,
            wordWrap='CJK'
        )

        code_style = ParagraphStyle(
            'CodeStyle',
            fontName='Courier',  # Fonte monoespaçada
            fontSize=10,
            textColor=colors.black,
            backColor=colors.lightgrey,  # Fundo cinza claro para destacar o código
            spaceBefore=6,
            spaceAfter=6,
            leftIndent=10,
            rightIndent=10,
            borderWidth=1,
            borderColor=colors.grey,
            borderPadding=4,
            borderRadius=4,
        )

        elements = []
        titles = []

        # Step 2: Split content into parts and identify section titles
        if self.Debug:
            if self.lang == "eng":
                cprint('🔍 Splitting content into sections and identifying titles...', 'yellow', attrs=['bold'])
            elif self.lang == "pt":
                cprint('🔍 Dividindo o conteúdo em seções e identificando os títulos...', 'yellow', attrs=['bold'])

        parts = re.split(r'---', content)
        for part in parts:
            lines = part.strip().split('\n')
            for line in lines:
                if line.startswith("### "):
                    titles.append(line[4:])
        
        elements.extend(self.create_contents_page(doc, titles))

        current_section = 0
        image_added = False

        # Step 3: Process content, add titles, and insert code blocks
        if self.Debug:
            if self.lang == "eng":
                cprint('📖 Processing content and adding sections...', 'yellow', attrs=['bold'])
            elif self.lang == "pt":
                cprint('📖 Processando conteúdo e adicionando seções...', 'yellow', attrs=['bold'])

        for part in parts:
            lines = part.strip().split('\n')

            code_lines = []  # To store the code block content
            in_code_block = False  # Flag to check if we're inside a code block

            for line in lines:
                if line.startswith("### "):
                    current_section += 1
                    title = line[4:]
                    doc.current_title = title

                    if self.Debug:
                        if self.lang == "eng":
                            cprint(f'📌 Section {current_section}: {title}', 'yellow', attrs=['bold'])
                        elif self.lang == "pt":
                            cprint(f'📌 Seção {current_section}: {title}', 'yellow', attrs=['bold'])

                    if not image_added:
                        image_path = self.get_random_image(image_folder)
                        if image_path:
                            img = Image(image_path, width=150, height=150)
                            table_data = [[img, Paragraph(f'<a name="section_{current_section}"/>{title}', title_style)]]
                            table = Table(table_data, colWidths=[160, doc.width - 180])
                            table.setStyle(TableStyle([
                                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                ('LEFTPADDING', (0, 0), (0, 0), 0),
                                ('RIGHTPADDING', (1, 0), (1, 0), 0)
                            ]))
                            elements.append(table)
                            image_added = True
                        else:
                            elements.append(Paragraph(f'<a name="section_{current_section}"/>{title}', title_style))
                    else:
                        elements.append(Paragraph(f'<a name="section_{current_section}"/>{title}', title_style))

                elif line.startswith("```python"):
                    in_code_block = True
                    code_lines = []  # Reset code lines

                elif in_code_block:
                    if line.startswith("```"):
                        in_code_block = False
                        code_content = '\n'.join(code_lines)
                        elements.append(Preformatted(code_content, code_style))  # Add code block
                        if self.Debug:
                            if self.lang == "eng":
                                cprint(f'🔲 Code block added: {code_content[:30]}...', 'yellow', attrs=['bold'])  # Preview the first 30 chars
                            elif self.lang == "pt":
                                cprint(f'🔲 Bloco de código adicionado: {code_content[:30]}...', 'yellow', attrs=['bold'])
                    else:
                        code_lines.append(line)

                else:
                    processed_line = self.process_text_with_styles(line)
                    if processed_line.strip():
                        elements.append(Paragraph(processed_line, body_style))

            elements.append(PageBreak())

        if elements and isinstance(elements[-1], PageBreak):
            elements.pop()

        # Step 4: Build the PDF document
        if self.Debug:
            if self.lang == "eng":
                cprint(f'✅ PDF build process completed successfully: {filename}', 'yellow', attrs=['bold'])
            elif self.lang == "pt":
                cprint(f'✅ Processo de criação do PDF concluído com sucesso: {filename}', 'yellow', attrs=['bold'])

        doc.build(elements)

    def create_content(self):
        countNumberTokensTotal = 0
        for i in range(self.Pages):
                
            if self.Debug:
                if self.lang == "eng":
                    cprint(f'📋 Function Creating Content Initialized', 'yellow', attrs=['bold'])
                elif self.lang == "pt":
                    cprint(f'📋 Função Criando Conteúdo Inicializada', 'yellow', attrs=['bold'])

            # Step 1: Authenticate and create AI agent
            if self.Debug:
                if self.lang == "eng":
                    cprint('🔑 Authenticating AI agent and creating or updating AI...', 'yellow', attrs=['bold'])
                elif self.lang == "pt":
                    cprint('🔑 Autenticando agente AI e criando ou atualizando AI...', 'yellow', attrs=['bold'])
            
            AI, instructionsassistant, nameassistant, model_select = AutenticateAgent.create_or_auth_AI(self.appfb, self.client, self.key, instruction, self.nameassistant, self.model_select)

            if self.Debug:
                if self.lang == "eng":
                    cprint(f'🤖 AI Agent created: {AI} | Model selected: {model_select}', 'yellow', attrs=['bold'])
                elif self.lang == "pt":
                    cprint(f'🤖 Agente AI criado: {AI} | Modelo selecionado: {model_select}', 'yellow', attrs=['bold'])

            # Step 2: List and process script files
            if self.Debug:
                if self.lang == "eng":
                    cprint('📂 Listing script files from "roteiro" directory...', 'yellow', attrs=['bold'])
                elif self.lang == "pt":
                    cprint('📂 Listando arquivos de roteiro do diretório "roteiro"...', 'yellow', attrs=['bold'])

            listaroteiros = os.listdir(os.path.join(os.path.dirname(__file__), "CoreApp", "Qprocess", "roteiro"))
            file_paths = []
            if not listaroteiros:
                pass
            else:
                for roteiro in listaroteiros:
                    pathabstract = os.path.abspath(os.path.join(os.path.dirname(__file__), "CoreApp", "Qprocess", "roteiro", f"{roteiro}"))
                    file_paths.append(pathabstract)
                    if self.Debug:
                        if self.lang == "eng":
                            cprint(f'📄 Found script file: {roteiro} | Path: {pathabstract}', 'yellow', attrs=['bold'])
                        elif self.lang == "pt":
                            cprint(f'📄 Arquivo de roteiro encontrado: {roteiro} | Caminho: {pathabstract}', 'yellow', attrs=['bold'])

                # Step 3: Upload files to the vector store
                if self.Debug:
                    if self.lang == "eng":
                        cprint('📤 Uploading files to the vector store...', 'yellow', attrs=['bold'])
                    elif self.lang == "pt":
                        cprint('📤 Enviando arquivos para o repositório de vetores...', 'yellow', attrs=['bold'])

                AI = Agent_files_update.del_all_and_upload_files_in_vectorstore(self.appfb, self.client, AI, "Pdf_Work_Environment", file_paths)

                if self.Debug:
                    if self.lang == "eng":
                        cprint(f'✅ Files uploaded to vector store. AI updated: {AI}', 'yellow', attrs=['bold'])
                    elif self.lang == "pt":
                        cprint(f'✅ Arquivos enviados para o repositório de vetores. AI atualizado: {AI}', 'yellow', attrs=['bold'])

            # Step 4: Prepare the message and additional instructions

            mensagem = f"""
            Por favor, analise cuidadosamente os conteúdos já criados e armazenados em `Pdf_Work_Environment` e continue a elaboração do documento com novas páginas que mantenham a coesão e consistência com o material existente. Crie e salve o conteúdo em formato `.txt` (usando autosave), garantindo que o documento completo tenha no mínimo **20.000 caracteres**. O conteúdo deve ser detalhado, bem estruturado e adequado para inclusão no PDF. Siga as instruções abaixo:

            1. **Expansão aprofundada do tema sobre {self.Theme}**, ampliando conceitos já abordados e introduzindo novos tópicos relevantes com profundidade e clareza.  
            2. **Introdução clara e objetiva** que contextualize a nova seção, destacando a importância do tema e preparando o leitor para o conteúdo.  
            3. **Seções bem organizadas** com títulos e subtítulos coerentes com o padrão existente, garantindo fluidez e fácil compreensão. Cada seção deve conter conteúdo extenso, detalhado e explicativo, contribuindo para atingir o total mínimo de 20.000 caracteres.  
            4. **Inclusão de exemplos práticos, listas e estudos de caso** que reforcem os conceitos apresentados, mostrando a aplicabilidade real do conteúdo.  
            5. **Conclusão reflexiva e completa**, que resuma os principais pontos abordados e proponha próximos passos ou reflexões adicionais.

            Salve o arquivo final em formato `.txt` (usando autosave) no seguinte caminho:  
            **D:\\Company Apps\\Projetos de codigo aberto\\Pdf Studio\\CoreApp\\Qprocess\\roteiro\\(NomeGeradoPaginax)**
            
            """
            adxitional_instructions_pdf = f"""

            """

            mensagem_final = mensagem 

            # Step 5: Call the response agent
            if self.Debug:
                if self.lang == "eng":
                    cprint('📝 Sending the request to the response agent...', 'yellow', attrs=['bold'])
                elif self.lang == "pt":
                    cprint('📝 Enviando a solicitação ao agente de resposta...', 'yellow', attrs=['bold'])

            response, total_tokens, prompt_tokens, completion_tokens = ResponseAgent.ResponseAgent_message_with_assistants(
                mensagem=mensagem_final,
                agent_id=AI, 
                key=self.key,
                app1=self.appfb,
                client=self.client,
                tools=tools_pdf,
                model_select=model_select,
                aditional_instructions=adxitional_instructions_pdf
            )

            if self.DebugTokens:
                valor_min, valor_max = ResponseAgent.calculate_dollar_value(total_tokens)
                if self.lang == "eng":
                    cprint(f'📜 Tokens consumed in the document: {total_tokens} 💸${valor_min:.4f} and 💸${valor_max:.4f}', 'yellow', attrs=['bold'])
                elif self.lang == "pt":
                    cprint(f'📜 Tokens Consumidos no documento : {total_tokens} 💸${valor_min:.4f} e 💸${valor_max:.4f}', 'yellow', attrs=['bold'])
                
                countNumberTokensTotal += total_tokens
                valor_min, valor_max = ResponseAgent.calculate_dollar_value(countNumberTokensTotal)
                if self.lang == "eng":
                    cprint(f'📜 Total Tokens Consumed: {countNumberTokensTotal} 💸${valor_min:.4f} and 💸${valor_max:.4f}', 'yellow', attrs=['bold'])
                elif self.lang == "pt":
                    cprint(f'📜 Total de Tokens Consumidos: {countNumberTokensTotal} 💸${valor_min:.4f} e 💸${valor_max:.4f}', 'yellow', attrs=['bold'])
                
            # Final status
            if self.Debug:
                if self.lang == "eng":
                    cprint('✅ Content creation process completed successfully!', 'yellow', attrs=['bold'])
                elif self.lang == "pt":
                    cprint('✅ Processo de criação de conteúdo concluído com sucesso!', 'yellow', attrs=['bold'])

    def compile_content(self, folder_path, output_pdf):
        # Log inicial para indicar o começo da função
        if self.Debug:
            if self.lang == "eng":
                cprint(f'📂 Compiling content from folder: {folder_path}', 'yellow', attrs=['bold'])
            elif self.lang == "pt":
                cprint(f'📂 Compilando conteúdo da pasta: {folder_path}', 'yellow', attrs=['bold'])

        # Coletar todos os arquivos .txt
        txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
        txt_files.sort()  # Ordenar os arquivos

        if self.Debug:
            if self.lang == "eng":
                cprint(f'🔎 Found {len(txt_files)} .txt files.', 'yellow', attrs=['bold'])
            elif self.lang == "pt":
                cprint(f'🔎 Encontrados {len(txt_files)} arquivos .txt.', 'yellow', attrs=['bold'])

        # Unir o conteúdo de todos os arquivos
        content = ""
        for file_name in txt_files:
            file_path = os.path.join(folder_path, file_name)

            if self.Debug:
                if self.lang == "eng":
                    cprint(f'📄 Reading file: {file_name}', 'yellow', attrs=['bold'])
                elif self.lang == "pt":
                    cprint(f'📄 Lendo o arquivo: {file_name}', 'yellow', attrs=['bold'])

            with open(file_path, 'r', encoding='utf-8') as file:
                content += file.read() + '\n\n'

        # Gerar PDF
        if self.Debug:
            if self.lang == "eng":
                cprint(f'📚 Generating PDF: {output_pdf}', 'yellow', attrs=['bold'])
            elif self.lang == "pt":
                cprint(f'📚 Gerando PDF: {output_pdf}', 'yellow', attrs=['bold'])

        self.create_pdf(content, output_pdf)

        # Log final indicando que o processo de criação do PDF foi concluído
        if self.Debug:
            if self.lang == "eng":
                cprint(f'✅ PDF generation completed: {output_pdf}', 'yellow', attrs=['bold'])
            elif self.lang == "pt":
                cprint(f'✅ Geração do PDF concluída: {output_pdf}', 'yellow', attrs=['bold'])

    def execute(self):
       # PdfStudioclass.create_content()
        PdfStudioclass.compile_content(os.path.join(os.path.dirname(__file__),  "CoreApp", "Qprocess", "roteiro"), os.path.join(os.path.dirname(__file__),  "CoreApp", "Qprocess", "completo", f"{self.NamePdf}.pdf"))

NamePdf = "Pyqt5"
Theme = "Py qt5"
Pages = 2
PdfStudioclass = PdfStudio(NamePdf, Theme, Pages)
PdfStudioclass.execute()

#

# create_pdf(response, r"CoreApp\process\pdf\roteiro.pdf", r"CoreApp\resources\Images")