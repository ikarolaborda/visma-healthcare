"""
FHIR-compliant serializers for Patient resource.

This module provides serializers that convert between Django models
and FHIR R4 Patient resource format.
"""
from rest_framework import serializers
from .models import Patient
from fhir.resources.patient import Patient as FHIRPatient
from fhir.resources.humanname import HumanName
from fhir.resources.address import Address
from fhir.resources.contactpoint import ContactPoint
from datetime import datetime


class PatientSerializer(serializers.ModelSerializer):
    """
    Standard Django REST Framework serializer for Patient model.
    Used for internal API operations.
    """

    class Meta:
        model = Patient
        fields = [
            'id',
            'family_name',
            'given_name',
            'middle_name',
            'gender',
            'birth_date',
            'address_line',
            'address_city',
            'address_state',
            'address_postal_code',
            'address_country',
            'email',
            'phone',
            'active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FHIRPatientSerializer(serializers.Serializer):
    """
    FHIR R4 compliant serializer for Patient resource.
    Converts Django Patient model to/from FHIR Patient resource format.
    """

    def to_representation(self, instance):
        """
        Convert Django Patient instance to FHIR Patient resource.

        Args:
            instance: Patient model instance

        Returns:
            dict: FHIR-compliant Patient resource dictionary
        """
        # Build HumanName
        given_names = [instance.given_name]
        if instance.middle_name:
            given_names.append(instance.middle_name)

        name = HumanName(**{
            'use': 'official',
            'family': instance.family_name,
            'given': given_names
        })

        # Build Address
        address_data = {}
        if instance.address_line:
            address_data['line'] = [instance.address_line]
        if instance.address_city:
            address_data['city'] = instance.address_city
        if instance.address_state:
            address_data['state'] = instance.address_state
        if instance.address_postal_code:
            address_data['postalCode'] = instance.address_postal_code
        if instance.address_country:
            address_data['country'] = instance.address_country

        address = None
        if address_data:
            address_data['use'] = 'home'
            address = Address(**address_data)

        # Build ContactPoints (telecom)
        telecom = []
        if instance.email:
            telecom.append(ContactPoint(**{
                'system': 'email',
                'value': instance.email,
                'use': 'home'
            }))
        if instance.phone:
            telecom.append(ContactPoint(**{
                'system': 'phone',
                'value': instance.phone,
                'use': 'home'
            }))

        # Create FHIR Patient resource
        fhir_data = {
            'resourceType': 'Patient',
            'id': str(instance.id),
            'active': instance.active,
            'name': [name],
            'gender': instance.gender,
            'birthDate': instance.birth_date.isoformat()
        }

        if address:
            fhir_data['address'] = [address]

        if telecom:
            fhir_data['telecom'] = telecom

        # Create FHIR Patient and return as dict
        fhir_patient = FHIRPatient(**fhir_data)
        result = fhir_patient.dict(exclude_none=True)

        # Ensure birthDate is a string (fhir.resources may convert it back to date object)
        if 'birthDate' in result and instance.birth_date:
            result['birthDate'] = instance.birth_date.isoformat()

        # Add custom metadata fields (not part of standard FHIR but useful for UI)
        result['created_at'] = instance.created_at.isoformat()
        result['updated_at'] = instance.updated_at.isoformat()

        return result

    def to_internal_value(self, data):
        """
        Convert FHIR Patient resource to Django Patient model data.

        Args:
            data: FHIR Patient resource dictionary

        Returns:
            dict: Validated data for Patient model
        """
        # Validate resource type
        if data.get('resourceType') != 'Patient':
            raise serializers.ValidationError({
                'resourceType': 'Resource must be of type Patient'
            })

        # Remove non-FHIR fields before validation
        fhir_data = data.copy()
        fhir_data.pop('created_at', None)
        fhir_data.pop('updated_at', None)

        # Parse FHIR resource using fhir.resources
        try:
            fhir_patient = FHIRPatient(**fhir_data)
        except Exception as e:
            raise serializers.ValidationError({
                'fhir_validation': f'Invalid FHIR Patient resource: {str(e)}'
            })

        # Extract name
        if not fhir_patient.name or len(fhir_patient.name) == 0:
            raise serializers.ValidationError({
                'name': 'At least one name is required'
            })

        name = fhir_patient.name[0]
        given_names = name.given or []

        # Validate required fields
        if not fhir_patient.gender:
            raise serializers.ValidationError({
                'gender': 'This field is required'
            })

        # Validate gender is one of the FHIR allowed values
        valid_genders = ['male', 'female', 'other', 'unknown']
        if fhir_patient.gender not in valid_genders:
            raise serializers.ValidationError({
                'gender': f'Invalid gender code. Must be one of: {", ".join(valid_genders)}'
            })

        if not fhir_patient.birthDate:
            raise serializers.ValidationError({
                'birthDate': 'This field is required'
            })

        patient_data = {
            'family_name': name.family,
            'given_name': given_names[0] if given_names else '',
            'middle_name': given_names[1] if len(given_names) > 1 else None,
            'gender': fhir_patient.gender,
            'birth_date': datetime.fromisoformat(fhir_patient.birthDate).date() if isinstance(fhir_patient.birthDate, str) else fhir_patient.birthDate,
            'active': fhir_patient.active if fhir_patient.active is not None else True
        }

        # Extract address
        if fhir_patient.address and len(fhir_patient.address) > 0:
            address = fhir_patient.address[0]
            patient_data['address_line'] = address.line[0] if address.line else None
            patient_data['address_city'] = address.city
            patient_data['address_state'] = address.state
            patient_data['address_postal_code'] = address.postalCode
            patient_data['address_country'] = address.country

        # Extract telecom
        if fhir_patient.telecom:
            for contact in fhir_patient.telecom:
                if contact.system == 'email':
                    patient_data['email'] = contact.value
                elif contact.system == 'phone':
                    patient_data['phone'] = contact.value

        return patient_data

    def create(self, validated_data):
        """Create a new Patient instance from validated FHIR data."""
        return Patient.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update an existing Patient instance from validated FHIR data."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
