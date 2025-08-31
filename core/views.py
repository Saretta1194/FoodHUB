from django.shortcuts import render
from django.http import HttpResponse
from restaurants.models import Restaurant
from orders.models import Order  # importa il modello giusto
import csv


def home(request):

    restaurants = Restaurant.objects.filter(is_active=True)[:3]
    return render(request, "core/home.html", {"restaurants": restaurants})


def operator_assign(request, order_id):

    pass


def export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        'attachment; filename="orders.csv"'
    )
    writer = csv.writer(response)
    writer.writerow(
        [
            "order_id",
            "user",
            "restaurant",
            "status",
            "created_at",
            "total_amount",
        ]
    )

    for order in Order.objects.all():
        writer.writerow(
            [
                order.id,
                order.user.username,
                order.restaurant.name,
                order.status,
                order.created_at.strftime("%Y-%m-%d %H:%M"),
                float(order.total_amount),
            ]
        )

    return response


def about(request):
    return render(request, "core/about.html")


def shipping(request):
    return render(request, "core/shipping.html")


def contact(request):
    return render(request, "core/contact.html")


def privacy(request):
    return render(request, "core/privacy.html")


def terms(request):
    return render(request, "core/terms.html")
