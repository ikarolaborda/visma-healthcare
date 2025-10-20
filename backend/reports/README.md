# Reports Module

## Overview

The Reports module provides comprehensive report generation capabilities for the FHIR R4 Healthcare Patient Management System. It implements modern software engineering patterns to ensure maintainability, extensibility, and adherence to SOLID principles.

## Design Patterns Implemented

### 1. Strategy Pattern
**Purpose**: Encapsulates different report generation algorithms (PDF, CSV, TXT, JSON)

**Implementation**:
- `IReportStrategy` (Abstract base class in `interfaces.py`)
- Concrete strategies in `strategies.py`:
  - `PDFReportStrategy` - Generates formatted PDF reports using ReportLab
  - `CSVReportStrategy` - Generates comma-separated value reports
  - `TXTReportStrategy` - Generates plain text tabular reports
  - `JSONReportStrategy` - Generates structured JSON reports

**Benefits**:
- Easy to add new output formats without modifying existing code
- Each format strategy is independent and testable
- Follows Open/Closed Principle (open for extension, closed for modification)

### 2. Factory Pattern
**Purpose**: Creates appropriate report strategy based on requested format

**Implementation**:
- `ReportFactory` class in `factory.py`
- Method: `create_strategy(format_type: str) -> IReportStrategy`
- Registry-based design allowing runtime strategy registration

**Benefits**:
- Centralizes object creation logic
- Decouples client code from concrete strategy classes
- Supports extensibility through runtime registration

### 3. Dependency Inversion Principle (DIP)
**Purpose**: High-level modules depend on abstractions, not concretions

**Implementation**:
- Abstract interfaces defined in `interfaces.py`:
  - `IReportGenerator` - Report generation service interface
  - `IReportStrategy` - Report format strategy interface
  - `IReportDataProvider` - Data fetching interface

- Concrete implementations:
  - `ReportService` implements `IReportGenerator`
  - Format strategies implement `IReportStrategy`
  - `DjangoReportDataProvider` implements `IReportDataProvider`

**Benefits**:
- Reduces coupling between components
- Enables easy mocking for unit tests
- Allows swapping implementations without changing client code

## Architecture Layers

### Domain Layer (`interfaces.py`)
Defines abstract interfaces that represent business contracts:
- `IReportStrategy` - Contract for report generation strategies
- `IReportGenerator` - Contract for report generation service
- `IReportDataProvider` - Contract for data retrieval

### Infrastructure Layer (`strategies.py`)
Concrete implementations of domain interfaces:
- PDF generation using ReportLab
- CSV generation using Python's csv module
- Plain text formatting
- JSON serialization

### Application Layer
- `factory.py` - Object creation and strategy selection
- `data_provider.py` - Data fetching from Django models
- `service.py` - Business logic orchestration

### Presentation Layer
- `views.py` - REST API endpoints
- `serializers.py` - Request/response serialization
- `urls.py` - URL routing

## API Endpoints

All endpoints require JWT authentication.

### Base URL: `/api/reports/`

#### 1. Get Available Options
```
GET /api/reports/options/
```
Returns available report types and output formats.

**Response**:
```json
{
  "report_types": ["patients", "practitioners", "appointments", ...],
  "formats": ["pdf", "csv", "txt", "json"]
}
```

#### 2. List Reports
```
GET /api/reports/
GET /api/reports/?report_type=patients&format=pdf&status=completed
```
Lists reports for the authenticated user with optional filtering.

**Query Parameters**:
- `report_type` - Filter by report type
- `format` - Filter by output format
- `status` - Filter by status (pending, processing, completed, failed)

#### 3. Generate Report
```
POST /api/reports/
```

**Request Body**:
```json
{
  "report_type": "patients",
  "format": "pdf",
  "title": "Active Patients Report",
  "description": "Report of all active patients",
  "filters": {
    "active": true,
    "created_from": "2025-01-01T00:00:00Z"
  }
}
```

**Response**: Report object with download URL (if completed)

#### 4. Get Report Details
```
GET /api/reports/{id}/
```
Retrieves details of a specific report.

#### 5. Download Report
```
GET /api/reports/{id}/download/
```
Downloads the generated report file.

#### 6. Delete Report
```
DELETE /api/reports/{id}/
```
Deletes a report and its associated file.

## Supported Report Types

1. **Patients Report** (`patients`)
   - Fields: ID, Full Name, Gender, Birth Date, Email, Phone, Status
   - Filters: active status, gender, date range

2. **Practitioners Report** (`practitioners`)
   - Fields: ID, Full Name, Specialization, Email, Phone, Status
   - Filters: active status, specialization

3. **Appointments Report** (`appointments`)
   - Fields: ID, Patient, Practitioner, Start Time, Status, Reason
   - Filters: status, date range, patient ID, practitioner ID

4. **Prescriptions Report** (`prescriptions`)
   - Fields: ID, Medication, Patient, Prescriber, Status, Dosage
   - Filters: status, patient ID, prescriber ID

5. **Invoices Report** (`invoices`)
   - Fields: ID, Patient, Total Amount, Status, Issued Date
   - Filters: status, patient ID

6. **Clinical Records Report** (`clinical_records`)
   - Fields: ID, Patient, Record Type, Date, Diagnosis
   - Filters: patient ID, record type

## Output Formats

### PDF
- Professional formatting with headers and footers
- Styled tables with alternating row colors
- Page numbers and metadata
- Uses ReportLab library

### CSV
- Standard comma-separated format
- Header row with field names
- Compatible with Excel and other spreadsheet software

### TXT
- Plain text tabular format
- Fixed-width columns
- ASCII-friendly
- Suitable for terminal viewing

### JSON
- Structured data format
- Includes metadata and data sections
- Easy to parse programmatically
- FHIR-compatible structure

## Data Model

### Report Model (`models.py`)

```python
class Report(models.Model):
    id = UUIDField  # Unique identifier
    user = ForeignKey(User)  # Report owner
    report_type = CharField  # Type of report
    format = CharField  # Output format
    status = CharField  # pending, processing, completed, failed
    filters = JSONField  # Filter parameters
    file = FileField  # Generated file
    file_size = IntegerField  # File size in bytes
    title = CharField  # Report title
    description = TextField  # Description
    record_count = IntegerField  # Number of records
    created_at = DateTimeField  # Creation timestamp
    updated_at = DateTimeField  # Last update
    completed_at = DateTimeField  # Completion timestamp
    error_message = TextField  # Error details if failed
```

## Usage Examples

### Generate a PDF report of active patients
```python
from reports.service import ReportService

service = ReportService()
report = service.generate_report(
    report_type='patients',
    format_type='pdf',
    filters={'active': True},
    user_id=1,
    title='Active Patients Report'
)

print(f"Report generated: {report.file.url}")
print(f"Records: {report.record_count}")
```

### Add a custom format strategy
```python
from reports.factory import ReportFactory
from reports.interfaces import IReportStrategy

class XMLReportStrategy(IReportStrategy):
    def generate(self, data, metadata):
        # XML generation logic
        pass

    def get_file_extension(self):
        return 'xml'

    def get_content_type(self):
        return 'application/xml'

# Register the new strategy
ReportFactory.register_strategy('xml', XMLReportStrategy)
```

## Testing

### Unit Tests
```bash
docker compose exec backend pytest reports/tests/test_strategies.py -v
docker compose exec backend pytest reports/tests/test_factory.py -v
docker compose exec backend pytest reports/tests/test_service.py -v
```

### Integration Tests
```bash
docker compose exec backend pytest reports/tests/test_api.py -v
```

## File Storage

Reports are stored in: `media/reports/YYYY/MM/DD/`

Example: `media/reports/2025/10/19/patients_20251019_153000.pdf`

## Performance Considerations

1. **Synchronous Generation**: Currently reports are generated synchronously. For large datasets, consider implementing:
   - Celery async tasks
   - Progress tracking
   - Background processing

2. **File Cleanup**: Implement periodic cleanup of old reports:
   - Create Celery Beat task
   - Delete reports older than X days
   - Configurable retention policy

3. **Caching**: Cache frequently generated reports with same parameters

## Security

- All endpoints require JWT authentication
- Users can only access their own reports
- File paths are validated to prevent directory traversal
- Input validation on all parameters

## Future Enhancements

1. **Async Generation**: Use Celery for background processing
2. **Email Delivery**: Email reports to users
3. **Scheduling**: Schedule recurring reports
4. **Custom Templates**: Allow custom report templates
5. **Charts/Graphs**: Add visualization support
6. **Excel Format**: Add XLSX output format
7. **Compression**: Compress large reports
8. **Batch Reports**: Generate multiple reports at once

## Dependencies

- `reportlab` - PDF generation
- `csv` (built-in) - CSV generation
- `json` (built-in) - JSON serialization
- Django file storage system

## Maintainers

- Backend Team
- For questions, contact: dev@healthcare.local
