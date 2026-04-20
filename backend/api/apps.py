from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        import threading
        import time

        def run_deadline_check():
            while True:
                time.sleep(3600)
                from django.core.management import call_command
                call_command('check_deadlines')

        t = threading.Thread(target=run_deadline_check, daemon=True)
        t.start()