# =============================================================================
# models.py – Entity-Klassen des Studien-Dashboards
# =============================================================================
# Enthält alle fachlichen Datenklassen gemäß UML-Klassendiagramm (Phase 1/2):
#   - SemesterStatus (Enum)
#   - ModulStatus (Enum)
#   - Studiengang
#   - Semester
#   - Modul
#   - Pruefungsleistung
# =============================================================================

from enum import Enum


class SemesterStatus(Enum):
    """Beschreibt den zeitlichen Verlauf eines Semesters."""
    GEPLANT = "geplant"
    LAUFEND = "laufend"
    BEENDET = "beendet"


class ModulStatus(Enum):
    """Beschreibt den inhaltlichen Bearbeitungsstand eines Moduls."""
    NOCH_NICHT_BEGONNEN = "noch_nicht_begonnen"
    IN_BEARBEITUNG      = "in_bearbeitung"
    ABGESCHLOSSEN       = "abgeschlossen"


class Pruefungsleistung:
    """
    Repräsentiert die Prüfungsleistung eines Moduls.

    Attribute:
        note  (float): Die erzielte Note (1,0–4,0 oder 5,0).
        datum (str):   Prüfungsdatum im Format TT.MM.JJJJ.
                       Entspricht dem UML-Typ Date.
    """

    def __init__(self, note: float, datum: str):
        self.note  = note
        self.datum = datum

    @property
    def bestanden(self) -> bool:
        """
        Abgeleitetes Attribut (/bestanden im UML).
        True wenn Note <= 4,0, sonst False.
        Wird nicht gespeichert, sondern bei jedem Zugriff berechnet.
        """
        return self.note <= 4.0

    def __repr__(self) -> str:
        return (f"Pruefungsleistung(note={self.note}, "
                f"datum='{self.datum}', bestanden={self.bestanden})")


class Modul:
    """
    Repräsentiert ein Modul innerhalb eines Semesters.

    Attribute:
        name    (str):        Name des Moduls.
        credits (int):        ECTS-Credits des Moduls.
        status  (ModulStatus): Aktueller Bearbeitungsstand.
        pruefung (Pruefungsleistung | None): Zugehörige Prüfungsleistung,
                              sofern bereits eingetragen (Komposition 1 zu 1).
    """

    def __init__(self, name: str, credits: int):
        self.name:     str        = name
        self.credits:  int        = credits
        self.status:   ModulStatus = ModulStatus.NOCH_NICHT_BEGONNEN
        # Komposition: Prüfungsleistung existiert nur im Kontext des Moduls.
        # Vor Eintragung einer Note ist pruefung None.
        self.pruefung: Pruefungsleistung | None = None

    def __repr__(self) -> str:
        return (f"Modul('{self.name}', {self.credits} CP, "
                f"{self.status.value})")


class Semester:
    """
    Repräsentiert ein Semester innerhalb eines Studiengangs.

    Attribute:
        semester_nummer (int):            Fortlaufende Nummer des Semesters.
        startdatum      (str):            Startdatum im Format TT.MM.JJJJ
                                          (UML-Typ: Date).
        enddatum        (str):            Enddatum im Format TT.MM.JJJJ
                                          (UML-Typ: Date).
        status          (SemesterStatus): Zeitlicher Status des Semesters.
        module          (list[Modul]):    Liste der zugehörigen Module
                                          (Komposition 1 zu 1..*).
    """

    def __init__(self, semester_nummer: int, startdatum: str, enddatum: str):
        self.semester_nummer: int            = semester_nummer
        self.startdatum:      str            = startdatum
        self.enddatum:        str            = enddatum
        self.status:          SemesterStatus = SemesterStatus.GEPLANT
        # Komposition: Module existieren nur im Kontext des Semesters.
        self.module: list[Modul] = []

    def modul_hinzufuegen(self, modul: Modul) -> None:
        """Fügt ein Modul zur Liste des Semesters hinzu."""
        self.module.append(modul)

    def __repr__(self) -> str:
        return (f"Semester({self.semester_nummer}, "
                f"{self.status.value}, {len(self.module)} Module)")


class Studiengang:
    """
    Repräsentiert den gesamten Studiengang.
    Wurzelobjekt des Objektbaums.

    Attribute:
        name                      (str):          Name des Studiengangs.
        startdatum                (str):          Startdatum im Format TT.MM.JJJJ
                                                  (UML-Typ: Date).
        regelstudienzeit_semester (int):          Vorgesehene Gesamtdauer in
                                                  Semestern (z. B. 8).
        semester                  (list[Semester]): Liste der Semester
                                                  (Komposition 1 zu 1..*).
    """

    def __init__(self, name: str, startdatum: str,
                 regelstudienzeit_semester: int):
        self.name:                      str      = name
        self.startdatum:                str      = startdatum
        self.regelstudienzeit_semester: int      = regelstudienzeit_semester
        # Komposition: Semester existieren nur im Kontext des Studiengangs.
        self.semester: list[Semester] = []

    def semester_hinzufuegen(self, semester: Semester) -> None:
        """Fügt ein Semester zur Liste des Studiengangs hinzu."""
        self.semester.append(semester)

    def __repr__(self) -> str:
        return (f"Studiengang('{self.name}', "
                f"{len(self.semester)} Semester)")
