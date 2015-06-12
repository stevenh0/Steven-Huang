from django.contrib import admin
from .models import FoodTruck, Position, LastImportDate
from parser import importData, clearData, testImportData, updateJSONObject
import datetime

lastImportDate = LastImportDate.objects.get(id=1)

def printLastImportDate():
	if lastImportDate.date is not None:
		return lastImportDate.date.__str__()
	else:
		return "Never"

def updateDatabase(modeladmin, request, queryset):
	clearData()
	importData()
	updateJSONObject()
	lastImportDate.date = datetime.date.today()
	lastImportDate.save()
	updateDatabase.short_description = "Fetch new data from City of Vancouver (Last updated: " + printLastImportDate() + ")"
	updateTestDatabase.short_description = "Fetch new data from test file (Last updated: " + printLastImportDate() + ")"

updateDatabase.short_description = "Fetch new data from City of Vancouver (Last updated: " + printLastImportDate() + ")"

def updateTestDatabase(modeladmin, request, queryset):
	clearData()
	testImportData()
	updateJSONObject()
	lastImportDate.date = datetime.date.today()
	lastImportDate.save()
	updateTestDatabase.short_description = "Fetch new data from test file (Last updated: " + printLastImportDate() + ")"
	updateDatabase.short_description = "Fetch new data from City of Vancouver (Last updated: " + printLastImportDate() + ")"

updateTestDatabase.short_description = "Fetch new data from test file (Last updated: " + printLastImportDate() + ")"

class FoodTruckAdmin(admin.ModelAdmin):
    list_display = ['name', 'foodType']
    ordering = ['name']
    actions = [updateDatabase, updateTestDatabase]

admin.site.register(FoodTruck, FoodTruckAdmin)
admin.site.register(Position)

