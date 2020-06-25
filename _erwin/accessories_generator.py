import os
from datetime import datetime

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

def generate_rss_feed(posts, posts_pre_slug, site_meta):
    rss_string = """<?xml version="1.0" encoding="UTF-8"?>
            <rss version="2.0"
            xmlns:content="http://purl.org/rss/1.0/modules/content/"
            xmlns:wfw="http://wellformedweb.org/CommentAPI/"
            xmlns:dc="http://purl.org/dc/elements/1.1/"
            xmlns:atom="http://www.w3.org/2005/Atom"
            xmlns:sy="http://purl.org/rss/1.0/modules/syndication/"
            xmlns:slash="http://purl.org/rss/1.0/modules/slash/"
            >

        <channel>
            <title>{site_title}</title>
            <atom:link href="{feed_url}" rel="self" type="application/rss+xml" />
            <link>{domain}</link>
            <description>{site_description}</description>
            <lastBuildDate>{last_build_date}</lastBuildDate>
            <language>{language}</language>
            <sy:updatePeriod>
            hourly	</sy:updatePeriod>
            <sy:updateFrequency>
            1	</sy:updateFrequency>
            <generator>{generator}</generator>
            
            
            
    """.format(
        site_title=site_meta['site_name'],
        feed_url=site_meta['domain'] + "/rss.xml",
        domain=site_meta['domain'],
        site_description=site_meta['site_claim'],
        last_build_date=datetime.strftime(datetime.now(), "%a, %d %b %Y %H:%M:%S") + " GMT",
        language=site_meta['language_full'],
        generator=site_meta['generator']
    )

    counter = 0
    for post in posts:
        rss_string += """<item>
                    <title>{title}</title>
                    <link>{url}</link>
                            <pubDate>{date}</pubDate>
                    <dc:creator><![CDATA[{author}]]></dc:creator>
                            <category><![CDATA[{category}]]></category>
                        <guid isPermaLink="true">{guid}</guid>
                            <description><![CDATA[{desc}]]></description>
                            <content:encoded><![CDATA[]]>{content}</content:encoded>
                </item>
        """.format(
            title=posts[post].metadata['title'],
            url=site_meta['domain'] + posts_pre_slug + "/" + posts[post].metadata['slug'],
            date=datetime.strftime(datetime.strptime(posts[post].metadata['date'], "%Y-%m-%d"), "%a, %d %b %Y %H:%M:%S") + " GMT",
            author=site_meta['author'],
            category=posts[post].metadata['tags'],
            guid=site_meta['domain'] + posts_pre_slug + "/" + posts[post].metadata['slug'],
            desc=posts[post].metadata['summary'],
            content=posts[post].metadata['summary']
        )
        counter+=1
        if counter == 5:
            break

    rss_string += """</channel>
        </rss>
    """

    rss_file_path = 'output/rss.xml'

    os.makedirs(os.path.dirname(rss_file_path), exist_ok=True)
    with open(rss_file_path, 'w') as file:
        file.write(rss_string)

def generate_webmanifest(site_meta):
    webmanifest_string = """{{"name": "{name}",
    "short_name": "{short_name}",
    "start_url": ".",
    "display": "standalone",
    "background_color" : "#{bg}" ,
    "theme_color": "#{bg2}",
    "description": "{desc}",
    """.format(
        name=site_meta['site_name'],
        short_name=site_meta['site_name'],
        bg=site_meta['background_color'],
        bg2=site_meta['background_color'],
        desc=site_meta['site_claim'],
    )

    icons_string = '"icons": ['

    counter = 1
    for icon_size in site_meta['icon_sizes']:
        icons_string += """{{
            "src": "/icon-{}x{}.png",
            "sizes": "{}x{}",
            "type": "image/png"
        }}""".format(icon_size,icon_size,icon_size,icon_size)
        if counter < len(site_meta['icon_sizes']):
            icons_string += ','
        counter += 1

    icons_string += ']'
    webmanifest_string += icons_string
    webmanifest_string += '}'
    webmanifest_file_path = 'output/manifest.webmanifest'

    os.makedirs(os.path.dirname(webmanifest_file_path), exist_ok=True)
    with open(webmanifest_file_path, 'w') as file:
        file.write(webmanifest_string)