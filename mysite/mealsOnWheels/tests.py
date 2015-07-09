from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core import mail
from parser import testImportData, clearData
from models import FoodTruck, Position
from django.shortcuts import render, get_object_or_404
import hashlib, datetime, random
from django.contrib.auth.models import User

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


# -------- Profile View Tests ---------

new_username = 'sarah'
new_password = 'world'

class ProfileViewTests(TestCase):

	def navigate_to_profile(self):
		new_user = User(username=username,email=email)
		new_user.set_password(password)
		new_user.save()
		self.client.login(username=username, password=password)
		response = self.client.get(reverse('mealsOnWheels:profile'), follow=True)
		self.assertEqual(response.status_code, 200)

	def test_change_username(self):
		self.navigate_to_profile()
		params = {'username': new_username,
				'password': password,
				'password_confirmation': password}
		response = self.client.post(reverse('mealsOnWheels:profile'), params)
		self.assertContains(response, 'Profile preferences have been saved.')

	def test_change_password(self):
		self.navigate_to_profile()
		params = {'username': username,
				'password': new_password,
				'password_confirmation': new_password}
		response = self.client.post(reverse('mealsOnWheels:profile'), params)
		self.assertContains(response, 'Profile preferences have been saved.')

	def test_missing_password(self):
		self.navigate_to_profile()
		params = {'username': username,
				'password': '',
				'password_confirmation': ''}
		response = self.client.post(reverse('mealsOnWheels:profile'), params)
		self.assertContains(response, 'This field is required.')

	def test_missing_username(self):
		self.navigate_to_profile()
		params = {'username': '',
				'password': new_password,
				'password_confirmation': new_password}
		response = self.client.post(reverse('mealsOnWheels:profile'), params)
		self.assertContains(response, 'This field is required.')

	def test_change_email(self):
		self.navigate_to_profile()
		params = {'username': username,
				'email': email,
				'password': password,
				'password_confirmation': password}
		response = self.client.post(reverse('mealsOnWheels:profile'), params)
		self.assertContains(response, 'Profile preferences have been saved.')

	def test_mismatched_passwords(self):
		self.navigate_to_profile()
		params = {'username': username,
				'password': password,
				'password_confirmation': new_password}
		response = self.client.post(reverse('mealsOnWheels:profile'), params)
		self.assertContains(response, 'Passwords don&#39;t match. Please try again.')


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
