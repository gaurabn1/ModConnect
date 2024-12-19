from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Post)
admin.site.register(Follow)
admin.site.register(Notification)

class CommentAdmin(admin.ModelAdmin):
    search_fields = ['id']

admin.site.register(Comment, CommentAdmin)
