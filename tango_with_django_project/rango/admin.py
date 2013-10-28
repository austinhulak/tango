from django.contrib import admin
from rango.models import Category, Page

class CategoryAdmin(admin.ModelAdmin):
    #rules go here
    fields = ['name','views','likes']
    list_display = ('name','views','likes')
class PageAdmin(admin.ModelAdmin):
    #rules go here
    fields = ['category','title','url','views']
    list_display = ('category','title','url','views')
    list_filter = ['category']
admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)