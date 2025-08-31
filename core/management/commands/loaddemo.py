from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.db import transaction
from restaurants.models import Restaurant
from menu.models import Dish
from decimal import Decimal


class Command(BaseCommand):
    help = "Load demo data: users, restaurants, dishes"

    @transaction.atomic
    def handle(self, *args, **options):
        # Users
        owner, _ = User.objects.get_or_create(
            username="owner1", defaults={"email": "owner1@example.com"}
        )
        if not owner.has_usable_password():
            owner.set_password("pass123")
            owner.save()

        customer, _ = User.objects.get_or_create(
            username="customer1", defaults={"email": "customer1@example.com"}
        )
        if not customer.has_usable_password():
            customer.set_password("pass123")
            customer.save()

        staff, _ = User.objects.get_or_create(
            username="operator",
            defaults={"email": "operator@example.com", "is_staff": True},
        )
        if not staff.has_usable_password():
            staff.set_password("pass123")
            staff.is_staff = True
            staff.save()

        rider_group, _ = Group.objects.get_or_create(name="rider")
        rider, _ = User.objects.get_or_create(
            username="rider1", defaults={"email": "rider1@example.com"}
        )
        if not rider.has_usable_password():
            rider.set_password("pass123")
            rider.save()
        rider.groups.add(rider_group)

        # Restaurants
        r1, _ = Restaurant.objects.get_or_create(
            owner=owner,
            name="Pizzeria Bella Napoli",
            defaults={
                "address": "Via Roma 12, Torino",
                "opening_hours": "11:30-22:30",
                "is_active": True,
                "description": "Traditional Neapolitan pizza with fresh ingredients.",
            },
        )
        r2, _ = Restaurant.objects.get_or_create(
            owner=owner,
            name="Sushi Koi",
            defaults={
                "address": "Corso Milano 25, Milano",
                "opening_hours": "12:00-23:00",
                "is_active": True,
                "description": "Fresh sushi, sashimi, and japanese bowls.",
            },
        )
        r3, _ = Restaurant.objects.get_or_create(
            owner=owner,
            name="Burger Craft",
            defaults={
                "address": "Via Firenze 8, Bologna",
                "opening_hours": "11:00-23:30",
                "is_active": True,
                "description": "Handmade burgers, fries and shakes.",
            },
        )

        # Dishes (some examples)
        dishes_r1 = [
            ("Margherita", "Tomato, mozzarella, basil", Decimal("6.50"), True),
            ("Diavola", "Spicy salami, tomato, mozzarella", Decimal("8.50"), True),
            (
                "Quattro Formaggi",
                "Mozzarella, gorgonzola, grana, provola",
                Decimal("9.00"),
                True,
            ),
            ("Marinara", "Tomato, garlic, oregano", Decimal("5.50"), True),
            (
                "Prosciutto e Funghi",
                "Cooked ham, mushrooms, mozzarella",
                Decimal("9.50"),
                True,
            ),
        ]
        dishes_r2 = [
            ("Sushi Mix 12pz", "Nigiri + Maki + Uramaki", Decimal("15.90"), True),
            ("Sashimi Salmone 10pz", "Fresh salmon slices", Decimal("13.50"), True),
            (
                "Uramaki California 8pz",
                "Crabstick, avocado, mayo",
                Decimal("7.90"),
                True,
            ),
            ("Ramen Shoyu", "Chicken broth, noodles, egg", Decimal("10.50"), True),
            ("Gyoza 6pz", "Pork dumplings", Decimal("5.90"), True),
        ]
        dishes_r3 = [
            ("Classic Burger", "Beef patty, lettuce, tomato", Decimal("9.00"), True),
            ("Cheese Burger", "Beef, cheddar, pickles", Decimal("9.50"), True),
            ("Bacon Burger", "Beef, bacon, cheddar", Decimal("10.50"), True),
            ("Veggie Burger", "Falafel patty, hummus, veggies", Decimal("9.00"), True),
            ("Fries", "Crispy french fries", Decimal("3.50"), True),
        ]

        for name, desc, price, available in dishes_r1:
            Dish.objects.get_or_create(
                restaurant=r1,
                name=name,
                defaults={"description": desc, "price": price, "available": available},
            )
        for name, desc, price, available in dishes_r2:
            Dish.objects.get_or_create(
                restaurant=r2,
                name=name,
                defaults={"description": desc, "price": price, "available": available},
            )
        for name, desc, price, available in dishes_r3:
            Dish.objects.get_or_create(
                restaurant=r3,
                name=name,
                defaults={"description": desc, "price": price, "available": available},
            )

        self.stdout.write(self.style.SUCCESS("Demo data loaded."))
        self.stdout.write("Logins:")
        self.stdout.write("  owner1 / pass123")
        self.stdout.write("  customer1 / pass123")
        self.stdout.write("  operator (staff) / pass123")
        self.stdout.write("  rider1 (rider group) / pass123")
