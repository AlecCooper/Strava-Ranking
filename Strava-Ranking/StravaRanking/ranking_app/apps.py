from django.apps import AppConfig

class RankingAppConfig(AppConfig):
    name = 'ranking_app'

    def ready(self):
        import ranking_app.signals

