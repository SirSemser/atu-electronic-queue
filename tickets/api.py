from django.db import transaction
from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status as drf_status

from .models import Ticket

import json, re
from pathlib import Path
from django.conf import settings


# ---------- helpers ----------
def load_cfg():
    p = Path(settings.BASE_DIR) / "static" / "config" / "config.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}

def pick_from(lst):
    return lst[0] if lst else None

def route_desk(ticket_data, cfg):
    d = (cfg or {}).get("desks", {}) or {}

    service = ticket_data.get("service")
    category = ticket_data.get("category") or ""
    track = ticket_data.get("track") or ""
    profile = ticket_data.get("profile") or ""

    if service == "online":
        return None

    if service == "consultation":
        if track == "design":
            return pick_from(d.get("design", []))
        if category == "foreign":
            return pick_from(d.get("foreign", []))
        if category == "master":
            return pick_from(d.get("master", []))
        if category == "army":
            return pick_from(d.get("army", []))
        return pick_from(d.get("default", []))

    if service in ("admission", "contest"):
        if profile == "creative":
            return pick_from(d.get("design", []))
        if category == "foreign":
            return pick_from(d.get("foreign", []))
        if category == "master":
            return pick_from(d.get("master", []))
        if category == "army":
            return pick_from(d.get("army", []))
        return pick_from(d.get("default", []))

    return pick_from(d.get("default", []))

def prefix_for_service(service):
    return {
        "consultation": "C",
        "admission": "A",
        "contest": "G",
        "online": "O",
    }.get(service, "T")

def next_number(prefix):
    last = (
        Ticket.objects
        .filter(number__startswith=f"{prefix}-")
        .order_by("-created_at")
        .first()
    )
    if not last or not last.number:
        return f"{prefix}-101"

    m = re.search(r"-(\d+)$", last.number)
    if not m:
        return f"{prefix}-101"

    n = int(m.group(1)) + 1
    return f"{prefix}-{n}"


# ---------- serializer ----------
class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = "__all__"
        read_only_fields = ("number", "desk", "status", "created_at")


# ---------- viewset ----------
class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all().order_by("-created_at")
    serializer_class = TicketSerializer
    permission_classes = [permissions.AllowAny]  # прототип (потом закроем)

    @transaction.atomic
    def perform_create(self, serializer):
        cfg = load_cfg()
        data = serializer.validated_data

        service = data.get("service")
        prefix = prefix_for_service(service)

        number = next_number(prefix)
        desk = route_desk(data, cfg)

        serializer.save(
            number=number,
            desk=desk,
            status="PENDING",
            is_online=(service == "online"),
        )

    # -----------------------
    # OPERATOR ACTIONS
    # -----------------------

    @action(detail=False, methods=["get"], url_path="pending")
    def pending(self, request):
        """GET /api/tickets/pending/?desk=3 -> список PENDING по desk"""
        desk = request.query_params.get("desk")
        qs = Ticket.objects.filter(status="PENDING")
        if desk:
            qs = qs.filter(desk=int(desk))
        qs = qs.order_by("created_at")
        return Response(TicketSerializer(qs, many=True).data)

    @action(detail=False, methods=["post"], url_path="next")
    @transaction.atomic
    def next_for_desk(self, request):
        """
        POST /api/tickets/next/  { "desk": 3 }
        Возьмёт самый ранний PENDING для desk и переведёт в ACCEPTED
        """
        desk = request.data.get("desk")
        if not desk:
            return Response({"detail": "desk required"}, status=drf_status.HTTP_400_BAD_REQUEST)

        # блокируем строку на время транзакции (чтобы 2 оператора не взяли один талон)
        t = (
            Ticket.objects
            .select_for_update(skip_locked=True)
            .filter(status="PENDING", desk=int(desk))
            .order_by("created_at")
            .first()
        )
        if not t:
            return Response({"detail": "no pending tickets"}, status=drf_status.HTTP_404_NOT_FOUND)

        t.status = "ACCEPTED"
        t.save(update_fields=["status"])
        return Response(TicketSerializer(t).data)

    @action(detail=True, methods=["post"], url_path="done")
    def done(self, request, pk=None):
        """POST /api/tickets/{id}/done/ -> DONE"""
        t = self.get_object()
        t.status = "DONE"
        t.save(update_fields=["status"])
        return Response(TicketSerializer(t).data)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        """POST /api/tickets/{id}/cancel/ -> CANCELLED"""
        t = self.get_object()
        t.status = "CANCELLED"
        t.save(update_fields=["status"])
        return Response(TicketSerializer(t).data)

    @action(detail=False, methods=["get"], url_path="board")
    def board(self, request):
        """
        GET /api/tickets/board/
        Возвращает текущие ACCEPTED по desk (по последнему принятому)
        """
        accepted = Ticket.objects.filter(status="ACCEPTED").order_by("-created_at")
        result = {}
        for t in accepted:
            if t.desk is None:
                continue
            if str(t.desk) not in result:
                result[str(t.desk)] = TicketSerializer(t).data
        return Response(result)
