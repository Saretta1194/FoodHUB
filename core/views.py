from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from restaurants.models import Restaurant
from orders.models import Order
import csv


def home(request):

    restaurants = Restaurant.objects.filter(is_active=True)[:3]
    return render(request, "core/home.html", {"restaurants": restaurants})


def operator_assign(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    User = get_user_model()
    riders = User.objects.filter(is_staff=True)  

    if request.method == "POST":
        rider_id = request.POST.get("rider")
        if rider_id:
            rider = get_object_or_404(User, pk=rider_id)
            order.rider = rider
            order.save()
            return redirect("deliveries:operator_queue")

    return render(request, "deliveries/operator_assign.html", {
        "order": order,
        "riders": riders,
    })


def export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="orders.csv"'
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
