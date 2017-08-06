from django import template

register = template.Library()


@register.filter(name='first_word')
def first_word(sentence):
    words = sentence.split()
    if len(words) > 0:
        return words[0]
    else:
        return ''
