var updateButtons = document.getElementsByClassName('update-cart')


for (var i = 0; i < updateButtons.length; i++) {
    updateButtons[i].addEventListener('click', function(){
        var productID = this.dataset.product
        var action = this.dataset.action
        console.log('productID: ', productID, 'action: ', action)

        console.log('User: ', user)
        if (user === 'AnonymousUser') {
            console.log('Not Authenticated')
        } else {
            updateUserOrder(productID, action)
        }
    })
}


function updateUserOrder(productID, action) {
    console.log('Authenticated')

    var url = '/update_item/'

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({'productID': productID, 'action': action})
    })

    .then((response) => {
        return response.json()
    })

    .then((data) => {
        console.log('Data:', data)
        location.reload()
    })
}