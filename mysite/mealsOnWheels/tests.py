from django.test import TestCase
from django.core.urlresolvers import reverse
#from .forms import UserForm
from parser import testImportData
from models import FoodTruck, Position

# Create your tests here.

# Test that page renders properly with all the appropriate fields

# Test that only by entering the appropriate information into the fields will you be able to login

"""

class LoginViewTests(TestCase):

    def test_login_render(self):
        response = self.client.get(reverse('mealsOnWheels:register'))
        self.assertEqual(response.status_code, 200)

    def test_missing_username(self):
        params = {
               'email': 'stevenh0@hotmail.com',
               'password:': 'hello',}

        response = self.client.post(reverse('mealsOnWheels:register'), params)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "user_form","username","This field is required.")


 # TODO: email field seems not to cause an error when left blank
 #   def test_missing_email(self):
 #       params = {'username': 'steven',
 #              'password:': 'hello',}
 #       response = self.client.post(reverse('mealsOnWheels:register'), params)
 #       self.assertEqual(response.status_code, 200)
 #       self.assertFormError(response, "user_form","email","This field is required.")

    def test_missing_password(self):
        params = {'username': 'steven',
               'email': 'stevenh0@hotmail.com',}
        response = self.client.post(reverse('mealsOnWheels:register'), params)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "user_form","password","This field is required.")

# TODO: tooltip pops up on page not sure how to test
#    def test_invalid_email(self):
#        params = {'username': 'steven',
#                  'email': 'asdfasdf',
#               'password:': 'hello',}
#        response = self.client.post(reverse('mealsOnWheels:register'), params)
#        self.assertEqual(response.status_code, 200)
#        self.assertFormError(response, "user_form","email","This field is required.")



    def test_complete_form(self):
         params = {'username': 'steven',
                   'email': 'stevenh0@hotmail.com',
                   'password': 'asdf'}
         response = self.client.post(reverse('mealsOnWheels:register'), params)
         self.assertContains(response, 'You are already registered')

    def test_duplicate_user(self):
        params = {'username': 'steven',
                   'email': 'stevenh0@hotmail.com',
                   'password': 'asdf'}
        self.client.post(reverse('mealsOnWheels:register'), params)
        response = self.client.post(reverse('mealsOnWheels:register'), params)
        self.assertFormError(response, "user_form","username","A user with that username already exists.")

        """

# TODO: make duplicate emails return warning
# TODO: make blank email page return warning
# TODO: write test to see if emails are being sent properly

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

