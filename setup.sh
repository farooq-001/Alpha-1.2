#!/bin/bash

# Copy the python code files
sudo cp -r .loin.png  /home/.loin.png
sudo cp -r  Stopped-Services-Info.py   /etc/Stopped-Services-Info.py 
sudo cp -r  System-Resource-Inof.py   /etc/System-Resource-Inof.py 
sudo cp -r  Alpha-Lead-Monitor.py    /etc/Alpha-Lead-Monitor.py


# Function to start the download
start_download() {
# Your download logic here
echo "Starting download..."
# Check if /etc/os-release exists
if [ -f "/etc/os-release" ]; then
    # Read the value of the ID variable from /etc/os-release
    source /etc/os-release
    case "$ID" in
        debian|ubuntu)
            echo "Detected Debian/Ubuntu"
            sudo apt update && sudo apt upgrade -y
            sudo apt install -y python3-pip
            pip3 install configparser
            pip3 install requests
            ;;
        centos|rhel|rocky)
            echo "Detected CentOS/RHEL/Rocky"
            sudo yum update -y
            sudo yum install -y python3-pip
            pip3 install configparser
            pip3 install requests
            ;;
        fedora)
            echo "Detected Fedora"
            sudo dnf update -y
            sudo dnf install -y python3-pip
            pip3 install configparser
            pip3 install requests
            ;;
        *)
            echo "Unsupported distribution: $ID"
            exit 1
            ;;
    esac
else
    echo "/etc/os-release not found. Unable to determine distribution."
    exit 1
fi

sudo tee /etc/systemd/system/Alpha-Master.service > /dev/null <<EOF
[Unit]
Description=[SNB-TECH] ALPHA-MASTER-7.2 Monitoring Services 
After=network.target

[Service]
Type=simple
ExecStart=/bin/bash -c '/usr/bin/python3 /etc/Alpha-Lead-Monitor.py  && /usr/bin/python3 /etc/Stopped-Services-Info.py && /usr/bin/python3 /etc/System-Resource-Inof.py'
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd to apply the changes
sudo systemctl daemon-reload
sudo systemctl restart Alpha.service
}

# Function to remove a file
remove_file() {
# Your file removal logic here
echo "Removing file..."

sudo systemctl stop Alpha-Master.service
sudo systemctl disable Alpha-Master.service
sudo rm -rf  /etc/Stopped-Services-Info.py /etc/System-Resource-Inof.py /etc/Alpha-Lead-Monitor.py  /home/.loin.png
sudo systemctl daemon-reload
}

# Menu for selecting options
while true; do
    echo "Choose an option:"
    echo "1. Start download"
    echo "2. Remove file"
    echo "3. Exit"
    read -p "Enter your choice: " choice

    case $choice in
        1) start_download ;;
        2) remove_file ;;
        3) break ;;
        *) echo "Invalid choice. Please enter 1, 2, or 3." ;;
    esac
done
