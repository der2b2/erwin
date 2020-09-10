---
title: Image Processing
date: 2020-05-18
tags: Features
img: timj-EJ4qfFp1g8Q-unsplash.jpg
summary: Automaic generation if different file sizes for screen sizes and an automatic icon generator
slug: image-processing
---

Well, image processing for web projects can be a pain in the a.. most of the time. I hate it to convert all the needed images to the different sizes and embed them accordingly.

So i wrote 2 simple but useful generators:

## Responsive Image Generator
For all images in /assets/responsive-img new images are generated in different pixel sizes, taken from site_config.ini -> "Image Sizes". These "thumbnails" are then stored to /output/img/ as .jpg and as .webm file.

The two template-macros responsive_img_thumbnail_list and responsive_img in /templates/macros/images.html then create the html picture_tag, with all the different sizes and with jpg and webm files. Webm is preferred, but if the browser does not support it, the jpg file is being used. 

## Icon Generator
Just put one file into /assats/static-img, min size 1024x1024 pixels. Write that filename to site_config.ini -> "Favicon File" and all icons are generated, even the favicon file. And By all icons i mean AAAAAALLLLLLLLLLL.  