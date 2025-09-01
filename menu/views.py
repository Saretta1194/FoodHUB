from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect

from .models import Dish
from .forms import DishForm
from restaurants.models import Restaurant


class OwnerDishMixin(LoginRequiredMixin):
    model = Dish
    form_class = DishForm
    template_name = "menu/dish_form.html"
    success_url = None

    def get_queryset(self):
        return Dish.objects.filter(restaurant__owner=self.request.user)

    def get_restaurant(self):
        if getattr(self, "object", None) is not None:
            return self.object.restaurant
        return get_object_or_404(
            Restaurant,
            pk=self.kwargs.get("restaurant_id"),
            owner=self.request.user,
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["restaurant"] = self.get_restaurant()
        return ctx

    def form_valid(self, form):
        if not getattr(form.instance, "restaurant_id", None):
            form.instance.restaurant = self.get_restaurant()
        messages.success(self.request, "Dish saved successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        restaurant = self.get_restaurant()
        return reverse(
            "menu:dish_list",
            kwargs={"restaurant_id": restaurant.id},
        )

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Dish deleted successfully!")
        return super().delete(request, *args, **kwargs)


class DishListView(OwnerDishMixin, ListView):
    template_name = "menu/dish_list.html"
    context_object_name = "dishes"

    def get_queryset(self):
        restaurant = self.get_restaurant()
        return restaurant.dishes.all().order_by("name")


class DishCreateView(OwnerDishMixin, CreateView):
    pass


class DishUpdateView(OwnerDishMixin, UpdateView):
    pass


class DishDeleteView(OwnerDishMixin, DeleteView):
    template_name = "menu/dish_confirm_delete.html"

    def post(self, request, *args, **kwargs):
        """
        handle the POST manually to avoid the behavior of FormMixin,
        which can leave the page at 200. Here, we guarantee the redirect (302).
        """
        self.object = self.get_object()
        restaurant = self.object.restaurant
        self.object.delete()
        messages.success(self.request, "Dish deleted successfully!")
        return redirect("menu:dish_list", restaurant_id=restaurant.id)
