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

    // Profile collapse toggle functionality: Toggle chevron icon on collapse events
    const collapseElements = document.querySelectorAll("#profile-page .collapse");
    collapseElements.forEach(function (collapseEl) {
        collapseEl.addEventListener("show.bs.collapse", function () {
            // Get the trigger element based on the collapse element's ID
            const trigger = document.querySelector(
                '[data-bs-toggle="collapse"][href="#' + collapseEl.id + '"]'
            );
            if (trigger) {
                const icon = trigger.querySelector("i");
                if (icon) {
                    icon.classList.remove("bi-chevron-down");
                    icon.classList.add("bi-chevron-up");
                }
            }
        });
        collapseEl.addEventListener("hide.bs.collapse", function () {
            // Get the trigger element based on the collapse element's ID
            const trigger = document.querySelector(
                '[data-bs-toggle="collapse"][href="#' + collapseEl.id + '"]'
            );
            if (trigger) {
                const icon = trigger.querySelector("i");
                if (icon) {
                    icon.classList.remove("bi-chevron-up");
                    icon.classList.add("bi-chevron-down");
                }
            }
        });
    });
});