"""
Expanded test to review more classifications and email quality
"""
import asyncio
from pathlib import Path
import json
import pandas as pd
from utils.parser import SpeakerParser
from utils.enrichment import CompanyEnricher
from utils.classifier import CompanyClassifier
from utils.email_generator import EmailGenerator


async def test_expanded():
    """Test pipeline with 15 diverse speakers"""
    print("🧪 Testing pipeline with 15 speakers...\n")
    
    # Step 1: Parse speakers
    print("Step 1: Parsing speakers...")
    parser = SpeakerParser("in/scraped_pages")
    all_speakers = parser.parse_all_speakers()
    
    # Select diverse sample - mix of companies likely to be builders, owners, partners
    selected_indices = [0, 5, 10, 15, 20, 25, 30, 50, 75, 100, 150, 200, 250, 300, 350]
    speakers = [all_speakers[i] for i in selected_indices if i < len(all_speakers)]
    
    print(f"Testing with {len(speakers)} speakers:")
    for s in speakers:
        sessions_count = len(s.get('sessions', []))
        print(f"  - {s['name']:30} | {s['company']:35} | {sessions_count} session(s)")
    print()
    
    # Step 2: Enrich with Tavily
    print("Step 2: Enriching with Tavily...")
    enricher = CompanyEnricher()
    enriched_speakers = await enricher.enrich_speakers_batch(speakers)
    print(f"✅ Enriched {len(enriched_speakers)} speakers\n")
    
    # Step 3: Classify companies
    print("Step 3: Classifying companies...")
    classifier = CompanyClassifier()
    classified_speakers = await classifier.classify_batch(enriched_speakers)
    
    # Show classification summary
    categories = {}
    for speaker in classified_speakers:
        cat = speaker.get('category', 'Unknown')
        categories[cat] = categories.get(cat, 0) + 1
        print(f"  {speaker['company']:35} → {cat:12} (confidence: {speaker.get('classification_confidence', 0):.2f})")
    
    print(f"\n📊 Classification Summary:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    print()
    
    # Step 4: Generate emails (only for Builders and Owners)
    print("Step 4: Generating emails...")
    generator = EmailGenerator()
    final_speakers = await generator.generate_emails_batch(classified_speakers)
    
    # Display emails
    print("\n📧 Generated Emails:")
    print("=" * 80)
    email_count = 0
    for speaker in final_speakers:
        if speaker.get("email_subject"):
            email_count += 1
            print(f"\n[{email_count}] {speaker['name']} ({speaker['company']})")
            print(f"    Category: {speaker['category']}")
            print(f"    Sessions: {', '.join([s['title'][:50] + '...' for s in speaker.get('sessions', [])][:2])}")
            print(f"    Subject: {speaker['email_subject']}")
            print(f"    Body Preview: {speaker['email_body'][:150]}...")
    
    if email_count == 0:
        print("No emails generated (all speakers were Partners/Competitors/Other)")
    
    # Save results
    df = pd.DataFrame([{
        'Speaker Name': s['name'],
        'Speaker Title': s.get('job_title', ''),
        'Speaker Company': s['company'],
        'Company Category': s.get('category', ''),
        'Email Subject': s.get('email_subject', ''),
        'Email Body': s.get('email_body', '')
    } for s in final_speakers])
    
    df.to_csv('out/test_expanded.csv', index=False)
    
    with open('out/test_expanded.json', 'w') as f:
        json.dump(final_speakers, f, indent=2)
    
    print(f"\n✅ Test complete!")
    print(f"   - Tested {len(speakers)} speakers")
    print(f"   - Generated {email_count} emails")
    print(f"   - Results saved to out/test_expanded.csv and out/test_expanded.json")


if __name__ == "__main__":
    Path("out").mkdir(exist_ok=True)
    asyncio.run(test_expanded())