from django.urls import path
from . import views
# Vues synthétiques pour les sujets/messages d'un enseignant
path('forum/mes-sujets/', views.sujets_liste, name='sujets_liste'),
path('forum/mes-sujets/detail/', views.sujets_detail, name='sujets_detail'),
from django.urls import path
from . import views
from django.urls import path

from .views import SujetCreateView, SujetListView, SujetDetailView, notifications, marquer_notif_lue

urlpatterns = [
    path('', views.acceuil, name='base'),
    path('connexion/', views.connexion, name='connexion'),
    path('ajout_session/', views.ajout_session, name='ajout_session'),
    path('choix_session/', views.choix_session, name='choix_session'),
    path('ajouterEtudiant/<int:session_id>', views.ajouterEtudiant, name='ajouterEtudiant'),
    path('listeEtudiant', views.listeEtudiant, name='listeEtudiant'),
    path('rechercher_etudiants/', views.rechercher_etudiants, name='rechercher_etudiants'),
    path('desactiver_utilisateur/<int:user_id>', views.desactiver_utilisateur, name='desactiver_utilisateur'),
    path('edit_user/<int:user_id>', views.edit_user, name='edit_user'),
    path('creer_emploi_de_temps', views.creer_emploi_de_temps, name='creer_emploi_de_temps'), 
    path('ajouter_activites/<int:emploi_de_temps_id>', views.ajouter_activites, name='ajouter_activites'),
    path('afficher_emploi_de_temps/<int:emploi_de_temps_id>', views.afficher_emploi_de_temps, name='afficher_emploi_de_temps'),
    path('supprimer_activite/<int:activite_id>', views.supprimer_activite_et_emploi, name='supprimer_activite'),
    path('pdf_emploi.html/<int:emploi_de_temps_id>', views.imprimer_emploi_de_temps, name='pdf_emploi.html'),
    path('deconnexion', views.deconnexion, name='deconnexion'),
    path('professeur', views.professeur, name='professeur'),
    path('listeProf', views.listeProf, name='listeProf'),
    path('desactiver_professeur/<int:user_id>', views.desactiver_professeur, name='desactiver_professeur'),
    path('edit_prof/<int:user_id>', views.edit_prof, name='edit_prof'),
    path('compte/<int:user_id>', views.compte, name='compte'),
    path('edit_compte/<int:user_id>', views.edit_compte, name='edit_compte'),
    path('scolarite', views.scolarite, name='scolarite'),
    path('afficher_scolarite', views.afficher_scolarite, name='afficher_scolarite'),
    path('imprimer_scolarite/<int:pk>', views.imprimer_scolarite, name='imprimer_scolarite'),
    path('supprimer_paiement/<int:pk>/', views.supprimer_paiement, name='supprimer_paiement'),
    path('filiere', views.filiere, name='filiere'),
    path('liste_filiere', views.liste_filiere, name='liste_filiere'),
    path('desactiver_filiere/<int:filiere_id>', views.desactiver_filiere, name='desactiver_filiere'),
    path('matiere', views.matiere, name='matiere'),
    path('liste_matiere', views.liste_matiere, name='liste_matiere'),
   
    path('desactiver_matiere/<int:matiere_id>/', views.desactiver_matiere, name='desactiver_matiere'),
    path('salle', views.salle, name='salle'),
    path('liste_salle', views.liste_salle, name='liste_salle'),
    path('desactiver_salle/<int:salle_id>/', views.desactiver_salle, name='desactiver_salle'),
    path('generer-statistiques/', views.generer_statistiques, name='generer_statistiques'),
    path('statistiques/', views.afficher_statistiques, name='afficher_statistiques'),
    # Forum de discussion éducatif
    path('forum/creer/', SujetCreateView.as_view(), name='sujet_create'),
    path('forum/filiere/<int:filiere_id>/', SujetListView.as_view(), name='sujet_list'),
    path('forum/sujet/<int:pk>/', SujetDetailView.as_view(), name='sujet_detail'),
    path('forum/sujet/<int:pk>/modifier/', views.SujetUpdateView.as_view(), name='sujet_update'),
    path('forum/sujet/<int:pk>/supprimer/', views.SujetDeleteView.as_view(), name='sujet_delete'),
    # Forum commentaires
    path('forum/commentaire/<int:pk>/modifier/', views.comment_update, name='comment_update'),
    path('forum/commentaire/<int:pk>/supprimer/', views.comment_delete, name='comment_delete'),
    path('notifications/', notifications, name='notifications'),
    path('notifications/lue/<int:notif_id>/', marquer_notif_lue, name='marquer_notif_lue'),
    path('notifications/supprimer/<int:notif_id>/', views.supprimer_notification, name='supprimer_notification'),
  # Notes
    path('students/', views.StudentFiliereListView.as_view(), name='student_list'),
    path('student/<int:student_id>/add-note/', views.NoteCreateView.as_view(), name='note_create'),
    path('student/<int:pk>/', views.StudentNotesDetailView.as_view(), name='student_notes'),
    path('note/<int:pk>/edit/', views.NoteUpdateView.as_view(), name='note_update'),
    path('note/<int:pk>/delete/', views.NoteDeleteView.as_view(), name='note_delete'),
    path('student/<int:student_id>/pdf/', views.generate_pdf, name='generate_pdf'),
    
    # Présences
    path('presences/', views.ListePresenceListView.as_view(), name='presence_list'),
    path('presences/add/', views.ListePresenceCreateView.as_view(), name='presence_add'),
    path('presences/<int:pk>/', views.ListePresenceDetailView.as_view(), name='presence_detail'),
    path('presences/<int:pk>/edit/', views.ListePresenceUpdateView.as_view(), name='presence_edit'),
    path('presences/<int:pk>/delete/', views.ListePresenceDeleteView.as_view(), name='presence_confirm_delete'),
    path('presences/<int:pk>/print/', views.ListePresencePrintView.as_view(), name='presence_print'),
    path('api/get_etudiants/', views.get_etudiants_by_filiere, name='get_etudiants'),
    
    # Attestations
    path('attestations/', views.AttestationListView.as_view(), name='attestation_list'),
    path('attestations/add/', views.AttestationCreateView.as_view(), name='attestation_add'),
    path('attestations/<int:pk>/', views.AttestationDetailView.as_view(), name='attestation_detail'),
    path('attestations/<int:pk>/edit/', views.AttestationUpdateView.as_view(), name='attestation_edit'),
    path('attestations/<int:pk>/delete/', views.AttestationDeleteView.as_view(), name='attestation_delete'),
    path('attestations/<int:pk>/print/', views.AttestationPrintView.as_view(), name='attestation_print')
]