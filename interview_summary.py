import json
import os
import numpy as np
from datetime import datetime

class InterviewSummaryGenerator:
    def __init__(self, conversation_history, pageant_info, contestant_info):
        """
        Initialize the summary generator with conversation data and context
        
        :param conversation_history: List of conversation entries
        :param pageant_info: Dictionary of pageant information
        :param contestant_info: Dictionary of contestant information
        """
        self.conversation_history = conversation_history
        self.pageant_info = pageant_info
        self.contestant_info = contestant_info
    
    def calculate_scores(self):
        """
        Generate comprehensive scoring for the interview
        
        :return: Dictionary of calculated scores
        """
        # Extract response texts
        responses = [entry['text'] for entry in self.conversation_history 
                     if entry.get('speaker', '').lower() == 'contestant']
        
        # Basic scoring metrics
        def calculate_response_quality(response):
            """
            Calculate quality score for a single response
            
            :param response: Text of the response
            :return: Quality score (0-100)
            """
            # Base score calculation
            base_score = min(len(response.split()) * 2, 100)  # More words = higher base score
            
            # Assess response depth and quality
            depth_score = 0
            if '.' in response:  # Multiple sentences
                depth_score += 10
            
            if any(keyword in response.lower() for keyword in [
                'challenge', 'improve', 'learn', 'grow', 'develop', 
                'community', 'impact', 'service', 'leadership'
            ]):
                depth_score += 15
            
            # Check for unique and meaningful content
            unique_words = len(set(response.lower().split()))
            if unique_words / len(response.split()) > 0.7:
                depth_score += 10
            
            # Combine scores
            total_score = min(base_score + depth_score, 100)
            
            return max(total_score, 50)  # Minimum score of 50
        
        # Calculate individual response scores
        response_scores = [calculate_response_quality(resp) for resp in responses]
        
        # Weighted scoring for different aspects
        overall_score = np.mean(response_scores)
        
        # Specialized scoring
        scores = {
            # Overall performance scores
            'overall_score': round(overall_score, 2),
            'presentation_score': round(overall_score * 0.95, 2),
            'content_score': round(overall_score * 0.98, 2),
            'confidence_score': round(overall_score * 0.92, 2),
            'relevance_score': round(overall_score * 0.96, 2),
            'authenticity_score': round(overall_score * 0.94, 2),
            
            # Additional specialized scores
            'technical_score': round(overall_score * 0.9, 2),
            'experience_relevance_score': round(overall_score * 0.93, 2),
            'skill_match_score': round(overall_score * 0.97, 2),
            'cultural_fit_score': round(overall_score * 0.91, 2),
            'communication_score': round(overall_score * 0.96, 2),
            
            # Percentage metrics
            'skill_match_percentage': round(overall_score, 2),
        }
        
        return scores
    
    def identify_strengths_and_improvements(self, scores):
        """
        Identify strengths and areas for improvement
        
        :param scores: Dictionary of scores
        :return: Tuple of strengths and improvement areas
        """
        # Determine strengths based on high scores
        strengths = []
        areas_for_improvement = []
        
        # Strength criteria
        strength_criteria = {
            'Exceptional Public Speaking': scores['presentation_score'] >= 85,
            'Strong Content Delivery': scores['content_score'] >= 85,
            'High Confidence': scores['confidence_score'] >= 80,
            'Excellent Relevance': scores['relevance_score'] >= 85,
            'Authentic Communication': scores['authenticity_score'] >= 85
        }
        
        # Improvement areas
        improvement_criteria = {
            'Develop More Specific Technical Knowledge': scores['technical_score'] < 75,
            'Enhance Experience Articulation': scores['experience_relevance_score'] < 75,
            'Refine Skill Demonstration': scores['skill_match_score'] < 75,
            'Improve Cultural Fit Communication': scores['cultural_fit_score'] < 75
        }
        
        # Collect strengths and improvements
        strengths = [
            strength for strength, is_strong in strength_criteria.items() 
            if is_strong
        ]
        
        areas_for_improvement = [
            improvement for improvement, needs_work in improvement_criteria.items() 
            if needs_work
        ]
        
        # Fallback if no specific strengths/improvements
        if not strengths:
            strengths = ['Potential for Growth', 'Enthusiastic Participant']
        
        if not areas_for_improvement:
            areas_for_improvement = ['Continue Developing Communication Skills']
        
        return strengths, areas_for_improvement
    
    def determine_recommendation(self, overall_score):
        """
        Determine interview recommendation based on overall score
        
        :param overall_score: Overall performance score
        :return: Recommendation string
        """
        if overall_score >= 90:
            return 'Exceptional Candidate'
        elif overall_score >= 80:
            return 'Strong Candidate'
        elif overall_score >= 70:
            return 'Promising Candidate'
        elif overall_score >= 60:
            return 'Candidate with Potential'
        else:
            return 'Needs Further Development'
    
    def generate_summary(self):
        """
        Generate comprehensive interview summary
        
        :return: Dictionary containing interview summary
        """
        # Calculate scores
        scores = self.calculate_scores()
        
        # Determine overall score
        overall_score = scores['overall_score']
        
        # Identify strengths and improvements
        strengths, areas_for_improvement = self.identify_strengths_and_improvements(scores)
        
        # Generate summary
        summary = {
            # Candidate and Pageant Info
            'candidate_name': self.contestant_info.get('name', 'Unknown Contestant'),
            'pageant_name': self.pageant_info.get('name', 'Unknown Pageant'),
            
            # Scores
            **scores,
            
            # Performance Assessment
            'recommendation': self.determine_recommendation(overall_score),
            
            # Strengths and Improvements
            'strengths': strengths,
            'areas_for_improvement': areas_for_improvement,
            
            # Additional Context
            'interview_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            
            # Notable Quotes and Notes
            'notable_quotes': self._extract_notable_quotes(),
            'notes': self._generate_additional_notes(),
        }
        
        return summary
    
    def _extract_notable_quotes(self, max_quotes=3):
        """
        Extract most impactful quotes from the conversation
        
        :param max_quotes: Maximum number of quotes to extract
        :return: List of notable quotes
        """
        # Filter contestant responses
        contestant_responses = [
            entry['text'] for entry in self.conversation_history 
            if entry.get('speaker', '').lower() == 'contestant'
        ]
        
        # Quote selection based on length and depth
        def quote_score(quote):
            score = len(quote.split())
            # Bonus for meaningful keywords
            if any(keyword in quote.lower() for keyword in [
                'impact', 'community', 'leadership', 'growth', 'develop'
            ]):
                score += 20
            return score
        
        # Sort and select top quotes
        notable_quotes = sorted(
            set(contestant_responses),  # Remove duplicates
            key=quote_score,
            reverse=True
        )[:max_quotes]
        
        return notable_quotes
    
    def _generate_additional_notes(self):
        """
        Generate additional observational notes about the interview
        
        :return: List of additional notes
        """
        notes = []
        
        # Number of questions answered
        num_responses = len([
            entry for entry in self.conversation_history 
            if entry.get('speaker', '').lower() == 'contestant'
        ])
        notes.append(f"Total responses: {num_responses}")
        
        # Response depth analysis
        response_lengths = [
            len(entry['text'].split()) for entry in self.conversation_history 
            if entry.get('speaker', '').lower() == 'contestant'
        ]
        
        avg_response_length = sum(response_lengths) / len(response_lengths) if response_lengths else 0
        
        # Engagement level notes
        if avg_response_length > 50:
            notes.append("Demonstrated high engagement with comprehensive responses")
        elif avg_response_length > 30:
            notes.append("Provided focused and concise answers")
        else:
            notes.append("Opportunities to provide more detailed responses")
        
        return notes

def save_interview_summary(interview_dir, conversation_history, pageant_info, contestant_info):
    """
    Generate and save interview summary
    
    :param interview_dir: Directory for the interview
    :param conversation_history: List of conversation entries
    :param pageant_info: Dictionary of pageant information
    :param contestant_info: Dictionary of contestant information
    :return: Generated summary dictionary
    """
    try:
        # Create summary generator
        summary_generator = InterviewSummaryGenerator(
            conversation_history, 
            pageant_info, 
            contestant_info
        )
        
        # Generate summary
        summary = summary_generator.generate_summary()
        
        # Save summary
        summary_path = os.path.join(interview_dir, 'summary.json')
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary
    except Exception as e:
        print(f"Error generating summary: {e}")
        
        # Fallback summary generation
        fallback_summary = {
            'candidate_name': contestant_info.get('name', 'Unknown Contestant'),
            'pageant_name': pageant_info.get('name', 'Unknown Pageant'),
            'overall_score': 50,
            'recommendation': 'Incomplete Interview',
            'strengths': ['Participation'],
            'areas_for_improvement': ['Complete Full Interview'],
            'notes': [f'Error generating summary: {str(e)}']
        }
        
        # Save fallback summary
        summary_path = os.path.join(interview_dir, 'summary.json')
        with open(summary_path, 'w') as f:
            json.dump(fallback_summary, f, indent=2)
        
        return fallback_summary
