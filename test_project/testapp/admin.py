from django.contrib import admin

from adminfiles.admin import FilePickerAdmin

from test_project.testapp.models import Article

class ArticleAdmin(FilePickerAdmin, admin.ModelAdmin):
    adminfiles_fields = {
        'content': {'browser_position': 'left', 'toolbox_position': 'left'},
        'title': {}
    }

admin.site.register(Article, ArticleAdmin)
