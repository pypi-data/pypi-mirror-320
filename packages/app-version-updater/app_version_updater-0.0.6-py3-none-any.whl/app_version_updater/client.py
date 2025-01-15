from standarted_logger.logger import Logger
import requests
from pathlib import Path
import sys
import asyncio

class UpdaterClientException(Exception):
    pass

class UpdaterClient():

    def __init__(self, host="127.0.0.1", login="user", password="user", 
                 use_logger=False, module_name="updater-server", log_level=0, log_file=None,
                 changable_host=False):
        self.HOST = host
        self.LOGIN = login
        self.PASSWORD = password
        self.changable_host = changable_host
        
        self.logger = Logger.get_logger(module_name, log_level, log_file) if use_logger else None

        if sys.platform == "win32":
            self.CLIENT_SAVE_FOLDER = Path.home() / "Downloads"
        elif sys.platform == "linux":
            self.CLIENT_SAVE_FOLDER = Path.home()

    async def manage_app_versions(self, current_app_version) -> None:
        '''
        Main thread that requests newer app versions from server,
        fetches updates (if any) and updates app
        '''
        while True:
            # try:
            version = self.get_actual_app_version() # Getting only version value
            if self.logger is not None:
                self.logger.info(f"Requested actual client version - got {version}")
            if not version:
                if self.logger is not None:
                    self.logger.debug(f"No client update")
                continue
            if current_app_version < version and version != "None":
                if self.logger is not None:
                    self.logger.info(f"Downloading version {version}...")
                app = self.download_new_app(version) # getting in memory, not on disk yet
                if self.logger is not None:
                    self.logger.info(f"Upgrading to verison {version}, extracting...")
                self.save_setup_file(app, version) # saving to path on disk
            else:
                if self.logger is not None:
                    self.logger.info(f"Latest app version ({version}) matching, no update required")

            # except Exception as e:
            #     if self.logger is not None:
            #         self.logger.error(e)
            #     raise UpdaterClientException("Error client update", e)
            await asyncio.sleep(self.app_request_version_period)

    def save_setup_file(self, content: bytes, version: str):
        # Loads setup (exe) file
        try:
            path = self.CLIENT_SAVE_FOLDER / f'setup_reclamations_{version.replace(".", "")}.exe'
            if path.exists():
                if path.stat().st_size == len(content):
                    raise FileExistsError("The setup file was already downloaded")
            path.write_bytes(content)
        except FileExistsError:
            if self.logger is not None:
                self.logger.info(f"Downloaded file was already downloaded")
            return
        # except Exception as e:
        #     if self.logger is not None:
        #         self.logger.error(e)
        #     raise UpdaterClientException("Error client update", e)
        if self.logger is not None:
            self.logger.info("Client update was downloaded")
        raise UpdaterClientException("Update", "After exit the app will be updated")

    def get_actual_app_version(self, cred) -> str:
        # Getting latest app version from server
        try:
            res = requests.get(self.HOST + "/recl/appVersion", 
                                params={"cred": cred})
        except Exception:
            self.change_host()
            res = requests.get(self.HOST + "/recl/appVersion", 
                                params={"cred": cred})
            
        if res.status_code == 200:
            return res.content.decode().replace("\"", "")
        if res.status_code == 404:
            return ""
        else:
            raise UpdaterClientException(f"HTTP {res.status_code} {res.text}")

    def download_new_app(self, new_version: str, cred) -> bytes:
        # Getting FileResponse from server in bytes - needs further writing to disk
        try:
            res = requests.get(self.HOST + "/recl/app", 
                                params={"cred": cred,
                                        "version": new_version})
            
        except Exception:
            self.change_host()
            res = requests.get(self.HOST + "/recl/app", 
                                params={"cred": cred,
                                        "version": new_version})
        if res.status_code == 200:
            return res.content
        else:
            raise UpdaterClientException(f"HTTP {res.status_code}") 
        
    def change_host(self):
        if self.changable_host:
            self.HOST = "http://192.168.0.97:50002" if self.HOST == "http://194.154.83.11:50002" else "http://194.154.83.11:50002" 
