from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse

from models import Journal, SubjectArea, Cart, CartItem

from forms import LoginForm

@login_required
def journals(request):
    journal_lists = []
    subject_area_list = SubjectArea.objects.all()
    for sa in subject_area_list:
        filtered_journals = Journal.objects.filter(subject_area=sa)
        journals = filtered_journals.order_by('-downloads')
        journal_lists.append({'subject_area': sa.name,
                              'journals': journals})
    context = {
        'subject_area_list': subject_area_list,
        'journal_lists': journal_lists
        }
    return render(request, 'poll/journals.html', context)
    
@login_required
def cart(request):
    user = request.user
    user_profile = user.user_profile
    cart = user_profile.cart
    cart_item_list = CartItem.objects.filter(cart=cart)
    context = {
        'cart': cart,
        'cart_item_list': cart_item_list
    }
    return render(request, 'poll/cart.html', context)

@login_required
def add_remove_journal(request):
    if request.is_ajax():
        if request.method == 'POST':
            print 'Raw Data: "%s"' % request.body
    return HttpResponse("OK")

@login_required
def user(request):
    return HttpResponse("OK")
    
def login_user(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            print username, password
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('journals')
                else:
                    form.non_field_errors = 'Account disabled'
            else:
                form.non_field_errors = 'Invalid Login'
        else:
           return render(request, 'poll/login.html', {'form' : form,})
    else:
        form = LoginForm()
    return render(request, 'poll/login.html', {'form' : form,})        
        
def logout_user(request):
    logout(request)
    return redirect('login')
    
