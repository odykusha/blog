import requests
import sys


def get_value(word, left_symb, right_symb):
    return word[word.find(left_symb) + len(left_symb):
                word.find(right_symb,
                word.find(left_symb) + len(left_symb))]


def get_a_tag(link, title=None):
    if not title:
        title = link
    return "<a href='" + link + "' target=\"_blank\">" + title + "</a>"


def get_img_tag(link):
    res = "<a href='" + link + "' target=\"_blank\">" + link + "</a>" + '\n'
    res += "<img src='" + link + "'>"
    return res


def get_youtube_tag(link, title):
    new_link = link\
                .replace('www.youtube.com/watch?v=', 'www.youtube.com/embed/')\
                .replace('&nohtml5=False','')
    res = title + '\n'
    res += "<a href='" + link + "' target=\"_blank\">" + link + "</a>" + '\n'
    res += '<iframe width="560" height="315" src="' + new_link + '" frameborder="0" allowfullscreen></iframe>'
    return res


def get_coub_tag(link, title):
    new_link = link.replace('coub.com/view/', 'coub.com/embed/')
    res = title + '\n'
    res += "<a href='" + link + "' target=\"_blank\">" + link + "</a>" + '\n'
    res += '<iframe src="' + new_link + '?muted=false&autostart=false&originalSize=false&startWithHD=true" allowfullscreen="true" frameborder="0" width="640" height="294"></iframe>'
    return res


def get_tag(some_link):
    try:
        response = requests.get(some_link)
    except requests.exceptions.ProxyError:
        print('||*|| except', sys.exc_info()[0])
        return get_a_tag(some_link)
    except:
        print('||**|| except', sys.exc_info()[0])
        if 'http' in some_link:
            return get_a_tag(some_link)
        return some_link

    CONTENT_TYPE = response.headers['content-type']
    # якщо силка на сайт
    if 'text/html' in CONTENT_TYPE:
        title = get_value(response.text, '<title>', '</title>')

        # якщо ютюб
        if 'YouTube' in title:
            res = get_youtube_tag(response.url, title)

        # якщо коуб
        elif 'coub.com' in response.url.lower():
            res = get_coub_tag(response.url, title)

        # якщо всі інші сайти
        elif 'support@pythonanywhere.com' in title:
            #print("|| support@:", response.url)
            if some_link[-4::] in ['.gif', '.png', '.jpg', '.bmp', '.ico', 'jpeg', 'tiff']:
                res = get_img_tag(some_link)
            else:
                res = get_a_tag(some_link)

        else:
            res = get_a_tag(some_link, title)
        return res

    # якщо ссилка на інший формат: js, css та інше
    elif 'text' in CONTENT_TYPE:
        #print("|| text:", response.url)
        return get_a_tag(response.url)

    # для картинок
    elif 'image' in CONTENT_TYPE:
        #print("|| image:", response.url)
        return get_img_tag(response.url)

    # якщо нідочого не відповідає
    else:
        #print("|| else:", response.url)
        return response.url


def filter(text):
    new_text = text.split()
    for i in new_text:
        text = text.replace(i, get_tag(i))
    return text
