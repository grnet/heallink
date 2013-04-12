from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse

from models import Journal, SubjectArea, Cart, CartItem

from forms import LoginForm

import json

@login_required
def journals(request):
    journal_lists = []
    user = request.user
    user_profile = user.user_profile
    cart = user_profile.cart
    cart_items = cart.cart_item__set.select_related('journal').all()
    journals_in_cart = set([item.journal.issn for item in cart_items])
    subject_area_list = SubjectArea.objects.all()
    active_subject_area = user_profile.subject_area
    for sa in subject_area_list:
        journal_list = {}
        if sa.id == active_subject_area.id:
            journal_list['active'] = 'active'
        else:
            journal_list['active'] = ''
        filtered_journals = Journal.objects.filter(subject_area=sa)
        journals = filtered_journals.order_by('-downloads')[:50]
        for journal in journals:
            if journal.issn in journals_in_cart:
                journal.in_cart = True
            else:
                journal.in_cart = False
        journal_list['subject_area'] = sa.name
        journal_list['journals'] = journals
        journal_lists.append(journal_list)
    context = {
        'journal_lists': journal_lists
        }
    return render(request, 'poll/journals.html', context)
    
@login_required
def cart(request):
    user = request.user
    user_profile = user.user_profile
    cart = user_profile.cart
    cart_item_list = CartItem.objects.filter(cart=cart).order_by('preference')
    context = {
        'cart': cart,
        'cart_item_list': cart_item_list
    }
    return render(request, 'poll/cart.html', context)

@login_required
def cart_item(request):
    user = request.user
    user_profile = user.user_profile
    cart = user_profile.cart
    if not request.is_ajax():
        return redirect(journals)
    issn = json.loads(request.body)['issn']
    journal = Journal.objects.filter(issn=issn)
    if not journal.exists():
        return redirect(journals)
    if request.method == 'POST':
        number_of_items = cart.cart_item__set.count()
        if not cart.cart_item__set.filter(journal=journal).exists():
            item = CartItem(cart=cart,
                            journal=journal[0],
                            preference=number_of_items+1)
            item.save()
    elif request.method == 'DELETE':
        cart_item_set = cart.cart_item__set.filter(journal=journal)
        if cart_item_set.exists():
            old_preference = cart_item_set[0].preference
            to_update = cart.cart_item__set
            to_update = to_update.filter(preference__gt=old_preference)
            CartItem.delete_set(to_update, cart_item_set)
    return HttpResponse("OK")

@login_required
def cart_item_top(request, issn):
    user = request.user
    user_profile = user.user_profile
    cart = user_profile.cart
    journal = Journal.objects.filter(issn=issn)
    if not journal.exists():
        return redirect(cart)
    cart_item_set = cart.cart_item__set.filter(journal=journal)
    if cart_item_set.exists():
        new_top = cart_item_set.all()[0]
        old_preference = new_top.preference
        to_update = cart.cart_item__set.filter(preference__lt=old_preference)
        to_update = to_update.order_by('-preference')
        for cart_item in to_update:
            cart_item.preference = cart_item.preference + 1
            cart_item.save()
        new_top.preference = 1
        new_top.save()
    return redirect('cart')

@login_required
def cart_item_up(request, issn):
    user = request.user
    user_profile = user.user_profile
    cart = user_profile.cart
    journal = Journal.objects.filter(issn=issn)
    if not journal.exists():
        return redirect(cart)
    cart_item_set = cart.cart_item__set.filter(journal=journal)
    if cart_item_set.exists():
        to_move = cart_item_set.all()[0]
        old_preference = to_move.preference
        to_update = cart.cart_item__set.filter(preference=old_preference-1)
        for cart_item in to_update:
            cart_item.preference = cart_item.preference + 1
            cart_item.save()
        to_move.preference = old_preference - 1
        to_move.save()
    return redirect('cart')

@login_required
def cart_item_down(request, issn):
    user = request.user
    user_profile = user.user_profile
    cart = user_profile.cart
    journal = Journal.objects.filter(issn=issn)
    if not journal.exists():
        return redirect(cart)
    cart_item_set = cart.cart_item__set.filter(journal=journal)
    if cart_item_set.exists():
        to_move = cart_item_set.all()[0]
        old_preference = to_move.preference
        to_update = cart.cart_item__set.filter(preference=old_preference+1)
        for cart_item in to_update:
            cart_item.preference = cart_item.preference - 1
            cart_item.save()
        to_move.preference = old_preference + 1
        to_move.save()
    return redirect('cart')
    
@login_required
def cart_item_bottom(request, issn):
    user = request.user
    user_profile = user.user_profile
    cart = user_profile.cart
    journal = Journal.objects.filter(issn=issn)
    if not journal.exists():
        return redirect(cart)
    cart_item_set = cart.cart_item__set.filter(journal=journal)
    if cart_item_set.exists():
        num_items = cart.cart_item__set.count()
        new_bottom = cart_item_set.all()[0]
        old_preference = new_bottom.preference
        to_update = cart.cart_item__set.filter(preference__gt=old_preference)
        to_update = to_update.order_by('preference')
        for cart_item in to_update:
            cart_item.preference = cart_item.preference - 1
            cart_item.save()
        new_bottom.preference = num_items
        new_bottom.save()
    return redirect('cart')

@login_required
def cart_item_delete(request, issn):
    user = request.user
    user_profile = user.user_profile
    cart = user_profile.cart
    journal = Journal.objects.filter(issn=issn)
    if not journal.exists():
        return redirect(cart)
    cart_item_set = cart.cart_item__set.filter(journal=journal)
    if cart_item_set.exists():
        old_preference = cart_item_set[0].preference
        to_update = cart.cart_item__set.filter(preference__gt=old_preference)
        CartItem.delete_set(to_update, cart_item_set)
    return redirect('cart')
        
@login_required
def user(request):
    user = request.user
    user_profile = user.user_profile
    context = {'user': user,
               'user_profile': user_profile,
               }
    return render(request, 'poll/user.html', context)
    
def login_user(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
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
    
