__author__ = 'yumikondo'

## recommender.py

import numpy as np
from sklearn.cluster import MiniBatchKMeans, KMeans
from mealsOnWheels.models import FoodTruck
from django.contrib.auth.models import User
import datetime

K = 4
n_init = 100
k_means = KMeans(init='k-means++', n_clusters=K, n_init=n_init)

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



fta = foodTruckArray()
dat = fta["dat"]
dat_foodkey = fta["dat_foodkey"]

k_means.fit(dat)
## cluster assignment
label = k_means.labels_
centers = k_means.cluster_centers_

user = User.objects.get(username="user_aian_1")
assignUser2Cluster(user,dat_foodkey,centers)

def vendorToRecommend(iclust,centers,fta):
    dat = fta["dat"]
    dat_foodkey = fta["dat_foodkey"]
    center_i = centers[iclust]
    bestVendori = np.argmax(center_i)
    bestVendorKey = dat_foodkey[bestVendori]
    bestVendorAveRate = center_i[bestVendori]
    return {"key":bestVendorKey,"aveRate" : bestVendorAveRate}


def assignUser2Cluster(user,dat_foodkey,centers):
    ## compute squared Euclidean distances between this user's review rate
    ## and the cluster centers.
    ## pick the cluster which the smallest Euclidean distance
    ## as the cluster of this user.
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
    return {"cluster" : myClust, "dist_each_term" : dist_each_term}
