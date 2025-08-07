"""
Stage 1: Fast parallel classification of all speakers
Saves checkpoint every 25 speakers for resume capability
"""
import asyncio
import json
from pathlib import Path
import time
from typing import List, Dict
import sys

from .parser import SpeakerParser
from .enrichment import CompanyEnricher
from .classifier import CompanyClassifier


async def classify_all_speakers(resume=False, batch_size=10):
    """
    Classify all speakers with high parallelization
    
    Args:
        resume: Resume from checkpoint if True
        batch_size: Number of concurrent classifications
    """
    print("=" * 70)
    print("STAGE 1: CLASSIFICATION")
    print("=" * 70)
    
    checkpoint_file = Path("out/checkpoint_classify.json")
    processed_speaker_ids = set()
    all_results = []
    
    # Check for resume
    if resume and checkpoint_file.exists():
        print("📂 Resuming from checkpoint...")
        with open(checkpoint_file, 'r') as f:
            checkpoint_data = json.load(f)
            all_results = checkpoint_data['results']
            # Create unique speaker IDs instead of just tracking companies
            processed_speaker_ids = {
                f"{s['name']}|{s['company']}" 
                for s in all_results
            }
            print(f"   Loaded {len(all_results)} previously classified speakers")
    else:
        processed_speaker_ids = set()
    
    # Parse speakers
    print("📋 Loading speaker data...")
    parser = SpeakerParser("in/scraped_pages")
    all_speakers = parser.parse_all_speakers()
    
    # Filter out already processed (by unique speaker ID, not just company)
    speakers_to_process = []
    for s in all_speakers:
        speaker_id = f"{s.get('name')}|{s.get('company')}"
        if speaker_id not in processed_speaker_ids:
            speakers_to_process.append(s)
    
    if not speakers_to_process:
        print("✅ All speakers already classified!")
        return all_results
    
    print(f"📊 Total: {len(all_speakers)} speakers")
    print(f"   To process: {len(speakers_to_process)}")
    print(f"   Already done: {len(processed_speaker_ids)}")
    print()
    
    # Initialize services
    enricher = CompanyEnricher()
    classifier = CompanyClassifier()
    
    # Statistics
    categories = {"Builder": 0, "Owner": 0, "Partner": 0, "Customer": 0, "Competitor": 0, "Other": 0}
    start_time = time.time()
    
    # Process in chunks for checkpointing
    checkpoint_interval = 10
    
    for i in range(0, len(speakers_to_process), checkpoint_interval):
        chunk = speakers_to_process[i:i+checkpoint_interval]
        chunk_num = (len(all_results) // checkpoint_interval) + 1
        
        print(f"\n📦 Processing chunk {chunk_num} ({len(chunk)} speakers)...")
        
        # Enrich
        print("   🔍 Enriching companies...")
        enriched = await enricher.enrich_speakers_batch(chunk)
        
        # Classify with high parallelization
        print(f"   🏷️ Classifying with {batch_size} parallel calls...")
        classified = await classifier.classify_batch(enriched, batch_size=batch_size)
        
        # Update statistics
        for speaker in classified:
            cat = speaker.get('category', 'Other')
            categories[cat] += 1
            all_results.append(speaker)
            # Track individual speakers, not just companies
            speaker_id = f"{speaker['name']}|{speaker['company']}"
            processed_speaker_ids.add(speaker_id)
        
        # Save checkpoint
        checkpoint_data = {
            'results': all_results,
            'processed': list(processed_speaker_ids),  # Save speaker IDs not companies
            'timestamp': time.time()
        }
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)
        
        # Progress report
        elapsed = time.time() - start_time
        rate = len(all_results) / elapsed if elapsed > 0 else 0
        eta = (len(all_speakers) - len(all_results)) / rate if rate > 0 else 0
        
        print(f"\n📊 Progress: {len(all_results)}/{len(all_speakers)} ({len(all_results)*100//len(all_speakers)}%)")
        print(f"   Speed: {rate:.1f} speakers/sec | ETA: {eta/60:.1f} minutes")
        print(f"   Builders: {categories['Builder']} | Owners: {categories['Owner']} | Customers: {categories['Customer']}")
        print(f"   💾 Checkpoint saved")
    
    # Save final results
    output_file = Path("out/speakers_classified.json")
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Final report
    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print("✅ CLASSIFICATION COMPLETE")
    print(f"   Time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
    print(f"   Processed: {len(all_results)} speakers")
    print("\n📊 Final Categories:")
    for cat, count in sorted(categories.items()):
        if count > 0:
            print(f"   {cat}: {count}")
    print(f"\n💾 Results saved to {output_file}")
    print("=" * 70)
    
    return all_results


if __name__ == "__main__":
    # Can be run standalone
    resume = "--resume" in sys.argv
    asyncio.run(classify_all_speakers(resume=resume))