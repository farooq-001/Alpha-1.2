import subprocess
import configparser
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import socket

# Configuration data as a multi-line string
config_data = """
[SERVICES]
services = ztn, logstash
"""
# Add services Names here  

# Load configuration from the multi-line string
config = configparser.ConfigParser()
config.read_string(config_data)

# Get services from configuration
services = config['SERVICES']['services'].split(',')

# Email configuration
email_address = "babafarooq001@gmail.com"
email_password = "glor fuby gbus rcal"

# Threshold values for memory and disk usage
memory_threshold = 45
disk_threshold = 45

class ServiceMonitor(object):
    def __init__(self, service):
        self.service = service

    def is_active(self):
        """Return True if service is running"""
        try:
            cmd = '/bin/systemctl status %s.service' % self.service
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            stdout_list = proc.communicate()[0].decode("utf-8").split("\n")
            for line in stdout_list:
                if 'Active:' in line:
                    if '(running)' in line:
                        print(self.service + " is running")
                        return True
            return False
        except Exception as e:
            return str(e)

    def start(self):
        """Restart service if not running"""
        try:
            cmd = '/bin/systemctl restart %s.service' % self.service
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            proc.communicate()
            print(self.service + " is restarted")
        except Exception as e:
            return str(e)

    def convert_to_human_readable(self, bytes):
        """Convert bytes to a human-readable format"""
        for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
            if abs(bytes) < 1024.0:
                return "%3.1f %sB" % (bytes, unit)
            bytes /= 1024.0
        return "%.1f %sB" % (bytes, 'Y')

    def get_memory_info(self):
        """Get total memory and used memory"""
        try:
            cmd = '/usr/bin/free -b | grep Mem'
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            stdout = proc.communicate()[0].decode("utf-8").split()
            total_memory = int(stdout[1])
            used_memory = int(stdout[2])
            return total_memory, used_memory
        except Exception as e:
            return None, None

    def get_disk_usage(self):
        """Get disk usage percentage"""
        try:
            cmd = '/bin/df -h | grep /dev/sda1'
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            stdout = proc.communicate()[0].decode("utf-8").split()
            disk_usage = stdout[4]
            return disk_usage
        except Exception as e:
            return None

    def send_email(self, subject, message, data_table):
        """Send an email"""
        try:
            if email_address.endswith('@gmail.com'):
                server = smtplib.SMTP('smtp.gmail.com', 587)
            elif email_address.endswith('@outlook.com'):
                server = smtplib.SMTP('smtp.office365.com', 587)
            else:
                print("Email configuration not supported")
                return

            server.starttls()
            server.login(email_address, email_password)
            msg = MIMEMultipart()
            msg['From'] = email_address
            msg['To'] = email_address
            msg['Subject'] = subject

            # Construct email body with data table
            email_body = f"<h2>{message}</h2>"
            email_body += "<table border='1'><tr><th>Key</th><th>Value</th></tr>"
            for key, value in data_table.items():
                email_body += f"<tr><td>{key}</td><td>{value}</td></tr>"
            email_body += "</table>"
            msg.attach(MIMEText(email_body, 'html'))

            # Get source host IP address, hostname, and hostname's IP addresses
            ip_address = socket.gethostbyname(socket.gethostname())
            hostname = socket.gethostname()
            ip_addresses = subprocess.check_output(['hostname', '-I']).decode('utf-8').strip().split()

            # Add source host information to the message
            source_info = f"Source Host IP: {ip_address}<br>Source Hostname: {hostname}<br>Hostname IP addresses: {', '.join(ip_addresses)}"
            msg.attach(MIMEText(source_info, 'html'))

            server.sendmail(email_address, email_address, msg.as_string())
            server.quit()
            print("Email sent successfully")
        except Exception as e:
            print("Failed to send email:", e)

    def get_resource_usage(self):
        """Get resource usage of the service"""
        try:
            total_memory, used_memory = self.get_memory_info()
            disk_usage = self.get_disk_usage()
            if total_memory is None or used_memory is None or disk_usage is None:
                return None
            memory_percentage = (used_memory / total_memory) * 100
            disk_percentage = float(disk_usage.strip('%'))
            if memory_percentage >= memory_threshold or disk_percentage >= disk_threshold:
                self.send_email("Resource Usage Alert", f"Memory Usage: {memory_percentage:.2f}%\nDisk Usage: {disk_percentage:.2f}%", {'Memory Usage': f"{memory_percentage:.2f}%", 'Disk Usage': f"{disk_percentage:.2f}%"})
            cmd = '/usr/bin/systemctl show %s.service -p ActiveEnterTimestamp,MemoryCurrent,ExecMainPID' % self.service
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            stdout = proc.communicate()[0].decode("utf-8").split("\n")
            usage_info = {}
            for line in stdout:
                if line.strip() != '':
                    key, value = line.split('=')
                    if key == 'MemoryCurrent':
                        value = self.convert_to_human_readable(int(value))
                    if key == 'ExecMainPID':
                        key = 'PID'
                    if key == 'ActiveEnterTimestamp':
                        key = 'ActiveTimestamp'
                    usage_info[key] = value
            usage_info['TotalMemory'] = self.convert_to_human_readable(total_memory)
            usage_info['UsedMemory'] = f"{self.convert_to_human_readable(used_memory)} ({memory_percentage:.2f}%)"
            usage_info['DiskUsage'] = disk_usage
            return usage_info
        except Exception as e:
            return str(e)
    
    def check_service_status(self):
        """Check if the service is running"""
        try:
            if not self.is_active():
                self.send_email("Service Stopped Alert", f"The {self.service} service has stopped.", {'Service': self.service})
        except Exception as e:
            print("Failed to check service status:", e)

if __name__ == '__main__':
    while True:
        # Monitor and restart services
        for service in services:
            monitor = ServiceMonitor(service.strip())
            if not monitor.is_active():
                monitor.start()
            resource_usage = monitor.get_resource_usage()
            if resource_usage is not None:
                print(f"Resource usage for {service}: {resource_usage}")
            monitor.check_service_status()  # Check service status
        time.sleep(1)  # Sleep for 1 second before checking again

