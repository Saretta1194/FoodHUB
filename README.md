 [FOODHUB logo] (https://res.cloudinary.com/dvfo3mqdj/image/upload/v1756631210/foodh_ac3ilg.png)

A full-stack Django web application for online food ordering and delivery management.  
Customers can browse restaurants, add dishes to their cart, and place orders.  
Restaurant owners manage menus and incoming orders.  
Operators assign deliveries to riders, who update delivery statuses.  


The deployed project live link is [HERE](https://foodhub-f53dab9dc3ee.herokuapp.com/)  

---

## 📌 Contents  

- [Introduction](#introduction)  
- [Project Goals](#project-goals)  
- [User Goals](#user-goals)  
- [Site Owner Goals](#site-owner-goals)  
- [Pre-Development Planning](#pre-development-planning)  
- [Development](#development)  
- [Features](#features)  
- [User Stories Implemented](#user-stories-implemented)  
- [Technologies Used](#technologies-used)  
- [Testing](#testing)  
- [Validation](#validation)  
- [Deployment](#deployment)  
- [Bugs](#bugs)  
- [Credits](#credits)  

---

## Introduction  

**FoodHub** is a food ordering and delivery platform inspired by services like JustEat.  
It allows different types of users (customers, restaurant owners, riders, and operators) to interact with the platform:  

- Customers can browse restaurants, place orders, and track deliveries in real time.  
- Restaurant owners manage menus and update the status of orders.  
- Riders are assigned to deliveries and update statuses (picked up → delivered).  
- Operators manage delivery assignments and monitor workflows.  

---

## Project Goals  

- Provide an intuitive platform for ordering food online.  
- Allow restaurant owners to manage their business digitally.  
- Streamline delivery logistics with clear rider assignments.  
- Notify customers of order progress with emails and tracking.  
- Ensure a responsive, mobile-friendly interface.  

---

## User Goals  

- Easily sign up and log in.  
- Browse restaurants and see menus with pictures, prices, and descriptions.  
- Add dishes to a cart, adjust quantities, and check out.  
- Receive confirmation messages and email updates on status changes.  
- Track orders and delivery progress in real time.  

---

## Site Owner Goals  

- Provide a professional, functional food ordering platform.  
- Ensure reliable status tracking (Created → Preparing → Ready → Delivered).  
- Support multiple roles with different permissions (owner, operator, rider, customer).  
- Offer a polished UI/UX with a modern design.  
- Deploy securely to production (Heroku + PostgreSQL + Cloudinary).  

---

## Pre-Development Planning  

- **Wireframes** designed for restaurants, orders, and rider views.  
- **User stories** defined (A1,A2,B1,B2,B3,C1, C2, D1, D3, E1, E2, UI/UX).  
- **Database models** created for Restaurants, Dishes, Orders, Deliveries.  
- **Flow diagrams** for order lifecycle (cart → checkout → status transitions).  

---

## Development  

- Django framework used for models, views, and templates.  
- Bootstrap 5 + custom CSS for responsive UI.  
- PostgreSQL database (Heroku).  
- Cloudinary for media storage (restaurant/dish images).  
- Crispy Forms for styled forms.  
- WhiteNoise for static file handling in production.  
- Automated tests with Django TestCase.  

---

## Features  

### 🛒 Customer  
- Browse restaurants and menus.  
- Add items to cart and checkout.  
- Track order + delivery in real time.  

### 🍴 Restaurant Owner  
- Create and edit restaurant profile.  
- Add dishes with photos, prices, descriptions.  
- Manage incoming orders and update statuses.  

### 🚴 Rider  
- View assigned deliveries.  
- Update delivery status (picked up → delivered).  

### 🧑‍💼 Operator  
- Assign riders to deliveries.  
- Monitor overall delivery flow.  

### 🔔 Notifications  
- Flash messages after key actions (order placed, status updated).  
- Email notifications on order/delivery status changes.  

### 🎨 UI/UX Polish  
- Custom color palette (#A76545, #FFA55D, #FFDF88, #ACC572).  
- Responsive navbar with logo.  
- Cards for restaurants and dishes.  
- Empty state alerts with Bootstrap.  
- Pagination for lists.  

---

## User Stories Implemented  
- **A1**: User registration
- **A2**: Profile management
- **B1**: Restaurant profile
- **B2**: Dish CRUD
- **B3**: Public view
- **C1/C2**: Customers can place and track orders.  
- **D1**: Operator can assign riders.  
- **D3**: Customer can track delivery timeline.  
- **E1**: Notifications on status change (flash + email).  
- **E2**: Operator can export orders to CSV.  
- **UI/UX**: Navbar, footer, alerts, crispy forms, responsive layout.  

---

## Technologies Used  

- **Backend**: Python, Django  
- **Database**: PostgreSQL (Heroku)  
- **Frontend**: Bootstrap 5, Crispy Forms, Custom CSS  
- **Media**: Cloudinary  
- **Deployment**: Heroku + Gunicorn + WhiteNoise  
- **Version Control**: GitHub  

---

## Testing  

The project has been tested with:  

- Django unit tests (`python manage.py test`).  
- Manual end-to-end testing (signup → order → assignment → delivery).  
- Mobile responsiveness testing (Chrome DevTools).  
- Browser compatibility (Chrome, Firefox, Safari).  

---

## Validation  

- **HTML/CSS** checked via W3C validators.  
- **Python code** checked via Flake8/CI Linter.  
- **Accessibility** tested with Lighthouse.  

---

## Deployment  

- Hosted on Heroku with PostgreSQL.  
- Media served via Cloudinary.  
- Static files handled by WhiteNoise.  
- Deployment steps:  
  - Push code to GitHub.  
  - Connect Heroku to GitHub repo.  
  - Set config vars (`SECRET_KEY`, `DATABASE_URL`, `CLOUDINARY_URL`, `EMAIL_*`).  
  - Deploy branch.  

---

## Bugs  

- Fixed login redirect loop by configuring `LOGIN_URL`.  
- Adjusted navbar to display correct links per role (customer/owner/rider).  
- Fixed crispy forms rendering on signup/profile pages.  
- Fixed delivery status flow to block invalid transitions.  

---

## Credits  

- **Code Institute**: Django walkthrough project as base inspiration.  
- **Bootstrap**: Responsive design framework.  
- **Cloudinary Docs**: Media hosting integration.  
- **Heroku Docs**: Deployment setup.  
- **Slack community + mentor**: Guidance and debugging help.  
- FoodHub branding and design inspired by services like JustEat.  

---
