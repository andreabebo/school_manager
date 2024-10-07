from django.contrib import admin
from .models import Student, User, Cours, Commentaire,Professeur, Salle, Matiere, PaiementScolarite, ActiviteJour, Stat, EmploiDeTemps, Filiere, Session
# Register your models here.

admin.site.register(User)
admin.site.register(Student)
admin.site.register(Cours)
admin.site.register(Commentaire)
admin.site.register(Professeur)
admin.site.register(Matiere)
admin.site.register(Salle)
admin.site.register(PaiementScolarite)
admin.site.register(Stat)
admin.site.register(EmploiDeTemps)
admin.site.register(ActiviteJour)
admin.site.register(Filiere)
admin.site.register(Session)
# admin.site.register(EmploiDeTemps)
