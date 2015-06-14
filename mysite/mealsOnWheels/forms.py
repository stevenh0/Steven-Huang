from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import ReadOnlyPasswordHashField
## Reference:
## https://docs.djangoproject.com/en/1.8/_modules/django/contrib/auth/forms/
## http://ipasic.com/article/user-registration-and-email-confirmation-django/
class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True,label="E-mail",widget=forms.TextInput(attrs={'placehoder':'E-mail address'}))
    class Meta:
        model = User
        fields = ('username','email','password1','password2',) ## password1 and password2 are defined in UserCreationForm

    def clean_email(self):
        ## If client specify the email address which is already taken, it fails
        email = self.cleaned_data["email"]
        try:
            User._default_manager.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError('duplicate email')

    # modify save() method so that we can set user.is_active to False when we first create our user
    def save(self,commit=True):
        user = super(RegistrationForm,self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.is_active = False ## Not active until this user opens activation link
            user.save()
        return user

class UserProfileForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('username','email',)

    def clean_password(self):
        return ""
