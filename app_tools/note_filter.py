import requests


STOP_WORDS = ['script', 'console']

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
        return get_a_tag(some_link)
    except:
        if 'http' in some_link[0:4]:
            return get_a_tag(some_link)
        # xss atack
        for stop_word in STOP_WORDS:
            if stop_word in some_link:
                some_link = some_link.replace(stop_word, '<img src="/static/img/noway-small.png" height="15px" width="15px" title="# '+ stop_word +'"/>')
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
            if some_link[-4::] in ['.gif', '.png', '.jpg', '.bmp', '.ico', 'jpeg', 'tiff']:
                res = get_img_tag(some_link)
            else:
                res = get_a_tag(some_link)

        else:
            res = get_a_tag(some_link, title)
        return res

    # якщо ссилка на інший формат: js, css та інше
    elif 'text' in CONTENT_TYPE:
        return get_a_tag(response.url)

    # для картинок
    elif 'image' in CONTENT_TYPE:
        return get_img_tag(response.url)

    # якщо нідочого не відповідає
    else:
        # print('##', response.url)
        return response.url


def filter(text):
    new_text = text.split()
    for i in new_text:
        text = text.replace(i, get_tag(i))
    return text


# -------------------------------------------------------------------------------------------------------------------- #
def generate_html_block_note(data):
    note_block = '<!-- тіло комента -->'+\
    '<table class="post_head" id="'+ str(data['note_id']) +'">'+\
            '<tr>'+\
        '<td rowspan="2" style="width: 30px;"> <img src="' + data['photo'] + '" class="vk_image"> </td>'+\
                '<td class="left">'+\
                    '<small>'+\
                    '<div>'+\
                        '<a class="not_like_link_id" href="/view/'+ str(data['note_id']) +'"> ІД: '+ str(data['note_id']) +'</a>'+\
                    '</div>'+\
                    '</small>'+\
                '</td>'+\
            '<!-- видно всім -->'+\
            '<td class="right">'+\
                '<small>'+\
                        '<div class="visible" style="display: none;">видно всім</div>'+\
            '</small>'+\
        '</td>'+\
    '</tr>'+\
'<!-- автор запису -->'+\
            '<tr><td class="left">'+\
                '<h2 class="post">'+\
                    '<a class="not_like_link_user" href="/users/'+ str(data['user_id']) + '"> '+ data['user_name'] +' </a>'+\
                    '<!-- соус поста -->'+\
                    '<img src="/static/img/edit.png" name="edit_this_post" id="'+ str(data['note_id']) +'" title="Редагувати"/>'+\
                '</h2>'+\
            '</td>'+\
            '<td class="right">'+\
                '<small>'+\
                        data['timestamp'] +\
                        '<!-- кнопка видалення -->'+\
                        ' <img src="/static/img/trash.png" name="delete_everything" id='+ str(data['note_id']) +' title="Видалити" />'+\
                        '<span id="'+ str(data['note_id']) +'" name="delete_hide_form" style="display:none;">'+\
                            '<abbr title="Видаляй" name="delete_yes">'+\
                                '<img src="/static/img/accept.png"/>'+\
                            '</abbr>'+\
                            ' / '+\
                            '<abbr title="Я передумав" name="delete_no">'+\
                                '<img src="/static/img/cancel.png"/>'+\
                            '</abbr>'+\
                        '</span>'+\
                '</small>'+\
            '</td>'+\
        '</tr>'+\
    '</table>'+\
    '<!-- тіло комента -->'+\
    '<table class="posts" id="'+ str(data['note_id']) +'">'+\
        '<td>'+\
            '<pre>'+ data['note_text'] +'</pre>'+\
            '<div name="hidden_change_post" id="'+ str(data['note_id']) + '" class="hidden_post" role="form">'+\
                '<input id="visible_post_source" name="visible_post_source" type="checkbox" value="y">відображати пост усім <br>'+\
                '<textarea cols="70" id="blog_text_source" name="blog_text_source" placeholder="Текст напишіть тут. Можливе використання тегів" rows="7"></textarea><br>'+\
                '<input id="submit_source" name="submit_source" type="submit" value="Змінити">'+\
            '</div>'+\
        '</td>'+\
    '</table>'

    return note_block


# -------------------------------------------------------------------------------------------------------------------- #
if __name__ == '__main__':
    text = """фільтрувати текст
            "console",
            "script",
            "console"
            "script"
            """
    print('|ORIGINAL|', text)
    print('|CHANGING|', filter(text))

    data = {'note_id': 333, 'user_id': 666, 'user_name': 'USER', 'timestamp': '01.03.2017 14:21', 'note_text': 'some fucking text, bla bla bla', 'photo': 'http://www.some.com'}
    print('||ORIGINAL||', data)
    print('||HTML GEN||', generate_html_block_note(data))