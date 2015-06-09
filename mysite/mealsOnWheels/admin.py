from django.contrib import admin
from .models import Question,Choice, FoodTruck
from parser import importData, clearData, testImportData, updateJSONObject

# Register your models here.
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class stupidnameAdmin(admin.ModelAdmin):
    list_display = ('pub_date','was_published_recently',
                    'question_text','question_text',)
    list_filter = ['pub_date','question_text',]
    search_fields = ('question_text',)
    ##    fields=['pub_date']
    ##fields = ['pub_date','question_text']
    fieldsets = [
         ('Date information',{'fields':['pub_date'],'classes':['collapse']}),
          (None,            {'fields':['question_text']}),
        ]
    inlines = [ChoiceInline]

admin.site.register(Question,stupidnameAdmin)
## admin.site.register(Choice)

def updateDatabase(modeladmin, request, queryset):
    clearData()
    importData()
    updateJSONObject()

updateDatabase.short_description = "Clear all data and fetch new data from City of Vancouver"

def updateTestDatabase(modeladmin, request, queryset):
    clearData()
    testImportData()
    updateJSONObject()

updateTestDatabase.short_description = "Clear all data and populate from test file"

class FoodTruckAdmin(admin.ModelAdmin):
    list_display = ['name', 'foodType']
    ordering = ['name']
    actions = [updateDatabase, updateTestDatabase]

admin.site.register(FoodTruck, FoodTruckAdmin)