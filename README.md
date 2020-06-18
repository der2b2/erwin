# Erwin SSG
python static site generator for blogs
(built and testet with python3)

## Features
- Templating with Jinja2
- SASS compiler
- Twitter and Facebook Cards
- Simple image processing with automated generation of different file sizes for responsive images with picture tag
- pipenv bundled
- reading time calculation
- Sitemap
- 3 Types of content:
  -- homepage
  -- posts or articles
  -- pages (for static content like about, privacy police or disclaimer)
- tags for posts

## Install
Install pipenv:
```
pip install pipenv
```
Download Erwin SSG and change into folder:
```
git clone https://github.com/der2b2/erwin.git
cd erwin-ssg
```
Generate and change to virtual environment with pipenv:
```
pipenv shell
```
Install dependencies:
```
pipenv install
```

## Usage
There are three scripts that can be run:
### clean.py
Clean the output folder, basically erases the complete output folder to get rid of old files
```
python clean.py
```

### build.py
This script builds the whole website and stores it ready for deploying into the output folder
```
python build.py
```

### serve.py
Starts a simple local Webserver for testing. The webserver just serves the stored files from the build script.
```
python serve.py
```
Server runs on "localhost:8000"

