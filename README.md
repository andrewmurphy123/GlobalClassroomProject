# Global Classroom Project – Wolfhound & Elk

This project is an e-commerce platform for our customer from **Wolfhound & Elk** that enables them to store their product database and sell their merchandise online and allows their customers to buy items in a very simple and, most importantly, secure way, because we have also integrated **Stripe** in the payment process, so the customers should not worry about their credit card details being compromised.

We used **Django Framework** for **Python** to create Back-End for this project, **HTML, CSS, JS** and **Bootstrap** to create Front-End. Data is being stored in a relational **SQL** database. Everything was built from scratch in order to meet the requirements as closely as possible.

*Note: this is a very early version, so certain features have not been fully implemented yet and some parts might not work as expected.* 

### Authors:
* Igor Alekhnovych
* Katie Crowley
* Seeun Lee
* Andrew Murphy
* Armando Cardozo

### Requirements:
* Python (Python Virtual Environment)
* Chrome, Edge, Safari or Firefox

### Installation Guide:
1. git clone https://github.com/andrewmurphy123/GlobalClassroomProject
2. cd GlobalClassroomProject-main/Wolfhound/ecommerce
3. pip install -r requirements.txt
4. python manage.py createsuperuser
5. python manage.py runserver
6. http://localhost:8000/

To apply changes in the database design:

1. python manage.py makemigrations
2. python manage.py migrate

## Functionality Overview

### Admin Dashboard

When super-user is created, you are now able to access the admin dashboard using this path http://localhost:8000/admin/ and populate your database. We recommend to start with Organisations and Products since they are vitally important for a proper e-shop functionality.

Let's try to create a product in this tutorial. Firstly, click on the name of a table that you are interested in and it will take you to a new screen.

<img width="640" alt="image" src="https://user-images.githubusercontent.com/59791908/165890519-9e44cd2b-fcde-4fc2-929b-d76453737a1e.png">

 Next, you should click on the *ADD PRODUCT* button on the right. Then you can fill in the form with various details about your product.

<img width="1084" alt="image" src="https://user-images.githubusercontent.com/59791908/165890904-2949a6ac-a96d-4ce2-8978-ac031f3db009.png">

In case you do not have an organisation or a size for this product, do not worry, you do not have to go back and create them elsewhere. You can create them just right now. Click on the green plus to the right from the respective field. Once you are finished, they will be stored in the database and you can use them later. When you are ready, just click on one of the *SAVE* buttons at the very bottom of the current page.

![image](https://user-images.githubusercontent.com/59791908/165891095-8be2be16-2f58-4f79-87d1-c5a52f127522.png)
<img width="1360" alt="image" src="https://user-images.githubusercontent.com/59791908/165892316-39d77263-0e6d-41b3-9876-d47e995f4a31.png">

Now you have a new product in your database. This is the overview of all the items that belong to the product table. To make your life easier, we have implemented certain helpful features. For example, if you click on a header of a column, you will be able to order it by this attribute. To the right, there is a list of filters that you can apply. Some tables also have a search bar, for example to search by name or email address.

If you click on the name of a chosen product, you will be able to see and edit all the details about this product, as well as simply delete it from your database. But we do not reccomend deleting products that have been ordered, because you might want to keep them for the order history and other records. If you do not want to show it for the customers, uncheck the availability checkbox.

![image](https://user-images.githubusercontent.com/59791908/165892573-7c50dc98-a24c-4023-ab08-36841b8d343a.png)

