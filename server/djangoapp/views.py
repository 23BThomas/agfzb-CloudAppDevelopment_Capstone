from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .models import CarModel
# from .restapis import related methods
from .restapis import get_dealers_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.
# Create an `about` view to render a static about page
# def about(request):
# ...
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)

# Create a `contact` view to return a static contact page
#def contact(request):
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)
# Create a `login_request` view to handle sign in request
# def login_request(request):
# ...
def login_request(request):
    context = {}
    if request.method == "POST":
        # pull from dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # check auth
        user = authenticate(username=username, password=password) 
        if user is not None:
            # login if valid
            login(request, user)
            return render(request, 'djangoapp/index.html', context)
        else:
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)
# Create a `logout_request` view to handle sign out request
# def logout_request(request):
# ...
def logout_request(request):
    context = {}
    # get user from session id
    print("Log out the user `{}`".format(request.user.username))
    logout(request)
    # redirect back to the index.html
    return render(request, 'djangoapp/index.html', context)

# Create a `registration_request` view to handle sign up request
# def registration_request(request):
# ...
def registration_request(request):
    context = {}
    # rend if it is a GET req
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # get user info
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is new user".format(username))
        if not user_exist:
            # create new user
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password)
            login(request, user)
            return render(request, 'djangoapp/index.html', context)
        else:
            return render(request, 'djangoapp/index.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        context = {}
        url = "https://bettysamthom-3000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        dealerships = get_dealers_from_cf(url)
        context["dealership_list"] = dealerships
       
        return render(request, 'djangoapp/index.html',context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    if(request.method == "GET"):
        context = {}
        dealer_url = "https://bettysamthom-3000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        reviews_url = "https://bettysamthom-5000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/get_reviews"
        dealerships = get_dealers_from_cf(dealer_url, id =dealer_id)
        context['dealership'] = dealerships[0]
        dealership_reviews = get_dealer_reviews_from_cf(reviews_url, id=dealer_id)
        context['review_list'] = dealership_reviews
        return render(request, 'djangoapp/dealer_details.html', context)


                      
# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request, dealer_id):
    if(request.method == "GET"):
        context = {}
        dealer_url = "https://bettysmthom-3000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        dealerships = get_dealers_from_cf(dealer_url, id=dealer_id)
        car_models = CarModel.objects.filter(dealer_id=dealer_id)
        context['cars'] = car_models
        context['dealership'] = dealerships[0]
        context['dealer_id'] = dealer_id
        return render(request, 'djangoapp/add_review.html', context)
    elif(request.method=="POST"):
        if(request.user.is_authenticated):
            url = "https://bettysamthom-5000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/post_review"
            review = dict()
            review["id"] = 1
            review["dealership"] = dealer_id
            review["name"] = request.POST.get('content')
            review["review"] = request.POST.get('content')
            review["purchase"] = request.POST.get('purchasecheck') == "on"
            review["purchase_date"] = request.POST.get('purchasedate')
            car_models = CarModel.objects.filter(id=request.POST.get('car'))
            car_model = car_models[0]
            review["car_make"] = car_model.make.name
            review["car_model"] = car_model.name
            review["car_year"] = str(car_model.year)[0:4]
            print(review)
            response = post_request(url, review, dealerId = dealer_id)
            print(response)
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)

