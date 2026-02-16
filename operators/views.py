import csv
from datetime import datetime

from config.utils import is_enabled

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST, require_GET

from tickets.models import Ticket
from .models import OperatorProfile, OperatorLog


# -------------------------
# RU/KZ labels
# -------------------------
SERVICE_LABELS = {
    "ru": {
        "consultation": "Консультация",
        "admission": "Поступление",
        "contest": "Грант конкурс",
        "online": "Онлайн поступление",
    },
    "kz": {
        "consultation": "Кеңес алу",
        "admission": "Оқуға түсу",
        "contest": "Грант конкурсы",
        "online": "Онлайн өтініш",
    }
}

CATEGORY_LABELS = {
    "ru": {
        "after11": "После 11 класса",
        "afterCollege": "После колледжа",
        "foreign": "Иностранец",
        "master": "Магистратура/Докторантура",
        "masters": "Магистратура/Докторантура",
        "army": "Военный",
    },
    "kz": {
        "after11": "11 сыныптан кейін",
        "afterCollege": "Колледжден кейін",
        "foreign": "Шетел азаматы",
        "master": "Магистратура/Докторантура",
        "masters": "Магистратура/Докторантура",
        "army": "Әскер",
    }
}

STATUS_LABELS = {
    "ru": {
        "PENDING": "Ожидает",
        "ACCEPTED": "Вызван",
        "DONE": "Завершён",
        "CANCELLED": "Отменён"
    },
    "kz": {
        "PENDING": "Күтуде",
        "ACCEPTED": "Шақырылды",
        "DONE": "Аяқталды",
        "CANCELLED": "Бас тартылды"
    },
}


def get_lang(request):
    lang = request.GET.get("lang")
    if lang in ("ru", "kz"):
        request.session["op_lang"] = lang
    return request.session.get("op_lang", "ru")


def t_service(service, lang):
    return SERVICE_LABELS.get(lang, {}).get(service, service or "")


def t_category(cat, lang):
    return CATEGORY_LABELS.get(lang, {}).get(cat, cat or "")


def t_status(st, lang):
    return STATUS_LABELS.get(lang, {}).get(st, st or "")


def _is_ajax(request):
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def _deny(request, ru_msg: str, kz_msg: str, status_code=403):
    msg = f"RU: {ru_msg} | KZ: {kz_msg}"
    if _is_ajax(request):
        return JsonResponse({"error": msg}, status=status_code)
    messages.error(request, msg)
    return redirect("operator_dashboard")


def log_action(request, profile: OperatorProfile, action: str, ticket: Ticket = None, meta: dict = None):
    OperatorLog.objects.create(
        operator=request.user,
        desk=profile.desk,
        action=action,
        ticket_number=(ticket.number if ticket else None),
        meta=(meta or {}),
    )


def _get_profile(request):
    try:
        return request.user.operator_profile
    except OperatorProfile.DoesNotExist:
        return None


def _flags_for_operator():
    return {
        "call_next": is_enabled("operator.call_next", True),
        "set_status": is_enabled("operator.set_status", True),
        "download_logs": is_enabled("operator.download_logs", True),
        "profile_edit": is_enabled("operator.profile_edit", True),
        "password_change": is_enabled("operator.password_change", True),
        "autorefresh": is_enabled("operator.autorefresh", True),
    }


# -------------------------
# Dashboard
# -------------------------
@login_required
def operator_dashboard(request):
    profile = _get_profile(request)
    if not profile:
        return render(request, "operator/no_profile.html")

    lang = get_lang(request)
    flags = _flags_for_operator()

    current = Ticket.objects.filter(
        desk=profile.desk,
        status="ACCEPTED"
    ).order_by("created_at").first()

    tickets = Ticket.objects.filter(
        desk=profile.desk,
        status="PENDING"
    ).order_by("created_at")

    for t in tickets:
        t.service_label = t_service(t.service, lang)
        t.category_label = t_category(t.category, lang)
        t.status_label = t_status(t.status, lang)

    if current:
        current.service_label = t_service(current.service, lang)
        current.category_label = t_category(current.category, lang)
        current.status_label = t_status(current.status, lang)

    log_action(request, profile, "VIEW", meta={"lang": lang})

    return render(request, "operator/dashboard.html", {
        "operator": request.user,
        "desk": profile.desk,
        "tickets": tickets,
        "current": current,
        "lang": lang,
        "flags": flags,   # ✅ важно для шаблона
    })


# -------------------------
# Actions
# -------------------------
@login_required
@require_POST
@transaction.atomic
def operator_call_next(request):
    profile = _get_profile(request)
    if not profile:
        return redirect("operator_dashboard")

    if not is_enabled("operator.call_next", True):
        return _deny(request, "Вызов следующего отключён админом.", "Келесіні шақыру әкімшімен өшірілген.")

    current = Ticket.objects.select_for_update().filter(
        desk=profile.desk,
        status="ACCEPTED"
    ).order_by("created_at").first()

    if current:
        return _deny(
            request,
            "Уже есть вызванный талон. Сначала завершите/отмените его.",
            "Шақырылған талон бар. Алдымен аяқтаңыз/болдырмаңыз.",
            status_code=409
        )

    t = Ticket.objects.select_for_update().filter(
        desk=profile.desk,
        status="PENDING"
    ).order_by("created_at").first()

    if not t:
        return _deny(request, "Нет талонов в очереди.", "Кезекте талон жоқ.", status_code=404)

    t.status = "ACCEPTED"
    t.save(update_fields=["status"])

    log_action(request, profile, "CALL_NEXT", ticket=t, meta={"to": "ACCEPTED"})

    if _is_ajax(request):
        return JsonResponse({"ok": True, "ticket": t.number})

    messages.success(request, f"RU: Вызван {t.number}. | KZ: {t.number} шақырылды.")
    return redirect("operator_dashboard")


@login_required
@require_POST
@transaction.atomic
def operator_set_status(request, ticket_id: int, new_status: str):
    profile = _get_profile(request)
    if not profile:
        return redirect("operator_dashboard")

    if not is_enabled("operator.set_status", True):
        return _deny(request, "Смена статуса отключена админом.", "Статусты өзгерту әкімшімен өшірілген.")

    allowed = {"PENDING", "ACCEPTED", "DONE", "CANCELLED"}
    if new_status not in allowed:
        return _deny(request, "Неверный статус.", "Қате статус.", status_code=400)

    t = get_object_or_404(
        Ticket.objects.select_for_update(),
        id=ticket_id,
        desk=profile.desk
    )

    if new_status == "ACCEPTED":
        other_current = Ticket.objects.select_for_update().filter(
            desk=profile.desk,
            status="ACCEPTED"
        ).exclude(id=t.id).first()
        if other_current:
            return _deny(
                request,
                "Уже есть вызванный талон (ACCEPTED).",
                "Шақырылған талон бар (ACCEPTED).",
                status_code=409
            )

    old = t.status
    t.status = new_status
    t.save(update_fields=["status"])

    log_action(request, profile, "SET_STATUS", ticket=t, meta={"from": old, "to": new_status})

    if _is_ajax(request):
        return JsonResponse({"ok": True, "ticket": t.number, "from": old, "to": new_status})

    messages.success(request, f"RU: Статус {t.number}: {old} → {new_status}. | KZ: {t.number}: {old} → {new_status}.")
    return redirect("operator_dashboard")


# -------------------------
# Profile
# -------------------------
@login_required
def operator_profile(request):
    profile = _get_profile(request)
    if not profile:
        return render(request, "operator/no_profile.html")

    if not is_enabled("operator.profile_edit", True):
        return _deny(request, "Профиль отключён админом.", "Профиль әкімшімен өшірілген.")

    if request.method == "POST":
        email = (request.POST.get("email") or "").strip()
        request.user.email = email
        request.user.save(update_fields=["email"])
        log_action(request, profile, "PROFILE_UPDATE", meta={"email": email})
        messages.success(request, "RU: Email сохранён. | KZ: Email сақталды.")
        return redirect("operator_profile")

    return render(request, "operator/profile.html", {
        "operator": request.user,
        "desk": profile.desk,
        "email": request.user.email or "",
    })


@login_required
def operator_password_change(request):
    profile = _get_profile(request)
    if not profile:
        return render(request, "operator/no_profile.html")

    if not is_enabled("operator.password_change", True):
        return _deny(request, "Смена пароля отключена админом.", "Құпиясөзді өзгерту әкімшімен өшірілген.")

    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            log_action(request, profile, "PASSWORD_CHANGE")
            messages.success(request, "RU: Пароль изменён. | KZ: Құпиясөз өзгертілді.")
            return redirect("operator_dashboard")
        else:
            messages.error(request, "RU: Ошибка смены пароля. | KZ: Құпиясөзді өзгерту қатесі.")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "operator/password.html", {"form": form})


# -------------------------
# AJAX queue
# -------------------------
@require_GET
@login_required
def operator_queue_json(request):
    profile = _get_profile(request)
    if not profile:
        return JsonResponse({"error": "no profile"}, status=403)

    if not is_enabled("operator.autorefresh", True):
        return JsonResponse({"error": "autorefresh disabled"}, status=403)

    lang = get_lang(request)

    current = Ticket.objects.filter(
        desk=profile.desk,
        status="ACCEPTED"
    ).order_by("created_at").first()

    pending = Ticket.objects.filter(
        desk=profile.desk,
        status="PENDING"
    ).order_by("created_at")

    def to_dict(t: Ticket):
        return {
            "id": t.id,
            "number": t.number,
            "service": t.service,
            "service_label": t_service(t.service, lang),
            "category": t.category,
            "category_label": t_category(t.category, lang),
            "fio": t.fio,
            "phone": t.phone,
            "status": t.status,
            "status_label": t_status(t.status, lang),
            "desk": t.desk,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }

    return JsonResponse({
        "lang": lang,
        "desk": profile.desk,
        "current": to_dict(current) if current else None,
        "pending": [to_dict(x) for x in pending],
    })


# -------------------------
# Logs CSV
# -------------------------
@login_required
def operator_logs_csv(request):
    profile = _get_profile(request)
    if not profile:
        return redirect("operator_dashboard")

    if not is_enabled("operator.download_logs", True):
        return _deny(request, "Скачивание журнала отключено админом.", "Журналды жүктеу әкімшімен өшірілген.")

    qs = OperatorLog.objects.filter(operator=request.user).order_by("-created_at")[:5000]
    log_action(request, profile, "DOWNLOAD_LOGS", meta={"scope": "self"})
    return _logs_as_csv(qs, filename=f"operator_{request.user.username}_logs.csv")


@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def admin_logs_csv(request):
    username = (request.GET.get("username") or "").strip()
    desk = (request.GET.get("desk") or "").strip()

    qs = OperatorLog.objects.all().order_by("-created_at")

    if username:
        qs = qs.filter(operator__username=username)
    if desk.isdigit():
        qs = qs.filter(desk=int(desk))

    qs = qs[:20000]
    return _logs_as_csv(qs, filename="operators_logs.csv")


def _logs_as_csv(qs, filename: str):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(["created_at", "operator", "desk", "action", "ticket_number", "meta"])

    for row in qs:
        writer.writerow([
            row.created_at.strftime("%Y-%m-%d %H:%M:%S") if row.created_at else "",
            getattr(row.operator, "username", ""),
            row.desk,
            row.action,
            row.ticket_number or "",
            row.meta or {},
        ])
    return response
