#!/usr/bin/env python3
"""
AI Lead Qualification Automation System
Main entry point for the workflow: New Lead → AI Analysis → Lead Scoring → Store Results
"""
import argparse
import sys
from typing import List, Dict, Any
from datetime import datetime
from tqdm import tqdm

from lead_analyzer import analyze_lead
from storage import (
    load_leads_from_csv,
    save_to_csv,
    save_to_google_sheets,
    format_result_for_storage
)
import config


def print_banner():
    """Print application banner"""
    print("\n" + "=" * 60)
    print("   AI Lead Qualification Automation System")
    print("=" * 60 + "\n")


def print_summary(results: List[Dict[str, Any]]):
    """Print summary of processed leads"""
    total = len(results)
    high_priority = sum(1 for r in results if r['Priority'] == 'High')
    medium_priority = sum(1 for r in results if r['Priority'] == 'Medium')
    low_priority = sum(1 for r in results if r['Priority'] == 'Low')

    avg_score = sum(r['Lead Score'] for r in results) / total if total > 0 else 0

    print("\n" + "-" * 40)
    print("           PROCESSING SUMMARY")
    print("-" * 40)
    print(f"Total Leads Processed: {total}")
    print(f"Average Lead Score: {avg_score:.1f}")
    print(f"High Priority Leads: {high_priority}")
    print(f"Medium Priority Leads: {medium_priority}")
    print(f"Low Priority Leads: {low_priority}")
    print("-" * 40)


def print_lead_result(result: Dict[str, Any]):
    """Print individual lead result"""
    print(f"\n{'─' * 50}")
    print(f"Lead Name: {result['Name']}")
    print(f"Company: {result['Company Name']}")
    print(f"Industry: {result['Industry']}")
    print(f"Lead Score: {result['Lead Score']}")
    print(f"Priority: {result['Priority']}")
    print(f"Business Need: {result['Business Need']}")
    print(f"Recommended Action: {result['Recommended Action']}")
    print(f"{'─' * 50}")


def process_leads(
    input_file: str,
    output_file: str = None,
    use_google_sheets: bool = False,
    verbose: bool = False
) -> List[Dict[str, Any]]:
    """
    Main workflow: Load leads → AI Analysis → Score → Store
    """
    print(f"Loading leads from: {input_file}")
    leads = load_leads_from_csv(input_file)
    print(f"Found {len(leads)} leads to process\n")

    results = []

    print("Analyzing leads with AI...")
    for lead in tqdm(leads, desc="Processing", unit="lead"):
        # Skip empty or invalid leads
        if not lead.get('Name') or not lead.get('Email'):
            continue

        # Analyze lead with AI
        analysis = analyze_lead(lead)

        # Format for storage
        result = format_result_for_storage(lead, analysis)
        results.append(result)

        # Print individual result if verbose
        if verbose:
            print_lead_result(result)

    # Print summary
    print_summary(results)

    # Save results
    print("\nSaving results...")

    # Always save to CSV
    csv_path = save_to_csv(results, output_file)
    print(f"Saved to CSV: {csv_path}")

    # Optionally save to Google Sheets
    if use_google_sheets:
        try:
            sheet_url = save_to_google_sheets(results)
            print(f"Saved to Google Sheets: {sheet_url}")
        except Exception as e:
            print(f"Warning: Could not save to Google Sheets: {e}")
            print("Make sure you have set up Google Sheets credentials correctly.")

    return results


def main():
    """Main entry point with CLI argument parsing"""
    parser = argparse.ArgumentParser(
        description="AI-powered Lead Qualification Automation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                                    # Process sample_leads.csv
  python main.py -i leads.csv                       # Process custom input file
  python main.py -i leads.csv -o results.csv        # Custom input and output
  python main.py --google-sheets                    # Also save to Google Sheets
  python main.py -v                                 # Verbose output
        """
    )

    parser.add_argument(
        '-i', '--input',
        default=config.INPUT_CSV_PATH,
        help='Input CSV file with leads (default: sample_leads.csv)'
    )

    parser.add_argument(
        '-o', '--output',
        default=config.OUTPUT_CSV_PATH,
        help='Output CSV file for results (default: qualified_leads.csv)'
    )

    parser.add_argument(
        '-g', '--google-sheets',
        action='store_true',
        help='Also save results to Google Sheets'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Print detailed output for each lead'
    )

    parser.add_argument(
        '--provider',
        choices=['openai', 'anthropic', 'groq'],
        help='Override LLM provider (default: from config)'
    )

    args = parser.parse_args()

    # Override provider if specified
    if args.provider:
        config.LLM_PROVIDER = args.provider

    print_banner()
    print(f"Using LLM Provider: {config.LLM_PROVIDER}")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        results = process_leads(
            input_file=args.input,
            output_file=args.output,
            use_google_sheets=args.google_sheets,
            verbose=args.verbose
        )

        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Lead qualification complete!")

        return 0

    except FileNotFoundError as e:
        print(f"Error: Input file not found - {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
