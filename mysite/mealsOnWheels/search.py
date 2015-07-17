from models import FoodTruck, Position, UserJSONObject
import numpy as np
from django.contrib.auth.models import User
import json
from json import dumps
from django.db.models import Q

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
		i = 0
		if dist < float(radius):
			i = i + 1
			search_results.append(truck)
	user_json = get_user_json(request)
	new_json = createJSONString(search_results)
	user_json.json_object = new_json
	user_json.save()

def search_by_term(term, request):
	all_trucks = FoodTruck.objects.all()
	search_results = all_trucks.filter(Q(name__icontains=term) | Q(location__icontains=term) | Q(foodType__icontains=term))
	user_json = get_user_json(request)
	new_json = createJSONString(search_results)
	user_json.json_object = new_json
	user_json.save()

def createJSONString(trucks):
	dastr = json.dumps(createJSONObject(trucks))
	return dastr

def get_user_json(request):
	print "get_user_json 1"
	curr_user = request.user
	print "get_user_json 2"
	try:
		val = UserJSONObject.objects.get(user=curr_user)
		print "get_user_json 3"
	except UserJSONObject.DoesNotExist:
		print "get_user_json 4"
		val	= UserJSONObject(json_object=createJSONString(FoodTruck.objects.all()), user=curr_user)
		print "get_user_json 5"
		val.save()
		print "get_user_json 6"
	return val

def get_user_location(request):
	curr_user = request.user
	val = get_user_json(request)
	if val.location != None:
		return str(val.location.lat) + "," + str(val.location.lon)
	else:
		return None

def reset_all_users_json():
	all_entries = UserJSONObject.objects.all().delete()

def reset_user_data(request):
	print "reset_user_data 1"
	val = get_user_json(request)
	print "reset_user_data 2"
	val.delete()
	print "reset_user_data 3"

def createJSONObject(trucks):
	response = []
	for truck in trucks:
		response.append({'key': truck.key, 'name': truck.name, 'description': truck.foodType, 'location': truck.location, 'latitude': truck.position.lat, 'longitude': truck.position.lon})
	return response