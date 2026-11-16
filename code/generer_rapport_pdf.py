import os, sys
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Preformatted
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#475569"))
        
        # En-tête (sauf page 1)
        if self._pageNumber > 1:
            self.drawString(40, 810, "Machine Learning Appliqué · Atelier 3 — La voix et l'image")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)
            self.line(40, 804, 555, 804)
            
        # Pied de page
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(40, 45, 555, 45)
        self.drawString(40, 32, "Rapport d'exécution, captures de tests et preuves expérimentales")
        self.drawRightString(555, 32, f"Page {self._pageNumber} sur {page_count}")
        self.restoreState()

def creer_bloc_terminal(titre, commande, sortie, duree=None):
    """Crée un bloc visuel sous forme de tableau hermétique simulant un terminal"""
    titre_text = f"<font color='#CBD5E1'>● ● ●</font>&nbsp;&nbsp;&nbsp;<b>{titre}</b>"
    if duree:
        titre_text += f"&nbsp;&nbsp;&nbsp;<font color='#94A3B8'><i>[Durée réelle : {duree}]</i></font>"
        
    header_p = Paragraph(titre_text, ParagraphStyle(
        'TermHeader',
        fontName='Helvetica',
        fontSize=8.5,
        textColor=colors.white,
    ))
    
    prompt = "PS C:\\Users\\MRAET MOHAMED AZIZ\\Desktop\\dsi3\\machine learning\\atelier3> "
    contenu = f"{prompt}{commande}\n\n{sortie.strip()}"
    
    body_pre = Preformatted(contenu, ParagraphStyle(
        'TermBody',
        fontName='Courier',
        fontSize=7.0,
        leading=9.2,
        textColor=colors.HexColor("#000000"),
    ))
    
    t = Table([[header_p], [body_pre]], colWidths=[515])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#1E293B")),
        ('TOPPADDING', (0,0), (0,0), 4),
        ('BOTTOMPADDING', (0,0), (0,0), 4),
        ('LEFTPADDING', (0,0), (0,0), 10),
        ('RIGHTPADDING', (0,0), (0,0), 10),
        
        ('BACKGROUND', (0,1), (0,1), colors.HexColor("#F8FAFC")),
        ('TOPPADDING', (0,1), (0,1), 6),
        ('BOTTOMPADDING', (0,1), (0,1), 6),
        ('LEFTPADDING', (0,1), (0,1), 10),
        ('RIGHTPADDING', (0,1), (0,1), 10),
        
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#64748B")),
        ('LINEBELOW', (0,0), (0,0), 1, colors.HexColor("#64748B")),
    ]))
    return KeepTogether([t, Spacer(1, 8)])

def generer_pdf(chemin_sortie):
    doc = SimpleDocTemplate(
        chemin_sortie,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=50,
        bottomMargin=55
    )
    
    titre_style = ParagraphStyle(
        'TitreDoc',
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=10
    )
    
    h1_style = ParagraphStyle(
        'H1',
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=14.5,
        textColor=colors.HexColor("#1E40AF"),
        spaceBefore=8,
        spaceAfter=5,
        keepWithNext=True
    )
    
    p_style = ParagraphStyle(
        'Paragraphe',
        fontName='Helvetica',
        fontSize=8.2,
        leading=11.0,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=6
    )

    story = []

    # En-tête de couverture
    story.append(Paragraph("Atelier 3 : La voix et l'image", titre_style))
    story.append(Paragraph("<b>Machine Learning Appliqué · 3e année DSI</b> — Évaluation comparée des canaux Texte, Voix (Whisper ASR) et Image (Vision Multimodale Qwen). Preuves complètes d'exécution et tests.", p_style))
    story.append(Spacer(1, 6))

    # SECTION 1 : Transcrire un message vocal
    story.append(Paragraph("1. Étape 1 — Transcrire un message vocal avec Whisper", h1_style))
    story.append(Paragraph("Implémentation de <code>transcrire()</code> dans <code>transcription.py</code> (lecture binaire, température 0, paramètre <code>language</code>).", p_style))

    story.append(creer_bloc_terminal(
        "Capture 1 : Transcription en français imposé (T016.mp3)",
        "python .\\code\\transcription.py ..\\data\\voix\\T016.mp3",
        "Ma facture de mars est de 89 euros alors que mon forfait est à 39 euros. Pouvez-vous m'expliquer la différence ?\n(0.6 s)",
        duree="0.6s"
    ))

    story.append(creer_bloc_terminal(
        "Capture 2 : Transcription courte avec détection automatique (T006.mp3)",
        "python .\\code\\transcription.py ..\\data\\voix\\T006.mp3 whisper-large-v3-turbo auto",
        "Stop. Thank you.\n(0.5 s)",
        duree="0.5s"
    ))

    story.append(Paragraph("<b>Rôle du paramètre language='fr' :</b> Sur un enregistrement court ou bruité (qualité téléphone), le mode <code>auto</code> tente de deviner la langue sur les premières secondes et peut halluciner ou traduire vers l'anglais (ex: <i>Stop. Thank you.</i>). Imposer explicitement <code>language='fr'</code> garantit une transcription déterministe en français et réduit drastiquement le WER.", p_style))

    story.append(Spacer(1, 4))

    # SECTION 2 : Calculer le WER
    story.append(Paragraph("2. Étape 2 — Calculer le WER et valider la normalisation", h1_style))
    story.append(Paragraph("Correction du bug d'import circulaire (<code>import re</code>) et implémentation de <code>normaliser()</code> dans <code>wer.py</code>.", p_style))

    story.append(creer_bloc_terminal(
        "Capture 3 : Test unitaire de la fonction normaliser() (test_wer.py)",
        "python .\\code\\test_wer.py",
        "8/8 tests reussis"
    ))

    story.append(creer_bloc_terminal(
        "Capture 4 : Calcul du WER brut vs normalisé et alignement mot à mot (wer.py)",
        "python .\\code\\wer.py",
        "brut       : 0.545\n"
        "normalise  : 0.083\n"
        "REF: ma facture de mars est de 89 euros pouvez vous m expliquer\n"
        "HYP: ma facture de mars  et de 89 euros pouvez vous m expliquer\n"
        "                          S                                    "
    ))

    story.append(Paragraph("<b>Impact de la normalisation :</b> Le WER chute de <b>0.545</b> à <b>0.083</b>. Sur les 6 erreurs brutes, 5 provenaient uniquement de la ponctuation, des majuscules et du symbole € (remplacé par <i>euros</i>). Seule 1 erreur d'écoute réelle subsiste (substitution : <i>est</i> → <i>et</i>).", p_style))

    story.append(PageBreak())

    # SECTION 3 : Évaluer la chaîne vocale
    story.append(Paragraph("3. Étape 3 — Évaluer la chaîne vocale (Texte lu vs Whisper)", h1_style))
    story.append(Paragraph("Évaluation sur les 72 tickets de référence avec le classifieur <code>qwen/qwen3.8-27b</code>.", p_style))

    story.append(creer_bloc_terminal(
        "Capture 5 : Évaluation du texte lu de référence (evaluer_voix.py texte)",
        "python .\\code\\evaluer_voix.py texte",
        "=== texte lu -> qwen/qwen3.8-27b ===\n"
        "accuracy    : 0.958\n"
        "macro-F1    : 0.959\n"
        "invalides   : 0.000\n\n"
        "categorie      precision   recall      F1     n\n"
        "facturation        0.917    1.000   0.957    22\n"
        "technique          1.000    0.900   0.947    20\n"
        "compte             0.941    1.000   0.970    16\n"
        "commercial         1.000    0.929   0.963    14\n\n"
        "Confusion matrix (lignes = verite, colonnes = prediction)\n"
        "                    factur       techni       compte       commer       invali\n"
        "facturation             22            0            0            0            0\n"
        "technique                1           18            1            0            0\n"
        "compte                   0            0           16            0            0\n"
        "commercial               1            0            0           13            0\n\n"
        "latence moyenne par ticket : 0.49 s\n"
        "resultat enregistre dans resultats\\texte.json"
    ))

    story.append(creer_bloc_terminal(
        "Capture 6 : Évaluation de la chaîne vocale complète (Whisper Turbo + Classifieur)",
        "python .\\code\\evaluer_voix.py whisper-large-v3-turbo",
        "WER sans normalisation : 0.010\n"
        "WER normalise          : 0.009\n"
        "   voix fr      : 0.003  (24 messages)\n"
        "   voix mb-fr1  : 0.008  (24 messages)\n"
        "   voix mb-fr4  : 0.017  (24 messages)\n"
        "secondes audio facturees : 725\n\n"
        "=== whisper-large-v3-turbo (fr) -> qwen/qwen3.8-27b ===\n"
        "accuracy    : 0.931\n"
        "macro-F1    : 0.932\n"
        "invalides   : 0.000\n\n"
        "categorie      precision   recall      F1     n\n"
        "facturation        0.913    0.955   0.933    22\n"
        "technique          0.947    0.900   0.923    20\n"
        "compte             0.882    0.938   0.909    16\n"
        "commercial         1.000    0.929   0.963    14\n\n"
        "Confusion matrix (lignes = verite, colonnes = prediction)\n"
        "                    factur       techni       compte       commer       invali\n"
        "facturation             21            0            1            0            0\n"
        "technique                1           18            1            0            0\n"
        "compte                   0            1           15            0            0\n"
        "commercial               1            0            0           13            0\n\n"
        "latence moyenne par message : 1.66 s (Whisper 1.15 s + classification 0.51 s)\n"
        "resultat enregistre dans resultats\\voix__whisper-large-v3-turbo__fr.json"
    ))

    story.append(PageBreak())

    # SECTION 4 : Propagation des erreurs
    story.append(Paragraph("4. Étape 4 — Observer la propagation des erreurs", h1_style))
    story.append(Paragraph("Classification matricielle des transitions entre prédiction texte et prédiction vocale.", p_style))

    story.append(creer_bloc_terminal(
        "Capture 7 : Test unitaire de propagation() (test_propagation.py)",
        "python .\\code\\test_propagation.py",
        "4/4 cases correctes"
    ))

    story.append(creer_bloc_terminal(
        "Capture 8 : Analyse de la propagation d'erreurs (propagation.py)",
        "python .\\code\\propagation.py whisper-large-v3-turbo",
        "                voix juste  voix fausse\n"
        "texte juste             67            2\n"
        "texte faux               0            3\n\n"
        "2 tickets perdus a cause de l'audio, 0 gagnes par hasard, sur 72.\n\n"
        "T023  [compte]  voix -> technique   WER du message 0.31\n"
        "   lu      : Le code de vérification par SMS n'arrive pas sur mon nouveau numéro.\n"
        "   entendu : Le code de vérification par SMS ne fonctionne pas sur mon équipement.\n\n"
        "T055  [facturation]  voix -> compte   WER du message 0.16\n"
        "   lu      : Bonjour, je n'ai pas reçu ma facture du mois de février par mail, pouvez-vous me la renvoyer ?\n"
        "   entendu : Bonjour, je n'ai pas reçu mon accès du mois de février par mail, pouvez-vous me le renvoyer ?"
    ))

    story.append(Paragraph("<b>Analyse détaillée des deux tickets perdus :</b><br/>"
                           "• <b>Ticket T023 :</b> Le message original portait sur la réception d'un code SMS sur un nouveau numéro (catégorie <i>compte</i>). Whisper a transcrit <i>'ne fonctionne pas sur mon équipement'</i>. Le terme <i>'équipement'</i> a réorienté le classifieur vers une panne matérielle (<i>technique</i>).<br/>"
                           "• <b>Ticket T055 :</b> Le mot-clé <i>'facture'</i> a été altéré en <i>'accès'</i>. Privé de la notion financière, le classifieur a interprété la demande comme un problème d'accès personnel (<i>compte</i>).<br/>"
                           "<b>Conclusion :</b> Le classifieur n'est pas défaillant ; il a classé fidèlement le texte reçu. L'erreur provient entièrement de l'étage ASR (Whisper).", p_style))

    story.append(PageBreak())

    # SECTION 5 : Vision end-to-end
    story.append(Paragraph("5. Étape 5 — Classer une capture d'écran avec un modèle de vision (End-to-End)", h1_style))
    story.append(Paragraph("Modèle <code>qwen/qwen3.8-27b</code> traitant directement l'image et la consigne en un seul appel.", p_style))

    story.append(creer_bloc_terminal(
        "Capture 9 : Test ponctuel de classification d'une capture (vision.py)",
        "python .\\code\\vision.py ..\\data\\captures\\I06.png",
        "facturation"
    ))

    story.append(creer_bloc_terminal(
        "Capture 10 : Évaluation globale des 20 captures (evaluer_images.py)",
        "python .\\code\\evaluer_images.py",
        "1/20 captures ... 20/20 captures\n\n"
        "=== captures -> qwen/qwen3.8-27b ===\n"
        "accuracy    : 1.000\n"
        "macro-F1    : 1.000\n"
        "invalides   : 0.000\n\n"
        "categorie      precision   recall      F1     n\n"
        "facturation        1.000    1.000   1.000     5\n"
        "technique          1.000    1.000   1.000     5\n"
        "compte             1.000    1.000   1.000     5\n"
        "commercial         1.000    1.000   1.000     5\n\n"
        "Confusion matrix (lignes = verite, colonnes = prediction)\n"
        "                    factur       techni       compte       commer       invali\n"
        "facturation              5            0            0            0            0\n"
        "technique                0            5            0            0            0\n"
        "compte                   0            0            5            0            0\n"
        "commercial               0            0            0            5            0\n\n"
        "Captures mal classees : Aucune\n\n"
        "latence moyenne par capture : 5.58 s\n"
        "resultat enregistre dans resultats\\image__qwen_qwen3.8-27b.json"
    ))

    story.append(Spacer(1, 4))

    # SECTION 6 : Comparaison des trois canaux
    story.append(Paragraph("6. Étape 6 — Comparaison globale des trois canaux (comparer.py)", h1_style))
    story.append(Paragraph("Mise en perspective des performances de classification, de la latence et du coût estimé.", p_style))

    story.append(creer_bloc_terminal(
        "Capture 11 : Synthèse comparative des canaux (comparer.py)",
        "python .\\code\\comparer.py",
        "canal   modele                   langue      WER  macro-F1  invalides    n  latence\n"
        "-------------------------------------------------------------------------------------\n"
        "image   qwen/qwen3.8-27b         -             -     1.000      0.000   20    5.58s\n"
        "texte   -                        -             -     0.959      0.000   72    0.49s\n"
        "voix    whisper-large-v3-turbo   fr        0.009     0.932      0.000   72    1.66s\n\n"
        "1 ticket sur 72 = 1,4 point de macro-F1 ; 1 image sur 20 = 5 points."
    ))

    # Tableau récapitulatif stylé
    tableau_data = [
        ["Canal", "Modèle(s)", "Qualité", "Latence moyenne", "Coût indicatif"],
        ["Texte", "Classifieur Qwen 27B", "Macro-F1 : 0.959", "0.49 s / ticket", "1 appel LLM (~300 tokens) - Le plus économique"],
        ["Voix", "Whisper Turbo + Qwen 27B", "WER : 0.009 | Macro-F1 : 0.932", "1.66 s / ticket (1.15s ASR + 0.51s LLM)", "2 appels (Audio facturé + LLM texte)"],
        ["Image", "Qwen 27B Multimodal (End-to-End)", "Macro-F1 : 1.000", "5.58 s / capture", "1 appel lourd (~2 000 tokens / image)"]
    ]
    t_synth = Table(tableau_data, colWidths=[55, 115, 125, 95, 125])
    t_synth.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E40AF")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 7.8),
        ('BOTTOMPADDING', (0,0), (-1,0), 5),
        ('TOPPADDING', (0,0), (-1,0), 5),
        
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F8FAFC")),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 7.2),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#94A3B8")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,1), (-1,-1), 4),
        ('BOTTOMPADDING', (0,1), (-1,-1), 4),
    ]))
    story.append(t_synth)
    story.append(Spacer(1, 8))

    # SECTION 7 : Questions de conclusion
    story.append(Paragraph("7. Réponses aux questions de conclusion", h1_style))
    story.append(Paragraph("<b>A. Quel canal donne le meilleur résultat ? Justifiez avec une mesure.</b><br/>"
                           "Le canal <b>Image</b> obtient un macro-F1 parfait de <b>1.000</b> sur les 20 captures, suivi par le canal <b>Texte</b> (macro-F1 de <b>0.959</b> sur 72 tickets). Le canal <b>Voix</b> arrive en retrait avec un macro-F1 de <b>0.932</b> (perte de 2,7 points de F1 par rapport au texte), démontrant l'impact pénalisant de la chaîne séquentielle où les erreurs acoustiques se répercutent.", p_style))
    story.append(Paragraph("<b>B. Pour la voix, les erreurs viennent-elles de la transcription ou de la classification ?</b><br/>"
                           "La matrice de propagation montre que sur les 2 tickets perdus (T023 et T055), le classifieur avait parfaitement prédit la bonne catégorie lorsque le texte de référence lui était soumis. C'est l'étage <b>Whisper</b> qui a déformé les mots-clés essentiels (ex: <i>facture</i> déformé en <i>accès</i>), induisant en erreur le classifieur aval. L'erreur vient donc de la <b>transcription</b> et de sa propagation.", p_style))
    story.append(Paragraph("<b>C. Quelles vérifications faudrait-il faire avant d’utiliser ce système dans un vrai guichet ?</b><br/>"
                           "1. <b>Robustesse acoustique :</b> Tester sur des voix réelles variées (accents régionaux, bruits ambiants, débit rapide, jargon métier).<br/>"
                           "2. <b>Gestion des ambiguïtés & rejet :</b> Définir un seuil de confiance sous lequel le ticket est redirigé vers un opérateur humain plutôt que classé à tort.<br/>"
                           "3. <b>Supervision et garde-fous :</b> Mettre en place un monitoring continu de la latence, des quotas d'API, et protéger les données sensibles (RGPD, masquage des numéros de carte et mots de passe dans les transcriptions audio).", p_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF généré avec succès : {chemin_sortie}")

if __name__ == "__main__":
    sortie = Path("Captures_Atelier3_Executions.pdf")
    generer_pdf(str(sortie))
