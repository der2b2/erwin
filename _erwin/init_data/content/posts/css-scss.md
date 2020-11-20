---
title: CSS and SCSS
date: 2020-05-27
tags: Features
img: pankaj-patel-6JVlSdgMacE-unsplash.jpg
summary: A scss compiler and a working solution for critical css loading
slug: css-scss
---

## The files
- /assets/css/main.css 
  * your main css
  * will be compiled and stored to /output/css/mani.css
  * will be inserted as file in the end of the html body for faster loading
- /assets/css/critical-main.scss
  * your critical css
  * will be compiled and stored to /output/css/critical-main.css
  * will be inserted inline to the head of your html
  * you can insert critical html by hand or use a tool, more on this see below

## SCSS compiler
Erwin uses the python sass library to compile all SASS in main.scss and critical-main.scss

## Generating critical css
You can write your critical css by hand and copy it into /assets/css/critical-main.scss.

While this is a valid approach, it is very tiresome, especially while using a css framework like bootstrap.

My approach / recommendation:

- empty the delivered standard critical-main.scss file (when critical-main.scss is empty, main.scss is used by Erwin)
- Write and style your site during development as usually with main.scss and your preferred css framework
- publish your site onto the final server and final domain
- go to [https://jonassebastianohlsson.com/criticalpathcssgenerator/](https://jonassebastianohlsson.com/criticalpathcssgenerator/)
- let this awsome tool generate all critical css for you
- copy the generated css into /assets/css/critical-main.scss
- rebuild and republish your site
- feel the speeeeeeed

