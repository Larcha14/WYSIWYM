// ------------------Окна регистрации и входа в аккаунт--------------------------


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

buttonLogin.onclick = function () {
    registration.style.display = "flex";
    // overlay.style.display = "flex";
}

buttonReg.onclick = function () {
    registration.style.display = "none";
    // overlay.style.display = "none";
}

document.addEventListener('keydown', function(event) {
    if (event.key === "Escape") {
        if (registration.style.display == 'flex' || 
            login.style.display == 'flex') {
            registration.style.display = "none";
            login.style.display = "none";
            overlay.style.display = "none";
        }
    }
});

var submitBtn = document.getElementById("Submit");
var sbmtBtn = document.getElementById("Sbmt");

submitBtn.onclick = function () {
    login.style.display = "none"
    registration.style.display = "none"
    overlay.style.display = "none";
    setTimeout(function() {
        window.location.href = 'My requests.html';
    }, 100); // Задержка в миллисекундах
}


sbmtBtn.onclick = function () {
    registration.style.display = "none"
    login.style.display = "none"
    overlay.style.display = "none";
    setTimeout(function() {
        window.location.href = 'My requests.html';
    }, 100); // Задержка в миллисекундах
} 


// ------------------------------------Окно информации о профиле----------------------------------------\

// var userInfoButton = document.getElementById("userLogo");
// var UserInfo = document.getElementById("profile")
// var signOutButton = document.getElementById("sign-out");

// userInfoButton.onclick = function () {
//     profile.style.display = "flex";
// }

// signOutButton.onclick = function () {
//     profile.style.display = "none"
//     window.location.href = 'file:///home/stepan/%D0%A0%D0%B0%D0%B1%D0%BE%D1%87%D0%B8%D0%B9%20%D1%81%D1%82%D0%BE%D0%BB/%D1%83%D1%87%D0%B5%D0%B1%D0%B0/prog4sem/itproject/main.html'
// }


