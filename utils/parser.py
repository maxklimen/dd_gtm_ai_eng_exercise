"""
HTML Parser for extracting speaker information from conference pages
"""
from bs4 import BeautifulSoup
from pathlib import Path
import json
from typing import Dict, List, Optional


class SpeakerParser:
    """Parse speaker information from HTML files"""
    
    def __init__(self, scraped_pages_dir: str):
        self.scraped_pages_dir = Path(scraped_pages_dir)
        self.speakers_dir = self.scraped_pages_dir / "speakers"
    
    def parse_speaker_page(self, html_path: Path) -> Optional[Dict[str, str]]:
        """
        Parse a single speaker HTML page
        
        Returns:
            Dictionary with name, company, job_title or None if parsing fails
        """
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            
            # Find the speaker-details div
            details_div = soup.find('div', class_='speaker-details')
            if not details_div:
                return None
            
            # Extract information
            speaker_info = {}
            
            # Parse each <p> tag in the details div
            for p_tag in details_div.find_all('p'):
                text = p_tag.get_text(strip=True)
                if 'Name:' in text:
                    speaker_info['name'] = text.replace('Name:', '').strip()
                elif 'Company:' in text:
                    speaker_info['company'] = text.replace('Company:', '').strip()
                elif 'Job Title:' in text:
                    speaker_info['job_title'] = text.replace('Job Title:', '').strip()
            
            # Validate we have all required fields
            if all(key in speaker_info for key in ['name', 'company', 'job_title']):
                return speaker_info
            
            return None
            
        except Exception as e:
            print(f"Error parsing {html_path}: {e}")
            return None
    
    def parse_all_speakers(self) -> List[Dict[str, str]]:
        """
        Parse all speaker HTML files
        
        Returns:
            List of speaker dictionaries
        """
        speakers = []
        
        # Iterate through all speaker directories
        for speaker_dir in self.speakers_dir.iterdir():
            if speaker_dir.is_dir():
                html_file = speaker_dir / "index.html"
                if html_file.exists():
                    speaker_info = self.parse_speaker_page(html_file)
                    if speaker_info:
                        speakers.append(speaker_info)
                    else:
                        print(f"Warning: Could not parse speaker from {speaker_dir.name}")
        
        return speakers
    
    def save_to_json(self, speakers: List[Dict[str, str]], output_path: str):
        """Save parsed speakers to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(speakers, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(speakers)} speakers to {output_path}")


# Example usage
if __name__ == "__main__":
    parser = SpeakerParser("in/scraped_pages")
    speakers = parser.parse_all_speakers()
    print(f"Found {len(speakers)} speakers")
    if speakers:
        print("Sample speaker:", speakers[0])