import time
from typing import Dict, Any, List, Tuple
import random
import re

class ConversationManager:
    """
    Manage the pageant interview conversation flow, track state,
    and generate appropriate responses.
    """
    
    def __init__(self, pageant_info, contestant_info):
        """
        Initialize the conversation manager with pageant and contestant information.
        
        Args:
            pageant_info: Processed pageant information
            contestant_info: Processed contestant information
        """
        self.pageant_info = pageant_info
        self.contestant_info = contestant_info
        
        # Initialize with templates for different question types
        self._initialize_question_templates()
        
        # Conversation state
        self.current_question_index = 0
        self.conversation_history = []
        self.follow_up_status = False
        self.current_question_type = None
        self.current_question = None
        
        # Generated script
        self.interview_script = None
        
        # Keep track of used questions to avoid repetition
        self.used_questions = set()
        
        # Contestant response evaluation
        self.contestant_evaluation = {
            'presentation_score': 0,  # Clarity of speech, articulation, delivery
            'content_score': 0,       # Substance, depth of answers
            'confidence_score': 0,    # Self-assurance, poise
            'relevance_score': 0,     # How well answers address the questions
            'authenticity_score': 0,  # Genuineness, personal connection
            'question_count': 0,
            'notes': []
        }
        
        # Track notes on strengths and areas for improvement
        self.strengths = []
        self.areas_for_improvement = []
        
        # Create a unique interview ID
        self.interview_id = f"pageant_interview_{time.time()}"
        
        # Debug mode
        self.debug_mode = False
    
    def _initialize_question_templates(self):
        """Initialize templates for different question types."""
        # Templates for different question types (customized for pageant interviews)
        self.introduction_templates = [
            "Welcome, {contestant_name}! It's great to have you with us. To start, could you tell us a little about your journey and what motivated you to participate in this pageant?",
            "Hello, {contestant_name}, and thank you for being here. What inspired you to compete in this pageant, and how has it shaped your personal growth?",
            "Hi {contestant_name}, we're thrilled to have you today. Could you share with us your story and why you believe you're a great fit for this pageant?"
        ]
        
        self.experience_templates = [
            "You mentioned in your bio that you have experience in {activity}. Can you tell us how this experience has influenced your preparation for the pageant?",
            "Your work with {organization} is impressive! How do you think your experiences there will help you as a representative of this pageant?",
            "You've participated in several events, such as {event}. What was your most memorable experience and how did it help you grow?"
        ]
        
        self.skill_templates = [
            "You highlighted your talent in {talent}. Could you tell us about a time when this skill gave you an edge or helped you overcome a challenge?",
            "How do you continue to improve your {skill} and stay at the top of your game for pageant events?",
            "Your profile mentions {skill}. Could you walk us through a moment when this skill was essential to your success in a public setting?"
        ]
        
        self.behavioral_templates = [
            "Tell us about a challenging moment during your pageant journey. How did you handle the stress, and what did you learn from it?",
            "Describe a situation where you had to deal with a difficult contestant or judge. How did you manage the situation?",
            "Can you share an instance where you had to quickly think on your feet during an event or stage performance?"
        ]
        
        self.platform_templates = [
            "Your platform is focused on {platform}. What inspired you to choose this cause, and what specific actions have you taken to advance it?",
            "How do you plan to leverage the pageant title to further your platform of {platform}?",
            "If selected as the winner, what specific initiatives would you implement to promote {platform} in our community?"
        ]
        
        self.pageant_values_templates = [
            "Our pageant values {value}. Can you tell us how you've demonstrated this value in your life?",
            "One of our key values is {value}. How have you embodied this value throughout your journey, and how do you plan to continue doing so?",
            "We are deeply committed to {value}. Can you share an experience where you worked towards upholding this value in your community?"
        ]
        
        self.situational_templates = [
            "If you were to win the title today, how would you use the platform to influence positive change in your community?",
            "Imagine you have to speak at a major event with little preparation. How would you handle the situation?",
            "If you faced a setback during your competition, how would you keep yourself motivated to push forward?"
        ]
        
        self.world_issue_templates = [
            "What do you believe is the most significant issue facing {demographic} today, and how would you address it as a pageant winner?",
            "How do you think your generation can contribute to solving {issue}?",
            "If you had the opportunity to address world leaders about {issue}, what would be your main message?"
        ]
        
        self.closing_templates = [
            "Thank you for sharing your journey with us today, {contestant_name}. Is there anything else you'd like to share with us about your vision as a potential winner?",
            "You've given us a lot to think about today. Before we conclude, do you have any final words or questions about the competition or next steps?",
            "We're honored to have had you here today, {contestant_name}. Is there anything else you'd like to add about your goals for the future?"
        ]
        
        # Generic follow-up templates
        self.generic_follow_ups = [
            "Can you elaborate on that?",
            "That's interesting. Could you provide a specific example?",
            "How did that experience shape your perspective?",
            "What were the key lessons you learned from that?",
            "How would you apply that to your role if you win this pageant?"
        ]
        
        # Type-specific follow-up templates
        self.type_specific_follow_ups = {
            'platform': [
                "What specific initiatives would you pursue to advance this platform?",
                "How do you measure the impact of your work on this platform?",
                "How do you engage others to support your platform?",
                "What challenges have you faced in promoting your platform?",
                "How has your perspective on this platform evolved over time?"
            ],
            'experience': [
                "What was your biggest takeaway from that experience?",
                "How did that experience prepare you for this pageant?",
                "What would you do differently if you could revisit that experience?",
                "How have you applied what you learned to other aspects of your life?",
                "How did that experience influence your pageant platform?"
            ],
            'skill': [
                "How do you continue to develop this skill?",
                "How have you used this skill to benefit your community?",
                "Can you describe a situation where this skill was particularly valuable?",
                "How do you think this skill will help you as a pageant winner?",
                "How do you adapt this skill to different situations?"
            ],
            'behavioral': [
                "Looking back, what would you have done differently?",
                "How has this situation informed your approach to similar challenges?",
                "What was the most challenging aspect of that situation?",
                "How did you know your approach was successful?",
                "How did this experience change your perspective?"
            ],
            'pageant_values': [
                "How have you helped promote these values in your community?",
                "How do you see yourself embodying these values if you win?",
                "Can you share another example of how you've demonstrated this value?",
                "How do you handle situations where others don't share these values?",
                "What aspects of this value resonate with you the most?"
            ],
            'world_issue': [
                "How would you use the pageant platform to address this issue?",
                "How has this issue personally affected you or your community?",
                "What specific solutions would you advocate for?",
                "How would you engage young people in addressing this issue?",
                "How do you stay informed about developments related to this issue?"
            ]
        }
        
        # Keywords for contextual follow-ups
        self.context_keywords = {
            'challenge': "What was the biggest challenge you faced during that?",
            'community': "How has your community responded to your efforts?",
            'passion': "When did you first discover this passion?",
            'inspire': "Who has been your biggest inspiration in this journey?",
            'goal': "How do you plan to achieve that goal?",
            'volunteer': "How has volunteering shaped your perspective?",
            'impact': "How do you measure the impact of your actions?",
            'future': "What specific steps are you taking to achieve that future vision?",
            'confidence': "How do you maintain your confidence in challenging situations?",
            'role model': "How do you ensure you're being a positive role model?"
        }
    
    def _is_similar_to_used(self, question: str, threshold: float = 0.7) -> bool:
        """
        Check if a question is similar to any previously used question.
        """
        question_words = set(re.findall(r'\b\w+\b', question.lower()))
        
        for used in self.used_questions:
            used_words = set(re.findall(r'\b\w+\b', used.lower()))
            intersection = len(question_words & used_words)
            union = len(question_words | used_words)
            similarity = intersection / union if union > 0 else 0
            
            if similarity > threshold:
                return True
        
        return False
    
    def generate_interview_script(self) -> List[Dict[str, str]]:
        """
        Generate a personalized pageant interview script based on contestant profile.
        
        Returns:
            List of question dictionaries, each with a 'type' and 'question' field
        """
        script = []
        self.used_questions = set()  # Reset used questions
        
        # Add introduction
        intro_template = random.choice(self.introduction_templates)
        intro_question = intro_template.format(
            contestant_name=self.contestant_info.get('name', 'contestant')
        )
        script.append({
            'type': 'introduction',
            'question': intro_question
        })
        self.used_questions.add(intro_question)
        
        # Add experience questions
        for exp in self.contestant_info.get('experiences', [])[:2]:  # Limit to 2 experiences
            if 'activity' in exp:
                exp_template = random.choice(self.experience_templates)
                exp_question = exp_template.format(activity=exp['activity'])
                if not self._is_similar_to_used(exp_question):
                    script.append({
                        'type': 'experience',
                        'question': exp_question
                    })
                    self.used_questions.add(exp_question)
            elif 'organization' in exp:
                exp_template = random.choice(self.experience_templates)
                exp_question = exp_template.format(organization=exp['organization'])
                if not self._is_similar_to_used(exp_question):
                    script.append({
                        'type': 'experience',
                        'question': exp_question
                    })
                    self.used_questions.add(exp_question)
            elif 'event' in exp:
                exp_template = random.choice(self.experience_templates)
                exp_question = exp_template.format(event=exp['event'])
                if not self._is_similar_to_used(exp_question):
                    script.append({
                        'type': 'experience',
                        'question': exp_question
                    })
                    self.used_questions.add(exp_question)
        
        # Add skill-based questions
        for skill in self.contestant_info.get('skills', [])[:2]:  # Limit to 2 skills
            skill_template = random.choice(self.skill_templates)
            skill_question = skill_template.format(talent=skill, skill=skill)
            if not self._is_similar_to_used(skill_question):
                script.append({
                    'type': 'skill',
                    'question': skill_question
                })
                self.used_questions.add(skill_question)
        
        # Add platform questions
        if 'platform' in self.contestant_info:
            platform_template = random.choice(self.platform_templates)
            platform_question = platform_template.format(platform=self.contestant_info['platform'])
            if not self._is_similar_to_used(platform_question):
                script.append({
                    'type': 'platform',
                    'question': platform_question
                })
                self.used_questions.add(platform_question)
        
        # Add pageant values questions
        for value in self.pageant_info.get('values', [])[:2]:  # Limit to 2 values
            value_template = random.choice(self.pageant_values_templates)
            value_question = value_template.format(value=value)
            if not self._is_similar_to_used(value_question):
                script.append({
                    'type': 'pageant_values',
                    'question': value_question
                })
                self.used_questions.add(value_question)
        
        # Add behavioral questions
        for _ in range(2):  # Add 2 behavioral questions
            behavioral_template = random.choice(self.behavioral_templates)
            if not self._is_similar_to_used(behavioral_template):
                script.append({
                    'type': 'behavioral',
                    'question': behavioral_template
                })
                self.used_questions.add(behavioral_template)
        
        # Add situational questions
        for _ in range(2):  # Add 2 situational questions
            situational_template = random.choice(self.situational_templates)
            if not self._is_similar_to_used(situational_template):
                script.append({
                    'type': 'situational',
                    'question': situational_template
                })
                self.used_questions.add(situational_template)
        
        # Add world issue question
        world_issue_template = random.choice(self.world_issue_templates)
        demographic = self.contestant_info.get('demographic', 'young women')
        issue = self.pageant_info.get('current_issue', 'climate change')
        world_issue_question = world_issue_template.format(demographic=demographic, issue=issue)
        if not self._is_similar_to_used(world_issue_question):
            script.append({
                'type': 'world_issue',
                'question': world_issue_question
            })
            self.used_questions.add(world_issue_question)
        
        # Add closing question
        closing_template = random.choice(self.closing_templates)
        closing_question = closing_template.format(
            contestant_name=self.contestant_info.get('name', 'contestant')
        )
        script.append({
            'type': 'closing',
            'question': closing_question
        })
        
        # Store the script
        self.interview_script = script
        
        return script
    
    def set_interview_script(self, script):
        """
        Set the interview script directly rather than generating it.
        
        Args:
            script: List of question dictionaries
        """
        self.interview_script = script
    
    def start_interview(self) -> str:
        """
        Start the interview with the first question.
        
        Returns:
            The first question to ask the contestant
        """
        if not self.interview_script:
            # Generate the script if it doesn't exist
            self.generate_interview_script()
        
        if not self.interview_script:
            return "I don't have any questions prepared for this interview."
        
        question_data = self.interview_script[self.current_question_index]
        self.current_question_type = question_data['type']
        self.current_question = question_data['question']
        
        # Record in conversation history
        self.conversation_history.append({
            'speaker': 'interviewer',
            'text': self.current_question,
            'timestamp': time.time(),
            'question_type': self.current_question_type
        })
        
        return self.current_question
    
    def generate_follow_up_question(self, question_type: str, question: str, response: str) -> str:
        """
        Generate a follow-up question based on the question type and contestant's response.
        
        Args:
            question_type: The type of the original question
            question: The original question
            response: The contestant's response
            
        Returns:
            A follow-up question
        """
        # Choose from type-specific follow-ups if available, otherwise use generic
        if question_type in self.type_specific_follow_ups:
            follow_up_options = self.type_specific_follow_ups[question_type]
        else:
            follow_up_options = self.generic_follow_ups
            
        # Check if any keywords are in the response
        for keyword, keyword_follow_up in self.context_keywords.items():
            if keyword in response.lower():
                return keyword_follow_up
                
        # If no keywords matched, return a random follow-up
        return random.choice(follow_up_options)
    
    def process_contestant_response(self, response: str) -> Dict[str, Any]:
        """
        Process the contestant's response and determine the next question.
        
        Args:
            response: The contestant's response to the current question
            
        Returns:
            Dict with next question and interview status
        """
        # Record contestant response
        self.conversation_history.append({
            'speaker': 'contestant',
            'text': response,
            'timestamp': time.time(),
            'in_response_to': self.current_question_type
        })
        
        # Evaluate the response
        self._evaluate_response(response)
        
        # Determine if we should ask a follow-up or move to the next question
        if not self.follow_up_status and self._should_ask_follow_up(response):
            follow_up = self.generate_follow_up_question(
                self.current_question_type,
                self.current_question,
                response
            )
            
            self.follow_up_status = True
            
            # Record the follow-up in history
            self.conversation_history.append({
                'speaker': 'interviewer',
                'text': follow_up,
                'timestamp': time.time(),
                'question_type': f"{self.current_question_type}_follow_up"
            })
            
            return {
                "next_question": follow_up,
                "is_complete": False
            }
        else:
            # Reset follow-up status for next question
            self.follow_up_status = False
            
            # Check if we've reached the end of the script
            if self.current_question_index >= len(self.interview_script) - 1:
                conclusion = self._generate_interview_conclusion()
                
                # Record the conclusion in history
                self.conversation_history.append({
                    'speaker': 'interviewer',
                    'text': conclusion,
                    'timestamp': time.time(),
                    'question_type': 'conclusion'
                })
                
                return {
                    "next_question": conclusion,
                    "is_complete": True
                }
            
            # Increment question index and get the next question
            self.current_question_index += 1
            next_question_data = self.interview_script[self.current_question_index]
            self.current_question = next_question_data['question']
            self.current_question_type = next_question_data['type']
            
            # Record the next question in history
            self.conversation_history.append({
                'speaker': 'interviewer',
                'text': self.current_question,
                'timestamp': time.time(),
                'question_type': self.current_question_type
            })
            
            return {
                "next_question": self.current_question,
                "is_complete": False
            }
    
    def _should_ask_follow_up(self, response: str) -> bool:
        """
        Determine if we should ask a follow-up question based on the response.
        
        Args:
            response: The contestant's response
            
        Returns:
            Boolean indicating whether to ask a follow-up
        """
        # Skip follow-ups for introduction or closing questions
        if self.current_question_type in ['introduction', 'closing']:
            return False
        
        # Basic heuristics:
        # 1. Response length - longer responses may have more to explore
        # 2. Interesting content - check for certain keywords
        # 3. Random chance - sometimes ask, sometimes don't
        
        # Check response length (100-500 chars is a moderate length response)
        response_length = len(response)
        if response_length < 50:  # Very short response
            self.areas_for_improvement.append("Providing more detailed responses")
            return True  # Ask follow-up to get more information
        
        # Look for interesting keywords worth exploring
        interesting_keywords = [
            'passion', 'challenge', 'overcome', 'success', 'failure', 'learn',
            'community', 'impact', 'service', 'volunteer', 'experience',
            'dream', 'goal', 'aspiration', 'inspire', 'change'
        ]
        
        has_interesting_content = any(keyword in response.lower() for keyword in interesting_keywords)
        
        # Random chance (30% chance of follow-up if no other criteria met)
        random_chance = random.random() < 0.3
        
        return has_interesting_content or random_chance
    
    def _evaluate_response(self, response: str) -> None:
        """
        Evaluate the contestant's response and update evaluation scores.
        
        Args:
            response: The contestant's response to the current question
        """
        # Don't evaluate if no response or very short response
        if not response or len(response) < 10:
            return
        
        # Increment question count
        self.contestant_evaluation['question_count'] += 1
        
        # Basic response quality indicators
        response_length = len(response)
        specific_details = any(term in response.lower() for term in 
                              ['specifically', 'example', 'instance', 'case', 'event', 'situation'])
        personal_connection = any(term in response.lower() for term in 
                                 ['i felt', 'my experience', 'personally', 'i believe', 'i learned'])
        
        # Check for clarity and structure
        clear_communication = 100 < response_length < 500  # Not too short, not too verbose
        structured_response = any(term in response.lower() for term in 
                                 ['first', 'second', 'finally', 'additionally', 'however', 'therefore'])
        
        # Basic scoring for presentation (based on response structure)
        presentation_score = (
            0.4 +                        # Base score
            (clear_communication * 0.3) +  # Clear communication
            (structured_response * 0.3)    # Structured response
        )
        self.contestant_evaluation['presentation_score'] += min(1.0, presentation_score)
        
        # Content score (depth and substance)
        content_score = (
            0.3 +                         # Base score
            (specific_details * 0.4) +      # Specific details
            (0.1 if response_length > 200 else 0) +  # Length indicates depth
            (personal_connection * 0.2)     # Personal connection
        )
        self.contestant_evaluation['content_score'] += min(1.0, content_score)
        
        # Confidence score (based on language used)
        confidence_indicators = [
            'confident', 'sure', 'certainly', 'definitely', 'absolutely',
            'i know', 'i am certain', 'without doubt', 'strongly believe'
        ]
        uncertainty_indicators = [
            'maybe', 'perhaps', 'i think', 'i guess', 'sort of', 'kind of',
            'not sure', 'might be', 'possibly', 'probably'
        ]
        
        confidence_marker = sum(1 for term in confidence_indicators if term in response.lower())
        uncertainty_marker = sum(1 for term in uncertainty_indicators if term in response.lower())
        
        confidence_score = (
            0.5 +                           # Base score
            (min(0.3, confidence_marker * 0.1)) -  # Confidence indicators
            (min(0.3, uncertainty_marker * 0.1))   # Uncertainty indicators
        )
        self.contestant_evaluation['confidence_score'] += min(1.0, max(0.1, confidence_score))
        
        # Relevance score (how well the answer addresses the question)
        # This is a simplistic approach - in a real system you'd use more sophisticated NLP
        relevance_score = 0.5  # Base score assuming moderate relevance
        
        # Check for question type specific keywords
        if self.current_question_type == 'platform':
            platform_keywords = ['platform', 'cause', 'issue', 'support', 'advocate', 'change', 'impact']
            relevance_score += min(0.5, sum(0.1 for term in platform_keywords if term in response.lower()))
        elif self.current_question_type == 'world_issue':
            issue_keywords = ['issue', 'problem', 'solution', 'address', 'solve', 'change', 'impact', 'world']
            relevance_score += min(0.5, sum(0.1 for term in issue_keywords if term in response.lower()))
        elif self.current_question_type == 'pageant_values':
            # Check if any pageant values are mentioned
            values = self.pageant_info.get('values', [])
            values_mentioned = sum(1 for value in values if value.lower() in response.lower())
            relevance_score += min(0.5, values_mentioned * 0.2)
        
        self.contestant_evaluation['relevance_score'] += min(1.0, relevance_score)
        
        # Authenticity score (genuineness)
        authenticity_indicators = [
            'i feel', 'i felt', 'my experience', 'personally', 'in my life',
            'i learned', 'influenced me', 'emotional', 'meaningful', 'journey'
        ]
        
        authenticity_marker = sum(1 for term in authenticity_indicators if term in response.lower())
        
        authenticity_score = (
            0.4 +                           # Base score
            (min(0.6, authenticity_marker * 0.1))  # Authenticity indicators
        )
        self.contestant_evaluation['authenticity_score'] += min(1.0, authenticity_score)
        
        # Add specific strengths and improvements based on scores
        self._update_strengths_and_improvements(
            presentation_score,
            content_score,
            confidence_score,
            relevance_score,
            authenticity_score
        )
    
    def _update_strengths_and_improvements(self, presentation, content, confidence, relevance, authenticity):
        """
        Update strengths and areas for improvement based on scores.
        
        Args:
            presentation: Presentation score for this response
            content: Content score for this response
            confidence: Confidence score for this response
            relevance: Relevance score for this response
            authenticity: Authenticity score for this response
        """
        # Check for strengths (scores over 0.7)
        if presentation > 0.7 and "Clear and articulate communication" not in self.strengths:
            self.strengths.append("Clear and articulate communication")
        
        if content > 0.7 and "Substantial and detailed responses" not in self.strengths:
            self.strengths.append("Substantial and detailed responses")
        
        if confidence > 0.7 and "Strong confidence and poise" not in self.strengths:
            self.strengths.append("Strong confidence and poise")
        
        if relevance > 0.7 and "Excellent ability to address questions directly" not in self.strengths:
            self.strengths.append("Excellent ability to address questions directly")
        
        if authenticity > 0.7 and "Genuine and authentic communication style" not in self.strengths:
            self.strengths.append("Genuine and authentic communication style")
        
        # Check for areas of improvement (scores under 0.5)
        if presentation < 0.5 and "Improving clarity of communication" not in self.areas_for_improvement:
            self.areas_for_improvement.append("Improving clarity of communication")
        
        if content < 0.5 and "Adding more depth to responses" not in self.areas_for_improvement:
            self.areas_for_improvement.append("Adding more depth to responses")
        
        if confidence < 0.5 and "Building confidence in delivery" not in self.areas_for_improvement:
            self.areas_for_improvement.append("Building confidence in delivery")
        
        if relevance < 0.5 and "Addressing questions more directly" not in self.areas_for_improvement:
            self.areas_for_improvement.append("Addressing questions more directly")
        
        if authenticity < 0.5 and "Adding more personal connection to answers" not in self.areas_for_improvement:
            self.areas_for_improvement.append("Adding more personal connection to answers")
    
    def _generate_interview_conclusion(self) -> str:
        """
        Generate a conclusion for the interview.
        
        Returns:
            Conclusion text
        """
        contestant_name = self.contestant_info.get('name', 'there')
        pageant_name = self.pageant_info.get('name', 'this pageant')
        
        conclusion_templates = [
            f"Thank you, {contestant_name}, for taking the time to interview with us today for {pageant_name}. "
            f"We've covered a lot of ground, and I appreciate your thoughtful responses. "
            f"Our panel will review your interview and get back to you soon regarding the results. "
            f"Do you have any final thoughts or questions before we conclude?",
            
            f"That concludes the formal part of our interview, {contestant_name}. "
            f"I've enjoyed learning more about your background and how you might represent {pageant_name}. "
            f"We'll be in touch soon with the judges' feedback. "
            f"Is there anything else you'd like to share about your vision for the title?",
            
            f"We've come to the end of our scheduled time, {contestant_name}. "
            f"Thank you for sharing your experiences and insights related to {pageant_name}. "
            f"The judging panel will evaluate all contestants and announce the results shortly. "
            f"Before we end, is there anything else you'd like to add about your goals or aspirations?"
        ]
        
        return random.choice(conclusion_templates)
    
    def get_interview_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of the interview.
        
        Returns:
            Dictionary with interview summary information
        """
        # Calculate overall score (weighted average)
        weights = {
            'presentation_score': 0.25,
            'content_score': 0.25,
            'confidence_score': 0.2,
            'relevance_score': 0.15,
            'authenticity_score': 0.15
        }
        
        if self.contestant_evaluation['question_count'] == 0:
            overall_score = 0
        else:
            score_sum = 0
            for key, weight in weights.items():
                score = self.contestant_evaluation[key] / self.contestant_evaluation['question_count']
                score_sum += score * weight
            
            # Normalize to 0-100 scale
            overall_score = min(100, score_sum * 100)
        
        # Ensure we have some strengths and areas for improvement
        if not self.strengths:
            self.strengths = ["Participated fully in the interview process"]
        
        if not self.areas_for_improvement:
            self.areas_for_improvement = ["Continue developing interview skills"]
        
        # Limit to top 5 strengths and improvements
        strengths = self.strengths[:5]
        improvements = self.areas_for_improvement[:5]
        
        # Get some notable quotes from the contestant
        notable_quotes = []
        for entry in self.conversation_history:
            if entry.get('speaker') == 'contestant':
                response = entry.get('text', '')
                if len(response) > 20:
                    # Get the first sentence or first 100 chars
                    quote = response.split('.')[0]
                    if len(quote) > 100:
                        quote = quote[:97] + "..."
                    if quote and quote not in notable_quotes:
                        notable_quotes.append(quote)
                        if len(notable_quotes) >= 3:  # Limit to 3 quotes
                            break
        
        return {
            'contestant_name': self.contestant_info.get('name', 'Contestant'),
            'pageant_name': self.pageant_info.get('name', 'Pageant'),
            'interview_date': time.strftime('%Y-%m-%d'),
            'overall_score': round(overall_score, 1),
            'presentation_score': round(self.contestant_evaluation['presentation_score'] * 100 / max(1, self.contestant_evaluation['question_count']), 1),
            'content_score': round(self.contestant_evaluation['content_score'] * 100 / max(1, self.contestant_evaluation['question_count']), 1),
            'confidence_score': round(self.contestant_evaluation['confidence_score'] * 100 / max(1, self.contestant_evaluation['question_count']), 1),
            'relevance_score': round(self.contestant_evaluation['relevance_score'] * 100 / max(1, self.contestant_evaluation['question_count']), 1),
            'authenticity_score': round(self.contestant_evaluation['authenticity_score'] * 100 / max(1, self.contestant_evaluation['question_count']), 1),
            'strengths': strengths,
            'areas_for_improvement': improvements,
            'notable_quotes': notable_quotes,
            'notes': self.contestant_evaluation['notes'],
            'conversation_transcript': self.conversation_history
        }