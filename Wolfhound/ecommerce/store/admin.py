from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserAdminCreationForm, UserAdminChangeForm
from .models import *

admin.site.unregister(Group)  # not being used


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ['name', 'count_members']
    search_fields = ['name']

    def count_members(self, obj):
        result = Customer.objects.filter(organisation=obj).count()
        return result

    count_members.short_description = "Members"


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    fields = ['user', 'organisation']
    list_display = ['user', 'get_customer_email', 'organisation']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'organisation__name']

    @admin.display(description='Email Address', ordering='user__email')
    def get_customer_email(self, obj):
        return obj.user.email


admin.site.register(Product)


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['product', 'total_stock']
    search_fields = ['product__name']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ['customer', 'billing_address', 'shipping_address', 'order_date', 'transaction_id']
    fields = ['customer', 'billing_address', 'shipping_address', 'order_status', 'order_date', 'transaction_id']
    list_filter = ['order_status']
    list_display = ['id', 'get_customer_name', 'get_customer_email', 'order_status', 'order_date', 'transaction_id']
    search_fields = ['id', 'customer__user__last_name', 'customer__user__first_name', 'customer__user__email', 'transaction_id']

    @admin.display(description='Customer Name', ordering='customer__name')
    def get_customer_name(self, obj):
        return f'{obj.customer.user.last_name}, {obj.customer.user.first_name}'

    @admin.display(description='Customer Email', ordering='customer__email')
    def get_customer_email(self, obj):
        return obj.customer.user.email


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    readonly_fields = ['order', 'date_added']
    fields = ['order', 'product', 'quantity', 'date_added']
    list_display = ['order', 'product', 'quantity', 'date_added', 'get_total']

    @admin.display(description='Item Total', ordering='customer__name')
    def get_order_items_total(self, obj):
        return f'{obj.get_total}'


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    fields = ['order', 'address', 'city', 'county', 'eircode']
    list_display = ['order', 'address', 'city', 'county', 'eircode']


User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ['email', 'first_name', 'last_name', 'admin']
    list_filter = ['admin']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Information', {'fields': ('first_name', 'last_name',)}),
        ('Permissions', {'fields': ('admin', 'staff')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'password_2')}
         ),
    )
    search_fields = ['email']
    ordering = ['email']
    filter_horizontal = ()
