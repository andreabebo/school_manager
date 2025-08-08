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
    
        return f"{self.nom_session} de {self.date_session}"

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
    sexe = models.CharField(max_length=20, choices=[
        ('M', 'Masculin'),
        ('F', 'Feminin'),
    ], default='M')
    
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
        


class Professeur(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE)
    age = models.DateField(auto_now_add=True)
    sexe = models.CharField(max_length=20, choices=[
        ('M', 'Masculin'),
        ('F', 'Feminin'),
    ], default='M')
    numero = models.CharField(max_length=15)  # Numéro de téléphone du professeur

    def __str__(self):
        return self.user.last_name+' '+self.user.first_name
    class Meta:
        ordering = ['user']
        verbose_name = "Professeur"
        verbose_name_plural ="Professeurs" 
        
        

class Matiere(models.Model):
    professeur = models.ForeignKey(Professeur, on_delete=models.CASCADE, related_name='matieres', null=True, blank=True)
    nom = models.CharField(max_length=100)
    unite_enseignement = models.CharField(max_length=100, default='UE1')
    coefficient = models.PositiveIntegerField(default=1)
    creneau_horaire = models.CharField(max_length=100)
    filiere = models.ForeignKey('Filiere', on_delete=models.CASCADE, related_name='matieres', default=1)
   
    bareme = models.PositiveIntegerField(default=20)  # fixe à 20 par défaut
    def __str__(self):
        return f"{self.nom} - {self.unite_enseignement} - {self.filiere.nom} - {self.coefficient} - {self.bareme} - {self.creneau_horaire} - {self.professeur.nom}"

    def __str__(self):
        return self.nom

class Salle(models.Model):
    nom = models.CharField(max_length=50)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.nom
    
class Filiere(models.Model):
    departement = models.CharField(max_length=200, null=True, blank=True)
    nom = models.CharField(max_length=100)
    montant_global = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Montant global de la filière")
    # NATURE_CHOICES déplacé dans PaiementScolarite
    active=models.BooleanField( default=True)
    
    @property
    def total_inscrit(self):
        inscrits = Student.objects.filter(filiere=self.pk).count()
        return inscrits
    
    def __str__(self):
        return self.nom

from django.utils import timezone

class EmploiDeTemps(models.Model):
    # ... vos autres champs ...
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, related_name='emplois_du_temps')
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True, blank=True, related_name='emplois_du_temps')
    date_debut = models.DateField()
    date_fin = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = "Emplois du temps"
        ordering = ['-date_debut', '-date_fin']
    
    def __str__(self):
        return f" {self.session.nom_session} ({self.filiere.nom}) ({self.date_debut} au {self.date_fin})"

class ActiviteJour(models.Model):
    JOURS_SEMAINE = [
        ('Lundi', 'Lundi'),
        ('Mardi', 'Mardi'),
        ('Mercredi', 'Mercredi'),
        ('Jeudi', 'Jeudi'),
        ('Vendredi', 'Vendredi'),
        ('Samedi', 'Samedi'),
    ]
    
    emploi_de_temps = models.ForeignKey(EmploiDeTemps, on_delete=models.CASCADE, related_name='activites')
    jour = models.CharField(max_length=10, choices=JOURS_SEMAINE)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='activites')
    professeur = models.ForeignKey(Professeur, on_delete=models.SET_NULL, null=True, blank=True, related_name='cours')
    salle = models.ForeignKey(Salle, on_delete=models.SET_NULL, null=True, blank=True, related_name='occupations')
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    
    class Meta:
        ordering = ['jour', 'heure_debut']
        verbose_name_plural = "Activités journalières"
    
    def __str__(self):
        return f"{self.jour} {self.heure_debut}-{self.heure_fin}: {self.matiere.nom}"
    
    def clean(self):
        if self.heure_debut >= self.heure_fin:
            raise ValidationError("L'heure de fin doit être après l'heure de début")
from django import forms
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
 

# Nouvelle classe Tranche liée à Filiere
class Tranche(models.Model):
    filiere = models.ForeignKey('Filiere', on_delete=models.CASCADE, related_name='tranches')
    nom = models.CharField(max_length=100)
    montant = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.nom} - {self.filiere.nom} ({self.montant} FCFA)"

class PaiementScolarite(models.Model):
    NATURE_CHOICES = [
        ("Espece", "Espèce"),
        ("Banque", "Banque"),
        ("OM/MOMO", "OM/MOMO"),
        ("Micro-finance", "Micro-finance"),
    ]
    nature_paiement = models.CharField(max_length=20, choices=NATURE_CHOICES, default="Espece", verbose_name="Nature du paiement")
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    filiere = models.ForeignKey('Filiere', on_delete=models.CASCADE, null=True, blank=True)
    session = models.ForeignKey('Session', on_delete=models.CASCADE, null=True, blank=True)
    tranche = models.ForeignKey('Tranche', on_delete=models.CASCADE)
    date_paiement = models.DateField()
    heure_paiement = models.TimeField()
    montant_verse = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def montant_restant(self):
        return self.filiere.montant_global - self.montant_verse

    @property
    def etat_scolarite(self):
        if self.montant_restant == 0:
            return "Soldé"
        else:
            return "Non soldé"

    def __str__(self):
        return f"Paiement de {self.student.user.get_full_name} le {self.date_paiement}"
    
# models.py
from django.db import models
from django.utils import timezone
class Stat(models.Model):
    session = models.ForeignKey('Session', on_delete=models.CASCADE, null=True, blank=True, related_name="stats")
    filiere = models.ForeignKey('Filiere', on_delete=models.CASCADE, null=True, blank=True, related_name="stats")
    
    # Champs de statistiques
    total_inscrits = models.PositiveIntegerField(default=0)
    total_hommes = models.PositiveIntegerField(default=0)
    total_femmes = models.PositiveIntegerField(default=0)
    total_reussite = models.PositiveIntegerField(default=0)
    
    date_calcul = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f'Stat: {self.session.nom_session} - {self.filiere.nom}'
    
    @property
    def pourcentage_reussite(self):
        if self.total_inscrits > 0:
            return round((self.total_reussite / self.total_inscrits) * 100, 2)
        return 0
    
    @property
    def pourcentage_hommes(self):
        if self.total_inscrits > 0:
            return round((self.total_hommes / self.total_inscrits) * 100, 2)
        return 0
    
    @property
    def pourcentage_femmes(self):
        if self.total_inscrits > 0:
            return round((self.total_femmes / self.total_inscrits) * 100, 2)
        return 0
    
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
class Note(models.Model):
    MENTION_CHOICES = [
        ('Excellent', 'Excellent'),
        ('Très bien', 'Très bien'),
        ('Bien', 'Bien'),
        ('Assez bien', 'Assez bien'),
        ('Passable', 'Passable'),
        ('Insuffisant', 'Insuffisant'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="notes")
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, null=True, blank=True, related_name="notes")
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name="notes")
    note_cc = models.FloatField(
        "Contrôle Continu", 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)]
    )
    note_sn = models.FloatField(
        "Session Normale", 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)]
    )
    moyenne = models.FloatField("Note finale", null=True, blank=True)
    mention = models.CharField(max_length=50, choices=MENTION_CHOICES, blank=True, null=True)
    date_creation = models.DateField(default=timezone.now) 
    fichier_pdf = models.FileField(upload_to='notes/pdf/', blank=True, null=True)
    valide = models.BooleanField(default=False)
    delivre_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="notes_delivrees")
    
    class Meta:
        unique_together = ('student', 'matiere')
    
    @property
    def coefficient(self):
        """Récupère dynamiquement le coefficient de la matière"""
        return self.matiere.coefficient if self.matiere else 1

    def save(self, *args, **kwargs):
        # Calcul de la moyenne pondérée si les deux notes sont fournies
        if self.note_cc is not None and self.note_sn is not None:
            note_cc = self.note_cc * 0.3
            note_sn = self.note_sn * 0.7
            self.moyenne = round(note_cc + note_sn, 2)
            
            # Attribution automatique de la mention
            if self.moyenne >= 18:
                self.mention = 'Excellent'
            elif self.moyenne >= 16:
                self.mention = 'Très bien'
            elif self.moyenne >= 14:
                self.mention = 'Bien'
            elif self.moyenne >= 12:
                self.mention = 'Assez bien'
            elif self.moyenne >= 10:
                self.mention = 'Passable'
            else:
                self.mention = 'Insuffisant'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student} - {self.matiere} - {self.moyenne or 'N/A'}"

class ListePresence(models.Model):
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, related_name="listes_presence")
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name="listes_presence")
    professeur = models.ForeignKey(Professeur, on_delete=models.CASCADE, related_name="listes_presence")
    date_cours = models.DateField(default=timezone.now)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    commentaire = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-date_cours']
    
    def __str__(self):
        return f"Présence - {self.matiere.nom} - {self.filiere.nom} - {self.date_cours}"

class PresenceEtudiant(models.Model):
    liste = models.ForeignKey(ListePresence, on_delete=models.CASCADE, related_name='presences')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='presences')
    est_present = models.BooleanField(default=True)
    justification = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        unique_together = ('liste', 'student')
        
        constraints = [
            models.UniqueConstraint(
                fields=['liste', 'student'], 
                name='unique_student_per_list'
            )
        ]
    
    def __str__(self):
        return f"{self.student} - {'Présent' if self.est_present else 'Absent'}"

class Attestation(models.Model):
    TYPE_CHOICES = [
        ('scolarite', 'Attestation de scolarité'),
        ('reussite', 'Attestation de réussite'),
        ('stage', 'Attestation de stage'),
        ('fin_etudes', 'Attestation de fin d\'études'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attestations")
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, related_name="attestations")
    type_attestation = models.CharField(max_length=30, choices=TYPE_CHOICES)
    date_emission = models.DateField(auto_now_add=True)
    texte_personnalise = models.TextField(blank=True, null=True)
    fichier_pdf = models.FileField(upload_to='attestations/', blank=True, null=True)
    delivre_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="attestations_delivrees")
    valide_jusqua = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.student} - {self.get_type_attestation_display()} - {self.filiere.nom}"






# Forum de discussion éducatif
from django.urls import reverse

class Sujet(models.Model):
    titre = models.CharField(max_length=200)
    description = models.TextField()
    filiere = models.ForeignKey('Filiere', on_delete=models.CASCADE, related_name='sujets')
    auteur = models.ForeignKey('User', on_delete=models.CASCADE, related_name='sujets')
    date_creation = models.DateTimeField(auto_now_add=True)
    fichier = models.FileField(upload_to='documents/', blank=True, null=True)

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('sujet_detail', args=[str(self.id)])

class SujetCommentaire(models.Model):
    sujet = models.ForeignKey(Sujet, on_delete=models.CASCADE, related_name='commentaires')
    auteur = models.ForeignKey('User', on_delete=models.CASCADE)
    texte = models.TextField()
    date_pub = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.auteur.get_full_name()} - {self.sujet.titre}"

class Notification(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='notifications')
    sujet = models.ForeignKey(Sujet, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    lu = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notif pour {self.user.email} - {self.sujet.titre}"



    