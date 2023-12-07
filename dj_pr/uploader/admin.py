from django.contrib import admin
from . import models

class DiagnosisAdmin(admin.ModelAdmin):
    search_fields = ['pet_name__petname']
    
class PetAdmin(admin.ModelAdmin):
    search_fields = ['users_id__users_id']


admin.site.register(models.Diagnosis, DiagnosisAdmin)
admin.site.register(models.Pet, PetAdmin)
# Register your models here.
