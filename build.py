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
from _erwin import image_processor
from _erwin import accessories_generator
from _erwin import helper


def main():
    print("Reading Configs...")
    print()

    #initiate configs
    config = configparser.ConfigParser()
    config.read('site_config.ini')

    #initiate site meta
    site_meta = {
        'domain':
        config['DEFAULT']['Domain'],
        'posts_pre_slug':
        config['DEFAULT']['Posts Pre Slug'],
        'author':
        config['DEFAULT']['Author'],
        'generator':
        config['DEFAULT']['Generator'],
        'site_name':
        config['DEFAULT']['Site Name'],
        'site_claim':
        config['DEFAULT']['Claim'],
        'twitter':
        config['DEFAULT']['Twitter'],
        'facebook':
        config['DEFAULT']['Facebook'],
        'logo_file':
        config['DEFAULT']['Logo File'],
        'avatar':
        config['DEFAULT']['Author Avatar Image'],
        'language':
        config['DEFAULT']['Language'],
        'language_full':
        config['DEFAULT']['Language Full'],
        'actual_year':
        datetime.now().year,
        'background_color':
        config['DEFAULT']['Background Color'],
        'favicon':
        config['DEFAULT']['Favicon File'],
        'image_sizes':
        config['DEFAULT']['Image Sizes'].split(',')
        [::-1],  #reversed images sizes!!
        'icon_sizes':
        config['DEFAULT']['Icon Sizes'].split(','),
        'pagination':
        True if config['DEFAULT']['Pagination'] == 'yes' else False,
        'articles_on_homepage':
        int(config['DEFAULT']['Articles on homepage'])
        if config['DEFAULT']['Articles on homepage'] != "" else None
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
        post: POSTS[post]
        for post in sorted(POSTS,
                           key=lambda post: datetime.strptime(
                               POSTS[post].metadata['date'], '%Y-%m-%d'),
                           reverse=True)
    }
    for post in POSTS:
        POSTS[post].metadata['reading_time'] = helper.reading_time(POSTS[post])
        ulist = ["\"", "\'", "&"]
        description = POSTS[post].metadata['summary']
        for ul in ulist:
            description = description.replace(ul, "")
        POSTS[post].metadata['description'] = description
        if POSTS[post].metadata['slug'] != "":
            pass
        else:
            POSTS[post].metadata['slug'] = helper.prepare_string_for_html(
                POSTS[post].metadata['title'])
    posts_metadata = [POSTS[post].metadata for post in POSTS]

    # Reading pages
    print("Preparing pages")
    PAGES = {}
    for markdown_page in tqdm(os.listdir('content/pages')):
        file_path = os.path.join('content/pages', markdown_page)

        with open(file_path, 'r') as file:
            PAGES[markdown_page] = markdown(file.read(), extras=['metadata'])

    # Sorting Pages
    PAGES = {
        page: PAGES[page]
        for page in sorted(PAGES,
                           key=lambda page: datetime.strptime(
                               PAGES[page].metadata['date'], '%Y-%m-%d'),
                           reverse=True)
    }

    for page in PAGES:
        ulist = ["\"", "\'", "&"]
        description = PAGES[page].metadata['summary']
        for ul in ulist:
            description = description.replace(ul, "")
        PAGES[page].metadata['description'] = description
        if PAGES[page].metadata['slug'] != "":
            pass
        else:
            PAGES[page].metadata['slug'] = helper.prepare_string_for_html(
                PAGES[page].metadata['title'])
    pages_metadata = [PAGES[page].metadata for page in PAGES]

    #Preparing Pages nav
    # Preparing categories from pages
    print("Preparing categories")
    categories = [page['category'] for page in pages_metadata]
    categories = list(dict.fromkeys(categories))
    categories = list(filter(None, categories))
    categories_helper = []
    for category in categories:
        categories_helper.append({
            'name':
            category,
            'slug':
            helper.prepare_string_for_html(category)
        })
    categories = categories_helper
    pages_nav = []
    category_nav = []

    for category in categories:
        category_pages = []
        for page in pages_metadata:
            if category['name'] == page['category']:
                category_pages.append(page)
        category_nav.append({
            'cat_meta': category,
            'cat_pages': category_pages
        })

    for page_site in pages_metadata:
        if page_site['category'] == "":
            pages_nav.append({
                'name': page_site['title'],
                'slug': page_site['slug']
            })
    site_meta['pages_nav'] = pages_nav
    site_meta['category_nav'] = category_nav

    # Preparing tags (?<!\d)[,]
    print("Preparing tags")
    tags = []
    for post in posts_metadata:
        post_tags = post['tags'].split(",")
        for post_tag in post_tags:
            tags.append(post_tag.strip())
    tags = list(dict.fromkeys(tags))
    tags_helper = []
    for tag in tags:
        tags_helper.append({
            'name': tag,
            'slug': helper.prepare_string_for_html(tag)
        })
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
    my_pagination = []
    pag_numbers = []
    homepage_posts = posts_metadata
    if site_meta['pagination']:
        pag_item = []
        counter = 0
        for post in posts_metadata:
            pag_item.append(post)
            counter += 1
            if counter % site_meta['articles_on_homepage'] == 0:
                my_pagination.append(pag_item)
                pag_item = []
                counter = 0
        if len(pag_item) > 0:
            my_pagination.append(pag_item)
        homepage_posts = my_pagination[0]

        for pag in range(len(my_pagination) - 1):
            pag_numbers.append(pag + 2)

    print("Rendering Homepage")
    home_html = home_template.render(posts=homepage_posts,
                                     site_meta=site_meta,
                                     pagination_numbers=pag_numbers)
    #writing homepage
    with open('output/index.html', 'w') as file:
        file.write(home_html)

    if site_meta['pagination']:

        pag_counter = 2
        for pag_sites in my_pagination[1:]:
            pag_html = home_template.render(posts=pag_sites,
                                            site_meta=site_meta,
                                            pagination_number=pag_counter,
                                            pagination_numbers=pag_numbers)
            #writing homepage
            pag_file_path = 'output/{}/index.html'.format(pag_counter)
            os.makedirs(os.path.dirname(pag_file_path), exist_ok=True)
            with open(pag_file_path, 'w') as file:
                file.write(pag_html)
            pag_counter += 1

    #writing posts
    print("Writing Posts")
    for post in tqdm(POSTS):
        post_metadata = POSTS[post].metadata

        if post_metadata['slug'] != "":
            m_slug = post_metadata['slug']
        else:
            m_slug = helper.prepare_string_for_html(post_metadata['title'])

        #read meta
        post_data = {
            'content': POSTS[post],
            'title': post_metadata['title'],
            'date': post_metadata['date'],
            'summary': post_metadata['summary'],
            'description': post_metadata['description'],
            'slug': m_slug,
            'img': post_metadata['img'].split('.')[0],
            'word_count': helper.count_words(POSTS[post]),
            'reading_time': post_metadata['reading_time']
        }

        #render post
        post_html = post_template.render(post=post_data, site_meta=site_meta)

        post_file_path = 'output{posts_pre_slug}/{slug}/index.html'.format(
            posts_pre_slug=site_meta['posts_pre_slug'],
            slug=post_metadata['slug'])

        os.makedirs(os.path.dirname(post_file_path), exist_ok=True)
        with open(post_file_path, 'w') as file:
            file.write(post_html)

    #writing tags
    print("Writing tag sites")
    for tag in tqdm(tags):
        tag_posts = []
        for post in posts_metadata:
            post_tags = post['tags'].split(",")
            for post_tag in post_tags:
                if tag['name'] == post_tag.strip():
                    tag_posts.append(post)
        template_html = tag_template.render(posts=tag_posts,
                                            site_meta=site_meta,
                                            tag=tag)
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
            'description': page_metadata['description'],
            'slug': page_metadata['slug'],
            'category': page_metadata['category'],
            'img': page_metadata['img'].split('.')[0]
        }

        #render page site
        page_html = page_template.render(page=page_data, site_meta=site_meta)

        page_file_path = 'output/{slug}/index.html'.format(
            slug=page_metadata['slug'])

        os.makedirs(os.path.dirname(page_file_path), exist_ok=True)
        with open(page_file_path, 'w') as file:
            file.write(page_html)

    #generate sitemap
    print('Generating Sitemap')
    accessories_generator.generate_sitemap(site_meta['domain'], PAGES, POSTS,
                                           site_meta['posts_pre_slug'])

    #generate rss feed
    print('Generating RSS feed')
    accessories_generator.generate_rss_feed(POSTS, site_meta['posts_pre_slug'],
                                            site_meta)

    #generate web_manifest
    print('Generating Webmanifest')
    accessories_generator.generate_webmanifest(site_meta)

    #generate robots.txt
    print('Generating Robots.txt')
    accessories_generator.generate_robots_txt(site_meta)

    #generate icons
    print('Generating Icons')
    image_processor.generate_icons(site_meta)

    # Copy Folders
    print('Copying static folders')
    folder_list = [{
        'from': 'assets/js',
        'to': 'output/js'
    }, {
        'from': 'assets/static',
        'to': 'output'
    }, {
        'from': 'assets/fonts',
        'to': 'output/fonts'
    }, {
        'from': 'assets/static-img',
        'to': 'output/img'
    }]
    for folder in tqdm(folder_list):
        helper.copy_files(folder['from'], folder['to'])

    #images
    print("Rendering image thumbnails")
    img_destination = 'output/img/'
    img_from = 'assets/responsive-img'
    image_processor.generate_responsive_images(img_from, img_destination,
                                               site_meta['image_sizes'])

    print()
    print("Yippie, site was build successfully")
    print("Now run python serve.py to start local server")
    print()


if __name__ == "__main__":
    main()
