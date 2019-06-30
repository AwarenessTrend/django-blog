from django.urls import path, include
from . import views

app_name = 'blog'
urlpatterns = [
    path('',views.index, name='index'),   #首页
    path('<int:blog_id>/', views.detail,name='detail'), #博客详细内容
    path('category/<int:category_id>/', views.category_entry_show,name='category'), #根据分类过滤博客
    path('tag/<int:tag_id>/', views.tag_entry_show,name='tag'),   #根据标签过滤博客
    path('search/',views.search, name='search'),  #搜索功能
    path('archives/<int:year>/<int:month>/',views.archives,name='archives'), #根据归档(创建时间）过滤博客
    path('login/',views.login,name='login'),     #登录账号
    path('logout/',views.logout,name='logout'),  #注销账号
    path('register/',views.register,name='register'),  #注册账号
    path('change_password/',views.change_password,name='change_password'),   #修改密码
    path('person_profile/',views.person_profile,name='person_profile'),  #个人简介
    path('change_person_profile/',views.change_person_profile,name='change_person_profile'),
    path('reply/<int:comment_id>/',views.reply_comment,name='reply_comment'),    #多级评论
    path('add_blog/',views.add_blog,name='add_blog'),  #新增博客
    path('edit_blog/<int:entry_id>/',views.edit_blog,name='edit_blog'),  #编辑博客
    path('my_info/',views.my_info,name='my_info'),  #关于我
    path('add_book/',views.add_book,name='add_book'),    #添加书籍
    path('add_project/',views.add_project,name='add_project'),   #添加项目
    path('edit_book/<int:book_id>/',views.edit_book,name='edit_book'),   #修改书籍
    path('edit_project/<int:project_id>/',views.edit_project,name='edit_project'),  #修改项目
    path('show_project/<int:project_id>/',views.show_project,name='show_project'),    #显示项目详细信息
    path('add_tag/',views.add_tag,name='add_tag'),  #增加标签
    path('delete/',views.delete,name='delete'),  #删除博客，书籍，项目
    path('email_confirm/',views.email_confirm,name='email_confirm'),   #邮箱验证处理
    path('test/',views.test), #测试用
]
