var modal = document.getElementById("sign-up");
var btn = document.getElementById("openModal");

btn.onclick = function() {
    modal.style.display = "flex";
}

window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}