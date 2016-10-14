from django import template

register = template.Library()


@register.filter(name='first_word')
def first_word(sentence):
    return sentence.split()[0]
