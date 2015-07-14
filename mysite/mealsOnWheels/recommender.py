__author__ = 'yumikondo'


import numpy as np
from sklearn.cluster import MiniBatchKMeans, KMeans
from mealsOnWheels.models import FoodTruck
from django.contrib.auth.models import User
import datetime


## TODO: What if there are lots of NAs?

## create array Nuser by NfoodTruck containing rates so that the dat will be
## used in Kmeans input. foodTruckArray() requires a few second to run.
## K-means should not be run all the time!
def foodTruckArray():
    foods = FoodTruck.objects.all()
    users = User.objects.all()
    Npat = users.count()
    NFoodTruck = foods.count()
    dat = np.ndarray(shape=(Npat,NFoodTruck))
    iuser = 0
    dat_foodkey = []
    dat_username = []
    for user in users:
        dat_username.append(user.username)
        myReviews = user.review_set.all()
        ifood = 0
        for food in foods:
            if iuser == 0:
                 dat_foodkey.append(food.key)
            myFilterReview = myReviews.filter(foodtruck=food)
            ##print myFilterReview.count()
            if myFilterReview.count() == 1:
                dat[iuser][ifood] = myFilterReview[0].rate
            ifood+=1
        iuser+=1
    return {"dat": dat,
            "dat_foodkey" : dat_foodkey,
            "dat_username" : dat_username,
            "pub_date" : datetime.datetime.today()}


def runKmeans(K):
    n_init = 100
    fta = foodTruckArray()
    dat = fta["dat"]
    dat_foodkey = fta["dat_foodkey"]
    np.savetxt("recommender_meanRate.txt",np.mean(dat, axis=0),delimiter=",")
    k_means = KMeans(init='k-means++', n_clusters=K, n_init=n_init)
    k_means.fit(dat)
    ## cluster assignment
    centers = k_means.cluster_centers_

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
            myClust = -1
            for ik in range(0,K):
                dist_each_term[ik] = -1
    except:
        myClust = -1
        for ik in range(0,K):
            dist_each_term[ik] = -1

    return {"cluster" : myClust, "dist_each_term" : dist_each_term}


