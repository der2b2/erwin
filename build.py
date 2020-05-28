import os
from datetime import datetime
from jinja2 import Environment, PackageLoader
from markdown2 import markdown
import configparser
import sass
import rcssmin
from PIL import Image

#initiate configs
config = configparser.ConfigParser()
config.read('site_config.ini')

#initiate site meta
site_meta = {
    'domain' : config['DEFAULT']['Domain'],
    'posts_pre_slug' : config['DEFAULT']['Posts Pre Slug']
}

#initiate site technical configs
site_config = {
    'image_sizes' : config['DEFAULT']['Image Sizes'].split(',')[::-1] #reversed images sizes!!
}

# Compile and write main.scss to main.css into output/css
css_string = sass.compile(filename="assets/css/main.scss")
css_file_path = "output/css/main.css"
os.makedirs(os.path.dirname(css_file_path), exist_ok=True)
with open(css_file_path, 'w') as file:
    file.write(rcssmin.cssmin(css_string))

#images
os.makedirs(os.path.dirname('output/img/test.txt'), exist_ok=True)
for images in os.listdir('assets/img'):
    file_path = os.path.join('assets/img', images)

    image_name = images.split(".")[0]

    for image_size in site_config['image_sizes']:
        new_image = Image.open(file_path)
        new_image.thumbnail((int(image_size),int(image_size)))
        image_file_path = 'output/img/{name}-{size}.jpg'.format(name=image_name, size=image_size)
        new_image.save(image_file_path, quality=60, optimize=True)
        
# Reading Posts
POSTS = {}
for markdown_post in os.listdir('content/posts'):
    file_path = os.path.join('content/posts', markdown_post)

    with open(file_path, 'r') as file:
        POSTS[markdown_post] = markdown(file.read(), extras=['metadata'])

# Reading Static Sites
STATICS = {}
for markdown_static in os.listdir('content/static'):
    file_path = os.path.join('content/static', markdown_static)

    with open(file_path, 'r') as file:
        STATICS[markdown_static] = markdown(file.read(), extras=['metadata'])

# Sorting Posts
POSTS = {
    post: POSTS[post] for post in sorted(POSTS, key=lambda post: datetime.strptime(POSTS[post].metadata['date'], '%Y-%m-%d'), reverse=True)
}

#loading templates
env = Environment(loader=PackageLoader('build', 'templates'))
home_template = env.get_template('home.html')
post_template = env.get_template('post.html')
static_template = env.get_template('statics.html')

#rendering homepage
posts_metadata = [POSTS[post].metadata for post in POSTS]
tags = [post['tags'] for post in posts_metadata]
home_html = home_template.render(posts=posts_metadata, tags=tags, site_meta=site_meta)

#writing homepage
with open('output/index.html', 'w') as file:
    file.write(home_html)

#writing posts
for post in POSTS:
    post_metadata = POSTS[post].metadata

    #read meta
    post_data = {
        'content': POSTS[post],
        'title': post_metadata['title'],
        'date': post_metadata['date'],
        'summary': post_metadata['summary'],
        'slug': post_metadata['slug'],
        'img': post_metadata['img'].split('.')[0]
    }

    #render post
    post_html = post_template.render(post=post_data, site_meta=site_meta, image_sizes=site_config['image_sizes'])

    post_file_path = 'output/{posts_pre_slug}/{slug}.html'.format(posts_pre_slug=site_meta['posts_pre_slug'], slug=post_metadata['slug'])

    os.makedirs(os.path.dirname(post_file_path), exist_ok=True)
    with open(post_file_path, 'w') as file:
        file.write(post_html)

#writing static sites
for static_site in STATICS:
    static_metadata = STATICS[static_site].metadata

    #read meta
    static_data = {
        'content': STATICS[static_site],
        'title': static_metadata['title'],
        'date': static_metadata['date'],
        'summary': static_metadata['summary'],
        'slug': static_metadata['slug']
    }

    #render static site
    static_html = static_template.render(static=static_data, site_meta=site_meta)

    static_file_path = 'output/{slug}.html'.format(slug=static_metadata['slug'])

    os.makedirs(os.path.dirname(static_file_path), exist_ok=True)
    with open(static_file_path, 'w') as file:
        file.write(static_html)