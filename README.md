# Healthcare — Digital Healthcare Management System

Role-based Django web app for hospitals, doctors, and patients, built to the
attached final project specification (automatic doctor-patient linking, OCR
prescription intake, medication reminders/adherence, and role-scoped
dashboards).

## Stack

| Layer | Choice |
|---|---|
| Backend | Django 5.2 |
| Database | PostgreSQL (SQLite supported for zero-setup local dev) |
| OCR | Tesseract via `pytesseract` (+ `pdf2image` for PDF uploads) |
| Frontend | Django templates + Bootstrap 5 |
| Auth | Django auth, extended with a `role` field (Admin/Doctor/Patient) |
| File storage | Local `MEDIA_ROOT` (swap for S3 in production) |
| Reminders | Celery + Redis (beat task auto-marks overdue reminders "Missed") |
| Charts | Chart.js, fed by JSON endpoints on each dashboard |

## Project layout

- `accounts` — custom `User` model (role field), login/logout, admin account registration
- `hospitals` — Hospital/Department models, directory browsing, admin CRUD
- `patients` — Patient model, patient dashboard, profile, prescription history, doctors consulted
- `doctors` — Doctor model, doctor-patient links, consultation notes, doctor dashboard
- `medications` — Medicine, DrugInteraction, MedicationReminder, lookup + interaction check, adherence
- `prescriptions` — Prescription/PrescriptionMedicine, OCR upload+verify flow, doctor-issued flow, print/download
- `core` — home routing, role dispatch, Administrator dashboard, demo data seed command

## Setup

### 1. Clone & create a virtualenv

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

Copy `.env.example` to `.env` and adjust as needed.

```
copy .env.example .env
```

By default it's set up for PostgreSQL. The easiest way to get Postgres + Redis
running locally is Docker:

```
docker compose up -d
```

That starts Postgres on `localhost:5432` and Redis on `localhost:6379` matching
the `.env.example` defaults.

If you don't want to install Docker/Postgres right now, set `DB_ENGINE=sqlite3`
in `.env` for a zero-dependency local database (this repo was validated against
that path).

### 3. Install Tesseract OCR (required for the prescription-upload OCR feature)

This is a native binary, not a Python package:

- Windows: install from https://github.com/UB-Mannheim/tesseract/wiki, then set
  `TESSERACT_CMD` in `.env` to the install path, e.g.
  `C:\Program Files\Tesseract-OCR\tesseract.exe`
- macOS: `brew install tesseract`
- Linux: `apt install tesseract-ocr`

Without Tesseract installed, everything else in the app works; only the OCR
extraction step will fail (the manual "add medicine" row in the verification
screen still lets you record a prescription by hand).

### 4. Migrate & seed demo data

```
python manage.py migrate
python manage.py seed_demo_data
```

`migrate` alone auto-creates a bootstrap Administrator account
(`accounts.0002_create_default_admin`), so there's always at least one admin
to log in with on a fresh install. Any Administrator can create further
Administrator accounts from the "Add Administrator" page — those accounts have
identical powers, including creating more admins in turn.

`seed_demo_data` then populates everything else: 5 hospitals (4 departments
each), 31 doctors, 6 patients, 8 reference medicines, 4 drug interactions, and
11 prescriptions (8 Active / 2 Completed / 1 Archived) so the dashboards show
real numbers instead of zeros. Every login is listed below.

## Login credentials

Pick the matching **Role** on the login form for whichever account you use.

**Administrator** — created by the migration (not the seed command) from
`ADMIN_USERNAME` / `ADMIN_PASSWORD` in your `.env`. If `ADMIN_PASSWORD` is
empty no admin is created; run `python manage.py createsuperuser` instead.

**Patients** — all password `patient12345`:

| Username | Name |
|---|---|
| `jsmith` | John Smith — **flagship account**: has 3 prescriptions (2 Active, 1 Completed) across 2 doctors, 4 medication reminders (2 Taken, 1 Pending, 1 Missed → 66.7% adherence), and 2 upcoming follow-ups. Best account to explore the full patient experience. |
| `ljohnson` | Linda Johnson — 1 Active prescription (with a deliberate Warfarin+Aspirin interaction pair — try the Medicine Lookup page), 1 Archived |
| `rwilliams` | Robert Williams — 1 Active prescription |
| `mgarcia` | Maria Garcia — 1 Active, 1 Completed, across 2 doctors |
| `wbrown` | William Brown — 1 Active prescription |
| `jdavis` | Jennifer Davis — 2 Active prescriptions |

**Doctors** — all password `doctor12345`. `drjones` is the one with the most
seeded activity (3 prescriptions, 1 linked patient); the other 30 are spread
6-per-hospital across Cardiology / General Medicine / Orthopedics / Pediatrics
and mostly have no prescriptions yet, so you can use them to test *issuing* a
first prescription (and watch the doctor-patient link get created live).

| Hospital | Usernames (all `doctor12345`) |
|---|---|
| City General Hospital | `drjones` (Sarah Jones, Gen. Medicine — flagship), `drsarahjones00` (Cardiology), `drjamessmith01` (Gen. Medicine), `dremilypatel02` (Orthopedics), `drmichaelgarcia03` (Pediatrics), `drdanielbrown05` (Gen. Medicine) |
| Riverside Medical Center | `drsophiakim10`, `drethannguyen11`, `dravadavis12`, `drmatthewwilson13`, `drisabellamartinez14`, `drdavidclark15` |
| Sunrise Health Institute | `drmialewis20`, `drjosephwalker21`, `drcharlottehall22`, `drandrewyoung23`, `drameliaallen24`, `drryanwright25` |
| Lakeside Regional Hospital | `drgraceking30`, `drnathanscott31`, `drchloegreen32`, `drkevinbaker33`, `drlilyadams34`, `drbriannelson35` |
| Metro Care Hospital | `drzoecarter40`, `drjustinmitchell41`, `drhannahperez42`, `draaronroberts43`, `drellaturner44`, `drtylerphillips45` |

The exact name/specialization/department behind each username is visible in
the app itself once logged in as `Shyamcharan` → **Accounts**, or in the
Hospital Directory (open to every role).

### 5. Run the app

```
python manage.py runserver
```

Visit http://127.0.0.1:8000/ and log in with one of the seeded accounts above
(pick the matching role on the login form).

### 6. (Optional) Run Celery for reminder automation

In separate terminals, with Redis running:

```
celery -A healthcare_config worker -l info
celery -A healthcare_config beat -l info
```

The beat schedule marks any `Pending` reminder whose scheduled time has passed
as `Missed`, which feeds the adherence percentage on the patient dashboard.

## Key business rules implemented

1. **Automatic doctor-patient linking** — created only when a doctor issues a
   digital prescription (`prescriptions/views.py::create_prescription`), never
   by the Administrator, and never duplicated (`get_or_create`).
2. **Hospital Directory is open to all authenticated roles**; only the
   Administrator can create/edit hospitals, departments, or doctor
   hospital/department assignment.
3. **Consultation notes are doctor-authored only** — there is no patient-facing
   entry point for `ConsultationNote`.
4. **OCR verification is a required loop** — `prescriptions:upload` runs OCR
   and stores extracted rows in the session; nothing is saved to the database
   until the patient reviews/corrects them on `prescriptions:verify_upload`
   and confirms.
5. **Prescription status** is a 3-value enum: Active / Completed / Archived.
6. **Medicine lookup + interaction check** is one combined view/action
   (`medications:lookup`) backed by the shared `Medicine`/`DrugInteraction`
   tables.
7. **Dashboards never read `Medicine`/`DrugInteraction` directly** — those
   tables are only touched by the OCR/prescription flow and the lookup view.
8. **Role-scoped visibility** is enforced via `core.decorators.role_required`
   plus per-view ownership checks (a doctor only sees their own linked
   patients; a patient only ever sees their own records; the Administrator
   can see across all doctors/patients).
