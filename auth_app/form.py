from django import forms
from .models import Filiere, Tranche
from django.contrib.auth.forms  import UserCreationForm
from .models import  EmploiDeTemps, Salle, Matiere, ActiviteJour, Note

# Forum
from .models import Sujet, SujetCommentaire

class FiliereForm(forms.ModelForm):
    class Meta:
        model = Filiere
        fields = ['departement', 'nom', 'montant_global', 'active']
        widgets = {
            'departement': forms.TextInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'montant_global': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_montant_global(self):
        montant = self.cleaned_data.get('montant_global')
        if montant is not None and montant < 0:
            raise forms.ValidationError("Le montant global ne peut pas être négatif.")
        return montant

class TrancheForm(forms.ModelForm):
    class Meta:
        model = Tranche
        fields = ['nom', 'montant']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def clean_montant(self):
        montant = self.cleaned_data.get('montant')
        if montant is not None and montant < 0:
            raise forms.ValidationError("Le montant de la tranche ne peut pas être négatif.")
        return montant

TrancheFormSet = forms.inlineformset_factory(
    Filiere, Tranche,
    form=TrancheForm,
    extra=1,
    can_delete=True
)
from .models import PaiementScolarite, Tranche, Student, Filiere, Session

class PaiementScolariteForm(forms.ModelForm):
    class Meta:
        model = PaiementScolarite
        fields = [
            'student', 'filiere', 'session', 'tranche',
            'nature_paiement',
            'montant_verse', 'date_paiement', 'heure_paiement'
        ]
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'filiere': forms.Select(attrs={'class': 'form-control'}),
            'session': forms.Select(attrs={'class': 'form-control'}),
            'tranche': forms.Select(attrs={'class': 'form-control'}),
            'nature_paiement': forms.Select(attrs={'class': 'form-control'}),
            'montant_verse': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'date_paiement': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'heure_paiement': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

    def clean_montant_verse(self):
        montant = self.cleaned_data.get('montant_verse')
        if montant is not None and montant < 0:
            raise forms.ValidationError("Le montant versé ne peut pas être négatif.")
        return montant
        # Optionally, you can filter queryset or set initial values here


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



from django import forms
from .models import EmploiDeTemps, ActiviteJour

class EmploiDeTempsForm(forms.ModelForm):
    class Meta:
        model = EmploiDeTemps
        fields = ['filiere', 'session', 'date_debut', 'date_fin']
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'type': 'date'}),
        }

class ActiviteJourForm(forms.ModelForm):
    class Meta:
        model = ActiviteJour
        fields = ['jour', 'matiere', 'professeur', 'salle', 'heure_debut', 'heure_fin']
        widgets = {
            'heure_debut': forms.TimeInput(attrs={'type': 'time'}),
            'heure_fin': forms.TimeInput(attrs={'type': 'time'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Version corrigée - utilisez simplement all() ou filtrez sur un champ existant
        self.fields['professeur'].queryset = Professeur.objects.all()

from .models import User, Student, Professeur, Matiere, Salle, Note, Sujet, SujetCommentaire

class MatiereForm(forms.ModelForm):
    class Meta:
        model = Matiere
        fields = ['nom', 'unite_enseignement', 'filiere','coefficient', 'creneau_horaire', 'bareme']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'unite_enseignement': forms.Select(attrs={'class': 'form-control'}),
            'filiere': forms.Select(attrs={'class': 'form-control'}),
    
            'coefficient': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'creneau_horaire': forms.Select(attrs={'class': 'form-control'}),
            'bareme': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

class SalleForm(forms.ModelForm):
    class Meta:
        model = Salle
        fields = ['nom']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            
        }
 
from django.contrib.auth.decorators import login_required             


from django.core.exceptions import ValidationError
from .models import Note, ListePresence, PresenceEtudiant, Attestation, Student, Filiere

from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from .models import Note

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['student', 'matiere', 'filiere', 'note_cc', 'note_sn']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'matiere': forms.Select(attrs={'class': 'form-control'}),
            'filiere': forms.Select(attrs={'class': 'form-control'}),
            'note_cc': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 20,
                'step': 0.25,  # Permet les quarts de point
                'placeholder': '0.00 - 20.00'
            }),
            'note_sn': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 20,
                'step': 0.25,  # Permet les quarts de point
                'placeholder': '0.00 - 20.00'
            }),
        }
        labels = {
            'note_cc': 'Note de Contrôle Continu (30%)',
            'note_sn': 'Note de Session Normale (70%)'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajout de validateurs explicites pour une validation côté serveur
        self.fields['note_cc'].validators.append(MinValueValidator(0))
        self.fields['note_cc'].validators.append(MaxValueValidator(20))
        self.fields['note_sn'].validators.append(MinValueValidator(0))
        self.fields['note_sn'].validators.append(MaxValueValidator(20))
    
    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        matiere = cleaned_data.get('matiere')
        note_cc = cleaned_data.get('note_cc')
        note_sn = cleaned_data.get('note_sn')
        
        # Vérification de la filière
        if student and matiere and student.filiere != matiere.filiere:
            raise ValidationError("L'étudiant n'est pas inscrit dans la filière de cette matière.")
        
        # Vérification qu'au moins une note est fournie
        if note_cc is None and note_sn is None:
            raise ValidationError("Veuillez saisir au moins une note (CC ou SN).")
        
        # Arrondi des notes pour éviter les valeurs comme 12.333
        if note_cc is not None:
            cleaned_data['note_cc'] = round(note_cc, 2)
        if note_sn is not None:
            cleaned_data['note_sn'] = round(note_sn, 2)
        
        return cleaned_data
    
    def clean_note_cc(self):
        note_cc = self.cleaned_data.get('note_cc')
        if note_cc is not None:
            # Vérification du pas de 0.25 (optionnel)
            if (note_cc * 4) % 1 != 0:
                raise ValidationError("Les notes doivent être en quarts de point (0.25, 0.5, 0.75).")
        return note_cc
    
    def clean_note_sn(self):
        note_sn = self.cleaned_data.get('note_sn')
        if note_sn is not None:
            # Vérification du pas de 0.25 (optionnel)
            if (note_sn * 4) % 1 != 0:
                raise ValidationError("Les notes doivent être en quarts de point (0.25, 0.5, 0.75).")
        return note_sn

class ListePresenceForm(forms.ModelForm):
    class Meta:
        model = ListePresence
        fields = ['filiere', 'matiere', 'professeur', 'date_cours', 'heure_debut', 'heure_fin', 'commentaire']
        widgets = {
            'filiere': forms.Select(attrs={'class': 'form-control'}),
            'matiere': forms.Select(attrs={'class': 'form-control'}),
            'professeur': forms.Select(attrs={'class': 'form-control'}),
            'date_cours': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'heure_debut': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'heure_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class PresenceEtudiantForm(forms.ModelForm):
    class Meta:
        model = PresenceEtudiant
        fields = ['student', 'est_present', 'justification']
    
    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        
        if student and hasattr(self, 'instance') and self.instance.liste:
            # Vérifier si l'étudiant existe déjà dans cette liste
            exists = PresenceEtudiant.objects.filter(
                liste=self.instance.liste, 
                student=student
            ).exists()
            
            if exists:
                raise ValidationError("Cet étudiant est déjà présent dans cette liste")
        
        return cleaned_data
class PresenceEtudiantForm(forms.ModelForm):
    class Meta:
        model = PresenceEtudiant
        fields = ['est_present', 'justification']
        widgets = {
            'est_present': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'justification': forms.TextInput(attrs={'class': 'form-control'}),
        }

class PresenceFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        # Ajouter des validations supplémentaires si nécessaire

class AttestationForm(forms.ModelForm):
    class Meta:
        model = Attestation
        fields = ['student', 'filiere', 'type_attestation', 'texte_personnalise', 'valide_jusqua']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'filiere': forms.Select(attrs={'class': 'form-control'}),
            'type_attestation': forms.Select(attrs={'class': 'form-control'}),
            'texte_personnalise': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'valide_jusqua': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les étudiants qui ont une filière
        self.fields['student'].queryset = Student.objects.filter(filiere__isnull=False)
        
        # Si une instance existe, limiter les filières à celle de l'étudiant
        if self.instance and self.instance.student and self.instance.student.filiere:
            self.fields['filiere'].queryset = Filiere.objects.filter(id=self.instance.student.filiere.id)
        else:
            self.fields['filiere'].queryset = Filiere.objects.none()
        
        # Mettre à jour les filières lorsqu'un étudiant est sélectionné
        if 'student' in self.data:
            try:
                student_id = int(self.data.get('student'))
                student = Student.objects.get(id=student_id)
                self.fields['filiere'].queryset = Filiere.objects.filter(id=student.filiere.id)
            except (ValueError, TypeError, Student.DoesNotExist):
                pass

from django import forms
from django.core.exceptions import ValidationError
from .models import Note, ListePresence, PresenceEtudiant, Attestation
from django.forms import inlineformset_factory

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['student', 'matiere', 'filiere', 'note_cc', 'note_sn']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'filiere': forms.Select(attrs={'class': 'form-select'}),
            
            'note_cc': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 20,
                'step': 0.25,
                'placeholder': '0.00 - 20.00'
            }),
            'note_sn': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 20,
                'step': 0.25,
                'placeholder': '0.00 - 20.00'
            }),
        }
        labels = {
            'note_cc': 'Note de Contrôle Continu (30%)',
            'note_sn': 'Note de Session Normale (70%)'
        }


from django.forms import modelformset_factory
from .models import ListePresence  # Correction du nom du modèle

ListePresenceFormSet = modelformset_factory(
    ListePresence,  # Utilisation du bon modèle
    fields=(
        'filiere', 
        'matiere', 
        'professeur', 
        'date_cours', 
        'heure_debut', 
        'heure_fin', 
        'commentaire'
    ),
    extra=1,
    can_delete=True
)
class ListePresenceFormSet(forms.ModelForm):
    class Meta:
        model = ListePresence
        fields = ['filiere', 'matiere', 'professeur', 'date_cours', 'heure_debut', 'heure_fin', 'commentaire']
        widgets = {
            'filiere': forms.Select(attrs={'class': 'form-select'}),
            'matiere': forms.Select(attrs={'class': 'form-select'}),
            'professeur': forms.Select(attrs={'class': 'form-select'}),
            'date_cours': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'heure_debut': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'heure_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class PresenceEtudiantForm(forms.ModelForm):
    class Meta:
        model = PresenceEtudiant
        fields = ['student', 'est_present', 'justification']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'est_present': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'justification': forms.TextInput(attrs={'class': 'form-control'}),
        }

PresenceEtudiantFormSet = inlineformset_factory(
    ListePresence,
    PresenceEtudiant,
    form=PresenceEtudiantForm,
    extra=0,
    can_delete=True,
    min_num=1,
    validate_min=True
)

class AttestationForm(forms.ModelForm):
    class Meta:
        model = Attestation
        fields = ['student', 'filiere', 'type_attestation', 'texte_personnalise', 'valide_jusqua']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'filiere': forms.Select(attrs={'class': 'form-select'}),
            'type_attestation': forms.Select(attrs={'class': 'form-select'}),
            'texte_personnalise': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'valide_jusqua': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }



# Forum de discussion éducatif
class SujetForm(forms.ModelForm):
    class Meta:
        model = Sujet
        fields = ['titre', 'description', 'filiere', 'fichier']

class SujetCommentaireForm(forms.ModelForm):
    class Meta:
        model = SujetCommentaire
        fields = ['texte']
        widgets = {
            'texte': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }





   
        
        
        



