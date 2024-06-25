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

    OutButton.onclick = function () {
        deleteUser();
        // Удаление данных пользователя из Local Storage
        localStorage.removeItem('id');
        localStorage.removeItem('username');
        localStorage.removeItem('email');
        profile.style.display = "none";
        setTimeout(function() {
            window.location.href = 'main.html';
        }, 100); // Задержка в миллисекундах
    }


});

// ----------drag-drop-------------
var addFilesBtn = document.getElementById("add-button");
var addFilesWindow = document.getElementById("add-files");
var uploadBtn = document.getElementById("upload");
var overlay = document.getElementById("overlay");

var heading = document.getElementById("Heading");
var mainList = document.getElementById("mainList");

var infoBlock = document.getElementById("info-block");

const inputField = document.getElementById('on-board-number');
const suggestionsList = document.getElementById('suggestions-list');

addFilesBtn.onclick = function () {
    addFilesWindow.style.display = "flex";
    overlay.style.display = "flex";
};

// -----escape to close--------
document.addEventListener('keydown', function(event) {
    if (event.key === "Escape") {
        if (profile.style.display == "flex" || addFilesWindow.style.display == "flex" ||
        overlay.style.display == "flex") {
            profile.style.display = "none";
            addFilesWindow.style.display = "none";
            overlay.style.display = "none";
            suggestionsList.style.display = 'none';
            inputField.value = '';
        }
    }
});

//--------------------------- drag-drop zone try-----------------------------------------
const dropZone = document.getElementById("drag-drop");
const dropZoneText = document.getElementById("drag-drop-text");
const filePreview = document.getElementById("file-preview");
const fileImage = document.getElementById("file-image");
const fileName = document.getElementById("file-name");
const clearButton = document.getElementById("clear-button");
const uploadButton = document.getElementById("upload-button");

let selectedFile = null;

dropZone.addEventListener('dragover', (event) =>  {
    event.preventDefault();
    dropZone.style.backgroundColor = '#f1f1f1';
    // dropZone.style.border = '3px dashed black';
    // dropZone.style.opacity = '0.8';
    dropZoneText.style.fontWeight = 'bold';
    dropZoneText.style.color = 'black';
});

dropZone.addEventListener('dragleave', (event) => {
    event.preventDefault();
    dropZone.style.backgroundColor = 'transparent';
    // dropZone.style.border = '2px dashed rgba(117, 120, 123, 1)';
    // dropZone.style.opacity = '1';
    dropZoneText.style.fontWeight = 'normal';
    dropZoneText.style.color = 'rgba(83, 86, 90, 1);';
});

dropZone.addEventListener('drop', (event) => {
    event.preventDefault();
    dropZone.style.backgroundColor = 'transparent';
    // dropZone.style.border = '2px dashed rgba(117, 120, 123, 1)';
    // dropZone.style.opacity = '1';
    dropZoneText.style.fontWeight = 'normal';
    dropZoneText.style.color = 'rgba(83, 86, 90, 1);'

    const files = event.dataTransfer.files;

    // Обработка только одного файла и ПРОВЕРКА НА ONLY .CSV
    if (files.length > 0) {
        if (files[0].type === 'text/csv' || files[0].name.endsWith('.csv')) {
            selectedFile = files[0];
            handleFile(selectedFile);
        } else {
            alert('Only .csv files are allowed.');
        }
    }
});

function handleFile(file) {

    console.log('Uploading file:', file);
    
    // Display preview
    fileName.textContent = file.name;

    // Check if the file is an image
    if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = function(e) {
            fileImage.src = e.target.result;
            fileImage.style.display = 'block';
        }
        reader.readAsDataURL(file);
    } else {
        fileImage.style.display = 'none';
    }

    filePreview.style.display = 'flex';
    clearButton.style.display = 'block';
    dropZoneText.style.opacity = '0'; // Hide the text when a file is uploaded

    uploadButton.disabled = false; // Enable the upload button
}

clearButton.addEventListener('click', () => {
    event.preventDefault();
    filePreview.style.display = 'none';
    fileImage.src = '';
    fileName.textContent = '';
    clearButton.style.display = 'none';
    dropZoneText.style.opacity = '1'; // Show the text again when the file is cleared

    selectedFile = null; // Clear the selected file
    uploadButton.disabled = true; // Disable the upload button
});

s7Logo.onclick = function(event) {
    event.preventDefault();
    s7Logo.classList.add('green-effect');
    setTimeout(function() {
        s7Logo.classList.remove('green-effect');
    }, 500); // Duration of the animation
}

uploadButton.disabled = false;

uploadButton.addEventListener('click', async (event) => {
    event.preventDefault();

    var username = localStorage.getItem('username');
    const onboardNumber = document.querySelector('input[placeholder="Enter/select on-board number"]').value;
    const projectName = document.querySelector('input[placeholder="Enter the name of the project..."]').value;
    
    if (!selectedFile) {
        alert('Загрузите файл в drag and drop');
        return;
    }

    if (!onboardNumber & !projectName) {
        alert('Please fill out all fields!');
        return;
    }

    if (!onboardNumber) {
        alert('Please enter on-board-Number in the special field!');
        return;
    }

    if (!projectName) {
        alert('Please enter a project-Name in the special field!');
        return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('onboardNumber', onboardNumber);
    formData.append('projectName', projectName); 
    formData.append('Username', username);

    try {
        const response = await fetch('http://127.0.0.1:8000/upload', {
            method: 'POST',
            body: formData,
        });

        if (response.ok) {
            alert('File uploaded successfully!');
            fileName.textContent = '';
            selectedFile = null;
            uploadButton.disabled = true; // Disable the upload button
        } else {
            alert('File upload failed.');
        }
    } catch (error) {
        console.error('Error uploading file:', error);
        alert('An error occurred while uploading the file.');
    }
});

//-------------------------trying suggestions menu----------------------------

// Массив с предложениями
const suggestions = ['VQ-BGU', 'VQ-BDU'];

function handleSuggestionClick(suggestion) {
    inputField.value = suggestion;
    hideSuggestions();
  
    // Здесь можно добавить дополнительную логику обработки выбранного значения
    console.log('Выбрано значение:', suggestion);
}

// Функция для отображения предложений
function showSuggestions() {
  suggestionsList.innerHTML = '';

  // Фильтруем предложения, начинающиеся с введенного текста
  const filteredSuggestions = suggestions.filter(suggestion =>
    suggestion.toLowerCase().startsWith(inputField.value.toLowerCase())
  );

  // Создаем элементы списка для каждого предложения
  filteredSuggestions.forEach(suggestion => {
    const listItem = document.createElement('li');
    listItem.textContent = suggestion;
    listItem.addEventListener('click', () => 
      handleSuggestionClick(suggestion));
    suggestionsList.appendChild(listItem);
  });

  // Показываем поле ввода, список предложений и обертку, если есть что показывать
  if (filteredSuggestions.length > 0) {
    suggestionsList.style.display = 'flex';
  } else {
    hideSuggestions();
  }
}


// Функция для скрытия списка предложений
function hideSuggestions() {
  suggestionsList.style.display = 'none';
}

// Обработчик события фокуса на поле ввода
inputField.addEventListener('focus', showSuggestions);

async function deleteUser() {
    var userId = localStorage.getItem('id');
    if (confirm('Вы действительно хотите удалить?')) {
        const response = await fetch(`http://127.0.0.1:8000/users/${userId}`, {
            method: 'DELETE',
        });
        if (response.ok) {
            alert('Пользователь удален успешно');
        } else {
            alert('Ошибка при удалении пользователя');
        }
    }
}

async function fetchRequests() {
    var username = localStorage.getItem('username');
    const response = await fetch(`http://127.0.0.1:8000/requests/${username}`);
    const requests = await response.json();
    const table = document.getElementById('user-request');

    requests.forEach(request => {
        const row = table.insertRow();
        const createdAtCell = row.insertCell(0);
        const projectNameCell = row.insertCell(1);
        const onboardNumberCell = row.insertCell(2);
        const actionCell = row.insertCell(3);
        
        projectNameCell.innerHTML = `<a href='#' onclick="GoToRequest(${request.id}); return false;">${request.project_name}</a>`;
        onboardNumberCell.textContent = request.onboard_number;
        createdAtCell.textContent = new Date(request.created_at).toLocaleString();
        actionCell.innerHTML = `<a href="#" onclick="deleteRequest(${request.id}); return false;">Удалить</a>`;
    });
}

async function deleteRequest(requestId) {
    if (confirm('Вы действительно хотите удалить?')) {
        const response = await fetch(`http://127.0.0.1:8000/requests/${requestId}`, {
            method: 'DELETE',
        });
        if (response.ok) {
            alert('Запрос удален успешно');
            document.location.reload();
        } else {
            alert('Ошибка при удалении запроса');
        }
    }
}


async function GoToRequest(requestId) {
    localStorage.setItem('id_request', requestId);
    window.location.href = "request.html";
}


window.onload = () => {
    fetchRequests();
};