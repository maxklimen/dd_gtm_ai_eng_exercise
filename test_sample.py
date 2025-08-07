"""
Test with specific interesting companies
"""
import asyncio
from pathlib import Path
import json
from utils.parser import SpeakerParser
from utils.enrichment import CompanyEnricher
from utils.classifier import CompanyClassifier
from utils.email_generator import EmailGenerator


async def test_sample():
    """Test with hand-picked companies"""
    print("🧪 Testing with selected companies...\n")
    
    # Parse all speakers
    parser = SpeakerParser("in/scraped_pages")
    all_speakers = parser.parse_all_speakers()
    
    # Find specific interesting companies
    interesting_companies = [
        "Laing O'Rourke",  # Likely Builder
        "Kier Construction",  # Likely Builder  
        "AECOM",  # Likely Builder/Engineering
        "WSP",  # Engineering/Consulting
        "Autodesk",  # Software - Partner/Competitor
        "Trimble",  # Software - Partner/Competitor
        "Turner & Townsend",  # Consulting
        "Multiplex",  # Builder
        "BAM Ireland",  # Builder
        "Ordnance Survey"  # Government/Data
    ]
    
    speakers = []
    for company in interesting_companies:
        speaker = next((s for s in all_speakers if s.get('company') == company), None)
        if speaker:
            speakers.append(speaker)
    
    print(f"Testing {len(speakers)} speakers from key companies:")
    for s in speakers:
        print(f"  - {s['name']:25} | {s['company']:25} | {len(s.get('sessions', []))} session(s)")
    print()
    
    # Enrich
    print("Enriching companies...")
    enricher = CompanyEnricher()
    enriched_speakers = await enricher.enrich_speakers_batch(speakers)
    
    # Classify
    print("\nClassifying companies...")
    classifier = CompanyClassifier()
    classified_speakers = await classifier.classify_batch(enriched_speakers)
    
    print("\n📊 Classification Results:")
    print("-" * 60)
    for speaker in classified_speakers:
        confidence = speaker.get('classification_confidence', 0)
        print(f"{speaker['company']:25} → {speaker['category']:12} ({confidence:.0%})")
        if speaker.get('classification_reasoning'):
            print(f"  Reasoning: {speaker['classification_reasoning'][:100]}...")
    
    # Generate emails
    print("\n✉️ Generating emails...")
    generator = EmailGenerator()
    final_speakers = await generator.generate_emails_batch(classified_speakers)
    
    # Show emails
    print("\n📧 Generated Emails:")
    print("=" * 80)
    for speaker in final_speakers:
        if speaker.get("email_subject"):
            print(f"\n{speaker['name']} ({speaker['company']}) - {speaker['category']}")
            print(f"Session: {speaker.get('sessions', [{}])[0].get('title', 'N/A')[:60]}...")
            print(f"\nSubject: {speaker['email_subject']}")
            print(f"\nBody:\n{speaker['email_body']}\n")
            print("-" * 80)
    
    # Summary
    builders = sum(1 for s in classified_speakers if s.get('category') == 'Builder')
    owners = sum(1 for s in classified_speakers if s.get('category') == 'Owner')
    partners = sum(1 for s in classified_speakers if s.get('category') == 'Partner')
    
    print(f"\n📊 Summary:")
    print(f"  Builders: {builders}")
    print(f"  Owners: {owners}")
    print(f"  Partners: {partners}")
    print(f"  Emails generated: {sum(1 for s in final_speakers if s.get('email_subject'))}")
    
    # Save
    with open('out/test_sample.json', 'w') as f:
        json.dump(final_speakers, f, indent=2)


if __name__ == "__main__":
    Path("out").mkdir(exist_ok=True)
    asyncio.run(test_sample())