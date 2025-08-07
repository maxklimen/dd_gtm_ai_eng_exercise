"""
Enhanced HTML Parser for extracting comprehensive speaker information from conference pages
Extracts: name, company, job title, sessions, image URLs, and bio (if available)
"""
from bs4 import BeautifulSoup
from pathlib import Path
import json
from typing import Dict, List, Optional


class SpeakerParser:
    """Parse comprehensive speaker information from HTML files"""
    
    def __init__(self, scraped_pages_dir: str):
        self.scraped_pages_dir = Path(scraped_pages_dir)
        self.speakers_dir = self.scraped_pages_dir / "speakers"
    
    def parse_speaker_page(self, html_path: Path) -> Optional[Dict]:
        """
        Parse a single speaker HTML page with enhanced extraction
        
        Returns:
            Dictionary with name, company, job_title, bio, sessions, and image_url
        """
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            
            speaker_info = {}
            
            # Extract basic details from speaker-details div
            details_div = soup.find('div', class_='speaker-details')
            if details_div:
                for p_tag in details_div.find_all('p'):
                    text = p_tag.get_text(strip=True)
                    if 'Name:' in text:
                        speaker_info['name'] = text.replace('Name:', '').strip()
                    elif 'Company:' in text:
                        speaker_info['company'] = text.replace('Company:', '').strip()
                    elif 'Job Title:' in text:
                        speaker_info['job_title'] = text.replace('Job Title:', '').strip()
            
            # Extract bio (if available)
            bio_div = soup.find('div', class_='speaker-bio')
            if bio_div:
                bio_content_div = bio_div.find('div', class_='bio-content')
                if bio_content_div:
                    # Get all paragraphs and join them
                    paragraphs = bio_content_div.find_all('p')
                    if paragraphs:
                        bio_text = '\n\n'.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
                        speaker_info['bio'] = bio_text
                    else:
                        # If no p tags, get all text
                        bio_text = bio_content_div.get_text(strip=True)
                        if bio_text and bio_text != 'Biography':
                            speaker_info['bio'] = bio_text
            
            # Extract sessions (conference talks/presentations)
            sessions_div = soup.find('div', class_='speaker-sessions')
            if sessions_div:
                sessions = []
                for link in sessions_div.find_all('a'):
                    session_title = link.get_text(strip=True)
                    session_url = link.get('href', '')
                    if session_title:
                        # Clean up HTML entities
                        session_title = session_title.replace('&#038;', '&').replace('&#8211;', '–')
                        sessions.append({
                            'title': session_title,
                            'url': session_url
                        })
                if sessions:
                    speaker_info['sessions'] = sessions
            
            # Extract speaker image URL from meta tags
            meta_image = soup.find('meta', property='og:image')
            if meta_image:
                speaker_info['image_url'] = meta_image.get('content', '')
            
            # Set defaults for missing fields
            speaker_info.setdefault('name', '')
            speaker_info.setdefault('company', '')
            speaker_info.setdefault('job_title', '')
            speaker_info.setdefault('bio', '')
            speaker_info.setdefault('sessions', [])
            speaker_info.setdefault('image_url', '')
            
            # Only return if we have at least name or company
            if speaker_info.get('name') or speaker_info.get('company'):
                return speaker_info
            
            return None
            
        except Exception as e:
            print(f"Error parsing {html_path}: {e}")
            return None
    
    def parse_all_speakers(self) -> List[Dict]:
        """
        Parse all speaker HTML files with enhanced extraction
        
        Returns:
            List of speaker dictionaries with all available information
        """
        speakers = []
        
        # Get all speaker directories (sorted for consistency)
        speaker_dirs = sorted([d for d in self.speakers_dir.iterdir() if d.is_dir()])
        
        for speaker_dir in speaker_dirs:
            html_file = speaker_dir / "index.html"
            if html_file.exists():
                speaker_info = self.parse_speaker_page(html_file)
                if speaker_info:
                    # Add speaker ID from directory name
                    speaker_info['speaker_id'] = speaker_dir.name
                    speakers.append(speaker_info)
                else:
                    print(f"Warning: Could not parse speaker from {speaker_dir.name}")
        
        return speakers
    
    def get_statistics(self, speakers: List[Dict]) -> Dict:
        """Generate statistics about the parsed data"""
        stats = {
            'total_speakers': len(speakers),
            'speakers_with_bio': sum(1 for s in speakers if s.get('bio')),
            'speakers_with_sessions': sum(1 for s in speakers if s.get('sessions')),
            'speakers_with_image': sum(1 for s in speakers if s.get('image_url')),
            'empty_job_titles': sum(1 for s in speakers if not s.get('job_title')),
            'total_sessions': sum(len(s.get('sessions', [])) for s in speakers),
            'multi_session_speakers': sum(1 for s in speakers if len(s.get('sessions', [])) > 1),
            'companies': len(set(s.get('company', '') for s in speakers if s.get('company')))
        }
        return stats
    
    def save_to_json(self, speakers: List[Dict], output_path: str):
        """Save parsed speakers to JSON file with statistics"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(speakers, f, indent=2, ensure_ascii=False)
        
        # Generate and display statistics
        stats = self.get_statistics(speakers)
        
        print(f"✅ Saved {len(speakers)} speakers to {output_path}")
        print(f"📊 Statistics:")
        print(f"   - Speakers with bio: {stats['speakers_with_bio']}/{stats['total_speakers']}")
        print(f"   - Speakers with sessions: {stats['speakers_with_sessions']}/{stats['total_speakers']}")
        print(f"   - Multi-session speakers: {stats['multi_session_speakers']}")
        print(f"   - Total sessions: {stats['total_sessions']}")
        print(f"   - Unique companies: {stats['companies']}")


# Example usage
if __name__ == "__main__":
    parser = SpeakerParser("in/scraped_pages")
    speakers = parser.parse_all_speakers()
    print(f"Found {len(speakers)} speakers")
    if speakers:
        print("Sample speaker:", speakers[0])