from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User
from doctors.models import Doctor, DoctorPatientLink
from hospitals.models import Hospital, Department
from medications.models import Medicine, DrugInteraction, MedicationReminder
from patients.models import Patient
from prescriptions.models import Prescription, PrescriptionMedicine

HOSPITALS = [
    ("City General Hospital", "123 Main St, Springfield", "555-0100"),
    ("Riverside Medical Center", "45 Riverside Ave, Rivertown", "555-0200"),
    ("Sunrise Health Institute", "78 Sunrise Blvd, Sunville", "555-0300"),
    ("Lakeside Regional Hospital", "12 Lakeside Dr, Laketown", "555-0400"),
    ("Metro Care Hospital", "300 Metro Plaza, Metro City", "555-0500"),
]

DEPARTMENT_SPECIALIZATION = {
    "Cardiology": "Cardiologist",
    "General Medicine": "General Physician",
    "Orthopedics": "Orthopedic Surgeon",
    "Pediatrics": "Pediatrician",
}
DEPARTMENTS = list(DEPARTMENT_SPECIALIZATION.keys())

DOCTOR_FIRST_NAMES = [
    "Sarah", "James", "Emily", "Michael", "Olivia", "Daniel",
    "Sophia", "Ethan", "Ava", "Matthew", "Isabella", "David",
    "Mia", "Joseph", "Charlotte", "Andrew", "Amelia", "Ryan",
    "Grace", "Nathan", "Chloe", "Kevin", "Lily", "Brian",
    "Zoe", "Justin", "Hannah", "Aaron", "Ella", "Tyler",
]
DOCTOR_LAST_NAMES = [
    "Jones", "Smith", "Patel", "Garcia", "Chen", "Brown",
    "Kim", "Nguyen", "Davis", "Wilson", "Martinez", "Clark",
    "Lewis", "Walker", "Hall", "Young", "Allen", "Wright",
    "King", "Scott", "Green", "Baker", "Adams", "Nelson",
    "Carter", "Mitchell", "Perez", "Roberts", "Turner", "Phillips",
]

PATIENTS = [
    ("jsmith", "John Smith", "1988-04-12", "jsmith@example.com"),
    ("ljohnson", "Linda Johnson", "1975-11-02", "ljohnson@example.com"),
    ("rwilliams", "Robert Williams", "1992-07-23", "rwilliams@example.com"),
    ("mgarcia", "Maria Garcia", "1983-01-30", "mgarcia@example.com"),
    ("wbrown", "William Brown", "1967-09-15", "wbrown@example.com"),
    ("jdavis", "Jennifer Davis", "1999-03-08", "jdavis@example.com"),
]

DOCTORS_PER_HOSPITAL = 6
DEFAULT_DOCTOR_PASSWORD = "doctor12345"
DEFAULT_PATIENT_PASSWORD = "patient12345"


class Command(BaseCommand):
    help = "Seed the database with demo hospitals, departments, doctors, patients, prescriptions, and reference data."

    @transaction.atomic
    def handle(self, *args, **options):
        # The bootstrap Administrator account is created by the
        # accounts.0002_create_default_admin migration, not seeded here.

        doctor_names = list(zip(DOCTOR_FIRST_NAMES, DOCTOR_LAST_NAMES))
        doctor_objects = []
        doctor_count = 0
        hospital_count = 0
        department_count = 0
        name_index = 0

        for hospital_index, (hosp_name, address, phone) in enumerate(HOSPITALS):
            hospital, created = Hospital.objects.get_or_create(
                name=hosp_name, defaults={"address": address, "phone": phone}
            )
            hospital_count += created

            departments = {}
            for dept_name in DEPARTMENTS:
                department, created = Department.objects.get_or_create(hospital=hospital, name=dept_name)
                departments[dept_name] = department
                department_count += created

            for slot in range(DOCTORS_PER_HOSPITAL):
                first, last = doctor_names[name_index % len(doctor_names)]
                name_index += 1
                dept_name = DEPARTMENTS[slot % len(DEPARTMENTS)]
                department = departments[dept_name]

                username = f"dr{first.lower()}{last.lower()}{hospital_index}{slot}"
                existing_user = User.objects.filter(username=username).first()
                if existing_user:
                    doctor_objects.append(Doctor.objects.get(user=existing_user))
                    continue

                doctor_user = User.objects.create_user(
                    username=username, password=DEFAULT_DOCTOR_PASSWORD, role=User.Role.DOCTOR
                )
                doctor = Doctor.objects.create(
                    user=doctor_user,
                    hospital=hospital,
                    department=department,
                    name=f"{first} {last}",
                    specialization=DEPARTMENT_SPECIALIZATION[dept_name],
                    experience=3 + (slot * 2) % 20,
                    contact=f"{username}@example.com",
                )
                doctor_objects.append(doctor)
                doctor_count += 1

        # Keep the originally-documented drjones / jsmith credentials working:
        # drjones is an extra doctor at City General Hospital / General Medicine.
        drjones_user = User.objects.filter(username="drjones").first()
        if drjones_user:
            drjones = Doctor.objects.get(user=drjones_user)
        else:
            first_hospital = Hospital.objects.get(name=HOSPITALS[0][0])
            general_medicine = Department.objects.get(hospital=first_hospital, name="General Medicine")
            drjones_user = User.objects.create_user(username="drjones", password=DEFAULT_DOCTOR_PASSWORD, role=User.Role.DOCTOR)
            drjones = Doctor.objects.create(
                user=drjones_user,
                hospital=first_hospital,
                department=general_medicine,
                name="Sarah Jones",
                specialization="General Physician",
                experience=8,
                contact="drjones@example.com",
            )
            doctor_count += 1

        patient_count = 0
        patient_objects = {}
        for username, name, dob, email in PATIENTS:
            existing_user = User.objects.filter(username=username).first()
            if existing_user:
                patient_objects[username] = Patient.objects.get(user=existing_user)
                continue
            patient_user = User.objects.create_user(
                username=username, password=DEFAULT_PATIENT_PASSWORD, role=User.Role.PATIENT
            )
            patient = Patient.objects.create(user=patient_user, name=name, dob=dob, contact=email)
            patient_objects[username] = patient
            patient_count += 1

        medicines_data = [
            ("Paracetamol", "Pain relief, fever reduction", "500mg every 6 hours", "Nausea, rash", "Avoid with liver disease"),
            ("Ibuprofen", "Pain and inflammation relief", "200-400mg every 6-8 hours", "Stomach upset, ulcers", "Avoid with kidney disease"),
            ("Amoxicillin", "Bacterial infections", "500mg every 8 hours", "Diarrhea, allergic reaction", "Complete full course"),
            ("Warfarin", "Blood thinner", "Dose varies, per INR", "Bleeding, bruising", "Regular blood monitoring required"),
            ("Aspirin", "Pain relief, blood thinning", "75-300mg daily", "Stomach bleeding", "Avoid in children with viral illness"),
            ("Metformin", "Type 2 diabetes management", "500mg twice daily", "GI upset, lactic acidosis (rare)", "Take with food"),
            ("Lisinopril", "Blood pressure control", "10mg once daily", "Dry cough, dizziness", "Monitor kidney function"),
            ("Simvastatin", "Cholesterol control", "20mg at night", "Muscle pain", "Avoid grapefruit juice"),
        ]
        medicines = {}
        for name, uses, dosage, side_effects, precautions in medicines_data:
            medicine, _ = Medicine.objects.get_or_create(
                name=name,
                defaults={"uses": uses, "dosage_info": dosage, "side_effects": side_effects, "precautions": precautions},
            )
            medicines[name] = medicine

        interactions_data = [
            ("Warfarin", "Aspirin", DrugInteraction.Severity.SEVERE, "Increased risk of severe bleeding."),
            ("Warfarin", "Ibuprofen", DrugInteraction.Severity.SEVERE, "Increased bleeding risk; avoid combination."),
            ("Aspirin", "Ibuprofen", DrugInteraction.Severity.MODERATE, "May reduce the cardioprotective effect of aspirin."),
            ("Lisinopril", "Ibuprofen", DrugInteraction.Severity.MODERATE, "NSAIDs may reduce effectiveness of ACE inhibitors and affect kidney function."),
        ]
        for a, b, severity, description in interactions_data:
            DrugInteraction.objects.get_or_create(
                medicine_a=medicines[a], medicine_b=medicines[b],
                defaults={"severity": severity, "description": description},
            )

        # --- Issue demo prescriptions so dashboards show real Active Rx, follow-ups, etc. ---
        rx_count = 0
        if not Prescription.objects.exists():
            today = date.today()

            def issue(doctor, patient, status, items, follow_up_days=None):
                nonlocal rx_count
                prescription = Prescription.objects.create(
                    doctor=doctor,
                    patient=patient,
                    status=status,
                    follow_up_date=today + timedelta(days=follow_up_days) if follow_up_days else None,
                )
                for medicine_name, dosage, frequency, duration in items:
                    PrescriptionMedicine.objects.create(
                        prescription=prescription, medicine=medicines[medicine_name],
                        dosage=dosage, frequency=frequency, duration=duration,
                    )
                DoctorPatientLink.objects.get_or_create(doctor=doctor, patient=patient)
                rx_count += 1
                return prescription

            jsmith = patient_objects["jsmith"]
            second_doctor_city_general = doctor_objects[2]  # City General Hospital, Orthopedics slot

            issue(drjones, jsmith, Prescription.Status.ACTIVE,
                  [("Paracetamol", "500mg", "3 times daily", "5 days"),
                   ("Amoxicillin", "500mg", "every 8 hours", "7 days")],
                  follow_up_days=14)
            issue(drjones, jsmith, Prescription.Status.COMPLETED,
                  [("Ibuprofen", "400mg", "twice daily", "5 days")])
            issue(second_doctor_city_general, jsmith, Prescription.Status.ACTIVE,
                  [("Lisinopril", "10mg", "once daily", "30 days")], follow_up_days=30)

            issue(doctor_objects[6], patient_objects["ljohnson"], Prescription.Status.ACTIVE,
                  [("Aspirin", "150mg", "once daily", "30 days"),
                   ("Warfarin", "5mg", "once daily", "30 days")],
                  follow_up_days=7)
            issue(doctor_objects[6], patient_objects["ljohnson"], Prescription.Status.ARCHIVED,
                  [("Simvastatin", "20mg", "at night", "30 days")])

            issue(doctor_objects[12], patient_objects["rwilliams"], Prescription.Status.ACTIVE,
                  [("Metformin", "500mg", "twice daily", "30 days")], follow_up_days=30)

            issue(doctor_objects[18], patient_objects["mgarcia"], Prescription.Status.ACTIVE,
                  [("Ibuprofen", "400mg", "twice daily", "5 days")], follow_up_days=10)
            issue(doctor_objects[19], patient_objects["mgarcia"], Prescription.Status.COMPLETED,
                  [("Amoxicillin", "500mg", "every 8 hours", "7 days")])

            issue(doctor_objects[24], patient_objects["wbrown"], Prescription.Status.ACTIVE,
                  [("Lisinopril", "10mg", "once daily", "30 days"),
                   ("Simvastatin", "20mg", "at night", "30 days")],
                  follow_up_days=21)

            issue(doctor_objects[3], patient_objects["jdavis"], Prescription.Status.ACTIVE,
                  [("Paracetamol", "500mg", "3 times daily", "5 days")], follow_up_days=10)
            issue(doctor_objects[3], patient_objects["jdavis"], Prescription.Status.ACTIVE,
                  [("Metformin", "500mg", "twice daily", "30 days")], follow_up_days=30)

            # Reminders + adherence history for jsmith, the flagship walkthrough account.
            MedicationReminder.objects.create(
                patient=jsmith, medicine=medicines["Paracetamol"],
                scheduled_date=today, time="08:00", status=MedicationReminder.Status.TAKEN,
            )
            MedicationReminder.objects.create(
                patient=jsmith, medicine=medicines["Amoxicillin"],
                scheduled_date=today, time="20:00", status=MedicationReminder.Status.PENDING,
            )
            MedicationReminder.objects.create(
                patient=jsmith, medicine=medicines["Amoxicillin"],
                scheduled_date=today - timedelta(days=1), time="08:00", status=MedicationReminder.Status.MISSED,
            )
            MedicationReminder.objects.create(
                patient=jsmith, medicine=medicines["Lisinopril"],
                scheduled_date=today, time="09:00", status=MedicationReminder.Status.TAKEN,
            )

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {Hospital.objects.count()} hospitals, {Department.objects.count()} departments, "
            f"{Doctor.objects.count()} doctors, {Patient.objects.count()} patients."
        ))
        self.stdout.write(self.style.SUCCESS(
            f"{Medicine.objects.count()} medicines, {DrugInteraction.objects.count()} interactions, "
            f"{Prescription.objects.count()} prescriptions, {MedicationReminder.objects.count()} reminders."
        ))
        self.stdout.write(self.style.SUCCESS("Demo data seeding complete."))
