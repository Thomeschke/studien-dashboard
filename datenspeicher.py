# =============================================================================
# datenspeicher.py – Datenpersistenz des Studien-Dashboards
# =============================================================================
# Verantwortlich für das Lesen und Schreiben der JSON-Datei.
# Übernimmt die vollständige Serialisierung des Objektbaums:
#   Studiengang → Semester → Modul → Pruefungsleistung
# Enum-Werte werden als Strings gespeichert und beim Laden typsicher
# als Enum-Objekte rekonstruiert.
# =============================================================================

import json
import os

from models import (
    Studiengang, Semester, Modul, Pruefungsleistung,
    SemesterStatus, ModulStatus
)


class DatenSpeicher:
    """
    Kapselt alle Datei-I/O-Operationen für das Studien-Dashboard.

    Attribute:
        dateipfad (str): Pfad zur JSON-Datendatei.
    """

    def __init__(self, dateipfad: str = "studiendaten.json"):
        self.dateipfad: str = dateipfad

    # ── Speichern ──────────────────────────────────────────────────────────

    def speichern(self, studiengang: Studiengang) -> None:
        """
        Serialisiert den gesamten Objektbaum und schreibt ihn als JSON.
        Enum-Werte werden als Strings gespeichert.
        """
        daten = self._studiengang_zu_dict(studiengang)
        with open(self.dateipfad, "w", encoding="utf-8") as datei:
            json.dump(daten, datei, ensure_ascii=False, indent=2)

    def _studiengang_zu_dict(self, studiengang: Studiengang) -> dict:
        """Wandelt ein Studiengang-Objekt in ein serialisierbares Dict um."""
        return {
            "name": studiengang.name,
            "startdatum": studiengang.startdatum,
            "regelstudienzeit_semester": studiengang.regelstudienzeit_semester,
            "semester": [
                self._semester_zu_dict(sem)
                for sem in studiengang.semester
            ]
        }

    def _semester_zu_dict(self, semester: Semester) -> dict:
        """Wandelt ein Semester-Objekt in ein serialisierbares Dict um."""
        return {
            "semester_nummer": semester.semester_nummer,
            "startdatum": semester.startdatum,
            "enddatum": semester.enddatum,
            # Enum-Wert als String speichern
            "status": semester.status.value,
            "module": [
                self._modul_zu_dict(modul)
                for modul in semester.module
            ]
        }

    def _modul_zu_dict(self, modul: Modul) -> dict:
        """Wandelt ein Modul-Objekt in ein serialisierbares Dict um."""
        return {
            "name": modul.name,
            "credits": modul.credits,
            # Enum-Wert als String speichern
            "status": modul.status.value,
            "pruefung": (
                self._pruefung_zu_dict(modul.pruefung)
                if modul.pruefung is not None else None
            )
        }

    def _pruefung_zu_dict(self, pruefung: Pruefungsleistung) -> dict:
        """Wandelt eine Pruefungsleistung in ein serialisierbares Dict um."""
        return {
            "note": pruefung.note,
            "datum": pruefung.datum
            # /bestanden wird nicht gespeichert – es ist ein abgeleitetes Attribut
        }

    # ── Laden ──────────────────────────────────────────────────────────────

    def laden(self) -> Studiengang:
        """
        Liest die JSON-Datei und rekonstruiert den vollständigen Objektbaum.
        Enum-Werte werden typsicher aus Strings rekonstruiert.

        Returns:
            Studiengang: Der vollständig rekonstruierte Studiengang.

        Raises:
            FileNotFoundError: Wenn die Datendatei nicht existiert.
        """
        if not os.path.exists(self.dateipfad):
            raise FileNotFoundError(
                f"Datendatei nicht gefunden: {self.dateipfad}"
            )
        with open(self.dateipfad, "r", encoding="utf-8") as datei:
            daten = json.load(datei)
        return self._dict_zu_studiengang(daten)

    def _dict_zu_studiengang(self, daten: dict) -> Studiengang:
        """Rekonstruiert ein Studiengang-Objekt aus einem Dict."""
        studiengang = Studiengang(
            name=daten["name"],
            startdatum=daten["startdatum"],
            regelstudienzeit_semester=daten["regelstudienzeit_semester"]
        )
        for sem_daten in daten.get("semester", []):
            studiengang.semester_hinzufuegen(
                self._dict_zu_semester(sem_daten)
            )
        return studiengang

    def _dict_zu_semester(self, daten: dict) -> Semester:
        """Rekonstruiert ein Semester-Objekt aus einem Dict."""
        semester = Semester(
            semester_nummer=daten["semester_nummer"],
            startdatum=daten["startdatum"],
            enddatum=daten["enddatum"]
        )
        # Enum typsicher aus String rekonstruieren
        semester.status = SemesterStatus(daten["status"])
        for modul_daten in daten.get("module", []):
            semester.modul_hinzufuegen(
                self._dict_zu_modul(modul_daten)
            )
        return semester

    def _dict_zu_modul(self, daten: dict) -> Modul:
        """Rekonstruiert ein Modul-Objekt aus einem Dict."""
        modul = Modul(
            name=daten["name"],
            credits=daten["credits"]
        )
        # Enum typsicher aus String rekonstruieren
        modul.status = ModulStatus(daten["status"])
        if daten.get("pruefung") is not None:
            modul.pruefung = self._dict_zu_pruefung(daten["pruefung"])
        return modul

    def _dict_zu_pruefung(self, daten: dict) -> Pruefungsleistung:
        """Rekonstruiert eine Pruefungsleistung aus einem Dict."""
        return Pruefungsleistung(
            note=daten["note"],
            datum=daten["datum"]
        )
