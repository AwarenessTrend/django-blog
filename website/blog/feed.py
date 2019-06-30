from django.contrib.syndication.views import Feed
from django.urls import reverse
from .models import Entry

class LatestEntryFeed(Feed):
    title = '我的博客网站'
    link = '/blog/'
    description = '最新的博客'

    def items(self):
        return  Entry.objects.all()[:5]

    def item_title(self,item):
        return item.title

    # def item_description(self, item):
    #     return item.body[:10]

    #def item_link(self, item):
     #   return reverse('xxx',args=item.pk)

