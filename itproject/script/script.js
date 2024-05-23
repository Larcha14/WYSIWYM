document.addEventListener('DOMContentLoaded', function() {
    var login = document.getElementById("sign-in");
    var registration = document.getElementById("sign-up");
    var btn = document.getElementById("openModal");
    var buttonLogin = document.getElementById("No_acc");
    var buttonReg = document.getElementById("have-acc");
    var overlay = document.getElementById("overlay");

    btn.onclick = function() {
        overlay.style.display = "flex";
        login.style.display = "flex";
    }

    buttonLogin.onclick = function() {
        registration.style.display = "flex";
        login.style.display = "none";
    }

    buttonReg.onclick = function() {
        registration.style.display = "none";
        login.style.display = "flex";
    }

    document.addEventListener('keydown', function(event) {
        if (event.key === "Escape") {
            if (registration.style.display == 'flex' || login.style.display == 'flex') {
                registration.style.display = "none";
                login.style.display = "none";
                overlay.style.display = "none";
            }
        }
    });

    // Обработка регистрации
    document.getElementById("registrationForm").onsubmit = async function(event) {
        event.preventDefault();
        
        var username = document.getElementById("registerUsername").value;
        var email = document.getElementById("registerEmail").value;
        var password = document.getElementById("registerPassword").value;
        var repeatPassword = document.getElementById("registerRepeatPassword").value;

        if (password !== repeatPassword) {
            alert("Passwords do not match!");
            return;
        }

        var response = await fetch("http://127.0.0.1:8000/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password
            })
        });

        var data = await response.json();

        if (response.ok) {
            alert("Registration successful!");
            registration.style.display = "none";
            login.style.display = "flex";
            
            // Перенаправление на страницу My requests.html после успешной регистрации
            window.location.href = "My requests.html";
        } else {
            alert("Registration failed: " + data.detail);
        }
    };

    // Обработка входа
    document.getElementById("loginForm").onsubmit = async function(event) {
        event.preventDefault();

        var username = document.getElementById("loginUsername").value;
        var password = document.getElementById("loginPassword").value;

        var response = await fetch("http://127.0.0.1:8000/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        var data = await response.json();

        if (response.ok) {
            alert("Login successful!");
            // Перенаправление на страницу My requests.html после успешного входа
            window.location.href = "My requests.html";
        } else {
            alert("Login failed: " + data.detail);
        }
    };
});
