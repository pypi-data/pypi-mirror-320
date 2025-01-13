

########################################################################

import sys
import os
import ctypes
import shutil
import subprocess
import time
########################################################################


# from src_ import icons_interpreter

########################################################################
# IMPORT GUI 
from src_.ui_installer import *
########################################################################

########################################################################
# IMPORT Custom widgets
from Custom_Widgets import *
from Custom_Widgets.QAppSettings import QAppSettings
from Custom_Widgets.QCustomModals import QCustomModals
########################################################################

########################################################################
# IMPORT CoreApp
#from QInstaller import Qinstaller
########################################################################

from src_.icones_interpreter import *


########################################################################
# IMPORT Pyside2
from PySide2extn.RoundProgressBar import roundProgressBar #IMPORT THE EXTENSION LIBRARY
from PySide2.QtCore import QTimer, Signal, QThread
from PySide2 import QtCore

########################################################################

########################################################################
import shutil
import os
import concurrent.futures
import winshell
from win32com.client import Dispatch
import pythoncom
import sys
import ctypes
import zipfile
########################################################################

class Qinstaller(QThread):
    progress = Signal(int)
    label_path_src_installing = Signal(str)
    finish = Signal()
    updatesucess = Signal(str)
    def __init__(self,
                lineEdit_path_install,
                path_exe,
                path_software,
                path_IVPNClient,
                destinIVPNClient,
                path_Python,
                destinPython
                ):
        super().__init__()
        self.lineEdit_path_install = lineEdit_path_install
        self.path_exe = path_exe
        self.path_software = path_software
        self.path_IVPNClient = path_IVPNClient
        self.destinIVPNClient = destinIVPNClient
        self.path_Python = path_Python
        self.destinPython = destinPython 



    def run(self):
   
        path_destin = rf"{self.lineEdit_path_install}"
        caminho_exe = self.path_exe
        self.createshortcut(caminho_exe, "Sua rotação de ip com 1 click")
        files_to_copy = []
        for root, _, files in os.walk(self.path_software):
            for file in files:
                full_path = os.path.join(root, file)
                files_to_copy.append(full_path)
        total_files = len(files_to_copy)
        copied_files = 0
        def copy_file(src_file):
            nonlocal copied_files
            relative_path = os.path.relpath(src_file, self.path_software)
            dest_file = os.path.join(path_destin, relative_path)
            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
            shutil.copy2(src_file, dest_file)
            self.label_path_src_installing.emit(dest_file)
            copied_files += 1
            progress_percent = int((copied_files / total_files) * 100)
            self.progress.emit(progress_percent)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(copy_file, files_to_copy)

        files_to_copy = []
        for root, _, files in os.walk(self.path_IVPNClient):
            for file in files:
                full_path = os.path.join(root, file)
                files_to_copy.append(full_path)
        total_files = len(files_to_copy)
        copied_files = 0
        def copy_file(src_file):
            nonlocal copied_files
            relative_path = os.path.relpath(src_file, self.path_IVPNClient)
            dest_file = os.path.join(self.destinIVPNClient, relative_path)
            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
            shutil.copy2(src_file, dest_file)
            self.label_path_src_installing.emit(dest_file)
            copied_files += 1
            progress_percent = int((copied_files / total_files) * 100)
            self.progress.emit(progress_percent)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(copy_file, files_to_copy)

        os.makedirs(self.destinPython, exist_ok=True)

        # Extract the contents of the zip file with progress
        with zipfile.ZipFile(self.path_Python, 'r') as zip_ref:
            total_files = len(zip_ref.infolist())
            for index, file_info in enumerate(zip_ref.infolist(), start=1):
                zip_ref.extract(file_info, self.destinPython)

                # Emit signals
                self.progress.emit(int((index / total_files) * 100))
                self.label_path_src_installing.emit(f"{self.destinPython}\\{file_info.filename}")

        self.progress.emit(100)
        self.finish.emit()

    def createshortcut(self, caminho_exe, descricao=None):
        try:
            pythoncom.CoInitialize() 
            shell = Dispatch('WScript.Shell')
            desktop = shell.SpecialFolders("Desktop")
            nome_arquivo = os.path.splitext(os.path.basename(caminho_exe))[0]  
            caminho_atalho = os.path.join(desktop, nome_arquivo + ".lnk")
            atalho = shell.CreateShortcut(caminho_atalho)
            atalho.TargetPath = caminho_exe
            atalho.WorkingDirectory = os.path.dirname(caminho_exe)
            atalho.Description = descricao if descricao else "Atalho para " + nome_arquivo
            atalho.Save()
            self.updatesucess.emit(f"Shortcut successfully created on the desktop!!")
        except Exception as e:
            pass
        finally:
            pythoncom.CoUninitialize()  

def ensure_admin():
    """Ensure the script is running with administrator privileges."""
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("The script requires administrator privileges. Restarting as administrator...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, '"' + '" "'.join(sys.argv) + '"', None, 1)
        sys.exit(0)
########################################################################
# MainWindow
class Main_Window(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.AppName = "IVPN Auto Rotate"
        self.AppSpace = "3,19 - 5,10 GB"

        loadJsonStyle(self, self.ui, jsonFiles = {"JsonStyle/style.json"})
        self.stackedWidget = self.ui.stackedWidget 
        self.progressBar = self.ui.progressBar
        self.label_4 = self.ui.label_4
        self.label_7 = self.ui.label_7
        self.label_8 = self.ui.label_8

        self.Tosearchfor = self.ui.Tosearchfor
        self.Tosearchfor.clicked.connect(self.filedialogsearchpath)

        self.lineEdit_path_install = self.ui.lineEdit_path_install
        self.label_space_required = self.ui.label_space_required
        self.Button_next = self.ui.Button_next
        self.Button_next.clicked.connect(self.Button_nextclick_)
        self.button_cancel = self.ui.button_cancel
        self.button_cancel.clicked.connect(self.button_cancelclick_)
        self.label_path_src_installing = self.ui.label_path_src_installing
        self.pushButton_cancel_installing = self.ui.pushButton_cancel_installing
        self.pushButton_cancel_installing.clicked.connect(self.button_cancelclick_)
        self.pushButton_finish_installer = self.ui.pushButton_finish_installer
        self.pushButton_finish_installer.clicked.connect(self.button_pushButton_finish_installer_)
        self.checkBoxRun = self.ui.checkBoxRun

        self.label_space_required.setText(F"At least {self.AppSpace} of free disk space is required.")
        self.label_7.setText(f"Installer {self.AppName}")
        self.label_8.setText(f"The Installer has finished installing {self.AppName} on your computer.<br>  The application can be launched by selecting installed shortcuts.")
        self.lineEdit_path_install.setPlainText(F"C:\Program Files\{self.AppName}")
        self.label_4.setText(F"Installing <br> Please wait while the installer installs {self.AppName} on your computer.")

        try:
            os.makedirs(rf"C:\Program Files\{self.AppName}", exist_ok=True)
        except:
            pass
        
        #QAppSettings.updateAppSettings(self)




    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def button_pushButton_finish_installer_(self):
        if self.checkBoxRun.isChecked:
            path = "C:/Program Files/IVPN Auto Rotate"
            os.chdir(path)
            os.system("IVPNAutoRotate.exe")
           
        self.close()

    def button_cancelclick_(self):
        self.close()

    def Button_nextclick_(self):
        self.stackedWidget.slideToNextWidget()

        diretorio_script = os.path.dirname(os.path.abspath(__file__))
        path_exe = os.path.join(diretorio_script, 'DataApp','IVPN Auto Rotate', 'IVPNAutoRotate.exe')
        path_software = os.path.join(diretorio_script, 'DataApp', 'IVPN Auto Rotate')
        self.selected_path = self.lineEdit_path_install.toPlainText()
        path_IVPNClient = os.path.join(diretorio_script, 'DataApp', 'IVPN Client')
        destinIVPNClient = "C:\\Program Files\\IVPN Client"
        path_Python = os.path.join(diretorio_script, 'DataApp', 'Python.zip')
        destinPython = "C:\\Program Files\\IVPN Auto Rotate\\Dependenc"
        
        self.QInstaller_class = Qinstaller(self.selected_path,
            path_exe,
            path_software,
            path_IVPNClient,
            destinIVPNClient,
            path_Python,
            destinPython
        )
        self.QInstaller_class.progress.connect(self.update_progress)
        self.QInstaller_class.label_path_src_installing.connect(self.update_label_path_src_installing)
        self.QInstaller_class.updatesucess.connect(self.update_custommodals_SuccessModal2)
        self.QInstaller_class.finish.connect(self.update_finish)
        self.QInstaller_class.start()

    def update_finish(self):
        self.stackedWidget.slideToNextWidget()
        self.update_custommodals_SuccessModal2(f"Installation finished!!", duration=9000)
        
    def update_progress(self, value):
        self.progressBar.setValue(value)

    def update_label_path_src_installing(self, str):
        self.label_path_src_installing.setText(str)

    def filedialogsearchpath(self):
        dialog = QFileDialog()
        dialog.setStyleSheet("""
            QFileDialog {
                background-color: white;
                border: 1px solid #F7F7F7;
                border-radius: 13px;
                color: black;
                font-size: 16px;
            }
            /* Personalizar os botões */
            QPushButton {
                background-color: #F7F7F7;
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #E6E6E6;
            }
            QPushButton:pressed {
                background-color: #D6D6D6;
            }
            /* Personalizar lista de arquivos */
            QListView, QTreeView {
                background-color: white;
                border: none;
                color: black;
                font-size: 14px;
            }
            /* Barra de navegação */
            QLineEdit {
                background-color: #F7F7F7;
                border: 1px solid #CCCCCC;
                border-radius: 6px;
                padding: 3px;
            }
        """)
        dialog.setFileMode(QFileDialog.Directory) 
        dialog.setOption(QFileDialog.ShowDirsOnly, True)
        dialog.setWindowTitle("Select the Path")
        if dialog.exec_():
            self.selected_path = dialog.selectedFiles()[0]
            self.lineEdit_path_install.setPlainText(self.selected_path)
            self.update_custommodals_SuccessModal2(f"Your installation path has been selected")


    def update_custommodals_SuccessModal2(self, description, pos='top-right', duration=5000):

        myModal = QCustomModals.SuccessModal(
            title="Information", 
            parent=self.stackedWidget,
            position=pos,
            closeIcon=":/feather/icons/feather/window_close.png",
            modalIcon=":/material_design/icons/material_design/info.png",
            description=description,
            isClosable=False,
            duration=duration
        )
        myModal.show()

########################################################################


if __name__ == "__main__":

    ensure_admin()
    app = QApplication(sys.argv)
    MainWindow = Main_Window()
    MainWindow.show()
    sys.exit(app.exec())