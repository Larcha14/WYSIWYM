document.addEventListener('DOMContentLoaded', function() {
    // Получение данных пользователя из Local Storage
    var username = localStorage.getItem('username');
    var email = localStorage.getItem('email');
    
    if (username && email) {
        document.getElementById('userLogin').innerText = username;
        document.getElementById('userEmail').innerText = email;
    } else {
        // Если данные пользователя не найдены, перенаправить на страницу входа
        window.location.href = 'main.html';
    }

    // Кнопка для отображения профиля
    var userInfoButton = document.getElementById("userLogo");
    var profile = document.getElementById("profile");

    userInfoButton.onclick = function () {
        profile.style.display = "flex";
    }

    // Кнопка для выхода из системы
    var signOutButton = document.getElementById("sign-out");

    signOutButton.onclick = function () {
        // Удаление данных пользователя из Local Storage
        localStorage.removeItem('username');
        localStorage.removeItem('email');
        profile.style.display = "none";
        setTimeout(function() {
            window.location.href = 'main.html';
        }, 100); // Задержка в миллисекундах
    }

    // ----------drag-drop-------------

    var addFilesBtn = document.getElementById("add-button");
    var addFilesWindow = document.getElementById("add-files");
    var uploadBtn = document.getElementById("upload");
    var overlay = document.getElementById("overlay");

    var heading = document.getElementById("Heading");
    var mainList = document.getElementById("mainList")

    var infoBlock = document.getElementById("info-block");

    addFilesBtn.onclick = function () {
        addFilesWindow.style.display = "flex";
        overlay.style.display = "flex";
    }

    uploadBtn.onclick = function () {
        addFilesWindow.style.display = "none";
        overlay.style.display = "none";
        heading.style.display = "none";
        mainList.style.display = "none";
        infoBlock.style.display = "inline";
    }

    // -----escape to close--------

    document.addEventListener('keydown', function(event) {
        if (event.key === "Escape") {
            if (profile.style.display == "flex" || addFilesWindow.style.display == "flex" ||
            overlay.style.display == "flex") {
                profile.style.display = "none";
                addFilesWindow.style.display = "none";
                overlay.style.display = "none";
            }
        }
    });

    // ---------------------report window-------------------------

    var rPlot = document.getElementById("r-plot");
    var rTable = document.getElementById("r-table");
    var pic1 = document.getElementById("img1");
    var pic2 = document.getElementById("img2");

    rTable.onclick = function () {
        pic1.style.display = "none";
        pic2.style.display = "flex";
        rTable.style.backgroundColor = "rgba(196, 214, 0, 1)";
        rPlot.style.backgroundColor = "rgba(117, 120, 123, 1)";
    }

    rPlot.onclick = function () {
        pic1.style.display = "flex";
        pic2.style.display = "none";
        rTable.style.backgroundColor = "rgba(117, 120, 123, 1)";
        rPlot.style.backgroundColor = "rgba(196, 214, 0, 1)";
    }
});
