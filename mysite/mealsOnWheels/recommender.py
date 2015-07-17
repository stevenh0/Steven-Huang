__author__ = 'yumikondo'


import numpy as np
from mealsOnWheels.models import FoodTruck
from django.contrib.auth.models import User
import datetime, random
import scipy.cluster.hierarchy as hier
import scipy.spatial.distance as dist

propMissing = 0.4

## Create array Nuser by NfoodTruck containing rates so that the dat will be
## used in Kmeans input. foodTruckArray() requires a few second to run.
## K-means should not be run all the time!


## Assume that FoodTruck is already fetched
##missingRate = -1; ## missing value is imputed with -1
def foodTruckArray():
    foods = FoodTruck.objects.all()
    users = User.objects.all()
    Npat = users.count()
    NFoodTruck = foods.count()
    ## initial values of all entries are NaN
    dat = np.ndarray(shape=(Npat,NFoodTruck))
    dat.fill(np.nan)
    iuser = 0
    dat_foodkey = []
    dat_username = []
    for user in users:
        print "user"+str(iuser);
        dat_username.append(user.username)
        myReviews = user.review_set.all()
        ifood = 0
        for food in foods:
            if iuser == 0:
                 dat_foodkey.append(food.key)
            myFilterReview = myReviews.filter(foodtruck=food)
            ##print myFilterReview.count()
            if myFilterReview.count() == 1:
                ## print "rate"+str(myFilterReview[0].rate)
                dat[iuser][ifood] = myFilterReview[0].rate
            ifood+=1
        iuser+=1
    ## don't use the users with more than propMissing of rating missing
    userToUse = np.mean(np.isnan(dat),axis=1) < propMissing
    dat = dat[userToUse,:]
    dat_username = np.array(dat_username)[userToUse]
    return {"dat": dat,
            "dat_foodkey" : dat_foodkey,
            "dat_username" : dat_username,
            "pub_date" : datetime.datetime.today()}

def getMissDist(x,y):
    return np.nanmean( (x - y)**2 )

def getMissDistMat(dat):
    Npat = dat.shape[0]
    dist = np.ndarray(shape=(Npat,Npat))
    dist.fill(0)
    for ix in range(0,Npat):
        x = dat[ix,]
        if ix >0:
            for iy in range(0,ix):
                y = dat[iy,]
                dist[ix,iy] = getMissDist(x,y)
                dist[iy,ix] = dist[ix,iy]
    return dist

def getCenters(label,dat):
    ## compute the cluster centers
    uniLabel = np.unique(label)
    K = len(uniLabel)
    centers = np.ndarray(shape=(K,dat.shape[1]))
    for ik in range(0,K):
        k = uniLabel[ik]
        centers[ik,]=np.nanmean(dat[label==k,],axis=0)
    return centers

def runClustering():
    fta = foodTruckArray()
    dat = fta["dat"]
    dat_foodkey = fta["dat_foodkey"]
    np.savetxt("recommender_foodkey.txt", dat_foodkey,  delimiter=",",fmt="%s")
    np.savetxt("recommender_meanRate.txt",np.nanmean(dat, axis=0),delimiter=",")
    ## Hierarchical clustering
    distMat = getMissDistMat(dat)
    condensDist = dist.squareform(distMat)
    ## single, complete, weighted or average
    link = hier.linkage(condensDist, method='average')
    label = hier.fcluster(link,t=4^2,criterion='distance')
    centers = getCenters(label=label,dat=dat)
    np.savetxt("recommender_centers.txt", centers, delimiter=",")

def getBestUnratedVendor(center_i,user,dat_foodkey):
    lng = len(center_i)
    while lng >0:
        bestVendori = np.argmax(center_i)
        bestVendorKey = dat_foodkey[bestVendori]
        ft = FoodTruck.objects.get(key=bestVendorKey)
        if user.review_set.filter(foodtruck = ft).count() == 0:
            break
        keep = range(0,lng) != bestVendori
        center_i = center_i[keep]
        dat_foodkey = dat_foodkey[keep]
        lng = len(center_i)
    if lng == 0: ## there is no vendor that has not been rated
        foodtruck = getRandomVendor()
    else:
        foodtruck = FoodTruck.objects.get(key=bestVendorKey)
    return foodtruck

def getRandomVendor():
    foodtrucks = FoodTruck.objects.all()
    Ntruck = foodtrucks.count()
    bestVendori = random.randint(0,Ntruck-1)
    foodtruck = foodtrucks[bestVendori]
    return foodtruck

def vendorToRecommend(iclust,user):
    ## recommend the vendor that has high rate among the users in the same cluster
    ## and this user has not rated yet!
    try:
        centers = np.loadtxt("recommender_centers.txt",delimiter=',')
        dat_foodkey = np.loadtxt("recommender_foodkey.txt",delimiter=',',dtype=np.str)
        if iclust == -1:
            ## no cluster specification choose the vendor that has the highest avaerage rate
            center_i = np.loadtxt("recommender_meanRate.txt",delimiter=",")
        else:
            center_i = centers[iclust,:]
        foodtruck = getBestUnratedVendor(center_i,user,dat_foodkey)
        ## bestVendori = np.argmax(center_i)
        ## bestVendorKey = dat_foodkey[bestVendori]
        ## bestVendorAveRate = center_i[bestVendori]
        ## foodtruck = FoodTruck.objects.get(key=bestVendorKey)
    except:
        print "error occurs! randomly selected vendor is suggested as recommendation"
        foodtruck = getRandomVendor()

    print "name" + foodtruck.name + "location" + foodtruck.location + "key" +foodtruck.key
    return {"name":foodtruck.name,
            "location":foodtruck.location,
            "key":foodtruck.key}

def assignUser2Cluster(user):
    ## compute squared Euclidean distances between this user's review rate
    ## and the cluster centers.
    ## pick the cluster which the smallest Euclidean distance
    ## as the cluster of this user.
    message = ""
    try:
        centers = np.loadtxt("recommender_centers.txt",delimiter=',')
        dat_foodkey = np.loadtxt("recommender_foodkey.txt",delimiter=',',dtype=np.str)
        myReviews = user.review_set.all()
        K = centers.shape[0]
        dist_each_term = np.ndarray(shape=K)
        dist_each_term.fill(0)
        if myReviews.count()>0:
            print "myReviews.count" + str(myReviews.count())
            for myReview in myReviews:
                ## food truck key of my review
                ifood = np.where(dat_foodkey == myReview.foodtruck.key)[0][0]
                print "ifood" + str(ifood)
                for ik in range(0,K):
                    dist_each_term[ik] += (centers[ik,ifood] - myReview.rate)**2
            myClust = dist_each_term.argmin()
        else:
            message =  "You haven't rated any vendor yet. Rate vendors then we can give better recommendations!"
            myClust = -1
            for ik in range(0,K):
                dist_each_term[ik] = -1
    except:
        message = "Go admin and perform clustering algorithm to get better recommendation"
        myClust = -1
    print message
    return {"cluster" : myClust, "message":message}
