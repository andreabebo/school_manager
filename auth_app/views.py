from django.contrib.auth.decorators import login_required
# --- Création d'une filière avec tranches dynamiques ---
from .form import FiliereForm, TrancheFormSet

@login_required
def filiere(request):
    if request.method == 'POST':
        form = FiliereForm(request.POST)
        tranches = TrancheFormSet(request.POST)
        if form.is_valid() and tranches.is_valid():
            filiere = form.save()
            tranches.instance = filiere
            tranches.save()
            return redirect('liste_filiere')
    else:
        form = FiliereForm()
        tranches = TrancheFormSet()
    return render(request, 'filiere.html', {'form': form, 'tranches': tranches})
# --- IMPORTS EN TÊTE DE FICHIER ---
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseForbidden
from .models import SujetCommentaire, PaiementScolarite, Sujet, Filiere, Student, Session, Tranche, Matiere, Salle
from django.db import models
from .form import SujetCommentaireForm, PaiementScolariteForm, FiliereForm, TrancheFormSet
from django.db.models import Q
# --- FIN IMPORTS ---

@login_required
def supprimer_paiement(request, pk):
    paiement = get_object_or_404(PaiementScolarite, pk=pk)
    paiement.delete()
    return redirect('afficher_scolarite')

@login_required
def comment_update(request, pk):
    commentaire = get_object_or_404(SujetCommentaire, pk=pk)
    if commentaire.auteur != request.user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = SujetCommentaireForm(request.POST, instance=commentaire)
        if form.is_valid():
            form.save()
            return redirect(commentaire.sujet.get_absolute_url())
    else:
        form = SujetCommentaireForm(instance=commentaire)
    # Pour le modal, on redirige toujours sur la page du sujet (le JS/HTML gère l'ouverture du modal)
    return redirect(commentaire.sujet.get_absolute_url())

@login_required
def comment_delete(request, pk):
    commentaire = get_object_or_404(SujetCommentaire, pk=pk)
    if commentaire.auteur != request.user:
        return HttpResponseForbidden()
    sujet_url = commentaire.sujet.get_absolute_url()
    if request.method == 'POST':
        commentaire.delete()
        return redirect(sujet_url)
    return redirect(sujet_url)
# --- Vues pour la synthèse des sujets/messages d'un enseignant ---
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import render, redirect
from .models import Sujet, SujetCommentaire
from django.db.models import Q
from .form import SujetCommentaireForm

@login_required
def sujets_liste(request):
    sujets = Sujet.objects.filter(auteur=request.user)
    nb_sujets = sujets.count()
    nb_commentaires = SujetCommentaire.objects.filter(sujet__in=sujets).count()
    return render(request, 'forum/sujets_liste.html', {
        'nb_sujets': nb_sujets,
        'nb_commentaires': nb_commentaires,
    })

@login_required
def sujets_detail(request):
    sujets = Sujet.objects.filter(auteur=request.user).order_by('-date_creation')
    if request.method == 'POST':
        sujet_id = request.POST.get('sujet_id')
        sujet = Sujet.objects.get(pk=sujet_id, auteur=request.user)
        form = SujetCommentaireForm(request.POST)
        if form.is_valid():
            commentaire = form.save(commit=False)
            commentaire.sujet = sujet
            commentaire.auteur = request.user
            commentaire.save()
            return redirect('sujets_detail')
    else:
        form = SujetCommentaireForm()
    sujets_commentaires = []
    for sujet in sujets:
        commentaires = SujetCommentaire.objects.filter(sujet=sujet).order_by('date_pub')
        sujets_commentaires.append({
            'sujet': sujet,
            'commentaires': commentaires,
            'form': SujetCommentaireForm(),
        })
    return render(request, 'forum/sujets_detail.html', {
        'sujets_commentaires': sujets_commentaires,
        'sujets': sujets,
    })

# Forum : Modifier et supprimer un sujet
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import UpdateView, DeleteView
from .models import Sujet, SujetCommentaire, Notification
from .form import SujetForm, SujetCommentaireForm

# Vue pour modifier un sujet
class SujetUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Sujet
    form_class = SujetForm
    template_name = 'forum/sujet_form.html'

    def test_func(self):
        sujet = self.get_object()
        return self.request.user == sujet.auteur

    def form_valid(self, form):
        from django.contrib import messages
        if not form.is_valid():
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(self.request, f"{form.fields[field].label if field in form.fields else field} : {error}")
            return self.form_invalid(form)
        messages.success(self.request, "Sujet modifié avec succès !")
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()

# Vue pour supprimer un sujet
class SujetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Sujet
    template_name = 'forum/sujet_confirm_delete.html'

    def test_func(self):
        sujet = self.get_object()
        return self.request.user == sujet.auteur

    def get_success_url(self):
        return reverse_lazy('sujet_list', kwargs={'filiere_id': self.object.filiere.id})
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django import forms

def supprimer_notification(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    notif.delete()
    return redirect('notifications')
# ...existing code...

# Forum imports
from django.views.generic import ListView, DetailView, CreateView
from django.utils.decorators import method_decorator
from .models import Sujet, SujetCommentaire, Notification
from .form import SujetForm, SujetCommentaireForm


# Fonctionnalité : supprimer une notification
@login_required
def supprimer_notification(request, notif_id):
    try:
        if request.user.is_superuser:
            notif = Notification.objects.get(id=notif_id)
        else:
            notif = Notification.objects.get(id=notif_id, user=request.user)
        notif.delete()
        messages.success(request, "Notification supprimée.")
    except Notification.DoesNotExist:
        messages.error(request, "Notification introuvable ou accès refusé.")
    return redirect('notifications')
from django.contrib.auth import login, authenticate, logout
from auth_app.models import User, Student
from django.contrib.auth.forms  import UserCreationForm
from .form import CustomUserCreationForm
from django.contrib import messages
from .form import EmploiDeTempsForm, ActiviteJourForm, NoteForm, MatiereForm, SalleForm
from .models import EmploiDeTemps, Professeur, PaiementScolarite, Filiere, ActiviteJour, Stat, Session
from django.contrib import messages

# Forum imports
from django.views.generic import ListView, DetailView, CreateView
from django.utils.decorators import method_decorator
from .models import Sujet, SujetCommentaire, Notification
from .form import SujetForm, SujetCommentaireForm


# Create your views here.
def inscription(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('base')
    else:
        form = CustomUserCreationForm()
    return render(request, 'inscription.html', {'form': form})            


# Forum de discussion éducatif
@method_decorator(login_required, name='dispatch')
class SujetCreateView(CreateView):
    model = Sujet
    form_class = SujetForm
    template_name = 'forum/sujet_form.html'

    def form_valid(self, form):
        from django.contrib import messages
        from django.shortcuts import redirect, render
        # Empêcher les étudiants de créer un sujet
        if Student.objects.filter(user=self.request.user).exists():
            messages.error(self.request, "Les étudiants ne sont pas autorisés à créer un sujet.")
            return render(self.request, self.template_name, {'form': form})

        if not form.is_valid():
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(self.request, f"{form.fields[field].label if field in form.fields else field} : {error}")
            return render(self.request, self.template_name, {'form': form})

        sujet = form.save(commit=False)
        sujet.auteur = self.request.user
        # Handle file upload if a file is provided
        if self.request.FILES.get('fichier'):
            sujet.fichier = self.request.FILES['fichier']
        sujet.save()
        self.object = sujet
        # Notifier tous les étudiants de la filière
        etudiants = Student.objects.filter(filiere=sujet.filiere)
        for etu in etudiants:
            Notification.objects.create(
                user=etu.user,
                sujet=sujet,
                message=f"Nouveau sujet dans {sujet.filiere.nom} : {sujet.titre}"
            )
        messages.success(self.request, "Sujet créé avec succès !")
        return redirect(sujet.get_absolute_url())

@method_decorator(login_required, name='dispatch')
class SujetListView(ListView):
    model = Sujet
    template_name = 'forum/sujet_list.html'
    context_object_name = 'sujets'


    def get_queryset(self):
        filiere_id = self.kwargs.get('filiere_id')
        return Sujet.objects.filter(filiere_id=filiere_id).order_by('-date_creation')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import Filiere, SujetCommentaire
        context['filieres'] = Filiere.objects.filter(active=True)
        user = self.request.user
        sujets = context['sujets']
        sujets_autres = sujets.exclude(auteur=user)
        nb_sujets_autres = sujets_autres.count()
        nb_commentaires_autres = SujetCommentaire.objects.filter(sujet__in=sujets_autres).count()
        nb_sujets = sujets.filter(auteur=user).count()
        nb_commentaires = SujetCommentaire.objects.filter(sujet__in=sujets.filter(auteur=user)).count()
        # Ajout du dernier commentaire pour chaque sujet (pour affichage WhatsApp-like)
        sujets_list = []
        for sujet in sujets:
            last_comment = SujetCommentaire.objects.filter(sujet=sujet).order_by('-date_pub').first()
            sujet.last_comment = last_comment
            # Calcul du nombre de nouveaux commentaires non lus (hors ceux de l'utilisateur)
            nb_nouveaux = SujetCommentaire.objects.filter(sujet=sujet, lu=False).exclude(auteur=user).count() if hasattr(SujetCommentaire, 'lu') else 0
            sujet.nb_nouveaux_commentaires = nb_nouveaux
            sujets_list.append(sujet)
        context['sujets'] = sujets_list
        context['nb_sujets_autres'] = nb_sujets_autres
        context['nb_commentaires_autres'] = nb_commentaires_autres
        context['nb_sujets'] = nb_sujets
        context['nb_commentaires'] = nb_commentaires
        return context

@method_decorator(login_required, name='dispatch')
class SujetDetailView(DetailView):
    model = Sujet
    template_name = 'forum/sujet_detail.html'
    context_object_name = 'sujet'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SujetCommentaireForm()
        context['commentaires'] = self.object.commentaires.order_by('date_pub')
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = SujetCommentaireForm(request.POST)
        if form.is_valid():
            commentaire = form.save(commit=False)
            commentaire.sujet = self.object
            commentaire.auteur = request.user
            commentaire.save()
            return redirect(self.object.get_absolute_url())
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

@login_required
def notifications(request):
    notifs = Notification.objects.all().order_by('-date')
    return render(request, 'forum/notifications.html', {'notifications': notifs})

@login_required
def marquer_notif_lue(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    notif.lu = True
    notif.save()
    return redirect('notifications')

def connexion(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('base')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
            # On renvoie le username pour pré-remplir le champ
            return render(request, 'connexion.html', {"username": username})
    return render(request, 'connexion.html')


@login_required
def acceuil(request):
    return render(request, 'base.html')


def deconnexion(request):
    logout(request)
    return redirect('connexion')

@login_required
def ajout_session(request):
    if request.method =='POST':
        nom_session = request.POST.get('nom_session')
        date_session = request.POST.get('date_session')
        print(nom_session, date_session) 
        session=Session.objects.create( nom_session=nom_session, date_session=date_session)
        session.save()
        return redirect('ajout_session')
    return render(request, 'ajout_session.html')

@login_required
def choix_session(request):
    sessions = Session.objects.all()
    context = {
        "sessions" : sessions
    }
    if request.method == 'POST':
        session_id = request.POST.get('session')
        return redirect('ajouterEtudiant', session_id=session_id)
    
    return render(request,'choix_session.html', context)
    
@login_required
def ajouterEtudiant(request, session_id):
    session = get_object_or_404(Session, pk=session_id)
    filieres = Filiere.objects.filter(active=True)
    if request.method == 'POST':
        nom = request.POST.get('last_name') 
        prenom = request.POST.get('first_name') 
        age= request.POST.get('age') 
        sexe= request.POST.get('sexe')
        email = request.POST.get('email') 
        ville = request.POST.get('ville') 
        diplome = request.POST.get('diplome') 
        filiereId = request.POST.get('filiere')
        contact = request.POST.get('contact') 
        password = request.POST.get('password')
        filiere = Filiere.objects.get(id=filiereId)
        user=User(first_name=prenom, last_name=nom, email=email)
        user.set_password(password)
        user.save()
        student=Student.objects.create(sexe=sexe, age=age, ville=ville, diplome=diplome, filiere=filiere, contact=contact, user=user, session=session)
        student.save()
        return redirect('listeEtudiant')
    return render(request, 'ajouterEtudiant.html', {'filieres': filieres, 'session': session})    

@login_required
def listeEtudiant(request):
    sessions=Session.objects.all()
    students=Student.objects.filter(user__is_active=True)
    return render(request, 'listeEtudiant.html', {"students": students, "sessions": sessions})  

@login_required
def rechercher_etudiants(request):
    sessions = Session.objects.all()

    session_id = request.GET.get('session')
    if session_id:
        students=Student.objects.filter(user__is_active=True, session__id=session_id)
        return render(request, 'listeEtudiant.html', {'students': students, 'sessions': sessions, 'session_id':session_id})  
        
@login_required
def desactiver_utilisateur(request, user_id):
    user = get_object_or_404(User, id=user_id) 
    students=Student.objects.filter(user__is_active=True)
    if not user.is_active:
        messages.warning(request, "l'utilisateur est déjà désactivé")
        return render(request, 'listeEtudiant.html', {"students": students})
    else:
       user.is_active= False
       user.save()
       messages.success(request,"Désactivation réussie") 
       return redirect('listeEtudiant')   
   
@login_required      
def edit_user(request, user_id):
    filieres = Filiere.objects.filter(active=True)
    user = get_object_or_404(User, id=user_id)
    student=Student.objects.get(user=user)
    studentAge = str(student.age)
    if request.method == 'POST':
        nom = request.POST.get('last_name') 
        prenom = request.POST.get('first_name') 
        age= request.POST.get('age') 
        sexe= request.POST.get('sexe')
        email = request.POST.get('email') 
        ville = request.POST.get('ville') 
        diplome = request.POST.get('diplome') 
        filiereId = request.POST.get('filiere')
        contact = request.POST.get('contact') 
        password = request.POST.get('password')
        filiere = Filiere.objects.get(id=filiereId)
        user.first_name = nom
        user.last_name = prenom
        user.email = email
        user.password = password
        user.save()
        student.age = age
        student.sexe = sexe
        student.ville = ville
        student.diplome = diplome
        student.filiere = filiere
        student.contact = contact
        student.save()
        return redirect('listeEtudiant')  
    else:
        form = UserCreationForm(instance=user)
    return render(request, 'edit_user.html', {"student": student, "studentAge":studentAge, 'filieres': filieres})




@login_required
def liste_emploi_de_temps(request):
    liste_emploi_de_temps = EmploiDeTemps.objects.all().order_by('-date_debut', 'date_fin')
    return render(request, 'liste_emploi_de_temps.html', {
        'liste_emploi_de_temps': liste_emploi_de_temps
    })
@login_required
def creer_emploi_de_temps(request):
    if request.method == "POST":
        form = EmploiDeTempsForm(request.POST)
        if form.is_valid():
            emploi = form.save()
            messages.success(request, "Emploi du temps créé avec succès!")
            return redirect('ajouter_activites', emploi.pk)
    else:
        form = EmploiDeTempsForm()
    
    return render(request, 'creer_emploi_de_temps.html', {
        'form': form,
        'filieres': Filiere.objects.filter(active=True)
    })

@login_required
def ajouter_activites(request, emploi_de_temps_id):
    emploi_de_temps = get_object_or_404(EmploiDeTemps, id=emploi_de_temps_id)
    
    # Récupération des données pour les selects
    matieres = Matiere.objects.all()
    salles = Salle.objects.all()
    professeurs = Professeur.objects.all().select_related('user')
    
    # Récupération des activités existantes
    activites_jour = ActiviteJour.objects.filter(
        emploi_de_temps=emploi_de_temps
    ).select_related(
        'matiere', 
        'professeur__user', 
        'salle'
    ).order_by('jour', 'heure_debut')

    if request.method == "POST":
        # Création manuelle du formulaire à partir des données POST
        form_data = {
            'jour': request.POST.get('jour'),
            'matiere': request.POST.get('matiere'),
            'professeur': request.POST.get('professeur'),
            'salle': request.POST.get('salle'),
            'heure_debut': request.POST.get('heure_debut'),
            'heure_fin': request.POST.get('heure_fin'),
        }
        
        form = ActiviteJourForm(form_data)
        if form.is_valid():
            activite = form.save(commit=False)
            activite.emploi_de_temps = emploi_de_temps
            activite.save()
            messages.success(request, "Activité ajoutée avec succès!")
            return redirect('ajouter_activites', emploi_de_temps_id=emploi_de_temps.id)
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = ActiviteJourForm()

    context = {
        'form': form,
        'emploi_de_temps': emploi_de_temps,
        'activites_jour': activites_jour,
        'matieres': matieres,
        'salles': salles,
        'professeurs': professeurs,
    }
    return render(request, 'ajouter_activites.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q

@login_required

def afficher_emploi_de_temps(request, emploi_de_temps_id):
    
    # Récupération des paramètres de filtre
    filiere_id = request.GET.get('filiere')
    session_id = request.GET.get('session')
    search_query = request.GET.get('search')
    
    
    # Base queryset avec prefetch_related pour les activités
    emplois = EmploiDeTemps.objects.all()\
        .select_related('filiere', 'session')\
        .prefetch_related('activites__matiere', 'activites__professeur', 'activites__salle')
    
    # Application des filtres
    if filiere_id:
        emplois = emplois.filter(filiere_id=filiere_id)
    if session_id:
        emplois = emplois.filter(session_id=session_id)
    if search_query:
        emplois = emplois.filter(
            Q(filiere__nom__icontains=search_query) |
            Q(activites__matiere__nom__icontains=search_query)
        ).distinct()
    
    # Récupération des options pour les filtres
    filieres = Filiere.objects.all()
    sessions = Session.objects.all()
    
    context = {
        'emplois': emplois,
        'filieres': filieres,
        'sessions': sessions,
        'selected_filiere': int(filiere_id) if filiere_id else None,
        'selected_session': int(session_id) if session_id else None,
        'search_query': search_query or '',
    }
    return render(request, 'afficher_emploi_de_temps.html', context)

    
@login_required
def supprimer_activite_et_emploi(request, activite_id):
    activite = get_object_or_404(ActiviteJour, id=activite_id)
    emploi = activite.emploi_de_temps  # Récupère l'emploi du temps associé

    if request.method == "POST":
        # Supprime d'abord l'activité
        activite.delete()
        # Puis l'emploi du temps
        emploi.delete()
        messages.success(request, "Activité et emploi du temps associés supprimés avec succès.")
        return redirect('liste_emplois')

    # GET → afficher la page de confirmation
    return render(request, 'emploi/supprimer_activite_et_emploi.html', {
        'activite': activite,
        'emploi': emploi,
    })
    
@login_required
def imprimer_emploi_de_temps(request, emploi_de_temps_id):
    emploi = get_object_or_404(EmploiDeTemps, id=emploi_de_temps_id)
    activites = ActiviteJour.objects.filter(emploi_de_temps=emploi).order_by('jour', 'heure_debut')

    return render(request, 'pdf_emploi.html', {
        'emploi': emploi,
        'activites': activites,
        'user': request.user
    })

@login_required
def professeur(request):
    if request.method == 'POST':
        nom = request.POST.get('last_name') 
        prenom = request.POST.get('first_name') 
        email = request.POST.get('email')
        age= request.POST.get('age') 
        sexe= request.POST.get('sexe') 
        numero = request.POST.get('numero')
        password = request.POST.get('password')
        print(nom, prenom, age, sexe, numero)
        user=User.objects.create(first_name=prenom, last_name=nom, email=email, password=password)
        user.save() 
        professeur=Professeur.objects.create(age=age, sexe=sexe, numero=numero, user=user)
        professeur.save()
        return redirect('listeProf')
    return render(request, 'professeur.html') 

@login_required
def listeProf(request):
    professeurs=Professeur.objects.filter(user__is_active=True)
    return render(request, 'listeProf.html', {"professeurs": professeurs}) 

@login_required
def desactiver_professeur(request, user_id):
    user = get_object_or_404(User, id=user_id) 
    professeurs=Professeur.objects.filter(user__is_active=True)
    if not user.is_active:
        messages.warning(request, "l'utilisateur est déjà désactivé")
        return render(request, 'listeProf.html', {"professeurs": professeurs})
    else:
       user.is_active= False
       user.save()
       messages.success(request,"Désactivation réussie") 
       return redirect('listeProf') 

@login_required   
def edit_prof(request, user_id):
    user = get_object_or_404(User, id=user_id)
    professeur=Professeur.objects.get(user=user)
    professeurAge = str(professeur.age)
    print(type(professeur.age))
    if request.method == 'POST':
        nom = request.POST.get('last_name') 
        prenom = request.POST.get('first_name') 
        age= request.POST.get('age') 
        sexe= request.POST.get('sexe')
        email = request.POST.get('email') 
        numero = request.POST.get('numero') 
        password = request.POST.get('password')
        user.first_name = nom
        user.last_name = prenom
        user.email = email
        user.password = password
        user.save()
        professeur.age = age
        professeur.sexe = sexe
        professeur.numero = numero
        professeur.save()
        return redirect('listeProf')  
    else:
        form = UserCreationForm(instance=user)
    return render(request, 'edit_prof.html', {"professeur": professeur, "professeurAge":professeurAge})   
@login_required
def compte(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return render(request, 'compte.html', {"user": user})
@login_required
def edit_compte(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        image = request.FILES.get('image') 
        nom = request.POST.get('last_name') 
        prenom = request.POST.get('first_name') 
        email = request.POST.get('email')
        password = request.POST.get('password')
        user.profile_image = image
        user.first_name = nom
        user.last_name = prenom
        user.email = email
        if len(password) != 0:
            user.set_password(password)
        user.save()
        return redirect('compte', user_id=user.pk)  
    else:
        form = UserCreationForm(instance=user)
    return render(request, 'edit_compte.html', {"user": user})



# @login_required
# def parametre_utilisateur(request):
#     # Vérifier si les paramètres de l'utilisateur existent, sinon les créer
#     parametres, created = ParametreUtilisateur.objects.get_or_create(utilisateur=request.user)
#
#     if request.method == 'POST':
#         form = ParametreUtilisateurForm(request.POST, request.FILES, instance=parametres)
#         if form.is_valid():
#             form.save()
#             return redirect('parametres_utilisateur')
#     else:
#         form = ParametreUtilisateurForm(instance=parametres)
#
#     return render(request, 'parametres_utilisateur.html', {'form': form, 'parametres': parametres})


@login_required
def scolarite(request):
    from .form import PaiementScolariteForm
    if request.method == 'POST':
        form = PaiementScolariteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('afficher_scolarite')
    else:
        form = PaiementScolariteForm()
    students = Student.objects.all()
    filieres = Filiere.objects.all()
    sessions = Session.objects.all()
    tranches = []  # Optionnel, à charger dynamiquement côté JS selon la filière
    # Ajout du contexte pour nature_paiement si besoin
    return render(request, 'scolarite.html', {
        'form': form,
        'students': students,
        'filieres': filieres,
        'sessions': sessions,
        'tranches': tranches,
    })

@login_required
def afficher_scolarite(request):
    filiere_id = request.GET.get('filiere')
    search = request.GET.get('search', '').strip()
    paiements = PaiementScolarite.objects.all().order_by('date_paiement')
    filieres = Filiere.objects.all()
    if filiere_id:
        paiements = paiements.filter(filiere_id=filiere_id)
    if search:
        paiements = paiements.filter(
            models.Q(student__user__first_name__icontains=search) |
            models.Q(student__user__last_name__icontains=search) |
            models.Q(student__matricule__icontains=search)
        )
    # Calculs automatiques
    total_verse = sum(p.montant_verse for p in paiements)
    total_restant = sum(p.montant_restant for p in paiements)
    soldes = [p for p in paiements if p.montant_restant == 0]
    non_soldes = [p for p in paiements if p.montant_restant != 0]
    total_soldes = len(soldes)
    total_non_soldes = len(non_soldes)


    # Export CSV si demandé
    if 'export' in request.GET:
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="paiements_scolarite.csv"'
        writer = csv.writer(response)
        writer.writerow(['Nom', 'Matricule', 'Filière', 'Département', 'Session', 'Date paiement', 'Heure paiement', 'Tranche', 'Montant versé', 'Montant global', 'Montant restant', 'Etat'])
        for p in paiements:
            writer.writerow([
                p.student.user.get_full_name(),
                p.student.matricule,
                p.filiere.nom,
                p.filiere.departement,
                p.session.nom_session if p.session else '',
                p.date_paiement,
                p.heure_paiement,
                p.tranche.nom,
                p.montant_verse,
                p.filiere.montant_global,
                p.montant_restant,
                p.etat_scolarite
            ])
        return response

    # Export PDF si demandé
    if 'export_pdf' in request.GET:
        from django.http import HttpResponse
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        import io
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
        data = [[
            'Nom', 'Matricule', 'Filière', 'Département', 'Session', 'Date paiement', 'Heure paiement', 'Tranche', 'Montant versé', 'Montant total', 'Montant restant', 'Etat'
        ]]
        for p in paiements:
            data.append([
                p.student.user.get_full_name(),
                p.student.matricule,
                p.filiere.nom,
                p.filiere.departement,
                p.session.nom_session if p.session else '',
                str(p.date_paiement),
                str(p.heure_paiement),
                p.tranche.nom,
                str(p.montant_verse),
                str(p.montant_total),
                str(p.montant_restant),
                p.etat_scolarite
            ])
        table = Table(data, repeatRows=1)
        style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ])
        table.setStyle(style)
        elements = []
        styles = getSampleStyleSheet()
        elements.append(Paragraph('Liste des paiements de scolarité', styles['Title']))
        elements.append(table)
        doc.build(elements)
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="paiements_scolarite.pdf"'
        return response

    return render(request, 'afficher_scolarite.html', {
        'paiements': paiements,
        'filieres': filieres,
        'filiere_id': filiere_id,
        'search': search,
        'total_verse': total_verse,
        'total_restant': total_restant,
        'total_soldes': total_soldes,
        'total_non_soldes': total_non_soldes,
    })

@login_required
def imprimer_scolarite(request, pk):
    paiement = get_object_or_404(PaiementScolarite, pk=pk)
    return render(request, 'imprimer_scolarite.html', {'paiement': paiement})


@login_required
def filiere(request):
    if request.method == 'POST':
        form = FiliereForm(request.POST)
        tranches = TrancheFormSet(request.POST)
        if form.is_valid() and tranches.is_valid():
            filiere = form.save()
            tranches.instance = filiere
            tranches.save()
            return redirect('liste_filiere')
    else:
        form = FiliereForm()
        tranches = TrancheFormSet()
    return render(request, 'filiere.html', {'form': form, 'tranches': tranches})

@login_required
def liste_filiere(request):
    filieres = Filiere.objects.all()
    return render(request, 'liste_filiere.html', {'filieres': filieres})


@login_required
def desactiver_filiere(request, filiere_id):
    filiere = get_object_or_404(Filiere, id=filiere_id) 
    if filiere.active:
        filiere.active=False
    filiere.save()
    messages.success(request,"Désactivation réussie") 
    return redirect('liste_filiere') 

# views.py
from django.shortcuts import render, redirect
from django.db.models import Count, Sum, Q
from .models import Session, Filiere, Student, Note, Stat
from django.contrib import messages
import json

def generer_statistiques(request):
    # Supprimer les anciennes statistiques
    Stat.objects.all().delete()
    
    # Récupérer toutes les sessions et filières
    sessions = Session.objects.all()
    filieres = Filiere.objects.all()
    
    for session in sessions:
        for filiere in filieres:
            # Compter les étudiants inscrits
            etudiants = Student.objects.filter(session=session, filiere=filiere)
            total_inscrits = etudiants.count()
            
            # Compter par sexe
            total_hommes = etudiants.filter(sexe='M').count()
            total_femmes = etudiants.filter(sexe='F').count()
            
            # Compter les réussites (moyenne >= 10)
            etudiants_ids = etudiants.values_list('id', flat=True)
            reussites = Note.objects.filter(
                student__in=etudiants_ids,
                moyenne__gte=10
            ).values('student').distinct().count()
            
            # Créer la statistique
            if total_inscrits > 0:
                Stat.objects.create(
                    session=session,
                    filiere=filiere,
                    total_inscrits=total_inscrits,
                    total_hommes=total_hommes,
                    total_femmes=total_femmes,
                    total_reussite=reussites
                )
    
    messages.success(request, "Statistiques générées avec succès!")
    return redirect('afficher_statistiques')

def afficher_statistiques(request):
    filieres = Filiere.objects.all()
    
    # Préparer les données pour les graphiques
    data = {
        'filiere_labels': [],
        'inscrits_data': [],
        'reussite_data': [],
        'hommes_data': [],
        'femmes_data': [],
        'sexe_labels': ['Hommes', 'Femmes'],
        'sexe_data': [0, 0],
        'colors': [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
            '#9966FF', '#FF9F40', '#8AC926', '#1982C4'
        ]
    }
    
    for filiere in filieres:
        stats = Stat.objects.filter(filiere=filiere)
        total_inscrits = stats.aggregate(total=Sum('total_inscrits'))['total'] or 0
        total_reussite = stats.aggregate(total=Sum('total_reussite'))['total'] or 0
        total_hommes = stats.aggregate(total=Sum('total_hommes'))['total'] or 0
        total_femmes = stats.aggregate(total=Sum('total_femmes'))['total'] or 0
        
        if total_inscrits > 0:
            data['filiere_labels'].append(filiere.nom)
            data['inscrits_data'].append(total_inscrits)
            data['reussite_data'].append(round((total_reussite / total_inscrits) * 100, 2))
            data['hommes_data'].append(total_hommes)
            data['femmes_data'].append(total_femmes)
            data['sexe_data'][0] += total_hommes
            data['sexe_data'][1] += total_femmes
    
    # Convertir les données en JSON pour les utiliser dans JavaScript
    chart_data = json.dumps(data)
    
    context = {
        'chart_data': chart_data,
        'total_global_inscrits': sum(data['inscrits_data']),
        'total_global_reussite': sum(data['reussite_data']) / len(data['reussite_data']) if data['reussite_data'] else 0,
    }
    return render(request, 'statistiques.html', context)

@login_required
def matiere(request):
    professeurs = Professeur.objects.all()
    if request.method == 'POST':
        nom = request.POST.get('nom')
        unite_enseignement = request.POST.get('unite_enseignement')
        coefficient = request.POST.get('coefficient')
        creneau_horaire = request.POST.get('creneau_horaire')
        filiere_id = request.POST.get('filiere')  # string, ex: '3'
        professeur_id = request.POST.get('professeur')  # string, ex: '1'

        # Récupération des instances nécessaires
        filiere = Filiere.objects.get(id=filiere_id)
        professeur = Professeur.objects.get(id=professeur_id)

        # Création de la matière
        matiere = Matiere(
            nom=nom,
            unite_enseignement=unite_enseignement,
            coefficient=coefficient,
            creneau_horaire=creneau_horaire,
            filiere=filiere,
            professeur=professeur,
        )
        matiere.save()

        return redirect('liste_matiere')  # ou la page que tu veux

    # Si GET, afficher le formulaire avec les filières et professeurs
    filieres = Filiere.objects.all()
    professeurs = Professeur.objects.all()
    return render(request, 'matiere.html', {
        'filieres': filieres,
        'professeurs': professeurs,
    })
@login_required
def rechercher_matiere(request):
    matiere = Matiere.objects.all()

    matiere_id = request.GET.get('matiere')
    if matiere_id:
        matiere=Matiere.objects.filter(user__is_active=True, matiere__id=matiere_id)
        return render(request, 'liste_matiere.html', {'matieres': matiere, 'sessions': sessions, 'session_id':session_id}) 
@login_required
def modifier_matiere ( request, matiere_id):
    matiere = get_object_or_404(Matiere, id=matiere_id)
    filieres = Filiere.objects.all()
    professeurs = Professeur.objects.all()

    if request.method == 'POST':
        matiere.nom = request.POST.get('nom')
        matiere.unite_enseignement = request.POST.get('unite_enseignement')
        matiere.coefficient = request.POST.get('coefficient')
        matiere.creneau_horaire = request.POST.get('creneau_horaire')
        matiere.bareme = request.POST.get('bareme')

        filiere_id = request.POST.get('filiere')
        professeur_id = request.POST.get('professeur')

        # Sécurité : on vérifie que l’ID est valide avant affectation
        if filiere_id:
            matiere.filiere = get_object_or_404(Filiere, id=filiere_id)
        if professeur_id:
            matiere.professeur = get_object_or_404(Professeur, id=professeur_id)

        matiere.save()
        messages.success(request, "La matière a été mise à jour avec succès.")
        return redirect('liste_matiere')  # nom de la vue de redirection après modif

    return render(request, 'modifier_matiere.html', {
        'matiere': matiere,
        'filieres': filieres,
        'professeurs': professeurs,
    })
@login_required
def liste_matiere(request):
    filieres = Filiere.objects.all()
    filiere_id = request.GET.get('filiere')  # ID de la filière choisie dans le filtre

    if filiere_id:
        matieres = Matiere.objects.filter(filiere__id=filiere_id)
    else:
        matieres = Matiere.objects.all()

    return render(request, 'liste_matiere.html', {
        'matieres': matieres,
        'filieres': filieres,
        'filiere_id': filiere_id,  # pour garder la sélection dans le menu déroulant
    })

@login_required
def desactiver_matiere(request, matiere_id):
    matiere = get_object_or_404(Matiere, id=matiere_id) 
    if matiere.active:
        matiere.active=False
    matiere.save()
    messages.success(request,"Désactivation réussie") 
    return redirect('liste_matiere') 

@login_required
def salle(request):
    if request.method == 'POST':
        form = SalleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_salle')
    else:
        form = SalleForm()
    return render(request, 'salle.html', {'form': form})

@login_required
def liste_salle(request):
    salles = Salle.objects.all()
    return render(request, 'liste_salle.html', {'salles': salles})

@login_required
def desactiver_salle(request, salle_id):
    salle = get_object_or_404(Salle, id=salle_id)
    salle.delete()
    messages.success(request, "Salle supprimée avec succès.")
    return redirect('liste_salle')

from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .form import ListePresenceFormSet
from .models import Note, ListePresence, PresenceEtudiant, Attestation
from .form import NoteForm, ListePresenceForm, PresenceEtudiantForm, AttestationForm

# ============== Notes ==============
from django.views.generic import ListView

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from .models import Filiere, Student, Note
from django.urls import reverse_lazy
import json
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

# Vue pour filtrer les étudiants par filière
class StudentFiliereListView(ListView):
    model = Student
    template_name = 'notes/student_list.html'
    context_object_name = 'students'

    def get_queryset(self):
        filiere_id = self.request.GET.get('filiere')
        if filiere_id:
            return Student.objects.filter(filiere_id=filiere_id)
        return Student.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filieres'] = Filiere.objects.all()
        return context

# Vue détaillée des notes d'un étudiant
# views.py
class StudentNotesDetailView(DetailView):
    model = Student
    template_name = 'notes/student_notes_detail.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        notes = Note.objects.filter(student=student)
        
        # Calcul des statistiques
        passed_count = 0
        failed_count = 0
        total = 0
        weighted_sum = 0
        total_coef = 0
        
        for note in notes:
            if note.moyenne is not None:
                total += 1
                if note.moyenne >= 10:
                    passed_count += 1
                else:
                    failed_count += 1
                
                # Calcul de la moyenne générale pondérée
                if note.matiere.coefficient:
                    weighted_sum += note.moyenne * note.matiere.coefficient
                    total_coef += note.matiere.coefficient

        # Calcul de la moyenne générale
        overall_average = weighted_sum / total_coef if total_coef > 0 else 0
        
        # Détermination de la mention générale
        overall_mention = "Insuffisant"
        if overall_average >= 18:
            overall_mention = "Excellent"
        elif overall_average >= 16:
            overall_mention = "Très bien"
        elif overall_average >= 14:
            overall_mention = "Bien"
        elif overall_average >= 12:
            overall_mention = "Assez bien"
        elif overall_average >= 10:
            overall_mention = "Passable"
        
        context['notes'] = notes
        context['passed_count'] = passed_count
        context['failed_count'] = failed_count
        context['overall_average'] = overall_average
        context['overall_mention'] = overall_mention
        return context

# Vue pour modifier une note
from django.views.generic import CreateView
from django.urls import reverse

class NoteCreateView(CreateView):
    model = Note
    template_name = 'notes/note_form.html'
    fields = ['matiere', 'note_cc', 'note_sn']
    
    def get_initial(self):
        initial = super().get_initial()
        student_id = self.kwargs.get('student_id')
        student = Student.objects.get(id=student_id)
        initial['student'] = student
        initial['filiere'] = student.filiere
        return initial
    
    def form_valid(self, form):
        form.instance.student = Student.objects.get(id=self.kwargs['student_id'])
        form.instance.filiere = form.instance.student.filiere
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('student_notes', args=[self.object.student.id])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = Student.objects.get(id=self.kwargs['student_id'])
        context['student'] = student
        context['is_creation'] = True
        return context

class NoteUpdateView(UpdateView):
    model = Note
    template_name = 'note/note_form.html'
    fields = ['note_cc', 'note_sn']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_creation'] = False
        return context
    
    def get_success_url(self):
        return reverse('student_notes', args=[self.object.student.id])

# Vue pour supprimer une note
class NoteDeleteView(DeleteView):
    model = Note
    template_name = 'notes/note_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('student_notes', args=[self.object.student.id])

# Génération du PDF
def generate_pdf(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    notes = Note.objects.filter(student=student)
    
    template = get_template('notes/student_note_pdf.html')
    context = {'student': student, 'notes': notes}
    html = template.render(context)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="notes_{student}.pdf"'
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Erreur lors de la génération du PDF')
    return response
# ============== Présences ==============

class ListePresenceListView(ListView):
    model = ListePresence
    template_name = 'presences/presence_list.html'
    context_object_name = 'listes'
    paginate_by = 10
    
    def get_queryset(self):
        return ListePresence.objects.select_related('filiere', 'matiere', 'professeur').order_by('-date_cours')


# views.py (ajouts et modifications)

from django.forms import formset_factory
from django.shortcuts import get_list_or_404

# Ajouter au début des imports
from django.http import JsonResponse
from django.db.models import Q

# ... autres imports existants ...

# Modifier la vue ListePresenceCreateView
class ListePresenceCreateView(CreateView):
    # ...
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        PresenceEtudiantFormSet = formset_factory(
            PresenceEtudiantForm, 
            extra=10,
            can_delete=False
        )
        
        if self.request.POST:
            context['presence_formset'] = PresenceEtudiantFormSet(
                self.request.POST,
                form_kwargs={'instance': self.object}  # Ajouté pour la validation
            )
        else:
            context['presence_formset'] = PresenceEtudiantFormSet(
                form_kwargs={'instance': self.object}  # Ajouté pour la validation
            )
        
        return context

# Nouvelle vue pour imprimer la liste de présence
class ListePresencePrintView(DetailView):
    model = ListePresence
    template_name = 'presences/presence_print.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['presences'] = self.object.presences.select_related('student__user')
        return context


class ListePresenceDetailView(DetailView):
    model = ListePresence
    template_name = 'presences/presence_detail.html'
    context_object_name = 'liste'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['presences'] = self.object.presences.select_related('student')
        return context


class ListePresenceUpdateView(UpdateView):
    model = ListePresence
    form_class = ListePresenceFormSet
    template_name = 'presences/presence_form.html'
    success_url = reverse_lazy('presence_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['presence_formset'] = PresenceEtudiantFormSet(self.request.POST, instance=self.object)
        else:
            context['presence_formset'] = PresenceEtudiantFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        presence_formset = context['presence_formset']
        if presence_formset.is_valid():
            presence_formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

# auth_app/views.py

from django.http import JsonResponse
from .models import Student

# ... autres imports et vues ...

@login_required
def get_etudiants_by_filiere(request):
    filiere_id = request.GET.get('filiere_id')
    if not filiere_id:
        return JsonResponse([], safe=False)
    
    try:
        etudiants = Student.objects.filter(filiere_id=filiere_id).select_related('user')
        data = [{
            'id': etudiant.id,
            'nom': etudiant.user.get_full_name(),
            'matricule': etudiant.matricule
        } for etudiant in etudiants]
        
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

class ListePresenceDeleteView(DeleteView):
    model = ListePresence
    template_name = 'presences/presence_confirm_delete.html'
    success_url = reverse_lazy('presence_list')
    
    # Ajoutez context_object_name pour utiliser 'object' dans le template
    context_object_name = 'object'

# ============== Attestations ==============

class AttestationListView(ListView):
    model = Attestation
    template_name = 'attestations/attestation_list.html'
    context_object_name = 'attestations'
    paginate_by = 10
    
    def get_queryset(self):
        return Attestation.objects.select_related('student', 'filiere').order_by('-date_emission')


class AttestationCreateView(CreateView):
    model = Attestation
    form_class = AttestationForm
    template_name = 'attestations/attestation_form.html'
    success_url = reverse_lazy('attestation_list')
    
    def form_valid(self, form):
        form.instance.delivre_par = self.request.user
        return super().form_valid(form)


class AttestationDetailView(DetailView):
    model = Attestation
    template_name = 'attestations/attestation_detail.html'
    context_object_name = 'attestation'

#imprimer une attestation

# auth_app/views.py
from django.views.generic import DetailView
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings

class AttestationPrintView(DetailView):
    model = Attestation
    template_name = 'attestations/attestation_print.html'
    
    def get(self, request, *args, **kwargs):
        attestation = self.get_object()
        
        # Rendre le template HTML
        html_content = render_to_string(self.template_name, {
            'attestation': attestation,
            'MEDIA_URL': settings.MEDIA_URL
        })
        
        # Retourner la réponse HTML
        return HttpResponse(html_content)
    
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from .models import Note, ListePresence, PresenceEtudiant, Attestation
from .form import NoteForm, ListePresenceForm, PresenceEtudiantFormSet, AttestationForm

# ============== Notes - Vues supplémentaires ==============

class NoteUpdateView(UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'notes/note_form.html'
    success_url = reverse_lazy('note_list')


class NoteDeleteView(DeleteView):
    model = Note
    template_name = 'notes/note_confirm_delete.html'
    success_url = reverse_lazy('note_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['note'] = self.object
        return context

# ============== Présences - Vues supplémentaires ==============

class ListePresenceListView(ListView):
    model = ListePresence
    template_name = 'presences/presence_list.html'
    context_object_name = 'listes'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = ListePresence.objects.select_related('filiere', 'matiere', 'professeur')
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(filiere__nom__icontains=search_query) |
                Q(matiere__nom__icontains=search_query) |
                Q(professeur__nom__icontains=search_query)
            )
        return queryset.order_by('-date_cours')


class ListePresenceDetailView(DetailView):
    model = ListePresence
    template_name = 'presences/presence_detail.html'
    context_object_name = 'liste'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['presences'] = self.object.presences.select_related('student')
        return context


class ListePresenceUpdateView(UpdateView):
    model = ListePresence
    form_class = ListePresenceForm
    template_name = 'presences/presence_form.html'
    success_url = reverse_lazy('presence_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['presence_formset'] = PresenceEtudiantFormSet(
                self.request.POST, instance=self.object
            )
        else:
            context['presence_formset'] = PresenceEtudiantFormSet(
                instance=self.object
            )
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        presence_formset = context['presence_formset']
        if presence_formset.is_valid():
            self.object = form.save()
            presence_formset.instance = self.object
            presence_formset.save()
            return HttpResponseRedirect(self.get_success_url())
        return self.render_to_response(self.get_context_data(form=form))


class ListePresenceDeleteView(DeleteView):
    model = ListePresence
    template_name = 'presences/presence_confirm_delete.html'
    success_url = reverse_lazy('presence_list')


# ============== Attestations - Vues supplémentaires ==============

class AttestationCreateView(CreateView):
    model = Attestation
    form_class = AttestationForm
    template_name = 'attestations/attestation_form.html'
    success_url = reverse_lazy('attestation_list')
    
    def form_valid(self, form):
        form.instance.delivre_par = self.request.user
        return super().form_valid(form)


class AttestationUpdateView(UpdateView):
    model = Attestation
    form_class = AttestationForm
    template_name = 'attestations/attestation_form.html'
    success_url = reverse_lazy('attestation_list')


class AttestationDeleteView(DeleteView):
    model = Attestation
    template_name = 'attestations/attestation_confirm_delete.html'
    success_url = reverse_lazy('attestation_list')


class AttestationDownloadView(DetailView):
    model = Attestation
    
    def get(self, request, *args, **kwargs):
        attestation = self.get_object()
        if attestation.fichier_pdf:
            response = HttpResponse(
                attestation.fichier_pdf.read(), 
                content_type='application/pdf'
            )
            filename = f"attestation_{attestation.student.id}_{attestation.type_attestation}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        return HttpResponse("Fichier non trouvé", status=404)