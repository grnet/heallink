from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test

from django.contrib.auth.hashers import make_password

from django.core.urlresolvers import reverse

from django.http import HttpResponse

from models import Journal, SubjectArea, Cart, CartItem

from forms import LoginForm, FirstTimeForm, UserForm

import json
import math

OFFSET = 0 
LIMIT = 200


def not_first_time(user):
    user_profile = user.user_profile
    return not user_profile.first_time

def paginate(offset, limit, num_items, url_name, *url_args):
    num_pages = int(math.ceil(float(num_items) / limit))
    if num_pages == 0:
        num_pages = 1
    args = url_args + (max(0, offset - 1), limit)
    previous_page = reverse(url_name, args=args)
    args = url_args + (min(offset + 1, num_pages - 1), limit)
    next_page = reverse(url_name, args=args)
    start = offset * limit
    end = start + limit
    page_urls = [reverse(url_name, args=(url_args + (page, limit)))
                 for page in range(num_pages)]
    return (start, end, previous_page, next_page, num_pages, page_urls)

@login_required(login_url='login')
@user_passes_test(not_first_time, login_url='first_time')
def journals(request):
    user = request.user
    user_profile = user.user_profile
    subject_area_id = user_profile.subject_area.id
    return journals_subject_area(request, subject_area_id)
    
@login_required(login_url='login')
@user_passes_test(not_first_time, login_url='first_time')
def journals_subject_area(request, subject_area_id, offset=None, limit=None):
    user = request.user
    user_profile = user.user_profile
    subject_areas = SubjectArea.objects.order_by('ordering').all()
    subject_area = SubjectArea.objects.get(pk=subject_area_id)
    filtered_journals = Journal.objects.filter(subject_area=subject_area)
    num_journals = filtered_journals.count()
    ordered_journals = filtered_journals.order_by('-downloads')
    if offset is None:
        offset = OFFSET
    else:
        offset = int(offset)
    if limit is None:
        limit = LIMIT
    else:
        limit = int(limit)
    paging = paginate(offset, limit, num_journals,
                      'journals_subject_area_paged', subject_area_id)
    (start, end, previous_page, next_page, num_pages, page_urls) = paging
    journals = ordered_journals[start:end]
    user_profile.mark_in_cart(journals)
    context = {
        'journal_list': journals,
        'subject_area_list': subject_areas,
        'active_subject_area': subject_area,
        'num_pages': range(num_pages),
        'page_urls': page_urls,
        'offset': offset,
        'previous_page': previous_page,
        'next_page': next_page,
        'start': start + 1,
        'end': min(end, num_journals),
        'total': num_journals,
        }
    return render(request, 'poll/journals.html', context)

@login_required(login_url='login')
@user_passes_test(not_first_time, login_url='first_time')
def search_journals(request, offset=None, limit=None):
    user = request.user
    user_profile = user.user_profile
    query = request.GET.get('q', '')
    if query == '':
        return render(request, 'poll/search_journals.html', {})
    filtered_journals = Journal.objects.filter(title__icontains=query)
    ordered_journals = filtered_journals.order_by('-downloads')
    num_journals = filtered_journals.count()
    if offset is None:
        offset = OFFSET
    else:
        offset = int(offset)
    if limit is None:
        limit = LIMIT
    else:
        limit = int(limit)
    paging = paginate(offset, limit, num_journals, 'search_journals')
    (start, end, previous_page, next_page, num_pages, page_urls) = paging
    journals = ordered_journals[start:end]
    user_profile.mark_in_cart(journals)
    context = {
        'journal_list': journals,
        'query': query,
        'num_pages': range(num_pages),
        'page_urls': page_urls,
        'offset': offset,
        'previous_page': previous_page,
        'next_page': next_page,
        'start': start + 1,
        'end': min(end, num_journals),
        'total': num_journals,
    }
    return render(request, 'poll/search_journals.html', context)
    
@login_required(login_url='login')
@user_passes_test(not_first_time, login_url='first_time')
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

@login_required(login_url='login')
@user_passes_test(not_first_time, login_url='first_time')
def cart_empty(request):
    user = request.user
    user_profile = user.user_profile
    cart = user_profile.cart
    cart.empty()
    return render(request, 'poll/cart.html')
    
@login_required(login_url='login')
@user_passes_test(not_first_time, login_url='first_time')
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
        number_of_items = cart.cart_item_set.count()
        if not cart.cart_item_set.filter(journal=journal).exists():
            item = CartItem(cart=cart,
                            journal=journal[0],
                            preference=number_of_items+1)
            item.save()
    elif request.method == 'DELETE':
        cart_item_set = cart.cart_item_set.filter(journal=journal)
        if cart_item_set.exists():
            old_preference = cart_item_set[0].preference
            to_update = cart.cart_item_set
            to_update = to_update.filter(preference__gt=old_preference)
            CartItem.delete_set(to_update, cart_item_set)
    return HttpResponse("OK")

@login_required(login_url='login')
@user_passes_test(not_first_time, login_url='first_time')
def cart_item_top(request, issn):
    user = request.user
    user_profile = user.user_profile
    cart = user_profile.cart
    journal = Journal.objects.filter(issn=issn)
    if not journal.exists():
        return redirect(cart)
    cart_item_set = cart.cart_item_set.filter(journal=journal)
    if cart_item_set.exists():
        new_top = cart_item_set.all()[0]
        old_preference = new_top.preference
        to_update = cart.cart_item_set.filter(preference__lt=old_preference)
        to_update = to_update.order_by('-preference')
        for cart_item in to_update:
            cart_item.preference = cart_item.preference + 1
            cart_item.save()
        new_top.preference = 1
        new_top.save()
    return redirect(cart)

@login_required(login_url='login')
@user_passes_test(not_first_time, login_url='first_time')
def cart_item_up(request, issn):
    user = request.user
    user_profile = user.user_profile
    cart = user_profile.cart
    journal = Journal.objects.filter(issn=issn)
    if not journal.exists():
        return redirect(cart)
    cart_item_set = cart.cart_item_set.filter(journal=journal)
    if cart_item_set.exists():
        to_move = cart_item_set.all()[0]
        old_preference = to_move.preference
        if old_preference == 1:
            return redirect(cart)
        to_update = cart.cart_item_set.filter(preference=old_preference-1)
        for cart_item in to_update:
            cart_item.preference = cart_item.preference + 1
            cart_item.save()
        to_move.preference = old_preference - 1
        to_move.save()
    return redirect(cart)

@login_required(login_url='login')
@user_passes_test(not_first_time, login_url='first_time')
def cart_item_down(request, issn):
    user = request.user
    user_profile = user.user_profile
    cart = user_profile.cart
    journal = Journal.objects.filter(issn=issn)
    if not journal.exists():
        return redirect(cart)
    cart_item_set = cart.cart_item_set.filter(journal=journal)
    if cart_item_set.exists():
        num_items = cart.cart_item_set.count()
        to_move = cart_item_set.all()[0]
        old_preference = to_move.preference
        if old_preference == num_items:
            return redirect(cart)
        to_update = cart.cart_item_set.filter(preference=old_preference+1)
        for cart_item in to_update:
            cart_item.preference = cart_item.preference - 1
            cart_item.save()
        to_move.preference = old_preference + 1
        to_move.save()
    return redirect(cart)
    
@login_required(login_url='login')
@user_passes_test(not_first_time, login_url='first_time')
def cart_item_bottom(request, issn):
    user = request.user
    user_profile = user.user_profile
    cart = user_profile.cart
    journal = Journal.objects.filter(issn=issn)
    if not journal.exists():
        return redirect(cart)
    cart_item_set = cart.cart_item_set.filter(journal=journal)
    if cart_item_set.exists():
        num_items = cart.cart_item_set.count()
        new_bottom = cart_item_set.all()[0]
        old_preference = new_bottom.preference
        to_update = cart.cart_item_set.filter(preference__gt=old_preference)
        to_update = to_update.order_by('preference')
        for cart_item in to_update:
            cart_item.preference = cart_item.preference - 1
            cart_item.save()
        new_bottom.preference = num_items
        new_bottom.save()
    return redirect(cart)

@login_required(login_url='login')
@user_passes_test(not_first_time, login_url='first_time')
def cart_item_delete(request, issn):
    user = request.user
    user_profile = user.user_profile
    cart = user_profile.cart
    journal = Journal.objects.filter(issn=issn)
    if not journal.exists():
        return redirect(cart)
    cart_item_set = cart.cart_item_set.filter(journal=journal)
    if cart_item_set.exists():
        old_preference = cart_item_set[0].preference
        to_update = cart.cart_item_set.filter(preference__gt=old_preference)
        CartItem.delete_set(to_update, cart_item_set)
    return redirect(cart)
        
@login_required(login_url='login')
@user_passes_test(not_first_time, login_url='first_time')
def user(request):
    user = request.user
    user_profile = user.user_profile
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            password = form.cleaned_data['password']            
            confirm_password = form.cleaned_data['confirm_password']
            subject_area_id = int(form.cleaned_data['subject_area'])
            user.first_name = first_name
            user.last_name = last_name
            user_profile.subject_area_id = subject_area_id
            if len(password) > 0 and password == confirm_password:
                user.password = make_password(password)
            user.save()
            user_profile.save()
    else:
        form = UserForm(initial = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'subject_area_id': user_profile.subject_area_id,
        })
    return render(request, 'poll/user.html', {'form': form,})
    
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
                    user_profile = user.user_profile
                    if user_profile.first_time == True:
                        return redirect(first_time)
                    else:
                        return redirect(journals)
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

@login_required(login_url='login')
def first_time(request):
    if request.method == 'POST':
        form = FirstTimeForm(request.POST)
        if form.is_valid():
            user = request.user
            if user is not None:
                subject_area_id = int(form.cleaned_data['subject_area'])
                user_profile = user.user_profile
                user_profile.initialize_cart(subject_area_id)
                return redirect(journals)
            else:
                form.non_field_errors = 'Invalid user'
        else:
            form.non_field_errors = 'Invalid Subject Area'
    else:
        form = FirstTimeForm()
    return render(request, 'poll/first_time.html', {'form': form,})

@login_required(login_url='login')
@user_passes_test(not_first_time, login_url='first_time')
def help(request):
    return render(request, 'poll/help.html')
