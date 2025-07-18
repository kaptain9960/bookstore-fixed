from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
	DIVISION_CHOICES = (
		('Abuja', 'Lugbe'),
		('Enugu', 'Nsukka'),
		('Nsukka', 'Peace park '),
	)

	DISCRICT_CHOICES = (
		('Abuja', 'Abuja'), 
		('Enugu', 'Enugu'),
		('Sokoto', 'Sokoto'),
		('Imo', 'Imo'),
		('Abia', 'Abia'),
	)

	PAYMENT_METHOD_CHOICES = (
		('UBA', 'UBA'),
		('Paypal','Paypal'),
		('moniepoint', 'Moniepoint'),
		('cash on delivery', 'Cash on Delivery'),
		
	)

	division = forms.ChoiceField(choices=DIVISION_CHOICES)
	district =  forms.ChoiceField(choices=DISCRICT_CHOICES)
	payment_method = forms.ChoiceField(choices=PAYMENT_METHOD_CHOICES, widget=forms.RadioSelect())

	class Meta:
		model = Order
		fields = ['name', 'email', 'phone', 'address', 'division', 'district', 'zip_code', 'payment_method', 'account_no', 'transaction_id']
