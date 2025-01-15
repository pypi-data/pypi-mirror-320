from standarted_logger.logger import Logger
import requests
from pathlib import Path
import sys
import re
import time

from app_version_updater.models import UpdaterException

class UpdaterClient():
    ipv4_pattern = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")

    def __init__(self, host: str, host_domain: str, request_period=600, use_logger=False, 
                 module_name="client-updater", log_level=10, log_file=None):
        
        assert UpdaterClient.ipv4_pattern.match(host), f"Invalid host provided: {host}"
        assert isinstance(host_domain, str), f"Invalid host_domain: {host_domain}"


        self.HOST = host
        self.host_domain = host_domain
        self.app_request_version_period = request_period
        self.logger = Logger.get_logger(module_name, log_level, log_file) if use_logger else None

        if sys.platform == "win32":
            self.CLIENT_SAVE_FOLDER = Path.home() / "Downloads"
        elif sys.platform == "linux":
            self.CLIENT_SAVE_FOLDER = Path.home()

    def manage_app_versions(self, current_app_version) -> None:
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

            time.sleep(self.app_request_version_period)

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
        if self.logger is not None:
            self.logger.info("Client update was downloaded")
        raise UpdaterException("Update", "After exit the app will be updated")

    def get_actual_app_version(self, cred) -> str:
        # Getting latest app version from server
        res = requests.get(self.HOST + f"/{self.host_domain}/appVersion", 
                            params={"cred": cred})
            
        if res.status_code == 200:
            return res.content.decode().replace("\"", "")
        if res.status_code == 404:
            return ""
        else:
            raise UpdaterException(f"HTTP {res.status_code} {res.text}")

    def download_new_app(self, new_version: str, cred) -> bytes:
        # Getting FileResponse from server in bytes - needs further writing to disk
        res = requests.get(self.HOST + f"/{self.host_domain}/app", 
                            params={"cred": cred, "version": new_version})
        
        if res.status_code == 200:
            return res.content
        else:
            raise UpdaterException(f"HTTP {res.status_code}") 
