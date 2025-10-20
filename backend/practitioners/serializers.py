"""
Serializers for Practitioner models.

This module provides Django REST Framework serializers for Practitioner models,
including both standard Django serialization and FHIR R4 compliant serialization.
"""

from datetime import datetime
from rest_framework import serializers
from fhir.resources.practitioner import Practitioner as FHIRPractitioner, PractitionerQualification
from fhir.resources.humanname import HumanName
from fhir.resources.address import Address
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.identifier import Identifier
from fhir.resources.codeableconcept import CodeableConcept

from .models import Practitioner


class PractitionerSerializer(serializers.ModelSerializer):
    """
    Standard Django REST Framework serializer for Practitioner model.

    This serializer handles basic CRUD operations for practitioners
    using Django's standard serialization format.
    """

    full_name = serializers.SerializerMethodField()
    credentials = serializers.SerializerMethodField()

    class Meta:
        model = Practitioner
        fields = [
            'id',
            'prefix',
            'given_name',
            'middle_name',
            'family_name',
            'full_name',
            'credentials',
            'gender',
            'birth_date',
            'npi',
            'license_number',
            'specialization',
            'qualification',
            'years_of_experience',
            'email',
            'phone',
            'address_line',
            'address_city',
            'address_state',
            'address_postal_code',
            'address_country',
            'active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'full_name', 'credentials']

    def get_full_name(self, obj):
        """Get the full name with prefix."""
        return obj.get_full_name()

    def get_credentials(self, obj):
        """Get formatted credentials string."""
        return obj.get_credentials()


class FHIRPractitionerSerializer(serializers.Serializer):
    """
    FHIR R4 compliant serializer for Practitioner resource.
    Converts Django Practitioner model to/from FHIR Practitioner resource format.
    """

    def to_representation(self, instance):
        """
        Convert Django Practitioner instance to FHIR Practitioner resource.

        Args:
            instance: Practitioner model instance

        Returns:
            dict: FHIR-compliant Practitioner resource dictionary
        """
        # Build HumanName
        given_names = [instance.given_name]
        if instance.middle_name:
            given_names.append(instance.middle_name)

        name_data = {
            'use': 'official',
            'family': instance.family_name,
            'given': given_names
        }

        if instance.prefix:
            name_data['prefix'] = [instance.prefix]

        name = HumanName(**name_data)

        # Build Identifiers
        identifiers = []
        if instance.npi:
            identifiers.append(Identifier(**{
                'system': 'http://hl7.org/fhir/sid/us-npi',
                'value': instance.npi,
                'use': 'official'
            }))

        if instance.license_number:
            identifiers.append(Identifier(**{
                'system': 'http://hospital.example.org/practitioners/license',
                'value': instance.license_number,
                'use': 'official'
            }))

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
            address_data['use'] = 'work'
            address = Address(**address_data)

        # Build ContactPoints (telecom)
        telecom = []
        if instance.email:
            telecom.append(ContactPoint(**{
                'system': 'email',
                'value': instance.email,
                'use': 'work'
            }))
        if instance.phone:
            telecom.append(ContactPoint(**{
                'system': 'phone',
                'value': instance.phone,
                'use': 'work'
            }))

        # Build Qualifications
        qualifications = []
        if instance.qualification:
            qualifications.append(PractitionerQualification(**{
                'code': CodeableConcept(**{
                    'text': instance.qualification
                })
            }))

        # Create FHIR Practitioner resource
        fhir_data = {
            'resourceType': 'Practitioner',
            'id': str(instance.id),
            'active': instance.active,
            'name': [name],
        }

        if identifiers:
            fhir_data['identifier'] = identifiers

        if instance.gender:
            fhir_data['gender'] = instance.gender

        if instance.birth_date:
            fhir_data['birthDate'] = instance.birth_date.isoformat()

        if address:
            fhir_data['address'] = [address]

        if telecom:
            fhir_data['telecom'] = telecom

        if qualifications:
            fhir_data['qualification'] = qualifications

        # Create FHIR Practitioner and return as dict
        fhir_practitioner = FHIRPractitioner(**fhir_data)
        result = fhir_practitioner.dict(exclude_none=True)

        # Ensure birthDate is a string (fhir.resources may convert it back to date object)
        if 'birthDate' in result and instance.birth_date:
            result['birthDate'] = instance.birth_date.isoformat()

        # Add custom extension for specialization (not standard FHIR but useful)
        if instance.specialization:
            result['specialization'] = instance.specialization

        if instance.years_of_experience:
            result['years_of_experience'] = instance.years_of_experience

        return result

    def to_internal_value(self, data):
        """
        Convert FHIR Practitioner resource to Django Practitioner model data.

        Args:
            data: FHIR Practitioner resource dictionary

        Returns:
            dict: Validated data for Practitioner model
        """
        # Validate resource type
        if data.get('resourceType') != 'Practitioner':
            raise serializers.ValidationError({
                'resourceType': 'Resource must be of type Practitioner'
            })

        # Extract custom fields before FHIR validation
        custom_fields = {}
        fhir_data = data.copy()

        if 'specialization' in fhir_data:
            custom_fields['specialization'] = fhir_data.pop('specialization')
        if 'years_of_experience' in fhir_data:
            custom_fields['years_of_experience'] = fhir_data.pop('years_of_experience')

        # Parse FHIR resource using fhir.resources
        try:
            fhir_practitioner = FHIRPractitioner(**fhir_data)
        except Exception as e:
            raise serializers.ValidationError({
                'fhir_validation': f'Invalid FHIR Practitioner resource: {str(e)}'
            })

        # Extract name
        if not fhir_practitioner.name or len(fhir_practitioner.name) == 0:
            raise serializers.ValidationError({
                'name': 'At least one name is required'
            })

        name = fhir_practitioner.name[0]
        given_names = name.given or []

        practitioner_data = {
            'family_name': name.family,
            'given_name': given_names[0] if given_names else '',
            'middle_name': given_names[1] if len(given_names) > 1 else None,
            'active': fhir_practitioner.active if fhir_practitioner.active is not None else True
        }

        # Extract prefix
        if name.prefix and len(name.prefix) > 0:
            practitioner_data['prefix'] = name.prefix[0]

        # Extract gender
        if fhir_practitioner.gender:
            practitioner_data['gender'] = fhir_practitioner.gender

        # Extract birth date
        if fhir_practitioner.birthDate:
            if isinstance(fhir_practitioner.birthDate, str):
                practitioner_data['birth_date'] = datetime.fromisoformat(fhir_practitioner.birthDate).date()
            else:
                practitioner_data['birth_date'] = fhir_practitioner.birthDate

        # Extract identifiers
        if fhir_practitioner.identifier:
            for identifier in fhir_practitioner.identifier:
                if identifier.system == 'http://hl7.org/fhir/sid/us-npi':
                    practitioner_data['npi'] = identifier.value
                elif 'license' in (identifier.system or '').lower():
                    practitioner_data['license_number'] = identifier.value

        # Extract address
        if fhir_practitioner.address and len(fhir_practitioner.address) > 0:
            address = fhir_practitioner.address[0]
            practitioner_data['address_line'] = address.line[0] if address.line else None
            practitioner_data['address_city'] = address.city
            practitioner_data['address_state'] = address.state
            practitioner_data['address_postal_code'] = address.postalCode
            practitioner_data['address_country'] = address.country

        # Extract telecom
        if fhir_practitioner.telecom:
            for contact in fhir_practitioner.telecom:
                if contact.system == 'email':
                    practitioner_data['email'] = contact.value
                elif contact.system == 'phone':
                    practitioner_data['phone'] = contact.value

        # Extract qualifications
        if fhir_practitioner.qualification and len(fhir_practitioner.qualification) > 0:
            qualification = fhir_practitioner.qualification[0]
            if qualification.code and qualification.code.text:
                practitioner_data['qualification'] = qualification.code.text

        # Add custom fields (specialization, years_of_experience)
        if 'specialization' in custom_fields:
            practitioner_data['specialization'] = custom_fields['specialization']

        if 'years_of_experience' in custom_fields:
            practitioner_data['years_of_experience'] = custom_fields['years_of_experience']

        # Ensure required fields
        if 'email' not in practitioner_data:
            raise serializers.ValidationError({
                'email': 'Email is required'
            })

        if 'phone' not in practitioner_data:
            raise serializers.ValidationError({
                'phone': 'Phone number is required'
            })

        if 'specialization' not in practitioner_data:
            raise serializers.ValidationError({
                'specialization': 'Specialization is required'
            })

        if 'qualification' not in practitioner_data:
            raise serializers.ValidationError({
                'qualification': 'Qualification is required'
            })

        return practitioner_data

    def create(self, validated_data):
        """Create a new Practitioner instance from validated FHIR data."""
        return Practitioner.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update an existing Practitioner instance from validated FHIR data."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
