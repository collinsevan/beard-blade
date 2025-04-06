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
            // Get the trigger element based on the collapse element
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

    // Retrieve timeslots data from the embedded JSON
    const timeslotsDataElem = document.getElementById("timeslots-data");
    if (timeslotsDataElem) {
        const timeslotsByDate = JSON.parse(timeslotsDataElem.textContent);
        const dateSelect = document.getElementById("date");
        const timeSelect = document.getElementById("time");

        // Populate time dropdown based on selected date
        function populateTimeOptions(selectedDate) {
            timeSelect.innerHTML = "";
            if (timeslotsByDate[selectedDate]) {
                timeslotsByDate[selectedDate].forEach(function (timeStr) {
                    const option = document.createElement("option");
                    option.value = timeStr;
                    option.textContent = timeStr;
                    timeSelect.appendChild(option);
                });
            }
        }
        // On page load populate time options for the current date
        if (dateSelect && dateSelect.value) {
            populateTimeOptions(dateSelect.value);
        }
        // Update time options when the date selection changes
        if (dateSelect) {
            dateSelect.addEventListener("change", function () {
                if (!timeslotsByDate[this.value]) {
                    // Trigger the Bootstrap modal instead
                    const modalElement = document.getElementById("noTimeSlotsModal");
                    const noTimeSlotsModal = new bootstrap.Modal(modalElement);
                    noTimeSlotsModal.show();
                    timeSelect.innerHTML = "";
                    const option = document.createElement("option");
                    option.value = "";
                    option.textContent = "No available time slots";
                    timeSelect.appendChild(option);
                } else {
                    populateTimeOptions(this.value);
                }
            });
        }
    }
    // Delete Review modal
    var confirmDeleteModal = document.getElementById("confirmDeleteModal");
    if (confirmDeleteModal) {
        confirmDeleteModal.addEventListener("show.bs.modal", function (event) {
            var button = event.relatedTarget;
            var reviewId = button.getAttribute("data-review-id");
            var form = document.getElementById("deleteReviewForm");
            form.action = "/review/delete/" + reviewId + "/";
        });
    }
});