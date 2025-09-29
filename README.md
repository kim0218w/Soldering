# Soldering
공학용캡스톤 디자인
#!/bin/bash
set -e

echo "=== Debian 12 ROS 2 Humble 준비 시작 ==="

# 1. 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# 2. 빌드 도구 및 필수 라이브러리 설치
sudo apt install -y \
  build-essential cmake git wget curl locales \
  python3-pip python3-setuptools python3-wheel python3-dev \
  libasio-dev libtinyxml2-dev libeigen3-dev libyaml-cpp-dev \
  libssl-dev libopencv-dev libcurl4-openssl-dev \
  python3-numpy python3-yaml python3-empy

# 3. pip 최신화
sudo pip3 install --upgrade pip --break-system-packages

# 4. colcon / vcstool / rosdep (Debian에는 apt 패키지 없음 → pip로 설치)
sudo pip3 install --break-system-packages colcon-common-extensions vcstool rosdep

# 5. rosdep 초기화
sudo rosdep init || true
rosdep update

echo "=== ROS 2 Humble 빌드 준비 완료 ==="
echo "colcon, vcstool, rosdep 정상 설치되었는지 확인하세요:"
echo "  rosdep --version"
echo "  vcs --version"
echo "  colcon --help"
