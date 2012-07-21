from django.contrib import admin

from adminfiles.admin import FilePickerAdmin

from test_project.testapp.models import Article

class ArticleAdmin(FilePickerAdmin):
#    adminfiles_fields = {'content': {}, 'title': {}, 'image':{}, }
    adminfiles_fields = ['content', 'title']

admin.site.register(Article, ArticleAdmin)
