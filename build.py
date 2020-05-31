import os
from datetime import datetime
from jinja2 import Environment, PackageLoader
from markdown2 import markdown
import configparser
import sass
import rcssmin
from PIL import Image
import time
from tqdm import tqdm

def sitemap_helper(url, lastmod, changefreq, priority):
    url_string = """<url>
        <loc>{}</loc>
        <lastmod>{}</lastmod>
        <changefreq>{}</changefreq>
        <priority>{}</priority>
    </url>""".format(url, lastmod, changefreq, priority)

    return url_string

def generate_sitemap(domain,statics,posts, posts_pre_slug):
    sitemap_string = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">"""

    #Domain
    sitemap_string += sitemap_helper(domain, datetime.now().strftime('%Y-%m-%d'), "weekly", 1.0)

    #STATICS
    for staticc in statics:
        sitemap_string += sitemap_helper("{}{}/{}".format(domain, "", statics[staticc].metadata['slug']), statics[staticc].metadata['date'], "monthly", 0.5)
    

    #POSTS
    for post in posts:
        sitemap_string += sitemap_helper("{}{}/{}".format(domain, posts_pre_slug, posts[post].metadata['slug']), posts[post].metadata['date'], "weekly", 0.8)
    
    sitemap_string += "</urlset>"
    sitemap_file_path = 'output/sitemap.xml'

    os.makedirs(os.path.dirname(sitemap_file_path), exist_ok=True)
    with open(sitemap_file_path, 'w') as file:
        file.write(sitemap_string)

def main():
    #initiate configs
    config = configparser.ConfigParser()
    config.read('site_config.ini')

    #initiate site meta
    site_meta = {
        'domain' : config['DEFAULT']['Domain'],
        'posts_pre_slug' : config['DEFAULT']['Posts Pre Slug'],
        'author' : config['DEFAULT']['Author'],
        'generator' : config['DEFAULT']['Generator'],
        'site_name' : config['DEFAULT']['Site Name'],
        'site_claim' : config['DEFAULT']['Claim'],
        'twitter' : config['DEFAULT']['Twitter'],
        'image_sizes' : config['DEFAULT']['Image Sizes'].split(',')[::-1] #reversed images sizes!!
    }

    print("Building Static Site with {}".format(site_meta['generator']))
    print("...")
    # Compile and write main.scss to main.css into output/css
    print("Compile and save scss to css")
    css_string = sass.compile(filename="assets/css/main.scss")
    css_file_path = "output/css/main.css"
    os.makedirs(os.path.dirname(css_file_path), exist_ok=True)
    with open(css_file_path, 'w') as file:
        file.write(rcssmin.cssmin(css_string))
            
    # Reading Posts
    print("Preparing posts")
    POSTS = {}
    for markdown_post in tqdm(os.listdir('content/posts')):
        file_path = os.path.join('content/posts', markdown_post)

        with open(file_path, 'r') as file:
            POSTS[markdown_post] = markdown(file.read(), extras=['metadata'])

    # Reading Static Sites
    print("Preparing static Sites")
    STATICS = {}
    for markdown_static in tqdm(os.listdir('content/static')):
        file_path = os.path.join('content/static', markdown_static)

        with open(file_path, 'r') as file:
            STATICS[markdown_static] = markdown(file.read(), extras=['metadata'])
    statics_nav = []
    for static_site in (STATICS):
        statics_nav.append({'name':STATICS[static_site].metadata['title'], 'slug':STATICS[static_site].metadata['slug']})
    site_meta['statics_nav'] = statics_nav

    # Sorting Posts
    POSTS = {
        post: POSTS[post] for post in sorted(POSTS, key=lambda post: datetime.strptime(POSTS[post].metadata['date'], '%Y-%m-%d'), reverse=True)
    }
    posts_metadata = [POSTS[post].metadata for post in POSTS]

    # Preparing tags
    print("Preparing tags")
    tags = [post['tags'] for post in posts_metadata]
    tags = list(dict.fromkeys(tags))
    tags_helper = []
    for tag in tags:
        tag_url = tag.lower()
        chars = {'ö':'oe','ä':'ae','ü':'ue','ß':'ss',' ':'-','_':'-','?':'','!':'','&':'-'}
        for char in chars:
            tag_url = tag_url.replace(char,chars[char])
        tags_helper.append({'name':tag, 'slug':tag_url})
    tags = tags_helper
    site_meta['tags_nav'] = tags


    #loading templates
    print("Loading Templates")
    env = Environment(loader=PackageLoader('build', 'templates'))
    home_template = env.get_template('home.html')
    post_template = env.get_template('post.html')
    static_template = env.get_template('statics.html')
    tag_template = env.get_template('tag.html')

    #rendering homepage
    print("Rendering Homepage")
    home_html = home_template.render(posts=posts_metadata, site_meta=site_meta)
    #writing homepage
    with open('output/index.html', 'w') as file:
        file.write(home_html)

    #writing posts
    print("Writing Posts")
    for post in tqdm(POSTS):
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
        post_html = post_template.render(post=post_data, site_meta=site_meta)

        post_file_path = 'output{posts_pre_slug}/{slug}.html'.format(posts_pre_slug=site_meta['posts_pre_slug'], slug=post_metadata['slug'])

        os.makedirs(os.path.dirname(post_file_path), exist_ok=True)
        with open(post_file_path, 'w') as file:
            file.write(post_html)

    #writing tags
    print("Writing tag sites")
    for tag in tqdm(tags):
        tag_posts = []
        for post in posts_metadata:
            if tag['name'] == post['tags']:
                tag_posts.append(post)
        template_html = tag_template.render(posts=tag_posts, site_meta=site_meta, tag=tag)
        template_file_path = 'output/{tag}.html'.format(tag=tag['slug'])

        os.makedirs(os.path.dirname(template_file_path), exist_ok=True)
        with open(template_file_path, 'w') as file:
            file.write(template_html)


    #writing static sites
    print("Writing static sites")
    for static_site in tqdm(STATICS):
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

    #generate sitemap
    print('Generating Sitemap')
    generate_sitemap(site_meta['domain'], STATICS, POSTS, site_meta['posts_pre_slug'])

    #images
    print("Rendering image thumbnails")
    os.makedirs(os.path.dirname('output/img/test.txt'), exist_ok=True)
    for images in tqdm(os.listdir('assets/img')):
        file_path = os.path.join('assets/img', images)

        image_name = images.split(".")[0]

        for image_size in tqdm(site_meta['image_sizes']):
            new_image = Image.open(file_path)
            new_image.thumbnail((int(image_size),int(image_size)))
            image_file_path = 'output/img/{name}-{size}.jpg'.format(name=image_name, size=image_size)
            new_image.save(image_file_path, quality=60, optimize=True)

    print()
    print("Yippie, site was build successfully")
    print("Now run python serve.py to start local server")
    print()

if __name__ == "__main__":
    main()