#!/usr/bin/env python3
"""
Generate ICD and RVS hierarchical ValueSets for ACR Library
"""

import json
import os
from datetime import datetime


def create_icd_valueset():
    """Create ValueSet for ICD hierarchical branch only."""
    return {
        "resourceType": "ValueSet",
        "id": "phic-acr-icd-hierarchical",
        "meta": {
            "versionId": "1",
            "lastUpdated": datetime.now().isoformat() + "Z"
        },
        "url": "http://www.philhealth.gov.ph/fhir/ValueSet/acr-icd-hierarchical",
        "identifier": [{
            "system": "urn:ietf:rfc:3986",
            "value": "urn:oid:2.16.840.1.113883.3.8.2.30"
        }],
        "version": "2.3.0",
        "name": "PHICACRICDHierarchical",
        "title": "PhilHealth ACR Library - ICD-10 Hierarchical",
        "status": "active",
        "experimental": False,
        "publisher": "Philippine Health Insurance Corporation",
        "contact": [{
            "telecom": [{
                "system": "url",
                "value": "https://www.philhealth.gov.ph"
            }]
        }],
        "description": "Hierarchical ValueSet for ICD-10 diagnosis codes from PhilHealth ACR Library. Structure: ICD (Category) -> ACR Groups -> ICD Codes. Contains 342 groups with 4,705 ICD-10 codes.",
        "compose": {
            "include": [{
                "system": "http://www.philhealth.gov.ph/fhir/CodeSystem/acr-library",
                "version": "2.3.0-hierarchical",
                "filter": [{
                    "property": "codeType",
                    "op": "in",
                    "value": "CATEGORY,GROUP,ICD"
                }]
            }]
        }
    }


def create_rvs_valueset():
    """Create ValueSet for RVS hierarchical branch only."""
    return {
        "resourceType": "ValueSet",
        "id": "phic-acr-rvs-hierarchical",
        "meta": {
            "versionId": "1",
            "lastUpdated": datetime.now().isoformat() + "Z"
        },
        "url": "http://www.philhealth.gov.ph/fhir/ValueSet/acr-rvs-hierarchical",
        "identifier": [{
            "system": "urn:ietf:rfc:3986",
            "value": "urn:oid:2.16.840.1.113883.3.8.2.31"
        }],
        "version": "2.3.0",
        "name": "PHICACRRVSHierarchical",
        "title": "PhilHealth ACR Library - RVS Hierarchical",
        "status": "active",
        "experimental": False,
        "publisher": "Philippine Health Insurance Corporation",
        "contact": [{
            "telecom": [{
                "system": "url",
                "value": "https://www.philhealth.gov.ph"
            }]
        }],
        "description": "Hierarchical ValueSet for RVS procedure codes from PhilHealth ACR Library. Structure: RVS (Category) -> ACR Groups -> RVS Codes. Contains 4,471 groups with 4,512 RVS codes.",
        "compose": {
            "include": [{
                "system": "http://www.philhealth.gov.ph/fhir/CodeSystem/acr-library",
                "version": "2.3.0-hierarchical",
                "filter": [{
                    "property": "codeType",
                    "op": "in",
                    "value": "CATEGORY,GROUP,RVS"
                }]
            }]
        }
    }


def main():
    output_dir = "fsh-generated/resources"
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("GENERATING ICD AND RVS HIERARCHICAL VALUESETS")
    print("=" * 60)
    print()
    
    # Create ICD ValueSet
    vs_icd = create_icd_valueset()
    filepath_icd = os.path.join(output_dir, "ValueSet-phic-acr-icd-hierarchical.json")
    with open(filepath_icd, 'w', encoding='utf-8') as f:
        json.dump(vs_icd, f, indent=2)
    print(f"✓ Created: {os.path.basename(filepath_icd)}")
    print(f"  URL: {vs_icd['url']}")
    print(f"  Contents: ICD Category + 342 Groups + 4,705 ICD codes")
    print()
    
    # Create RVS ValueSet
    vs_rvs = create_rvs_valueset()
    filepath_rvs = os.path.join(output_dir, "ValueSet-phic-acr-rvs-hierarchical.json")
    with open(filepath_rvs, 'w', encoding='utf-8') as f:
        json.dump(vs_rvs, f, indent=2)
    print(f"✓ Created: {os.path.basename(filepath_rvs)}")
    print(f"  URL: {vs_rvs['url']}")
    print(f"  Contents: RVS Category + 4,471 Groups + 4,512 RVS codes")
    print()
    
    print("=" * 60)
    print("2 HIERARCHICAL VALUESETS CREATED")
    print("=" * 60)
    print("\nNext: Upload to terminology server")


if __name__ == "__main__":
    main()
