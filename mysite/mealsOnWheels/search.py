from models import FoodTruck, Position, UserJSONObject
import numpy as np
from django.contrib.auth.models import User
import json
from json import dumps
from parser import createJSONObject

def search_by_radius(radius, position, request):
	parr = position.split(",")
	plat = np.radians(float(parr[0]))
	plon = np.radians(float(parr[1]))
	all_trucks = FoodTruck.objects.all()
	search_results = []
	for truck in all_trucks:
		tlat = np.radians(truck.position.lat)
		tlon = np.radians(truck.position.lon)
		dist = np.arccos(np.sin(tlat) * np.sin(plat) + np.cos(tlat) * np.cos(plat) * np.cos(tlon - plon)) * 6371
		print "This truck is " + str(dist) + "away"
		i = 0
		if dist < float(radius):
			i = i + 1
			search_results.append(truck)
	user_json = get_user_json(request)
	print "Num matches: " + str(i)
	print "Search results: " + str(search_results)
	new_json = createJSONString(search_results)
	print "new_json:" + new_json
	user_json.json_object = new_json
	user_json.save()
	
def createJSONString(trucks):
	print "createJSONString was called"
	dastr = json.dumps(createJSONObject(trucks))
	return dastr

def get_user_json(request):
	curr_user = request.user
	try:
		val = UserJSONObject.objects.get(user=curr_user)
	except UserJSONObject.DoesNotExist:
		val	= UserJSONObject(json_object=createJSONString(FoodTruck.objects.all()), user=curr_user)
		val.save()
	return val

def get_user_location(request):
	curr_user = request.user
	val = get_user_json(request)
	if val.location != None:
		return str(val.location.lat) + "," + str(val.location.lon)
	else:
		return None