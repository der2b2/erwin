---
title: Speed and Security
date: 2019-04-17
tags: Features
img: chuttersnap-eH_ftJYhaTY-unsplash.jpg
summary: It's like a website on drugs. 
slug: speed
---

Static site generators produce static sites. There is no workload on the server side.

So there is less (almost none) work to do for the server, which results in faster loading times.

Because the sites are static, there is no weak point in the site itself like bad php scripts that can be used by hackers to gain access to the server.

You don't have to worry about security updates.

## Speed tweaks

While working on erwin, i learned a lot about web technology. To increase the speed of the generates sites, i added a way to implement critical css. 

A big focus was to get images fast and easy to work with, so i developed a simple image processing function that generates images in several sizes and implemented those in the template to get responsive images.

See how Erwin performs in the Google Chrome Lighthouse test for a image rich site:

![Erwin SSG Speed](/img/erwin-ssg-speed.jpg)
[ernaehrung-ist-gesund.de](https://www.ernaehrung-ist-gesund.de)

