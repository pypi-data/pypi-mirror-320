import questionary
from django.core.management.base import BaseCommand
from django.db import models
from django.apps import apps
from django.db import connection
import os
from typing import Optional

class Command(BaseCommand):
    help = 'Resets primary keys for a specific model in a selected app by deleting data and resetting primary keys.'

    def handle(self, *args, **kwargs) -> None:
        """Main entry point for the command."""
        app_name = self.select_app()
        try:
            model_name = self.select_model(app_name)
        except AttributeError:
            self.stdout.write(self.style.ERROR("Cancelled by user"))
            return
        
        if model_name is None:
            self.stdout.write(self.style.ERROR("Cancelled by user"))
            return
        
        destructive_confirmation = questionary.select(
            "This is a destructive action. There is no going back. Do you want to reset the primary key for this model?",
            choices=["Yes, proceed", "No, cancel"]
        ).ask()

        if destructive_confirmation == "Yes, proceed":
            self.reset_specific_model_primary_key(app_name, model_name)
            self.stdout.write(self.style.SUCCESS(f'Primary key for model {model_name} in app {app_name} has been reset.'))
        else:
            self.stdout.write(self.style.WARNING('Operation cancelled. Primary key not reset.'))

    def select_app(self) -> str:
        """Let the user select an app."""
        app_choices = []
        for app in apps.get_app_configs():
            app_path = app.path
            for root, dirs, files in os.walk(app_path):
                if 'apps.py' in files:
                    app_choices.append(app.name)
                    break
        app_choice = questionary.select(
            "Select an app whose model's primary key you want to reset:",
            choices=app_choices
        ).ask()
        return app_choice

    def select_model(self, app_name: str) -> Optional[str]:
        """Let the user select a model from a selected app."""
        try:
            app_config = apps.get_app_config(app_name)
        except LookupError:
            app_config = apps.get_app_config(app_name.split('.')[-1])
        model_choices = [model.__name__ for model in app_config.get_models()]
        model_choice = questionary.select(
            f"Select a model in the app {app_name} to reset the primary key:",
            choices=model_choices
        ).ask()
        return model_choice

    def reset_specific_model_primary_key(self, app_name: str, model_name: str) -> None:
        """Reset primary key for a specific model in a specific app."""
        try:
            model = apps.get_model(app_name, model_name)
            self.stdout.write(f'Resetting primary key for model {model_name} in app {app_name}...')
            self.reset_primary_key_for_model(model)
            self.stdout.write(self.style.SUCCESS(f'Primary key for model {model_name} has been reset.'))
        except LookupError:
            app_name = app_name.split('.')[-1]
            model = apps.get_model(app_name, model_name)
            self.stdout.write(f'Resetting primary key for model {model_name} in app {app_name}...')
        try: 
            self.reset_primary_key_for_model(model)
            self.stdout.write(self.style.SUCCESS(f'Primary key for model {model_name} has been reset.'))
        except LookupError as e:
            self.stdout.write(self.style.ERROR(f"Failed to find model {model_name} in app {app_name}: {str(e)}"))

    def reset_primary_key_for_model(self, model: models.Model) -> None:
        """Reset the primary key for a given model."""
        try:
            primary_key_field = model._meta.pk
            if isinstance(primary_key_field, models.AutoField):
                table_name = model._meta.db_table
                cursor = connection.cursor()
                cursor.execute(f"ALTER SEQUENCE {table_name}_{primary_key_field.attname}_seq RESTART WITH 1;")
                cursor.close()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to reset primary key for model {model.__name__}: {str(e)}"))
