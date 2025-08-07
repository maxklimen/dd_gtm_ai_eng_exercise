"""
Email generator for personalized outreach to conference speakers
"""
import os
from typing import Dict, List
from dotenv import load_dotenv
import json


class EmailGenerator:
    """Generate personalized emails based on company category and speaker info"""
    
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
    
    def _create_email_prompt(self, speaker_data: Dict) -> str:
        """Create prompt for email generation with session awareness"""
        name = speaker_data["name"]
        company = speaker_data["company"]
        job_title = speaker_data["job_title"]
        category = speaker_data["category"]
        sessions = speaker_data.get("sessions", [])
        
        # Category-specific messaging
        category_messaging = {
            "Builder": "As a construction professional, you understand the challenges of managing complex projects, ensuring safety, and delivering on time and budget. DroneDeploy helps contractors like you capture real-time site progress, identify issues early, and improve communication with stakeholders.",
            "Owner": "As someone overseeing construction projects, you need visibility into progress, budget tracking, and quality assurance. DroneDeploy provides owners with unprecedented transparency into their projects through regular aerial captures and AI-powered insights."
        }
        
        context = category_messaging.get(category, "DroneDeploy's construction solutions help organizations capture, analyze, and share reality data from their job sites.")
        
        # Build session context
        session_context = ""
        if sessions:
            if len(sessions) == 1:
                session_context = f"\n- Speaking session: {sessions[0]['title']}"
            elif len(sessions) > 1:
                session_context = f"\n- Speaking at {len(sessions)} sessions including: {sessions[0]['title']}"
        
        prompt = f"""Generate a personalized email to invite a conference speaker to visit our booth #42 at Digital Construction Week.

Speaker Information:
- Name: {name}
- Company: {company}
- Job Title: {job_title}
- Category: {category}{session_context}

Context: {context}

Requirements:
- Subject line should be compelling and relevant to their role/company
- Email body should be 3-4 sentences
- If they have sessions, reference their talk(s) naturally
- Mention booth #42 and free gift
- Professional but engaging tone
- Focus on specific value for their role/company type
- Include a clear call to action

Provide the email in the following JSON format:
{{
    "subject": "Email subject line",
    "body": "Email body text"
}}"""
        
        return prompt
    
    async def generate_email(self, speaker_data: Dict) -> Dict:
        """
        Generate personalized email for a speaker
        
        Returns:
            Dictionary with subject and body
        """
        # Skip competitors and partners
        if speaker_data["category"] in ["Competitor", "Partner"]:
            return {
                "subject": "",
                "body": ""
            }
        
        prompt = self._create_email_prompt(speaker_data)
        
        try:
            if hasattr(self.llm_client, 'chat'):  # OpenAI
                response = self.llm_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": "You are an expert at writing compelling B2B outreach emails for the construction technology industry."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    response_format={"type": "json_object"}
                )
                result = json.loads(response.choices[0].message.content)
            else:  # Anthropic
                response = self.llm_client.messages.create(
                    model="claude-3-opus-20240229",
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                # Parse JSON from response
                content = response.content[0].text
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = {"subject": "", "body": ""}
            
            return result
            
        except Exception as e:
            print(f"Error generating email for {speaker_data.get('name', 'Unknown')}: {e}")
            return {
                "subject": "",
                "body": ""
            }
    
    async def generate_emails_batch(self, classified_speakers: List[Dict]) -> List[Dict]:
        """
        Generate emails for multiple speakers
        
        Returns:
            List of speakers with email subject and body added
        """
        speakers_with_emails = []
        
        for speaker_data in classified_speakers:
            email = await self.generate_email(speaker_data)
            
            # Add email to speaker data
            speaker_data["email_subject"] = email["subject"]
            speaker_data["email_body"] = email["body"]
            
            speakers_with_emails.append(speaker_data)
            
            if email["subject"]:  # Only log if email was generated
                print(f"Generated email for {speaker_data['name']} at {speaker_data['company']}")
        
        return speakers_with_emails


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test():
        generator = EmailGenerator()
        test_speaker = {
            "name": "Jane Smith",
            "company": "ABC Construction",
            "job_title": "VP of Operations",
            "category": "Builder"
        }
        result = await generator.generate_email(test_speaker)
        print(json.dumps(result, indent=2))
    
    asyncio.run(test())