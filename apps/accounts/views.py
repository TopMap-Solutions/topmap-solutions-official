from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model

User = get_user_model()


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user:
            login(request, user)
            return redirect("parcel_dashboard")

        return render(request, "login.html", {"error": "Incorrect email or password"})

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("accounts:login")

