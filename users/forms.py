from django import forms

from .models import WaitingList


class WaitingListForm(forms.ModelForm):
    class Meta:
        model = WaitingList
        fields = ["email", "first_name", "last_name", "company", "company_size", "use_case"]
        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "class": "mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-white shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50",
                    "placeholder": "your.email@company.com",
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-white shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50",
                    "placeholder": "John",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-white shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50",
                    "placeholder": "Doe",
                }
            ),
            "company": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-white shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50",
                    "placeholder": "Your Company (optional)",
                }
            ),
            "company_size": forms.Select(
                attrs={
                    "class": "mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-white shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50",
                }
            ),
            "use_case": forms.Textarea(
                attrs={
                    "class": "mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-white shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50",
                    "rows": 4,
                    "placeholder": "Tell us about your use case for financial data (optional)",
                }
            ),
        }
        labels = {
            "email": "Email Address",
            "first_name": "First Name",
            "last_name": "Last Name",
            "company": "Company",
            "company_size": "Company Size",
            "use_case": "How will you use our API?",
        }
