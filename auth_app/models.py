from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from .managers import UserManager
from datetime import datetime

def get_profil_picture_filepath(self, filename):
    return f'images/profile/{self.pk}/{filename}'

class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="Email", null=False, blank=False)
    username = None
    profile_image = models.ImageField(
        verbose_name = "photo de profil", null=True, blank=True, upload_to=get_profil_picture_filepath
    )
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

class Session(models.Model):
    date_session = models.DateTimeField()
    nom_session = models.CharField(max_length=250, null=True, blank=True)
    def __str__(self):
    
        return f"Session de {self.date_session}"

class Student(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='students')
    age =  models.DateField(
        verbose_name="Date de naissance", null=True, blank=True
    )
    matricule = models.CharField(
        verbose_name="matricule", max_length=250, null=True, blank=True
    )
    ville = models.CharField(
        verbose_name="Résidence", max_length=250, null=True, blank=True 
    )
    diplome = models.CharField(
        verbose_name="Dernier diplome obtenu", max_length=250, null=True, blank=True
    )
    filiere = models.ForeignKey('Filiere', related_name="student", on_delete=models.CASCADE)
    contact = models.CharField(
        verbose_name="Numéro de téléphone", max_length=250, null=True, blank=True
    )
    
    def save(self, *args, **kwargs):
        mat = ""
        
        fullname_letters = self.user.get_full_name().split(' ')
        if len(fullname_letters) >= 2:
            mat+=fullname_letters[0][0].upper()
            mat+=fullname_letters[1][0].upper()
        
        studentAge = datetime.strptime(self.age, '%Y-%m-%d')
        age = studentAge.strftime('%y')
        mat+=age
        mat+=self.user.date_joined.strftime('%y')
        
        self.matricule = mat
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.user.first_name+' '+self.user.last_name
    class Meta:
        ordering = ['user']
        verbose_name = "Etudiant"
        verbose_name_plural ="Etudiants"    
        

class Cours(models.Model):
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    fichier = models.FileField(upload_to='documents/', blank=True, null=True)
    date_pub = models.DateTimeField(auto_now_add=True)
    heure_pub = models.TimeField(auto_now_add=True)
    auteur = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.titre
    class Meta:
        verbose_name = "Cours"
        verbose_name_plural ="Cours"  


class Commentaire(models.Model):
    cours = models.ForeignKey(Cours, related_name="commentaires", on_delete=models.CASCADE)
    auteur = models.ForeignKey(User, on_delete=models.CASCADE)
    texte = models.TextField()
    date_pub = models.DateTimeField(auto_now_add=True)
    heure_pub = models.TimeField(auto_now_add=True)

    def __str__(self):
        return f"Commentaire de {self.auteur} sur {self.cours.titre}"
    class Meta:
         verbose_name = "Commentaire"
         verbose_name_plural ="Commentaires"  
   
    
class Professeur(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE)
    age = models.DateField(auto_now_add=True)
    specialite = models.CharField(max_length=100)
    numero = models.CharField(max_length=15)  # Numéro de téléphone du professeur

    def __str__(self):
        return self.user.last_name+' '+self.user.first_name
    class Meta:
        ordering = ['user']
        verbose_name = "Professeur"
        verbose_name_plural ="Professeurs" 

class Matiere(models.Model):
    nom = models.CharField(max_length=100)
    cours = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

class Salle(models.Model):
    nom = models.CharField(max_length=50)

    def __str__(self):
        return self.nom
    
class Filiere(models.Model):
    departement = models.CharField(max_length=200, null=True, blank=True)
    nom = models.CharField(max_length=100)
    active=models.BooleanField( default=True)
    
    @property
    def total_inscrit(self):
        inscrits = Student.objects.filter(filiere=self.pk).count()
        return inscrits
    
    def __str__(self):
        return self.nom

class EmploiDeTemps(models.Model):
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE)
    date_debut = models.DateField()
    date_fin = models.DateField()
    

    def __str__(self):
        return f'Emploi de temps {self.filiere.nom} du {self.date_debut} au {self.date_fin}'

class ActiviteJour(models.Model):
    emploi_de_temps = models.ForeignKey(EmploiDeTemps, on_delete=models.CASCADE)
    matiere = models.CharField(max_length=250)
    jour = models.CharField(max_length=10)  # Ex: Lundi, Mardi, etc.
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()

    def __str__(self):
        return f'{self.matiere} ({self.jour})'


class Parametre(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fond_ecran = models.ImageField(upload_to='fonds_ecran/', blank=True, null=True)
    langue = models.CharField(max_length=20, choices=[
        ('fr', 'Français'),
        ('en', 'Anglais'),
        ('es', 'Espagnol'),
    ], default='fr')

    def __str__(self):
        return f"Paramètres de {self.user.username}"
 
class PaiementScolarite(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    tranche = models.FloatField()
    date_paiement = models.DateField()
    heure_paiement = models.TimeField()
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    montant_verse = models.DecimalField(max_digits=10, decimal_places=2)
    

    @property
    def montant_restant(self):
        return self.montant_total - self.montant_verse
    
    @property
    def etat_scolarite(self):
        if self.montant_restant == 0:
            return "Soldé"
        else:
            return "Non soldé"


    def __str__(self):
        return f"Paiement de {self.student.user.get_full_name} le {self.date_paiement}"
    
class Stat(models.Model):
    date_session = models.DateField()
    nom_session = models.CharField(max_length=200, null=True, blank=True)
    inscrits = models.FloatField()
    

    def __str__(self):
        return f'Stat {self.date_session} du {self.inscrits} au {self.nom_session}'

    
    