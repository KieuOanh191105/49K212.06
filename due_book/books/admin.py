from django.contrib import admin
from .models import Book,User,Subject
# Register your models here.


# Register your models here.

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', "code", "description",)
    
