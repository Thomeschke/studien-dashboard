# =============================================================================
# main.py – Einstiegspunkt des Studien-Dashboards
# =============================================================================

from controller import StudienController
from dashboard_app import DashboardApp
from models import (
    Studiengang, Semester, Modul,
    SemesterStatus, ModulStatus, Pruefungsleistung
)


def beispieldaten_erstellen() -> Studiengang:
    """
    Erstellt den realen Studiengang B.Sc. Cyber Security (Fernstudium, TZ I).
    Modulaufteilung gemäß Studienablaufplan über 8 Semester.
    Aktueller Stand: Semester 1 abgeschlossen, Semester 2 laufend.
    """
    sg = Studiengang(
        name="B.Sc. Cyber Security",
        startdatum="01.10.2024",
        regelstudienzeit_semester=8
    )

    # ── Semester 1 – Abgeschlossen ────────────────────────────────────────
    sem1 = Semester(1, "01.10.2024", "31.03.2025")
    sem1.status = SemesterStatus.BEENDET

    m1 = Modul("Betriebssysteme, Rechnernetze und verteilte Systeme", 5)
    m1.status   = ModulStatus.ABGESCHLOSSEN
    m1.pruefung = Pruefungsleistung(1.3, "15.01.2025")

    m2 = Modul("Einführung in Datenschutz und IT-Sicherheit", 5)
    m2.status   = ModulStatus.ABGESCHLOSSEN
    m2.pruefung = Pruefungsleistung(2.0, "15.01.2025")

    m3 = Modul("Einführung in die Programmierung mit Python", 5)
    m3.status   = ModulStatus.ABGESCHLOSSEN
    m3.pruefung = Pruefungsleistung(2.0, "15.01.2025")

    m4 = Modul("Einführung in das wissenschaftliche Arbeiten für IT und Technik", 5)
    m4.status   = ModulStatus.ABGESCHLOSSEN
    m4.pruefung = Pruefungsleistung(2.0, "15.01.2025")

    m5 = Modul("Projekt: Objektorientierte und funktionale Programmierung mit Python", 5)
    m5.status   = ModulStatus.ABGESCHLOSSEN
    m5.pruefung = Pruefungsleistung(2.0, "15.01.2025")

    for m in [m1, m2, m3, m4, m5]:
        sem1.modul_hinzufuegen(m)
    sg.semester_hinzufuegen(sem1)

    # ── Semester 2 – Laufend ──────────────────────────────────────────────
    sem2 = Semester(2, "01.04.2025", "30.09.2025")
    sem2.status = SemesterStatus.LAUFEND

    sem2.modul_hinzufuegen(Modul("Wahlpflichtbereich C (1/6)", 5))
    sem2.modul_hinzufuegen(Modul("Einführung in die Netzwerkforensik", 5))
    sem2.modul_hinzufuegen(Modul("Mathematik Grundlagen I", 5))
    sem2.modul_hinzufuegen(
        Modul("Statistik – Wahrscheinlichkeit und deskriptive Statistik", 5)
    )
    sg.semester_hinzufuegen(sem2)

    # ── Semester 3 – Geplant ──────────────────────────────────────────────
    sem3 = Semester(3, "01.10.2025", "31.03.2026")
    sem3.modul_hinzufuegen(Modul("Requirements Engineering", 5))
    sem3.modul_hinzufuegen(Modul("Projekt: Agiles Projektmanagement", 5))
    sem3.modul_hinzufuegen(Modul("Wahlpflichtbereich C (2/6)", 5))
    sem3.modul_hinzufuegen(Modul("Grundzüge des System-Pentestings", 5))
    sem3.modul_hinzufuegen(
        Modul("Theoretische Informatik und Mathematische Logik", 5)
    )
    sg.semester_hinzufuegen(sem3)

    # ── Semester 4 – Geplant ──────────────────────────────────────────────
    sem4 = Semester(4, "01.04.2026", "30.09.2026")
    sem4.modul_hinzufuegen(Modul("Social Engineering und Insider Threats", 5))
    sem4.modul_hinzufuegen(
        Modul("Technische und betriebliche IT-Sicherheitskonzeptionen", 5)
    )
    sem4.modul_hinzufuegen(Modul("Projekt: Social Engineering", 5))
    sem4.modul_hinzufuegen(Modul("Wahlpflichtbereich C (3/6)", 5))
    sg.semester_hinzufuegen(sem4)

    # ── Semester 5 – Geplant ──────────────────────────────────────────────
    sem5 = Semester(5, "01.10.2026", "31.03.2027")
    sem5.modul_hinzufuegen(
        Modul("DevSecOps und gängige Software-Schwachstellen", 5)
    )
    sem5.modul_hinzufuegen(Modul("Kryptografische Verfahren", 5))
    sem5.modul_hinzufuegen(Modul("Host- und Softwareforensik", 5))
    sem5.modul_hinzufuegen(
        Modul("Seminar: Aktuelle Themen in Computer Science", 5)
    )
    sem5.modul_hinzufuegen(
        Modul("Projekt: Einsatz und Konfiguration von SIEM-Systemen", 5)
    )
    sg.semester_hinzufuegen(sem5)

    # ── Semester 6 – Geplant ──────────────────────────────────────────────
    sem6 = Semester(6, "01.04.2027", "30.09.2027")
    sem6.modul_hinzufuegen(Modul("Wahlpflichtbereich C (4/6)", 5))
    sem6.modul_hinzufuegen(Modul("Threat Modeling", 5))
    sem6.modul_hinzufuegen(Modul("Standards der Informationssicherheit", 5))
    sem6.modul_hinzufuegen(Modul("Wahlpflichtbereich A", 10))
    sg.semester_hinzufuegen(sem6)

    # ── Semester 7 – Geplant ──────────────────────────────────────────────
    sem7 = Semester(7, "01.10.2027", "31.03.2028")
    sem7.modul_hinzufuegen(Modul("Projekt: Threat Modeling", 5))
    sem7.modul_hinzufuegen(Modul("Wahlpflichtbereich C (5/6)", 5))
    sem7.modul_hinzufuegen(Modul("Wahlpflichtbereich B", 10))
    sg.semester_hinzufuegen(sem7)

    # ── Semester 8 – Geplant ──────────────────────────────────────────────
    sem8 = Semester(8, "01.04.2028", "30.09.2028")
    sem8.modul_hinzufuegen(
        Modul("Projekt: Allgemeine Programmierung mit C/C++", 5)
    )
    sem8.modul_hinzufuegen(Modul("Wahlpflichtbereich C (6/6)", 5))
    sem8.modul_hinzufuegen(Modul("Bachelorarbeit", 9))
    sem8.modul_hinzufuegen(Modul("Kolloquium", 1))
    sg.semester_hinzufuegen(sem8)

    return sg


def main() -> None:
    """Hauptfunktion – initialisiert Controller, lädt Daten und startet GUI."""
    controller = StudienController("studiendaten.json")

    if not controller.studiengang_laden():
        print("Keine Daten gefunden – Studiendaten werden angelegt.")
        sg = beispieldaten_erstellen()
        controller.studiengang_initialisieren(sg)

    app = DashboardApp(controller)
    app.anzeige_aktualisieren()
    app.starten()


if __name__ == "__main__":
    main()
