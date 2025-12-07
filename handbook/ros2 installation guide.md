# Steps to install ROS 2 Humble on Ubuntu 22.04 in MacOS

First, install a virtualization software (VM host) UTM or Parallels

Second, install Ubuntu 22.04 server ISO image: `Ubuntu 22.04.5 Live Server ARM64.iso` file

Then the virutalization app and create a Linux VM by mounting the Ubuntu 22.04 Server ISO file above (refer to this guide: <https://docs.getutm.app/guides/ubuntu/>)

Once in Ubunutu (CLI):
Update the list of all available packages/repositories then upgrade them:

```bash
sudo apt update && sudo apt upgrade -y
```

Then install the Ubuntu Desktop GUI:

```bash
sudo apt install ubuntu-desktop
sudo reboot
```

Install basic (core) packages/tools:

```bash
sudo apt install software-properties-common build-essential curl wget git lsb-release gnupg -y
```

Enable `universe` (required):

```bash
sudo add-apt-repository universe
```

ROS 2 Humble installation setup (add ROS2 repo to your system’s package sources):

```bash
sudo apt update
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F\" '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb
```

Update apt repository caches and upgrade packages again:

```bash
sudo apt update && sudo apt upgrade -y
```

Install ROS 2 Humble and its controls:

```bash
sudo apt install ros-humble-desktop ros-dev-tools -y
sudo apt install ros-humble-ros2-control ros-humble-ros2-controllers
```

Auto-source ROS 2 setup in all new terminals:

```bash
echo 'source /opt/ros/humble/setup.bash' >> ~/.bashrc
source ~/.bashrc
```

Recommended commands for performant ROS 2 on VM:

```bash
# GPU-accelerated OpenGL packages (for Graphics)
sudo apt install mesa-utils libgl1-mesa-dri -y
# Improve DDS discovery reliability (Better connectivity for VMs)
sudo apt install ros-humble-rmw-cyclonedds-cpp -y
```

Then use CycloneDDS as the middleware implementation to your environment:

```bash
echo "export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp" >> ~/.bashrc
source ~/.bashrc
```

Install ROS 2 Humble Gazebo and its bridge packages (enables Gazebo ROS 2 topics inter-communication)

```bash
sudo apt update
sudo apt install ros-humble-ros-gz -y
sudo apt install ros-humble-ros-gz-bridge ros-humble-ros-gz-image ros-humble-gz-ros2-control -y
```

Make Gazebo work in VM envrionments:

```bash
echo "export LIBGL_DRI3_DISABLE=1" >> ~/.bashrc
source ~/.bashrc
```

Extra stability (less performance):

```bash
echo "export LIBGL_ALWAYS_SOFTWARE=1" >> ~/.bashrc
source ~/.bashrc
# export MESA_LOADER_DRIVER_OVERRIDE=llvmpipe (optional)
```
