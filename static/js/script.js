document.addEventListener("DOMContentLoaded", function () {
    const togglePassword = document.getElementById("togglePassword");
    const passwordInput = document.getElementById("password-box");
    // Toggle to show passwsord 
    if (togglePassword && passwordInput) {
        togglePassword.addEventListener("click", function () {
            const currentType = passwordInput.getAttribute("type");
            const newType = currentType === "password" ? "text" : "password";
            passwordInput.setAttribute("type", newType);

            const icon = togglePassword.querySelector("i");
            if (icon) {
                icon.classList.toggle("bi-eye");
                icon.classList.toggle("bi-eye-slash");
            }
        });
    }

    console.log("script.js loaded and running");
});