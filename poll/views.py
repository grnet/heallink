from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse

from django.http import HttpResponse

from models import Journal, SubjectArea, Cart, CartItem

from forms import LoginForm

import json
import math

OFFSET = 0 
LIMIT = 200

def paginate(offset, limit, num_items, url_name, *url_args):
    num_pages = max(1, int(math.ceil(float(num_items) / limit)))
    args = url_args + (max(0, offset - 1), limit)
    previous_page = reverse(url_name, args=args)
    args = url_args + (min(offset + 1, num_pages - 1), limit)
    next_page = reverse(url_name, args=args)
    start = offset * limit
    end = start + limit
    page_urls = [reverse(url_name, args=(url_args + (page, limit)))
                 for page in range(num_pages)]
    return (start, end, previous_page, next_page, num_pages, page_urls)

@login_required
def journals(request):
    user = request.user
    user_profile = user.user_profile
    subject_area_id = user_profile.subject_area.id
    return journals_subject_area(request, subject_area_id)
    
@login_required
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
        }
    return render(request, 'poll/journals.html', context)

@login_required
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
    }
    return render(request, 'poll/search_journals.html', context)
    
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
def cart_empty(request):
    user = request.user
    user_profile = user.user_profile
    cart = user_profile.cart
    cart.empty()
    return render(request, 'poll/cart.html')
    
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
        if old_preference == 1:
            return redirect('cart')
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
        num_items = cart.cart_item__set.count()
        to_move = cart_item_set.all()[0]
        old_preference = to_move.preference
        if old_preference == num_items:
            return redirect('cart')
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
    
