/**
 * FHIR R4 Type Definitions
 * Based on HL7 FHIR R4 specification
 */

// Base FHIR types
export interface FHIRResource {
  resourceType: string
  id?: string
  meta?: Meta
}

export interface Meta {
  versionId?: string
  lastUpdated?: string
}

// Human Name
export interface HumanName {
  use?: 'official' | 'usual' | 'temp' | 'nickname' | 'anonymous' | 'old' | 'maiden'
  text?: string
  family?: string
  given?: string[]
  prefix?: string[]
  suffix?: string[]
}

// Address
export interface Address {
  use?: 'home' | 'work' | 'temp' | 'old' | 'billing'
  type?: 'postal' | 'physical' | 'both'
  text?: string
  line?: string[]
  city?: string
  district?: string
  state?: string
  postalCode?: string
  country?: string
}

// Contact Point (telecom)
export interface ContactPoint {
  system?: 'phone' | 'fax' | 'email' | 'pager' | 'url' | 'sms' | 'other'
  value?: string
  use?: 'home' | 'work' | 'temp' | 'old' | 'mobile'
  rank?: number
}

// Identifier
export interface Identifier {
  use?: 'usual' | 'official' | 'temp' | 'secondary' | 'old'
  system?: string
  value?: string
}

// Codeable Concept
export interface CodeableConcept {
  coding?: Coding[]
  text?: string
}

export interface Coding {
  system?: string
  code?: string
  display?: string
}

// Reference
export interface Reference {
  reference?: string
  type?: string
  display?: string
}

// Period
export interface Period {
  start?: string
  end?: string
}

// Patient Resource
export interface Patient extends FHIRResource {
  resourceType: 'Patient'
  active?: boolean
  name?: HumanName[]
  telecom?: ContactPoint[]
  gender?: 'male' | 'female' | 'other' | 'unknown'
  birthDate?: string
  address?: Address[]
  identifier?: Identifier[]
}

// Practitioner Resource
export interface Practitioner extends FHIRResource {
  resourceType: 'Practitioner'
  active?: boolean
  name?: HumanName[]
  telecom?: ContactPoint[]
  address?: Address[]
  gender?: 'male' | 'female' | 'other' | 'unknown'
  birthDate?: string
  identifier?: Identifier[]
  qualification?: PractitionerQualification[]
  // Custom fields (non-standard FHIR)
  specialization?: string
  years_of_experience?: number
}

export interface PractitionerQualification {
  identifier?: Identifier[]
  code: CodeableConcept
  period?: Period
  issuer?: Reference
}

// Appointment Resource
export interface Appointment extends FHIRResource {
  resourceType: 'Appointment'
  status: 'proposed' | 'pending' | 'booked' | 'arrived' | 'fulfilled' | 'cancelled' | 'noshow' | 'entered-in-error' | 'checked-in' | 'waitlist'
  cancelationReason?: CodeableConcept
  serviceCategory?: CodeableConcept[]
  serviceType?: ServiceType[]
  specialty?: CodeableConcept[]
  appointmentType?: CodeableConcept
  reasonCode?: CodeableConcept[]
  reasonReference?: Reference[]
  priority?: number
  description?: string
  start?: string
  end?: string
  minutesDuration?: number
  slot?: Reference[]
  created?: string
  comment?: string
  patientInstruction?: string
  participant: AppointmentParticipant[]
}

export interface ServiceType {
  coding?: Coding[]
  text?: string
}

export interface AppointmentParticipant {
  type?: CodeableConcept[]
  actor?: Reference
  required?: 'required' | 'optional' | 'information-only'
  status: 'accepted' | 'declined' | 'tentative' | 'needs-action'
  period?: Period
}

// MedicationRequest (Prescription) Resource
export interface MedicationRequest extends FHIRResource {
  resourceType: 'MedicationRequest'
  status: 'active' | 'on-hold' | 'cancelled' | 'completed' | 'entered-in-error' | 'stopped' | 'draft' | 'unknown'
  intent: 'proposal' | 'plan' | 'order' | 'original-order' | 'reflex-order' | 'filler-order' | 'instance-order' | 'option'
  category?: CodeableConcept[]
  priority?: 'routine' | 'urgent' | 'asap' | 'stat'
  medicationCodeableConcept?: CodeableConcept
  medicationReference?: Reference
  subject: Reference
  encounter?: Reference
  supportingInformation?: Reference[]
  authoredOn?: string
  requester?: Reference
  performer?: Reference
  performerType?: CodeableConcept
  recorder?: Reference
  reasonCode?: CodeableConcept[]
  reasonReference?: Reference[]
  note?: Annotation[]
  dosageInstruction?: Dosage[]
  dispenseRequest?: DispenseRequest
  substitution?: MedicationRequestSubstitution
  // Custom fields for simplified display
  medication_name?: string
  patient_name?: string
  prescriber_name?: string
  dosage_text?: string
  dosage_period_start?: string
  dosage_period_end?: string
}

export interface Annotation {
  authorReference?: Reference
  authorString?: string
  time?: string
  text: string
}

export interface Dosage {
  sequence?: number
  text?: string
  additionalInstruction?: CodeableConcept[]
  patientInstruction?: string
  timing?: Timing
  asNeededBoolean?: boolean
  asNeededCodeableConcept?: CodeableConcept
  site?: CodeableConcept
  route?: CodeableConcept
  method?: CodeableConcept
  doseAndRate?: DoseAndRate[]
  maxDosePerPeriod?: Ratio
  maxDosePerAdministration?: Quantity
  maxDosePerLifetime?: Quantity
}

export interface Timing {
  event?: string[]
  repeat?: TimingRepeat
  code?: CodeableConcept
}

export interface TimingRepeat {
  boundsDuration?: Duration
  boundsRange?: Range
  boundsPeriod?: Period
  count?: number
  countMax?: number
  duration?: number
  durationMax?: number
  durationUnit?: 's' | 'min' | 'h' | 'd' | 'wk' | 'mo' | 'a'
  frequency?: number
  frequencyMax?: number
  period?: number
  periodMax?: number
  periodUnit?: 's' | 'min' | 'h' | 'd' | 'wk' | 'mo' | 'a'
  dayOfWeek?: string[]
  timeOfDay?: string[]
  when?: string[]
  offset?: number
}

export interface Duration {
  value?: number
  comparator?: '<' | '<=' | '>=' | '>'
  unit?: string
  system?: string
  code?: string
}

export interface Range {
  low?: Quantity
  high?: Quantity
}

export interface DoseAndRate {
  type?: CodeableConcept
  doseRange?: Range
  doseQuantity?: Quantity
  rateRatio?: Ratio
  rateRange?: Range
  rateQuantity?: Quantity
}

export interface Quantity {
  value?: number
  comparator?: '<' | '<=' | '>=' | '>'
  unit?: string
  system?: string
  code?: string
}

export interface Ratio {
  numerator?: Quantity
  denominator?: Quantity
}

export interface DispenseRequest {
  initialFill?: DispenseRequestInitialFill
  dispenseInterval?: Duration
  validityPeriod?: Period
  numberOfRepeatsAllowed?: number
  quantity?: Quantity
  expectedSupplyDuration?: Duration
  performer?: Reference
}

export interface DispenseRequestInitialFill {
  quantity?: Quantity
  duration?: Duration
}

export interface MedicationRequestSubstitution {
  allowedBoolean?: boolean
  allowedCodeableConcept?: CodeableConcept
  reason?: CodeableConcept
}

// Observation (for Clinical Records/Patient History)
export interface Observation extends FHIRResource {
  resourceType: 'Observation'
  status: 'registered' | 'preliminary' | 'final' | 'amended' | 'corrected' | 'cancelled' | 'entered-in-error' | 'unknown'
  category?: CodeableConcept[]
  code: CodeableConcept
  subject?: Reference
  encounter?: Reference
  effectiveDateTime?: string
  effectivePeriod?: Period
  issued?: string
  performer?: Reference[]
  valueQuantity?: Quantity
  valueCodeableConcept?: CodeableConcept
  valueString?: string
  valueBoolean?: boolean
  valueInteger?: number
  valueRange?: Range
  valueRatio?: Ratio
  valueSampledData?: SampledData
  valueTime?: string
  valueDateTime?: string
  valuePeriod?: Period
  dataAbsentReason?: CodeableConcept
  interpretation?: CodeableConcept[]
  note?: Annotation[]
  bodySite?: CodeableConcept
  method?: CodeableConcept
  specimen?: Reference
  device?: Reference
  referenceRange?: ObservationReferenceRange[]
  component?: ObservationComponent[]
}

export interface SampledData {
  origin: Quantity
  period: number
  factor?: number
  lowerLimit?: number
  upperLimit?: number
  dimensions: number
  data?: string
}

export interface ObservationReferenceRange {
  low?: Quantity
  high?: Quantity
  type?: CodeableConcept
  appliesTo?: CodeableConcept[]
  age?: Range
  text?: string
}

export interface ObservationComponent {
  code: CodeableConcept
  valueQuantity?: Quantity
  valueCodeableConcept?: CodeableConcept
  valueString?: string
  valueBoolean?: boolean
  valueInteger?: number
  valueRange?: Range
  valueRatio?: Ratio
  valueSampledData?: SampledData
  valueTime?: string
  valueDateTime?: string
  valuePeriod?: Period
  dataAbsentReason?: CodeableConcept
  interpretation?: CodeableConcept[]
  referenceRange?: ObservationReferenceRange[]
}

// Invoice (for Billing)
export interface Invoice extends FHIRResource {
  resourceType: 'Invoice'
  identifier?: Identifier[]
  status: 'draft' | 'issued' | 'balanced' | 'cancelled' | 'entered-in-error'
  cancelledReason?: string
  type?: CodeableConcept
  subject?: Reference
  recipient?: Reference
  date?: string
  participant?: InvoiceParticipant[]
  issuer?: Reference
  account?: Reference
  lineItem?: InvoiceLineItem[]
  totalPriceComponent?: InvoicePriceComponent[]
  totalNet?: Money
  totalGross?: Money
  paymentTerms?: string
  note?: Annotation[]
}

export interface InvoiceParticipant {
  role?: CodeableConcept
  actor: Reference
}

export interface InvoiceLineItem {
  sequence?: number
  chargeItemReference?: Reference
  chargeItemCodeableConcept?: CodeableConcept
  priceComponent?: InvoicePriceComponent[]
}

export interface InvoicePriceComponent {
  type: 'base' | 'surcharge' | 'deduction' | 'discount' | 'tax' | 'informational'
  code?: CodeableConcept
  factor?: number
  amount?: Money
}

export interface Money {
  value?: number
  currency?: string
}

// FHIR Bundle (for list responses)
export interface Bundle<T extends FHIRResource = FHIRResource> {
  resourceType: 'Bundle'
  type: 'document' | 'message' | 'transaction' | 'transaction-response' | 'batch' | 'batch-response' | 'history' | 'searchset' | 'collection'
  total?: number
  link?: BundleLink[]
  entry?: BundleEntry<T>[]
}

export interface BundleLink {
  relation: string
  url: string
}

export interface BundleEntry<T extends FHIRResource = FHIRResource> {
  fullUrl?: string
  resource?: T
  search?: BundleEntrySearch
}

export interface BundleEntrySearch {
  mode?: 'match' | 'include' | 'outcome'
  score?: number
}
