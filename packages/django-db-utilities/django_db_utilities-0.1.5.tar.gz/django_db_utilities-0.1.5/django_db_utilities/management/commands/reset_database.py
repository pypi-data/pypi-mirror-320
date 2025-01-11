import questionary
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Resets the database by running migrations and clearing data'

    def handle(self, *args, **kwargs) -> None:
        """Main entry point for the command."""
        confirmation = questionary.select(
            "Are you sure you want to reset the database? This will remove all data.",
            choices=["Yes", "No"]
        ).ask()

        if confirmation == "Yes":
            destructive_confirmation = questionary.select(
                "This is a destructive action. There is no going back. Do you want to proceed?",
                choices=["Yes, proceed", "No, cancel"]
            ).ask()

            if destructive_confirmation == "Yes, proceed":
                self.stdout.write('Resetting database...')
                connection.close()  # Close the current database connection
                self.stdout.write(self.style.SUCCESS('Database has been reset.'))
            else:
                self.stdout.write(self.style.WARNING('Operation cancelled. Database not reset.'))
        else:
            self.stdout.write(self.style.WARNING('Operation cancelled. Database not reset.'))
