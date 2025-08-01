#!/bin/bash

BUILD_NUM="%build.number%"
BUILD_DATE=$(date "+%b %-d, %Y")

sed -i "s/Build = \".*\"/Build = \"${BUILD_NUM}\"/" Version.py
sed -i "s/BuildDate = \".*\"/BuildDate = \"${BUILD_DATE}\"/" Version.py
 