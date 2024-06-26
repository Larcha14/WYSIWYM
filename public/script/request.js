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
        if (profile.style.display === "flex") {
            profile.style.display = "none";
        } else {
            profile.style.display = "flex";
        }
    }

    // Кнопка для выхода из системы
    var signOutButton = document.getElementById("sign-out");

    signOutButton.onclick = function () {
        // Удаление данных пользователя из Local Storage
        localStorage.removeItem('id');
        localStorage.removeItem('username');
        localStorage.removeItem('email');
        profile.style.display = "none";
        setTimeout(function() {
            window.location.href = 'main.html';
        }, 100); // Задержка в миллисекундах
    }

    // Кнопка удаления аккаунта
    var OutButton = document.getElementById("deleteAcc");

    OutButton.onclick = async function () {
        const isDeleted = await deleteUser();
        if (isDeleted) {
            // Удаление данных пользователя из Local Storage только если удаление успешно
            localStorage.removeItem('id');
            localStorage.removeItem('username');
            localStorage.removeItem('email');
            profile.style.display = "none";
            setTimeout(function() {
                window.location.href = 'main.html';
            }, 100); // Задержка в миллисекундах
        }
    }

});

// Обработчик события фокуса на поле ввода
inputField.addEventListener('focus', showSuggestions);

async function deleteUser() {
    var userId = localStorage.getItem('id');
    if (!confirm('Do you really want to delete the user?')) {
        return false;
    }
    
    try {
        const response = await fetch(`http://127.0.0.1:8000/users/${userId}`, {
            method: 'DELETE',
        });

        if (response.ok) {
            alert('The user was deleted successfully.');
            return true;
        } else {
            alert('Error deleting the user.');
            return false;
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while deleting the user.');
        return false;
    }
}

async function GoToRequest(requestId) {
    localStorage.setItem('id_request', requestId);
    window.location.href = "request.html";
}
