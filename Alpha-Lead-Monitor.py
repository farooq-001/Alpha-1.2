# Your Python script content here
import subprocess
import configparser
import time

# Configuration data as a multi-line string
config_data = """
[SERVICES]
services = ztn, windows
"""
# Add services Names here  

# Load configuration from the multi-line string
config = configparser.ConfigParser()
config.read_string(config_data)

# Get services from configuration
services = config['SERVICES']['services'].split(',')

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

if __name__ == '__main__':
    while True:
        # Monitor and restart services
        for service in services:
            monitor = ServiceMonitor(service.strip())
            if not monitor.is_active():
                monitor.start()
        time.sleep(1)  # Sleep for 1 second before checking again
