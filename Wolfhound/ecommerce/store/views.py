from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import JsonResponse, HttpResponse
from django.db.models import F
from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
import datetime
import json

from .models import *
from .forms import UserRegisterForm, UserLoginForm


def user_register(request):
    if request.user.is_authenticated:
        return redirect('store')
    else:
        if request.method == 'POST':
            form = UserRegisterForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                Customer.objects.create(user=user, organisation=None)
                messages.success(request, 'User Registration Successful!')
                return redirect('store')
            else:
                messages.error(request, 'Error: Something Went Wrong.')
        else:
            form = UserRegisterForm()

        return render(request, 'store/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('store')
    else:
        if request.method == 'POST':
            form = UserLoginForm(data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                return redirect('store')
        else:
            form = UserLoginForm()
        return render(request, 'store/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('login')


def store(request):
    if not request.user.is_authenticated:
        # return redirect('login')
        return render(request, 'store/error.html')
        # raise PermissionDenied
    else:
        try:
            customer = request.user.customer
        except ObjectDoesNotExist:
            print("Error - Customer does not exist for this User Account.")
            return HttpResponse('Error 403 - Forbidden', status=403)

        if customer.organisation is None:
            print("Error - Customer has not been assigned an Organisation.")
            return HttpResponse('Error 403 - Forbidden', status=403)
        else:
            order, created = Order.objects.get_or_create(customer=customer, order_status='pending')

            if request.user.is_staff or request.user.is_admin:
                # management can see all products
                products = Product.objects.all()
            else:
                # customers can see only specific products
                products = Product.objects.filter(organisation=customer.organisation)

            cart_items = order.get_cart_items
            context = {'products': products, 'cart_items': cart_items}
            return render(request, 'store/store.html', context)


def get_product(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        try:
            product = Product.objects.get(pk=product_id)
        except ObjectDoesNotExist:
            print("Error - Page Not Found.")
            return HttpResponse('Error 404 - Page Not Found', status=404)

        try:
            customer = request.user.customer
        except ObjectDoesNotExist:
            print("Error - Customer does not exist for this User Account.")
            return HttpResponse('Error 403 - Forbidden', status=403)

        if customer.organisation != product.organisation:
            if not request.user.is_admin or not request.user.is_staff:
                print("Error - You do not have access to this Product.")
                return HttpResponse('Error 403 - Forbidden', status=403)

        context = {'product': product}
        return render(request, 'store/product.html', context)


def cart(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        try:
            customer = request.user.customer
        except ObjectDoesNotExist:
            print("Error - Customer does not exist for this User Account.")
            return HttpResponse('Error 403 - Forbidden', status=403)

        order, created = Order.objects.get_or_create(customer=customer, order_status='pending')
        items = order.orderitem_set.all()
        cart_items = order.get_cart_items

        context = {'items': items, 'order': order, 'cart_items': cart_items}
        return render(request, 'store/cart.html', context)


def checkout(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        try:
            customer = request.user.customer
        except ObjectDoesNotExist:
            print("Error - Customer does not exist for this User Account.")
            return HttpResponse('Error 403 - Forbidden', status=403)

        order, created = Order.objects.get_or_create(customer=customer, order_status='pending')
        items = order.orderitem_set.all()
        cart_items = order.get_cart_items

        context = {'items': items, 'order': order, 'cart_items': cart_items}
        return render(request, 'store/checkout.html', context)


def update_item(request):
    data = json.loads(request.body)
    product_id = data['productID']
    action = data['action']

    customer = request.user.customer
    product = Product.objects.get(id=product_id)
    order, created = Order.objects.get_or_create(customer=customer, order_status='pending')
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        order_item.quantity = F('quantity') + 1  # class F is used to avoid race condition in DB
    elif action == 'remove':
        order_item.quantity = F('quantity') - 1  # class F is used to avoid race condition in DB
    elif action == 'delete':
        order_item.quantity = 0

    order_item.save()
    order_item.refresh_from_db()

    if order_item.quantity <= 0:
        order_item.delete()

    return JsonResponse('Item Added', safe=False)


def process_order(request):
    data = json.loads(request.body)
    transaction_id = datetime.datetime.now().timestamp()

    if request.user.is_authenticated:
        try:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, order_status='pending')
            total = float(data['form']['total'])
            order.transaction_id = transaction_id

            if total == order.get_cart_total:
                order.order_status = 'awaiting_payment'

            order.shipping_address = ShippingAddress.objects.create(
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                county=data['shipping']['county'],
                eircode=data['shipping']['eircode'],
            )

            order.billing_address = BillingAddress.objects.create(
                address=data['billing']['address'],
                city=data['billing']['city'],
                county=data['billing']['county'],
                eircode=data['billing']['eircode'],
            )

            order.save()
        except ObjectDoesNotExist:
            print("Customer does not exist for this User Account.")
    else:
        print('User Not Logged In')

    return JsonResponse('Payment Complete', safe=False)
