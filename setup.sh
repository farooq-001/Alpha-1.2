#!/bin/bash

# Copy the files
sudo cp -r  Alpha-Master.service       /etc/systemd/system/
sudo cp -r  Stopped-Services-Info.py   /etc/
sudo cp -r  System-Resource-Inof.py    /etc/
sudo cp -r  Alpha-Lead-Monitor.py      /etc/
sudo cp -r  Alpha.conf                 /home/Alpha.conf
sudo cp -r .loin.png                   /home/.lion.png


# Function to start the download
start_download() {
    # Your download logic here
    echo "Starting download..."

    # Supported distributions:
    # 1. CentOS 7 (using yum)
    # 2. CentOS 8+ (using dnf)
    # 3. Red Hat Enterprise Linux (RHEL)
    # 4. Fedora
    # 5. Rocky Linux
    # 6. Ubuntu
    # 7. Amazon Linux 2

    # Determine the package manager
    if command -v dnf >/dev/null 2>&1; then
        PKG_MANAGER="dnf"
    elif command -v yum >/dev/null 2>&1; then
        PKG_MANAGER="yum"
    elif command -v apt >/dev/null 2>&1; then
        PKG_MANAGER="apt"
    else
        echo "Unsupported distribution"
        exit 1
    fi

    # Update package lists
    if [ "$PKG_MANAGER" == "apt" ]; then
        sudo apt update
    else
        sudo $PKG_MANAGER update -y
    fi

    # Install Python 3 and pip
    if [ "$PKG_MANAGER" == "apt" ]; then
        sudo apt install -y python3-pip
    else
        sudo $PKG_MANAGER install -y python3-pip
    fi

    # Install required Python libraries
    pip3 install configparser pytz

    # Install psutil if not on Ubuntu
    if [ "$PKG_MANAGER" != "apt" ]; then
        sudo $PKG_MANAGER install -y python3-psutil
    fi

    # Display the OS type
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "Detected OS: $ID $VERSION_ID"
    else
        echo "Unable to determine OS type"
    fi
    sudo pip3 install psutil
     sudo pip3 install tabulate
    
    #centos
    python3 -m venv myenv
    source myenv/bin/activate
    sudo pip3 install tabulate
    deactivate
    
    # Reload systemd to apply the changes
    sudo systemctl daemon-reload
    sudo systemctl restart Alpha-Master.service
    sudo systemctl status Alpha-Master.service   
}

# Function to remove a file
remove_file() {
    # Your file removal logic here
    echo "Removing file..."

    sudo systemctl stop Alpha-Master.service
    sudo systemctl disable Alpha-Master.service
    sudo rm -rf /etc/Stopped-Services-Info.py /etc/System-Resource-Inof.py /etc/Alpha-Lead-Monitor.py /home/.lion.png
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
        1) start_download ; break ;;
        2) remove_file ; break ;;
        3) exit ;;
        *) echo "Invalid choice. Please enter 1, 2, or 3." ;;
    esac
done
