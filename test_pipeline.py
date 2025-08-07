"""
Test script to verify the pipeline with a small sample
"""
import asyncio
from pathlib import Path
import json
from utils.parser import SpeakerParser
from utils.enrichment import CompanyEnricher
from utils.classifier import CompanyClassifier
from utils.email_generator import EmailGenerator


async def test_pipeline():
    """Test pipeline with 3 speakers"""
    print("🧪 Testing pipeline with 3 speakers...\n")
    
    # Step 1: Parse speakers
    print("Step 1: Parsing speakers...")
    parser = SpeakerParser("in/scraped_pages")
    all_speakers = parser.parse_all_speakers()
    
    # Take only first 3 for testing
    speakers = all_speakers[:3]
    print(f"Testing with: {[s['name'] for s in speakers]}\n")
    
    # Step 2: Enrich with Tavily
    print("Step 2: Testing Tavily enrichment...")
    enricher = CompanyEnricher()
    enriched_speakers = await enricher.enrich_speakers_batch(speakers)
    print(f"✅ Enriched {len(enriched_speakers)} speakers\n")
    
    # Step 3: Classify companies
    print("Step 3: Testing classification...")
    classifier = CompanyClassifier()
    classified_speakers = await classifier.classify_batch(enriched_speakers)
    print()
    
    for speaker in classified_speakers:
        if 'name' in speaker and 'company' in speaker and 'category' in speaker:
            print(f"  - {speaker['name']} ({speaker['company']}): {speaker['category']}")
    print()
    
    # Step 4: Generate emails
    print("Step 4: Testing email generation...")
    generator = EmailGenerator()
    final_speakers = await generator.generate_emails_batch(classified_speakers)
    
    # Show results
    print("\n📧 Generated Emails:")
    print("=" * 60)
    for speaker in final_speakers:
        if speaker.get("email_subject"):
            print(f"\n{speaker['name']} ({speaker['company']})")
            print(f"Sessions: {len(speaker.get('sessions', []))}")
            print(f"Category: {speaker['category']}")
            print(f"Subject: {speaker['email_subject']}")
            print(f"Body: {speaker['email_body'][:200]}...")
    
    # Save test results
    with open("out/test_results.json", "w") as f:
        json.dump(final_speakers, f, indent=2)
    print(f"\n✅ Test complete! Results saved to out/test_results.json")


if __name__ == "__main__":
    Path("out").mkdir(exist_ok=True)
    asyncio.run(test_pipeline())