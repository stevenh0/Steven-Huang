from django.shortcuts import render, get_object_or_404
from .models import Choice,Question
from django.template import RequestContext, loader
from django.http import HttpResponseRedirect
# Create your views here.
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

import xlrd
import requests
import requests_ftp

## HttpRequest object as the first argument
def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    ##template = loader.get_template('mealsOnWheels/index.html')
    ##context = RequestContext(request, {
    ##    'latest_question_list': latest_question_list,
    ##})
    ##return HttpResponse(template.render(context))
    context = {'latest_question_list':latest_question_list}
    return render(request,'mealsOnWheels/index.html',context)


@login_required
def detail(request, question_id):
    question = get_object_or_404(Question,pk=question_id)
    return render(request,'mealsOnWheels/detail.html',{'question': question})





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
#def results(request,question_id):
#    response = "You are looking at the results of question %s."
#    return HttpResponse(response % question_id)
@login_required
def results(request,question_id):
    question = get_object_or_404(Question,pk=question_id)


    worksheet = importData()
    ## The following shows each row of the downloaded data
    num_rows = worksheet.nrows - 1
    curr_row = -1
    while curr_row < num_rows:
	    curr_row += 1
	    row = worksheet.row(curr_row)
	    print row




    return render(request,'mealsOnWheels/results.html',{'question':question})

@login_required
def vote(request, question_id):
    p = get_object_or_404(Question,pk=question_id)
    try:
        print("I am printing request.POST['choice']: " + request.POST['choice'])
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        ## Redisplay the question voting form
        dict = {'question':p,'error_message':"You did not select any choice stupid! (from vote in views.py)"}
        return render(request, 'mealsOnWheels/detail.html',dict)
        ##  return HttpResponse("You are voting on question %s" % question_id)
    else:
        ## parameters checking
        print("choice_text is: "+ selected_choice.choice_text)
        print("selected_choice.votes: "+str(selected_choice.votes))

        selected_choice.votes += 1
        selected_choice.save()
        ## HttpResponseRedirect only takes single argument: the URLto which the user will be re-directed
        ## so does this call urlconf???

        return HttpResponseRedirect(reverse('mealsOnWheels:results', args=(p.id,)))


from .forms import UserForm, UserProfileForm
from django.core.mail import EmailMessage

def register(request):
    ## get the request's context
    ## context=RequestContext(request)
    ## A boolean value for telling the template whether the registration was
    ## succeesful. Set to False initially.

    registered = False
    print("request.method: "+request.method)
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        print("user_form.is_valid(): " + str(user_form.is_valid()))
        print("profile_form.is_valid():"+ str(profile_form.is_valid()))
        if user_form.is_valid() and profile_form.is_valid():
            print("within if statement")
            user = user_form.save()
            print("user_form.save() passed correctly")
            user.set_password(user.password)
            print("user.set_password(user.password) passed correctly")
            profile = profile_form.save(commit=False)
            print("rofile_form.save() passed correctly")
            profile.user = user
            print("profile.user = user passed correctly")
            profile.save()
            print("profile.save() passed correctly")
            user.save()
            print("user.id: "+ str(user.id))


            ## Send email reference
            ## http://www.mangooranges.com/2008/09/15/sending-email-via-gmail-in-django/
            Subject = 'Well Done! Registration to Foods on Wheel is completed!'
            Body1 = 'Hi ' + user.username + ','
            Body2 = '\nThank you very much for registering to our Foods on Wheel.'
            Body3 =  '\nCheck out our awesome website at\n'+'http://127.0.0.1:8000/mealsOnWheels/login/'
            email = EmailMessage(Subject, Body1+Body2+Body3, to=[user.email])
            email.send()

            print("profile.id: "+str(profile.id))
            registered =True

        else:
            print user_form.errors, profile_form.errors
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    print("registered: "+str(registered))
    return render(
        request,
        'mealsOnWheels/register.html',
        {
            'user_form': user_form,
            'profile_form': profile_form,
            'registered':registered,
        }
    )

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

        ## If we have a user object, the dtails are correct.
        ## If None (Python's way of representing the absence of a value), no user with
        ## matching credentials are found
        if user:
            print("user.is_active: "+ str(user.is_active))
            if user.is_active:

                login(request,user)
                print("login(request,user) is passed!???!")
                return HttpResponseRedirect('/mealsOnWheels/')
            else:
                return HttpResponse("Your Poll2 account is disabled.")
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
