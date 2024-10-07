from django import forms
from django.contrib.auth.forms  import UserCreationForm
from .models import Cours, Commentaire, EmploiDeTemps, Professeur, Salle, Matiere, ActiviteJour

class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        strip="False",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    password2 = forms.CharField(
        label="Password confirmation",
        strip="False",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    
    class Meta (UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("password1", "password2")




class CoursForm(forms.ModelForm):
    class Meta:
        model = Cours
        fields = ['titre', 'contenu', 'fichier']
        widgets = {
            'texte' : forms.Textarea(attrs={
                'class': 'form-control text-dark'
            }),
        }

class CommentaireForm(forms.ModelForm):
    class Meta:
        model = Commentaire
        fields = ['texte']
        widgets = {
            'texte' : forms.Textarea(attrs={
                'class': 'form-control text-dark'
            }),
        }

class EmploiDeTempsForm(forms.ModelForm):
    class Meta:
        model = EmploiDeTemps
        fields = ('filiere', 'date_debut', 'date_fin')
        widgets = {
           "date_debut" : forms.DateInput(attrs={
                'class': ' text-dark'
            }),
           "date_fin" : forms.DateInput(attrs={
                'class': ' text-dark'
            }),
        }

class ActiviteJourForm(forms.ModelForm):
    class Meta:
        model = ActiviteJour
        fields = ['matiere', 'jour', 'heure_debut', 'heure_fin']
        widgets = {
           "heure_debut" : forms.TimeInput(attrs={
                'class': ' text-dark'
            }),
           "heure_fin" : forms.TimeInput(attrs={
                'class': ' text-dark'
            }),
        }







   
        
        
        



