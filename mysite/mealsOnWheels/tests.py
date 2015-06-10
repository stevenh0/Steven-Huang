from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core import mail
#from .forms import UserForm
from parser import testImportData, clearData
from models import FoodTruck, Position

# Create your tests here.

# Test that page renders properly with all the appropriate fields

# Test that only by entering the appropriate information into the fields will you be able to login



class RegisterViewTests(TestCase):

    def test_login_render(self):
        response = self.client.get(reverse('mealsOnWheels:register'))
        self.assertEqual(response.status_code, 200)

    def test_missing_username(self):
        params = {
               'email': 'stevenh0@hotmail.com',
               'password1': 'hello',
               'password2': 'hello'}

        response = self.client.post(reverse('mealsOnWheels:register'), params)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form","username","This field is required.")



    def test_missing_email(self):
        params = {'username': 'steven',
               'password1': 'hello',
               'password2': 'hello'}
        response = self.client.post(reverse('mealsOnWheels:register'), params)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form","email","This field is required.")

    def test_missing_password(self):
        params = {'username': 'steven',
               'email': 'stevenh0@hotmail.com',
               'password2:': 'hello'}
        response = self.client.post(reverse('mealsOnWheels:register'), params)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form","password1","This field is required.")


    def test_invalid_email(self):
        params = {'username': 'steven',
                  'email': 'asdfasdf',
               'password1': 'hello',
               'password2': 'hello'}
        response = self.client.post(reverse('mealsOnWheels:register'), params)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form","email","Enter a valid email address.")



    def test_complete_form(self):
         response1 = self.client.get(reverse('mealsOnWheels:register'))
         self.assertContains(response1, 'Create a new account')
         params = {'username': 'steven',
                   'email': 'stevenh0@hotmail.com',
                   'password1': 'asdf',
                   'password2': 'asdf'}
         self.assertEqual(len(mail.outbox), 0)
         response2 = self.client.post(reverse('mealsOnWheels:register'), params)
         self.assertContains(response2, 'To complete the registration')

         # all emails sent are redirected to dummy outbox, if outbox contains an email, confirmation was sent

         self.assertEqual(len(mail.outbox), 1)

    def test_duplicate_user(self):
        params1 = {'username': 'steven',
                   'email': 'stevenh0@hotmail.com',
                   'password1': 'asdf',
                   'password2': 'asdf'}
        params2 = {'username': 'steven',
                   'email': 'stevenh1@hotmail.com',
                   'password1': 'asdf',
                   'password2': 'asdf'}
        self.client.post(reverse('mealsOnWheels:register'), params1)
        response = self.client.post(reverse('mealsOnWheels:register'), params2)
        self.assertFormError(response, "form","username","A user with that username already exists.")


    def test_duplicate_email(self):
        params1 = {'username': 'steven1',
                   'email': 'stevenh0@hotmail.com',
                   'password1': 'asdf',
                   'password2': 'asdf'}
        params2 = {'username': 'steven2',
                   'email': 'stevenh0@hotmail.com',
                   'password1': 'asdf',
                   'password2': 'asdf'}
        self.client.post(reverse('mealsOnWheels:register'), params1)
        response = self.client.post(reverse('mealsOnWheels:register'), params2)
        self.assertFormError(response, "form","email","duplicate email")



# TODO: rewrite test for complete form so that it doesn't check redirect based on text on page

# -------- Login View Tests -----------

class LoginViewTests(TestCase):

    def test_invalid_login(self):
        params = {'username':'',
                  'password':''}
        response = self.client.post(reverse('mealsOnWheels:login'), params)
        self.assertContains(response, 'Invalid username or password')

"""
    def test_login(self):
        params = {'username': 'steven',
                   'email': 'stevenh0@hotmail.com',
                   'password1': 'asdf',
                   'password2': 'asdf'}
        self.client.post(reverse('mealsOnWheels:register'), params)
 """

        
# TODO: Test login works. Issue: how to mimic email confirmation?
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



