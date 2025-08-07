"""
Stage 3: Export final results to CSV
"""
import json
import pandas as pd
from pathlib import Path


def export_to_csv():
    """Export final results to CSV format"""
    print("=" * 70)
    print("STAGE 3: CSV EXPORT")
    print("=" * 70)
    
    # Load speakers with emails
    input_file = Path("out/speakers_with_emails.json")
    if not input_file.exists():
        # Try classified file if emails not generated yet
        input_file = Path("out/speakers_classified.json")
        if not input_file.exists():
            print("❌ Error: No data to export!")
            print("   Run Stage 1 (classification) first")
            return False
    
    print(f"📂 Loading data from {input_file}...")
    with open(input_file, 'r') as f:
        speakers = json.load(f)
    
    print(f"📊 Processing {len(speakers)} speakers...")
    
    # Prepare data for CSV
    csv_data = []
    emails_count = 0
    
    for speaker in speakers:
        # Ensure all fields exist
        speaker_name = speaker.get('name', '')
        job_title = speaker.get('job_title', '')
        company = speaker.get('company', '')
        category = speaker.get('category', 'Other')
        email_subject = speaker.get('email_subject', '')
        email_body = speaker.get('email_body', '')
        
        if email_subject:
            emails_count += 1
        
        csv_data.append({
            'Speaker Name': speaker_name,
            'Speaker Title': job_title,
            'Speaker Company': company,
            'Company Category': category,
            'Email Subject': email_subject,
            'Email Body': email_body
        })
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(csv_data)
    
    # Sort by category (Builders first, then Owners, then others)
    category_order = {'Builder': 0, 'Owner': 1, 'Customer': 2, 'Partner': 3, 'Competitor': 4, 'Other': 5}
    df['sort_order'] = df['Company Category'].map(category_order).fillna(6)
    df = df.sort_values(['sort_order', 'Speaker Company', 'Speaker Name'])
    df = df.drop('sort_order', axis=1)
    
    # Save to CSV
    output_file = Path("out/email_list.csv")
    df.to_csv(output_file, index=False)
    
    # Statistics
    category_counts = df['Company Category'].value_counts()
    
    print("\n📊 Export Summary:")
    print(f"   Total rows: {len(df)}")
    print(f"   Emails generated: {emails_count}")
    print("\n   Category breakdown:")
    for cat, count in category_counts.items():
        print(f"     {cat}: {count}")
    
    print(f"\n✅ CSV exported to {output_file}")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    # Can be run standalone
    export_to_csv()