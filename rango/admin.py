# -*- coding: utf-8 -*-

from django.contrib import admin
from .models import Category, Page

# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}


admin.site.register(Category)
admin.site.register(Page)