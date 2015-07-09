from ftplib import FTP
import xlrd
from models import FoodTruck, Position
import os
from xlrd import empty_cell
import json
from json import dumps
import time
from zipfile import ZipFile, is_zipfile
import xml.sax, xml.sax.handler
from xml.sax import saxutils, make_parser
from xml.sax.handler import feature_namespaces
import traceback
import urllib2
import shutil


# Import data from City of Vancouver website using FTP module

def importData():
	try:
		filedst = open('testThisFile.xls', 'w')
		req = urllib2.Request("ftp://webftp.vancouver.ca/OpenData/xls/new_food_vendor_locations.xls")
		filesrc = urllib2.urlopen(req)
		shutil.copyfileobj(filesrc, filedst)
		filedst.close()
		filesrc.close()
		workbook = xlrd.open_workbook('testThisFile.xls')
	except:
		print "mealsOnWheels :: .xls file from server cannot be read. Trying KML File.."
		if not importKMZData():
			return
		workbook = xlrd.open_workbook('localfoodtruckfile.xls')

	worksheet = workbook.sheet_by_name('Query_vendor_food')

	# Initialize counters for parsing through file

	num_rows = worksheet.nrows - 1
	num_cols = worksheet.ncols - 1
	curr_row = 0

	# Parse through file and save to database

	while curr_row < num_rows:
		curr_row += 1
		saveRowAsTruck(worksheet, curr_row)



class HandleFoodTrucks(xml.sax.handler.ContentHandler):
	curr_name = ""
	curr_description = ""
	curr_position = Position(lat=0,lon=0)
	curr_id = 0
	buff = ""
		
	def startElement(self, name, attrs):
		self.buff = ""
		if name == 'Placemark':
			self.curr_id = attrs.get("id")
	
	def characters(self, ch):
		self.buff = self.buff + ch ## YK
	
	def endElement(self, name):
		if name == 'Placemark':
			truck = FoodTruck(key=self.curr_id, name=self.curr_name, foodType=self.curr_description, position=self.curr_position)
			truck.save()
			print "saved: "+ str(truck);
			self.curr_name = ""
			self.curr_description = ""
			self.curr_position = Position(lat=0,lon=0)
			self.curr_id = 0
			self.buff = ""
		elif name == 'name':
			self.curr_name = self.buff
		elif name == 'description':
			self.curr_description = self.buff
		elif name == 'coordinates':
			coords = self.buff.split(",")
			print "float(coords[0])" + str(coords[0]) + "float(coords[1])" + str(coords[1])
			self.curr_position = Position(lat=float(coords[1]), lon=float(coords[0]))
			self.curr_position.save()
		self.buff = ""

def importKMZData():
	try:
		filedst = open('testThisFile.kmz', 'w')
		print "importKMZData()pass1"
		req = urllib2.Request("http://data.vancouver.ca/download/kml/food_vendor_pilot.kmz")
		print "importKMZData()pass2"
		filesrc = urllib2.urlopen(req)
		print "importKMZData()pass3"
		shutil.copyfileobj(filesrc, filedst)
		print "importKMZData()pass4"
		filedst.close()
		filesrc.close()
		
		with open('testThisFile.kmz', 'rb') as MyZip:
			print "ANYA HERE ARE THE FUCKING MAGIC NUMBERS FUCK: " + MyZip.read(4)
			
		print "IS THIS A FUCKING ZIPFILE? " + str(is_zipfile('testThisFile.kmz'))
		
		kmz = ZipFile('testThisFile.kmz', 'r')
		print "Zipped!"
		kml = kmz.open('street_food_vendors.kml', 'r')
		print "opened!"
		# Parse like the wind!!!
		parser = make_parser()
		print "parsed!"
		parser.setFeature(feature_namespaces, 0)
		print "feature namespace!"
		dh = HandleFoodTrucks()
		print "HandleFoodTrucks()"
		parser.setContentHandler(dh)
		print "parser.setContentHandler(dh)"
		parser.parse(kml)
		return 0
	except:
		print "mealsOnWheels :: KML file could not be read. Switching to local file."
		traceback.print_exc()
		return 1

# This method imports test data instead for testing purposes

def testImportData():
	workbook = xlrd.open_workbook('testXLSfile.xls')
	worksheet = workbook.sheet_by_name('test_sheet')

	num_rows = worksheet.nrows - 1
	num_cols = worksheet.ncols - 1
	curr_row = 0

	# Parse through file and save to database

	while curr_row < num_rows:
		curr_row += 1
		saveRowAsTruck(worksheet, curr_row)

# Where the actual data saving is done
# TODO: implement else case: figure out what functionality we want when an invalid truck is passed in, probably just does nothing but could throw exception/print to console etc.

def saveRowAsTruck(worksheet, row_index):
	if (isValidTruck(worksheet, row_index)):
		flat = worksheet.cell_value(row_index, 6)
		flon = worksheet.cell_value(row_index, 7)
		p = Position(lat=float(flat), lon=float(flon))
		p.save()

		if (worksheet.cell_type(row_index, 3) is not 1):
			fname = "Food Cart"
		else:
			fname = worksheet.cell_value(row_index, 3)

		if (worksheet.cell_type(row_index, 5) is not 1):
			fdescription = "Mystery Food"
		else:
			fdescription = worksheet.cell_value(row_index, 5)

		fkey = worksheet.cell_value(row_index, 0)
		t = FoodTruck(key=fkey, name=fname, foodType=fdescription, position=p)
		t.save()

# TODO: Only provides partial functionality, need to finish implementing
# This method should accept trucks with empty names or descriptions, but they must have one of the two, as well as a key and valid position

def isValidTruck(worksheet, row_index):
	if (worksheet.cell_type(row_index, 0) is not 1):
		return False
	if (worksheet.cell_type(row_index, 6) is not 2):
		return False
	if (worksheet.cell_type(row_index, 7) is not 2):
		return False
	if ((worksheet.cell_type(row_index, 3) is not 1) and (worksheet.cell_type(row_index, 5) is not 1)):
		return False
	return True

# The purpose of this is to clear all old data before importing new set

def clearData():
	trucks = FoodTruck.objects.all()
	trucks.delete()
	positions = Position.objects.all()
	positions.delete()

# this method takes all the database data and writes it to the JSON file

def updateJSONObject():
	trucks = FoodTruck.objects.all()
	createJSONObject(trucks)
	with open('mealsOnWheels/templates/mealsOnWheels/food_trucks.json', 'w') as outfile:
		json.dump(createJSONObject(trucks), outfile, indent=4)

def createJSONObject(trucks):
	response = []
	for truck in trucks:
		response.append({'key': truck.key, 'name': truck.name, 'description': truck.foodType, 'latitude': truck.position.lat, 'longitude': truck.position.lon})
	return response
	