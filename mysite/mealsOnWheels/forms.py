
from django.contrib.auth.models import User
from django import forms

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ('username','email','password',)


## ---- code above are old ---
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True,label="E-mail",widget=forms.TextInput(attrs={'placehoder':'E-mail address'}))
    password1 = forms.CharField(required=True,label="Password",
                                help_text="Please enter your password",widget=forms.PasswordInput())
    password2 = forms.CharField(required=True,label="Password",
                                help_text="Please reenter your password",widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ('username','email','password2','password1',)

    def clean_password1(self):
        ## This function is called by form.is_valid()
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        print "password1" + str(password1)
        print "password2" + str(password2)
        ## If a client specify two different passwords then Error message appears
        if password1 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")

        return password1

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
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.is_active = False ## Not active until this user opens activation link
            user.save()
        return user






