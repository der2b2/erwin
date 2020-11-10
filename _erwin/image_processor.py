import os
from tqdm import tqdm
from PIL import Image
import threading, queue
from _thread import start_new_thread
import psutil
import glob

def foo():
    print("image foo")

def generate_icons(site_meta):
    os.makedirs(os.path.dirname('output/img/test.txt'), exist_ok=True)
    file_path = "assets/static-img/" + site_meta['favicon']

    for icon_size in tqdm(site_meta['icon_sizes']):
        new_image = Image.open(file_path)
        new_image.thumbnail((int(icon_size),int(icon_size)))
        image_file_path_png = 'output/{name}-{size}x{size2}.png'.format(name="icon", size=icon_size, size2=icon_size)
        new_image.save(image_file_path_png)

    #Favicons
    new_image = Image.open(file_path)
    new_image.thumbnail((32,32))
    new_image.save('output/favicon.ico')

    new_image = Image.open(file_path)
    new_image.thumbnail((16,16))
    new_image.save('output/favicon-16x16.png')

    new_image = Image.open(file_path)
    new_image.thumbnail((32,32))
    new_image.save('output/favicon-32x32.png')

def generate_responsive_images_helper(from_path, to_path, images, image_sizes, my_que=None):
    file_path = os.path.join(from_path, images)

    image_name = images.split(".")[0]
    
    if len(glob.glob(to_path + image_name + "*")) != len(image_sizes)*2:
        m_image = Image.open(file_path)
        for image_size in image_sizes:
            new_image = m_image.copy()
            new_image.thumbnail((int(image_size),int(image_size)))
            image_file_path_webp = to_path + '{name}-{size}.webp'.format(name=image_name, size=image_size)
            image_file_path_jpg = to_path + '{name}-{size}.jpg'.format(name=image_name, size=image_size)
            new_image.save(image_file_path_webp, quality=50, method=0)
            new_image.save(image_file_path_jpg, quality=50, optimize=True)
    else:
        print("Image with name " + image_name + " generated before, skipping. To regenerate please execute clean.py and repeat.")
    if my_que:
        my_que.put("Done")

def generate_responsive_images(from_path, to_path, image_sizes):
    os.makedirs(os.path.dirname(to_path + 'test.txt'), exist_ok=True)
    my_que = None
    success = ""

    #Compute images in threads, thread number depends on available RAM
    counter = 1
    thread_number = 1
    mb_available = int(psutil.virtual_memory().available/1000000) - 250
    thread_number = max(1, int(mb_available / 200))
    
    if thread_number > 1:
        my_que = queue.Queue()
    
    for images in tqdm(os.listdir(from_path)):
        if thread_number == 1:
            generate_responsive_images_helper(from_path, to_path, images, image_sizes, my_que)
        else:
          start_new_thread(generate_responsive_images_helper, (from_path, to_path, images, image_sizes, my_que,))

          if counter % thread_number == 0:
             for number in range(thread_number):
               success = my_que.get()
          counter += 1
