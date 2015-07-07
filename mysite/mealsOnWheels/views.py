from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
# Create your views here.
from django.contrib.auth.decorators import login_required
import xlrd


## HttpRequest object as the first argument
def index(request):
    return render(request,'mealsOnWheels/index.html',{})



def importData():
    ftp = FTP('webftp.vancouver.ca')
    ftp.login()
    ftp.cwd('OpenData/xls')
    filename = 'new_food_vendor_locations.xls'
    ftp.retrbinary('RETR %s' % filename, open('myLovelyNewFile.xls', 'w').write)
    ftp.quit()
    workbook = xlrd.open_workbook('myLovelyNewFile.xls')
    worksheet = workbook.sheet_by_name('Query_vendor_food')
    return worksheet



from ftplib import FTP
from django.core.mail import EmailMessage
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect,HttpResponse


def user_login(request):
    ## If the request is a HTTP POST, try to pull out the relevant infomation
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username,password=password)
        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect('/mealsOnWheels/')
            else:
                message="disable"
                return render(request,'mealsOnWheels/login.html',{"message":message})
        else:
            message="invalid"
            return render(request,'mealsOnWheels/login.html',{"message":message})
    else:
        message="work"
        return render(request,'mealsOnWheels/login.html',{"message":message})


from django.contrib.auth import logout

# User the login_required decorator to ensure only those logged in can access to the view
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out
    logout(request)
    # Take the user back to the index page
    return HttpResponseRedirect('/mealsOnWheels/')

@login_required
def render_map(request):
    return render(request,'mealsOnWheels/map.html',{})

@login_required
def render_json(request):
    return render(request,'mealsOnWheels/food_trucks.json',{})

@login_required
def render_about(request):
    return render(request,'mealsOnWheels/about.html',{})

from .forms import *
from .models import *
import hashlib, datetime, random
from django.core.context_processors import csrf

## Send email reference
## http://www.mangooranges.com/2008/09/15/sending-email-via-gmail-in-django/
def register_user(request):
    args = {}
    args.update(csrf(request))

    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        args['form'] = form

        if form.is_valid():
            form.save() ## save the registration form (overriden in form.py)
            ## saved user is NOT ACTIVE YET
            ## Necessary for the confirmation email
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            ## To generate activation key we used random and hashlib modules
            ## # because we wanted to get some random number which we use to create SHA hash.
            salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
            ## combined that 'salt' value with user's username
            ## to get final value of activation key that will be sent to user
            activation_key = hashlib.sha1(salt + email).hexdigest()
            ## set the date when the activation key will expire
            key_expires = datetime.datetime.today() + datetime.timedelta(days=1)
            #Get user by username
            user=User.objects.get(username=username)
            # Create and save a new userprofile which is connected to User that we have just created
            # we pass to it values of activation key and key expiration date.
            new_profile = UserProfile(user=user,activation_key=activation_key,key_expires=key_expires)
            new_profile.save()


            Subject = 'Account confirmation for Meals on Wheels'
            Body1 = 'Hello %s, \n\nThank you very much for signing up. ' % (username)
            Body2 = 'To activate your account, click this link below within 24 hours: '
            Body3 = '\nhttp://127.0.0.1:8000/mealsOnWheels/confirm/%s' % (activation_key)
            Body4 = '\nhttp://djanguars.pythonanywhere.com/mealsOnWheels/confirm/%s' % (activation_key)
            email = EmailMessage(Subject, Body1+Body2+Body3 + Body4, to=[email])
            email.send()

            return render(request,'mealsOnWheels/registration_step1.html',{})
        else:
            print form.errors
    else:
       args['form'] = RegistrationForm()

    return render(
            request,
        'mealsOnWheels/register.html',
        args
    )

def register_confirm(request, activation_key):
    # check if user is already logged in
    if request.user.is_authenticated():
        HttpResponseRedirect('/mealsOnWeels')
    # check if there is UserProfile which matches the activation key if not then display 404
    user_profile = get_object_or_404(UserProfile,activation_key=activation_key)
    # check if the activation key has expired if it has then render confirm_expired.html
    if user_profile.key_expires < timezone.now():
        return HttpResponse("The activation key has been expired.")
    # if the key has not been expired, then save user and set him as active and render some template to confirm activation.
    user = user_profile.user
    user.is_active = True
    user.save()
    return render(request,'mealsOnWheels/registration_confirm.html',{})

@login_required
def change_profile_settings(request):

    # A boolean value for telling the template whether the user settings changed.
    # Set to False initially. Code changes value to True when the setting change succeeds.
    settings_changed = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        user_form = UserProfileForm(request.POST, instance=request.user)

        # If the form is valid...
        if user_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            password = user_form.cleaned_data['password']
            user.set_password(password)
            user.save()

            # Update our variable to tell the template the settings change was successful.
            settings_changed = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors

    # Not a HTTP POST, so we render our form.
    # The form will be blank, ready for user input.
    else:
        user_form = UserProfileForm(instance=request.user)

    # Render the template depending on the context.
    return render(request,
            'mealsOnWheels/profile.html',
            {'user_form': user_form, 'settings_changed': settings_changed} )
