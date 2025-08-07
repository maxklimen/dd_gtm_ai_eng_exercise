"""
Company classifier using LLM to categorize companies
"""
import os
import asyncio
from typing import Dict, List, Optional
from dotenv import load_dotenv
import json


class CompanyClassifier:
    """Classify companies into categories using LLM"""
    
    CATEGORIES = ["Builder", "Owner", "Partner", "Competitor", "Customer", "Other"]
    
    def __init__(self):
        load_dotenv()
        self.llm_client = self._init_llm_client()
    
    def _init_llm_client(self):
        """Initialize LLM client based on available API keys"""
        if os.getenv("OPENAI_API_KEY"):
            from openai import OpenAI
            return OpenAI()
        elif os.getenv("ANTHROPIC_API_KEY"):
            from anthropic import Anthropic
            return Anthropic()
        else:
            raise ValueError("No LLM API key found. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY")
    
    def _create_classification_prompt(self, enriched_data: Dict) -> str:
        """Create prompt for classification"""
        company = enriched_data.get("company", "Unknown Company")
        job_title = enriched_data.get("job_title", "")
        search_results = enriched_data.get("search_results", [])
        
        # Compile search results into context
        context = f"Company: {company}\nSpeaker Job Title: {job_title}\n\n"
        context += "Search Results:\n"
        for i, result in enumerate(search_results[:3]):  # Use top 3 results
            context += f"{i+1}. {result.get('title', '')}\n{result.get('content', '')[:200]}...\n\n"
        
        prompt = f"""Based on the following information about a company, classify it into one of these categories:

1. Builder - Construction companies, general contractors, specialty contractors, engineering firms that PHYSICALLY BUILD projects. Examples: Multiplex, Laing O'Rourke, Turner Construction, AECOM (construction division)
2. Owner - Property owners, developers, real estate companies, government agencies that COMMISSION/OWN construction projects
3. Partner - Software companies, technology vendors, consultants that don't build but provide tools/services. Examples: Autodesk, Trimble, Oracle, Microsoft
4. Competitor - Companies offering drone services, aerial imagery, or competing construction tech (Propeller, Pix4D, Skycatch)
5. Customer - EXISTING DroneDeploy customers (look for mentions of "partnership with DroneDeploy", "uses DroneDeploy", "DroneDeploy customer")
6. Other - Doesn't fit clearly into above categories

{context}

IMPORTANT: 
- If search results mention the company has a partnership with DroneDeploy or uses DroneDeploy, classify as CUSTOMER
- If the company name contains "Construction", "Contractors", "Engineering" they are likely a BUILDER (unless they're already a DroneDeploy customer)
- Kier Group is a known DroneDeploy customer (enterprise agreement mentioned)

DroneDeploy provides drone-based reality capture and aerial data analytics for construction sites.

Provide your classification in the following JSON format:
{{
    "category": "Builder|Owner|Partner|Competitor|Other",
    "reasoning": "Brief explanation for the classification",
    "confidence": 0.0-1.0
}}"""
        
        return prompt
    
    async def classify_company(self, enriched_data: Dict) -> Dict:
        """
        Classify a single company
        
        Returns:
            Dictionary with category, reasoning, and confidence
        """
        prompt = self._create_classification_prompt(enriched_data)
        
        try:
            if hasattr(self.llm_client, 'chat'):  # OpenAI
                response = self.llm_client.chat.completions.create(
                    model="gpt-4.1-mini-2025-04-14",
                    messages=[
                        {"role": "system", "content": "You are an expert at classifying companies in the construction industry."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                result = json.loads(response.choices[0].message.content)
            else:  # Anthropic
                response = self.llm_client.messages.create(
                    model="claude-sonnet-4-20250514",
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )
                # Parse JSON from response
                content = response.content[0].text
                # Extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = {"category": "Other", "reasoning": "Failed to parse response", "confidence": 0.0}
            
            # Validate category
            if result.get("category") not in self.CATEGORIES:
                result["category"] = "Other"
            
            return result
            
        except Exception as e:
            print(f"Error classifying {enriched_data.get('company', 'Unknown')}: {e}")
            return {
                "category": "Other",
                "reasoning": f"Classification failed: {str(e)}",
                "confidence": 0.0
            }
    
    async def classify_batch(self, enriched_speakers: List[Dict], batch_size: int = 5) -> List[Dict]:
        """
        Classify multiple companies in parallel batches
        
        Args:
            enriched_speakers: List of enriched speaker data
            batch_size: Number of concurrent classifications (default 5)
        
        Returns:
            List of speakers with classification added
        """
        classified_speakers = []
        total = len(enriched_speakers)
        
        # Process in batches for better performance
        for i in range(0, total, batch_size):
            batch = enriched_speakers[i:i+batch_size]
            
            # Create classification tasks for parallel execution
            tasks = []
            for speaker_data in batch:
                tasks.append(self.classify_company(speaker_data))
            
            # Run classifications in parallel
            classifications = await asyncio.gather(*tasks)
            
            # Merge classification results with speaker data
            for speaker_data, classification in zip(batch, classifications):
                speaker_data["category"] = classification["category"]
                speaker_data["classification_reasoning"] = classification["reasoning"]
                speaker_data["classification_confidence"] = classification["confidence"]
                
                classified_speakers.append(speaker_data)
                
                print(f"[{len(classified_speakers)}/{total}] Classified {speaker_data['company']} as {classification['category']} "
                      f"(confidence: {classification['confidence']:.2f})")
            
            # Small delay between batches to avoid rate limiting
            if i + batch_size < total:
                await asyncio.sleep(0.5)
        
        return classified_speakers


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test():
        classifier = CompanyClassifier()
        test_data = {
            "company": "Turner Construction",
            "job_title": "VP of Innovation",
            "search_results": [
                {
                    "title": "Turner Construction - Leading General Contractor",
                    "content": "Turner Construction is one of the largest construction companies in the US..."
                }
            ]
        }
        result = await classifier.classify_company(test_data)
        print(json.dumps(result, indent=2))
    
    asyncio.run(test())