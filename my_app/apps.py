from django.apps import AppConfig


class MyAppConfig(AppConfig):
    name = 'my_app'

def ready(self):
        # models.py ထဲက signal တွေကို app စပွင့်ကတည်းက အသက်သွင်းထားလိုက်တာဖြစ်ပါတယ်
        import my_app.models
