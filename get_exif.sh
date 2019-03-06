#!/usr/bin/env bash

if [[ $# -lt 1 ]]
then
  echo 'usage: <img>'
  exit
fi

img=$1

# Image is rotated 90 so X->height, Y->width
img_width=$(identify ${img} | grep "exif:ImageLength:" | awk '{print $NF}')
img_height=$(identify -verbose ${img} | grep "exif:ImageWidth:" | awk '{print $NF}')
f_length_35=$(identify -verbose ${img} | grep "exif:FocalLengthIn35mmFilm:" | awk '{print $NF}')

echo ${img_width} ${img_height} ${f_length_35}

#img_width = int(img_width[0])
#img_height = int(img_height[0])
#f_length_35 = int(f_length_35[0])

#f_length = f_length_35/36*img_width
#print(f_length)
#sensor_size = (img_width, img_height)

