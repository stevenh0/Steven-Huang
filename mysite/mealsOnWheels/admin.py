from django.contrib import admin
from .models import FoodTruck, Position, last_import_date
from parser import import_data, clear_data, test_import_data, update_json_object
import datetime

last_import_date = last_import_date.objects.get(id=1)

def print_last_import_date():
	if last_import_date.date is not None:
		return last_import_date.date.__str__()
	else:
		return "Never"

def update_database(modeladmin, request, queryset):
	clear_data()
	import_data()
	update_json_object()
	last_import_date.date = datetime.date.today()
	last_import_date.save()
	update_database.short_description = "Fetch new data from City of Vancouver (Last updated: " + print_last_import_date() + ")"
	update_test_database.short_description = "Fetch new data from test file (Last updated: " + print_last_import_date() + ")"

update_database.short_description = "Fetch new data from City of Vancouver (Last updated: " + print_last_import_date() + ")"

def update_test_database(modeladmin, request, queryset):
	clear_data()
	test_import_data()
	update_json_object()
	last_import_date.date = datetime.date.today()
	last_import_date.save()
	update_test_database.short_description = "Fetch new data from test file (Last updated: " + print_last_import_date() + ")"
	update_database.short_description = "Fetch new data from City of Vancouver (Last updated: " + print_last_import_date() + ")"

update_test_database.short_description = "Fetch new data from test file (Last updated: " + print_last_import_date() + ")"

class FoodTruckAdmin(admin.ModelAdmin):
	list_display = ['name', 'foodType']
	ordering = ['name']
	actions = [update_database, update_test_database]

admin.site.register(FoodTruck, FoodTruckAdmin)
admin.site.register(Position)

