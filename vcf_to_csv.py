#!/usr/bin/env python3

import argparse
import csv
import re
import sys
import vobject

def clean_phone_number(number):
    if not number:
        return ""
    # keep digits and a leading plus sign for international numbers
    cleaned = re.sub(r'[^\d+]', '', str(number))
    return cleaned

def convert_vcf_to_csv(vcf_path, csv_path):
    
    #
    # Note the creation of this function used the help of AI. I have reviewed and tested the code.
    #
    
    contacts_processed = 0
    numbers_exported = 0
    
    try:
        with open(vcf_path, 'r', encoding='utf-8') as vcf_file:
            with open(csv_path, 'w', newline='', encoding='utf-8') as csv_file:
                csv_writer = csv.writer(csv_file)
                
                # Write the header for the CSV file
                csv_writer.writerow(['Name', 'Number'])
                
                # vobject.readComponents is a generator that yields one vCard at a time
                for vcard in vobject.readComponents(vcf_file):
                    contacts_processed += 1
                    
                    # Use the Formatted Name (FN) if available, it's the most reliable
                    name = getattr(vcard, 'fn', None)
                    name = name.value.strip() if name else "Unknown Contact"
                    
                    # Check if the contact has any phone numbers
                    if not hasattr(vcard, 'tel_list'):
                        print(f"Warning: Contact '{name}' has no phone number. Skipping.")
                        continue
                        
                    # A contact can have multiple phone numbers.
                    # We create a separate row for each one.
                    for tel in vcard.tel_list:
                        original_number = tel.value
                        cleaned_number = clean_phone_number(original_number)
                        
                        if cleaned_number:
                            csv_writer.writerow([name, cleaned_number])
                            numbers_exported += 1
                        else:
                            print(f"Warning: Could not clean number '{original_number}' for contact '{name}'. Skipping.")

    except FileNotFoundError:
        print(f"Error: The file '{vcf_path}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

    print(f"\nConversion complete!")
    print(f"Processed {contacts_processed} contacts from '{vcf_path}'.")
    print(f"Exported {numbers_exported} phone numbers to '{csv_path}'.")


def main():
    parser = argparse.ArgumentParser(
        description="Convert a VCF contact file to a simple CSV.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "vcf_file", 
        help="The path to the input VCF file."
    )
    
    parser.add_argument(
        "-o", "--output", 
        default="contacts_mmcli.csv",
        help="The path for the output CSV file.\n(default: contacts_mmcli.csv)"
    )
    
    args = parser.parse_args()
    
    # Check for the vobject library
    try:
        import vobject
    except ImportError:
        print("Error: The 'vobject' library is required to run this script.")
        print("Please install it using: pip install vobject")
        sys.exit(1)
        
    convert_vcf_to_csv(args.vcf_file, args.output)


if __name__ == "__main__":
    main()