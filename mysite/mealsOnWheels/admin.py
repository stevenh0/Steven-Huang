from django.contrib import admin
from .models import FoodTruck
from parser import importData, clearData, testImportData, updateJSONObject



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