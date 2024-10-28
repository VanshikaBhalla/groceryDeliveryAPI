document.getElementById("placeOrderForm").addEventListener("submit", function(event) {
    event.preventDefault();
    const email = document.getElementById("email").value;

    fetch(`/orders/checkout?email=${email}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("orderConfirmation").innerHTML = `
            <h3>${data.message || "Order Error"}</h3>
            <p>Order ID: ${data.OrderID || "N/A"}</p>
            <p>Total Price: $${data.TotalPrice || "N/A"}</p>
            <p>Estimated Delivery Time: ${data.EstimatedDeliveryTime || "N/A"}</p>
            <p>Delivery Partner: ${data.AssignedDeliveryPartner || "N/A"}</p>
        `;
    })
    .catch(error => console.error('Error placing order:', error));
});

document.getElementById("trackOrderForm").addEventListener("submit", (event) => {
        event.preventDefault();

        const orderId = document.getElementById("order-id").value;
            fetch(`/orders/${orderId}/track`)
            .then(response => {
                if (!response.ok) {
                    throw new Error("Order not found!");
                }
                return response.json();
            })
            .then(data => {
                document.getElementById("trackOrder").innerHTML = `
                    <p><strong>Order ID:</strong> ${data.OrderID}</p>
                    <p><strong>Status:</strong> ${data.Status}</p>
                `;
            })
            .catch(error => {
                document.getElementById("trackOrder").innerHTML = `<p>${error.message}</p>`;
            });
    });

document.getElementById("getOrderDetailsForm").addEventListener("submit", function(event) {
    event.preventDefault();
    const orderId = document.getElementById("orderId").value;
    const email = document.getElementById("detailsEmail").value;

    fetch(`/orders/${orderId}?email=${email}`)
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById("orderDetails").innerHTML = `<p>${data.error}</p>`;
        } else {
            document.getElementById("orderDetails").innerHTML = `
                <h3>Order ID: ${data.OrderID}</h3>
                <p>Estimated Delivery Time: ${data.EstimatedDeliveryTime}</p>
                <p>Assigned Delivery Partner: ${data.AssignedDeliveryPartner}</p>
                <p>Delivered Status: ${data.DeliveredStatus}</p>
                <h4>Items:</h4>
                <ul>
                    ${data.Items.map(item => `
                        <li>Product ID: ${item.ProductID}, Quantity: ${item.Quantity}, Price: $${item.Price}</li>
                    `).join("")}
                </ul>
                <p>Total Price: $${data.TotalPrice}</p>
                <p>Payment Status: ${data.PaymentStatus}</p>
            `;
        }
    })
    .catch(error => console.error('Error fetching order details:', error));
});

document.getElementById("b3").addEventListener("click",()=>{
    document.getElementById("trackOrder").innerHTML = "";
    document.getElementById("order-id").value = "";
});

document.getElementById("b2").addEventListener("click",()=>{
    document.getElementById("orderConfirmation").innerHTML = "";
    document.getElementById("email").value = "";
});

document.getElementById("b1").addEventListener("click",()=>{
    document.getElementById("orderDetails").innerHTML = "";
    document.getElementById("detailsEmail").value = "";
    document.getElementById("orderId").value = "";
});

document.getElementById("b4").addEventListener("click", async () => {
    const orderId = document.getElementById("orderIdpay").value;
    const email = document.getElementById("emailpay").value;

    try {
        const response = await fetch('/payments/init?order_id=' + orderId + '&email=' + email, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        const data = await response.json();
        document.getElementById("responseMessage").innerText = data.msg || data.error;

        if (response.status === 201) {
            console.log('Payment initiated:', data.payment_id);
            setTimeout(() => window.location.href = '/paynow?orderid=' + orderId + '&amt=' + data.amount, 2000);
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById("responseMessage").innerText = "An error occurred. Please try again.";
    }
});

document.getElementById('clear-pay').addEventListener("click",function(){
    document.getElementById('paymentForm').reset();
    document.getElementById('responseMessage').innerText = "";
});

document.getElementById("verifyButton").addEventListener("click", async () => {
    const paymentId = document.getElementById("paymentId").value;
    const razorpayOrderId = document.getElementById("razorpayOrderId").value;

    try {
        const response = await fetch('/payments/verify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                payment_id: paymentId,
                order_id: razorpayOrderId
            }),
        });

        const data = await response.json();
        if (!response.ok) {
            console.error('Verification error:', data);
            document.getElementById("verificationMessage").innerText = data.message || data.error;
            return;
        }
        document.getElementById("verificationMessage").innerText = data.message;
    } catch (error) {
        console.error('Error:', error);
        document.getElementById("verificationMessage").innerText = "Verification failed. Please try again.";
    }
});

document.getElementById('clear-verify').addEventListener("click", function() {
    document.getElementById('verificationForm').reset();
    document.getElementById('verificationMessage').innerText = "";
});
