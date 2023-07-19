#!/usr/bin/env bash
#
# Make windows icon .ico from an image file such as png
#
# Example
#     ./image2ico.sh ../../../docs/images/dfvue_icon.png

set -e

IN=${1}

OUT1=$(basename ${IN})
OUT2=${OUT1%.*}.ico

sips -z 256 256 -o ${OUT1} ${IN}
magick convert ${OUT1} ${OUT2}
