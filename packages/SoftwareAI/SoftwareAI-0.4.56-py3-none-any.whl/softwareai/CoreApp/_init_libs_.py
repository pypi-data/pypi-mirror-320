
#########################################
# IMPORT Libs
import importlib
import pkgutil
import os
import subprocess
import threading
import asyncio
import json
from firebase_admin import credentials, initialize_app, storage, db, delete_app
from openai import OpenAI
import time
import pandas as pd
import shutil
import tiktoken
from github import Github
import re
import requests
import base64
import random
from datetime import datetime, timedelta
import struct
from dotenv import load_dotenv, find_dotenv
import git
from requests.auth import HTTPBasicAuth
import sys
import json
import ast
import os
import subprocess
import platform
from firebase_admin import credentials, initialize_app, storage, db, delete_app
import concurrent.futures
from PySide2extn.RoundProgressBar import roundProgressBar #IMPORT THE EXTENSION LIBRARY
from PySide2.QtCore import QTimer, Signal, QThread
from PySide2.QtWidgets import QFileDialog
import sys
import json
import time
import os
import subprocess
import platform
from firebase_admin import credentials, initialize_app, storage, db, delete_app
import concurrent.futures
import hashlib
import schedule
from typing import Optional, List, Union
from typing_extensions import override
from openai import AssistantEventHandler, OpenAI
from openai.types.beta.threads import Text, TextDelta
from openai.types.beta.threads.runs import ToolCall, ToolCallDelta


from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.pdfgen import canvas
## IMPORTS Libs
import sys
import os
import subprocess
from typing import Dict, Any
import time
import psutil
import GPUtil
import math
import hashlib
from typing import Dict, Any
import os
import subprocess
import requests
import json
import requests
import re
from firebase_admin import credentials, initialize_app, storage, db, delete_app
import concurrent.futures
from reportlab.platypus import PageBreak
from reportlab.lib.colors import Color, black, white


from reportlab.platypus import PageBreak, Table, TableStyle,Preformatted, Image, Paragraph, HRFlowable, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.tableofcontents import TableOfContents

from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import BaseDocTemplate, Paragraph, PageBreak, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

import requests
import json
import random
import re
import os
import time
from firebase_admin import credentials, storage, db
import requests
import firebase_admin
import obsws_python as obs
from openai import OpenAI
import base64
import requests
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from termcolor import cprint


#########################################
