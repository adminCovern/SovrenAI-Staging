#!/bin/bash

# FreeSWITCH Minimal Configuration
# This script configures FreeSWITCH with only essential modules

echo "Configuring FreeSWITCH with minimal modules..."

# Clean previous configuration
make clean 2>/dev/null || true
make distclean 2>/dev/null || true

# Configure with minimal modules
./configure \
    --enable-core-pgsql-support \
    --disable-all-modules \
    --enable-mod-sofia \
    --enable-mod-commands \
    --enable-mod-dptools \
    --enable-mod-logfile \
    --enable-mod-console \
    --enable-mod-cdr-csv \
    --enable-mod-event-socket \
    --enable-mod-format-cdr \
    --enable-mod-hash \
    --enable-mod-httapi \
    --enable-mod-esf \
    --enable-mod-fsv \
    --enable-mod-cluechoo \
    --enable-mod-voicemail \
    --enable-mod-voicemail-ivr \
    --enable-mod-db \
    --enable-mod-expr \
    --enable-mod-spandsp \
    --enable-mod-g723-1 \
    --enable-mod-amr \
    --enable-mod-amrwb \
    --enable-mod-b64 \
    --enable-mod-sndfile \
    --enable-mod-native-file \
    --enable-mod-tone-stream \
    --enable-mod-vlc \
    --enable-mod-av \
    --enable-mod-avcodec \
    --enable-mod-avformat \
    --enable-mod-swscale \
    --enable-mod-swresample \
    --enable-mod-avfilter \
    --enable-mod-avdevice \
    --enable-mod-postproc \
    --prefix=/usr/local/freeswitch \
    --with-pic \
    --enable-shared \
    --enable-static

echo "Configuration complete!"
echo "Run 'make' to compile FreeSWITCH" 