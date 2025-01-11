import questionary
from django.core.management.base import BaseCommand
from django.apps import apps
from typing import List

class Command(BaseCommand):
    help = "Resets specified models by clearing their data."

    def handle(self, *args, **options) -> None:
        """Main entry point for the command."""
        self.stdout.write("Fetching all available models...")

        models = [
            f"{model._meta.app_label}.{model.__name__}"
            for model in apps.get_models()
        ]

        if not models:
            self.stdout.write("No models found in the project.")
            return

        selected_models = questionary.checkbox(
            "Select models to reset (use space to select, enter to confirm):",
            choices=models,
        ).ask()

        if not selected_models:
            self.stdout.write("No models selected. Exiting.")
            return

        self.stdout.write("Starting to reset selected models...")

        for model_path in selected_models:
            app_label, model_name = model_path.split('.')
            model = apps.get_model(app_label, model_name)
            
            self.stdout.write(f"Resetting model: {app_label}.{model_name}")
            
            model.objects.all().delete()
            self.stdout.write(f"Model {app_label}.{model_name} reset successfully.")

        self.stdout.write("Selected models have been reset.")
