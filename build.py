import os
import shutil
from datetime import datetime
from jinja2 import Environment, PackageLoader
from markdown2 import markdown
import configparser
import sass
import rcssmin
from PIL import Image
import time
from tqdm import tqdm
import re

def sitemap_helper(url, lastmod, changefreq, priority):
    url_string = """<url>
        <loc>{}</loc>
        <lastmod>{}</lastmod>
        <changefreq>{}</changefreq>
        <priority>{}</priority>
    </url>""".format(url, lastmod, changefreq, priority)

    return url_string

def generate_sitemap(domain,pages,posts, posts_pre_slug):
    sitemap_string = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">"""

    #Domain
    sitemap_string += sitemap_helper(domain, datetime.now().strftime('%Y-%m-%d'), "weekly", 1.0)

    #PAGES
    for pagec in pages:
        sitemap_string += sitemap_helper("{}{}/{}".format(domain, "", pages[pagec].metadata['slug']), pages[pagec].metadata['date'], "monthly", 0.5)
    

    #POSTS
    for post in posts:
        sitemap_string += sitemap_helper("{}{}/{}".format(domain, posts_pre_slug, posts[post].metadata['slug']), posts[post].metadata['date'], "weekly", 0.8)
    
    sitemap_string += "</urlset>"
    sitemap_file_path = 'output/sitemap.xml'

    os.makedirs(os.path.dirname(sitemap_file_path), exist_ok=True)
    with open(sitemap_file_path, 'w') as file:
        file.write(sitemap_string)

def copy_files(from_folder, to_folder):
    os.makedirs(os.path.dirname(to_folder + "/test.txt"), exist_ok=True)
    for file in os.listdir(from_folder):
        shutil.copy(from_folder + "/" + file, to_folder)

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def count_words(input_string):
    res = len(re.findall(r'\w+', clean_html(input_string)))
    return res

#returns average reading length in minutes
#minimum is 1
def reading_time(input_string):
    return max(int(round(count_words(input_string) / 200.0, 0)), 1)

def main():
    print("Reading Configs...")
    print()

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
        'facebook' : config['DEFAULT']['Facebook'],
        'logo_file' : config['DEFAULT']['Logo File'],
        'avatar' : config['DEFAULT']['Author Avatar Image'],
        'language' : config['DEFAULT']['Language'],
        'actual_year' : datetime.now().year,
        'image_sizes' : config['DEFAULT']['Image Sizes'].split(',')[::-1] #reversed images sizes!!
    }

    print("Building page Site with {}".format(site_meta['generator']))
    print("...")

    # Compile and write main.scss to main.css into output/css
    print("Compile and save scss to css")
    css_string = sass.compile(filename="assets/css/main.scss")
    css_file_path = "output/css/main.css"
    os.makedirs(os.path.dirname(css_file_path), exist_ok=True)
    with open(css_file_path, 'w') as file:
        file.write(rcssmin.cssmin(css_string))

    # Compile and write critical-main.scss to critical-main.css into output/css
    print("Compile and save critical scss to css")
    css_string_crit = sass.compile(filename="assets/css/critical-main.scss")
    if css_string_crit == "":
        site_meta['critical_css'] = rcssmin.cssmin(css_string)
    else:
        site_meta['critical_css'] = rcssmin.cssmin(css_string_crit)
                
    # Reading Posts
    print("Preparing posts")
    POSTS = {}
    for markdown_post in tqdm(os.listdir('content/posts')):
        file_path = os.path.join('content/posts', markdown_post)

        with open(file_path, 'r') as file:
            POSTS[markdown_post] = markdown(file.read(), extras=['metadata'])
    # Sorting Posts
    POSTS = {
        post: POSTS[post] for post in sorted(POSTS, key=lambda post: datetime.strptime(POSTS[post].metadata['date'], '%Y-%m-%d'), reverse=True)
    }
    for post in POSTS:
        POSTS[post].metadata['reading_time'] = reading_time(POSTS[post])
    posts_metadata = [POSTS[post].metadata for post in POSTS]

    # Reading pages
    print("Preparing pages")
    PAGES = {}
    for markdown_page in tqdm(os.listdir('content/pages')):
        file_path = os.path.join('content/pages', markdown_page)

        with open(file_path, 'r') as file:
            PAGES[markdown_page] = markdown(file.read(), extras=['metadata'])
    #Preparing Pages nav
    pages_nav = []
    for page_site in (PAGES):
        pages_nav.append({'name':PAGES[page_site].metadata['title'], 'slug':PAGES[page_site].metadata['slug']})
    site_meta['pages_nav'] = pages_nav

    # Preparing tags
    print("Preparing tags")
    tags = [post['tags'] for post in posts_metadata]
    tags = list(dict.fromkeys(tags))
    tags_helper = []
    for tag in tags:
        tag_url = tag.lower()
        chars = {'ö':'oe','ä':'ae','ü':'ue','ß':'ss',' ':'-','_':'-','?':'','!':'','&':'-','/':'-'}
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
    page_template = env.get_template('page.html')
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
            'img': post_metadata['img'].split('.')[0],
            'word_count' : count_words(POSTS[post]),
            'reading_time' : post_metadata['reading_time']
        }

        #render post
        post_html = post_template.render(post=post_data, site_meta=site_meta)

        post_file_path = 'output{posts_pre_slug}/{slug}/index.html'.format(posts_pre_slug=site_meta['posts_pre_slug'], slug=post_metadata['slug'])

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
        template_file_path = 'output/{tag}/index.html'.format(tag=tag['slug'])

        os.makedirs(os.path.dirname(template_file_path), exist_ok=True)
        with open(template_file_path, 'w') as file:
            file.write(template_html)


    #writing page sites
    print("Writing page sites")
    for page_site in tqdm(PAGES):
        page_metadata = PAGES[page_site].metadata

        #read meta
        page_data = {
            'content': PAGES[page_site],
            'title': page_metadata['title'],
            'date': page_metadata['date'],
            'summary': page_metadata['summary'],
            'slug': page_metadata['slug']
        }

        #render page site
        page_html = page_template.render(page=page_data, site_meta=site_meta)

        page_file_path = 'output/{slug}/index.html'.format(slug=page_metadata['slug'])

        os.makedirs(os.path.dirname(page_file_path), exist_ok=True)
        with open(page_file_path, 'w') as file:
            file.write(page_html)

    #generate sitemap
    print('Generating Sitemap')
    generate_sitemap(site_meta['domain'], PAGES, POSTS, site_meta['posts_pre_slug'])

    # Copy Folders
    print('Copying static folders')
    folder_list = [
        {'from':'assets/js', 'to':'output/js'},
        {'from':'assets/static', 'to':'output'},
        {'from':'assets/fonts', 'to':'output/fonts'},
        {'from':'assets/static-img', 'to':'output/img'}
    ]
    for folder in tqdm(folder_list):
        copy_files(folder['from'], folder['to'])

    #images
    print("Rendering image thumbnails")
    os.makedirs(os.path.dirname('output/img/test.txt'), exist_ok=True)
    for images in tqdm(os.listdir('assets/responsive-img')):
        file_path = os.path.join('assets/responsive-img', images)

        image_name = images.split(".")[0]

        for image_size in tqdm(site_meta['image_sizes']):
            new_image = Image.open(file_path)
            new_image.thumbnail((int(image_size),int(image_size)))
            image_file_path_webp = 'output/img/{name}-{size}.webp'.format(name=image_name, size=image_size)
            image_file_path_jpg = 'output/img/{name}-{size}.jpg'.format(name=image_name, size=image_size)
            new_image.save(image_file_path_webp, quality=50, method=0)
            new_image.save(image_file_path_jpg, quality=50, optimize=True)

    print()
    print("Yippie, site was build successfully")
    print("Now run python serve.py to start local server")
    print()

if __name__ == "__main__":
    main()