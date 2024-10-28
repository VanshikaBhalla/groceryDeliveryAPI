async function fetchProducts() {
    try {
        const response = await fetch('/products');
        print(response.json())
        const products = await response.json();
        displayProducts(products);
    } catch (error) {
        console.error('Error fetching products:', error);
    }
}

function displayProducts(products) {
    const productList = document.querySelector('.product-list');
    productList.innerHTML = '';

    products.forEach(product => {
        const productDiv = document.createElement('div');
        productDiv.classList.add('product');
        productDiv.innerHTML = `
            <h3>${product.ProductName}</h3>
            <p>Price: $${product.Price}</p>
            <p>Rating: ${product.Rating}</p>
            <p>In Stock: ${product.InStock}</p>
            <button onclick="addToCart('{{product.ProductID}})">Add to Cart</button>
        `;
        productList.appendChild(productDiv);
    });
}

document.getElementById('clear-search').addEventListener('click', () => {
    document.getElementById('results').innerHTML = '';
    document.getElementById('search-key').value = '';
})


async function searchProducts(query) {
  const response = await fetch(`/products/search?key=${query}`);
  if (!response.ok) {
    throw new Error(`Error fetching products: ${response.statusText}`);
  }

  const data = await response.json();

  if (data.error) {
    alert(data.error);
    return [];
  }

  if (data.msg) {
    alert(data.msg);
    return [];
  }
  return data;
}

document.getElementById('search-button').addEventListener('click', () => {
  const query = document.getElementById('search-key').value;
  console.log(query);
  searchProducts(query)
    .then(products => {
      const resultsDiv = document.getElementById('results');
      resultsDiv.innerHTML = '';

      if (products.length === 0) {
        resultsDiv.textContent = 'No products found.';
      } else {
        products.forEach(product => {
          const productDiv = document.createElement('div');
          productDiv.innerHTML = `
          <div class="product">
                            <h4>${product['Product Name']}</h4>
                            <p>Price: $${product['Price']}</p>
                            <p>Rating: ${product['Rating']}</p>
                            <p>In Stock: ${product['In Stock']}</p>
                            <button onclick="addToCart('${product['Product ID']}')">Add to Cart</button>
                        </div>
          `;
          resultsDiv.appendChild(productDiv);
        });
      }
    })
    .catch(error => {
      console.error(error);
      const resultsDiv = document.getElementById('results');
      resultsDiv.textContent = 'An error occurred while searching.';
    });
});

let eg = "";
async function addToCart(productID) {
    const email = prompt('Confirm your email:');
    if (!email) {
        alert("Email confirmation is required to add items to the cart.");
        return;
    }
    const data = { email: email, product_id: productID, quantity: 1 };

    try {
        const response = await fetch('/cart/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorResult = await response.json();
            throw new Error(errorResult.error || 'Failed to add item to cart');
        } else {
            alert('Item added to cart successfully');
            eg = email;
        }
        await loadCartItems(email);

    } catch (error) {
        console.error('Error:', error);
        alert(error.message);
    }
}

async function loadCartItems(email) {
    try {
        const response = await fetch(`/cart?email=${encodeURIComponent(email)}`);
        if (!response.ok) throw new Error('Failed to load cart items');

        const cartItems = await response.json();
        document.querySelector('#cart-head').innerHTML = eg + "'s Cart"
        const cartList = document.querySelector('.cart-list');
        cartList.innerHTML = '';

        cartItems.forEach(item => {
            const cartItem = document.createElement('div');
            cartItem.classList.add('cart-item');
            cartItem.innerHTML = `
                <div class="product product-cart">
                    <h4>${item['Product Name']}</h4>
                    <p>Quantity: ${item['In cart']}</p>
                    <p>In Stock: ${item['In Stock']}</p>
                    <p>Price: $${(item['Product Price (per unit)'] * item['In cart']).toFixed(2)}</p>
                    <button type="button" class="rm-cart" data-product-id="${item['Product ID']}">Remove from Cart</button>
                </div>
            `;
            cartList.appendChild(cartItem);
        });
        addRemoveEventListeners();

    } catch (error) {
        console.error('Error loading cart items:', error);
        alert(error.message);
    }
}

function addRemoveEventListeners() {
    document.querySelectorAll('.rm-cart').forEach(button => {
        button.addEventListener('click', async function () {
            const productID = this.dataset.productId;
            const email = prompt('Confirm your email to remove the product from your cart:');
            if (!email) {
                alert("Email confirmation is required to remove items from the cart.");
                return;
            }
            if (email !== eg) {
                alert("wrong email.");
                return;
            }
            try {
                const response = await fetch(`/cart/${productID}?email=${encodeURIComponent(email)}`, {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' }
                });

                if (!response.ok) {
                    const errorResult = await response.json();
                    throw new Error(errorResult.error || 'Failed to remove item from cart');
                }

                alert('Product removed from cart successfully!');
                await loadCartItems(email);

            } catch (error) {
                console.error('Error removing from cart:', error);
                alert(error.message);
            }
        });
    });
}

document.querySelector("#checkout-btn").addEventListener("click", ()=>{
    setTimeout(() => window.location.href = "/orders/checkout", 2000);
})
fetchProducts();
