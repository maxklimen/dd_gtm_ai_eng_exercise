"""
Main orchestration script for DroneDeploy GTM Exercise
Generates personalized emails for conference speakers
"""
import asyncio
import pandas as pd
from pathlib import Path
import json
from tqdm import tqdm
import time

from utils.parser import SpeakerParser
from utils.enrichment import CompanyEnricher
from utils.classifier import CompanyClassifier
from utils.email_generator import EmailGenerator


async def main():
    """Main pipeline execution"""
    print("🚀 Starting DroneDeploy GTM Email Generation Pipeline\n")
    start_time = time.time()
    
    # Step 1: Parse speaker data
    print("📋 Step 1: Parsing speaker data from HTML files...")
    parser = SpeakerParser("in/scraped_pages")
    speakers = parser.parse_all_speakers()
    print(f"✅ Found {len(speakers)} speakers\n")
    
    # Save intermediate results
    parser.save_to_json(speakers, "out/speakers_raw.json")
    
    # Step 2: Enrich with Tavily
    print("🔍 Step 2: Enriching company data with Tavily API...")
    enricher = CompanyEnricher()
    enriched_speakers = await enricher.enrich_speakers_batch(speakers)
    print(f"✅ Enriched {len(enriched_speakers)} speakers\n")
    
    # Save enriched data
    with open("out/speakers_enriched.json", "w") as f:
        json.dump(enriched_speakers, f, indent=2)
    
    # Step 3: Classify companies
    print("🏷️  Step 3: Classifying companies...")
    classifier = CompanyClassifier()
    classified_speakers = await classifier.classify_batch(enriched_speakers)
    
    # Print classification summary
    categories = {}
    for speaker in classified_speakers:
        cat = speaker["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\n📊 Classification Summary:")
    for cat, count in sorted(categories.items()):
        print(f"  - {cat}: {count} companies")
    print()
    
    # Save classified data
    with open("out/speakers_classified.json", "w") as f:
        json.dump(classified_speakers, f, indent=2)
    
    # Step 4: Generate emails
    print("✉️  Step 4: Generating personalized emails...")
    generator = EmailGenerator()
    final_speakers = await generator.generate_emails_batch(classified_speakers)
    
    # Count generated emails
    emails_generated = sum(1 for s in final_speakers if s.get("email_subject"))
    print(f"✅ Generated {emails_generated} emails\n")
    
    # Step 5: Create final CSV
    print("📝 Step 5: Creating final CSV output...")
    
    # Prepare data for CSV
    csv_data = []
    for speaker in final_speakers:
        csv_data.append({
            "Speaker Name": speaker["name"],
            "Speaker Title": speaker["job_title"],
            "Speaker Company": speaker["company"],
            "Company Category": speaker["category"],
            "Email Subject": speaker.get("email_subject", ""),
            "Email Body": speaker.get("email_body", "")
        })
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(csv_data)
    df.to_csv("out/email_list.csv", index=False)
    print(f"✅ Saved results to out/email_list.csv\n")
    
    # Final summary
    elapsed_time = time.time() - start_time
    print("🎉 Pipeline Complete!")
    print(f"⏱️  Total time: {elapsed_time:.1f} seconds")
    print(f"📊 Processed {len(speakers)} speakers")
    print(f"✉️  Generated {emails_generated} emails")
    print(f"🚫 Skipped {len(speakers) - emails_generated} (competitors/partners/other)")


if __name__ == "__main__":
    # Create output directory if it doesn't exist
    Path("out").mkdir(exist_ok=True)
    
    # Run the pipeline
    asyncio.run(main())