from flask_wtf import Form
from wtforms import (
    SubmitField, validators, TextAreaField, BooleanField, RadioField
)


###############################################################################
# WTForm's
###############################################################################
class BlogForm(Form):
    blog_text = TextAreaField("text",
        validators=[validators.Length(min=3, message='цей грьобаний текст ніколи не відобразиться')])
    visible_post = BooleanField("Видний усім")
    submit = SubmitField('Добавити')

    blog_text_source = TextAreaField("text")
    visible_post_source = BooleanField("Видний усім")
    submit_source = SubmitField('Змінити')


class RandForm(Form):
    select_role = RadioField(
        choices=[('first', 'first'), ('second', 'second'), ('other', 'other')], default='other')
    first_text = TextAreaField("text")
    second_text = TextAreaField("text")
    other_text = TextAreaField("text")
    save = SubmitField("Зберегти")
    go_rand = SubmitField("Поїхали")
