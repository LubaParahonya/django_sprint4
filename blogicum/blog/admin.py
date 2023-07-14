from django.contrib import admin

from .models import Category, Location, Post

admin.site.register(Category)
admin.site.register(Location)


@admin.register(Post)
class UserAdmin(admin.ModelAdmin):
    list_display = ['title', 'text']
    list_editable = ['text']
