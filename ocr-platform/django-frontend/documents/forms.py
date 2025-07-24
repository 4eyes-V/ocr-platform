from django import forms
from .models import Doc


class DocUploadForm(forms.ModelForm):
    class Meta:
        model = Doc
        fields = ['file_path']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file_path'].widget.attrs.update({'class': 'form-control'})


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })