from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'Accounts'

    def ready(self):
        from . import signals
    
    # def ready(self):
    #     from .signals  import update_user_type

        
