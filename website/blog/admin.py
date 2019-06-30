from django.contrib import admin
from . import models

# Register your models here.
class EntryAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'visiting', 'created_time', 'modified_time']
class UserAdmin(admin.ModelAdmin):
    #一览表显示的字段
    list_display = ['username','email','last_login','date_joined','has_confirmed']
    #详细内容显示的字段
    fields = ('username', 'email','last_login','date_joined','password','has_confirmed')
    #侧边栏的过滤器
    list_filter = ['date_joined']
class BookAdmin(admin.ModelAdmin):
    list_display = ['name','category','status','created_time','modified_time']
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name','category','created_time','modified_time']
class UserEmailConfirmAdmin(admin.ModelAdmin):
    list_display = ['user','code','c_time']
admin.site.register(models.Category)
admin.site.register(models.Tag)
admin.site.register(models.Entry,EntryAdmin)
admin.site.register(models.User,UserAdmin)
admin.site.register(models.Book,BookAdmin)
admin.site.register(models.Project,ProjectAdmin)
admin.site.register(models.UserEmailConfirm,UserEmailConfirmAdmin)