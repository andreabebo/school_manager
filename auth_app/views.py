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
from .form import CoursForm, EmploiDeTempsForm, CommentaireForm, ActiviteJourForm, NoteForm
from .models import Cours, Commentaire, EmploiDeTemps, Professeur, PaiementScolarite, Filiere, ActiviteJour, Stat, Session
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
        student=Student.objects.create(age=age, ville=ville, diplome=diplome, filiere=filiere, contact=contact, user=user, session=session)
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
def publier_cours(request):
    if request.method == "POST":
        form = CoursForm(request.POST, request.FILES)
        if form.is_valid():
            cours = form.save(commit=False)
            cours.auteur = request.user
            cours.save()
            return redirect('detail_cours', pk=cours.pk)
    else:
        form = CoursForm()
    return render(request, 'publier_cours.html', {'form': form})



@login_required
def detail_cours(request, pk):
    cours = get_object_or_404(Cours, pk=pk)
    commentaires = cours.commentaires.all()
    if request.method == "POST":
        form = CommentaireForm(request.POST)
        if form.is_valid():
            commentaire = form.save(commit=False)
            commentaire.auteur = request.user
            commentaire.cours = cours
            commentaire.save()
    else:
        form = CommentaireForm()
    
    return render(request, 'detail_cours.html', {
        'cours': cours, 
        'commentaires': commentaires, 
        'form': form
    })
    
@login_required
def cours(request):
    cours = Cours.objects.all().order_by('-date_pub') 

    print( cours )
    return render(request, 'cours.html', {'cours': cours})

@login_required
def liste_emploi_de_temps(request):
    liste_emploi_de_temps = EmploiDeTemps.objects.all().order_by('-date_cours', 'heure_debut') 
    # Trier par date et heure
    print( liste_emploi_de_temps)
    return render(request, 'liste_emploi_de_temps.html', {'liste_emploi_de_temps': liste_emploi_de_temps})

@login_required
def creer_emploi_de_temps(request):
    filieres = Filiere.objects.filter(active=True)
    if request.method == "POST":
        form = EmploiDeTempsForm(request.POST)
        if form.is_valid():
            emploi_de_temps = form.save()
            return redirect('ajouter_activites', emploi_de_temps.pk)
    else:
        form = EmploiDeTempsForm()
    return render(request, 'creer_emploi_de_temps.html', {
        'filieres': filieres,
        'form': form
    })

@login_required
def ajouter_activites(request, emploi_de_temps_id):
    emploi_de_temps = EmploiDeTemps.objects.get(id=emploi_de_temps_id)
    activites_jour = ActiviteJour.objects.filter(emploi_de_temps__id=emploi_de_temps_id)
    if request.method == "POST":
       form = ActiviteJourForm(request.POST)
       if form.is_valid():
            activitejour = form.save(commit=False)
            activitejour.emploi_de_temps = emploi_de_temps
            activitejour.save()
            return redirect('ajouter_activites', emploi_de_temps.id) 
    else:
        form = ActiviteJourForm()
    return render(request, 'ajouter_activites.html', {
        'form': form,
        'activites_jour':activites_jour
    })

@login_required    
def afficher_emploi_de_temps(request, emploi_de_temps_id):
    emploi_de_temps = EmploiDeTemps.objects.get(id=emploi_de_temps_id)
    activites_jour = ActiviteJour.objects.filter(emploi_de_temps=emploi_de_temps)
   
    return render(request, 'afficher_emploi_de_temps.html', {
        'emploi_de_temps': emploi_de_temps,
        'activites_jour': activites_jour, 
    })


    


@login_required
def professeur(request):
    if request.method == 'POST':
        nom = request.POST.get('last_name') 
        prenom = request.POST.get('first_name') 
        email = request.POST.get('email')
        age= request.POST.get('age')  
        specialite = request.POST.get('specialite') 
        numero = request.POST.get('numero')
        password = request.POST.get('password')
        print(nom, prenom, age, specialite, numero)
        user=User.objects.create(first_name=prenom, last_name=nom, email=email, password=password)
        user.save() 
        professeur=Professeur.objects.create(age=age, specialite=specialite, numero=numero, user=user)
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
        email = request.POST.get('email') 
        specialite = request.POST.get('specialite')
        numero = request.POST.get('numero') 
        password = request.POST.get('password')
        user.first_name = nom
        user.last_name = prenom
        user.email = email
        user.password = password
        user.save()
        professeur.age = age
        professeur.specialite = specialite
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



@login_required
def parametre_utilisateur(request):
    # Vérifier si les paramètres de l'utilisateur existent, sinon les créer
    parametres, created = ParametreUtilisateur.objects.get_or_create(utilisateur=request.user)

    if request.method == 'POST':
        form = ParametreUtilisateurForm(request.POST, request.FILES, instance=parametres)
        if form.is_valid():
            form.save()
            return redirect('parametres_utilisateur')
    else:
        form = ParametreUtilisateurForm(instance=parametres)

    return render(request, 'parametres_utilisateur.html', {'form': form, 'parametres': parametres})


@login_required
def scolarite(request):
    students = Student.objects.all()
    if request.method == 'POST':
        st_id = request.POST.get('student')
        student = Student.objects.get(id=st_id)
        tranche = request.POST.get('tranche')
        date_paiement = request.POST.get('date_paiement')
        heure_paiement = request.POST.get('heure_paiement')
        montant_total = request.POST.get('montant_total')
        montant_verse = request.POST.get('montant_verse')
        scolarite=PaiementScolarite.objects.create(student=student, tranche=tranche, date_paiement=date_paiement, heure_paiement=heure_paiement, montant_total=montant_total, montant_verse=montant_verse)
        scolarite.save()
        return redirect('afficher_scolarite')
    return render(request, 'scolarite.html', {'students': students})

@login_required
def afficher_scolarite(request):
    paiements = PaiementScolarite.objects.all().order_by('date_paiement')
    return render(request, 'afficher_scolarite.html', {'paiements': paiements})

@login_required
def imprimer_scolarite(request, pk):
    paiement = get_object_or_404(PaiementScolarite, pk=pk)
    return render(request, 'imprimer_scolarite.html', {'paiement': paiement})


@login_required
def filiere(request):
    if request.method == 'POST':
        departement = request.POST.get('departement') 
        nom = request.POST.get('nom') 
        print(departement, nom) 
        filiere=Filiere.objects.create(departement=departement, nom=nom)
        filiere.save()
        return redirect('liste_filiere')
    return render(request, 'filiere.html') 

@login_required
def liste_filiere(request):
    filieres= Filiere.objects.filter(active=True)
    return render(request,'liste_filiere.html',  {'filieres': filieres})


@login_required
def desactiver_filiere(request, filiere_id):
    filiere = get_object_or_404(Filiere, id=filiere_id) 
    if filiere.active:
        filiere.active=False
    filiere.save()
    messages.success(request,"Désactivation réussie") 
    return redirect('liste_filiere') 

@login_required
def statistiques(request):
    labels = []
    data = []
    sessions = Stat.objects.all().values('nom_session').order_by('date_session')
    inscrits = Stat.objects.all().values('inscrits').order_by('date_session')
    print(type(sessions))
    for i in sessions:
        labels.append(i['nom_session'])
        
    for i in inscrits:
        data.append(i['inscrits'])
    
    context = {
        'labels': labels,
        'data': data,
    }
    return render(request,'statistiques.html', context)

@login_required
def ajout_stat(request):
    if request.method == 'POST':
        date_session = request.POST.get('date_session') 
        nom_session = request.POST.get('nom_session') 
        inscrits = request.POST.get('inscrits') 
        print(date_session, nom_session, inscrits) 
        statistiques=Stat.objects.create(date_session=date_session, nom_session=nom_session, inscrits=inscrits)
        statistiques.save()
        return redirect('statistiques')
    return render(request, 'ajout_stat.html') 








