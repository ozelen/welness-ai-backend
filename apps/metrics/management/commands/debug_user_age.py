from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import date


class Command(BaseCommand):
    help = 'Debug user age calculation issues'

    def add_arguments(self, parser):
        parser.add_argument('username', nargs='?', type=str, help='Username to check (optional)')

    def handle(self, *args, **options):
        username = options['username']
        
        if username:
            try:
                user = User.objects.get(username=username)
                self.check_user_age(user)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User "{username}" not found'))
        else:
            # Check all users
            users = User.objects.all()
            self.stdout.write(f'Checking {users.count()} users...')
            
            for user in users:
                self.check_user_age(user)
                self.stdout.write('---')

    def check_user_age(self, user):
        self.stdout.write(f'User: {user.username} ({user.email})')
        
        # Check if user has profile
        if hasattr(user, 'profile'):
            self.stdout.write(f'  ✓ Has profile')
            
            if user.profile.date_of_birth:
                self.stdout.write(f'  ✓ Has date of birth: {user.profile.date_of_birth}')
                
                # Calculate age
                today = date.today()
                age = today.year - user.profile.date_of_birth.year - (
                    (today.month, today.day) < (user.profile.date_of_birth.month, user.profile.date_of_birth.day)
                )
                self.stdout.write(f'  ✓ Calculated age: {age}')
            else:
                self.stdout.write(self.style.WARNING('  ✗ No date of birth set'))
        else:
            self.stdout.write(self.style.ERROR('  ✗ No profile found'))
