from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from auth_app.models import User, Student
from django.contrib.auth.forms  import UserCreationForm
from .form import CustomUserCreationForm
from django.contrib import messages
from .form import CoursForm, EmploiDeTempsForm, CommentaireForm, ActiviteJourForm
from .models import Cours, Commentaire, EmploiDeTemps, Professeur, PaiementScolarite, Filiere, ActiviteJour, Stat, Session



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

def connexion(request):
    if request.method == 'POST':
      username = request.POST['username']
      password = request.POST['password']
      user = authenticate(request, username=username, password=password)
      if user is not None:
       login(request, user)
       return redirect('base')
    else:
       messages.error(request, 'Username ou mot de passe incorrect.')
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
        return redirect('ajouterEtudiant')
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
        user=User.objects.create(first_name=prenom, last_name=nom, email=email, password=password)
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
        nom = request.POST.get('nom') 
        prenom = request.POST.get('prenom') 
        email = request.POST.get('email')
        age= request.POST.get('age')  
        specialite = request.POST.get('specialite') 
        numero = request.POST.get('numero')
        password = request.POST.get('password')
        print(nom, prenom, age, specialite, numero)
        user=User.objects.create(first_name=prenom, last_name=nom, email=email, password=password)
        user.save() 
        professeur=Professeur.objects.create(age=age, specialite=specialite, numero=numero, user=user)
        Professeur.save()
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