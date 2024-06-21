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

    s7Logo.onclick = function(event) {
        event.preventDefault();
        s7Logo.classList.add('green-effect');
        setTimeout(function() {
            s7Logo.classList.remove('green-effect');
        }, 500); // Duration of the animation
    }

    // Обработка регистрации
    document.getElementById("registrationForm").onsubmit = async function(event) {
        event.preventDefault();
        
        var username = document.getElementById("registerUsername").value;
        var email = document.getElementById("registerEmail").value;
        var password = document.getElementById("registerPassword").value;
        var repeatPassword = document.getElementById("registerRepeatPassword").value;

        if (!username || !email || !password || !repeatPassword) {
            alert("All fields are required.");
            return;
        }

        if (username.length < 3 || !/^[A-Za-z0-9]+$/.test(username)) {
            alert("Username must be at least 3 characters long and contain only Latin characters and digits.");
            return;
        }

        if (!/^[^@]{3,}@[^@]{3,}\.[^@]{2,}$/.test(email)) {
            alert("Email must be in the format 'example'@'example'.'com' with at least 3 characters for each part, except for the 1st level domain");
            return;
        }

        if (password.length < 5 || !/^[A-Za-z0-9]+$/.test(password)) {
            alert("Password must be at least 5 characters long and contain only Latin characters and digits.");
            return;
        }

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

            // Сохраняем данные пользователя в Local Storage
            localStorage.setItem('username', username);
            localStorage.setItem('email', email);

            window.location.href = "Projects.html";
        } else {
            alert("Registration failed: " + data.detail);
        }
    };

    // Обработка входа
    document.getElementById("loginForm").onsubmit = async function(event) {
        event.preventDefault();

        var username = document.getElementById("loginUsername").value;
        var password = document.getElementById("loginPassword").value;

        if (username === "admin" && password === "admin"){
            alert("ADMIN login successful!");
            window.location.href = "admin.html";
        } else{

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

            // Сохраняем данные пользователя в Local Storage
            localStorage.setItem('username', data.username);
            localStorage.setItem('email', data.email);

            window.location.href = "Projects.html";
        } else {
            alert("Login failed: " + data.detail);
        }
    }
    };
});
