# =============================================================================
# controller.py – Steuerungslogik des Studien-Dashboards
# =============================================================================
# Vermittelt zwischen der GUI (DashboardApp) und den Entity-Klassen.
# Enthält alle fachlichen Regeln (Validierung, Berechnungen, Statusübergänge).
# Die GUI ruft ausschließlich Methoden des Controllers auf.
# =============================================================================

from models import (
    Studiengang, Semester, Modul, Pruefungsleistung,
    ModulStatus, SemesterStatus
)
from datenspeicher import DatenSpeicher


# Menge der in Deutschland gültigen Hochschulnoten
GUELTIGE_NOTEN = {1.0, 1.3, 1.7, 2.0, 2.3, 2.7,
                  3.0, 3.3, 3.7, 4.0, 5.0}


class StudienController:
    """
    Steuerungsklasse des Studien-Dashboards.

    Kapselt alle fachlichen Regeln und Berechnungen.
    Hält eine Referenz auf das Studiengang-Objekt (Assoziation),
    das den gesamten Datenbaum enthält.
    Delegiert Persistenzoperationen an DatenSpeicher (Abhängigkeit).
    """

    def __init__(self, dateipfad: str = "studiendaten.json"):
        self._speicher:    DatenSpeicher      = DatenSpeicher(dateipfad)
        self._studiengang: Studiengang | None = None

    # ── Datenzugriff ───────────────────────────────────────────────────────

    @property
    def studiengang(self) -> Studiengang | None:
        """Gibt das aktuelle Studiengang-Objekt zurück."""
        return self._studiengang

    # ── Laden / Speichern ──────────────────────────────────────────────────

    def studiengang_laden(self) -> bool:
        """
        Lädt den Studiengang aus der JSON-Datei.

        Returns:
            True wenn erfolgreich geladen, False wenn keine Datei vorhanden.
        """
        try:
            self._studiengang = self._speicher.laden()
            return True
        except FileNotFoundError:
            return False

    def studiengang_initialisieren(self, studiengang: Studiengang) -> None:
        """
        Setzt einen neuen Studiengang (z. B. beim ersten Start)
        und speichert ihn sofort.
        """
        self._studiengang = studiengang
        self.studiengang_speichern()

    def studiengang_speichern(self) -> None:
        """Speichert den aktuellen Studiengang in die JSON-Datei."""
        if self._studiengang is not None:
            self._speicher.speichern(self._studiengang)

    # ── Modulverwaltung ────────────────────────────────────────────────────

    def modul_starten(self, modul: Modul) -> None:
        """
        Setzt den Status eines Moduls auf IN_BEARBEITUNG.
        Nur möglich wenn Status NOCH_NICHT_BEGONNEN.
        """
        if modul.status == ModulStatus.NOCH_NICHT_BEGONNEN:
            modul.status = ModulStatus.IN_BEARBEITUNG
            self._semester_status_aktualisieren()
            self.studiengang_speichern()

    def modul_zuruecksetzen(self, modul: Modul) -> None:
        """
        Setzt ein versehentlich gestartetes Modul zurück auf
        NOCH_NICHT_BEGONNEN. Nur möglich wenn Status IN_BEARBEITUNG
        und noch keine Note eingetragen wurde.
        """
        if modul.status == ModulStatus.IN_BEARBEITUNG and modul.pruefung is None:
            modul.status = ModulStatus.NOCH_NICHT_BEGONNEN
            self.studiengang_speichern()

    def note_eintragen(self, modul: Modul,
                       note_eingabe: str, datum: str) -> str | None:
        """
        Trägt eine Note für ein Modul ein (fachliche Regel im Controller).
        Bei Note <= 4,0 wechselt das Modul in den Status ABGESCHLOSSEN.
        Bei Note 5,0 bleibt der Status IN_BEARBEITUNG.

        Args:
            modul:        Das Modul, für das die Note eingetragen wird.
            note_eingabe: Notenwert als String (z. B. "2,0" oder "1.7").
            datum:        Prüfungsdatum im Format TT.MM.JJJJ.

        Returns:
            Fehlermeldung als String bei ungültiger Eingabe, sonst None.
        """
        # Validierung als fachliche Regel im Controller verankert
        fehler = self._note_validieren(note_eingabe)
        if fehler:
            return fehler
        fehler = self._datum_validieren(datum)
        if fehler:
            return fehler

        note = float(note_eingabe.replace(",", "."))
        modul.pruefung = Pruefungsleistung(note=note, datum=datum)

        if modul.pruefung.bestanden:
            modul.status = ModulStatus.ABGESCHLOSSEN
        # Bei 5,0: Status bleibt IN_BEARBEITUNG, kein Statuswechsel

        # Prüfen ob alle Module eines Semesters abgeschlossen sind
        # → Semester automatisch auf BEENDET setzen
        self._semester_status_aktualisieren()

        self.studiengang_speichern()
        return None  # kein Fehler

    def _note_validieren(self, note_eingabe: str) -> str | None:
        """
        Validiert eine Noteneingabe als fachliche Regel.

        Returns:
            Fehlermeldung als String bei ungültigem Wert, sonst None.
        """
        try:
            note = float(note_eingabe.replace(",", "."))
        except ValueError:
            return f"'{note_eingabe}' ist kein gültiger Zahlenwert."
        if note not in GUELTIGE_NOTEN:
            return (f"{note_eingabe} ist keine gültige Note. "
                    f"Erlaubt: 1,0 – 4,0 oder 5,0.")
        return None

    def _datum_validieren(self, datum: str) -> str | None:
        """
        Validiert ein Datum auf Format TT.MM.JJJJ und Existenz.

        Returns:
            Fehlermeldung als String bei ungültigem Wert, sonst None.
        """
        import re
        from datetime import datetime
        if not re.fullmatch(r"\d{2}\.\d{2}\.\d{4}", datum):
            return "Ungültiges Datum. Bitte Format TT.MM.JJJJ verwenden."
        try:
            datetime.strptime(datum, "%d.%m.%Y")
        except ValueError:
            return f"'{datum}' ist kein gültiges Datum."
        return None

    # ── Berechnungen ───────────────────────────────────────────────────────

    def _semester_status_aktualisieren(self) -> None:
        """
        Prüft für jedes Semester, ob alle Module abgeschlossen sind.
        Wenn ja, wird der Semesterstatus automatisch auf BEENDET gesetzt
        und das nächste Semester (falls GEPLANT) auf LAUFEND gesetzt.
        """
        if self._studiengang is None:
            return
        semester_liste = self._studiengang.semester
        for i, sem in enumerate(semester_liste):
            if sem.status == SemesterStatus.BEENDET:
                continue  # bereits beendet, nicht zurücksetzen
            alle_abgeschlossen = (
                len(sem.module) > 0
                and all(
                    m.status == ModulStatus.ABGESCHLOSSEN
                    for m in sem.module
                )
            )
            if alle_abgeschlossen:
                sem.status = SemesterStatus.BEENDET
                # Nächstes Semester automatisch auf LAUFEND setzen
                if i + 1 < len(semester_liste):
                    naechstes = semester_liste[i + 1]
                    if naechstes.status == SemesterStatus.GEPLANT:
                        naechstes.status = SemesterStatus.LAUFEND

    def notendurchschnitt_berechnen(self) -> float | None:
        """
        Berechnet den Notendurchschnitt aller bestandenen Prüfungsleistungen.

        Returns:
            Durchschnitt als Float, oder None wenn keine Note vorhanden.
        """
        if self._studiengang is None:
            return None
        noten = [
            modul.pruefung.note
            for sem in self._studiengang.semester
            for modul in sem.module
            if modul.pruefung is not None and modul.pruefung.bestanden
        ]
        if not noten:
            return None
        return round(sum(noten) / len(noten), 2)

    def studienfortschritt_berechnen(self) -> tuple[int, int]:
        """
        Berechnet den Studienfortschritt als Anzahl aktiver/beendeter Semester
        (Status LAUFEND oder BEENDET) im Verhältnis zur Regelstudienzeit.
        Semester mit Status GEPLANT zählen noch nicht zum Fortschritt.

        Returns:
            Tuple (aktive_semester, regelstudienzeit).
        """
        if self._studiengang is None:
            return (0, 0)
        from models import SemesterStatus
        aktive_semester = sum(
            1 for sem in self._studiengang.semester
            if sem.status in (SemesterStatus.LAUFEND, SemesterStatus.BEENDET)
        )
        regelstudienzeit = self._studiengang.regelstudienzeit_semester
        return (aktive_semester, regelstudienzeit)

    def module_zaehlen(self) -> tuple[int, int]:
        """
        Zählt bestandene und Gesamtanzahl der Module.

        Returns:
            Tuple (bestanden, gesamt).
        """
        if self._studiengang is None:
            return (0, 0)
        gesamt    = 0
        bestanden = 0
        for sem in self._studiengang.semester:
            for modul in sem.module:
                gesamt += 1
                if modul.status == ModulStatus.ABGESCHLOSSEN:
                    bestanden += 1
        return (bestanden, gesamt)

    def note_zuruecksetzen(self, modul: Modul) -> None:
        """
        Setzt die Note und den Status eines abgeschlossenen Moduls zurück
        auf IN_BEARBEITUNG, damit die Note neu eingetragen werden kann.
        Setzt auch den Semesterstatus von BEENDET zurück auf LAUFEND,
        falls das Semester dadurch nicht mehr vollständig abgeschlossen ist.
        """
        if modul.status != ModulStatus.ABGESCHLOSSEN:
            return
        modul.pruefung = None
        modul.status   = ModulStatus.IN_BEARBEITUNG

        # Semesterstatus ggf. von BEENDET zurück auf LAUFEND setzen
        if self._studiengang is not None:
            for sem in self._studiengang.semester:
                if sem.status == SemesterStatus.BEENDET:
                    hat_offene = any(
                        m.status != ModulStatus.ABGESCHLOSSEN
                        for m in sem.module
                    )
                    if hat_offene:
                        sem.status = SemesterStatus.LAUFEND

        self.studiengang_speichern()

    def alle_module(self) -> list[tuple[Modul, Semester]]:
        """
        Gibt alle Module des Studiengangs zusammen mit ihrem Semester zurück.

        Returns:
            Liste von Tupeln (Modul, Semester).
        """
        if self._studiengang is None:
            return []
        return [
            (modul, sem)
            for sem in self._studiengang.semester
            for modul in sem.module
        ]
