"""
Stage 2: Fast parallel email generation for Builders and Owners only
"""
import asyncio
import json
from pathlib import Path
import time
from typing import List, Dict
import sys

from .email_generator import EmailGenerator


async def generate_all_emails(resume=False, batch_size=15):
    """
    Generate emails for all Builders and Owners
    
    Args:
        resume: Resume from checkpoint if True
        batch_size: Number of concurrent email generations
    """
    print("=" * 70)
    print("STAGE 2: EMAIL GENERATION")
    print("=" * 70)
    
    # Load classified speakers
    classified_file = Path("out/speakers_classified.json")
    if not classified_file.exists():
        print("❌ Error: Run Stage 1 (classification) first!")
        print("   File not found: out/speakers_classified.json")
        return []
    
    with open(classified_file, 'r') as f:
        all_speakers = json.load(f)
    
    # Filter for Builders and Owners only
    target_speakers = [
        s for s in all_speakers 
        if s.get('category') in ['Builder', 'Owner']
    ]
    
    print(f"📊 Found {len(target_speakers)} Builders/Owners (from {len(all_speakers)} total)")
    
    if not target_speakers:
        print("⚠️ No Builders or Owners found to generate emails for")
        return all_speakers
    
    # Check for resume
    checkpoint_file = Path("out/checkpoint_emails.json")
    processed_ids = set()
    
    if resume and checkpoint_file.exists():
        print("📂 Resuming from checkpoint...")
        with open(checkpoint_file, 'r') as f:
            checkpoint_data = json.load(f)
            processed_ids = set(checkpoint_data['processed'])
            
            # Update speakers with generated emails
            email_map = checkpoint_data.get('emails', {})
            for speaker in all_speakers:
                speaker_id = f"{speaker.get('name')}_{speaker.get('company')}"
                if speaker_id in email_map:
                    speaker['email_subject'] = email_map[speaker_id].get('subject', '')
                    speaker['email_body'] = email_map[speaker_id].get('body', '')
            
            print(f"   Loaded {len(processed_ids)} previously generated emails")
    
    # Filter out already processed
    speakers_to_process = [
        s for s in target_speakers
        if f"{s.get('name')}_{s.get('company')}" not in processed_ids
    ]
    
    if not speakers_to_process:
        print("✅ All emails already generated!")
        return all_speakers
    
    print(f"📧 To generate: {len(speakers_to_process)} emails")
    print()
    
    # Initialize email generator
    generator = EmailGenerator()
    
    # Statistics
    start_time = time.time()
    emails_generated = len(processed_ids)
    email_map = {}
    
    # Load existing email map if resuming
    if resume and checkpoint_file.exists():
        with open(checkpoint_file, 'r') as f:
            checkpoint_data = json.load(f)
            email_map = checkpoint_data.get('emails', {})
    
    # Process in chunks for checkpointing
    checkpoint_interval = 20
    
    for i in range(0, len(speakers_to_process), checkpoint_interval):
        chunk = speakers_to_process[i:i+checkpoint_interval]
        chunk_num = (emails_generated // checkpoint_interval) + 1
        
        print(f"\n📦 Generating emails for chunk {chunk_num} ({len(chunk)} speakers)...")
        
        # Generate emails with high parallelization
        chunk_with_emails = await generator.generate_emails_batch(chunk, batch_size=batch_size)
        
        # Update all speakers list and email map
        for speaker in chunk_with_emails:
            speaker_id = f"{speaker.get('name')}_{speaker.get('company')}"
            processed_ids.add(speaker_id)
            
            if speaker.get('email_subject'):
                emails_generated += 1
                email_map[speaker_id] = {
                    'subject': speaker['email_subject'],
                    'body': speaker['email_body']
                }
                
                # Update in main list
                for s in all_speakers:
                    if s.get('name') == speaker.get('name') and s.get('company') == speaker.get('company'):
                        s['email_subject'] = speaker['email_subject']
                        s['email_body'] = speaker['email_body']
                        break
        
        # Save checkpoint
        checkpoint_data = {
            'processed': list(processed_ids),
            'emails': email_map,
            'timestamp': time.time()
        }
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)
        
        # Progress report
        elapsed = time.time() - start_time
        rate = (emails_generated - len(processed_ids) + len(speakers_to_process)) / elapsed if elapsed > 0 else 0
        remaining = len(target_speakers) - emails_generated
        eta = remaining / rate if rate > 0 else 0
        
        print(f"\n📊 Progress: {emails_generated}/{len(target_speakers)} emails")
        print(f"   Speed: {rate:.1f} emails/sec | ETA: {eta/60:.1f} minutes")
        print(f"   💾 Checkpoint saved")
    
    # Save final results with emails
    output_file = Path("out/speakers_with_emails.json")
    with open(output_file, 'w') as f:
        json.dump(all_speakers, f, indent=2)
    
    # Final report
    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print("✅ EMAIL GENERATION COMPLETE")
    print(f"   Time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
    print(f"   Generated: {emails_generated} emails")
    print(f"   Skipped: {len(all_speakers) - emails_generated} (Partners/Competitors/Customers)")
    print(f"\n💾 Results saved to {output_file}")
    print("=" * 70)
    
    return all_speakers


if __name__ == "__main__":
    # Can be run standalone
    resume = "--resume" in sys.argv
    asyncio.run(generate_all_emails(resume=resume))