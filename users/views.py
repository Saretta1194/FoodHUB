from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UserProfileForm


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, "Welcome to FoodHub! Your account has been created."
            )
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "users/signup.html", {"form": form})


@login_required
def my_profile(request):
    profile = request.user.profile  # garantito dai signals
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("my_profile")
    else:
        form = UserProfileForm(instance=profile)

    return render(
        request,
        "users/my_profile.html",
        {
            "form": form,
            "profile": profile,
        },
    )
