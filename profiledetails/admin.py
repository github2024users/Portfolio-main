from django.contrib import admin
from .models import Projects, contactus

class project_admin(admin.ModelAdmin):
    list_display = ("project_title", "project_series", "project_technology", "project_desc")
    search_fields = ("project_title", "project_technology")

class contactus_admin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "created_at")
    list_filter = ("created_at",)  #this is used to filter the list with date in django admin
    search_fields = ("name", "email", "phone") # this is usesd to filter the contact details with given parameters
    readonly_fields = ("created_at",)  #Makes specified fields non-editable in the admin form


admin.site.register(Projects, project_admin)
admin.site.register(contactus,contactus_admin)