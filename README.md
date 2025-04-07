# Beard & Blade

A premium barber services web application offering online booking, user reviews, and account management.

![Homepage Screenshot](static/images/homepage.png)

# [Live Site](https://beard-blade-b70a56b4f23e.herokuapp.com/)

## Table of Contents

- [Overview](#overview)
- [Languages & Technologies](#languages--technologies)
- [Installation & Setup](#installation--setup)
- [Deployment](#Deployment)
- [Features](#features)
- [Color Scheme](#color-scheme)
- [Database Schema](#database-schema)
- [Wireframes](#wireframes)
- [User Story & Admin Story](#user-story--admin-story)
- [Lighthouse Testing](#lighthouse-testing)
- [Manual Testing](#manual-testing)
- [Known Bugs](#known-bugs)
- [References](#references)

## Overview

Beard & Blade is a Django-based application that provides a premium barbering experience. Users can browse available services, book appointments, and leave reviews, while administrators can manage bookings, services, and reviews.

## Languages & Technologies

- **Backend:** Python, Django
- **Frontend:** HTML, CSS, Bootstrap, JavaScript
- **Database:** PostgreSQL (configured via dj_database_url)
- **Others:** django-crontab, django-allauth, django-star-ratings, autopep, django-debug-toolbar, whitenoise, mailjet (for email notifications)

## Installation & Setup

1. **Activate the Virtual Environment:**  
   Windows: `venv\Scripts\activate`  
   macOS/Linux: `source venv/bin/activate`

2. **Install Dependencies:**  
   Upgrade pip: `pip install --upgrade pip`  
   Install required packages: `pip install -r requirements.txt`

3. **Configure Environment Variables:**  
   Create an `env.py` file in the project root with the following content:  
   ```python
   import os
   os.environ["SECRET_KEY"] = "your-secret-key"
   os.environ["DATABASE_URL"] = "your-database-url"  # e.g., postgres://user:password@localhost:5432/dbname
   os.environ["MAILJET_API_KEY"] = "your-mailjet-api-key"
   os.environ["MAILJET_API_SECRET"] = "your-mailjet-api-secret"

**Database Setup & Migrations:** Run: `python manage.py migrate` (Optional: Create superuser: `python manage.py createsuperuser`)

**Collect Static Files:** Run: `python manage.py collectstatic`

**Run Automated Tasks:**  
Generate Timeslots: `python manage.py timeslots --days 7`  
Mark Completed: `python manage.py mark_completed`

**Running the Development Server:** Run: `python manage.py runserver`  
Then visit [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser

## Features

### User Management

- **Registration & Authentication:**  
  Users can sign up, log in, and log out. The system validates inputs, ensuring unique usernames and matching passwords.
- **Password Management:**  
  Integrated password reset (via email) and password change functionalities for secure account handling.

### Service & Booking System

- **Service Catalog:**  
  Display a list of available services, each with a name, price, and duration. Services are defined in the `Service` model.
- **Booking Process:**  
  Users can book a service by selecting a date and a start time. The booking process:
  - Validates that the selected date is not in the past.
  - Determines the required number of contiguous 15-minute timeslots based on the service duration.
  - Checks for availability of timeslots before creating a booking.
  - Allows users to edit or cancel their bookings via their profile.
- **Timeslot Management:**  
  Timeslots are generated in 15-minute intervals using the `TimeSlot` model. The project includes a management command (`timeslots.py`) that:
  - Generates future timeslots based on the shop's opening hours defined in the `OpeningHours` model.
  - Ensures each timeslot is set as 'available' until booked.
- **Automatic Booking Updates:**  
  A management command (`completed.py`) automatically marks confirmed bookings as completed when their end time has passed.

### Reviews & Ratings

- **Review Submission:**  
  After a completed booking, users can submit reviews with a star rating and an optional comment. Each booking can have one review.
- **Star Rating Integration:**  
  Reviews use a star rating widget, leveraging the `star_ratings` package for visual feedback.
- **Review Management:**  
  Users can edit or delete their reviews from the profile page.

### Admin Features

- **Admin Dashboard:**  
  Administrators have access to a dedicated admin panel where they can manage:
  - Services, timeslots, and opening hours.
  - Bookings, including confirming, declining, or cancelling them via custom admin actions.
  - Reviews submitted by users.
- **Custom Admin Widgets:**  
  Custom star rating widgets allow for a better review management experience in the admin interface.

### Additional Functionalities

- **Cron Jobs & Automated Tasks:**
  - A cron job (configured in `settings.py`) runs the timeslot generator command daily to prepare future appointment slots.
  - Another cron job marks bookings as completed once the booking's end time has passed.
- **Email Notifications:**  
  Integrated email backend (using Mailjet) handles password reset emails and other notifications.
- **Custom Error Handling:**  
  The project includes custom error pages (400, 403, 404, 500, etc.) for a better user experience in case of errors.

## Color Scheme

Below is the project's color palette, as defined in the CSS and used across various templates:

![Color Scheme](static/images/color_scheme.png)

### Color Usage

- **Primary Dark (`#1c1c1c`):**

  - **Usage:** Set as the overall body background in `style.css` to create a modern, dark theme.
  - **Templates:** Applied globally via the `<body>` element in `base.html`.

- **Rich Brown (`#5d2506`):**

  - **Usage:** Used for primary action buttons (`.btn-brown`), such as "Sign Up" in `register.html` and "Log In" in `login.html`.
  - **Templates:** Consistent call-to-action elements in multiple templates.

- **Gold Accent (`#af8c16`):**

  - **Usage:** Defined as a variable for potential highlights or secondary accents.
  - **Templates:** Available for future use where additional emphasis is needed.

- **Professional White (`#f5f5f5`):**

  - **Usage:** Applied to text elements like headings and paragraphs to ensure high contrast on dark backgrounds.
  - **Templates:** Widely used in `base.html`, `about.html`, and other content sections.

- **Light Background (`#f4f4f4`):**

  - **Usage:** Provides a lighter contrast background when needed, although it appears less frequently.
  - **Templates:** Can be used for sections where a softer background is desired.

- **Dark Gray (`rgb(60, 60, 60)`):**

  - **Usage:** Used as the background color for forms, cards, and modals (e.g., in `booking.html`, `register.html`, `login.html`, and `review_form.html`).
  - **Templates:** Helps the content stand out against the overall dark theme.

- **Grey Buttons (`#6c757d`):**
  - **Usage:** Applied to secondary buttons, such as those for cancel actions and password changes.
  - **Templates:** Seen in the profile page and various modals for consistent secondary action styling.

## Database Schema

Below is the ER diagram representing the database schema for Beard & Blade:

![Database Schema](static/images/schema.png)

### Models and Relationships

- **User**

  - **Fields:**
    - `id`: Primary Key
    - `username`: User's unique username
    - `email`: User's email address

- **Service**

  - **Fields:**
    - `id`: Primary Key
    - `name`: Service name (unique)
    - `duration`: Duration of the service (stored as a duration/timedelta)
    - `price`: Service price (decimal)

- **TimeSlot**

  - **Fields:**
    - `id`: Primary Key
    - `date`: Date of the timeslot
    - `start_time`: Start time of the timeslot
    - `end_time`: End time of the timeslot
    - `status`: Status of the slot (choices: "available", "pending", "booked", "expired")
  - **Constraints:**  
    Unique together on (`date`, `start_time`, `end_time`)

- **OpeningHours**

  - **Fields:**
    - `id`: Primary Key
    - `day_of_week`: Integer representing the day (0=Monday, ..., 6=Sunday; unique)
    - `open_time`: Opening time for the day
    - `close_time`: Closing time for the day

- **Booking**

  - **Fields:**
    - `id`: Primary Key
    - `status`: Booking status (choices: "pending", "confirmed", "completed", "cancelled")
    - `created_at`: Timestamp when the booking was created
    - `updated_at`: Timestamp when the booking was last updated
    - `user`: Foreign Key to **User** (the user who made the booking)
    - `service`: Foreign Key to **Service** (the booked service)
  - **Relationships:**
    - **Many-to-Many:** Connects with **TimeSlot** via a join table (each booking reserves multiple 15-minute timeslots)

- **Review**
  - **Fields:**
    - `id`: Primary Key
    - `rating`: Rating value (1 to 5)
    - `comment`: Optional text field for additional feedback
    - `created_at`: Timestamp when the review was created
    - `updated_at`: Timestamp when the review was updated
    - `booking`: One-to-One relation with **Booking** (each booking can have one review)
    - `user`: Foreign Key to **User** (the user who wrote the review)

## Wireframes

Below are the wireframes for each major page of the Beard & Blade application. Each wireframe shows the general layout, navigation, and key elements of the respective page.

### Home Page Wireframe

![Home Page Wireframe](static/images/home_wire.png)

- **Purpose:** Introduces users to Beard & Blade with a hero section and prominent call-to-action button.
- **Layout Highlights:**
  - Navigation bar at the top.
  - Hero section with a background image, branding text, and "Book Now" button.
  - Footer connected at the bottom.

---

### Services Page Wireframe

![Services Page Wireframe](static/images/services_wire.png)

- **Purpose:** Displays a grid of available services (name, duration, price) with a "Book Now" option.
- **Layout Highlights:**
  - Navigation bar at the top.
  - Service cards arranged in rows, each showing essential information.
  - Footer connected at the bottom.

---

### About Page Wireframe

![About Page Wireframe](static/images/about_wire.png)

- **Purpose:** Provides background information on the establishment and head barber.
- **Layout Highlights:**
  - Navigation bar at the top.
  - Two sections showcasing images and descriptive text (one for the establishment, one for the barber).
  - Footer at the bottom for consistency.

---

### Login Page Wireframe

![Login Page Wireframe](static/images/login_wire.png)

- **Purpose:** Allows returning users to log into their accounts securely.
- **Layout Highlights:**
  - Navigation bar at the top.
  - Simple form for entering username and password.
  - "Log In" button styled in line with the site’s color scheme.
  - Footer connected at the bottom.

---

### Registration Page Wireframe

![Registration Page Wireframe](static/images/register_wire.png)

- **Purpose:** Lets new users create an account with username, email, and password fields.
- **Layout Highlights:**
  - Navigation bar at the top.
  - Form fields for username, email, password, and password confirmation.
  - "Sign Up" button in the site’s signature color.
  - Footer at the bottom to maintain site consistency.

## User Story & Admin Story

### User Stories

1. **Service Browsing & Booking**  
   **Story:** As a user, I want to browse the available services with clear details (name, duration, price) so that I can easily decide which service best fits my needs and book an appointment with minimal hassle.  
   **Implementation:**

   - Developed a `Service` model to store service details.
   - Created the `services.html` template to display services in a grid, each with a "Book Now" option.
   - Built the booking process in the `book_now` view, which validates input (e.g., ensuring the date is not in the past), calculates the required contiguous 15-minute timeslots, and reserves them using the `Booking` and `TimeSlot` models.
   - Utilized custom management commands (`timeslots.py` for generating timeslots and `completed.py` for marking bookings completed) to automate backend processes.

   **Screenshot:**  
   ![Service Browsing & Booking](static/images/service_user.png)

---

2. **Account Management**  
   **Story:** As a user, I want to create an account, log in, and manage my bookings and reviews so that I can track my appointment history, update my profile, and provide feedback after my appointments.  
   **Implementation:**

   - Implemented user registration using a custom `register` view that validates data and creates a new user.
   - Integrated Django’s built-in authentication for logging in and out using templates like `login.html`.
   - Developed the `profile.html` page to display the user’s current bookings (both upcoming and past) and reviews, with options to edit or cancel bookings and leave or update reviews.

   **Screenshot:**  
   ![Account Management](static/images/account_user.png)

---

3. **Review Submission**  
   **Story:** As a user, I want to leave reviews and ratings for completed bookings so that I can share my service experience and help guide other customers.  
   **Implementation:**

   - Designed a `Review` model with a one-to-one relationship to `Booking`, ensuring each booking can have only one review.
   - Created the `review_form.html` template with a star rating widget (leveraging the `star_ratings` package) and a comment field.
   - Implemented `create_review` and `edit_review` views to handle review submission and updates, ensuring proper validation and feedback.

   **Screenshot:**  
   ![Review Submission](static/images/editrev_user.png)

---

### Admin Stories

1. **Service & Booking Management**  
   **Story:** As an admin, I want to manage and update the service offerings so that the list of available services remains current, and view, confirm, cancel, or mark bookings as completed to ensure a smooth operational workflow.  
   **Implementation:**

   - Utilized the `Service` and `Booking` models to store and manage service details and booking data.
   - Customized the Django admin interface in `admin.py` with actions (e.g., confirm or decline bookings) to update booking statuses and associated timeslots.
   - Added filtering, search, and custom display options in the admin for efficient booking management.

   **Screenshot:**  
   ![Service & Booking Management](static/images/service&book_admin.png)

---

2. **User Reviews Moderation**  
   **Story:** As an admin, I want to manage user reviews—editing or removing them if necessary—to maintain the quality and reliability of customer feedback on the platform.  
   **Implementation:**

   - Integrated the `Review` model into the admin with a custom form that features a star rating widget.
   - Enabled filtering and searching of reviews by user, booking, or rating, making moderation straightforward.

   **Screenshot:**  
   ![User Reviews Moderation](static/images/reviewmod_admin.png)

---

3. **Operating Hours Setup**  
   **Story:** As an admin, I want to define and update the shop's operating hours so that the system can generate accurate timeslots for booking.  
   **Implementation:**

   - Created the `OpeningHours` model to store daily opening and closing times.
   - Leveraged these settings in the `timeslots.py` management command to generate 15-minute timeslots based on the defined operating hours.

   **Screenshot:**  
   ![Operating Hours Setup](static/images/operationhour_admin.png)

---

4. **Automated Task Scheduling**  
   **Story:** As an admin, I want to schedule automated tasks for generating timeslots and updating booking statuses to reduce manual intervention and keep the system up-to-date.  
   **Implementation:**
   - Configured `django-crontab` in `settings.py` to run the `timeslots` and `completed` management commands at scheduled intervals.
   - This automation ensures that future timeslots are generated daily and confirmed bookings are marked as completed when appropriate.

- **Generate Timeslots:**  
  This command generates 15-minute timeslots for upcoming days based on the shop's defined opening hours.
  ```bash
  python manage.py timeslots --days 7


  ```

## Mark Completed

This command checks for bookings whose end time has passed and updates their status to "completed". Use this command to manually update booking statuses if the automated cron job isn’t running.

``` bash python manage.py mark_completed ```

---

5. **Custom Admin Tools**
   **Story:** As an admin, I want access to custom admin tools—such as star rating widgets for reviews—to streamline administrative tasks and improve overall efficiency.
   **Implementation:**
   - Developed custom admin widgets (e.g., for star ratings in the `Review` model) to enhance usability.
   - Extended the admin interface to include additional filtering and searching options for better control over services, bookings, and reviews.

## Lighthouse Testing

We have tested every page of Beard & Blade using Google Lighthouse. All pages scored at least 85 and above across Performance, Accessibility, Best Practices, and SEO. The results confirm that our site is optimized for a fast, accessible, and user-friendly experience. All registration pages tested and passed.

**Lighthouse Test Screenshots:**

- **Home Page:**  
  ![Lighthouse Home Page](static/images/lighthouse_home.png)
  
- **Services Page:**  
  ![Lighthouse Services Page](static/images/lighthouse_services.png)
  
- **About Page:**  
  ![Lighthouse About Page](static/images/lighthouse_about.png)
  
- **Login Page:**  
  ![Lighthouse Login Page](static/images/lighthouse_account.png)
  
- **Registration Page:**  
  ![Lighthouse Registration Page](static/images/lighthouse_register.png)
  
- **Review Edit Page:**  
  ![Lighthouse Profile Page](static/images/lighthouse_reviewedit.png)

- **Review Page:**  
  ![Lighthouse Profile Page](static/images/lighthouse_review.png)

Each screenshot represents a successful Lighthouse report, demonstrating our commitment to high quality and efficient performance across the application.

## Manual Testing

### User Authentication and Account Management

- **Registration Flow:**  
  - **Test:** Completed new user registration by filling out username, email, password, and password confirmation fields.  
  - **Validation:** Checked for proper error messages for missing fields, mismatched passwords, and duplicate usernames.  
  - **Result:** Valid registrations succeeded and users were redirected to the login page with a success message.

- **Login Flow:**  
  - **Test:** Logged in with valid credentials and attempted login with invalid data.  
  - **Validation:** Verified that the password toggle worked correctly and that unauthenticated users were redirected appropriately when accessing restricted pages.  
  - **Result:** Login functioned as expected with clear error messages on invalid attempts.

- **Password Reset Flow:**  
  - **Test:** Initiated a password reset by submitting a registered email address and followed the reset link to set a new password.  
  - **Validation:** Confirmed that the email was sent (using Mailjet) and that the new password allowed successful login.  
  - **Result:** Password reset and change processes performed correctly with valid feedback.

### Booking and Timeslot Management

- **Service Booking:**  
  - **Test:** Booked a service by selecting a valid service, date, and start time.  
  - **Validation:** Verified that the booking process correctly computed the number of contiguous 15-minute timeslots required, reserved them, and updated the booking status ("pending", then "confirmed" upon confirmation).  
  - **Result:** Bookings were created and edited successfully; the correct timeslot allocation was enforced.

- **Timeslot Generation:**  
  - **Test:** Ran the `python manage.py timeslots --days 7` command to generate timeslots based on the shop's opening hours.  
  - **Validation:** Checked that timeslots were created for each day without duplicates and in the correct time increments.  
  - **Result:** Timeslot generation functioned as intended, providing sufficient availability for booking.

- **Booking Status Updates:**  
  - **Test:** Simulated past booking times and manually executed the `python manage.py mark_completed` command.  
  - **Validation:** Verified that bookings with end times in the past were correctly marked as "completed."  
  - **Result:** Bookings updated accurately upon manual execution of the command.

### Modal and UI Component Testing

- **"No Available Timeslots" Modal:**  
  - **Test:** Selected a date/time slot with no available timeslots to trigger the modal on the booking page.  
  - **Validation:** Checked that the modal displayed the correct message and that the "OK" button properly dismissed the modal.  
  - **Result:** Modal functionality worked smoothly, providing clear user feedback.

- **Review Deletion Confirmation Modal:**  
  - **Test:** Clicked the delete button for a review in the profile page, triggering the confirmation modal.  
  - **Validation:** Verified that the modal appeared with a confirmation prompt and that confirming the deletion successfully removed the review.  
  - **Result:** Review deletion modals operated as intended, ensuring proper user confirmation.

### Model and Data Validation

- **Booking Model Validations:**  
  - **Test:** Attempted to create bookings with non-contiguous or an incorrect number of timeslots.  
  - **Validation:** Confirmed that validations in the `Booking` model prevented invalid bookings and returned clear error messages.  
  - **Result:** Model-level validations enforced contiguous timeslot selection and correct booking durations.

- **Review Model Validations:**  
  - **Test:** Submitted reviews for completed bookings and attempted to submit duplicate reviews for the same booking.  
  - **Validation:** Ensured that the review model only accepted one review per booking and that the star rating widget captured ratings correctly.  
  - **Result:** Review submissions and validations performed as expected.

- **Authentication Middleware:**  
  - **Test:** Attempted access to restricted pages (e.g., booking and profile pages) while not logged in.  
  - **Validation:** Checked that unauthenticated users were redirected to the login page.  
  - **Result:** Authentication flow was secure and correctly enforced redirection.

### Summary

All manually tested features—including user registration, login, password reset, booking processes, timeslot generation, modal displays, and model validations—performed as expected. The application provides clear user feedback, robust error handling, and secure authentication, ensuring a smooth and reliable user experience.

## Known Bugs

- **Average Rating Issue:**  
  The average rating currently displays as "1" instead of calculating the average across all submitted ratings.

- **Rated Score Display Issue:**  
  After selecting a rating score, the "Rated" field shows "0" instead of reflecting the chosen or computed average score.

![Bug picture](static/images/bug.png)

- **Logout Confirmation Issue:**  
  When canceling on the logout confirmation ("Are you sure?") page, the user is unexpectedly logged out instead of staying logged in.

These issues are known and are under investigation for future fixes.


## References

- **Django Documentation:**  
  [Django Docs](https://docs.djangoproject.com/en/4.2/) – Official documentation for Django, covering topics like authentication, custom management commands, and deployment.

- **Django Authentication & Authorization:**  
  [Django Auth Documentation](https://docs.djangoproject.com/en/4.2/topics/auth/) – Details on user authentication, registration, and built-in views for login, logout, and password management.

- **Navbar Implementation:**  
  [Navbar Code Tutorial](https://www.youtube.com/watch?v=zOtxP7ahi4M) – YouTube tutorial for building a responsive navigation bar.

- **Log In Flow:**  
  [Log In Tutorial](https://www.youtube.com/watch?v=z-ITKWB7YyQ) – YouTube tutorial covering the login process using Django's authentication system.

- **Automated Management Commands:**  
  [Custom Management Commands](https://docs.djangoproject.com/en/4.2/howto/custom-management-commands/) – Official guide on creating and running Django management commands (e.g., timeslot generation and marking bookings completed).  
  [django-crontab Documentation](https://pypi.org/project/django-crontab/) – Information on scheduling cron jobs with Django.

- **Django Custom Management Commands Tutorial:**  
  [Writing custom Django management commands](https://docs.djangoproject.com/en/4.2/howto/custom-management-commands/) – Official Django documentation on creating and using custom management commands.

- **Django-Crontab Tutorial:**  
  [django-crontab Documentation](https://pypi.org/project/django-crontab/) – Official PyPI page for django-crontab with installation, configuration, and usage instructions.

- **Scheduling Cron Jobs in Django – Tutorial:**  
  [Using Django-Crontab to schedule tasks](https://simpleisbetterthancomplex.com/tutorial/2016/08/22/how-to-schedule-django-cron-jobs.html) – A practical guide on how to set up and manage cron jobs in Django using django-crontab.

- **Django Cron Jobs – Video Tutorial:**  
  [How to Setup Cron Jobs in Django](https://www.youtube.com/watch?v=QULW6SbF-FE) – A YouTube tutorial demonstrating how to configure and run cron jobs in a Django application using django-crontab.

- **Django Allauth:**  
  [django-allauth Documentation](https://django-allauth.readthedocs.io/en/latest/) – Comprehensive guide for third-party account management in Django.

- **Star Ratings Integration:**  
  [Django Star Ratings](https://github.com/wildfish/django-star-ratings) – GitHub repository for the star ratings package used for review submissions.

- **Email Integration in Django:**  
  [Django Email Documentation](https://docs.djangoproject.com/en/4.2/topics/email/) – Covers setting up email backends (e.g., Mailjet) for password resets and notifications.

- **Whitenoise for Static Files:**  
  [Whitenoise Documentation](http://whitenoise.evans.io/en/stable/) – Guide on serving static files efficiently in Django with Whitenoise.

- **Bootstrap Documentation:**  
  [Bootstrap Docs](https://getbootstrap.com/) – For front-end design and responsive layout elements.

- **Django Debug Toolbar:**  
  [Django Debug Toolbar](https://django-debug-toolbar.readthedocs.io/en/latest/) – A powerful tool for debugging and performance analysis in Django applications.

- **Wireframe Tools:**  
  [Wireframe.cc](https://wireframe.cc/) – A simple, free tool for creating low-fidelity wireframes.  
  [Pencil Project](https://pencil.evolus.vn/) – An open-source tool for creating mockups and wireframes.

- **Autopep8:**  
  [autopep8 on PyPI](https://pypi.org/project/autopep8/) – A tool that automatically formats Python code to conform to the PEP 8 style guide.

- **Additional Django Tutorials:**  
  [Real Python Django Tutorials](https://realpython.com/tutorials/django/) – Comprehensive tutorials covering various aspects of Django development.
