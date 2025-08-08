from django.contrib import admin
from .models import Student, User, Professeur, Salle, Matiere, PaiementScolarite, ActiviteJour, Stat, EmploiDeTemps, Filiere, Session
# Register your models here.

admin.site.register(User)
admin.site.register(Student)
## admin.site.register(Cours)
## admin.site.register(Commentaire)
admin.site.register(Professeur)
admin.site.register(Matiere)
admin.site.register(Salle)
admin.site.register(PaiementScolarite)
admin.site.register(Stat)
admin.site.register(ActiviteJour)
admin.site.register(Filiere)
admin.site.register(Session)
# admin.site.register(EmploiDeTemps)
@admin.register(EmploiDeTemps)
class EmploiDeTempsAdmin(admin.ModelAdmin):
    list_display = ('filiere', 'session', 'date_debut', 'date_fin')
    list_filter = ('filiere', 'session')
    search_fields = ('filiere__nom', 'session__nom_session')
