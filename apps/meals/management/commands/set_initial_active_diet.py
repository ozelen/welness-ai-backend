from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from meals.models import Diet


class Command(BaseCommand):
    help = 'Set the first diet as active for users who don\'t have an active diet'

    def handle(self, *args, **options):
        users_without_active_diet = User.objects.filter(
            diet__is_active=False
        ).distinct()

        for user in users_without_active_diet:
            first_diet = Diet.objects.filter(user=user).first()
            if first_diet:
                first_diet.is_active = True
                first_diet.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Set diet "{first_diet.name}" as active for user {user.username}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully set initial active diets')
        )
