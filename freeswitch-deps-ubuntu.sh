#!/bin/bash

# FreeSWITCH Dependencies Fix for Modern Ubuntu Systems
# Copy this entire script to your Ubuntu server and run it

echo "Installing FreeSWITCH dependencies for Ubuntu..."

# Update package list
sudo apt update

# Install essential build tools
sudo apt install -y \
    build-essential \
    pkg-config \
    autoconf \
    automake \
    libtool \
    git \
    wget \
    cmake

# Install core FreeSWITCH dependencies (modern package names)
sudo apt install -y \
    libspandsp-dev \
    libpq-dev \
    libopenal-dev \
    unixodbc-dev \
    libmariadb-dev \
    libsqlite3-dev \
    libssl-dev \
    libxml2-dev \
    libcurl4-openssl-dev \
    libjpeg-dev \
    libpng-dev \
    libspeex-dev \
    libspeexdsp-dev \
    libldns-dev \
    libedit-dev \
    libpcre3-dev \
    libyaml-dev

# Install FFmpeg development libraries (modern versions)
sudo apt install -y \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libswresample-dev \
    libswscale-dev \
    libavfilter-dev \
    libavdevice-dev \
    libpostproc-dev

# Install additional audio/video codecs
sudo apt install -y \
    libg7231-dev \
    libamr-dev \
    libamrwb-dev \
    libsndfile1-dev \
    libvorbis-dev \
    libflac-dev \
    libmp3lame-dev \
    libopus-dev

# Install database support
sudo apt install -y \
    libhiredis-dev \
    libmemcached-dev

# Install additional utilities
sudo apt install -y \
    libuuid1 \
    uuid-dev

echo "Dependencies installed successfully!"
echo "You can now run: ./configure && make && sudo make install" 