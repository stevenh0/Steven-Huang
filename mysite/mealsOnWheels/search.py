from models import FoodTruck, Position, UserJSONObject
import numpy as np
from django.contrib.auth.models import User
import json
from json import dumps
from parser import createJSONObject

def search_by_radius(radius, position, request):
	all_trucks = FoodTruck.objects.all()
	search_results = []
	for truck in all_trucks:
		dist = np.arccos(np.sin(truck.position.lat) * np.sin(position.lat) + np.cos(truck.position.lat) * np.cos(position.lat) * np.cos(truck.position.lon - position.lon)) * 6371
		if dist < radius:
			search_results.append(truck)
	user_json = get_user_json(request)
	user_json.json_object = createJSONString(search_results)
	user_json.save()
	
def createJSONString(trucks):
	dastr = json.dumps(createJSONObject(trucks))
	return dastr

def get_user_json(request):
	curr_user = request.user
	try:
		val = UserJSONObject.objects.get(user=curr_user)
		print "Our thing has a value of " + str(val.pk)
	except UserJSONObject.DoesNotExist:
		val	= UserJSONObject(json_object=createJSONString(FoodTruck.objects.all()), user=curr_user)
		print "Our thing has a value of " + str(val.pk)
		val.save(force_insert=True)
	val	= UserJSONObject(json_object=createJSONString(FoodTruck.objects.all()), user=curr_user)
	val.save(force_update=True)
	return val

def get_user_location(request):
	curr_user = request.user
	try:
		val = UserJSONObject.objects.get(user=curr_user)
		loc = Position.objects.get(id=val.location)
		return str(loc)
	except:
		return None