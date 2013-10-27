from django.http import HttpResponse

def index(request):
    return HttpResponse('Rango says hello world, click here for the <a href="/rango/about/">about</a> page')

def about(request):
    return HttpResponse('This is the about page!!! Go back to the rango <a href="/rango/">home page</a>')