from datetime import date

import app.models  # registra relaciones ORM

from app.core.database import SessionLocal
from app.schemas.patient import PatientCreate
from app.schemas.clinical_record import ClinicalRecordCreate
from app.services.patient_service import (
    create_patient,
    get_patient_by_document,
    list_patients,
)
from app.services.clinical_record_service import (
    create_clinical_record,
    list_clinical_records_by_patient,
)


def main():
    db = SessionLocal()
    try:
        # ---------- PATIENT ----------
        data = PatientCreate(
            full_name="Juan Perez",
            document_type="CC",
            document_number="123456789",
            birth_date=date(2000, 1, 15),
            gender="M",
        )

        patient = get_patient_by_document(db, data.document_type, data.document_number)
        if patient:
            print("YA EXISTE:", patient.id, patient.full_name)
        else:
            patient = create_patient(db, data)
            print("CREADO:", patient.id, patient.full_name)

        items, total = list_patients(db, q="Juan")
        print("PACIENTES:", total)

        record = create_clinical_record(
            db,
            patient.id,
            ClinicalRecordCreate(content="Consulta inicial.")
        )
        print("RECORD CREADO:", record.id, record.patient_id)

        records, total_records = list_clinical_records_by_patient(
            db,
            patient.id,
            skip=0,
            limit=10,
        )
        print("TOTAL RECORDS:", total_records)
        print("RECORDS:", [(str(r.id), r.created_at) for r in records])

    finally:
        db.close()


if __name__ == "__main__":
    main()
