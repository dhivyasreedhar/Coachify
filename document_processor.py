
import re
from typing import Dict, List, Any

class DocumentProcessor:
    """
    Process pageant profiles and contestant biographies to extract relevant information
    for generating personalized pageant interview questions.
    """
    
    def __init__(self):
        pass
        
    def process_pageant_profile(self, pageant_profile: str) -> Dict[str, Any]:
        """
        Extract structured information from a pageant profile.
        
        Args:
            pageant_profile: Raw text of the pageant profile
            
        Returns:
            Dictionary with extracted pageant information
        """
        # Extract pageant name
        name_match = re.search(r'(Name|Title):\s*(.*?)(?:\n|$)', pageant_profile, re.IGNORECASE)
        name = name_match.group(2).strip() if name_match else ""
        
        # Extract pageant mission
        mission_match = re.search(r'Mission:?\s*(.*?)(?:\n\n|\n[A-Z]|$)', pageant_profile, re.IGNORECASE | re.DOTALL)
        mission = mission_match.group(1).strip() if mission_match else ""
        
        # Extract pageant values
        values_match = re.search(r'(?:Core\s*)?Values:?\s*(.*?)(?:\n\n|\n[A-Z]|$)', pageant_profile, re.IGNORECASE | re.DOTALL)
        values_text = values_match.group(1).strip() if values_match else ""
        values = [v.strip() for v in re.split(r'[,•\n]', values_text) if v.strip()]
        
        # Extract focus areas
        focus_match = re.search(r'(?:Focus\s*Areas|Causes):?\s*(.*?)(?:\n\n|\n[A-Z]|$)', pageant_profile, re.IGNORECASE | re.DOTALL)
        focus_text = focus_match.group(1).strip() if focus_match else ""
        focus_areas = [f.strip() for f in re.split(r'[,•\n]', focus_text) if f.strip()]
        
        # Extract history
        history_match = re.search(r'History:?\s*(.*?)(?:\n\n|\n[A-Z]|$)', pageant_profile, re.IGNORECASE | re.DOTALL)
        history = history_match.group(1).strip() if history_match else ""
        
        # Extract requirements
        req_match = re.search(r'Requirements:?\s*(.*?)(?:\n\n|\n[A-Z]|$)', pageant_profile, re.IGNORECASE | re.DOTALL)
        req_text = req_match.group(1).strip() if req_match else ""
        requirements = [r.strip() for r in re.split(r'[•\n]', req_text) if r.strip()]
        
        return {
            "name": name,
            "mission": mission,
            "values": values,
            "focus_areas": focus_areas,
            "history": history,
            "requirements": requirements,
            "raw_text": pageant_profile
        }
    
    def process_contestant_profile(self, contestant_profile: str) -> Dict[str, Any]:
        """
        Extract structured information from a contestant profile.
        
        Args:
            contestant_profile: Raw text of the contestant's profile
            
        Returns:
            Dictionary with extracted contestant information
        """
        # Extract contestant name
        name_match = re.search(r'(Name):\s*(.*?)(?:\n|$)', contestant_profile, re.IGNORECASE)
        name = name_match.group(2).strip() if name_match else ""
        
        # Extract age
        age_match = re.search(r'Age:\s*(\d+)', contestant_profile, re.IGNORECASE)
        age = int(age_match.group(1)) if age_match else 0
        
        # Extract hometown
        hometown_match = re.search(r'Hometown:\s*(.*?)(?:\n|$)', contestant_profile, re.IGNORECASE)
        hometown = hometown_match.group(1).strip() if hometown_match else ""
        
        # Extract education
        education_match = re.search(r'Education:\s*(.*?)(?:\n\n|\n[A-Z]|$)', contestant_profile, re.IGNORECASE | re.DOTALL)
        education = education_match.group(1).strip() if education_match else ""
        
        # Extract platform
        platform_match = re.search(r'Platform:\s*(.*?)(?:\n|$)', contestant_profile, re.IGNORECASE)
        platform = platform_match.group(1).strip() if platform_match else ""
        
        # Extract talents
        talents_match = re.search(r'Talents?:\s*(.*?)(?:\n\n|\n[A-Z]|$)', contestant_profile, re.IGNORECASE | re.DOTALL)
        talents_text = talents_match.group(1).strip() if talents_match else ""
        talents = [t.strip() for t in re.split(r'[,•\n]', talents_text) if t.strip()]
        
        # Extract experiences
        experiences = []
        
        # Look for various types of experiences
        community_match = re.search(r'Community( Service)?:\s*(.*?)(?:\n\n|\n[A-Z]|$)', contestant_profile, re.IGNORECASE | re.DOTALL)
        if community_match:
            community_text = community_match.group(2).strip()
            community_items = [item.strip() for item in re.split(r'[•\n]', community_text) if item.strip()]
            for item in community_items:
                experiences.append({"activity": item, "type": "community_service"})
        
        activities_match = re.search(r'Activities:\s*(.*?)(?:\n\n|\n[A-Z]|$)', contestant_profile, re.IGNORECASE | re.DOTALL)
        if activities_match:
            activities_text = activities_match.group(1).strip()
            activity_items = [item.strip() for item in re.split(r'[•\n]', activities_text) if item.strip()]
            for item in activity_items:
                experiences.append({"activity": item, "type": "activity"})
        
        leadership_match = re.search(r'Leadership:\s*(.*?)(?:\n\n|\n[A-Z]|$)', contestant_profile, re.IGNORECASE | re.DOTALL)
        if leadership_match:
            leadership_text = leadership_match.group(1).strip()
            leadership_items = [item.strip() for item in re.split(r'[•\n]', leadership_text) if item.strip()]
            for item in leadership_items:
                experiences.append({"activity": item, "type": "leadership"})
        
        achievements_match = re.search(r'Achievements:\s*(.*?)(?:\n\n|\n[A-Z]|$)', contestant_profile, re.IGNORECASE | re.DOTALL)
        if achievements_match:
            achievements_text = achievements_match.group(1).strip() 
            achievement_items = [item.strip() for item in re.split(r'[•\n]', achievements_text) if item.strip()]
            for item in achievement_items:
                experiences.append({"activity": item, "type": "achievement"})
        
        # Extract bio/personal statement
        bio_match = re.search(r'(?:Bio|Personal Statement|About):\s*(.*?)(?:\n\n|\n[A-Z]|$)', contestant_profile, re.IGNORECASE | re.DOTALL)
        bio = bio_match.group(1).strip() if bio_match else ""
        
        # Extract goals
        goals_match = re.search(r'Goals:\s*(.*?)(?:\n\n|\n[A-Z]|$)', contestant_profile, re.IGNORECASE | re.DOTALL)
        goals_text = goals_match.group(1).strip() if goals_match else ""
        goals = [g.strip() for g in re.split(r'[•\n]', goals_text) if g.strip()]
        
        return {
            "name": name,
            "age": age,
            "hometown": hometown,
            "education": education,
            "platform": platform,
            "talents": talents,
            "experiences": experiences,
            "bio": bio,
            "goals": goals,
            "raw_text": contestant_profile
        }
    
    def analyze_contestant_pageant_match(self, pageant_info: Dict[str, Any], contestant_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze how well the contestant matches the pageant's values and requirements.
        
        Args:
            pageant_info: Extracted pageant profile information
            contestant_info: Extracted contestant profile information
            
        Returns:
            Dictionary with match analysis
        """
        # Check if contestant's platform aligns with pageant focus areas
        platform_alignment = 0
        if contestant_info.get('platform'):
            for focus in pageant_info.get('focus_areas', []):
                if any(word.lower() in contestant_info['platform'].lower() for word in focus.split()):
                    platform_alignment += 1
        
        platform_alignment_score = min(100, (platform_alignment / max(len(pageant_info.get('focus_areas', [])), 1)) * 100)
        
        # Extract key themes from both profiles
        pageant_keywords = self._extract_keywords(pageant_info.get('raw_text', ''))
        contestant_keywords = self._extract_keywords(contestant_info.get('raw_text', ''))
        
        # Find matching themes
        common_keywords = set(pageant_keywords) & set(contestant_keywords)
        
        # Calculate overall match percentage
        values_match = len(common_keywords) / max(len(pageant_keywords), 1) * 50 + platform_alignment_score * 0.5
        
        return {
            "platform_alignment_score": platform_alignment_score,
            "values_match_percentage": min(100, values_match),
            "common_themes": list(common_keywords),
            "platform_strengths": self._identify_platform_strengths(contestant_info, pageant_info),
            "development_areas": self._identify_development_areas(contestant_info, pageant_info)
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords and themes from text."""
        important_themes = [
            'leadership', 'community', 'service', 'education', 'confidence', 
            'empowerment', 'advocacy', 'charity', 'volunteering', 'mentorship',
            'public speaking', 'talent', 'poise', 'grace', 'determination',
            'perseverance', 'diversity', 'inclusion', 'social impact', 'outreach',
            'inspiration', 'role model', 'ambition', 'achievement', 'excellence'
        ]
        
        found_themes = [theme for theme in important_themes if theme in text.lower()]
        return found_themes
    
    def _identify_platform_strengths(self, contestant_info: Dict[str, Any], pageant_info: Dict[str, Any]) -> List[str]:
        """Identify strengths of the contestant's platform in relation to the pageant."""
        strengths = []
        
        # Check if platform is mentioned
        if contestant_info.get('platform'):
            platform = contestant_info['platform'].lower()
            
            # Check alignment with pageant focus areas
            for focus in pageant_info.get('focus_areas', []):
                if any(word.lower() in platform for word in focus.split()):
                    strengths.append(f"Platform aligns with pageant focus area: {focus}")
            
            # Check experiences relevant to platform
            platform_related_experiences = []
            for exp in contestant_info.get('experiences', []):
                if 'activity' in exp and any(word in exp['activity'].lower() for word in platform.split()):
                    platform_related_experiences.append(exp['activity'])
            
            if platform_related_experiences:
                strengths.append(f"Has {len(platform_related_experiences)} experiences related to platform")
        
        return strengths
    
    def _identify_development_areas(self, contestant_info: Dict[str, Any], pageant_info: Dict[str, Any]) -> List[str]:
        """Identify areas for development based on pageant requirements."""
        development_areas = []
        
        # Check if platform is missing
        if not contestant_info.get('platform'):
            development_areas.append("Develop a clear platform aligned with pageant values")
        
        # Check for community service
        has_community_service = False
        for exp in contestant_info.get('experiences', []):
            if exp.get('type') == 'community_service':
                has_community_service = True
                break
        
        if not has_community_service:
            development_areas.append("Strengthen community service involvement")
        
        # Check for leadership experience
        has_leadership = False
        for exp in contestant_info.get('experiences', []):
            if exp.get('type') == 'leadership':
                has_leadership = True
                break
        
        if not has_leadership:
            development_areas.append("Develop leadership experience")
        
        return development_areas