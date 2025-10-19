"""
Factory Pattern implementation for FHIR resource creation.

The Factory Pattern provides a centralized way to create FHIR-compliant
resource objects from Django models, ensuring consistency and reducing
code duplication.

Benefits:
- Open/Closed Principle: Easy to add new FHIR resources without modifying existing code
- Single Responsibility: Each factory method handles one resource type
- Dependency Inversion: Code depends on the factory interface, not concrete implementations
- Consistency: All FHIR resources are created using the same pattern
- Testability: Easy to test FHIR resource generation
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type
from datetime import datetime
from django.db import models
from fhir.resources.patient import Patient as FHIRPatient
from fhir.resources.practitioner import Practitioner as FHIRPractitioner
from fhir.resources.appointment import Appointment as FHIRAppointment
from fhir.resources.medicationrequest import MedicationRequest as FHIRMedicationRequest
from fhir.resources.encounter import Encounter as FHIREncounter
from fhir.resources.claim import Claim as FHIRClaim
from fhir.resources.diagnosticreport import DiagnosticReport as FHIRDiagnosticReport


class FHIRResourceFactory:
    """
    Factory for creating FHIR-compliant resource objects.

    This factory provides static methods to convert Django model instances
    into FHIR R4 compliant resource objects. It follows the Factory Pattern
    to ensure consistent FHIR resource creation across the application.

    Usage:
        patient_fhir = FHIRResourceFactory.create_patient(patient_model)
        practitioner_fhir = FHIRResourceFactory.create_practitioner(doctor_model)

    Note:
        All methods return FHIR resource objects from the fhir.resources library.
        These can be serialized to JSON using the .dict() method.
    """

    @staticmethod
    def create_patient(patient_model) -> FHIRPatient:
        """
        Create a FHIR Patient resource from a Patient model instance.

        Args:
            patient_model: Django Patient model instance

        Returns:
            FHIR Patient resource

        Example:
            patient = Patient.objects.get(id=patient_id)
            fhir_patient = FHIRResourceFactory.create_patient(patient)
            json_data = fhir_patient.dict()
        """
        from fhir.resources.humanname import HumanName
        from fhir.resources.identifier import Identifier
        from fhir.resources.contactpoint import ContactPoint
        from fhir.resources.address import Address

        # Build name
        name = HumanName(
            use="official",
            family=patient_model.family_name,
            given=[patient_model.given_name]
        )

        # Build identifiers
        identifiers = []
        if hasattr(patient_model, 'mrn') and patient_model.mrn:
            identifiers.append(Identifier(
                system="http://hospital.example.org/patients",
                value=patient_model.mrn
            ))

        # Build telecom (contact points)
        telecom = []
        if hasattr(patient_model, 'phone') and patient_model.phone:
            telecom.append(ContactPoint(
                system="phone",
                value=patient_model.phone,
                use="mobile"
            ))
        if hasattr(patient_model, 'email') and patient_model.email:
            telecom.append(ContactPoint(
                system="email",
                value=patient_model.email
            ))

        # Build address
        addresses = []
        if hasattr(patient_model, 'address_line') and patient_model.address_line:
            addresses.append(Address(
                use="home",
                line=[patient_model.address_line],
                city=getattr(patient_model, 'city', None),
                state=getattr(patient_model, 'state', None),
                postalCode=getattr(patient_model, 'postal_code', None),
                country=getattr(patient_model, 'country', None)
            ))

        # Create FHIR Patient resource
        fhir_patient = FHIRPatient(
            id=str(patient_model.id),
            identifier=identifiers if identifiers else None,
            active=getattr(patient_model, 'active', True),
            name=[name],
            telecom=telecom if telecom else None,
            gender=getattr(patient_model, 'gender', None),
            birthDate=patient_model.birth_date.isoformat() if hasattr(patient_model, 'birth_date') and patient_model.birth_date else None,
            address=addresses if addresses else None
        )

        return fhir_patient

    @staticmethod
    def create_practitioner(practitioner_model) -> FHIRPractitioner:
        """
        Create a FHIR Practitioner resource from a Practitioner model instance.

        Args:
            practitioner_model: Django Practitioner model instance

        Returns:
            FHIR Practitioner resource
        """
        from fhir.resources.humanname import HumanName
        from fhir.resources.identifier import Identifier
        from fhir.resources.contactpoint import ContactPoint
        from fhir.resources.practitionerrole import PractitionerRole
        from fhir.resources.codeableconcept import CodeableConcept
        from fhir.resources.coding import Coding

        # Build name
        name = HumanName(
            use="official",
            family=practitioner_model.family_name,
            given=[practitioner_model.given_name],
            prefix=[practitioner_model.prefix] if hasattr(practitioner_model, 'prefix') and practitioner_model.prefix else None
        )

        # Build identifiers
        identifiers = []
        if hasattr(practitioner_model, 'npi') and practitioner_model.npi:
            identifiers.append(Identifier(
                system="http://hl7.org/fhir/sid/us-npi",
                value=practitioner_model.npi
            ))

        # Build telecom
        telecom = []
        if hasattr(practitioner_model, 'phone') and practitioner_model.phone:
            telecom.append(ContactPoint(
                system="phone",
                value=practitioner_model.phone,
                use="work"
            ))
        if hasattr(practitioner_model, 'email') and practitioner_model.email:
            telecom.append(ContactPoint(
                system="email",
                value=practitioner_model.email
            ))

        # Build qualification
        qualifications = []
        if hasattr(practitioner_model, 'qualification') and practitioner_model.qualification:
            from fhir.resources.practitionerqualification import PractitionerQualification
            qualifications.append(PractitionerQualification(
                code=CodeableConcept(
                    text=practitioner_model.qualification
                )
            ))

        # Create FHIR Practitioner resource
        fhir_practitioner = FHIRPractitioner(
            id=str(practitioner_model.id),
            identifier=identifiers if identifiers else None,
            active=getattr(practitioner_model, 'active', True),
            name=[name],
            telecom=telecom if telecom else None,
            gender=getattr(practitioner_model, 'gender', None),
            qualification=qualifications if qualifications else None
        )

        return fhir_practitioner

    @staticmethod
    def create_appointment(appointment_model) -> FHIRAppointment:
        """
        Create a FHIR Appointment resource from an Appointment model instance.

        Args:
            appointment_model: Django Appointment model instance

        Returns:
            FHIR Appointment resource
        """
        from fhir.resources.reference import Reference
        from fhir.resources.appointmentparticipant import AppointmentParticipant
        from fhir.resources.codeableconcept import CodeableConcept

        # Build participants
        participants = []

        # Patient participant
        if hasattr(appointment_model, 'patient') and appointment_model.patient:
            participants.append(AppointmentParticipant(
                actor=Reference(
                    reference=f"Patient/{appointment_model.patient.id}",
                    display=f"{appointment_model.patient.given_name} {appointment_model.patient.family_name}"
                ),
                status="accepted",
                required="required"
            ))

        # Practitioner participant
        if hasattr(appointment_model, 'practitioner') and appointment_model.practitioner:
            participants.append(AppointmentParticipant(
                actor=Reference(
                    reference=f"Practitioner/{appointment_model.practitioner.id}",
                    display=f"{appointment_model.practitioner.given_name} {appointment_model.practitioner.family_name}"
                ),
                status="accepted",
                required="required"
            ))

        # Create FHIR Appointment resource
        fhir_appointment = FHIRAppointment(
            id=str(appointment_model.id),
            status=getattr(appointment_model, 'status', 'booked'),
            start=appointment_model.start_time.isoformat() if hasattr(appointment_model, 'start_time') and appointment_model.start_time else None,
            end=appointment_model.end_time.isoformat() if hasattr(appointment_model, 'end_time') and appointment_model.end_time else None,
            participant=participants if participants else None,
            description=getattr(appointment_model, 'reason', None),
            comment=getattr(appointment_model, 'notes', None)
        )

        return fhir_appointment

    @staticmethod
    def create_medication_request(prescription_model) -> FHIRMedicationRequest:
        """
        Create a FHIR MedicationRequest resource from a Prescription model instance.

        Args:
            prescription_model: Django Prescription model instance

        Returns:
            FHIR MedicationRequest resource
        """
        from fhir.resources.reference import Reference
        from fhir.resources.codeableconcept import CodeableConcept
        from fhir.resources.coding import Coding
        from fhir.resources.dosage import Dosage

        # Build medication reference
        medication_codeable = CodeableConcept(
            text=getattr(prescription_model, 'medication_name', 'Unknown')
        )

        # Build dosage instruction
        dosage = []
        if hasattr(prescription_model, 'dosage_instruction') and prescription_model.dosage_instruction:
            dosage.append(Dosage(
                text=prescription_model.dosage_instruction
            ))

        # Create FHIR MedicationRequest resource
        fhir_med_request = FHIRMedicationRequest(
            id=str(prescription_model.id),
            status=getattr(prescription_model, 'status', 'active'),
            intent="order",
            medicationCodeableConcept=medication_codeable,
            subject=Reference(
                reference=f"Patient/{prescription_model.patient.id}",
                display=f"{prescription_model.patient.given_name} {prescription_model.patient.family_name}"
            ) if hasattr(prescription_model, 'patient') and prescription_model.patient else None,
            authoredOn=prescription_model.created_at.isoformat() if hasattr(prescription_model, 'created_at') and prescription_model.created_at else None,
            requester=Reference(
                reference=f"Practitioner/{prescription_model.practitioner.id}",
                display=f"{prescription_model.practitioner.given_name} {prescription_model.practitioner.family_name}"
            ) if hasattr(prescription_model, 'practitioner') and prescription_model.practitioner else None,
            dosageInstruction=dosage if dosage else None
        )

        return fhir_med_request

    @staticmethod
    def create_encounter(encounter_model) -> FHIREncounter:
        """
        Create a FHIR Encounter resource from an Encounter model instance.

        Args:
            encounter_model: Django Encounter model instance

        Returns:
            FHIR Encounter resource
        """
        from fhir.resources.reference import Reference
        from fhir.resources.codeableconcept import CodeableConcept
        from fhir.resources.coding import Coding
        from fhir.resources.encounterparticipant import EncounterParticipant
        from fhir.resources.period import Period

        # Build class coding
        encounter_class = Coding(
            system="http://terminology.hl7.org/CodeSystem/v3-ActCode",
            code=getattr(encounter_model, 'class_code', 'AMB'),
            display=getattr(encounter_model, 'class_display', 'ambulatory')
        )

        # Build participants
        participants = []
        if hasattr(encounter_model, 'practitioner') and encounter_model.practitioner:
            participants.append(EncounterParticipant(
                individual=Reference(
                    reference=f"Practitioner/{encounter_model.practitioner.id}",
                    display=f"{encounter_model.practitioner.given_name} {encounter_model.practitioner.family_name}"
                )
            ))

        # Build period
        period = None
        if hasattr(encounter_model, 'start_time') and encounter_model.start_time:
            period = Period(
                start=encounter_model.start_time.isoformat(),
                end=encounter_model.end_time.isoformat() if hasattr(encounter_model, 'end_time') and encounter_model.end_time else None
            )

        # Create FHIR Encounter resource
        fhir_encounter = FHIREncounter(
            id=str(encounter_model.id),
            status=getattr(encounter_model, 'status', 'finished'),
            class_fhir=encounter_class,
            subject=Reference(
                reference=f"Patient/{encounter_model.patient.id}",
                display=f"{encounter_model.patient.given_name} {encounter_model.patient.family_name}"
            ) if hasattr(encounter_model, 'patient') and encounter_model.patient else None,
            participant=participants if participants else None,
            period=period,
            reasonCode=[CodeableConcept(text=encounter_model.reason)] if hasattr(encounter_model, 'reason') and encounter_model.reason else None
        )

        return fhir_encounter

    @staticmethod
    def create_claim(claim_model) -> FHIRClaim:
        """
        Create a FHIR Claim resource from a Claim model instance.

        Args:
            claim_model: Django Claim model instance

        Returns:
            FHIR Claim resource
        """
        from fhir.resources.reference import Reference
        from fhir.resources.codeableconcept import CodeableConcept
        from fhir.resources.money import Money

        # Create FHIR Claim resource
        fhir_claim = FHIRClaim(
            id=str(claim_model.id),
            status=getattr(claim_model, 'status', 'active'),
            type=CodeableConcept(
                text=getattr(claim_model, 'claim_type', 'institutional')
            ),
            use=getattr(claim_model, 'use', 'claim'),
            patient=Reference(
                reference=f"Patient/{claim_model.patient.id}",
                display=f"{claim_model.patient.given_name} {claim_model.patient.family_name}"
            ) if hasattr(claim_model, 'patient') and claim_model.patient else None,
            created=claim_model.created_at.isoformat() if hasattr(claim_model, 'created_at') and claim_model.created_at else None,
            provider=Reference(
                reference=f"Practitioner/{claim_model.practitioner.id}",
                display=f"{claim_model.practitioner.given_name} {claim_model.practitioner.family_name}"
            ) if hasattr(claim_model, 'practitioner') and claim_model.practitioner else None,
            priority=CodeableConcept(text="normal"),
            total=Money(
                value=float(claim_model.total_amount) if hasattr(claim_model, 'total_amount') and claim_model.total_amount else 0.0,
                currency="USD"
            ) if hasattr(claim_model, 'total_amount') else None
        )

        return fhir_claim

    @staticmethod
    def create_diagnostic_report(report_model) -> FHIRDiagnosticReport:
        """
        Create a FHIR DiagnosticReport resource from a Report model instance.

        Args:
            report_model: Django Report model instance

        Returns:
            FHIR DiagnosticReport resource
        """
        from fhir.resources.reference import Reference
        from fhir.resources.codeableconcept import CodeableConcept

        # Create FHIR DiagnosticReport resource
        fhir_report = FHIRDiagnosticReport(
            id=str(report_model.id),
            status=getattr(report_model, 'status', 'final'),
            code=CodeableConcept(
                text=getattr(report_model, 'report_type', 'General Report')
            ),
            subject=Reference(
                reference=f"Patient/{report_model.patient.id}",
                display=f"{report_model.patient.given_name} {report_model.patient.family_name}"
            ) if hasattr(report_model, 'patient') and report_model.patient else None,
            effectiveDateTime=report_model.created_at.isoformat() if hasattr(report_model, 'created_at') and report_model.created_at else None,
            issued=report_model.created_at.isoformat() if hasattr(report_model, 'created_at') and report_model.created_at else None,
            conclusion=getattr(report_model, 'conclusion', None)
        )

        return fhir_report
