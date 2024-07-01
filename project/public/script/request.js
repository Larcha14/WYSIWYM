document.addEventListener('DOMContentLoaded', function() {
    // Получение данных пользователя из Local Storage
    var username = localStorage.getItem('username');
    var email = localStorage.getItem('email');
    var projectName = localStorage.getItem('project_name');
    var id_project = localStorage.getItem('id_request');

    if (username && email) {
        document.getElementById('userLogin').innerText = username;
        document.getElementById('userEmail').innerText = email;
    } else {
        // Если данные пользователя не найдены, перенаправить на страницу входа
        window.location.href = '/';
    }
    // Устанавливаем имя проекта в заголовке
    if (projectName) {
    document.getElementById('Heading').innerText = `Project: ${projectName}`;
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
            window.location.href = '/';
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
                window.location.href = '/';
            }, 100); // Задержка в миллисекундах
        }
    }
});


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
    window.location.href = "/request";
}



let csvData1 = null;
let csvData2 = null;

document.getElementById('yColumnSelect1').addEventListener('change', updateChart1, false);
document.getElementById('egtmCheckbox1').addEventListener('change', updateChart1, false);

document.getElementById('yColumnSelect2').addEventListener('change', updateChart2, false);
document.getElementById('egtmCheckbox2').addEventListener('change', updateChart2, false);

async function fetchRequestFiles() {
    var id_project = localStorage.getItem('id_request');
    if (!id_project) {
        alert("ID request not found in localStorage.");
        return;
    }

    try {
        const response = await fetch(`http://127.0.0.1:8000/requests/${id_project}/csv-files`);
        if (response.ok) {
            const data = await response.json();
            const csvFile1 = data.csv_file1.replace(/\\/g, '/');  
            const csvFile2 = data.csv_file2.replace(/\\/g, '/');

            // Корректируем пути относительно корня веб-сервера
            const csvPath1 = `.${csvFile1}`;  
            const csvPath2 = `.${csvFile2}`;  

            loadCSVData(csvPath1, csvPath2);
        } else {
            const errorData = await response.json();
            alert('Ошибка при получении CSV файлов: ' + errorData.detail);
        }
    } catch (error) {
        console.error('Ошибка при выполнении запроса:', error);
        alert('Произошла ошибка при получении CSV файлов');
    }
}

function loadCSVData(csvPath1, csvPath2) {
    fetch(csvPath1)
        .then(response => response.text())
        .then(data => {
            csvData1 = parseCSV(data);
            populateColumnSelector(csvData1.labels, 'yColumnSelect1');
            updateChart1();
        })
        .catch(error => {
            console.error('Ошибка при загрузке первого CSV файла:', error);
        });

    fetch(csvPath2)
        .then(response => response.text())
        .then(data => {
            csvData2 = parseCSV(data);
            populateColumnSelector(csvData2.labels, 'yColumnSelect2');
            updateChart2();
        })
        .catch(error => {
            console.error('Ошибка при загрузке второго CSV файла:', error);
        });
}

window.onload = () => {
    fetchRequestFiles();
};

// Функции для первого графика
function handleFileSelect1(event) {
    const file = event.target.files[0];
    const reader = new FileReader();

    reader.onload = function(e) {
        const text = e.target.result;
        csvData1 = parseCSV(text);
        populateColumnSelector(csvData1.labels, 'yColumnSelect1');
        updateChart1();
    };

    reader.readAsText(file);
}

function updateChart1() {
    if (!csvData1) return;

    const yIndex = document.getElementById('yColumnSelect1').value;
    const showEgt = document.getElementById('egtmCheckbox1').checked;

    const xData = csvData1.values.map(row => row[csvData1.labels.indexOf('reportts')]);
    const yData = csvData1.values.map(row => row[yIndex]);

    const traces = [{
        x: xData,
        y: yData,
        type: 'scatter',
        mode: 'lines+markers',
        name: csvData1.labels[yIndex]
    }];

    if (showEgt) {
        const predictData = csvData1.values.map(row => row[csvData1.labels.length - 1]);
        traces.push({
            x: xData,
            y: predictData,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Predict',
            line: {
                color: 'red'
            },
            yaxis: 'y2'
        });
    }

    const layout = {
        title: 'POS 1',
        xaxis: {
            title: 'reportts',
            type: 'date'
        },
        yaxis: {
            title: csvData1.labels[yIndex]
        },
        yaxis2: {
            title: 'Predict',
            overlaying: 'y',
            side: 'right'
        }
    };

    Plotly.newPlot('plotlyChart1', traces, layout);
}

// Функции для второго графика
function handleFileSelect2(event) {
    const file = event.target.files[0];
    const reader = new FileReader();

    reader.onload = function(e) {
        const text = e.target.result;
        csvData2 = parseCSV(text);
        populateColumnSelector(csvData2.labels, 'yColumnSelect2');
        updateChart2();
    };

    reader.readAsText(file);
}

function updateChart2() {
    if (!csvData2) return;

    const yIndex = document.getElementById('yColumnSelect2').value;
    const showEgt = document.getElementById('egtmCheckbox2').checked;

    const xData = csvData2.values.map(row => row[csvData2.labels.indexOf('reportts')]);
    const yData = csvData2.values.map(row => row[yIndex]);

    const traces = [{
        x: xData,
        y: yData,
        type: 'scatter',
        mode: 'lines+markers',
        name: csvData2.labels[yIndex]
    }];

    if (showEgt) {
        const predictData = csvData2.values.map(row => row[csvData2.labels.length - 1]);
        traces.push({
            x: xData,
            y: predictData,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Predict',
            line: {
                color: 'red'
            },
            yaxis: 'y2'
        });
    }

    const layout = {
        title: 'POS 2',
        xaxis: {
            title: 'reportts',
            type: 'date'
        },
        yaxis: {
            title: csvData2.labels[yIndex]
        },
        yaxis2: {
            title: 'Predict',
            overlaying: 'y',
            side: 'right'
        }
    };

    Plotly.newPlot('plotlyChart2', traces, layout);
}

// Общие функции
function parseCSV(text) {
    const rows = text.trim().split('\n').map(row => row.split(','));
    const labels = rows[0];
    const values = rows.slice(1).map(row => row.map(cell => isNaN(cell) ? cell : parseFloat(cell)));

    return { labels, values };
}

function populateColumnSelector(labels, selectId) {
    const yColumnSelect = document.getElementById(selectId);
    yColumnSelect.innerHTML = '';

    labels.forEach((label, index) => {
        const option = document.createElement('option');
        option.value = index;
        option.text = label;
        yColumnSelect.appendChild(option);
    });

    yColumnSelect.selectedIndex = 0;
}

// -----escape to close--------
document.addEventListener('keydown', function(event) {
    if (event.key === "Escape") {
        if (profile.style.display == "flex") {
            profile.style.display = "none";
        }
    }
});