import questionary
from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = 'Resets the data for a specific model in a selected app.'

    def handle(self, *args, **kwargs):
        # Let the user select the app
        app_name = self.select_app()

        # Let the user select the model
        model_name = self.select_model(app_name)

        # Destructive action confirmation: This will now appear at the end
        destructive_confirmation = questionary.select(
            "This is a destructive action. There is no going back. Do you want to reset the data for this model?",
            choices=["Yes, proceed", "No, cancel"]
        ).ask()

        if destructive_confirmation == "Yes, proceed":
            # Reset the data for the selected model
            self.reset_model_data(app_name, model_name)
            self.stdout.write(self.style.SUCCESS(f'Data for model {model_name} in app {app_name} has been reset.'))
        else:
            self.stdout.write(self.style.WARNING('Operation cancelled. Data not reset.'))

    def select_app(self):
        """Let the user select the app."""
        app_choices = [app.name for app in apps.get_app_configs()]
        app_choice = questionary.select(
            "Select an app whose model data you want to reset:",
            choices=app_choices
        ).ask()
        return app_choice

    def select_model(self, app_name):
        """Let the user select a model from a selected app."""
        app_config = apps.get_app_config(app_name)
        model_choices = [model.__name__ for model in app_config.get_models()]
        model_choice = questionary.select(
            f"Select a model in the app {app_name} to reset the data:",
            choices=model_choices
        ).ask()
        return model_choice

    def reset_model_data(self, app_name, model_name):
        """Reset the data for a specific model in a specific app."""
        try:
            model = apps.get_model(app_name, model_name)
            self.stdout.write(f'Resetting data for model {model_name} in app {app_name}...')
            self.clear_model_data(model)
            self.stdout.write(self.style.SUCCESS(f'Data for model {model_name} has been reset.'))
        except LookupError:
            self.stdout.write(self.style.ERROR(f"Model '{model_name}' in app '{app_name}' not found."))

    def clear_model_data(self, model):
        """Clear the data for the given model."""
        try:
            # Delete all objects in the model
            model.objects.all().delete()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to clear data for model {model.__name__}: {str(e)}"))
