import requests
import sys

def get_value(word, left_symb, right_symb):
    return word[word.find(left_symb) + len(left_symb):
                word.find(right_symb,
                word.find(left_symb) + len(left_symb))]


def get_tag(some_link):
    try:
        response = requests.get(some_link)
    # except urllib.error.URLError:
    #     print('||*|| except', sys.exc_info()[0])
    #     return some_link
    except:
        print('||**|| except', sys.exc_info()[0])
        return some_link
    CONTENT_TYPE = response.headers['content-type']
    # якщо силка на сайт
    if 'text/html' in CONTENT_TYPE:
        print('Content-type: text/html', some_link)
        title = get_value(response.text, '<title>', '</title>')
        # якщо ютюб
        if 'YouTube' in title:
            print('YouTube: Content-type: text/html', some_link)
            new_link = response.url\
                .replace('www.youtube.com/watch?v=', 'www.youtube.com/embed/')\
                .replace('&nohtml5=False','')
            res = title + '\n'
            res += "<a href='" + response.url + "' target=\"_blank\">" + response.url + "</a>" + '\n'
            res += '<iframe width="560" height="315" src="' + new_link + '" frameborder="0" allowfullscreen></iframe>'
        # якщо коуб
        elif 'coub.com' in response.url.lower():
            print('COUB: Content-type: text/html', some_link)
            new_link = response.url.replace('coub.com/view/', 'coub.com/embed/')
            res = title + '\n'
            res += "<a href='" + response.url + "' target=\"_blank\">" + response.url + "</a>" + '\n'
            res += '<iframe src="' + new_link + '?muted=false&autostart=false&originalSize=false&startWithHD=true" allowfullscreen="true" frameborder="0" width="640" height="294"></iframe>'
        # якщо всі інші сайти
        else:
            print('else: Content-type: text/html', some_link)
            res = "<a href='" + some_link + "' target=\"_blank\">" + title + "</a>"
        return res
    # якщо ссилка на інший формат: js, css та інше
    elif 'text' in CONTENT_TYPE:
        print('Content-type: text', some_link)
        return "<a href='" + response.url + "' target=\"_blank\">" + response.url + "</a>"
    # для картинок
    elif 'image' in CONTENT_TYPE:
        print('Content-type: image/..', some_link)
        res = "<a href='" + response.url + "'>" + response.url + "</a>" + '\n'
        res += "<img src='" + response.url + "'>"
        return res
    # якщо нідочого не відповідає
    else:
        print('some else', some_link)
        return response.url