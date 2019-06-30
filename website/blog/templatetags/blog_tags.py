from django import template
from ..models import Entry,Category,Tag

register = template.Library()

@register.simple_tag
def get_recent_blog(num=5):
    return Entry.objects.all().order_by('-created_time')[0:num]

@register.simple_tag
def get_popular_blog(num=5):
    return Entry.objects.all().order_by('-visiting')[0:num]

@register.simple_tag
def get_all_category():
    return Category.objects.all()

@register.simple_tag
def archives():
    return Entry.objects.dates('created_time','month',order='DESC')

@register.simple_tag
def get_blog_num_in_time(month,year):
    return Entry.objects.filter(created_time__year=year,created_time__month=month).count()

@register.simple_tag
def get_all_tags():
    return Tag.objects.all()

