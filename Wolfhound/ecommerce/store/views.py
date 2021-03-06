from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.forms import EmailField
from django.http import JsonResponse, HttpResponse
from django.db.models import F
from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
import datetime
import json

import stripe
from django.conf import settings

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
        return redirect('login')
    else:
        try:
            customer = request.user.customer
        except ObjectDoesNotExist:
            return render(request, 'store/error.html', {'error_code': 404, 'error_message': 'Customer Not Found.'})

        if customer.organisation is None and (not request.user.is_staff or not request.user.is_admin):
            return render(request, 'store/error.html', {'error_code': 403, 'error_message': 'Access Denied.'})
        else:
            order, created = Order.objects.get_or_create(customer=customer, order_status='pending')

            if request.user.is_staff or request.user.is_admin:
                # management can see all products
                products = Product.objects.all()
            else:
                # customers can see only specific products
                products = Product.objects.filter(organisation=customer.organisation)

            cart_items = order.get_cart_items
            context = {'products': products, 'cart_items': cart_items, 'title': 'Products'}
            return render(request, 'store/store.html', context)


def get_product(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        try:
            product = Product.objects.get(pk=product_id)
        except ObjectDoesNotExist:
            return render(request, 'store/error.html', {'error_code': 404, 'error_message': 'Product Not Found.'})

        try:
            customer = request.user.customer
        except ObjectDoesNotExist:
            return render(request, 'store/error.html', {'error_code': 404, 'error_message': 'Customer Not Found.'})

        if customer.organisation != product.organisation:
            if not request.user.is_admin or not request.user.is_staff:
                return render(request, 'store/error.html', {'error_code': 403, 'error_message': 'Access Denied.'})

        context = {'product': product}
        return render(request, 'store/product.html', context)


def cart(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        try:
            customer = request.user.customer
        except ObjectDoesNotExist:
            return render(request, 'store/error.html', {'error_code': 404, 'error_message': 'Customer Not Found.'})

        order, created = Order.objects.get_or_create(customer=customer, order_status='pending')
        items = order.orderitem_set.all()
        cart_items = order.get_cart_items

        context = {'items': items, 'order': order, 'cart_items': cart_items, 'title': 'My Shopping Cart'}
        return render(request, 'store/cart.html', context)


def checkout(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        try:
            customer = request.user.customer
        except ObjectDoesNotExist:
            return render(request, 'store/error.html', {'error_code': 404, 'error_message': 'Customer Not Found.'})
            
        order, created = Order.objects.get_or_create(customer=customer, order_status='pending')
        items = order.orderitem_set.all()

        if order.get_cart_total <= 0:
            return redirect('store')

        price = order.get_cart_total * 100
        cart_items = order.get_cart_items
        stripe.api_key = settings.STRIPE_SECRET_KEY

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': 'Your Order',
                    },
                    'unit_amount_decimal': price,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://127.0.0.1:8000/',
            cancel_url='http://127.0.0.1:8000/',
        )

        context = {'items': items,
                   'order': order,
                   'cart_items': cart_items,
                   'session_id': session.id,
                   'stripe_public_key': settings.STRIPE_PUBLIC_KEY}

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

            if total == order.get_cart_total:
                order.order_status = 'awaiting_shipment'

            order.save()
        except ObjectDoesNotExist:
            print("Customer does not exist for this User Account.")
    else:
        print('User Not Logged In')

    return JsonResponse('Payment Complete', safe=False)


def order_confirmed(request):
    template = render_to_string('store/email.html', {'name': request.user.fullname})
    
    email = EmailMessage(
        'Thank you for purchasing from Wolfhound & Elk',
        template,
        settings.EMAIL_HOST_USER,
        [request.user.email],
    )

    email.fail_silently=False
    email.send()

    return JsonResponse('Order is placed', safe=False)