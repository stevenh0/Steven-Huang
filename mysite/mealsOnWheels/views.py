from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
# Create your views here.
from django.contrib.auth.decorators import login_required
import xlrd


## HttpRequest object as the first argument
def index(request):
    return render(request,'mealsOnWheels/index.html',{})



def importData():
    # Persing .xcel file
    ## FTP into the web server
    ftp = FTP('webftp.vancouver.ca')
    ## Log-in as anonymous user
    ftp.login()
    ## change directory into xls
    ftp.cwd('OpenData/xls')
    ## File name of the xls file is:
    filename = 'new_food_vendor_locations.xls'
    ## Retrive the xls file and save it as myLovelyNewFile.xls into my current directory
    ftp.retrbinary('RETR %s' % filename, open('myLovelyNewFile.xls', 'w').write)
    ## Quit ftp
    ftp.quit()
    ## Now read the myLovelyNewFile.xls from my current directry
    workbook = xlrd.open_workbook('myLovelyNewFile.xls')
    ## The first sheet contains our food data
    worksheet = workbook.sheet_by_name('Query_vendor_food')
    return worksheet



from ftplib import FTP
from django.core.mail import EmailMessage
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect,HttpResponse


def user_login(request):
    print("user_login inside")
    ## If the request is a HTTP POST, try to pull out the relevant infomation
    if request.method == 'POST':
        ## Gather the username and password provided by the users
        ## This information is obtained from the login form
        username = request.POST['username']
        print("username: "+ username)
        password = request.POST['password']
        print("password: "+ password)
        user = authenticate(username=username,password=password)

        ## If we have a user object, the details are correct.
        ## If None (Python's way of representing the absence of a value), no user with
        ## matching credentials are found
        if user:
            print("user.is_active: "+ str(user.is_active))
            if user.is_active:

                login(request,user)
                print("login(request,user) is passed!???!")
                return HttpResponseRedirect('/mealsOnWheels/')
            else:
                return HttpResponse("Your meals on wheels account is disabled.")
        else:
            TriedBefore=True
            print "Invalid login details: {0}, {1}".format(username,password)
            return render(request,'mealsOnWheels/login.html',{"TriedBefore":TriedBefore})
            ##HttpResponse("Invalid login details are shipped")
    else:
        TriedBefore=False
        #return HttpResponse("Wow")#
        return render(request,'mealsOnWheels/login.html',{"TriedBefore":TriedBefore})


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
def user_profile(request):
    return render(request,'mealsOnWheels/profile.html',{})

from .forms import *
from .models import *
import hashlib, datetime, random
from django.core.context_processors import csrf

def register_user(request):
    args = {}
    args.update(csrf(request))
    print "register_user: request.method " + str(request.method)

    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        args['form'] = form

        if form.is_valid():
            print "form.is_valid() passed"
            form.save() ## save the registration form (overriden in form.py)
            print "form.save() passed"
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

            ## Send email reference
            ## http://www.mangooranges.com/2008/09/15/sending-email-via-gmail-in-django/
            Subject = 'Account confirmation for Meals on Wheels'
            Body1 = 'Hello %s, \n\nThank you very much for signing up. ' % (username)
            Body2 = 'To activate your account, click this link below within 24 hours: '
            ## Body 3 will be omitted in the future
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

