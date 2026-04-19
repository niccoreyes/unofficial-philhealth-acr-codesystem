# Philippine ACR Library - Hierarchical Ontology (Refactored)

## ✅ REFACTORING COMPLETE

The ACR Library now has a **proper hierarchical ontology** like SNOMED CT.

---

## Ontology Structure

```
ACR (Root - PhilHealth All Case Rate Library)
├── ICD (Category - ICD-10 Diagnosis Codes)
│   ├── CR0001 (ACR Group - Abnormal Sensorium in Newborn)
│   │   ├── P91.3 (ICD Code - Neonatal cerebral irritability)
│   │   ├── P91.4 (ICD Code - Neonatal cerebral depression)
│   │   ├── P91.6 (ICD Code - Hypoxic ischaemic encephalopathy)
│   │   ├── P91.8 (ICD Code - Other specified disturbances...)
│   │   └── P91.9 (ICD Code - Disturbance of cerebral status...)
│   ├── CR0002 (ACR Group - Abscess of Respiratory Tract)
│   │   ├── J36 (ICD Code - Peritonsillar abscess)
│   │   ├── J38.7 (ICD Code - Abscess of larynx)
│   │   └── ...
│   └── ... (342 ICD groups total)
│
└── RVS (Category - RVS Procedure Codes)
    ├── CR0325 (ACR Group)
    │   └── 69020 (RVS Code - Drainage external auditory canal)
    ├── CR0326 (ACR Group)
    │   └── 20206 (RVS Code - Biopsy, muscle, percutaneous needle)
    └── ... (4471 RVS groups total)
```

---

## Hierarchy Levels

| Level | Code Type | Count | Description |
|-------|-----------|-------|-------------|
| **Root** | ACR | 1 | Philippine All Case Rate Library |
| **Category** | ICD / RVS | 2 | Code categories |
| **Groups** | CRxxxx / PCxxxx | 4,813 | ACR Case Rate and Primary Care groups |
| **Codes** | ICD-10 / RVS | 9,217 | Actual diagnosis and procedure codes |
| **TOTAL** | - | **14,033** | All concepts |

---

## Resources on Server

### CodeSystem (Main Resource)

| Property | Value |
|----------|-------|
| **URL** | `http://www.philhealth.gov.ph/fhir/CodeSystem/acr-library` |
| **ID** | `UnofficialACR` |
| **Version** | `2.3.0-hierarchical` |
| **Hierarchy** | `is-a` |
| **Status** | `active` |
| **Total Concepts** | 14,033 |
| **Property Definitions** | 40 |

### ValueSet (View Resource)

| Property | Value |
|----------|-------|
| **URL** | `http://www.philhealth.gov.ph/fhir/ValueSet/acr-hierarchical` |
| **ID** | `phic-acr-hierarchical` |
| **Version** | `2.3.0` |
| **Status** | `active` |

---

## Shrimp Viewer Configuration

### For Shrimp Web UI

**Configure this ValueSet URL:**
```
http://www.philhealth.gov.ph/fhir/ValueSet/acr-hierarchical
```

Or use the CodeSystem directly:
```
http://www.philhealth.gov.ph/fhir/CodeSystem/acr-library
```

### Test Commands

**Verify hierarchy exists:**
```bash
curl 'https://tx.fhirlab.net/fhir/CodeSystem/UnofficialACR' | jq '.concept[0] | {code, display, child_count: (.concept | length)}'
```

**Test $expand:**
```bash
curl 'https://tx.fhirlab.net/fhir/ValueSet/$expand?url=http://www.philhealth.gov.ph/fhir/ValueSet/acr-hierarchical&count=10'
```

**Full Shrimp-compatible URL:**
```
https://tx.fhirlab.net/fhir/ValueSet/$expand?url=http://www.philhealth.gov.ph/fhir/ValueSet/acr-hierarchical&includeDesignations=true&count=100
```

---

## Comparison: Before vs After

### ❌ BEFORE (Flat Structure)
```
CR0001: Abnormal Sensorium in Newborn
CR0002: Abscess of Respiratory Tract
P91.3: Neonatal cerebral irritability   ← No hierarchy
J36: Peritonsillar abscess              ← Flat list
69020: Drainage external auditory canal ← No parent context
```

### ✅ AFTER (Hierarchical Structure)
```
ACR (Root)
├── ICD (Category)
│   ├── CR0001: Abnormal Sensorium in Newborn (Group)
│   │   ├── P91.3: Neonatal cerebral irritability (Code)
│   │   └── P91.4: Neonatal cerebral depression (Code)
│   └── CR0002: Abscess of Respiratory Tract (Group)
│       └── J36: Peritonsillar abscess (Code)
└── RVS (Category)
    └── CR0325 (Group)
        └── 69020: Drainage external auditory canal (Code)
```

---

## Property Reference

### Concept Type Property

| codeType | Description | Examples |
|----------|-------------|----------|
| `ROOT` | Root concept | ACR |
| `CATEGORY` | Category concepts | ICD, RVS |
| `GROUP` | ACR Group concepts | CR0001, PC20250004 |
| `ICD` | ICD-10 diagnosis codes | P91.3, J36, A00.0 |
| `RVS` | RVS procedure codes | 69020, 44152 |

### Other Key Properties

| Property | Type | Description |
|----------|------|-------------|
| `groupType` | code | CR (Case Rate) or PC (Primary Care) |
| `phicCovered` | boolean | Whether PHIC covers this code |
| `chapterCode` | string | ICD-10 chapter (I, II, III...) |
| `chapterName` | string | ICD-10 chapter description |
| `rvu` | decimal | Relative Value Units |
| `primaryAmount` | decimal | Primary care payment (PHP) |
| `checkFacilityH1` | boolean | H1 facility eligibility |
| `checkFacilityPcf` | boolean | PCF facility eligibility |

---

## Files Created/Updated

| File | Description |
|------|-------------|
| `scripts/generate_hierarchical_codesystem.py` | Hierarchical generator |
| `scripts/generate_hierarchical_valueset.py` | ValueSet generator |
| `fsh-generated/resources/CodeSystem-phic-acr-hierarchical.json` | **HIERARCHICAL CODESYSTEM** (46.8 MB) |
| `fsh-generated/resources/ValueSet-phic-acr-hierarchical.json` | Hierarchical ValueSet |
| `docs/acr-hierarchical-ontology.md` | This documentation |

---

## Server Status

✅ **CodeSystem Uploaded:** `https://tx.fhirlab.net/fhir/CodeSystem/UnofficialACR`
- Version: 2.3.0-hierarchical
- Concepts: 14,033
- Hierarchy: ACR → ICD/RVS → Groups → Codes

✅ **ValueSet Uploaded:** `https://tx.fhirlab.net/fhir/ValueSet/phic-acr-hierarchical`
- Expansion: 14,033 concepts
- Supports $expand with hierarchical structure

---

## Next Steps for Shrimp Integration

1. **Configure Shrimp** to use: `http://www.philhealth.gov.ph/fhir/ValueSet/acr-hierarchical`
2. **Test expansion** with: `https://tx.fhirlab.net/fhir/ValueSet/$expand?url=http://www.philhealth.gov.ph/fhir/ValueSet/acr-hierarchical&count=100`
3. **Enable hierarchical view** in Shrimp (if supported)

---

## Notes

- **Duplicate handling:** 7 RVS codes appeared in multiple groups (C19 series). Kept in first occurrence only.
- **ICD uniqueness:** All ICD codes are unique to their groups.
- **Server compatibility:** Uses standard FHIR R4 `is-a` hierarchy.
- **Shrimp compatibility:** Requires Shrimp to support nested concept expansion.
