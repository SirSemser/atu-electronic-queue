from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Ticket


@login_required
def dashboard(request):
    username = request.user.username

    # operator3 → 3
    if username.startswith("operator"):
        try:
            desk_number = int(username.replace("operator", ""))
        except:
            desk_number = None
    else:
        desk_number = None

    tickets = Ticket.objects.filter(desk=desk_number, status="PENDING")

    return render(request, "operator/dashboard.html", {
        "tickets": tickets,
        "desk": desk_number
    })
