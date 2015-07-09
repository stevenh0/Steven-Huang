from models import FoodTruck, Position, UserJSONObject
import numpy as np
from django.contrib.auth.models import User

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
	response = "["
	for truck in trucks:
		response += "{'key': " + truck.key + ", 'name': " +truck.name + ", 'description': " + truck.foodType + ", 'latitude': " + str(truck.position.lat) + ", 'longitude': " + str(truck.position.lon) + "}"
	response += "]"
	return response

def get_user_json(request):
	curr_user = request.user
	try:
		val = UserJSONObject.objects.get(user=curr_user)
	except UserJSONObject.DoesNotExist:
		val	= UserJSONObject(json_object=createJSONString(FoodTruck.objects.all()), user=curr_user)
		val.save()
	return val