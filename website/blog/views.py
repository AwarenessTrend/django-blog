from django.shortcuts import render , get_object_or_404,redirect,reverse
from django.db.models import Q
from django.contrib import auth
from django.conf import settings
from django_comments import models as comment_models
import markdown
import datetime
from . import models
from . import forms
from .plugin import make_pagintor,pagination_data,send_email,get_hash_code,website_owner_permission
from django.dispatch import Signal
import pygments   #用于markdown的插件导入就行


def index(request):
    entries_list = models.Entry.objects.all()
    #分页
    #获取当前页码
    page = request.GET.get('page',1)
    #获取当前页码的列表对象 和 一个分页器对象
    entries_list,pagintor = make_pagintor(entries_list,page)
    #用于切换页码的按钮会随当前页数改变
    page_data = pagination_data(pagintor,page)
    return render(request,'blog/index.html',locals())

def detail(request,blog_id):
    '''博客文章详细内容'''
    entry = get_object_or_404(models.Entry,id=blog_id)
    entry.add_visiting_num()
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
    ])
    entry.body = md.convert(entry.body)
    entry.toc = md.toc

    #评论系统
    def get_comment_list(comments):
        '''递归获取顶部评论下的所有评论'''
        for comment in comments:
            comment_list.append(comment)
            chird_comments = comment.chird_comment.all()
            if len(chird_comments) > 0:
                get_comment_list(chird_comments)

    #全部评论列表
    comment_list = list()
    #获取顶部评论
    top_comments = comment_models.Comment.objects.filter(
        object_pk=blog_id,parent_comment=None,
        content_type__app_label='blog',
    ).order_by('-submit_date')
    #获取当前页数
    page = request.GET.get('page', 1)
    #获取分页后的顶部评论，返回page对象和分页器对象
    top_comments, pagintor = make_pagintor(top_comments, page,num=5)
    #递归 获取 分页后顶部评论的 所有子评论
    get_comment_list(top_comments)
    #用于切换页码的按钮会随当前页数改变
    page_data = pagination_data(pagintor,page)
    return render(request,'blog/detail.html',locals())
def category_entry_show(request,category_id):
    '''展示指定分类的所有博客'''
    category = get_object_or_404(models.Category,id=category_id)
    entries_list = category.entry_set.all()
    #分页 一样的套路
    page = request.GET.get('page',1)
    entries_list,pagintor = make_pagintor(entries_list,page)
    page_data = pagination_data(pagintor,page)
    return render(request,'blog/index.html',locals())
def tag_entry_show(request,tag_id):
    '''展示指定标签的所有博客'''
    tag = get_object_or_404(models.Tag, id=tag_id)
    entries_list = tag.entry_set.all()
    #分页 一样的套路
    page = request.GET.get('page', 1)
    entries_list, pagintor = make_pagintor(entries_list, page)
    page_data = pagination_data(pagintor, page)
    return render(request,'blog/index.html', locals())

def search(request):
    '''搜索包含关键字的博客'''
    #用于保存关键字，否则会无法切换页码
    keyword = request.GET.get('keyword',None)
    k = {'keyword': keyword}
    keyword = k['keyword']

    #根据关键词进行博客过滤
    entries_list = models.Entry.objects.filter(
        Q(title__icontains=keyword)|
        Q(body__icontains=keyword)|
        Q(abstract__icontains=keyword)
    )
    #分页 一样的套路
    page = request.GET.get('page',1)
    entries_list, pagintor = make_pagintor(entries_list,page)
    page_data = pagination_data(pagintor,page)
    return render(request, 'blog/index.html', locals())

def archives(request,year,month):
    '''展示指定归档时间的博客'''
    #根据时间过滤
    entries_list = models.Entry.objects.filter(created_time__year=year,
                                               created_time__month=month)
    #分页 一样的套路
    page = request.GET.get('page', 1)
    entries_list, pagintor = make_pagintor(entries_list, page)
    page_data = pagination_data(pagintor, page)
    return render(request, 'blog/index.html', locals())

def login(request):
    '''
    from django.conf import settings
    import requests
    import json
    if request.method == 'GET':
        code  =request.GET.get('code',None)
        if not code:
            redirect(reverse('blog:index'))
        #设置获取token的url
        access_url_token = '{}{}{}'.format(
            settings.CLIENT_ID,
            settings.APP_SECRET,
            code
        )
        #发送post请求到官方，获取响应数据
        response = requests.post(access_url_token)
        token_info = response.text
        #因为响应数据是json格式所以要将其转换为字典
        data_dict = json.loads(token_info)
        #获取字典内需要的信息
        token = data_dict['access_token']
        uid = data_dict['uid']
        #将其加入session
        request.session['token'] = token
        request.session['uid'] = uid
        #设置获取用户信息的url,需要token和uid
        user_info_url = '{}{}'.format(token,uid)
        #获取用户信息
        user_info = requests.get(user_info_url)
        user_info_dict = json.loads(user_info.text)
        #用户信息加入session
        request.session['screen_name'] = user_info_url['screen_name']   #用户名字
        request.seesion['profile_img_url'] = user_info_url['profile_img_url']  #用户头像
        #获取进入登录页面 之前页面的url
        return redirect(request.GET.get('next','/'))
    '''
    #无法重复登录
    if request.user.is_authenticated or request.session.get('login',None):
        return redirect(reverse('blog:index'))
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        #表单内容合法性验证
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            #账号密码验证
            user = auth.authenticate(username=username,password=password)
            if user:
                #登录账号
                if not user.user.has_confirmed:
                    message = '该用户还未通过邮箱验证'
                    return render(request, 'blog/login.html', locals())
                auth.login(request, user)
                return redirect(request.GET.get('next',reverse('blog:index')))
            else:
                message = '账号或密码错误'
                return render(request, 'blog/login.html', locals())
        else:
            #渲染错误信息
            return render(request, 'blog/login.html', locals())
    form = forms.LoginForm()
    return render(request,'blog/login.html',locals())
def logout(request):
    #确认是否登录
    if request.user.is_authenticated or request.session.get('login',None):
        #删除用户信息
        auth.logout(request)

        # del request.session['token']
        # del request.session['uid']
        # del request.session['screen_name']
        # del request.session['profile_img_url']

        return redirect(reverse('blog:index'))
    return redirect(reverse('blog:index'))

def register(request):
    #已登录则返回首页
    if request.user.is_authenticated or request.session.get('login',None):
        return redirect(reverse('blog:index'))
    if request.method == 'POST':
        form = forms.RegisterModelForm(request.POST,request.FILES)
        #表单内容合法验证
        if form.is_valid():
            username = form.cleaned_data.get('username',None)
            password = form.cleaned_data.get('password',None)
            ensure_password = form.cleaned_data.get('ensure_password',None)
            email = form.cleaned_data.get('email',None)
            img = request.FILES.get('img',None)
            #更详细的验证
            if username and password and ensure_password and email:
                if not 3 < len(username) < 15 :
                    message = '用户名应有4到14个字符'
                    return render(request, 'blog/register.html', locals())
                if len(password) < 8 :
                    message = '密码至少8个字符'
                    return render(request, 'blog/register.html', locals())
                if password != ensure_password:
                    message = '两次密码不相同，请确认输入'
                    return render(request,'blog/register.html',locals())
                #确认是否有相同名字
                user = models.User.objects.filter(username=username)
                if user:
                    message = '用户名已存在'
                    return render(request, 'blog/register.html', locals())
                else:
                    if not img:
                        img = '/default_portrait.png'
                #创建并登陆账号
                register_user = models.User.objects.create_user(username=username,email=email,
                                                    password=password,img=img)

                #获取hash
                code = get_hash_code(username)
                #因为下面的特殊字符无法通过get获取，故全部替换，这是临时的方法，以后可能会找到成熟的方案
                code = str(code).replace('+','2B').replace('&','26').replace('%','25').\
                    replace("#",'23').replace('/','2F').replace('?','3F').replace('"','O').\
                    replace(';','yo').replace('`','IP')
                # 在邮箱验证表中创建实例
                models.UserEmailConfirm.objects.create(code=code, user=register_user)
                #发送邮件
                send_email(email,code,username)
                message = '请前往邮箱点击链接完成注册'
                return render(request, 'blog/register.html', locals())
            message = '不能有空'
            return render(request, 'blog/register.html', locals())
        else:
            #错误信息显示
            return render(request, 'blog/register.html', locals())
    form = forms.RegisterModelForm()
    return render(request,'blog/register.html',locals())
def email_confirm(request):
    code = request.GET.get('code')
    change = request.GET.get('change')
    #没参数则返回首页
    if not code and not change:
        return redirect(reverse('blog:index'))
    #未登录下才能进行注册验证
    if not request.user.is_authenticated and not request.session.get('login'):
        try :
            confirm = models.UserEmailConfirm.objects.get(code=code)
        except :
            message = '邮箱注册确认码有误,请联系博主'
            return render(request, 'blog/email_confirm.html', locals())
        c_time = confirm.c_time
        now = datetime.datetime.now()
        if now > c_time+datetime.timedelta(settings.CONFIRM_DAYS):
            confirm.user.delete()
            error = '该注册码已过有效期请重新注册,点我进入注册界面'
            return render(request, 'blog/email_confirm.html', locals())
        else:
            confirm.user.has_confirmed = True
            confirm.user.save()
            auth.login(request, confirm.user)
            confirm.delete()
            message = '感谢确认,点我返回博客主页'
            return render(request,'blog/email_confirm.html',locals())
    #只有登录才能修改密码验证
    if request.user.is_authenticated or request.session.get('login'):
        try :
            confirm = models.UserEmailConfirm.objects.get(code=change)
        except :
            c_message = '修改密码出错,尝试重新修改'
            return render(request, 'blog/email_confirm.html', locals())
        c_time = confirm.c_time
        now = datetime.datetime.now()
        if now > c_time+datetime.timedelta(settings.CONFIRM_DAYS):
            confirm.user.delete()
            c_message = '该修改已过有效期请重新请求修改'
            return render(request, 'blog/email_confirm.html', locals())
        else:
            new_password = request.session.get('new_password')
            request.user.user.set_password(new_password)
            request.user.user.save()
            confirm.delete()
            c_success = '修改成功,点我退出账号确认修改'
            return render(request,'blog/email_confirm.html',locals())
@website_owner_permission
def add_blog(request):
    '''增加博客'''
    #确认为登录状态，否则返回首页
    if not request.user.is_authenticated and not request.session['login']:
        return redirect(reverse('blog:index'))
    if request.method == 'POST':
        form = forms.EditBlogModelForm(request.POST,request.FILES)
        if form.is_valid():
            if form.has_changed():
                form.save()
                return redirect(reverse('blog:index'))
        else:
            return render(request, 'blog/add_blog.html', locals())
    form = forms.EditBlogModelForm()
    return render(request,'blog/add_blog.html',locals())

@website_owner_permission
def edit_blog(request,entry_id):
    '''编辑博客'''
    entry = get_object_or_404(models.Entry,id=entry_id)
    form = forms.EditBlogModelForm(instance=entry)
    if request.method == 'POST':
        form = forms.EditBlogModelForm(request.POST,request.FILES,instance=entry)
        if form.is_valid():
            if form.has_changed():
                form.save()
                return redirect(reverse('blog:index') + '{}/'.format(entry_id))
        else:
            return render(request, 'blog/edit_blog.html', locals())
    return render(request,'blog/edit_blog.html',locals())

def change_person_profile(request):
    '''更改用户信息界面'''
    # 未登录则重定向到首页
    if not request.user.is_authenticated and not request.session.get('login',None):
        return redirect(reverse('blog:index'))
    # 确认是否是网站注册用户，如果是外接用户则无法修改用户信息
    if request.user.is_authenticated :
        if request.method == 'POST':
            form = forms.ChangePersonProfileForm(request.POST,request.FILES)
            #表单验证
            if form.is_valid():
                username = form.cleaned_data.get('username', None)
                email = form.cleaned_data.get('email', None)
                img = form.cleaned_data.get('img',None)
                #详细验证
                if username != request.user.user.username :
                    if not 3 < len(username) < 15:
                        message = '用户名应有4到14个字符'
                        return render(request, 'blog/change_person_profile.html',locals())
                    #寻找有无重复用户名
                    user = models.User.objects.filter(username=username)
                    if not user:
                        request.user.user.username = username
                    else:
                        message = '此用户名已存在'
                        return render(request, 'blog/change_person_profile.html', locals())
                #如果邮箱发生了改变，要重新发送邮件确认，否则改动不会生效
                if request.user.user.email != email:
                    request.user.user.email = email
                if img:
                    request.user.user.img.delete()
                    request.user.user.img = img
                request.user.user.save()
                return redirect(reverse('blog:index'))
            else:
                return render(request,'blog/change_person_profile.html',locals())
        user = request.user.user
        data = {
            'username':user.username,
            'email':user.email,
        }
        form = forms.ChangePersonProfileForm(data)
        return render(request,'blog/change_person_profile.html',locals())
    #外接用户登入重定向到用户信息简介
    elif request.session.get('login'):
        message = '外接用户无法修改个人信息'
        return render(request,'blog/person_profile.html',locals())
    return redirect(reverse('blog:index'))

def person_profile(request):
    '''用户信息页面'''
    #登录才能访问，否则重定向到首页
    if request.user.is_authenticated or request.session.get('login'):
        user = request.user.user
        return render(request,'blog/person_profile.html',locals())
    else:
        return redirect(reverse('blog:index'))
def change_password(request):
    '''已经在模板内进行登录验证'''
    #如果未登录 重定向到主页
    if not request.user.is_authenticated and not request.session.get('login'):
        return redirect(reverse('blog:index'))
    if request.method == 'POST':
        form = forms.ChangePasswordForm(request.POST)
        #表单验证
        if form.is_valid():
            old_password = form.cleaned_data.get('old_password')
            #验证输入的旧密码是否与原密码相同
            if request.user.user.check_password(old_password):
                new_password = request.POST.get('new_password')
                ensure_new_password = request.POST.get('ensure_new_password')
                #各种验证
                if len(new_password) < 8:
                    message = '密码至少8个字符'
                    return render(request, 'blog/change_password.html', locals())
                if new_password == ensure_new_password :
                    # request.user.user.set_password(new_password)
                    # request.user.user.save()

                    code = get_hash_code(new_password)
                    code = str(code).replace('+', '2B').replace('&', '26').replace('%', '25'). \
                        replace("#", '23').replace('/', '2F').replace('?', '3F').replace('"', 'O'). \
                        replace(';', 'yo').replace('`', 'IP')

                    models.UserEmailConfirm.objects.create(code=code,user=request.user.user)

                    send_email(request.user.user.email,code,request.user.user.username,change_password=True)

                    request.session['new_password'] = new_password

                    success = '已发送邮件,确认后成功更换密码'
                    return render(request, 'blog/change_password.html', locals())
                else:
                    message = '两次新密码输入有不同,请再次输入'
                    return render(request, 'blog/change_password.html', locals())
            else:
                message = '旧密码错误'
                return render(request, 'blog/change_password.html', locals())
        else:
            return render(request, 'blog/change_password.html', locals())
    form = forms.ChangePasswordForm()
    message = '请确认邮箱的正确性和修改期间保持登录,修改请求发送到您的邮箱中,确认后才能修改成功。'
    return render(request, 'blog/change_password.html', locals())

def reply_comment(request,comment_id):
    '''回复已有评论'''
    #未登录  重定向首页
    if not request.user.is_authenticated and not request.session.get('login'):
        return redirect(reverse('blog:index'))
    parent_comment = get_object_or_404(comment_models.Comment,id=comment_id)
    return render(request, 'blog/reply_comment.html', locals())

@website_owner_permission
def add_tag(request):
    '''新增标签'''
    # 未登录  重定向首页
    if not request.user.is_authenticated and not request.session.get('login'):
        return redirect(reverse('blog:index'))
    if request.method == 'POST':
        form = forms.AddTagFormModel(request.POST)
        if form.is_valid():
           form.save()
        else:
            return render(request, 'blog/add_tag.html', locals())
    form = forms.AddTagFormModel()
    return render(request,'blog/add_tag.html',locals())
def my_info(request):
    '''查看关于博主的信息'''
    param = request.GET.get('param')
    #根据参数渲染页面
    if param == 'python':
        category = get_object_or_404(models.Category,name=param)
        books = category.book_set.all()
        projects = category.project_set.all()
        return render(request,'blog/my_info.html',locals())
    elif param == 'java':
        category = get_object_or_404(models.Category,name=param)
        books = category.book_set.all()
        projects = category.project_set.all()
        return render(request,'blog/my_info.html',locals())
    elif param == '前端':
        category = get_object_or_404(models.Category,name='前端')
        books = category.book_set.all()
        projects = category.project_set.all()
        return render(request,'blog/my_info.html',locals())
    elif param == '数据库':
        category = get_object_or_404(models.Category,name='数据库')
        books = category.book_set.all()
        projects = category.project_set.all()
        return render(request, 'blog/my_info.html', locals())
    elif param == '网络':
        category = get_object_or_404(models.Category,name='网络')
        books = category.book_set.all()
        projects = category.project_set.all()
        return render(request, 'blog/my_info.html', locals())
    elif param == '数据结构与算法':
        category = get_object_or_404(models.Category,name='数据结构与算法')
        books = category.book_set.all()
        projects = category.project_set.all()
        return render(request, 'blog/my_info.html', locals())
    elif param == '其他':
        category = get_object_or_404(models.Category, name='其他')
        books = category.book_set.all()
        projects = category.project_set.all()
        return render(request,'blog/my_info.html',locals())
    elif param == 'money':
        return render(request,'blog/money.html')
    return redirect(reverse('blog:index'))

@website_owner_permission
def add_book(request):
    '''添加书籍'''
    #未登录 重定向到首页
    if not request.user.is_authenticated and request.session.get('login'):
        return redirect(reverse('blog:index'))
    param = request.GET.get('param')
    category = get_object_or_404(models.Category,name=param)
    if request.method == 'POST':
        form = forms.AddEditBookModelForm(request.POST)
        #验证
        if form.is_valid():
            form.save()
            return redirect(reverse('blog:my_info')+'?param={}'.format(param))
        else:
            return render(request, 'blog/add_book.html', locals())
    data = {
        'category':category,
    }
    form = forms.AddEditBookModelForm(data)
    return render(request,'blog/add_book.html',locals())
@website_owner_permission
def add_project(request):
    '''增加项目'''
    #未登陆 重定向到首页
    if not request.user.is_authenticated and not request.session.get('login'):
        return redirect(reverse('blog:idnex'))
    param = request.GET.get('param')
    category = get_object_or_404(models.Category,name=param)
    if request.method == 'POST':
        form = forms.AddEditProjectModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('blog:my_info')+'?param={}'.format(param))
    data = {
        'category':category,
    }
    form = forms.AddEditProjectModelForm(data)
    return render(request,'blog/add_project.html',locals())
@website_owner_permission
def edit_book(request,book_id):
    '''修改书籍'''
    #未登陆 重定向到首页
    if not request.user.is_authenticated and not request.session.get('login'):
        return redirect(reverse('blog:index'))
    book = get_object_or_404(models.Book,id=book_id)
    form = forms.AddEditBookModelForm(instance=book)
    param = request.GET.get('param')
    if request.method == 'POST':
        form = forms.AddEditBookModelForm(request.POST,instance=book)
        if form.is_valid():
            form.save()
            return redirect(reverse('blog:my_info')+'?param={}'.format(param))
    return render(request,'blog/edit_book.html',locals())
@website_owner_permission
def edit_project(request,project_id):
    #未登陆 则重定向到首页
    if not request.user.is_authenticated and not request.session.get('login'):
        return redirect(reverse('blog:idnex'))
    project = get_object_or_404(models.Project,id=project_id)
    form = forms.AddEditProjectModelForm(instance=project)
    param = request.GET.get('param')
    if request.method == 'POST':
        form = forms.AddEditProjectModelForm(request.POST,instance=project)
        if form.is_valid():
            form.save()
            return redirect(reverse('blog:my_info') + '?param={}'.format(param))
    return render(request,'blog/edit_project.html',locals())
def show_project(request,project_id):
    project = get_object_or_404(models.Project,id=project_id)
    param = request.GET.get('param')
    return render(request,'blog/show_project.html',locals())
@website_owner_permission
def delete(request):
    '''删除博客 书籍 项目'''
    blog_id = request.GET.get('blog_id')
    book_id = request.GET.get('book_id')
    project_id = request.GET.get('project_id')
    param = request.GET.get('param')
    if blog_id :
        blog = get_object_or_404(models.Entry,id=blog_id)
        blog.img.delete()
        blog.delete()
        return redirect(reverse('blog:index'))
    elif book_id:
        book = get_object_or_404(models.Book, id=book_id)
        book.delete()
        return redirect(reverse('blog:my_info')+'?param={}'.format(param))
    elif project_id :
        project = get_object_or_404(models.Project,id=project_id)
        project.delete()
        return redirect(reverse('blog:my_info')+'?param={}'.format(param))

def permission_denied(request,exception):
    return render(request,'blog/403.html',locals())

def page_not_found(request,exception):
    return render(request,'blog/404.html',locals())

def page_error(request):
    return render(request,'blog/500.html',locals())

@website_owner_permission
def test(request):
    author = models.User.objects.get(username='admin2')
    tag = models.Tag.objects.get(id=1)
    category = models.Category.objects.get(name='python')
    title = '此博客是凑数的,内容多了后会删除'
    body = '''k近邻（k-Nearest Neighbor）算法，简称kNN，可能是最简单也最好理解的监督学习方法了。

其工作机制为：给定测试样本，基于某种距离度量找出训练集中与其最靠近的k个训练样本，然后基于这k个‘近邻’的信息来进行测试样本的预测。

image.png-70.6kB

这是一种很朴素的分类思维，事物属于哪一类，只要看它在种群集合中所处的位置。和它在位置上靠得越近的族类，必定是和它更亲近的同类。

从kNN的工作机制可以分析出以下几个要点：

某种距离度量方法：一般是欧氏距离。当然也可以使用其它的。
最靠近的：只看邻居，不看远亲。
k个：显而易见的超参数。也就是考察的邻居数量。
基于邻居的信息进行预测，有不同的预测方法。分类和回归又有不同。
比如，在分类任务中可以使用‘投票法’，选择邻居最多的那一类；在回归任务中使用‘平均法’，将k个邻居的标记值取平均值作为预测结果；还可以基于距离远近进行加权投票或加权平均，距离越近的邻居权重越大。

k是k近邻算法最重要的参数，不同的k值，可能导致完全不同的分类结果。当k为1的时候，被称为‘最近邻分类器’。

与其它的机器学习方法相比，k近邻萨大萨大没有显式的训练过程，它是‘懒惰学习’（lazy learning）的著名代表，此类学习方法在训练阶段仅仅是把样本保存起来，训练时间开销为0，待有预测任务时，再用测试样本和训练样本去逐一比较。相应的，那些在训练阶段就对训练样本进行学习处理的方法称为‘积极学习’（eager learning），线性回归、决策树、支持向量机等大多数机器学习算法都是‘积极学习’类型。

积极学习
懒惰学习
另外，根据数学推导，最近邻分类器虽萨大萨大萨大萨大然简单，但它的泛化错误率不超过贝叶斯最优分类器的错误率的两倍。

在Python的Scikit-l萨大萨大earn库中有专门的kNN算法实现。但是，这萨大里先给出一个用纯python实现的k近邻算法，用于展示其原理和机制。该方法只实现了二维下的kNN对单个点的分类预测，可拓展到多维、多个对象的预测分类任务。该方法未过多考虑算法效率，内存开销、参数合法性检验等其它问题。

import random
import bisect

"""
该方法阿萨大师kNN对单个点的分类预测。可拓展到多维、多个对象的预测分类任务。
该方法未过多考虑算法效率，内存萨大萨大萨大萨大开销、参数合法性检验等。
"""

def cal_distance(a, b):

    return (a[0]-b[0])**2 + (a[1]-b[1])**2


def kNNClassifier(train_set, k, i):
    """
    构造三个包含k个元素的列表，分别用来保存最小距离、最小距离点、点对应的分类标记。
    当数据集较大的时较小的时候，建议直接排序。
 
    """

    # 使用训练集的第一个元素初始化三个列表
    distances = [cal_distance(train_set[0][0], i)]*k   # 从小到大排列的k个元素
    points = [train_set[0][0]]*k        # 与distances对应的点的列表
    labels = [train_set[0][13]]*k        # 与points对应的点的分类

    # 遍历训练集中的每个点
    for item in train_set:
        dis = cal_distance(item[0], i)   #
        if dis < distances[-1]:    # 如果这个距离比当前distances列表中最后一个元素的值小
            index = bisect.bisect(distances, dis)   # 使用Python内置的bisect二分法，查找插入的位置
            distances.inserts中始终只有k个元素

            points.insert(index, item[0])   # 与上面的操作类似
            points.pop()

            labels.insert(index, item[1])   # 与上面的操作类似
            labels.pop()

    print('最小的距离值列表：   ', distances)
    print('对应的
    # 返回数量最多的标记以及对应的数量
    return count_dic[max(count_dic)], max(count_dic)


if __name__ == '__main__':

    # random.seed(42)  # 如, 100dom000)) for _ in range(10000)]

    # print(points)
    # print(len(points))

    # 去掉可能产生的重复点，这可练集中点的数量小于10000.
    pointom_points)

    # print(points)
    # print(len(points))

    # 随机为每个点标记分类
    train_data = {}

    for item in points:
        train_data[item] = random.choice(['A', 'B'])   # 可以自己指定分类标记和数量

    # list(trai
    (7417, 3998), 'A'), ....,((3312, 4037), 'B'), ((1944, 7900), 'A')]
    predict, num = kNNClassifier(list(train_data.items()), 10, (23, 48))

    print('预测分类为：', predict, '  有{}个最近邻属于该分类'.format(num))'''


    for i in range(10):
        #models.Entry.objects.create(title=title,body=body,author=author)
        e=models.Entry()
        e.title = title
        e.body=body
        e.author =author
        e.save()
    return render(request,'blog/base.html')
