#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import urllib.request
import os
import img2pdf

from os import walk
from os.path import join
from bs4 import BeautifulSoup

work_dir = os.path.dirname(__file__)

def safe_filename(filename):
    return "".join([c for c in filename if c.isalpha() or c.isdigit() or c==' ']).rstrip()


def safe_download(img_url, img_file):
    print("Safe Download '%s' to '%s'" % (img_url, img_file))
    for i in range(10):
        command = 'wget %s -O %s --quiet' % (img_url, img_file)
        ret = os.system(command)
        if ret == 0:
            break
        else:
            print("Retry %8d ..." % i)

def guess_title(soup):
    title = safe_filename(soup.title.string)
    print("Title : '%s'" % title)
    spans = soup.findAll('span', {'class': 'j-title-breadcrumb'})
    if len(spans) == 1:
        title = safe_filename(spans[0].text.strip())
        print("SPAN title : '%s'" % title)
    return title

def download_images(url):
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html)
    title = 'pdf_images'  # soup.title.string
    pdf_filename = "%s.pdf" % guess_title(soup)
    images = soup.findAll('img', {'class': 'slide_image'})
    os.system("mkdir -p pdf_images")

    for idx, image in enumerate(images):
        image_url = image.get('data-full').split('?')[0]
        img_file = "pdf_images/%08d.jpg" % idx
        safe_download(image_url, img_file)

    convert_pdf(title, pdf_filename)


def convert_pdf(url, pdf_filename=None):
    if not pdf_filename:
        pdf_filename = "presentation.pdf"

    f = []
    for (dirpath, dirnames, filenames) in walk(url):
        f.extend(filenames)
        break
    f = sorted(["%s/%s" % (url, x) for x in f])
    print("Making pdf")

    pdf_bytes = img2pdf.convert(f, dpi=300, x=None, y=None)
    with open(pdf_filename, "wb") as doc:
        doc.write(pdf_bytes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", type=str,
                        help="download an slideshare presentation given the url")
    args = parser.parse_args()

    download_images(args.url)
    os.system('rm -r pdf_images')

