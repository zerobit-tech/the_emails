from django.apps import AppConfig


class EmailsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'the_emails'

    def ready(self) -> None:
        import the_emails.agents