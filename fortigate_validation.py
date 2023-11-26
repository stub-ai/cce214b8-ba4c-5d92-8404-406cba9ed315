import concurrent.futures
import difflib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fortigate_api import FortiGateAPI
from backup_server import BackupServer

def fetch_previous_backup():
    backup_server = BackupServer()
    encrypted_backup = backup_server.fetch_backup()
    decrypted_backup = backup_server.decrypt_backup(encrypted_backup)
    return backup_server.extract_backup(decrypted_backup)

def fetch_current_backup():
    fortigate_api = FortiGateAPI()
    return fortigate_api.fetch_backup()

def compare_backups(previous_backup, current_backup):
    diff = difflib.HtmlDiff().make_file(previous_backup, current_backup)
    return diff

def send_email(diff):
    msg = MIMEMultipart()
    msg['From'] = 'your_email@example.com'
    msg['To'] = 'recipient_email@example.com'
    msg['Subject'] = 'FortiGate Configuration Changes'
    msg.attach(MIMEText(diff, 'html'))

    server = smtplib.SMTP('smtp.example.com', 587)
    server.starttls()
    server.login('your_email@example.com', 'your_password')
    server.send_message(msg)
    server.quit()

def main():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        previous_backup_future = executor.submit(fetch_previous_backup)
        current_backup_future = executor.submit(fetch_current_backup)

        previous_backup = previous_backup_future.result()
        current_backup = current_backup_future.result()

        diff = compare_backups(previous_backup, current_backup)
        send_email(diff)

if __name__ == '__main__':
    main()