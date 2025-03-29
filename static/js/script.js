document.addEventListener("DOMContentLoaded", function () {
    // Select all toggle elements for password fields
    const toggles = document.querySelectorAll(".password-toggle");
    toggles.forEach(function (toggle) {
        toggle.addEventListener("click", function () {
            // Get the target password field by its ID
            const targetId = this.getAttribute("data-target");
            const passwordInput = document.getElementById(targetId);
            if (passwordInput) {
                // Toggle the type attribute
                const currentType = passwordInput.getAttribute("type");
                const newType = currentType === "password" ? "text" : "password";
                passwordInput.setAttribute("type", newType);

                // Toggle the icon class
                const icon = this.querySelector("i");
                if (icon) {
                    icon.classList.toggle("bi-eye");
                    icon.classList.toggle("bi-eye-slash");
                }
            }
        });
    });
    console.log("Password toggle script loaded and running");
});