from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.shortcuts import get_object_or_404


from .forms import RestaurantForm
from .models import Restaurant
from menu.models import Dish


class OwnerMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Ensures the user is logged in and is the owner for object-level views.
    For list/create, test_func returns True for any authenticated user.
    """

    def test_func(self):
        obj = getattr(self, "object", None)
        if obj is None:
            # Allow access to list/create for authenticated users
            return self.request.user.is_authenticated
        return obj.owner == self.request.user

    def handle_no_permission(self):
        # Optionally customize (default redirects to login for LoginRequiredMixin)
        return super().handle_no_permission()


class OwnerRestaurantListView(OwnerMixin, ListView):
    model = Restaurant
    template_name = "restaurants/owner_list.html"
    context_object_name = "restaurants"
    paginate_by = 10

    def get_queryset(self):
        return Restaurant.objects.filter(owner=self.request.user).order_by(
            "-created_at"
        )


class RestaurantCreateView(OwnerMixin, CreateView):
    model = Restaurant
    form_class = RestaurantForm
    template_name = "restaurants/form.html"
    success_url = reverse_lazy("restaurants:owner_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RestaurantUpdateView(OwnerMixin, UpdateView):
    model = Restaurant
    form_class = RestaurantForm
    template_name = "restaurants/form.html"
    success_url = reverse_lazy("restaurants:owner_list")

    def get_queryset(self):
        # Important: prevent editing others' restaurants
        return Restaurant.objects.filter(owner=self.request.user)


class RestaurantDeleteView(OwnerMixin, DeleteView):
    model = Restaurant
    template_name = "restaurants/confirm_delete.html"
    success_url = reverse_lazy("restaurants:owner_list")

    def get_queryset(self):
        return Restaurant.objects.filter(owner=self.request.user)


class RestaurantListView(ListView):
    model = Restaurant
    template_name = "restaurants/public_list.html"
    context_object_name = "restaurants"
    paginate_by = 12

    def get_queryset(self):
        return Restaurant.objects.filter(is_active=True).order_by("name")


class RestaurantDetailView(DetailView):
    model = Restaurant
    template_name = "restaurants/public_detail.html"
    context_object_name = "restaurant"

    def get_object(self, queryset=None):
        # Only show active restaurants
        return get_object_or_404(
            Restaurant, pk=self.kwargs["pk"], is_active=True
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Only available dishes, sorted by category -> name
        dishes = Dish.objects.filter(
            restaurant=self.object, available=True
        ).order_by("category", "name")
        ctx["dishes"] = dishes
        return ctx
