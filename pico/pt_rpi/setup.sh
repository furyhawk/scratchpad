#!/bin/bash

if [ "$EUID" -ne 0 ]; then
    echo "This script must be run with sudo."
    echo "Use 'sudo ./setup.sh' instead of './setup.sh'"
    echo "Exiting..."
    exit 1
fi

# Default value for using other source
use_index=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    -i|--index)
      use_index=true
      shift
      ;;
    *)
      # Unknown option
      echo "Usage: $0 [-i | --index] (to use other source)"
      exit 1
      ;;
  esac
done

if [ -e /boot/firmware/config.txt ] ; then
  FIRMWARE=/firmware
else
  FIRMWARE=
fi
CONFIG=/boot${FIRMWARE}/config.txt

is_pi () {
  ARCH=$(dpkg --print-architecture)
  if [ "$ARCH" = "armhf" ] || [ "$ARCH" = "arm64" ] ; then
    return 0
  else
    return 1
  fi
}

if is_pi ; then
  if [ -e /proc/device-tree/chosen/os_prefix ]; then
    PREFIX="$(cat /proc/device-tree/chosen/os_prefix)"
  fi
  CMDLINE="/boot${FIRMWARE}/${PREFIX}cmdline.txt"
else
  CMDLINE=/proc/cmdline
fi

is_pifive() {
  grep -q "^Revision\s*:\s*[ 123][0-9a-fA-F][0-9a-fA-F]4[0-9a-fA-F][0-9a-fA-F][0-9a-fA-F]$" /proc/cpuinfo
  return $?
}


# Config cmdline.txt
sed -i $CMDLINE -e "s/console=ttyAMA0,[0-9]\+ //"
sed -i $CMDLINE -e "s/console=serial0,[0-9]\+ //"


# Config config.txt
set_config_var() {
  lua - "$1" "$2" "$3" <<EOF > "$3.bak"
local key=assert(arg[1])
local value=assert(arg[2])
local fn=assert(arg[3])
local file=assert(io.open(fn))
local made_change=false
for line in file:lines() do
  if line:match("^#?%s*"..key.."=.*$") then
    line=key.."="..value
    made_change=true
  end
  print(line)
end

if not made_change then
  print(key.."="..value)
end
EOF
mv "$3.bak" "$3"
}

if is_pifive ; then
  set_config_var dtparam=uart0 on $CONFIG
else
  set_config_var enable_uart 1 $CONFIG
fi


# Check if camera_auto_detect is set to 0 in /boot/config.txt
echo "# set camera_auto_detect is set to 0 in /boot/config.txt"
if ! grep -q 'camera_auto_detect=0' /boot/config.txt; then
  sed -i 's/camera_auto_detect=1/camera_auto_detect=0/' /boot/config.txt
fi

# Add dtoverlay=ov5647 to /boot/config.txt
echo "# Add dtoverlay=ov5647 to /boot/config.txt"
if ! grep -q 'dtoverlay=ov5647' /boot/config.txt; then
  echo 'dtoverlay=ov5647' >> /boot/config.txt
fi

# Add gpu_mem=128 to /boot/config.txt
echo "# Add gpu_mem=128 to /boot/config.txt"
if ! grep -q 'gpu_mem=128' /boot/config.txt; then
  echo 'gpu_mem=128' >> /boot/config.txt
fi

# Add gpu_mem=128 to /boot/config.txt
echo "# Add dtoverlay=disable-bt to /boot/config.txt"
if ! grep -q 'dtoverlay=disable-bt' /boot/config.txt; then
  echo 'dtoverlay=disable-bt' >> /boot/config.txt
fi

sudo systemctl disable hciuart.service
sudo systemctl disable bluetooth.service


# Change sources
if $use_index; then
  # Backup the original sources.list file
  if ! [ -e /etc/apt/sources.list.bak ]; then
    sudo cp /etc/apt/sources.list /etc/apt/sources.list.bak
  fi

  # Create a new sources.list file with other mirrors, keeping the release name "bookworm"
  echo "Updating sources.list with other mirrors..."
  sudo sh -c 'echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian bookworm main contrib non-free non-free-firmware\ndeb https://mirrors.tuna.tsinghua.edu.cn/debian-security bookworm-security main contrib non-free non-free-firmware\ndeb https://mirrors.tuna.tsinghua.edu.cn/debian bookworm-updates main contrib non-free non-free-firmware" > /etc/apt/sources.list'


  if ! [ -e /etc/apt/sources.list.d/raspi.list.bak ]; then
    sudo cp /etc/apt/sources.list.d/raspi.list /etc/apt/sources.list.d/raspi.list.bak
  fi

  sudo sh -c 'echo "deb https://mirrors.tuna.tsinghua.edu.cn/raspberrypi bookworm main" > /etc/apt/sources.list.d/raspi.list'


  # Update the package list
  echo "Updating package list..."
  sudo apt update

  echo "Done! Your sources.list has been updated with Aliyun mirrors while keeping the release name 'bookworm'."
else
  echo "# Using default sources."
fi



# Install required software
echo "# Install required software."
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y libopenblas-dev libatlas3-base libcamera-dev python3-opencv portaudio19-dev
sudo apt-get install -y util-linux procps hostapd iproute2 iw haveged dnsmasq iptables espeak

# Install create_ap
echo "# Install create_ap."
# git clone https://github.com/oblique/create_ap.git
cd $PWD/create_ap/
sudo make install
cd ..



echo "# Create a Python virtual environment."
# Create a Python virtual environment
cd $PWD
python -m venv --system-site-packages ugv-env

echo "# Activate a Python virtual environment."

echo "# Install dependencies from requirements.txt"
# Install dependencies from requirements.txt
if $use_index; then
  sudo -H -u $USER bash -c 'source $PWD/ugv-env/bin/activate && pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt && deactivate'
else
  sudo -H -u $USER bash -c 'source $PWD/ugv-env/bin/activate && pip install -r requirements.txt && deactivate'
fi

echo "# Add current user to group so it can use serial."
sudo usermod -aG dialout $USER



echo "Setup completed. Please to reboot your Raspberry Pi for the changes to take effect."

echo "Use the command below to run app.py onboot."

echo "sudo chmod +x autorun.sh"

echo "./autorun.sh"