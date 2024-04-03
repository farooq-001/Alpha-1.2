import subprocess
import configparser
import time
import psutil
import logging
import os
from tabulate import tabulate
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration from a file
CONFIG_FILE = '/home/Alpha.conf'

class ServiceMonitor:
    def __init__(self, service):
        self.service = service

    def is_active(self):
        """Check if service is running"""
        try:
            cmd = f'/bin/systemctl status {self.service}.service'
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, _ = proc.communicate()
            return '(running)' in stdout.decode("utf-8")
        except Exception as e:
            logging.error(f"Error checking status of {self.service} service: {e}")
            return False

    def start(self):
        """Restart service"""
        try:
            cmd = f'/bin/systemctl restart {self.service}.service'
            subprocess.run(cmd, shell=True, check=True)
            logging.info(f"{self.service} service restarted")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error restarting {self.service} service: {e}")

    def get_pid(self):
        """Get PID of the active service"""
        try:
            cmd = f'/bin/systemctl show --property MainPID --value {self.service}.service'
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, _ = proc.communicate()
            return stdout.decode("utf-8").strip()
        except Exception as e:
            logging.error(f"Error getting PID of {self.service} service: {e}")
            return None

    @staticmethod
    def convert_size(size):
        """Convert size to human-readable format"""
        power = 2 ** 10
        n = 0
        power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
        while size > power:
            size /= power
            n += 1
        return f"{size:.2f} {power_labels[n]}B"

    @staticmethod
    def get_disk_usage():
        """Get disk usage"""
        try:
            usage = psutil.disk_usage('/')
            return {
                'total': ServiceMonitor.convert_size(usage.total),
                'used': ServiceMonitor.convert_size(usage.used),
                'percent': usage.percent
            }
        except Exception as e:
            logging.error(f"Error getting disk usage: {e}")
            return {'total': 'N/A', 'used': 'N/A', 'percent': 'N/A'}

    @staticmethod
    def get_memory_usage():
        """Get memory usage"""
        try:
            usage = psutil.virtual_memory()
            return {
                'total': ServiceMonitor.convert_size(usage.total),
                'used': ServiceMonitor.convert_size(usage.used),
                'percent': usage.percent
            }
        except Exception as e:
            logging.error(f"Error getting memory usage: {e}")
            return {'total': 'N/A', 'used': 'N/A', 'percent': 'N/A'}

if __name__ == '__main__':
    services = []

    while True:
        # Load configuration
        try:
            config = configparser.ConfigParser()
            config.read(CONFIG_FILE)
            services = [service.strip() for service in config['SERVICES']['services'].split(',')]
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")
            exit(1)

        # Monitor and restart services
        table_data = []
        for service in services:
            monitor = ServiceMonitor(service)
            if not monitor.is_active():
                monitor.start()
            else:
                pid = monitor.get_pid()
                disk_usage = ServiceMonitor.get_disk_usage()
                memory_usage = ServiceMonitor.get_memory_usage()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                status = "Running"
                table_data.append([
                    timestamp,
                    service,
                    status,
                    pid,
                    f"{disk_usage['percent']}%",
                    disk_usage['total'],
                    disk_usage['used'],
                    f"{memory_usage['percent']}%",
                    memory_usage['total'],
                    memory_usage['used']
                ])

        if table_data:
            headers = ["Timestamp", "Service", "Status", "PID", "Disk Usage", "Total Disk", "Used Disk", "Memory Usage", "Total Memory", "Used Memory"]
            print(tabulate(table_data, headers=headers, tablefmt="grid", showindex=False))

        time.sleep(1)  # Sleep for 1 second before checking again
