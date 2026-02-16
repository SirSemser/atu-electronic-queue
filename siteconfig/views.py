from django.shortcuts import render, redirect
from django.contrib import messages
from config.utils import is_enabled

def app_online(request):
    if not is_enabled("service.online", True):
        messages.error(request, "RU: Онлайн-поступление отключено админом. | KZ: Онлайн өтініш әкімшімен өшірілген.")
        return redirect("/app/service/")
    return render(request, "app/online.html")
