# PhilHealth ACR FHIR CodeSystem

**Community FHIR R4 Implementation of PhilHealth All Case Rate (ACR) Library v2.3**

[![Status](https://img.shields.io/badge/status-active-green)]()
[![FHIR Version](https://img.shields.io/badge/FHIR-R4-orange)]()
[![Server](https://img.shields.io/badge/server-ontoserver-blue)]()
[![Community](https://img.shields.io/badge/Community%20Implementation-blue)]()

## 📋 Overview

This repository contains a **hierarchical FHIR CodeSystem** and **ValueSets** for the Philippine Health Insurance Corporation (PhilHealth) All Case Rate (ACR) Library Version 2.3.

### What is ACR Library?

The ACR Library is PhilHealth's comprehensive case rate system containing:
- **ICD-10 diagnosis codes** with corresponding case rates
- **RVS (Relative Value Scale) procedure codes** with payment amounts
- **Financial rules** including hospital/professional shares
- **Facility eligibility** flags (H1, H2, H3, ASC, PCF, etc.)

---

## ⚠️ Disclaimer

**This is a community implementation, not an official PhilHealth product.**

This repository was created by **Thomas Reyes** as an open-source community project to provide FHIR R4 interoperability for the PhilHealth ACR Library. 

- **Data Source:** Philippine Health Insurance Corporation (PhilHealth)
- **Implementation:** Community-driven by Thomas Reyes
- **Status:** Unofficial - not endorsed or maintained by PhilHealth
- **Purpose:** To enable healthcare interoperability through FHIR standards

If you need official PhilHealth FHIR resources, please contact PhilHealth directly.

### FHIR Implementation

| Resource | URL | Concepts |
|----------|-----|----------|
| **CodeSystem** | `http://www.philhealth.gov.ph/fhir/CodeSystem/acr-library` | 14,033 |
| **Complete ValueSet** | `http://www.philhealth.gov.ph/fhir/ValueSet/acr-hierarchical` | 14,033 |
| **ICD ValueSet** | `http://www.philhealth.gov.ph/fhir/ValueSet/acr-icd-hierarchical` | 9,520 |
| **RVS ValueSet** | `http://www.philhealth.gov.ph/fhir/ValueSet/acr-rvs-hierarchical` | 9,327 |

**Live Server:** `https://tx.fhirlab.net/fhir`

---

## 🗂️ Repository Structure

```
UnofficialACRCodeSystem/
├── .gitignore                          # Git ignore rules (excludes .db file)
├── README.md                           # This file
├── acr-library-v2.3-source.db        # ⚠️ Source database (10 MB, gitignored)
│
├── generate-codesystem.py              # Creates hierarchical CodeSystem
├── generate-valueset-complete.py         # Creates complete ValueSet
├── generate-valueset-branches.py        # Creates ICD/RVS branch ValueSets
│
├── output/                             # Generated FHIR resources
│   ├── CodeSystem-acr-hierarchical.json     # 46.8 MB - Main CodeSystem
│   ├── ValueSet-acr-complete.json         # ICD + RVS combined
│   ├── ValueSet-acr-icd.json            # ICD diagnosis codes only
│   └── ValueSet-acr-rvs.json            # RVS procedure codes only
│
└── ONTOLOGY.md                         # Detailed ontology documentation
```

### File Descriptions

| File | Purpose | When to Use |
|------|---------|-------------|
| `generate-codesystem.py` | Reads SQLite DB and creates hierarchical CodeSystem JSON | When source data changes |
| `generate-valueset-complete.py` | Creates ValueSet referencing the complete CodeSystem | When CodeSystem is updated |
| `generate-valueset-branches.py` | Creates ICD-only and RVS-only ValueSets | When CodeSystem is updated |
| `acr-library-v2.3-source.db` | **Source data** from PhilHealth (proprietary) | Keep private, don't commit |
| `CodeSystem-acr-hierarchical.json` | **Main output** - Hierarchical FHIR CodeSystem | Upload to terminology server |
| `ValueSet-acr-complete.json` | Complete view with all codes | Use in Shrimp/validation |
| `ValueSet-acr-icd.json` | ICD diagnosis codes only | Use when only ICD needed |
| `ValueSet-acr-rvs.json` | RVS procedure codes only | Use when only RVS needed |

---

## 🏗️ Ontology Structure

The CodeSystem uses a **4-level hierarchy** with `hierarchyMeaning: is-a`:

```
ACR (Root)
│   "PhilHealth All Case Rate (ACR) Library"
│
├── ICD (Category)
│   │   "ICD-10 Diagnosis Codes"
│   │
│   ├── CR0001 (ACR Group)
│   │   │   "ABNORMAL SENSORIUM IN THE NEWBORN"
│   │   │
│   │   ├── P91.3 (ICD Code)
│   │   │   "Neonatal cerebral irritability"
│   │   │   [properties: primaryAmount, checkFacilityH1, etc.]
│   │   │
│   │   ├── P91.4 (ICD Code)
│   │   │   "Neonatal cerebral depression"
│   │   │
│   │   └── ... (3 more ICD codes)
│   │
│   ├── CR0002 (ACR Group)
│   │   │   "ABSCESS OF RESPIRATORY TRACT"
│   │   │
│   │   ├── J36 (ICD Code)
│   │   │   "Peritonsillar abscess"
│   │   │
│   │   └── ... (9 more ICD codes)
│   │
│   └── ... (340 more ICD groups)
│
└── RVS (Category)
    │   "RVS Procedure Codes"
    │
    ├── CR0325 (ACR Group)
    │   └── 69020 (RVS Code)
    │       "DRAINAGE EXTERNAL AUDITORY CANAL, ABSCESS"
    │
    └── ... (4,470 more RVS groups)
```

### Concept Types

| codeType | Level | Count | Description |
|----------|-------|-------|-------------|
| `ROOT` | 1 | 1 | ACR (top-level container) |
| `CATEGORY` | 2 | 2 | ICD and RVS categories |
| `GROUP` | 3 | 4,813 | ACR Case Rate groups (CRxxxx, PCxxxx) |
| `ICD` | 4 | 4,705 | ICD-10 diagnosis codes |
| `RVS` | 4 | 4,512 | RVS procedure codes |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.7+** (uses only standard library)
- **Source database** (`acr-library-v2.3-source.db` - not included in git)

### Regenerate FHIR Resources

```bash
# 1. Generate hierarchical CodeSystem (takes ~60 seconds)
python3 generate-codesystem.py

# 2. Generate ValueSets
python3 generate-valueset-complete.py
python3 generate-valueset-branches.py

# 3. Output files will be in ./output/
ls -lh output/
```

### Upload to Terminology Server

```bash
# Upload CodeSystem
curl -X PUT https://tx.fhirlab.net/fhir/CodeSystem/UnofficialACR \
  -H "Content-Type: application/fhir+json" \
  -d @output/CodeSystem-acr-hierarchical.json

# Upload ValueSets
curl -X PUT https://tx.fhirlab.net/fhir/ValueSet/phic-acr-hierarchical \
  -H "Content-Type: application/fhir+json" \
  -d @output/ValueSet-acr-complete.json

curl -X PUT https://tx.fhirlab.net/fhir/ValueSet/phic-acr-icd-hierarchical \
  -H "Content-Type: application/fhir+json" \
  -d @output/ValueSet-acr-icd.json

curl -X PUT https://tx.fhirlab.net/fhir/ValueSet/phic-acr-rvs-hierarchical \
  -H "Content-Type: application/fhir+json" \
  -d @output/ValueSet-acr-rvs.json
```

---

## 🌐 Server Configuration

### Terminology Server Details

| Property | Value |
|----------|-------|
| **Base URL** | `https://tx.fhirlab.net/fhir` |
| **Type** | Ontoserver / HAPI FHIR |
| **FHIR Version** | R4 (4.0.1) |
| **CodeSystem ID** | `UnofficialACR` |
| **CodeSystem Version** | `2.3.0-hierarchical` |

### Verify Upload

```bash
# Check CodeSystem
curl https://tx.fhirlab.net/fhir/CodeSystem/UnofficialACR

# Check ValueSet expansion
curl "https://tx.fhirlab.net/fhir/ValueSet/\$expand?url=http://www.philhealth.gov.ph/fhir/ValueSet/acr-hierarchical&count=5"
```

---

## 🦐 Shrimp Viewer Configuration

### Option 1: Complete Hierarchical View

**ValueSet URL:**
```
http://www.philhealth.gov.ph/fhir/ValueSet/acr-hierarchical
```

**Full Expansion URL:**
```
https://tx.fhirlab.net/fhir/ValueSet/$expand?url=http://www.philhealth.gov.ph/fhir/ValueSet/acr-hierarchical&includeDesignations=true&count=100
```

**Shows:** ACR Root → ICD/RVS Categories → All Groups → All Codes

### Option 2: ICD Diagnosis Codes Only

**ValueSet URL:**
```
http://www.philhealth.gov.ph/fhir/ValueSet/acr-icd-hierarchical
```

**Shows:** ICD Category → Groups with ICD codes only

### Option 3: RVS Procedure Codes Only

**ValueSet URL:**
```
http://www.philhealth.gov.ph/fhir/ValueSet/acr-rvs-hierarchical
```

**Shows:** RVS Category → Groups with RVS codes only

### Shrimp Settings

| Setting | Recommended Value |
|---------|-------------------|
| Terminology Server | `https://tx.fhirlab.net/fhir` |
| ValueSet URL | `http://www.philhealth.gov.ph/fhir/ValueSet/acr-hierarchical` |
| Version | `2.3.0` |
| Include Designations | ✅ Yes |
| Page Size | `100` |

---

## 📊 Statistics

| Metric | Count |
|--------|-------|
| **Total Concepts** | 14,033 |
| ACR Groups | 4,813 |
| ICD-10 Codes | 4,705 |
| RVS Codes | 4,512 |
| Property Definitions | 40 |
| CodeSystem File Size | 46.8 MB |

---

## 📚 Documentation

- **ONTOLOGY.md** - Detailed ontology structure and hierarchy explanation
- **CodeSystem URL:** `http://www.philhealth.gov.ph/fhir/CodeSystem/acr-library`
- **OID:** `urn:oid:2.16.840.1.113883.3.8.2.1`

---

## ⚠️ Important Notes

### Source Database

- The file `acr-library-v2.3-source.db` is **NOT included in git** (see `.gitignore`)
- This contains proprietary PhilHealth data
- Obtain the database separately and place it in the project root
- **Never commit** the `.db` file to version control

### Regenerating Resources

When the source database is updated:
1. Replace `acr-library-v2.3-source.db`
2. Run the 3 Python scripts
3. Upload new JSON files to server
4. Update version number if needed

### Duplicate Handling

- 7 RVS codes appear in multiple groups (C19 series COVID codes)
- These are kept in their first occurrence only
- All ICD codes are unique to their groups

---

## 🔧 Technical Details

### Dependencies

**None!** The Python scripts use only the standard library:
- `sqlite3` - Database access
- `json` - JSON handling
- `datetime` - Timestamps
- `os` - File operations

### Property Types

The CodeSystem defines 40 properties including:
- `codeType` (code): ROOT, CATEGORY, GROUP, ICD, RVS
- `groupType` (code): CR (Case Rate) or PC (Primary Care)
- `phicCovered` (boolean): PHIC coverage status
- `chapterCode` (string): ICD-10 chapter
- `primaryAmount` (decimal): Payment amount
- `checkFacilityH1` (boolean): Facility eligibility flags
- And more...

---

## 📞 Attribution

- **Data Source:** Philippine Health Insurance Corporation (PhilHealth)
- **ACR Library Version:** 2.3
- **Original Publisher:** Philippine Health Insurance Corporation
- **Community Implementation:** Thomas Reyes
- **FHIR Format:** R4
- **Purpose:** Interoperability and terminology services

**Note:** This is a community-driven implementation. The original ACR Library data is owned by PhilHealth. The FHIR structure and implementation are provided by the community for interoperability purposes.

---

## 📝 License

The FHIR resources in `output/` are provided for **interoperability purposes**.

- **Original Data:** © Philippine Health Insurance Corporation (ACR Library v2.3)
- **Community Implementation:** © Thomas Reyes - Community Implementation
- **FHIR Structure:** HL7 FHIR Standard (CC0)
- **Purpose:** For healthcare information exchange

**Important:** This is a community implementation and is **not officially endorsed by PhilHealth**. Use at your own discretion. For official PhilHealth FHIR resources, please contact PhilHealth directly.

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.3.0-hierarchical | 2026-04-19 | Initial hierarchical implementation |

---

**Questions or issues?** [Open an issue on GitHub](https://github.com/niccoreyes/philippine-acr-fhir-codesystem/issues) - Community maintained by Thomas Reyes.

For official PhilHealth inquiries, please contact [PhilHealth](https://www.philhealth.gov.ph) directly.
