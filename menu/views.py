from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .models import Dish
from .forms import DishForm
from restaurants.models import Restaurant


class OwnerDishMixin(LoginRequiredMixin):
    model = Dish
    form_class = DishForm
    template_name = "menu/dish_form.html"
    success_url = reverse_lazy("restaurants:owner_list")

    def get_queryset(self):
        return Dish.objects.filter(restaurant__owner=self.request.user)

    def get_restaurant(self):
        # Recupera il ristorante: da URL (quando crei/listi) oppure dall'oggetto (quando editi/cancelli)
        if hasattr(self, "object") and self.object is not None:
            return self.object.restaurant
        return get_object_or_404(
            Restaurant,
            pk=self.kwargs.get("restaurant_id"),
            owner=self.request.user,
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["restaurant"] = self.get_restaurant()   # 🔹 Qui aggiungiamo sempre restaurant al context
        return ctx

    def form_valid(self, form):
        if not getattr(form.instance, "restaurant_id", None):
            form.instance.restaurant = self.get_restaurant()
        messages.success(self.request, "Dish saved successfully!")
        return super().form_valid(form)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Dish deleted successfully!")
        return super().delete(request, *args, **kwargs)

    model = Dish
    form_class = DishForm
    template_name = "menu/dish_form.html"
    success_url = reverse_lazy("restaurants:owner_list")  # redirect back to owner restaurants

    def get_queryset(self):
        # Only dishes from restaurants owned by the user
        return Dish.objects.filter(restaurant__owner=self.request.user)

    def form_valid(self, form):
        # Link the dish to the correct restaurant (passed via URL)
        restaurant = get_object_or_404(Restaurant, pk=self.kwargs["restaurant_id"], owner=self.request.user)
        form.instance.restaurant = restaurant
        messages.success(self.request, "Dish saved successfully!")
        return super().form_valid(form)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Dish deleted successfully!")
        return super().delete(request, *args, **kwargs)


class DishListView(OwnerDishMixin, ListView):
    template_name = "menu/dish_list.html"
    context_object_name = "dishes"

    def get_queryset(self):
        restaurant = get_object_or_404(Restaurant, pk=self.kwargs["restaurant_id"], owner=self.request.user)
        return restaurant.dishes.all().order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["restaurant"] = get_object_or_404(Restaurant, pk=self.kwargs["restaurant_id"], owner=self.request.user)
        return context


class DishCreateView(OwnerDishMixin, CreateView):
    pass


class DishUpdateView(OwnerDishMixin, UpdateView):
    pass


class DishDeleteView(OwnerDishMixin, DeleteView):
    template_name = "menu/dish_confirm_delete.html"
