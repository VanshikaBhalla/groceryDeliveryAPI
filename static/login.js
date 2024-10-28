
async function loginUser() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const messageElement = document.getElementById("message");
    messageElement.textContent = "";

    if (!email || !password) {
        messageElement.textContent = "Please fill in all fields.";
        return;
    }

    const userData = {
        email: email,
        pwd: password
    };

    try {
        const response = await fetch('/users/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });

        const result = await response.json();

        if (response.ok) {
            messageElement.style.color = "green";
            messageElement.textContent = "Login successful! Redirecting...";
            localStorage.setItem('token', result.token);
            const redirectPath = result.role === 'delivery_personnel' ? '/delivery' : '/products';
            setTimeout(() => window.location.href = redirectPath, 2000);

        } else {
            messageElement.style.color = "red";
            messageElement.textContent = result.error;
        }
    } catch (error) {
        messageElement.style.color = "red";
        messageElement.textContent = "Login failed, please try again.";
    }
}

document.getElementById("loginForm").addEventListener("submit", (event) => {
    event.preventDefault();
    loginUser();
});
