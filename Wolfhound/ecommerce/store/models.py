from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

User = settings.AUTH_USER_MODEL


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """ Create and Save a User with the given Email and Password. """
        if not email:
            raise ValueError('Users must have an Email Address.')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        """ Create and Save a Staff User with the given Email and Password. """
        user = self.create_user(email=email, password=password)
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """ Create and Save a Super User with the given Email and Password. """
        user = self.create_user(email=email, password=password)
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(verbose_name='Email Address', max_length=255, unique=True, null=False, blank=False)
    first_name = models.CharField(verbose_name='First Name', max_length=35, blank=False)
    last_name = models.CharField(verbose_name='Last Name', max_length=35, blank=False)
    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(verbose_name='Date Joined', default=timezone.now)

    # password field is already built-in
    # email and password are required by default

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['last_name', 'first_name']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def has_perm(self, perm, obj=None):
        """ Does the user have a specific permission? """
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """ Does the user have permissions to view the app `app_label`? """
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        """ Is the user a member of staff? """
        return self.staff

    @property
    def is_admin(self):
        """ Is the user an admin member? """
        return self.admin

    def __str__(self):
        return f'{self.last_name}, {self.first_name}'


class Organisation(models.Model):
    name = models.CharField(verbose_name='Name', max_length=100, unique=True, null=False, blank=False)

    class Meta:
        verbose_name = 'Organisation'
        verbose_name_plural = 'Organisations'
        ordering = ['name']

    def __str__(self):
        return self.name


class Customer(models.Model):
    user = models.OneToOneField(User, verbose_name='User', on_delete=models.RESTRICT, null=False, blank=False)
    organisation = models.ForeignKey(Organisation, verbose_name='Organisation', on_delete=models.RESTRICT, null=True, blank=True)

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        ordering = ['user']

    def __str__(self):
        return f'{self.user.last_name} {self.user.first_name} — ({self.user.email})'


class Size(models.Model):
    CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('unisex', 'Unisex'),
    )

    size = models.CharField(verbose_name='Size', max_length=10, null=False, blank=False)
    gender = models.CharField(verbose_name='Gender', max_length=10, default='unisex', choices=CHOICES)

    class Meta:
        verbose_name = 'Size'
        verbose_name_plural = 'Sizes'
        unique_together = ['size', 'gender']
        ordering = ['gender']

    def __str__(self):
        return f'{self.size} - {self.gender}'


class Product(models.Model):
    price = models.DecimalField(verbose_name='Price', max_digits=6, decimal_places=2, null=False, default=0, validators=[MinValueValidator(0.00)])
    name = models.CharField(verbose_name='Name', max_length=100, null=False, blank=False)
    description = models.TextField(verbose_name='Description', null=True, blank=True)
    sizes = models.ManyToManyField(Size, verbose_name='Sizes', null=True, blank=True)
    organisation = models.ForeignKey(Organisation, verbose_name='Organisation', on_delete=models.CASCADE, null=True, blank=True)
    availability = models.BooleanField(verbose_name='Availability', default=True)
    image = models.ImageField(verbose_name='Image', upload_to='photos/%Y/%m/%d/', null=True, blank=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['organisation', 'name']

    @property
    def image_url(self):
        try:
            url = self.image.url    # link to display the image from the database
        except:
            url = '/media/photos/placeholder.png'   # default placeholder if there is no image
        return url

    def __str__(self):
        return self.name


class ShippingAddress(models.Model):
    address = models.CharField(max_length=200, null=False, blank=False)
    city = models.CharField(max_length=50, null=True, blank=True)
    county = models.CharField(max_length=50, null=True, blank=True)
    eircode = models.CharField(max_length=8, null=True, blank=True)

    class Meta:
        verbose_name = 'Shipping Address'
        verbose_name_plural = 'Shipping Addresses'
        ordering = ['eircode']

    def __str__(self):
        return self.address


class BillingAddress(models.Model):
    address = models.CharField(max_length=200, null=False, blank=False)
    city = models.CharField(max_length=50, null=True, blank=True)
    county = models.CharField(max_length=50, null=True, blank=True)
    eircode = models.CharField(max_length=8, null=True, blank=True)

    class Meta:

        verbose_name = 'Billing Address'
        verbose_name_plural = 'Billing Addresses'
        ordering = ['eircode']

    def __str__(self):
        return self.address


class Order(models.Model):
    CHOICES = (
        ('pending', 'Pending'),
        ('awaiting_payment', 'Awaiting Payment'),
        ('awaiting_shipment', 'Awaiting Shipment'),
        ('shipped', 'Shipped'),
    )

    customer = models.ForeignKey(Customer, verbose_name='Customer', editable=False, on_delete=models.SET_NULL, null=True, blank=True)
    billing_address = models.OneToOneField(BillingAddress, verbose_name='Billing Address', editable=False, on_delete=models.SET_NULL, null=True, blank=True)
    shipping_address = models.OneToOneField(ShippingAddress, verbose_name='Shipping Address', editable=False, on_delete=models.SET_NULL, null=True, blank=True)
    transaction_id = models.CharField(verbose_name='Transaction ID', editable=False, max_length=100, null=True, blank=True)
    order_status = models.CharField(verbose_name='Order Status', max_length=50, null=False, blank=False, choices=CHOICES)
    order_date = models.DateTimeField(verbose_name='Order Date', auto_now_add=True, editable=False)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-id']

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

    def __str__(self):
        return str(self.id)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name='Order ID', editable=False, on_delete=models.CASCADE, null=False, blank=False)
    product = models.ForeignKey(Product, verbose_name='Product Name', on_delete=models.SET_NULL, null=True, blank=False)
    quantity = models.IntegerField(verbose_name='Quantity', null=False, default=0, validators=[MinValueValidator(0)])
    date_added = models.DateTimeField(verbose_name='Date Added', auto_now_add=True, editable=False)

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        ordering = ['order']

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

    def __str__(self):
        return str(self.id)