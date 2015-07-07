from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core import mail
#from .forms import UserForm
from parser import testImportData, clearData
from models import FoodTruck, Position
from django.shortcuts import render, get_object_or_404
import hashlib, datetime, random

# Create your tests here.

# Test that page renders properly with all the appropriate fields

# Test that only by entering the appropriate information into the fields will you be able to login

username = 'steven'
email = 'stevenh0@hotmail.com'
password = 'hello'

class RegisterViewTests(TestCase):

    def test_login_render(self):
        response = self.client.get(reverse('mealsOnWheels:register'))
        self.assertEqual(response.status_code, 200)

    def test_missing_username(self):
        params = {
               'email': email,
               'password1': password,
               'password2': password}

        response = self.client.post(reverse('mealsOnWheels:register'), params)
        self.assertFormError(response, "form","username","This field is required.")
        self.assertContains(response, 'Create a new account')

    def test_missing_email(self):
        params = {'username': username,
               'password1': password,
               'password2': password}
        response = self.client.post(reverse('mealsOnWheels:register'), params)
        self.assertFormError(response, "form","email","This field is required.")
        self.assertContains(response, 'Create a new account')

    def test_missing_password(self):
        params = {'username': username,
               'email': email,
               'password2:': password}
        response = self.client.post(reverse('mealsOnWheels:register'), params)
        self.assertFormError(response, "form","password1","This field is required.")
        self.assertContains(response, 'Create a new account')

    def test_invalid_email(self):
        params = {'username': username,
                  'email': 'asdfasdf',
               'password1': password,
               'password2': password}
        response = self.client.post(reverse('mealsOnWheels:register'), params)
        self.assertFormError(response, "form","email","Enter a valid email address.")
        self.assertContains(response, 'Create a new account')

    def test_mismatching_passwords(self):
        params = {'username': username,
                  'email': 'asdfasdf',
               'password1': password,
               'password2': 'goodbye'}
        response = self.client.post(reverse('mealsOnWheels:register'), params)
        self.assertFormError(response, 'form', 'password2', "The two password fields didn't match.")
        self.assertContains(response, 'Create a new account')

    def test_complete_form(self):
         response1 = self.client.get(reverse('mealsOnWheels:register'))
         self.assertContains(response1, 'Create a new account')
         params = {'username': username,
                   'email': email,
                   'password1': 'asdf',
                   'password2': 'asdf'}
         self.assertEqual(len(mail.outbox), 0)
         response2 = self.client.post(reverse('mealsOnWheels:register'), params)
         # check that registration with valid form redirects you to confirmation page
         self.assertContains(response2, 'To complete the registration')
         # all emails sent are redirected to dummy outbox, if outbox contains an email, confirmation was sent
         self.assertEqual(len(mail.outbox), 1)
         """
         # check that hashing provides valid confirmation page for users when they visit it from email
         salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
         activation_key = hashlib.sha1(salt + 'stevenh0@hotmail.com').hexdigest()
         body1 = '\nhttp://127.0.0.1:8000/mealsOnWheels/confirm/%s' % (activation_key)
         response3 = self.client.get(body1)
         self.assertContains(response3, 'Congratulations!')
         """

    def test_duplicate_user(self):
        params1 = {'username': username,
                   'email': email,
                   'password1': password,
                   'password2': password}
        params2 = {'username': username,
                   'email': email,
                   'password1': password,
                   'password2': password}
        self.client.post(reverse('mealsOnWheels:register'), params1)
        response = self.client.post(reverse('mealsOnWheels:register'), params2)
        # check that registration fails
        self.assertFormError(response, "form","username","A user with that username already exists.")
        # check that we are still on the registration page
        self.assertContains(response, 'Create a new account')

    def test_duplicate_email(self):
        params1 = {'username': username + '1',
                   'email': email,
                   'password1': password,
                   'password2': password}
        params2 = {'username': username + '2',
                   'email': email,
                   'password1': password,
                   'password2': password}
        self.client.post(reverse('mealsOnWheels:register'), params1)
        response = self.client.post(reverse('mealsOnWheels:register'), params2)
        self.assertFormError(response, "form","email","duplicate email")


# TODO: tests for authentication? I think because it takes a random number you can't just hash the same
# TODO: way to get the same key

# -------- Login View Tests -----------

class LoginViewTests(TestCase):

    def setup_user(self):
        params1 = {'username': username,
                   'email': email,
                   'password1': password,
                   'password2': password}
        self.client.post(reverse('mealsOnWheels:register'), params1)

    def test_missing_username(self):
        self.setup_user()
        params = {'username': '',
                  'password': password}
        response = self.client.post(reverse('mealsOnWheels:login'), params)
        self.assertContains(response, 'Invalid username or password')

    def test_missing_password(self):
        self.setup_user()
        params = {'username': username,
                  'password': ''}
        response = self.client.post(reverse('mealsOnWheels:login'), params)
        self.assertContains(response, 'Invalid username or password')

    def test_invalid_login(self):
        self.setup_user()
        params = {'username': '',
                  'password': ''}
        response = self.client.post(reverse('mealsOnWheels:login'), params)
        self.assertContains(response, 'Invalid username or password')

    def test_invalid_username(self):
         self.setup_user()
         params = {'username': 'bob',
                  'password': password}
         response = self.client.post(reverse('mealsOnWheels:login'), params)
         self.assertContains(response, 'Invalid username or password')

    def test_invalid_password(self):
         self.setup_user()
         params = {'username': username,
                  'password':'invalid'}
         response = self.client.post(reverse('mealsOnWheels:login'), params)
         self.assertContains(response, 'Invalid username or password')

"""
    def test_login_unauth(self):
        self.setup_user()
        params = {'username': username,
                   'password': password}
        response = self.client.post(reverse('mealsOnWheels:login'), params)
        self.assertContains(response, 'Your meals on wheels account has not been activated.')
        #self.assertEqual(response['Location'], 'http://localhost:8000/mealsOnWheels/index')
"""

# TODO: response['Location'] should return url but just results in an error for me, would be better to test for url than page content but
# TODO: can't seem to get it to work
# TODO: how to test authenticated users?
# TODO: Remove Register and Login buttons from home page after logging in with a user?

# -------- Import Data Tests ---------

class ImportDataTests(TestCase):

    def setUp(self):
        testImportData()

    def testDataExistsAfterImport(self):
        self.assertFalse(FoodTruck.objects.all() == [])

    def testTrucksExistAfterImport(self):
        self.assertFalse(FoodTruck.objects.get(key="a1") is None)
        self.assertFalse(FoodTruck.objects.get(key="c3") is None)
        self.assertFalse(FoodTruck.objects.get(key="g7") is None)

    def testTruckNamesExistAfterImport(self):
        truck1 = FoodTruck.objects.get(key="a1")
        truck2 = FoodTruck.objects.get(key="c3")
        truck3 = FoodTruck.objects.get(key="g7")
        self.assertEquals(truck1.name, "Japadog")
        self.assertEquals(truck2.name, "Food Cart")
        self.assertEquals(truck3.name, "Angry Al's")

    def testInvalidTrucksAreNotAdded(self):
        self.assertEquals(FoodTruck.objects.all().count(), 6)

    def testFoodTypesExistAfterImport(self):
        self.assertEquals(FoodTruck.objects.filter(foodType="Hot Dogs").count(), 2)
        self.assertEquals(FoodTruck.objects.get(key="c3").foodType, "Fish Tacos")
        self.assertEquals(FoodTruck.objects.get(name="Angry Al's").foodType, "Mystery Food")

    def testDataGoneAfterBeingCleared(self):
        clearData()
        self.assertEquals(FoodTruck.objects.all().count(), 0)


