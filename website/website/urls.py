"""website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import handler404, handler500,handler403
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from blog.feed import LatestEntryFeed
from blog import views as blog_views
from blog.models import Entry

info_dict={
    'queryset':Entry.objects.all(),
    'date_field':'modified_time',
}
urlpatterns = [
    path('', blog_views.index),     #主站点
    path('admin/', admin.site.urls),     #管理站点
    path('blog/',include('blog.urls')),    #为博客app设置二级路由
    path('latest/feed/', LatestEntryFeed(), name='rss'),  #用于RSS订阅
    path('sitemap.xml/',sitemap,{
         'sitemaps':{
             'blog':GenericSitemap(info_dict=info_dict,priority=0.6)
         }
    },name='django.contrib.sitemaps.views.sitemap'),      #用于生成sitemap
    path('captcha/', include('captcha.urls')),     #用于生成验证码
    path('comments/', include('django_comments.urls')),    #用于评论系统
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)   #用于设置博客图片的保存url


handler403 = blog_views.permission_denied
handler404 = blog_views.page_not_found
handler500 = blog_views.page_error
