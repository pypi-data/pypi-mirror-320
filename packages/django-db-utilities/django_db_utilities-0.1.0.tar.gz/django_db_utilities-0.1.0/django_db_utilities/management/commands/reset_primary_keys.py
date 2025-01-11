import questionary
from django.core.management.base import BaseCommand
from django.db import models
from django.apps import apps
from django.db import connection

class Command(BaseCommand):
    help = 'Resets primary keys for a specific model in a selected app by deleting data and resetting primary keys.'

    def handle(self, *args, **kwargs):
        # Let the user select the app
        app_name = self.select_app()

        # Let the user select the model
        model_name = self.select_model(app_name)

        # Destructive action confirmation: This will now appear at the end
        destructive_confirmation = questionary.select(
            "This is a destructive action. There is no going back. Do you want to reset the primary key for this model?",
            choices=["Yes, proceed", "No, cancel"]
        ).ask()

        if destructive_confirmation == "Yes, proceed":
            # Reset the primary key for the selected model
            self.reset_specific_model_primary_key(app_name, model_name)
            self.stdout.write(self.style.SUCCESS(f'Primary key for model {model_name} in app {app_name} has been reset.'))
        else:
            self.stdout.write(self.style.WARNING('Operation cancelled. Primary key not reset.'))

    def select_app(self):
        """Let the user select an app."""
        app_choices = [app.name for app in apps.get_app_configs()]
        app_choice = questionary.select(
            "Select an app whose model's primary key you want to reset:",
            choices=app_choices
        ).ask()
        return app_choice

    def select_model(self, app_name):
        """Let the user select a model from a selected app."""
        app_config = apps.get_app_config(app_name)
        model_choices = [model.__name__ for model in app_config.get_models()]
        model_choice = questionary.select(
            f"Select a model in the app {app_name} to reset the primary key:",
            choices=model_choices
        ).ask()
        return model_choice

    def reset_specific_model_primary_key(self, app_name, model_name):
        """Reset primary key for a specific model in a specific app."""
        try:
            model = apps.get_model(app_name, model_name)
            self.stdout.write(f'Resetting primary key for model {model_name} in app {app_name}...')
            self.reset_primary_key_for_model(model)
            self.stdout.write(self.style.SUCCESS(f'Primary key for model {model_name} has been reset.'))
        except LookupError:
            self.stdout.write(self.style.ERROR(f"Model '{model_name}' in app '{app_name}' not found."))

    def reset_primary_key_for_model(self, model):
        """Reset the primary key for a given model."""
        try:
            # Identify the primary key field (usually 'id')
            primary_key_field = model._meta.pk
            if isinstance(primary_key_field, models.AutoField):
                table_name = model._meta.db_table
                cursor = connection.cursor()
                # Reset the auto-increment value of the primary key to 1
                cursor.execute(f"ALTER SEQUENCE {table_name}_{primary_key_field.attname}_seq RESTART WITH 1;")
                cursor.close()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to reset primary key for model {model.__name__}: {str(e)}"))
