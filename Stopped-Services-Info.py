import psutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage  # Added this import
from datetime import datetime
import pytz
import time
import subprocess

def bytes_to_human_readable(bytes):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    i = 0
    while bytes >= 1024 and i < len(suffixes) - 1:
        bytes /= 1024.0
        i += 1
    return f"{bytes:.2f} {suffixes[i]}"

sender_email = 'babafarooq001@gmail.com'
receiver_email = 'babafarooq001@gmail.com'
password = 'glor fuby gbus rcal'

listed_services = ['logstash', 'change-wallpaper']

if receiver_email.endswith('@outlook.com') or receiver_email.endswith('@hotmail.com'):
    smtp_server = 'smtp-mail.outlook.com'
elif receiver_email.endswith('@gmail.com'):
    smtp_server = 'smtp.gmail.com'
else:
    print("Unsupported email domain. Please use Outlook, Hotmail, or Gmail.")
    exit()

while True:
    # Check if any listed services are stopped
    stopped_services = []
    for service in listed_services:
        if service not in (psutil.Process(pid).name() for pid in psutil.pids()):
            stopped_services.append(service)

    if stopped_services:
        # Wait 5 minutes
        time.sleep(30)

        # Check if the service is still not running after 5 minutes
        final_stopped_services = []
        for service in stopped_services:
            if service not in (psutil.Process(pid).name() for pid in psutil.pids()):
                final_stopped_services.append(service)

        if final_stopped_services:
            system_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ist = pytz.timezone('Asia/Kolkata')
            ist_timestamp = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')
            hostname_ip = subprocess.check_output(['hostname', '-I']).decode().strip().split()[0]
            hostname = subprocess.check_output(['hostname']).decode().strip()
            uptime_seconds = int(time.time() - psutil.boot_time())
            uptime_hours = uptime_seconds // 3600
            uptime_minutes = (uptime_seconds % 3600) // 60
            uptime = f"{uptime_hours} hours, {uptime_minutes} minutes"

            message = MIMEMultipart()
            message['From'] = sender_email
            message['To'] = receiver_email
            message['Subject'] = 'Stopped Services Information'

            # Construct the email body with the table
            body = f"""\
            <html>
            <body>
            <h2>Stopped Services Information</h2>
            <p>System Uptime: {uptime}</p>
            <table style="border-collapse: collapse;">
            <tr>
            <th style="border: 1px solid green; padding: 8px;">Hostname</th>
            <th style="border: 1px solid green; padding: 8px;">Hostname IP</th>
            <th style="border: 1px solid green; padding: 8px;">Service Name</th>
            <th style="border: 1px solid green; padding: 8px;">Timestamp</th>
            </tr>
            """
            for service in final_stopped_services:
                body += f"""
                <tr>
                <td style="border: 1px solid green; padding: 8px;">{hostname}</td>
                <td style="border: 1px solid green; padding: 8px;">{hostname_ip}</td>
                <td style="border: 1px solid green; padding: 8px;">{service}</td>
                <td style="border: 1px solid green; padding: 8px;">{system_timestamp}</td>
                </tr>
                """
            body += """
            </table>
            <p><strong style="color: indigo;">Information providing By,</strong><br>
            SNB-Tech Software Solutions,<br>
            Cell Number: +91 8142566154<br>
            Baba Farooq SN<br>
            <img src="cid:lion" alt="Lion Image" style="width: 70px; height: 70px;"></p>
            </body>
            </html>
            """

            message.attach(MIMEText(body, 'html'))

            with open('/home/farooq/Downloads/lion.png', 'rb') as fp:
                img_data = fp.read()
            img = MIMEImage(img_data)
            img.add_header('Content-ID', '<lion>')
            message.attach(img)

            with smtplib.SMTP(smtp_server, 587) as server:
                server.starttls()
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message.as_string())

    # Wait for 1 minute before checking again
    time.sleep(30)
