# Atelier 3 : La voix et l'image
**Machine Learning Appliqué · 3e année DSI**

## Présentation de la mission
Dans la continuité de l'Atelier 2, le guichet de support client reçoit désormais des **messages vocaux** (laissés sur le répondeur) et des **captures d'écran** (envoyées via l'application). Notre classifieur textuel retenu à l'atelier 2 (`qwen/qwen3.8-27b`) ne lisant que du texte, nous intégrons :
1. **Un modèle audio (Whisper)** pour transformer la parole en texte via une chaîne séquentielle à deux étages (Audio → Whisper → Texte → Classifieur → Catégorie).
2. **Un modèle de vision multimodal (`qwen/qwen3.8-27b`)** capable d'analyser directement une capture d'écran de bout en bout (Capture PNG + Consigne → Modèle → Catégorie).

---

## Architecture des chaînes de traitement

### Chaîne séquentielle (Voix)
```
  Message vocal (.mp3)
          │
          ▼
┌───────────────────┐
│   Whisper (ASR)   │ ──► Mesuré par le WER (Word Error Rate)
└───────────────────┘
          │ Texte transcrit
          ▼
┌───────────────────┐
│ Classifieur Texte │ ──► Mesuré par le Macro-F1
└───────────────────┘
          │
          ▼
      Catégorie (facturation, technique, compte, commercial)
```

### Modèle End-to-End (Image)
```
  Capture d'écran (.png) + Consigne
                 │
                 ▼
┌─────────────────────────────────┐
│ Modèle de vision multimodal     │ ──► Mesuré par le Macro-F1
│ (qwen/qwen3.8-27b)              │
└─────────────────────────────────┘
                 │
                 ▼
             Catégorie
```

---

## Structure du projet

```
atelier3/
├── .gitignore                          # Exclusion des fichiers temporaires et des rapports PDF
├── README.md                           # Documentation complète de l'atelier
├── code/
│   ├── classifieur.py                  # Module de classification textuelle (Atelier 2)
│   ├── comparer.py                     # Script de synthèse comparative des 3 canaux
│   ├── evaluation.py                   # Fonctions de calcul des métriques (Accuracy, Macro-F1, Confusion)
│   ├── evaluer_images.py               # Évaluation du modèle de vision sur les 20 captures
│   ├── evaluer_voix.py                 # Évaluation sur texte brut et audio Whisper
│   ├── generer_rapport_pdf.py          # Script de génération du rapport PDF des captures
│   ├── propagation.py                  # Étape 4 : Matrice de propagation des erreurs (Texte vs Audio)
│   ├── test_propagation.py             # Test unitaire de validation de propagation()
│   ├── test_wer.py                     # Test unitaire de validation de normaliser()
│   ├── transcription.py                # Étape 1 : Appel de Whisper avec gestion de la langue
│   ├── verifier_enregistrements.py     # Contrôle d'intégrité des enregistrements
│   ├── vision.py                       # Étape 5 : Classification d'image de bout en bout
│   └── wer.py                          # Étape 2 : Normalisation et calcul du Word Error Rate
├── data/
│   ├── captures/                       # 20 captures d'écran de l'application (PNG)
│   ├── voix/                           # 72 messages vocaux synthétisés (MP3)
│   ├── images.csv                      # Métadonnées et annotations des captures
│   ├── messages.csv                    # Métadonnées, textes oraux et catégories des 72 tickets
│   └── classifications/                # Caches locaux de prédictions
└── resultats/
    ├── texte.json                      # Évaluation sur texte lu de référence
    ├── voix__whisper-large-v3-turbo__fr.json  # Évaluation sur voix transcrite par Whisper
    └── image__qwen_qwen3.8-27b.json    # Évaluation sur captures d'écran
```

---

## Résultats expérimentaux et Synthèse

### 1. Tableau comparatif des trois canaux (`python comparer.py`)

| Canal | Modèle | Langue | WER | Macro-F1 | Invalides | Support (n) | Latence moyenne | Coût indicatif |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Image** | `qwen/qwen3.8-27b` | — | — | **1.000** | 0.000 | 20 | 5.58 s | 1 appel lourd (~2 000 tokens / image) |
| **Texte** | `qwen/qwen3.8-27b` | — | — | **0.959** | 0.000 | 72 | 0.49 s | 1 appel LLM (~300 tokens) - Le plus économique |
| **Voix** | `whisper-turbo` + `qwen 27b` | `fr` | **0.009** | **0.932** | 0.000 | 72 | 1.66 s | 2 appels (Audio facturé + LLM texte) |

*Règle de sensibilité : 1 ticket sur 72 = 1,4 point de macro-F1 ; 1 image sur 20 = 5 points.*

---

### 2. Propagation des erreurs (`python propagation.py whisper-large-v3-turbo`)

```
                voix juste  voix fausse
texte juste             67            2
texte faux               0            3
```
* **Tickets perdus à cause de l'audio :** 2 sur 72.
* **Tickets gagnés par hasard :** 0.

#### Analyse des deux tickets perdus :
1. **Ticket T023 (`compte` → prédit `technique`) :**
   * *Lu :* `Le code de vérification par SMS n'arrive pas sur mon nouveau numéro.`
   * *Entendu par Whisper :* `Le code de vérification par SMS ne fonctionne pas sur mon équipement.`
   * *Explication :* La déformation de la mention du numéro en *« ne fonctionne pas sur mon équipement »* fait disparaître le contexte d'accès au compte et introduit un lexique matériel/panne, orientant le classifieur vers `technique`.
2. **Ticket T055 (`facturation` → prédit `compte`) :**
   * *Lu :* `Bonjour, je n'ai pas reçu ma facture du mois de février par mail, pouvez-vous me la renvoyer ?`
   * *Entendu par Whisper :* `Bonjour, je n'ai pas reçu mon accès du mois de février par mail, pouvez-vous me le renvoyer ?`
   * *Explication :* Le mot-clé financier *« facture »* a été remplacé par *« accès »*. Le classifieur n'a fait que catégoriser le texte reçu : l'erreur provient intégralement de l'étage ASR (Whisper).

---

## Réponses aux questions de conclusion

### A. Quel canal donne le meilleur résultat ? Justifiez avec une mesure.
Le canal **Image** obtient le score le plus élevé avec un Macro-F1 parfait de **1.000** (20/20 bien classées), suivi par le canal **Texte** avec un Macro-F1 de **0.959** sur 72 tickets. Le canal **Voix** obtient **0.932** : bien que le WER soit très faible (0.009, soit moins de 1% d'erreur mot), la perte de 2 tickets clés sur des termes critiques entraîne une baisse de 2,7 points de Macro-F1.

### B. Pour la voix, les erreurs viennent-elles de la transcription ou de la classification ?
Les erreurs viennent de la **transcription (Whisper)**. Sur les tickets perdus, le classifieur avait parfaitement trouvé la bonne catégorie quand on lui soumettait le texte de référence d'origine. C'est l'étage de transcription qui a altéré les termes distinctifs (ex: *facture* déformé en *accès*), propageant une mauvaise information au modèle aval.

### C. Quelles vérifications faudrait-il faire avant d’utiliser ce système dans un vrai guichet ?
1. **Évaluation acoustique en conditions réelles :** Tester sur des voix réelles avec accents divers, bruits de fond, mauvaise qualité de ligne et débit rapide.
2. **Mécanisme de confiance et de repli (Fallback) :** Mettre en place un seuil de probabilité/confiance pour router les cas ambigus vers un agent humain plutôt que de risquer un mauvais aiguillage.
3. **Sécurité et RGPD :** Filtrer et caviarder automatiquement les données bancaires et personnelles (numéros de carte, mots de passe) avant envoi vers les API externes.

---

## Installation et Exécution

```bash
# Prérequis
python -m pip install groq jiwer mutagen reportlab

# Définition de la clé API
export GROQ_API_KEY="gsk_votre_cle"

# Tests unitaires
cd code
python test_wer.py
python test_propagation.py

# Évaluations
python evaluer_voix.py texte
python evaluer_voix.py whisper-large-v3-turbo
python evaluer_images.py

# Bilan comparatif
python comparer.py
```
