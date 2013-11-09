from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from rango.forms import PageForm
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime


def encode_url(input_string):
    return input_string.replace(' ', '-')

def decode_url(input_string):
    return input_string.replace('-', ' ')

def index(request):
    context = RequestContext(request)
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict = {'categories': category_list}

    pages_list = Page.objects.order_by('-views')[:5]
    context_dict['pages'] = pages_list

    for category in category_list:
        category.url = encode_url(category.name)

    ## addng code for the cookie counter
    # obtain response early so we can add cookie info
    response = render_to_response('rango/index.html', context_dict, context)

    #call cookie info and cast as int - if the visits cookie doesnt exist, just default to zero
    if request.session.get('last_visit'):
        last_visit_time = request.session.get('last_visit')
        visits = request.session.get('visits',0)

        if (datetime.now() - datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).days > 0:
            request.session['visits'] = visits + 1
            request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = 1

    # visits = int(request.COOKIES.get('visits','0'))

    # if request.COOKIES.has_key('last_visit'):
    #     last_visit = request.COOKIES['last_visit']
    #     # cast value as python date/time object
    #     last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

    #     #if its been more than one day since the last visit
    #     if (datetime.now() - last_visit_time).days > 0:
    #         #set visits to one more than it previously was
    #         response.set_cookie('visits', visits + 1)
    #         response.set_cookie('last_visit', datetime.now())
    # else:
    #     response.set_cookie('last_visit', datetime.now())
    #     response.set_cookie('visits', visits + 1)
    # return response

    return render_to_response('rango/index.html',context_dict,context)


def about(request):
    if request.session.get('visits'):
        return HttpResponse('You have been here ' + str(request.session['visits']))
    else:
        return HttpResponse('This is the about page!!! Go back to the rango <a href="/rango/">home page</a>')

def category(request, category_name_url):
    context = RequestContext(request)
    category_name = decode_url(category_name_url)
    context_dict = {'category_name': category_name}
    context_dict['category_name_url'] = category_name_url

    try:
        category = Category.objects.get(name=category_name)
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages
        context_dict['category'] = category

    except Category.DoesNotExist:
        pass
    return render_to_response('rango/category.html',context_dict,context)

@login_required
def add_category(request):
    context = RequestContext(request)

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print form.errors

    else:
        form = CategoryForm()

    return render_to_response('rango/add_category.html', {'form': form},context)

@login_required
def add_page(request, category_name_url):
    context = RequestContext(request)

    category_name = decode_url(category_name_url)
    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            # This time we cannot commit straight away.
            # Not all fields are automatically populated!
            page = form.save(commit=False)

            # Retrieve the associated Category object so we can add it.
            cat = Category.objects.get(name=category_name)
            page.category = cat

            # Also, create a default value for the number of views.
            page.views = 0

            # With this, we can then save our new model instance.
            page.save()

            # Now that the page is saved, display the category instead.
            return category(request, category_name)
        else:
            print form.errors
    else:
        form = PageForm()

    return render_to_response( 'rango/add_page.html',
            {'category_name_url': category_name_url,
             'category_name': category_name, 'form': form},
             context)

def register(request):
    context = RequestContext(request)

    # set a boolean to determine if a user is registers - start with false, and code will change it to true
    registered = False

    #if the request is a post you need to process the form data
    if request.method == 'POST':

        #now we have to handle two different form inputs
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        #if both of the forms are valid
        if user_form.is_valid() and profile_form.is_valid():

            #save the user form to the database
            user = user_form.save()

            #now we need to hash the password and resave
            user.set_password(user.password)
            user.save()

            #now we handle the user profile instance - we set commit to false in order to wait until we've ser the user attribute
            profile = profile_form.save(commit=False)
            profile.user = user

            #next we need to check and see if the user provided an image for the profile pic

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            #now we can save the profile
            profile.save()

            registered = True
        else:
            print user_form.errors, profile_form.errors

    #if its not a post we simply render the form
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    #no we return the render to template response
    return render_to_response('rango/register.html',
        {'user_form': user_form, 'profile_form': profile_form,'registered': registered},
        context)

def user_login(request):
    context = RequestContext(request)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect('/rango/')
            else:
                HttpResponse("Your rango account is not active")

        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        return render_to_response('rango/login.html',{},context)

@login_required
def user_logout(request):
    logout(request)

    return HttpResponseRedirect('/rango/')