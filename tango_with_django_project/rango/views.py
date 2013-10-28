from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm

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

    return render_to_response('rango/index.html', context_dict, context)

def about(request):
    return HttpResponse('This is the about page!!! Go back to the rango <a href="/rango/">home page</a>')

def category(request, category_name_url):
    context = RequestContext(request)
    category_name = decode_url(category_name_url)
    context_dict = {'category_name': category_name}

    try:
        category = Category.objects.get(name=category_name)
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        pass
    return render_to_response('rango/category.html',context_dict,context)

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

