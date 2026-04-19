#!/usr/bin/env python3
"""
Generate hierarchical ValueSet for ACR Library
"""

import json
import os
from datetime import datetime


def create_hierarchical_valueset():
    """Create a ValueSet that includes the entire hierarchical CodeSystem."""
    return {
        "resourceType": "ValueSet",
        "id": "phic-acr-hierarchical",
        "meta": {
            "versionId": "1",
            "lastUpdated": datetime.now().isoformat() + "Z"
        },
        "url": "http://www.philhealth.gov.ph/fhir/ValueSet/acr-hierarchical",
        "identifier": [{
            "system": "urn:ietf:rfc:3986",
            "value": "urn:oid:2.16.840.1.113883.3.8.2.20"
        }],
        "version": "2.3.0",
        "name": "PHICACRLibraryHierarchical",
        "title": "PhilHealth ACR Library - Hierarchical View",
        "status": "active",
        "experimental": False,
        "publisher": "Philippine Health Insurance Corporation",
        "contact": [{
            "telecom": [{
                "system": "url",
                "value": "https://www.philhealth.gov.ph"
            }]
        }],
        "description": "Hierarchical ValueSet for PhilHealth ACR Library. Ontology: ACR (Root) -> ICD/RVS (Categories) -> ACR Groups -> Codes. Use $expand with includeHierarchy=true or hierarchical=true to see nested structure.",
        "compose": {
            "include": [{
                "system": "http://www.philhealth.gov.ph/fhir/CodeSystem/acr-library",
                "version": "2.3.0-hierarchical"
            }]
        }
    }


def main():
    output_dir = "fsh-generated/resources"
    os.makedirs(output_dir, exist_ok=True)
    
    vs = create_hierarchical_valueset()
    filepath = os.path.join(output_dir, "ValueSet-phic-acr-hierarchical.json")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(vs, f, indent=2)
    
    print(f"✓ Created: {filepath}")
    print(f"  URL: {vs['url']}")
    print(f"  ID: {vs['id']}")


if __name__ == "__main__":
    main()
