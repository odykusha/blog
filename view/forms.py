from flask.ext.wtf import Form
from wtforms import SubmitField, \
                    validators, TextAreaField, BooleanField


###############################################################################
# WTForm's
###############################################################################
class BlogForm(Form):
    blog_text = TextAreaField("text",
        [validators.Length(max=3, message='цей грьобаний текст ніколи не відобразиться')])
    visible_post = BooleanField("Видний усім")
    submit = SubmitField('Добавити')

    blog_text_source = TextAreaField("text")
    visible_post_source = BooleanField("Видний усім")
    submit_source = SubmitField('Змінити')