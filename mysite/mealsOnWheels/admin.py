from django.contrib import admin
from .models import FoodTruck, Position, LastImportDate,Review
from parser import importData, clearData, testImportData, updateJSONObject
from search import reset_all_users_json
import datetime

lastImportDate = LastImportDate.objects.get(id=1)

def printLastImportDate():
	if lastImportDate.date is not None:
		return lastImportDate.date.__str__()
	else:
		return "Never"


def getDatabase(out=False):
	clearData()
	reset_all_users_json()
	worksheet = importData(out=out)
	updateJSONObject()
	lastImportDate.date = datetime.date.today()
	lastImportDate.save()
	updateDatabase.short_description = "Fetch new data from City of Vancouver (Last updated: " + printLastImportDate() + ")"
	updateTestDatabase.short_description = "Fetch new data from test file (Last updated: " + printLastImportDate() + ")"
	if out:
		return worksheet

def updateDatabase(modeladmin, request, queryset):
	getDatabase()

updateDatabase.short_description = "Fetch new data from City of Vancouver (Last updated: " + printLastImportDate() + ")"

def updateTestDatabase(modeladmin, request, queryset):
	clearData()
	reset_all_users_json()
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



def reset_json(modeladmin, request, queryset):
	reset_all_users_json()



from mealsOnWheels.fakeUsers import generateFakeUser
def generateUser(modeladmin, request, queryset):
	generateFakeUser()

from django.contrib import messages
from mealsOnWheels.recommender import runClustering
def classifyUser(modeladmin, request, queryset):
	try:
		runClustering()
	except:
		messages.error(request, "This functionality is currently not supported")

generateUser.short_description = "Generate bob and 100 users (Asian-food lovers, seafood lovers, " \
									"hotdogs lovers and those with no preference)"
classifyUser.short_description = "Classify these users into four clusters of similar rating behaviors"


from django.contrib.auth.models import User
class ReviewInline(admin.TabularInline):
	model = Review
	extra = 5


class UserAdmin(admin.ModelAdmin):
	list_display = ['name','email','is_stuff']
	actions = [generateUser,classifyUser,reset_json]
	inlines = [ReviewInline]


UserAdmin.list_display = ('username','email', 'is_active', 'date_joined', 'is_staff')
admin.site.unregister(User)
admin.site.register(User, UserAdmin)