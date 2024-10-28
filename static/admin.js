loadDashboardData();
setInterval(() => {
    loadDashboardData();
}, 60000);

    function loadDashboardData() {
    fetch('/admin/dashboard')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      }).then(data => {
                document.getElementById("dashboard-stats").innerHTML = `
                    <p><b>Total Orders:</b> ${data.total_orders}</p>
                    <p><b>Active Users:</b> ${data.active_users}</p>
                    <p><b>Top Selling Products:</b> ${data.top_selling_products.join(', ')}</p>
                    <p><b>Average Delivery Time (Hours):</b> ${data.average_delivery_time_hours}</p>
                `;
            })
            .catch(error => {
        console.error('Error loading dashboard data:', error);
        document.getElementById("dashboard-stats").innerHTML = '<p>Failed to load dashboard data. Please try again later.</p>';
      });
    }


async function assignDeliveryPartner(orderId, deliveryEmail) {
    const url = `/orders/${orderId}/assign?email=${encodeURIComponent(deliveryEmail)}`;
    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    };

    try {
        const response = await fetch(url, options);

        if (response.ok) {
            const data = await response.json();
            document.getElementById('assignDeliveryResult').innerText = data.message;
        } else {
            const errorData = await response.json();
            document.getElementById('assignDeliveryResult').innerText = errorData.error;
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('assignDeliveryResult').innerText = 'An error occurred while assigning the delivery partner. Please try again.';
    }
}


document.getElementById('assignDeliveryForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const orderId = document.getElementById('order-id-delivery').value;
    const deliveryEmail = document.getElementById('delivery-email').value;
    assignDeliveryPartner(orderId, deliveryEmail);
});


document.getElementById('clear-assign-delivery').addEventListener('click', function() {
    document.getElementById('order-id-delivery').value = '';
    document.getElementById('delivery-email').value = '';
    document.getElementById('assignDeliveryResult').innerText = '';
});


async function cancelOrder(orderId) {
    const url = `/admin/orders/${orderId}/cancel`;
    const options = {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        }
    };

    try {
        const response = await fetch(url, options);


        if (response.ok) {
            const data = await response.json();
            document.getElementById('cancelOrderResult').innerText = data.msg;
        } else {
            const errorData = await response.json();
            document.getElementById('cancelOrderResult').innerText = errorData.error;
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('cancelOrderResult').innerText = 'An error occurred while canceling the order. Please try again.';
    }
}


document.getElementById('cancelOrderForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const orderId = document.getElementById('order-id-cancel').value;
    cancelOrder(orderId);
});


document.getElementById('clear-cancel-order').addEventListener('click', function() {
    document.getElementById('order-id-cancel').value = '';
    document.getElementById('cancelOrderResult').innerText = '';
});

async function addProduct(productData) {
    try {
        const response = await fetch('/products', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(productData)
        });

        const result = await response.json();
        if (response.ok) {
            alert(result.message);
        } else {
            alert(result.error);
        }
    } catch (error) {
        console.error('Error adding product:', error);
        alert('An error occurred while adding the product.');
    }
}

document.getElementById('addProductForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const productData = {
        pname: document.getElementById('product-name').value,
        price: document.getElementById('product-price').value,
        rating: document.getElementById('product-rating').value,
        category: document.getElementById('product-category').value,
        inStock: document.getElementById('product-count').value
    };
    addProduct(productData);
});

document.getElementById('clear-add-product').addEventListener("click", function(){
    document.getElementById("addProductForm").reset();
});

async function updateProductPrice(id, newPrice) {
    try {
        const response = await fetch(`/products/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ new_price: newPrice })
        });

        const result = await response.json();
        if (response.ok) {
            alert(result.msg);
        } else {
            alert(result.error);
        }
    } catch (error) {
        console.error('Error updating product price:', error);
        alert('An error occurred while updating the product price.');
    }
}

document.getElementById('updatePriceForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const productId = document.getElementById('product-id-price').value;
    const newPrice = document.getElementById('new-price').value;
    updateProductPrice(productId, newPrice);
});

document.getElementById('clear-update-price').addEventListener("click", function(){
    document.getElementById("updatePriceForm").reset();
});

async function updateProductCount(id, newCount) {
    try {
        const response = await fetch(`/products/count?id=${id}&new_count=${newCount}`, {
            method: 'PUT'
        });

        const result = await response.json();
        if (response.ok) {
            alert(result.msg);
        } else {
            alert(result.error);
        }
    } catch (error) {
        console.error('Error updating product count:', error);
        alert('An error occurred while updating the product count.');
    }
}

document.getElementById('updateCountForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const productId = document.getElementById('product-id-count').value;
    const newCount = document.getElementById('new-count').value;
    updateProductCount(productId, newCount);
});

document.getElementById('clear-update-count').addEventListener("click", function(){
    document.getElementById("updateCountForm").reset();
});

async function deleteProduct(id) {
    try {
        const response = await fetch(`/products/${id}`, {
            method: 'DELETE'
        });

        const result = await response.json();
        if (response.ok) {
            alert(result.msg);
        } else {
            alert(result.error);
        }
    } catch (error) {
        console.error('Error deleting product:', error);
        alert('An error occurred while deleting the product.');
    }
}

document.getElementById('deleteProductForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const productId = document.getElementById('product-id-delete').value;
    deleteProduct(productId);
});

document.getElementById('clear-delete-product').addEventListener("click", function(){
    document.getElementById("deleteProductForm").reset();
});

document.getElementById('fetchProfileForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const email = document.getElementById('user-email').value;

    try {
        const response = await fetch('/users/profile', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email })
        });

        const result = await response.json();
        const userProfileResult = document.getElementById('userProfileResult');
        userProfileResult.innerHTML = '';

        if (response.ok) {
            userProfileResult.innerHTML = `<p>Name: ${result.name}</p>
                                           <p>Email: ${result.email}</p>
                                           <p>Phone: ${result.phn}</p>
                                           <p>Role: ${result.role}</p>`;
        } else {
            userProfileResult.innerHTML = `<p>${result.error}</p>`;
        }
    } catch (error) {
        console.error('Error fetching profile:', error);
    }
});

document.getElementById('clear-fetch-profile').addEventListener('click', function(){
    document.getElementById('fetchProfileForm').reset();
    document.getElementById('userProfileResult').innerHTML = '';
});
document.getElementById('updateProfileForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const email = document.getElementById('update-email').value;
    const newPhone = document.getElementById('new-phone').value;

    try {
        const response = await fetch('/users/profile', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, new_phn: newPhone })
        });

        const result = await response.json();
        const updateProfileResult = document.getElementById('updateProfileResult');
        updateProfileResult.innerHTML = '';

        if (response.ok) {
            updateProfileResult.innerHTML = `<p>${result.msg}</p>`;
        } else {
            updateProfileResult.innerHTML = `<p>${result.error}</p>`;
        }
    } catch (error) {
        console.error('Error updating profile:', error);
    }
});

document.getElementById('clear-update-profile').addEventListener('click', function(){
    document.getElementById('updateProfileForm').reset();
});
