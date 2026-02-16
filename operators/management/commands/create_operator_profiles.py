from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from operators.models import OperatorProfile


class Command(BaseCommand):
    help = "Create OperatorProfile for operator1..operator25 with desks 1..25"

    def handle(self, *args, **options):
        User = get_user_model()
        created = 0
        updated = 0
        skipped = 0

        for i in range(1, 26):
            username = f"operator{i}"

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Skip: {username} not found"))
                skipped += 1
                continue

            profile, was_created = OperatorProfile.objects.get_or_create(
                user=user,
                defaults={"desk": i},
            )

            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created profile: {username} -> desk {i}"))
            else:
                # если уже есть профиль — синхронизируем desk
                if profile.desk != i:
                    profile.desk = i
                    profile.save(update_fields=["desk"])
                    updated += 1
                    self.stdout.write(self.style.SUCCESS(f"Updated profile: {username} -> desk {i}"))
                else:
                    skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done. created={created}, updated={updated}, skipped={skipped}"
        ))
