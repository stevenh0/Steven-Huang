## This code assumes that all the food vendors
## python manage.py shell

from django.contrib.auth.models import User
import datetime
import xlrd
import numpy as np
from mealsOnWheels.parser import importData, clearData
from mealsOnWheels.models import FoodTruck, Review
from collections import Counter
from random import randint

## maximum rate
maxRate = 10
## the number of users to generate
Nuser = 100


## create FoodTruck objects
clearData()
importData()
User.objects.all().delete()
print "no user?" + str(User.objects.all().count()) == 0


workbook = xlrd.open_workbook('testThisFile.xls')
worksheet = workbook.sheet_by_name('Query_vendor_food')
Nvendor = worksheet.nrows

fname = []
fdescription = []
fkey = []
for row_index in range(0,Nvendor):
    fname.append( worksheet.cell_value(row_index, 3) )
    fdescription.append( worksheet.cell_value(row_index, 5) )
    fkey.append( worksheet.cell_value(row_index, 0))


## classify the vendors into 4 clusters:
keywordSet = [
    ["thai","india","japa","asia","chine","korea","vietna"],  ## Asia
    ["dogs"], ## hot dogs
    ["sea","pacific","mediter"]  ## sea food
    ] ## other

Nclust = len(keywordSet) + 1

def isCluster(fnamei,fdesci,keywords):
    for keyword in keywords:
        ## "thaifood".find("thai") == 0
        if fnamei.find(keyword)!=-1:
            return True
        if fdesci.find(keyword)!=-1:
            return True
    return False

def classify(fnamei,fdesci,keywordSet):
    fnamei=fnamei.lower()
    fdesci=fdesci.lower()
    print "fnamei:"+fnamei+" fdesci:"+fdesci
    Nclust = len(keywordSet) + 1
    for iclust in range(0,len(keywordSet)):
        if isCluster(fnamei,fdesci,keywordSet[iclust]):
            return iclust
    return Nclust-1

clusterFood = []
for ivendor in range(0,len(fname)):
    fnamei = fname[ivendor]
    fdesci = fdescription[ivendor]
    label = classify(fnamei,fdesci,keywordSet)
    print label
    clusterFood.append(label)




freqs = Counter(clusterFood)
print freqs

## probRate[i,j] * 10 represents the mean rate of the
## the vendors in cluster j by the
## users who like vendors in cluster i
probRate = [[0.9,0.3,0.2,0.1], ## Asia cluster
            [0.1,1.0,0.1,0.1], ## hot dogs
            [0.0,0.0,0.8,0.3], ## sea food
            [0.3,0.3,0.3,0.3]  ## others
            ]


def assignUserToCluster(iuser,Nuser,Nclust):
    NuserInClust = Nuser/Nclust
    for iclust in range(0,Nclust):
        if iuser < (iclust+1)*NuserInClust:
            return iclust

def randomRate(p,maxRate):
    return np.random.binomial(maxRate, p, 1)[0]


def randomDay():
    return datetime.timedelta(days=randint(0,30))

np.random.seed(0)
User.objects.all().delete()
for iuser in range(0,Nuser):
    iusercluster = assignUserToCluster(iuser,Nuser,Nclust)
    user = User(username="user" + str(iuser))
    user.set_password("user" + str(iuser))
    user.save()
    for food in FoodTruck.objects.all():
        ifoodcluster = clusterFood[fkey.index(food.key)]
        p = probRate[iusercluster][ifoodcluster]
        rate = randomRate(p,maxRate)
        pub_date=datetime.datetime.today() - randomDay()
        r = Review(foodtruck=food,rate=rate,user=user, pub_date=pub_date)
        print "iuser" + str(iuser) + " iusercluster:" + str(iusercluster) + " ifoodcluster:" + str(ifoodcluster) + " rate:"+ str(rate) + "foodname:"+str(food.name)
        r.save()


