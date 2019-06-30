from django.db import models
from django.contrib.auth.models import User as django_user
from django.urls import reverse
import os

def user_image_file_path(instance,filename):
    '''用户头像图片保存在用户名的文件夹下'''
    username = instance.username
    return os.path.join(username,'avatar',filename)
def bolg_image_file_path(instance,filename):
    '''用户博客图片保存在用户名的文件夹下'''
    username = instance.author.username
    return os.path.join(username,'blog_images',filename)

class User(django_user):
    '''用户表'''
    img = models.ImageField(verbose_name='用户头像',null=True,blank=True,
                            upload_to=user_image_file_path)
    #邮件验证字段
    has_confirmed = models.BooleanField(default=False)
    def __str__(self):
        return self.username


class UserEmailConfirm(models.Model):
    '''用户邮件确认注册表'''
    code = models.CharField(max_length=256)
    user = models.OneToOneField('User',on_delete=models.CASCADE)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} : {}'.format(self.user.username,self.code)

    class Meta:
        ordering = ['-c_time']
        verbose_name = '邮件确认码'
        verbose_name_plural = '邮件确认码'

class Category(models.Model):
    '''分类表'''
    name = models.CharField(max_length=128, verbose_name='分类名字')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "博客分类"
        verbose_name_plural = '博客分类'

class Tag(models.Model):
    '''分类下的标签表'''
    category = models.ManyToManyField('Category',verbose_name='所属分类')
    name = models.CharField(max_length=128, verbose_name='标签名字')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "博客标签"
        verbose_name_plural = '博客标签'

class Entry(models.Model):
    '''博客文章表'''
    title = models.CharField(max_length=128, verbose_name='文章标题')
    author = models.ForeignKey('User', verbose_name='博客作者',on_delete=models.DO_NOTHING)
    img = models.ImageField(upload_to=bolg_image_file_path, null=True, blank=True, verbose_name='博客配图')
    body = models.TextField(verbose_name='博客正文')
    visiting = models.PositiveIntegerField(default=0, verbose_name='博客访问量')
    category = models.ManyToManyField('Category', verbose_name='博客分类')
    tags = models.ManyToManyField('Tag', verbose_name='博客标签')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modified_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        '''获取文章的url，用于RSS订阅'''
        return reverse('blog:detail',kwargs={'blog_id':self.id})

    def add_visiting_num(self):
        '''增加访问量'''
        self.visiting +=1
        self.save(update_fields=['visiting'])

    class Meta:
        ordering = ['-created_time']
        verbose_name = "博客"
        verbose_name_plural = '博客'

class Book(models.Model):
    '''书籍表'''
    status_type = (
        (0,'未读'),
        (1,'阅读中'),
        (2,'已读完'),
    )
    name = models.CharField(max_length=100,verbose_name='书本名称')
    category = models.ForeignKey('Category',verbose_name='所属类别',on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(verbose_name='阅读状态',choices=status_type,default=0)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modified_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "书籍"
        verbose_name_plural = '书籍'

class Project(models.Model):
    name = models.CharField(max_length=164,verbose_name='项目名称')
    summary = models.TextField(verbose_name='项目描述',blank=True,null=True)
    category = models.ForeignKey('Category',verbose_name='所属类别',on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modified_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "项目"
        verbose_name_plural = '项目'
