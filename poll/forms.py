#!/usr/bin/python
# -*- coding: utf-8 -*-

from django import forms

from poll.models import SubjectArea

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class FirstTimeForm(forms.Form):
    subject_area = forms.ChoiceField(choices=SubjectArea.get_subject_areas())

class UserForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    username = forms.CharField()
    username.widget.attrs['readonly'] = True
    email = forms.EmailField()
    email.widget.attrs['readonly'] = True
    project = forms.CharField()
    project.widget.attrs['readonly'] = True    
    password = forms.CharField(required=False,
                               widget=forms.PasswordInput(attrs = {
                                   'placeholder': 'Κωδικός',
                               }))
    confirm_password = forms.CharField(required=False,
                                       widget=forms.PasswordInput(attrs = {
                                           'placeholder': 'Επαλήθευση Κωδικού',
                                       }))
    subject_area = forms.ChoiceField(choices=SubjectArea.get_subject_areas())
