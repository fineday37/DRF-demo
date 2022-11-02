from django import forms


class UserForm(forms.Form):
    username = forms.CharField(label="用户名", max_length=10, widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(label="密码", max_length=30, widget=forms.PasswordInput(attrs={"class": "form-control"}))


class MusicTest(forms.Form):
    singer = forms.CharField(label="歌手", max_length=10)
    location = forms.CharField(label="位置", max_length=20)
