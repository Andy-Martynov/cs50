from django import template

register = template.Library()

@register.filter(name='tospace')
def tospace(value, arg):
    return value.replace(arg, ' ')