import concurrent.futures
import requests
import logging
from typing import Dict

class FortiGateFirewall:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.verify = False
        self.csrf_token = self.login(username, password)

    def login(self, username: str, password: str) -> str:
        login_endpoint = f"{self.base_url}/logincheck"
        login_payload = {"username": username, "secretkey": password}
        login_headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            response = self.session.post(login_endpoint, data=login_payload, headers=login_headers)
            response.raise_for_status()
            csrf_token = self.session.cookies["ccsrftoken"][1:-1]  # Trim the quotes
            return csrf_token
        except requests.exceptions.RequestException as e:
            logging.error(f"Login failed: {e}")
            return ""

    def logout(self):
        logout_endpoint = f"{self.base_url}/logout"
        try:
            self.session.get(logout_endpoint)
        except requests.exceptions.RequestException as e:
            logging.error(f"Logout failed: {e}")

    def get_info(self, endpoint: str) -> Dict:
        headers = {"X-CSRFTOKEN": self.csrf_token}
        try:
            response = self.session.get(f"{self.base_url}/{endpoint}", headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Get info failed: {e}")
            return {}

    # Add similar methods for add, edit, delete operations

def worker(device: str, username: str, password: str):
    firewall = FortiGateFirewall(device, username, password)
    info = firewall.get_info("api/v2/cmdb/system/status")
    # Perform add, edit, delete operations
    firewall.logout()
    return info

def main():
    devices = ["https://device1", "https://device2", "https://device3"]  # Add all 700 devices
    username = "username"
    password = "password"

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(worker, device, username, password) for device in devices}
        for future in concurrent.futures.as_completed(futures):
            print(future.result())

if __name__ == "__main__":
    main()