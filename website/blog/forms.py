from django import forms
from captcha.fields import CaptchaField ,CaptchaTextInput
from .models import Entry ,Book ,Project,User,Tag
class AddTagFormModel(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name','category']
        widgets = {
            'name':forms.TextInput(attrs={
                'class':'form-control',
                'autofocus':'True',
            }),
        }

class EditBlogModelForm(forms.ModelForm):
    '''编辑博客用模型表单'''
    #captcha = CaptchaField(label='验证码', widget=CaptchaTextInput(attrs={'class': 'yanzhen'}))
    class Meta :
        model = Entry
        fields =['title','body','img','category','tags','author']
        widgets = {
            'title':forms.TextInput(attrs={
                'class':'form-control',
                'autofocus': 'True',
                'style':'width:80%;margin-bottom:5px;'
            }),
            'body':forms.Textarea(attrs={
                'class':'form-control',
                'rows':'20',
            }),
        }

class LoginForm(forms.Form):
    '''登录用表单'''
    username = forms.CharField(max_length=30,label='用户名',widget=forms.TextInput(attrs={
        'class':'form-control',
        'placeholder':'用户名',
        'autofocus': 'True',
    }))
    password = forms.CharField(max_length=50,label='密码',widget=forms.PasswordInput(attrs={
        'class':'form-control',
        'placeholder': '密码',
    }))
    captcha = CaptchaField(label='验证码', widget=CaptchaTextInput(attrs={
        'class': 'yanzhen',
    }))

class RegisterModelForm(forms.ModelForm):
    '''注册用模型表单'''
    captcha = CaptchaField(label='验证码', widget=CaptchaTextInput(attrs={
        'class': 'yanzhen',
    }))
    ensure_password = forms.CharField(max_length=50,label='确认密码',widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': '确认密码',
    }))
    class Meta:
        model = User
        fields = ['username','password','email','img']
        help_texts = {
            'email':'请填写正确的邮箱,注册时会发确认邮件',

        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '名字要在4到14个字符',
                'autofocus': 'True',
            }),
            'password':forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': '密码至少8个字符',
            }),
            'email':forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': '邮箱',
            }),
        }
class AddEditBookModelForm(forms.ModelForm):
    '''编辑书籍用模型表单'''
    class Meta:
        model = Book
        fields = ['name','category','status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
            }),
        }

class AddEditProjectModelForm(forms.ModelForm):
    '''编辑项目用模型表单'''
    class Meta:
        model = Project
        fields = ['name','summary','category']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'summary': forms.Textarea(attrs={
                'class':'form-control',
            }),
        }

class ChangePersonProfileForm(forms.Form):
    '''修改个人简介用表单'''
    username = forms.CharField(max_length=30, label='更换用户名', widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': '用户名要在4到14个字符',
        'autofocus': 'True',
    }))
    email = forms.EmailField(label='更换邮箱',widget=forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': '邮箱',
    }))
    img = forms.ImageField(label='更换头像',required=False)

class ChangePasswordForm(forms.Form):
    '''修改密码用表单'''
    old_password = forms.CharField(max_length=50, label='旧密码',
                                              widget=forms.PasswordInput(attrs={
                                                  'class': 'form-control',
                                                  'placeholder': '旧密码',
                                                  'autofocus': 'True',
                                              }))
    new_password = forms.CharField(max_length=50, label='新密码',
                                              widget=forms.PasswordInput(attrs={
                                                  'class': 'form-control',
                                                  'placeholder': '新密码',
                                              }))
    ensure_new_password =forms.CharField(max_length=50, label='确认密码',
                                              widget=forms.PasswordInput(attrs={
                                                  'class': 'form-control',
                                                  'placeholder': '确认密码',
                                              }))
