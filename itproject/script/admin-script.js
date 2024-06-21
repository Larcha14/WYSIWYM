
async function fetchUsers() {
    const response = await fetch('http://127.0.0.1:8000/users/');
    const users = await response.json();
    const table = document.getElementById('users-table');
    users.forEach(user => {
        const row = table.insertRow();
        const idCell = row.insertCell(0);
        const usernameCell = row.insertCell(1);
        const emailCell = row.insertCell(2);
        const passw = row.insertCell(3);
        const actionCell = row.insertCell(4);
        usernameCell.textContent = user.username;
        emailCell.textContent = user.email;
        idCell.textContent = user.id;
        passw.textContent = user.password;
        actionCell.innerHTML = `<a href="#" onclick="deleteUser(${user.id}); return false;">Удалить</a>`;
    });
}
async function deleteUser(userId) {
    if (confirm('Вы действительно хотите удалить?')) {
        const response = await fetch(`http://127.0.0.1:8000/users/${userId}`, {
            method: 'DELETE',
        });
        if (response.ok) {
            alert('Пользователь удален успешно');
            document.location.reload();
        } else {
            alert('Ошибка при удалении пользователя');
        }
    }
}

window.onload = fetchUsers;