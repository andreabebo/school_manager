def unread_notifications(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, lu=False).count()
    else:
        count = 0
    return {'unread_notifications': count}

from .models import Notification, Filiere

def filieres(request):
    return {'filieres': Filiere.objects.filter(active=True)}
