from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from metrics.models import HealthCalculator
from metrics.services import HealthCalculatorService


class Command(BaseCommand):
    help = 'Test BMR calculation for users'

    def add_arguments(self, parser):
        parser.add_argument('username', nargs='?', type=str, help='Username to test (optional)')

    def handle(self, *args, **options):
        username = options['username']
        
        if username:
            try:
                user = User.objects.get(username=username)
                self.test_user_bmr(user)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User "{username}" not found'))
        else:
            # Test all users
            users = User.objects.all()
            self.stdout.write(f'Testing BMR calculation for {users.count()} users...')
            
            for user in users:
                self.test_user_bmr(user)
                self.stdout.write('---')

    def test_user_bmr(self, user):
        self.stdout.write(f'User: {user.username}')
        
        # Get age
        age = None
        if hasattr(user, 'profile') and user.profile.date_of_birth:
            from datetime import date
            today = date.today()
            age = today.year - user.profile.date_of_birth.year - (
                (today.month, today.day) < (user.profile.date_of_birth.month, user.profile.date_of_birth.day)
            )
            self.stdout.write(f'  Age: {age}')
        else:
            self.stdout.write(self.style.WARNING('  No age available'))
        
        # Test BMR calculation with sample data
        weight_kg = 70.0
        height_cm = 170.0
        gender = 'male'
        
        if age:
            bmr = HealthCalculatorService.calculate_bmr(weight_kg, height_cm, age, gender)
            self.stdout.write(f'  BMR (age {age}): {bmr:.0f} kcal/day')
        else:
            # Test with default age
            default_age = 30
            bmr = HealthCalculatorService.calculate_bmr(weight_kg, height_cm, default_age, gender)
            self.stdout.write(f'  BMR (default age {default_age}): {bmr:.0f} kcal/day')
        
        # Test TDEE
        tdee = HealthCalculatorService.calculate_tdee(bmr, 'moderately_active')
        self.stdout.write(f'  TDEE: {tdee:.0f} kcal/day')
