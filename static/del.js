document.getElementById("updateStatusForm").addEventListener("submit", function(event) {
    event.preventDefault();

    const orderId = document.getElementById("order-id-status").value;
    const email = document.getElementById("delivery-email-status").value;
    const status = document.getElementById("status-update").value;

    fetch('/delivery/update-status', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            order_id: orderId,
            delivery_personnel_email: email,
            status: status
        })
    })
    .then(response => response.json())
    .then(data => {
        const resultDiv = document.getElementById("updateStatusResult");
        if (data.error) {
            resultDiv.textContent = `Error: ${data.error}`;
            resultDiv.style.color = "red";
        } else {
            resultDiv.textContent = data.message;
            resultDiv.style.color = "green";
        }
    })
    .catch(error => {
        console.error("Error:", error);
        document.getElementById("updateStatusResult").textContent = "An error occurred. Please try again.";
    });
});

document.getElementById("clear-update-status").addEventListener("click", function() {
    document.getElementById("updateStatusForm").reset();
    document.getElementById("updateStatusResult").textContent = "";
});
