from django.contrib import admin
from django.contrib.auth.admin import User
from django.contrib.auth.admin import UserAdmin as OriginalUserAdmin
from poll.models import *

admin.site.register(Journal)
admin.site.register(Project)
admin.site.register(Institute)
admin.site.register(Instrument)
admin.site.register(Cart)

# From http://nerdydevel.blogspot.gr/2012/07/extending-django-user-model.html
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    
class UserAdmin(OriginalUserAdmin):
    inlines = [UserProfileInline, ]


    
try:
    admin.site.unregister(User)
finally:
    admin.site.register(User, UserAdmin)


