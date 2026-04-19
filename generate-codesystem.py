#!/usr/bin/env python3
"""
ACR Library Hierarchical CodeSystem Generator

Creates a proper ontology with SNOMED CT-style hierarchy:

ACR (Root)
├── ICD (Category)
│   ├── CR0001 (ICD Group)
│   │   ├── P91.3 (ICD Code)
│   │   ├── P91.4 (ICD Code)
│   │   └── ...
│   ├── CR0002 (ICD Group)
│   │   └── J36 (ICD Code)
│   └── ...
└── RVS (Category)
    ├── CR0325 (RVS Group)
    │   └── 69020 (RVS Code)
    └── ...

Features:
- hierarchyMeaning: is-a
- Nested concept structures
- Handles 7 duplicate RVS codes by keeping first occurrence
- All financial properties preserved
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict


def connect_db(db_path: str) -> sqlite3.Connection:
    """Connect to SQLite database."""
    return sqlite3.connect(db_path)


def load_data(conn: sqlite3.Connection) -> tuple:
    """Load all data from database."""
    cursor = conn.cursor()
    
    # Load ACR Groups
    cursor.execute("SELECT ACR_GROUPID, DESCRIPTION, EFF_DATE FROM ACR_GROUPS")
    groups = {row[0]: {"code": row[0], "display": row[1], "effDate": row[2], 
                       "groupType": "PC" if row[0].startswith("PC") else "CR"} 
              for row in cursor.fetchall()}
    
    # Load ICD codes with hierarchy
    cursor.execute("""
        SELECT ICD_CODE, DESCRIPTION, CHAPTER_CODE, CHAPTER_NAME, 
               BLOCK_CODE, PARENT_CODE, IS_PHIC_COVERED
        FROM WHO_ICD_CODES
    """)
    icd_codes = {row[0]: {
        "code": row[0], "display": row[1], "chapterCode": row[2],
        "chapterName": row[3], "blockCode": row[4], "parentCode": row[5],
        "phicCovered": bool(row[6])
    } for row in cursor.fetchall()}
    
    # Load ICD assignments
    cursor.execute("SELECT ACR_GROUPID, ICDCODE, DESCRIPTION FROM ACR_GROUP_ICDS WHERE ACTIVE='T'")
    group_icds = defaultdict(list)
    for row in cursor.fetchall():
        group_icds[row[0]].append({"code": row[1], "description": row[2]})
    
    # Load RVS assignments
    cursor.execute("SELECT ACR_GROUPID, RVSCODE, DESCRIPTION, RVU FROM ACR_GROUP_RVS WHERE ACTIVE='T'")
    group_rvs = defaultdict(list)
    for row in cursor.fetchall():
        rvu = 0.0
        if row[3]:
            try:
                rvu = float(row[3])
            except:
                pass
        group_rvs[row[0]].append({"code": row[1], "description": row[2], "rvu": rvu})
    
    # Load ICD rules
    cursor.execute("""
        SELECT ACR_GROUPID, ICDCODE, MAX(EFF_DATE) as latest_date
        FROM ACR_PERICD_RULES WHERE ACTIVE='T' GROUP BY ACR_GROUPID, ICDCODE
    """)
    icd_rules = {}
    for row in cursor.fetchall():
        cursor.execute("SELECT * FROM ACR_PERICD_RULES WHERE ACR_GROUPID=? AND ICDCODE=? AND EFF_DATE=?",
                      (row[0], row[1], row[2]))
        rule_row = cursor.fetchone()
        if rule_row:
            columns = [desc[0] for desc in cursor.description]
            icd_rules[(row[0], row[1])] = dict(zip(columns, rule_row))
    
    # Load RVS rules
    cursor.execute("""
        SELECT ACR_GROUPID, RVSCODE, MAX(EFF_DATE) as latest_date
        FROM ACR_PERRVS_RULES WHERE ACTIVE='T' GROUP BY ACR_GROUPID, RVSCODE
    """)
    rvs_rules = {}
    for row in cursor.fetchall():
        cursor.execute("SELECT * FROM ACR_PERRVS_RULES WHERE ACR_GROUPID=? AND RVSCODE=? AND EFF_DATE=?",
                      (row[0], row[1], row[2]))
        rule_row = cursor.fetchone()
        if rule_row:
            columns = [desc[0] for desc in cursor.description]
            rvs_rules[(row[0], row[1])] = dict(zip(columns, rule_row))
    
    return groups, icd_codes, dict(group_icds), dict(group_rvs), icd_rules, rvs_rules


def format_decimal(value: Any) -> Optional[float]:
    """Safely format decimal value."""
    if value is None:
        return None
    try:
        return float(value)
    except:
        return None


def parse_boolean(value: Any) -> Optional[bool]:
    """Parse T/F string to boolean."""
    if value is None:
        return None
    if isinstance(value, str):
        return value.upper() == 'T'
    return bool(value)


def build_icd_code_concept(code: str, icd_info: Dict, rule: Optional[Dict]) -> Dict:
    """Build ICD code concept with all properties."""
    concept = {
        "code": code,
        "display": icd_info.get("display", ""),
        "property": [{"code": "codeType", "valueCode": "ICD"}]
    }
    
    # Add ICD hierarchy info
    for prop_code, key in [
        ("phicCovered", "phicCovered"),
        ("chapterCode", "chapterCode"),
        ("chapterName", "chapterName"),
        ("blockCode", "blockCode"),
        ("parentCode", "parentCode")
    ]:
        if icd_info.get(key):
            val_type = "valueBoolean" if key == "phicCovered" else "valueString"
            concept["property"].append({"code": prop_code, val_type: icd_info[key]})
    
    # Add financial rules
    if rule:
        for field, prop_name in [
            ("PRIMARY_AMOUNT", "primaryAmount"),
            ("PRIMARY_HOSP_SHARE", "primaryHospShare"),
            ("PRIMARY_PROF_SHARE", "primaryProfShare"),
            ("SECONDARY_AMOUNT", "secondaryAmount"),
            ("SECONDARY_HOSP_SHARE", "secondaryHospShare"),
            ("SECONDARY_PROF_SHARE", "secondaryProfShare"),
            ("PCF_AMOUNT", "pcfAmount"),
            ("PCF_HOSP_SHARE", "pcfHospShare"),
            ("PCF_PROF_SHARE", "pcfProfShare"),
        ]:
            value = format_decimal(rule.get(field))
            if value is not None:
                concept["property"].append({"code": prop_name, "valueDecimal": value})
        
        for field, prop_name in [
            ("CHECK_FACILITY_H1", "checkFacilityH1"),
            ("CHECK_FACILITY_H2", "checkFacilityH2"),
            ("CHECK_FACILITY_H3", "checkFacilityH3"),
            ("CHECK_FACILITY_ASC", "checkFacilityAsc"),
            ("CHECK_FACILITY_PCF", "checkFacilityPcf"),
            ("CHECK_FACILITY_MAT", "checkFacilityMat"),
            ("CHECK_FACILITY_FSDC", "checkFacilityFsdc"),
            ("CHECK_FACILITY_ABTC", "checkFacilityAbtc"),
            ("CHECK_FACILITY_OPMC", "checkFacilityOpmc"),
            ("CHECK_FACILITY_PCB", "checkFacilityPcb"),
            ("CHECK_FACILITY_RHU", "checkFacilityRhu"),
            ("CHECK_FACILITY_TBDOTSC", "checkFacilityTbdotsc"),
            ("CHECK_FACILITY_TSEKAP", "checkFacilityTsekap"),
            ("CHECK_FACILITY_DATRC", "checkFacilityDatrc"),
            ("CHECK_FACILITY_HIVTH", "checkFacilityHivth"),
            ("CHECK_FACILITY_FPC", "checkFacilityFpc"),
            ("CHECK_FACILITY_CIU", "checkFacilityCiu"),
            ("CHECK_FACILITY_DSP", "checkFacilityDsp"),
            ("CHECK_PCF_SECONDARY_CR", "checkPcfSecondaryCr"),
            ("CHECK_ASC_SECONDARY_CR", "checkAscSecondaryCr"),
        ]:
            value = parse_boolean(rule.get(field))
            if value is not None:
                concept["property"].append({"code": prop_name, "valueBoolean": value})
        
        if rule.get("EFF_DATE"):
            concept["property"].append({"code": "ruleEffDate", "valueString": rule["EFF_DATE"]})
        if rule.get("EFF_END_DATE"):
            concept["property"].append({"code": "ruleEndDate", "valueString": rule["EFF_END_DATE"]})
    
    return concept


def build_rvs_code_concept(code: str, rvs_info: Dict, rule: Optional[Dict]) -> Dict:
    """Build RVS code concept with all properties."""
    concept = {
        "code": code,
        "display": rvs_info.get("description", ""),
        "property": [{"code": "codeType", "valueCode": "RVS"}]
    }
    
    if rvs_info.get("rvu"):
        concept["property"].append({"code": "rvu", "valueDecimal": rvs_info["rvu"]})
    
    # Add financial rules
    if rule:
        for field, prop_name in [
            ("PRIMARY_AMOUNT", "primaryAmount"),
            ("PRIMARY_HOSP_SHARE", "primaryHospShare"),
            ("PRIMARY_PROF_SHARE", "primaryProfShare"),
            ("SECONDARY_AMOUNT", "secondaryAmount"),
            ("SECONDARY_HOSP_SHARE", "secondaryHospShare"),
            ("SECONDARY_PROF_SHARE", "secondaryProfShare"),
            ("PCF_AMOUNT", "pcfAmount"),
            ("PCF_HOSP_SHARE", "pcfHospShare"),
            ("PCF_PROF_SHARE", "pcfProfShare"),
        ]:
            value = format_decimal(rule.get(field))
            if value is not None:
                concept["property"].append({"code": prop_name, "valueDecimal": value})
        
        for field, prop_name in [
            ("CHECK_FACILITY_H1", "checkFacilityH1"),
            ("CHECK_FACILITY_H2", "checkFacilityH2"),
            ("CHECK_FACILITY_H3", "checkFacilityH3"),
            ("CHECK_FACILITY_ASC", "checkFacilityAsc"),
            ("CHECK_FACILITY_PCF", "checkFacilityPcf"),
            ("CHECK_FACILITY_MAT", "checkFacilityMat"),
            ("CHECK_FACILITY_FSDC", "checkFacilityFsdc"),
            ("CHECK_FACILITY_ABTC", "checkFacilityAbtc"),
            ("CHECK_FACILITY_OPMC", "checkFacilityOpmc"),
            ("CHECK_FACILITY_PCB", "checkFacilityPcb"),
            ("CHECK_FACILITY_RHU", "checkFacilityRhu"),
            ("CHECK_FACILITY_TBDOTSC", "checkFacilityTbdotsc"),
            ("CHECK_FACILITY_TSEKAP", "checkFacilityTsekap"),
            ("CHECK_FACILITY_DATRC", "checkFacilityDatrc"),
            ("CHECK_FACILITY_HIVTH", "checkFacilityHivth"),
            ("CHECK_FACILITY_FPC", "checkFacilityFpc"),
            ("CHECK_FACILITY_CIU", "checkFacilityCiu"),
            ("CHECK_FACILITY_DSP", "checkFacilityDsp"),
            ("CHECK_PCF_SECONDARY_CR", "checkPcfSecondaryCr"),
            ("CHECK_ASC_SECONDARY_CR", "checkAscSecondaryCr"),
        ]:
            value = parse_boolean(rule.get(field))
            if value is not None:
                concept["property"].append({"code": prop_name, "valueBoolean": value})
        
        if rule.get("EFF_DATE"):
            concept["property"].append({"code": "ruleEffDate", "valueString": rule["EFF_DATE"]})
        if rule.get("EFF_END_DATE"):
            concept["property"].append({"code": "ruleEndDate", "valueString": rule["EFF_END_DATE"]})
    
    return concept


def build_hierarchical_codesystem(db_path: str) -> Dict:
    """Build hierarchical CodeSystem with proper ontology."""
    print(f"Loading data from: {db_path}")
    conn = connect_db(db_path)
    groups, icd_codes, group_icds, group_rvs, icd_rules, rvs_rules = load_data(conn)
    conn.close()
    
    print(f"Loaded {len(groups)} groups, {len(icd_codes)} ICD codes")
    print(f"ICD assignments: {len(group_icds)} groups, RVS assignments: {len(group_rvs)} groups")
    
    # Track seen codes to handle duplicates
    seen_rvs_codes = set()
    duplicate_rvs_skipped = []
    
    # Build ICD branch
    print("\nBuilding ICD hierarchy...")
    icd_group_concepts = []
    icd_code_count = 0
    
    for group_id, group_info in groups.items():
        icd_assignments = group_icds.get(group_id, [])
        if not icd_assignments:
            continue
        
        # Build ICD codes as children
        icd_children = []
        for icd_assignment in icd_assignments:
            icd_code = icd_assignment["code"]
            icd_info = icd_codes.get(icd_code, {
                "code": icd_code, "display": icd_assignment["description"],
                "phicCovered": True
            })
            rule = icd_rules.get((group_id, icd_code))
            icd_concept = build_icd_code_concept(icd_code, icd_info, rule)
            icd_children.append(icd_concept)
            icd_code_count += 1
        
        # Create group concept with ICD children
        group_concept = {
            "code": group_id,
            "display": group_info["display"],
            "property": [
                {"code": "codeType", "valueCode": "GROUP"},
                {"code": "groupType", "valueCode": group_info["groupType"]}
            ]
        }
        if group_info.get("effDate"):
            group_concept["property"].append({"code": "effDate", "valueString": group_info["effDate"]})
        
        if icd_children:
            group_concept["concept"] = icd_children
        
        icd_group_concepts.append(group_concept)
    
    # Build RVS branch
    print("Building RVS hierarchy...")
    rvs_group_concepts = []
    rvs_code_count = 0
    
    for group_id, group_info in groups.items():
        rvs_assignments = group_rvs.get(group_id, [])
        if not rvs_assignments:
            continue
        
        # Build RVS codes as children
        rvs_children = []
        for rvs_assignment in rvs_assignments:
            rvs_code = rvs_assignment["code"]
            
            # Handle duplicates (7 codes appear in multiple groups)
            if rvs_code in seen_rvs_codes:
                duplicate_rvs_skipped.append(f"{rvs_code} in {group_id}")
                continue
            seen_rvs_codes.add(rvs_code)
            
            rule = rvs_rules.get((group_id, rvs_code))
            rvs_concept = build_rvs_code_concept(rvs_code, rvs_assignment, rule)
            rvs_children.append(rvs_concept)
            rvs_code_count += 1
        
        # Create group concept with RVS children
        group_concept = {
            "code": group_id,
            "display": group_info["display"],
            "property": [
                {"code": "codeType", "valueCode": "GROUP"},
                {"code": "groupType", "valueCode": group_info["groupType"]}
            ]
        }
        if group_info.get("effDate"):
            group_concept["property"].append({"code": "effDate", "valueString": group_info["effDate"]})
        
        if rvs_children:
            group_concept["concept"] = rvs_children
        
        rvs_group_concepts.append(group_concept)
    
    print(f"\nICD branch: {len(icd_group_concepts)} groups with {icd_code_count} codes")
    print(f"RVS branch: {len(rvs_group_concepts)} groups with {rvs_code_count} codes")
    if duplicate_rvs_skipped:
        print(f"Skipped {len(duplicate_rvs_skipped)} duplicate RVS occurrences")
    
    # Create ICD category concept
    icd_category = {
        "code": "ICD",
        "display": "ICD-10 Diagnosis Codes",
        "definition": "International Classification of Diseases, 10th Revision diagnosis codes in PhilHealth ACR Library",
        "property": [{"code": "codeType", "valueCode": "CATEGORY"}],
        "concept": icd_group_concepts
    }
    
    # Create RVS category concept
    rvs_category = {
        "code": "RVS",
        "display": "RVS Procedure Codes",
        "definition": "Relative Value Scale procedure codes in PhilHealth ACR Library",
        "property": [{"code": "codeType", "valueCode": "CATEGORY"}],
        "concept": rvs_group_concepts
    }
    
    # Create root ACR concept
    root_concept = {
        "code": "ACR",
        "display": "PhilHealth All Case Rate (ACR) Library",
        "definition": "Comprehensive case rate library containing ICD-10 diagnosis codes and RVS procedure codes with financial rules",
        "property": [{"code": "codeType", "valueCode": "ROOT"}],
        "concept": [icd_category, rvs_category]
    }
    
    # Calculate total concepts
    total_groups = len(icd_group_concepts) + len(rvs_group_concepts)
    total_codes = icd_code_count + rvs_code_count
    total_concepts = 1 + 2 + total_groups + total_codes  # Root + 2 categories + groups + codes
    
    print(f"\nHierarchy complete:")
    print(f"  Root: 1 (ACR)")
    print(f"  Categories: 2 (ICD, RVS)")
    print(f"  Groups: {total_groups}")
    print(f"  Codes: {total_codes}")
    print(f"  TOTAL: {total_concepts}")
    
    # Build CodeSystem
    codesystem = {
        "resourceType": "CodeSystem",
        "id": "UnofficialACR",
        "meta": {
            "versionId": "2",
            "lastUpdated": datetime.now().isoformat() + "Z"
        },
        "url": "http://www.philhealth.gov.ph/fhir/CodeSystem/acr-library",
        "identifier": [{
            "system": "urn:ietf:rfc:3986",
            "value": "urn:oid:2.16.840.1.113883.3.8.2.1"
        }],
        "version": "2.3.0-hierarchical",
        "name": "PHICACRLibrary",
        "title": "PhilHealth All Case Rate (ACR) Library - Hierarchical",
        "status": "active",
        "experimental": False,
        "publisher": "Philippine Health Insurance Corporation",
        "contact": [{
            "telecom": [{
                "system": "url",
                "value": "https://www.philhealth.gov.ph"
            }]
        }],
        "description": f"Hierarchical code system for PhilHealth ACR Library v2.3. Ontology: ACR (Root) -> ICD/RVS (Categories) -> Groups -> Codes. Contains {total_groups} ACR groups, {icd_code_count} ICD-10 codes, {rvs_code_count} RVS codes with full financial rules.",
        "hierarchyMeaning": "is-a",
        "content": "complete",
        "property": [
            {"code": "codeType", "type": "code", "description": "Concept type: ROOT, CATEGORY, GROUP, ICD, RVS"},
            {"code": "groupType", "type": "code", "description": "ACR Group type: CR (Case Rate) or PC (Primary Care)"},
            {"code": "phicCovered", "type": "boolean", "description": "PHIC coverage status"},
            {"code": "chapterCode", "type": "string", "description": "ICD-10 chapter code"},
            {"code": "chapterName", "type": "string", "description": "ICD-10 chapter name"},
            {"code": "blockCode", "type": "string", "description": "ICD-10 block code range"},
            {"code": "parentCode", "type": "string", "description": "Parent code in ICD-10 hierarchy"},
            {"code": "rvu", "type": "decimal", "description": "Relative Value Units"},
            {"code": "primaryAmount", "type": "decimal", "description": "Primary care payment amount"},
            {"code": "primaryHospShare", "type": "decimal", "description": "Hospital share (primary)"},
            {"code": "primaryProfShare", "type": "decimal", "description": "Professional share (primary)"},
            {"code": "secondaryAmount", "type": "decimal", "description": "Secondary care payment amount"},
            {"code": "pcfAmount", "type": "decimal", "description": "PCF payment amount"},
            {"code": "checkFacilityH1", "type": "boolean", "description": "H1 eligibility"},
            {"code": "checkFacilityH2", "type": "boolean", "description": "H2 eligibility"},
            {"code": "checkFacilityH3", "type": "boolean", "description": "H3 eligibility"},
            {"code": "checkFacilityAsc", "type": "boolean", "description": "ASC eligibility"},
            {"code": "checkFacilityPcf", "type": "boolean", "description": "PCF eligibility"},
            {"code": "ruleEffDate", "type": "string", "description": "Rule effective date"},
        ],
        "concept": [root_concept]
    }
    
    return codesystem, duplicate_rvs_skipped


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate hierarchical ACR CodeSystem")
    parser.add_argument("--db", default="scripts/CodeSystem/acrLibraryVersion2.3-custom.db")
    parser.add_argument("--output", default="fsh-generated/resources/CodeSystem-phic-acr-hierarchical.json")
    args = parser.parse_args()
    
    print("=" * 60)
    print("ACR HIERARCHICAL CODESYSTEM GENERATOR")
    print("=" * 60)
    print()
    
    codesystem, duplicates = build_hierarchical_codesystem(args.db)
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(codesystem, f, indent=2, ensure_ascii=False)
    
    file_size_mb = os.path.getsize(args.output) / (1024 * 1024)
    
    print(f"\n{'=' * 60}")
    print("HIERARCHICAL CODESYSTEM CREATED")
    print(f"{'=' * 60}")
    print(f"Output: {args.output}")
    print(f"Size: {file_size_mb:.1f} MB")
    print(f"Version: {codesystem['version']}")
    print(f"Hierarchy: ACR -> ICD/RVS -> Groups -> Codes")
    print(f"Total concepts: {codesystem['description'].split('Contains')[1].split('with')[0].strip() if 'Contains' in codesystem['description'] else 'See summary above'}")
    
    if duplicates:
        print(f"\nNote: Skipped {len(duplicates)} duplicate RVS code occurrences")
        for dup in duplicates[:5]:
            print(f"  - {dup}")
    
    print(f"\nReady for upload to: https://tx.fhirlab.net/fhir/CodeSystem/UnofficialACR")


if __name__ == "__main__":
    main()
