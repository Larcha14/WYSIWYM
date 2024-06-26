
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
    if (confirm('Do you really want to delete the user?')) {
        const response = await fetch(`http://127.0.0.1:8000/users/${userId}`, {
            method: 'DELETE',
        });
        if (response.ok) {
            alert('The user was deleted successfully.');
            document.location.reload();
        } else {
            alert('Error deleting the user.');
        }
    }
}

async function fetchRequests() {
    const response = await fetch('http://127.0.0.1:8000/requests/');
    const requests = await response.json();
    const table = document.getElementById('requests-table');

    requests.forEach(request => {
        const row = table.insertRow();
        const usernameCell = row.insertCell(0);
        const projectNameCell = row.insertCell(1);
        const onboardNumberCell = row.insertCell(2);
        const createdAtCell = row.insertCell(3);
        const linknameCell = row.insertCell(4);
        const actionCell = row.insertCell(5);

        usernameCell.textContent = request.username;
        projectNameCell.textContent = request.project_name;
        onboardNumberCell.textContent = request.onboard_number;
        createdAtCell.textContent = new Date(request.created_at).toLocaleString();
        linknameCell.textContent = request.linkname;
        actionCell.innerHTML = `<a href="#" onclick="deleteRequest(${request.id}); return false;">Удалить</a>`;
    });
}

async function deleteRequest(requestId) {
    if (confirm('Do you really want to delete the request?')) {
        const response = await fetch(`http://127.0.0.1:8000/requests/${requestId}`, {
            method: 'DELETE',
        });
        if (response.ok) {
            alert('The request was deleted successfully.');
            document.location.reload();
        } else {
            alert('Error deleting the request.');
        }
    }
}


window.onload = () => {
    fetchUsers();
    fetchRequests();
};