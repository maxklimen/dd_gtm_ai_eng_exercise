"""
Tavily API enrichment for company information
"""
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional
from tavily import TavilyClient
import os
from dotenv import load_dotenv


class CompanyEnricher:
    """Enrich company information using Tavily API"""
    
    def __init__(self, cache_dir: str = "cache"):
        load_dotenv()
        self.client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / "tavily_cache.json"
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load cache from file"""
        if self.cache_file.exists():
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_cache(self):
        """Save cache to file"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def _get_cache_key(self, company: str, speaker_name: str) -> str:
        """Generate cache key for company/speaker combination"""
        return f"{company}|{speaker_name}".lower()
    
    async def enrich_company(self, company: str, speaker_name: str, job_title: str) -> Dict:
        """
        Enrich company information using Tavily search
        
        Returns:
            Dictionary with enriched company information
        """
        cache_key = self._get_cache_key(company, speaker_name)
        
        # Check cache first
        if cache_key in self.cache:
            print(f"Using cached data for {company}")
            return self.cache[cache_key]
        
        try:
            # Search for company in construction industry context
            query = f"{company} construction industry digital transformation drone technology"
            
            # Use Tavily search
            search_results = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=5
            )
            
            # Extract relevant information
            enriched_data = {
                "company": company,
                "speaker_name": speaker_name,
                "job_title": job_title,
                "search_results": []
            }
            
            for result in search_results.get("results", []):
                enriched_data["search_results"].append({
                    "title": result.get("title", ""),
                    "content": result.get("content", ""),
                    "url": result.get("url", "")
                })
            
            # Cache the result
            self.cache[cache_key] = enriched_data
            self._save_cache()
            
            return enriched_data
            
        except Exception as e:
            print(f"Error enriching {company}: {e}")
            return {
                "company": company,
                "speaker_name": speaker_name,
                "job_title": job_title,
                "search_results": [],
                "error": str(e)
            }
    
    async def enrich_speakers_batch(self, speakers: List[Dict[str, str]]) -> List[Dict]:
        """
        Enrich multiple speakers in parallel
        
        Args:
            speakers: List of speaker dictionaries with name, company, job_title
            
        Returns:
            List of enriched speaker data
        """
        enriched_speakers = []
        
        # Process speakers in batches of 5
        for i in range(0, len(speakers), 5):
            batch = speakers[i:i+5]
            tasks = []
            
            for speaker in batch:
                task = self.enrich_company(
                    speaker["company"],
                    speaker.get("name", ""),
                    speaker.get("job_title", "")
                )
                tasks.append(task)
            
            # Run batch enrichment
            batch_results = await asyncio.gather(*tasks)
            
            # Merge enrichment data with original speaker data
            for speaker, enrichment in zip(batch, batch_results):
                enriched_speaker = speaker.copy()  # Keep all original data
                enriched_speaker.update(enrichment)  # Add enrichment data
                enriched_speakers.append(enriched_speaker)
            
            # Small delay to avoid rate limiting
            if i + 5 < len(speakers):
                await asyncio.sleep(1)
        
        return enriched_speakers


# Example usage
if __name__ == "__main__":
    async def test():
        enricher = CompanyEnricher()
        test_speaker = {
            "name": "John Doe",
            "company": "Acme Construction",
            "job_title": "CEO"
        }
        result = await enricher.enrich_company(
            test_speaker["company"],
            test_speaker["name"],
            test_speaker["job_title"]
        )
        print(json.dumps(result, indent=2))
    
    asyncio.run(test())