async function registerUser() {
    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const phone = document.getElementById("phone").value;
    const role = document.getElementById("role").value;

    const messageElement = document.getElementById("message");
    messageElement.textContent = "";

    if (!name || !email || !password || !phone || !role) {
        messageElement.textContent = "Please fill in all fields.";
        return;
    }

    const userData = {
        name: name,
        email: email,
        pwd: password,
        phone: phone,
        role: role
    };

    try {
        const response = await fetch('/users/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });

        const result = await response.json();

        if (response.ok) {
            messageElement.style.color = "green";
            messageElement.textContent = result.message;
            setTimeout(() => window.location.href = "/users/login", 2000);  // redirect to login page
        } else {
            messageElement.style.color = "red";
            messageElement.textContent = result.error;
        }
    } catch (error) {
        messageElement.style.color = "red";
        messageElement.textContent = "Registration failed, please try again.";
    }
}

document.getElementById("registrationForm").addEventListener("submit", (event) => {
    event.preventDefault();
    registerUser();
});
