import psutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
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

if receiver_email.endswith('@outlook.com') or receiver_email.endswith('@hotmail.com'):
    smtp_server = 'smtp-mail.outlook.com'
elif receiver_email.endswith('@gmail.com'):
    smtp_server = 'smtp.gmail.com'
else:
    print("Unsupported email domain. Please use Outlook, Hotmail, or Gmail.")
    exit()

while True:
    memory_percentage = float(psutil.virtual_memory().percent)
    disk_usage = float(psutil.disk_usage('/').percent)

    if memory_percentage >= 15 or disk_usage >= 15:
        system_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ist = pytz.timezone('Asia/Kolkata')
        ist_timestamp = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')
        total_memory = psutil.virtual_memory().total
        used_memory = psutil.virtual_memory().used
        total_disk_space = psutil.disk_usage('/').total
        used_disk_space = psutil.disk_usage('/').used
        host_ip = subprocess.check_output(['hostname', '-I']).decode().strip()
        hostname = subprocess.check_output(['hostname']).decode().strip()
        
        uptime_seconds = int(time.time() - psutil.boot_time())
        uptime_hours = uptime_seconds // 3600
        uptime_minutes = (uptime_seconds % 3600) // 60
        uptime = f"{uptime_hours} hours, {uptime_minutes} minutes"

        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = 'System Resource Information'

        # Construct the email body with the table
        body = f"""\
        <html>
        <body>
        <h2>System Resource Information</h2>
        <p>System Uptime: {uptime}</p>
        <table border="1" style="border-collapse: collapse;">
        <tr style="background-color: lightblue;">
        <th>Hostname</th>
        <th>Parameter</th>
        <th>Value</th>
        </tr>
        <tr>
        <td rowspan="7">{hostname}</td>
        <td>System Timestamp</td>
        <td>{system_timestamp}</td>
        </tr>
        <tr>
        <td>IST Time</td>
        <td>{ist_timestamp}</td>
        </tr>
        <tr>
        <td>Total Memory</td>
        <td>{bytes_to_human_readable(total_memory)}</td>
        </tr>
        <tr>
        <td>Used Memory</td>
        <td>{bytes_to_human_readable(used_memory)} ({memory_percentage:.2f}%)</td>
        </tr>
        <tr>
        <td>Total Disk Space</td>
        <td>{bytes_to_human_readable(total_disk_space)}</td>
        </tr>
        <tr>
        <td>Used Disk Space</td>
        <td>{bytes_to_human_readable(used_disk_space)} ({disk_usage:.2f}%)</td>
        </tr>
        <tr>
        <td>Host IP</td>
        <td>{host_ip}</td>
        </tr>
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

        with open('/home/.lion.png', 'rb') as fp:
            img_data = fp.read()
        img = MIMEImage(img_data)
        img.add_header('Content-ID', '<lion>')
        message.attach(img)

        with smtplib.SMTP(smtp_server, 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

    time.sleep(60)

