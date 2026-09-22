from .models import Config


def app_config(request):
    my_app_config = Config.objects.first()
    return {
        'app_config': my_app_config
    }
