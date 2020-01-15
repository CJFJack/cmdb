from django.apps import AppConfig


class MyworkflowsConfig(AppConfig):
    name = 'myworkflows'

    def ready(self):
        import myworkflows.signals
