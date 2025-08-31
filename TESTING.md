# 🧪 Testing – FoodHub  

Once the FoodHub application was complete, thorough testing was performed to ensure the platform works as expected across all user roles (customers, restaurant owners, riders, operators) and that errors are properly handled.  

---

## 👥 User Testing & Feedback  

The application was tested in a controlled environment by different types of users:  

- **Customers** placed orders, viewed carts, and tracked deliveries.  
- **Restaurant Owners** added restaurants and menus, and managed incoming orders.  
- **Riders** updated delivery statuses from *ASSIGNED → PICKED_UP → DELIVERED*.  
- **Operators** assigned riders to orders and exported data to CSV.  

Feedback improvements applied:  
- Empty states were clarified (e.g., "No restaurants available").  
- Flash messages were added after important actions.  
- Navbar links were restricted per role (customers don’t see owner/operator pages).  
- Mobile burger menu colors fixed for visibility.  

---

## ✅ Functional Tests  

| Feature                   | Action                          | Expected Result                                      | Actual Result           |
|----------------------------|---------------------------------|------------------------------------------------------|-------------------------|
| Signup/Login               | Register & login user           | User account created, login redirects to home         | ✅ Works as expected    |
| Customer – Cart Add        | Add dish to cart                | Dish appears in cart with correct quantity/price      | ✅ Works as expected    |
| Checkout                   | Place order                     | Order created, success message shown                  | ✅ Works as expected    |
| Customer – My Orders       | View orders list                | Orders listed with status and items                   | ✅ Works as expected    |
| Order Tracking             | Open order detail               | Status and timeline update automatically (AJAX poll)  | ✅ Works as expected    |
| Restaurant Owner – Menu    | Add dish with photo             | Dish visible with name, price, and image              | ✅ Works as expected    |
| Owner – Orders             | Mark order as "Ready"           | Status updates, customer sees change                  | ✅ Works as expected    |
| Operator – Assign          | Assign rider to delivery        | Rider attached, delivery created                      | ✅ Works as expected    |
| Rider – Update Status      | Change ASSIGNED → DELIVERED     | Status advances, events logged, email sent            | ✅ Works as expected    |
| CSV Export                 | Export orders in date range     | CSV file downloads with correct rows                  | ✅ Works as expected    |
| Empty States               | No restaurants/orders/deliveries| Info alert displayed instead of blank page            | ✅ Works as expected    |
| Navbar Permissions         | Login as customer/owner/rider   | Each role sees only relevant links                    | ✅ Works as expected    |

---

## 🌐 Browser & Device Testing  

- **Browsers tested**:  
  - Chrome  
  - Firefox  
  - Safari  

- **Devices tested**:  
  - Desktop (macOS, Windows)  
  - iOS (iPhone)  
  - Android (Samsung Galaxy)  

The site is fully responsive with Bootstrap 5 and custom CSS. Burger menu tested on mobile screens.  

---

## 📧 Email & Notifications  

- **Development**: Console backend used to print emails.  
- **Production (Heroku)**: SMTP via config vars.  

Test results:  
- Customers receive email notifications when order/delivery status changes.  
- Flash messages appear consistently (success/error/info).  

---

## 🧾 Input Validation  

- Forms (signup, login, profile, checkout) all validated.  
- Dish/restaurant creation requires required fields.  
- Invalid actions (e.g., rider trying to deliver unassigned order) blocked with error.  
- Cart prevents negative or zero quantities.  

---

## 📊 Automated Tests  

Django unit tests were written for:  

- **Deliveries**: status flow, rider permissions, operator assignment.  
- **Orders**: customer tracking JSON endpoint, owner-only permissions.  
- **Exports**: CSV generation.  

Command:  
```bash
python manage.py test
