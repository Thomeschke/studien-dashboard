# =============================================================================
# dashboard_app.py – Tkinter-GUI des Studien-Dashboards
# =============================================================================
# Hauptklasse der grafischen Benutzeroberfläche.
# Baut das Fenster mit allen Widgets auf, reagiert auf Benutzereingaben
# und aktualisiert die Anzeige.
# Greift ausschließlich über den StudienController auf die Daten zu.
# =============================================================================

import tkinter as tk
from tkinter import ttk, messagebox

from controller import StudienController
from models import Modul, ModulStatus, SemesterStatus


# ── Farbschema ────────────────────────────────────────────────────────────────
FARBE_HINTERGRUND   = "#FFFFFF"
FARBE_HELL          = "#F5F5F5"
FARBE_RAHMEN        = "#E0E0E0"
FARBE_TEXT          = "#1A1A1A"
FARBE_TEXT_GRAU     = "#666666"
FARBE_AKZENT        = "#2E75B6"
FARBE_GRUEN         = "#27AE60"
FARBE_DUNKELGRUEN   = "#0A6C33"
FARBE_GELB          = "#F39C12"
FARBE_GRAU          = "#BDC3C7"
FARBE_SCHALTFLAECHE = "#2E75B6"
FARBE_SCHALT_TEXT   = "#FFFFFF"
FARBE_FEHLER        = "#FF1900"

SCHRIFT_NORMAL  = ("Arial", 11)
SCHRIFT_KLEIN   = ("Arial", 9)
SCHRIFT_GROSS   = ("Arial", 20, "bold")
SCHRIFT_MITTEL  = ("Arial", 13, "bold")
SCHRIFT_LABEL   = ("Arial", 8)


class DashboardApp:
    """
    Hauptklasse der Tkinter-GUI des Studien-Dashboards.

    Baut das Fenster mit allen Widgets auf und reagiert auf
    Benutzereingaben über Event-Handler-Methoden.
    Greift ausschließlich über den StudienController auf die Daten zu.
    """

    def __init__(self, controller: StudienController):
        self._controller      = controller
        self._ausgewaehltes_modul: Modul | None = None

        # ── Hauptfenster ──────────────────────────────────────────────────
        self._root = tk.Tk()
        self._root.title("Studien-Dashboard – IU Fernstudium B.Sc. Cyber Security")
        self._root.configure(bg=FARBE_HINTERGRUND)
        self._root.resizable(True, True)
        self._root.minsize(900, 600)
        # Startgröße – breit genug für Modulliste + Panel + Bedienungshinweise
        self._root.geometry("1200x850")

        self._widgets_aufbauen()

    # ── Starten ───────────────────────────────────────────────────────────
    def starten(self) -> None:
        """Startet die Tkinter-Hauptschleife."""
        # Progressbalken nach kurzem Delay zeichnen, damit das Canvas seine finale Breite kennt
        self._root.after(100, self.anzeige_aktualisieren)
        self._root.mainloop()

    # ── Aufbau ────────────────────────────────────────────────────────────
    def _widgets_aufbauen(self) -> None:
        """Baut alle Widgets des Dashboards auf."""
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(1, weight=1)
        self._kpi_leiste_aufbauen()
        self._hauptbereich_aufbauen()

    # ── KPI-Leiste ────────────────────────────────────────────────────────
    def _kpi_leiste_aufbauen(self) -> None:
        """Baut die obere KPI-Leiste mit den vier Kennzahlen auf."""
        rahmen = tk.Frame(self._root, bg=FARBE_HELL,
                          relief="flat", bd=0,
                          highlightbackground=FARBE_RAHMEN,
                          highlightthickness=1)
        rahmen.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        rahmen.columnconfigure((0, 1, 2, 3), weight=1)

        # KPI-Kacheln
        self._kpi_durchschnitt, self._kpi_durchschnitt_sub = self._kpi_kachel(
            rahmen, 0, "NOTENDURCHSCHNITT", "–", "aus bestandenen Modulen"
        )
        self._kpi_fortschritt, self._kpi_fortschritt_sub = self._kpi_kachel(
            rahmen, 1, "STUDIENFORTSCHRITT", "Sem. – / –", "– % der Regelstudienzeit",
            mit_progress=True
        )
        self._kpi_module, self._kpi_module_sub = self._kpi_kachel(
            rahmen, 2, "MODULE BESTANDEN", "– / –", "– noch offen"
        )
        self._kpi_regelzeit, _ = self._kpi_kachel(
            rahmen, 3, "REGELSTUDIENZEIT", "8 Sem.", "4 Jahre Fernstudium"
        )

    def _kpi_kachel(self, elternteil, spalte: int,
                    titel: str, wert: str, untertitel: str,
                    mit_progress: bool = False):
        """
        Erstellt eine einzelne KPI-Kachel.
        Gibt Tuple (wert_var, untertitel_var) zurück.
        Mit mit_progress=True wird ein Progressbalken zwischen Wert und
        Untertitel eingefügt (Balken erscheint dann ÜBER dem Untertitel).
        """
        rahmen = tk.Frame(elternteil, bg=FARBE_HELL, padx=20, pady=14)
        rahmen.grid(row=0, column=spalte, sticky="nsew",
                    padx=(0, 1) if spalte < 3 else 0)

        tk.Label(rahmen, text=titel, font=SCHRIFT_LABEL,
                 fg=FARBE_TEXT_GRAU, bg=FARBE_HELL).pack(anchor="w")

        wert_var = tk.StringVar(value=wert)
        # Spalte 0 = Notendurchschnitt → dunkelgrün, alle anderen schwarz
        if spalte == 0:
            wert_farbe = FARBE_DUNKELGRUEN  # Notendurchschnitt: dunkelgrün
        elif spalte == 2:
            wert_farbe = "#E67E22"          # Module bestanden: orange-gelb
        else:
            wert_farbe = FARBE_TEXT         # alle anderen: schwarz
        tk.Label(rahmen, textvariable=wert_var, font=SCHRIFT_GROSS,
                 fg=wert_farbe, bg=FARBE_HELL).pack(anchor="w")

        if mit_progress:
            # Progressbalken zwischen Wert und Untertitel
            self._progress_canvas = tk.Canvas(
                rahmen, height=6, bg=FARBE_RAHMEN,
                highlightthickness=0
            )
            self._progress_canvas.pack(fill="x", pady=(6, 2))

        untertitel_var = tk.StringVar(value=untertitel)
        tk.Label(rahmen, textvariable=untertitel_var, font=SCHRIFT_KLEIN,
                 fg=FARBE_TEXT_GRAU, bg=FARBE_HELL).pack(anchor="w")

        return wert_var, untertitel_var

    def _hauptbereich_aufbauen(self) -> None:
        """Baut den Hauptbereich mit Modulliste (links) und Panel (rechts) auf."""
        rahmen = tk.Frame(self._root, bg=FARBE_HINTERGRUND)
        rahmen.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        rahmen.columnconfigure(0, weight=3)
        rahmen.columnconfigure(1, weight=1)
        rahmen.rowconfigure(0, weight=1)

        self._modulliste_aufbauen(rahmen)
        self._notenpanel_aufbauen(rahmen)

    # ── Modulliste ────────────────────────────────────────────────────────

    def _modulliste_aufbauen(self, elternteil) -> None:
        """Baut die linke Spalte mit der scrollbaren Modulliste auf."""
        rahmen = tk.Frame(elternteil, bg=FARBE_HINTERGRUND,
                          highlightbackground=FARBE_RAHMEN,
                          highlightthickness=1)
        rahmen.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        rahmen.rowconfigure(1, weight=1)
        rahmen.columnconfigure(0, weight=1)

        # Überschrift
        tk.Label(rahmen, text="MODULE – ÜBERSICHT",
                 font=SCHRIFT_KLEIN, fg=FARBE_TEXT_GRAU,
                 bg=FARBE_HINTERGRUND).grid(
            row=0, column=0, sticky="w", padx=14, pady=(10, 4))

        # Scrollbarer Bereich
        canvas = tk.Canvas(rahmen, bg=FARBE_HINTERGRUND,
                           highlightthickness=0)
        scrollbar = ttk.Scrollbar(rahmen, orient="vertical",
                                  command=canvas.yview)
        self._scroll_rahmen = tk.Frame(canvas, bg=FARBE_HINTERGRUND)

        self._scroll_rahmen.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self._scroll_rahmen,
                             anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")

        # Mausrad-Scrolling
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(
                            -1 * (e.delta // 120), "units"))

        self._canvas = canvas

    def _modulliste_aktualisieren(self) -> None:
        """Füllt die Modulliste neu mit aktuellen Daten."""
        # Alte Widgets löschen
        for widget in self._scroll_rahmen.winfo_children():
            widget.destroy()

        if self._controller.studiengang is None:
            return

        # Gruppiert nach Semester und Status
        for sem in self._controller.studiengang.semester:
            # Semester-Überschrift
            sem_farbe = {
                SemesterStatus.BEENDET:  "#27AE60",
                SemesterStatus.LAUFEND:  "#F39C12",
                SemesterStatus.GEPLANT:  FARBE_TEXT_GRAU,
            }.get(sem.status, FARBE_TEXT_GRAU)

            sem_label = (f"SEMESTER {sem.semester_nummer} – "
                         f"{sem.status.value.upper().replace('_', ' ')}")
            tk.Label(self._scroll_rahmen, text=sem_label,
                     font=SCHRIFT_KLEIN, fg=sem_farbe,
                     bg=FARBE_HINTERGRUND).pack(
                anchor="w", padx=14, pady=(12, 2))

            # Module des Semesters
            for modul in sem.module:
                self._modul_zeile_erstellen(modul)

    def _modul_zeile_erstellen(self, modul: Modul) -> None:
        """Erstellt eine einzelne Modulzeile in der Liste."""
        # Farbe des Statuspunkts
        punkt_farbe = {
            ModulStatus.ABGESCHLOSSEN:       FARBE_GRUEN,
            ModulStatus.IN_BEARBEITUNG:      FARBE_GELB,
            ModulStatus.NOCH_NICHT_BEGONNEN: FARBE_GRAU,
        }.get(modul.status, FARBE_GRAU)

        # Hintergrund bei Auswahl
        hintergrund = "#FFD9A3" if modul == self._ausgewaehltes_modul \
                      else FARBE_HINTERGRUND

        zeile = tk.Frame(self._scroll_rahmen, bg=hintergrund,
                         cursor="hand2")
        zeile.pack(fill="x", padx=8, pady=1)

        # Statuspunkt
        tk.Label(zeile, text="●", fg=punkt_farbe,
                 bg=hintergrund, font=("Arial", 10)).pack(
            side="left", padx=(6, 4))

        # Modulname
        tk.Label(zeile, text=modul.name, font=SCHRIFT_NORMAL,
                 fg=FARBE_TEXT, bg=hintergrund,
                 anchor="w").pack(side="left", fill="x", expand=True,
                                  pady=4)

        # Note (rechts) oder Starten-Button
        if modul.status == ModulStatus.ABGESCHLOSSEN and modul.pruefung:
            note_text = f"{modul.pruefung.note:.1f}".replace(".", ",")
            # Bearbeiten-Button
            tk.Button(
                zeile, text="Bearb.",
                font=("Arial", 9),
                fg=FARBE_TEXT_GRAU, bg=FARBE_HINTERGRUND,
                relief="solid", bd=1,
                highlightbackground=FARBE_TEXT_GRAU,
                highlightcolor=FARBE_TEXT_GRAU,
                highlightthickness=0,
                activebackground=FARBE_RAHMEN,
                activeforeground=FARBE_TEXT_GRAU,
                cursor="hand2", padx=8, pady=3,
                command=lambda m=modul: self.note_bearbeiten(m)
            ).pack(side="right", padx=(0, 6))
            tk.Label(zeile, text=note_text, font=SCHRIFT_NORMAL,
                     fg=FARBE_AKZENT, bg=hintergrund,
                     width=5).pack(side="right", padx=(8, 0))

        elif modul.status == ModulStatus.NOCH_NICHT_BEGONNEN:
            btn = tk.Button(
                zeile, text="Starten",
                font=("Arial", 9),
                fg=FARBE_AKZENT, bg=FARBE_HINTERGRUND,
                relief="solid", bd=1,
                highlightbackground=FARBE_AKZENT,
                highlightcolor=FARBE_AKZENT,
                highlightthickness=0,
                activebackground=FARBE_HELL,
                activeforeground=FARBE_AKZENT,
                cursor="hand2", padx=10, pady=3,
                command=lambda m=modul: self.modul_starten(m)
            )
            btn.pack(side="right", padx=10, pady=4)

        elif modul.status == ModulStatus.IN_BEARBEITUNG and modul.pruefung is None:
            # Zurücksetzen-Button für versehentlich gestartete Module
            btn = tk.Button(
                zeile, text="Zurücksetzen",
                font=("Arial", 9),
                fg=FARBE_GELB, bg=FARBE_HINTERGRUND,
                relief="solid", bd=1,
                highlightbackground=FARBE_GELB,
                highlightcolor=FARBE_GELB,
                highlightthickness=0,
                activebackground=FARBE_HELL,
                activeforeground=FARBE_GELB,
                cursor="hand2", padx=8, pady=3,
                command=lambda m=modul: self.modul_zuruecksetzen(m)
            )
            btn.pack(side="right", padx=10, pady=4)

        # Klick auf Zeile → Modul auswählen (nur IN_BEARBEITUNG)
        # Wichtig: Buttons (Zurücksetzen, Bearbeiten) werden ausgenommen, damit deren eigener Command nicht überschrieben wird.
        if modul.status == ModulStatus.IN_BEARBEITUNG:
            zeile.bind("<Button-1>",
                       lambda e, m=modul: self.modul_auswaehlen(m))
            for child in zeile.winfo_children():
                if not isinstance(child, tk.Button):
                    child.bind("<Button-1>",
                               lambda e, m=modul: self.modul_auswaehlen(m))

    # ── Noteneingabe-Panel ────────────────────────────────────────────────

    def _notenpanel_aufbauen(self, elternteil) -> None:
        """Baut das rechte Noteneingabe-Panel auf."""
        rahmen = tk.Frame(elternteil, bg=FARBE_HELL,
                          highlightbackground=FARBE_RAHMEN,
                          highlightthickness=1)
        rahmen.grid(row=0, column=1, sticky="nsew",
                    padx=(5, 10), pady=10)
        rahmen.columnconfigure(0, weight=1)

        tk.Label(rahmen, text="NOTE EINTRAGEN",
                 font=SCHRIFT_KLEIN, fg=FARBE_TEXT_GRAU,
                 bg=FARBE_HELL).pack(anchor="w", padx=14, pady=(12, 4))

        tk.Label(rahmen,
                 text='Wähle ein Modul mit Status "In Bearbeitung" aus,\num Note und Prüfungsdatum einzutragen.',
                 font=SCHRIFT_KLEIN, fg=FARBE_TEXT_GRAU,
                 bg=FARBE_HELL, justify="left").pack(
            anchor="w", padx=14, pady=(0, 8))

        # Ausgewähltes Modul – Platzhalter-Container immer gepackt,
        # aber nur sichtbar wenn ein Modul ausgewählt ist.
        self._var_modul_name = tk.StringVar(value="")
        # Aeusserer Container – immer sichtbar, kein Hintergrund
        self._modul_container = tk.Frame(rahmen, bg=FARBE_HELL)
        self._modul_container.pack(fill="x", padx=14, pady=(0, 0))

        # Innerer Rahmen – initial unsichtbar (keine Farbe, kein Rand)
        # Wird bei Auswahl auf gelb umgefärbt
        self._modul_rahmen = tk.Frame(
            self._modul_container, bg=FARBE_HELL,
            highlightbackground=FARBE_HELL,
            highlightthickness=1
        )
        self._modul_rahmen.pack(fill="x")
        self._label_modul = tk.Label(
            self._modul_rahmen, textvariable=self._var_modul_name,
            font=("Arial", 10, "bold"), fg=FARBE_TEXT,
            bg=FARBE_HELL, wraplength=200, justify="left",
            padx=8, pady=0
        )
        self._label_modul.pack(anchor="w")

        # Noteingabe
        tk.Label(rahmen, text="NOTE", font=SCHRIFT_KLEIN,
                 fg=FARBE_TEXT_GRAU, bg=FARBE_HELL).pack(
            anchor="w", padx=14)
        self._var_note = tk.StringVar()
        tk.Entry(rahmen, textvariable=self._var_note,
                 font=SCHRIFT_NORMAL, width=10).pack(
            anchor="w", padx=14, pady=(2, 10))

        # Datumeingabe
        tk.Label(rahmen, text="PRÜFUNGSDATUM (TT.MM.JJJJ)",
                 font=SCHRIFT_KLEIN, fg=FARBE_TEXT_GRAU,
                 bg=FARBE_HELL).pack(anchor="w", padx=14)
        self._var_datum = tk.StringVar()
        tk.Entry(rahmen, textvariable=self._var_datum,
                 font=SCHRIFT_NORMAL, width=14).pack(
            anchor="w", padx=14, pady=(2, 14))

        # Fehlermeldung
        self._var_fehler = tk.StringVar(value="")
        self._label_fehler = tk.Label(
            rahmen, textvariable=self._var_fehler,
            font=SCHRIFT_KLEIN, fg=FARBE_FEHLER,
            bg=FARBE_HELL, wraplength=200, justify="left"
        )
        self._label_fehler.pack(anchor="w", padx=14, pady=(0, 4))

        # Speichern-Button
        self._btn_speichern = tk.Button(
            rahmen,
            text="Note speichern → Abgeschlossen",
            font=("Arial", 10, "bold"),
            fg=FARBE_TEXT_GRAU, bg=FARBE_RAHMEN,
            disabledforeground=FARBE_TEXT_GRAU,
            relief="flat", padx=10, pady=8, cursor="hand2",
            command=self.note_speichern,
            state="disabled"
        )
        self._btn_speichern.pack(fill="x", padx=14, pady=(0, 8))

        # Auswahl aufheben
        tk.Button(
            rahmen, text="Auswahl aufheben",
            font=SCHRIFT_KLEIN, fg=FARBE_TEXT_GRAU,
            bg=FARBE_HELL, relief="flat", cursor="hand2",
            command=self.auswahl_aufheben
        ).pack(anchor="w", padx=14)

        # ── Trennlinie ────────────────────────────────────────────────────
        tk.Frame(rahmen, bg=FARBE_RAHMEN, height=1).pack(
            fill="x", padx=14, pady=(16, 0)
        )

        # ── Bedienungshinweise ────────────────────────────────────────────
        tk.Label(rahmen, text="BEDIENUNGSHINWEISE",
                 font=SCHRIFT_LABEL, fg=FARBE_TEXT_GRAU,
                 bg=FARBE_HELL).pack(anchor="w", padx=14, pady=(10, 6))

        hinweise = [
            ("Starten",
             "Bearbeitung eines Moduls beginnen."),
            ("Zurücksetzen",
             "Gestartetes Modul ohne Note zurück in den\nStatus 'Noch nicht begonnen' setzen."),
            ("Modul anklicken",
             "Modul mit gelbem Punkt anklicken, um\nNote und Datum einzutragen."),
            ("[Bearb.]",
             "Note eines abgeschlossenen Moduls\nnachträglich bearbeiten."),
            ("Note speichern",
             "Note 1,0–4,0: Modul wird als bestanden\nmarkiert.\nNote 5,0: Modul verbleibt in Bearbeitung."),
            ("Semesterstatus",
             "Sobald alle Module eines Semesters\nabgeschlossen sind, wird das Semester\nautomatisch beendet und das nächste\ngestartet."),
        ]

        for titel, text in hinweise:
            eintrag = tk.Frame(rahmen, bg=FARBE_HELL)
            eintrag.pack(fill="x", padx=14, pady=(0, 6))

            tk.Label(eintrag, text=titel,
                     font=("Arial", 9, "bold"),
                     fg=FARBE_TEXT, bg=FARBE_HELL,
                     anchor="w").pack(anchor="w")

            tk.Label(eintrag, text=text,
                     font=SCHRIFT_KLEIN,
                     fg=FARBE_TEXT_GRAU, bg=FARBE_HELL,
                     justify="left", anchor="w").pack(anchor="w", padx=(8, 0))

    # ── Event-Handler ─────────────────────────────────────────────────────

    def note_bearbeiten(self, modul: Modul) -> None:
        """
        Setzt ein abgeschlossenes Modul zurück auf IN_BEARBEITUNG,
        damit die Note neu eingetragen werden kann.
        Ruft die entsprechende Controller-Methode auf.
        """
        antwort = tk.messagebox.askyesno(
            "Note bearbeiten",
            f"Möchtest du die Note für\n\n'{modul.name}'\n\nzurücksetzen "
            f"und neu eintragen?\n\nDie bisherige Note "
            f"({str(modul.pruefung.note).replace('.', ',')}) wird gelöscht."
        )
        if not antwort:
            return
        self._controller.note_zuruecksetzen(modul)
        self.modul_auswaehlen(modul)
        self.anzeige_aktualisieren()

    def modul_auswaehlen(self, modul: Modul) -> None:
        """
        Wählt ein Modul für die Noteneingabe aus.
        Nur Module mit Status IN_BEARBEITUNG können ausgewählt werden.
        """
        if modul.status != ModulStatus.IN_BEARBEITUNG:
            return
        self._ausgewaehltes_modul = modul
        self._var_modul_name.set(modul.name)
        self._var_fehler.set("")
        self._btn_speichern.configure(
            state="normal",
            fg=FARBE_SCHALT_TEXT,
            bg=FARBE_SCHALTFLAECHE
        )
        # Modul-Rahmen sichtbar machen: gelbe Farbe und Rand setzen
        self._modul_rahmen.configure(
            bg="#FFF3CD", highlightbackground=FARBE_GELB
        )
        self._label_modul.configure(bg="#FFF3CD", pady=6)
        self._modulliste_aktualisieren()

    def modul_starten(self, modul: Modul) -> None:
        """
        Setzt den Status eines Moduls auf IN_BEARBEITUNG.
        Ruft die entsprechende Controller-Methode auf.
        """
        self._controller.modul_starten(modul)
        self.anzeige_aktualisieren()

    def modul_zuruecksetzen(self, modul: Modul) -> None:
        """
        Setzt ein versehentlich gestartetes Modul zurück auf
        NOCH_NICHT_BEGONNEN. Zeigt Bestätigungsdialog.
        """
        antwort = tk.messagebox.askyesno(
            "Modul zurücksetzen",
            f"Möchtest du das Modul\n\n'{modul.name}'\n\n"
            f"zurück auf 'Noch nicht begonnen' setzen?"
        )
        if not antwort:
            return
        # Falls dieses Modul gerade ausgewählt ist, Auswahl aufheben
        if self._ausgewaehltes_modul == modul:
            self.auswahl_aufheben()
        self._controller.modul_zuruecksetzen(modul)
        self.anzeige_aktualisieren()

    def note_speichern(self) -> None:
        """
        Liest Note und Datum aus den Eingabefeldern und übergibt
        sie an den Controller. Zeigt Fehlermeldung bei ungültiger Eingabe.
        Ruft die entsprechende Controller-Methode auf.
        """
        if self._ausgewaehltes_modul is None:
            return

        note_eingabe = self._var_note.get().strip()
        datum_eingabe = self._var_datum.get().strip()

        if not note_eingabe:
            self._var_fehler.set("Bitte eine Note eingeben.")
            return
        if not datum_eingabe:
            self._var_fehler.set("Bitte ein Datum eingeben.")
            return

        # Validierung und Eintragung im Controller
        # (Datumsformat und Notenwert werden im StudienController geprüft)
        fehler = self._controller.note_eintragen(
            self._ausgewaehltes_modul, note_eingabe, datum_eingabe
        )

        if fehler:
            # Fehlermeldung anzeigen – Modul bleibt IN_BEARBEITUNG
            self._var_fehler.set(fehler)
            return

        # Hinweis bei Note 5,0 – Modul bleibt IN_BEARBEITUNG
        note_float = float(note_eingabe.replace(",", "."))
        if note_float == 5.0:
            self._var_fehler.set(
                "Note 5,0 eingetragen – Prüfung nicht bestanden. "
                "Das Modul bleibt in Bearbeitung."
            )
            self._var_note.set("")
            self._var_datum.set("")
            self.anzeige_aktualisieren()
            return

        # Erfolgreich gespeichert – Anzeige vollständig aktualisieren
        self.auswahl_aufheben()
        self.anzeige_aktualisieren()

    def auswahl_aufheben(self) -> None:
        """
        Hebt die aktuelle Modulauswahl auf und leert die Eingabefelder.
        """
        self._ausgewaehltes_modul = None
        self._var_modul_name.set("")
        self._var_note.set("")
        self._var_datum.set("")
        self._var_fehler.set("")
        self._btn_speichern.configure(
            state="disabled",
            fg=FARBE_TEXT_GRAU,
            bg=FARBE_RAHMEN
        )
        # Modul-Rahmen unsichtbar machen: Farbe auf Panel-Hintergrund setzen
        self._modul_rahmen.configure(
            bg=FARBE_HELL, highlightbackground=FARBE_HELL
        )
        self._label_modul.configure(bg=FARBE_HELL, pady=0)
        self._modulliste_aktualisieren()

    # ── Anzeige aktualisieren ─────────────────────────────────────────────

    def anzeige_aktualisieren(self) -> None:
        """
        Aktualisiert alle Anzeigeelemente des Dashboards
        mit den aktuellen Daten aus dem Controller.
        """
        self._kpi_aktualisieren()
        self._modulliste_aktualisieren()

    def _kpi_aktualisieren(self) -> None:
        """Aktualisiert die vier KPI-Kacheln inkl. Untertitel."""
        # Notendurchschnitt
        durchschnitt = self._controller.notendurchschnitt_berechnen()
        bestanden_anz, _ = self._controller.module_zaehlen()
        self._kpi_durchschnitt.set(
            f"{durchschnitt:.2f}".replace(".", ",")
            if durchschnitt is not None else "–"
        )
        self._kpi_durchschnitt_sub.set(
            f"aus {bestanden_anz} bestandenen Modulen"
        )

        # Studienfortschritt
        akt, regel = self._controller.studienfortschritt_berechnen()
        prozent = round((akt / regel) * 100) if regel > 0 else 0
        self._kpi_fortschritt.set(f"Sem. {akt} / {regel}")
        self._kpi_fortschritt_sub.set(f"{prozent} % der Regelstudienzeit")

        # Progressbalken zeichnen
        self._progress_canvas.update_idletasks()
        breite = self._progress_canvas.winfo_width()
        if breite > 1:
            self._progress_canvas.delete("all")
            self._progress_canvas.create_rectangle(
                0, 0, breite, 6, fill=FARBE_RAHMEN, outline=""
            )
            if prozent > 0:
                self._progress_canvas.create_rectangle(
                    0, 0, int(breite * prozent / 100), 6,
                    fill=FARBE_AKZENT, outline=""
                )

        # Module bestanden
        bestanden, gesamt = self._controller.module_zaehlen()
        offen = gesamt - bestanden
        self._kpi_module.set(f"{bestanden} / {gesamt}")
        self._kpi_module_sub.set(f"{offen} noch offen")
