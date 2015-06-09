from ftplib import FTP
import xlrd
from models import FoodTruck, Position
import os
from xlrd import empty_cell


# Import data from City of Vancouver website using FTP module

def importData():
	ftp = FTP('webftp.vancouver.ca')
	ftp.login()
	ftp.cwd('OpenData/xls')
	filename = 'new_food_vendor_locations.xls'
	ftp.retrbinary('RETR %s' % filename, open('myLovelyNewFile.xls', 'w').write)
	ftp.quit()

	# Open workbook so data can be read

	workbook = xlrd.open_workbook('myLovelyNewFile.xls')
	worksheet = workbook.sheet_by_name('Query_vendor_food')

	# Initialize counters for parsing through file

	num_rows = worksheet.nrows - 1
	num_cols = worksheet.ncols - 1
	curr_row = 0

	# Parse through file and save to database

	while curr_row < num_rows:
	    curr_row += 1
	    saveRowAsTruck(worksheet, curr_row)

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