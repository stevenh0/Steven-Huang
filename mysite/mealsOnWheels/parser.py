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
		ftp = FTP('webftp.vancouver.ca')
		ftp.login()
		ftp.cwd('OpenData/xls')
		filename = 'new_food_vendor_locations.xls'
		ftp.retrbinary('RETR %s' % filename, open('testThisFile.xls', 'w').write)
		ftp.quit()
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
		buff = ""
		if name == 'Placemark':
			curr_id = attrs.get(id)
	
	def characters(self, ch):
		buff = buff + ch
	
	def endElement(self, name):
		if name == 'Placemark':
			truck = FoodTruck(key=curr_id, name=curr_name, foodType=curr_description, position=curr_position)
			truck.save()
			curr_name = ""
			curr_description = ""
			curr_position = Position(lat=0,lon=0)
			curr_id = 0
			buff = ""
		elif name == 'name':
			curr_name = buff
		elif name == 'description':
			curr_description = buff
		elif name == 'coordinates':
			coords = buff.split(sep=",")
			curr_position = Position(lat=float(coords[0]), lon=float(coords[1]))
			curr_position.save()
		buff = ""

def importKMZData():
	try:
		filedst = open('testThisFile.kmz', 'w')
		req = urllib2.Request("http://data.vancouver.ca/download/kml/food_vendor_pilot.kmz")
		filesrc = urllib2.urlopen(req)
		shutil.copyfileobj(filesrc, filedst)
		filedst.close()
		filesrc.close()
		
		with open('testThisFile.kmz', 'rb') as MyZip:
			print "ANYA HERE ARE THE FUCKING MAGIC NUMBERS FUCK: " + MyZip.read(4)
			
		print "IS THIS A FUCKING ZIPFILE? " + str(is_zipfile('testThisFile.kmz'))
		
		kmz = ZipFile('testThisFile.kmz', 'r')
		kml = kmz.open('street_food_vendors.kml', 'r')
		
		# Parse like the wind!!!
		parser = make_parser()
		parser.setFeature(feature_namespaces, 0)
		dh = HandleFoodTrucks()
		parser.setContentHandler(dh)
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
	response = []
	trucks = FoodTruck.objects.all()
	for truck in trucks:
		response.append({'key': truck.key, 'name': truck.name, 'description': truck.foodType, 'latitude': truck.position.lat, 'longitude': truck.position.lon})

	with open('mealsOnWheels/templates/mealsOnWheels/food_trucks.json', 'w') as outfile:
		json.dump(response, outfile, indent=4)