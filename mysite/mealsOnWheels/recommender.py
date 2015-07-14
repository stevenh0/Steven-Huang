__author__ = 'yumikondo'


import numpy as np
## from sklearn.cluster import MiniBatchKMeans, KMeans
from scipy.cluster.vq import kmeans2
from mealsOnWheels.models import FoodTruck
from django.contrib.auth.models import User
import datetime


## TODO: What if there are lots of NAs?

## create array Nuser by NfoodTruck containing rates so that the dat will be
## used in Kmeans input. foodTruckArray() requires a few second to run.
## K-means should not be run all the time!

## Assume that FoodTruck is there
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
    ## which observation has all nan?
    allnan = np.all(np.isnan(dat),axis=1)


    return {"dat": dat,
            "dat_foodkey" : dat_foodkey,
            "dat_username" : dat_username,
            "pub_date" : datetime.datetime.today()}


def runKmeans(K):
    n_init = 100
    fta = foodTruckArray()
    dat = fta["dat"]
    dat_foodkey = fta["dat_foodkey"]
    np.savetxt("recommender_meanRate.txt",np.nanmean(dat, axis=0),delimiter=",")
    ##k_means = KMeans(init='k-means++', n_clusters=K, n_init=n_init)
    ##k_means.fit(dat)
    ## centers = k_means.cluster_centers_
    centers, label = kmeans2(dat, k=K, iter=n_init, thresh=1e-05, minit='random', missing='warn')
    ## cluster assignment


    np.savetxt("recommender_centers.txt", centers, delimiter=",")
    np.savetxt("recommender_foodkey.txt", dat_foodkey,  delimiter=",",fmt="%s")


def vendorToRecommend(iclust):
    centers = np.loadtxt("recommender_centers.txt",delimiter=',')
    dat_foodkey = np.loadtxt("recommender_foodkey.txt",delimiter=',',dtype=np.str)
    if iclust == -1:
        ## no cluster specification choose the vendor that has the highest avaerage rate
        meanRate = np.loadtxt("recommender_meanRate.txt",delimiter=",")
        center_i = meanRate
    else:
        center_i = centers[iclust]
    bestVendori = np.argmax(center_i)
    bestVendorKey = dat_foodkey[bestVendori]
    bestVendorAveRate = center_i[bestVendori]

    foodtruck = FoodTruck.objects.get(key=bestVendorKey)

    return {"name":foodtruck.name,
            "location":foodtruck.location,
            "key":foodtruck.key,
            "aveRate" : bestVendorAveRate}


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
        if myReviews.count()>0:
            for myReview in myReviews:
                ## food truck key of my review
                ifood = dat_foodkey.index(myReview.foodtruck.key)
                for ik in range(0,K):
                    dist_each_term[ik] += (centers[ik,ifood] - myReview.rate)**2
            myClust = dist_each_term.argmin()
        else:
            message =  "You haven't rated any vendor yet. Rate vendors then we can give better recommendations!"
            myClust = -1
            for ik in range(0,K):
                dist_each_term[ik] = -1
    except:
        message = "Admin error: perform clustering algorithm"
        myClust = -1
        for ik in range(0,K):
            dist_each_term[ik] = -1

    print message
    return {"cluster" : myClust, "dist_each_term" : dist_each_term,"message":message}


