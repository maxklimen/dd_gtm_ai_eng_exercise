"""
Main orchestration script for DroneDeploy GTM Exercise
Can run as single pipeline or in stages for better control
"""
import asyncio
import sys
import time
from pathlib import Path

# Import stage modules
from utils.stage1_classify import classify_all_speakers
from utils.stage2_generate import generate_all_emails
from utils.stage3_export import export_to_csv


async def run_all_stages():
    """Run all stages sequentially"""
    print("🚀 DroneDeploy GTM Email Generation Pipeline")
    print("=" * 70)
    print("Running all stages: Classification → Email Generation → Export")
    print("=" * 70)
    
    total_start = time.time()
    
    # Stage 1: Classification
    print("\n" + "🏷️ " * 20)
    await classify_all_speakers(resume=False, batch_size=10)
    
    # Stage 2: Email Generation
    print("\n" + "✉️ " * 20)
    await generate_all_emails(resume=False, batch_size=15)
    
    # Stage 3: Export
    print("\n" + "📝 " * 20)
    export_to_csv()
    
    # Final summary
    total_elapsed = time.time() - total_start
    print("\n" + "=" * 70)
    print("🎉 PIPELINE COMPLETE!")
    print(f"⏱️  Total time: {total_elapsed:.1f} seconds ({total_elapsed/60:.1f} minutes)")
    print("📊 Check out/email_list.csv for final results")
    print("=" * 70)


async def run_classification_only():
    """Run only classification stage"""
    print("🏷️  Running Classification Only")
    await classify_all_speakers(resume="--resume" in sys.argv, batch_size=10)


async def run_email_generation_only():
    """Run only email generation stage"""
    print("✉️  Running Email Generation Only")
    await generate_all_emails(resume="--resume" in sys.argv, batch_size=15)


def run_export_only():
    """Run only export stage"""
    print("📝 Running Export Only")
    export_to_csv()


def print_usage():
    """Print usage instructions"""
    print("""
DroneDeploy GTM Email Pipeline

Usage:
  python main.py [options]

Options:
  (no args)     Run all stages (default)
  --classify    Run classification only (Stage 1)
  --generate    Run email generation only (Stage 2)
  --export      Run CSV export only (Stage 3)
  --resume      Resume from last checkpoint (use with stage options)
  --help        Show this help message

Examples:
  python main.py                    # Run complete pipeline
  python main.py --classify         # Classify all speakers
  python main.py --generate --resume # Resume email generation
  python main.py --export           # Export to CSV

Stages can be run independently:
  1. Classification creates: out/speakers_classified.json
  2. Email generation creates: out/speakers_with_emails.json
  3. Export creates: out/email_list.csv

For very large runs, consider running stages separately to avoid timeouts.
    """)


async def main():
    """Main entry point with command line argument handling"""
    # Create output directory
    Path("out").mkdir(exist_ok=True)
    
    # Parse command line arguments
    if "--help" in sys.argv or "-h" in sys.argv:
        print_usage()
        return
    
    if "--classify" in sys.argv:
        await run_classification_only()
    elif "--generate" in sys.argv:
        await run_email_generation_only()
    elif "--export" in sys.argv:
        run_export_only()
    else:
        # Default: run all stages
        await run_all_stages()


if __name__ == "__main__":
    # Run the pipeline
    asyncio.run(main())