from bs4 import BeautifulSoup as bs4
import requests
import urllib
import argparse
import wget
import os
import sys
import lxml

imagenum = 0
chapter_explain = '!under construction! Chapters You Wanna Scrape, Example: -C 12 [Gets Chapter 12], -C 1~4 [Gets Chapter 1, 2, 3, 4]'
name = "" #folder name here
parsed_url = ''

def check_url(in_url):
    try:
        global parsed_url
        parsed_url = requests.get(in_url).text
    except:
        print("Wrong url, check your internet connection or the url")
        sys.exit()

def better_dirname(dirname):
    dirname = dirname.replace(' ', '-')
    dirname = dirname.replace(':', '')
    dirname = dirname.replace('*', '')
    dirname = dirname.replace('?', '')
    dirname = dirname.replace('"', '')
    dirname = dirname.replace("'", '')
    dirname = dirname.replace('|', '')
    dirname = dirname.replace('>', '')
    dirname = dirname.replace('<', '')
    dirname = dirname.lower()
    return dirname

def create_dir(html):
    soup = bs4(html, 'lxml')
    global name
    # Try to get manga name from <h1 class="entry-title"> or fallback to URL
    h1 = soup.find('h1', {'class': 'entry-title'})
    if h1 and h1.text.strip():
        name = better_dirname(h1.text.strip())
    else:
        # fallback: use last part of URL
        from urllib.parse import urlparse
        path = urlparse(sys.argv[-1]).path
        name = better_dirname(path.strip('/').split('/')[-2] if '/' in path else path)
    if not name:
        print("Could not determine manga name. Exiting.")
        sys.exit(1)
    if not os.path.exists(name):
        os.makedirs(name)

def get_list(html):
    global imagenum
    soup = bs4(html, 'html.parser')
    # Find all <div class="flex flex-col justify-center items-center">
    divs = soup.find_all('div', {'class': 'flex flex-col justify-center items-center'})
    for div in divs:
        imgtags = div.find_all('img')
        for image in imgtags:
            img_url = image.get('src') or image.get('data-src')
            if img_url:
                print("Downloading " + img_url + " 🐱‍🏍")
                get_image(img_url)
                imagenum += 1

def get_image(url):
    import os
    import requests
    from urllib.parse import urlparse
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        filename = os.path.basename(urlparse(url).path)
        filepath = os.path.join(name, filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
    except Exception as e:
        print(f"Failed to download {url}: {e}")

def initiate(url):
    check_url(url)
    create_dir(parsed_url)
    get_list(parsed_url)

# initiate(parsed_url)
if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description='Download Manga from OmegaScans 🍌', usage='%(prog)s [options] URL', epilog='Thanks for using %(prog)s ✌')
        parser.add_argument('url', help='The URL to manga 🔥')
        args = parser.parse_args()
        initiate(args.url)
        print("Downloaded " + str(imagenum) + " images 🥳")
    except KeyboardInterrupt:
        print('\nKeyboard interrupt detected \nBye 😔')
