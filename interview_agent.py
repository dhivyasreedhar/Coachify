import os
import json
import time
import datetime
from typing import Dict, Any, Optional, List, Tuple
import uuid
import csv
import random

class InterviewAgent:
    """
    Main Pageant Interview Agent that coordinates the entire pageant interview process.
    """
    
    def __init__(self):
        # Store processed documents
        self.pageant_info = None
        self.contestant_info = None
        self.conversation_manager = None
        
        # Interview state
        self.interview_in_progress = False
        self.interview_complete = False
        self.interview_summary = None
        self.interview_id = str(uuid.uuid4())  # Generate ID at initialization
        
        # Interview timing
        self.interview_start_time = None
        self.interview_end_time = None
        self.interview_duration = None
        self.interview_max_duration = None  # In minutes
        
        # Debugging mode
        self.debug_mode = True  # Set to True to enable more verbose logging
        
        # Make sure reports directory exists
        os.makedirs('data/reports', exist_ok=True)
    
    def enable_debug_mode(self):
        """Enable debugging mode for more verbose output"""
        self.debug_mode = True
        print("Debug mode enabled")
    
    def load_pageant_profile(self, pageant_profile_text: str) -> Dict[str, Any]:
        """
        Load and process a pageant profile.
        
        Args:
            pageant_profile_text: Raw text of the pageant profile
            
        Returns:
            Processed pageant information
        """
        if self.debug_mode:
            print(f"Processing pageant profile: {len(pageant_profile_text)} characters")
            print(f"Raw pageant profile text: {pageant_profile_text[:200]}...")
        
        # Simple processing of pageant profile
        lines = pageant_profile_text.strip().split('\n')
        pageant_info = {}
        
        # Process line by line
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key, value = parts
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip()
                    
                    if self.debug_mode:
                        print(f"Found key-value pair: {key} = {value}")
                    
                    if key in ['values', 'core_values']:
                        values = [v.strip() for v in value.split(',')]
                        pageant_info['values'] = values
                        if self.debug_mode:
                            print(f"Parsed values: {values}")
                    elif key == 'current_issues' or key == 'focus_issues':
                        issues = [i.strip() for i in value.split(',')]
                        pageant_info['current_issues'] = issues
                        if issues:
                            pageant_info['current_issue'] = issues[0]
                            if self.debug_mode:
                                print(f"Set current issue to: {issues[0]}")
                    else:
                        pageant_info[key] = value
        
        # Make sure we have at least a name
        if 'name' not in pageant_info:
            if self.debug_mode:
                print("Warning: No pageant name found, setting default")
            pageant_info['name'] = "Pageant"
            
        # If no values were found, add a default
        if 'values' not in pageant_info:
            if self.debug_mode:
                print("Warning: No values found, setting defaults")
            pageant_info['values'] = ["leadership", "service", "excellence"]
            
        # If no current issue is set, add a default
        if 'current_issue' not in pageant_info:
            if self.debug_mode:
                print("Warning: No current issue found, setting default")
            pageant_info['current_issue'] = "community service"
            pageant_info['current_issues'] = ["community service"]
        
        self.pageant_info = pageant_info
        
        if self.debug_mode:
            print(f"Extracted pageant name: {self.pageant_info.get('name', 'Unknown')}")
            print(f"Identified {len(self.pageant_info.get('values', []))} core values")
            print(f"Final pageant info: {self.pageant_info}")
            
        return self.pageant_info
    
    def load_contestant_profile(self, contestant_profile_text: str) -> Dict[str, Any]:
        """
        Load and process a contestant profile.
        
        Args:
            contestant_profile_text: Raw text of the contestant's profile
            
        Returns:
            Processed contestant information
        """
        if self.debug_mode:
            print(f"Processing contestant profile: {len(contestant_profile_text)} characters")
            print(f"Raw contestant profile text: {contestant_profile_text[:200]}...")
        
        # Simple processing of contestant profile
        lines = contestant_profile_text.strip().split('\n')
        contestant_info = {}
        
        # Initialize arrays for multi-value fields
        contestant_info['experiences'] = []
        contestant_info['skills'] = []
        
        current_section = 'general'
        
        # Process line by line
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a section header
            if line.endswith(':'):
                # This is a section header
                current_section = line[:-1].lower().replace(' ', '_')
                contestant_info[current_section] = []
                if self.debug_mode:
                    print(f"Found section header: {current_section}")
                continue
                
            # Check if this is a key-value pair
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key, value = parts
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip()
                    
                    if self.debug_mode:
                        print(f"Found key-value pair: {key} = {value}")
                    
                    if key in ['skills', 'talents']:
                        skills = [s.strip() for s in value.split(',')]
                        contestant_info['skills'].extend(skills)
                        if self.debug_mode:
                            print(f"Added skills: {skills}")
                    elif key in ['experience', 'experiences', 'activities']:
                        experiences = [{'activity': e.strip()} for e in value.split(',')]
                        contestant_info['experiences'].extend(experiences)
                        if self.debug_mode:
                            print(f"Added experiences: {experiences}")
                    elif key == 'platform':
                        contestant_info['platform'] = value
                    else:
                        contestant_info[key] = value
            elif current_section in contestant_info:
                # Add to the current section if it exists
                contestant_info[current_section].append(line)
                if self.debug_mode:
                    print(f"Added to section {current_section}: {line}")
        
        # Make sure we have a name
        if 'name' not in contestant_info:
            if self.debug_mode:
                print("Warning: No contestant name found, setting default")
            contestant_info['name'] = "Contestant"
            
        # If no platform is set, add a default based on available info
        if 'platform' not in contestant_info and contestant_info.get('experiences'):
            platform_hint = contestant_info['experiences'][0].get('activity', '')
            if platform_hint:
                contestant_info['platform'] = f"Advocacy for {platform_hint}"
                if self.debug_mode:
                    print(f"Generated default platform: {contestant_info['platform']}")
        
        # If no demographic is set, add a default
        if 'demographic' not in contestant_info:
            contestant_info['demographic'] = "young women"
            if self.debug_mode:
                print("Added default demographic: young women")
            
        # If no skills were found, add some defaults
        if not contestant_info['skills']:
            contestant_info['skills'] = ["public speaking", "leadership", "community service"]
            if self.debug_mode:
                print("Added default skills")
        
        self.contestant_info = contestant_info
        
        if self.debug_mode:
            print(f"Extracted contestant name: {self.contestant_info.get('name', 'Unknown')}")
            print(f"Identified {len(self.contestant_info.get('skills', []))} skills")
            print(f"Extracted {len(self.contestant_info.get('experiences', []))} experiences")
            print(f"Final contestant info: {self.contestant_info}")
            
        return self.contestant_info
    
    def set_conversation_manager(self, conversation_manager):
        """
        Set the conversation manager to use for the interview.
        
        Args:
            conversation_manager: An instance of a conversation manager
        """
        self.conversation_manager = conversation_manager
    
    def set_interview_duration(self, max_minutes: int) -> None:
        """
        Set the maximum duration for the interview in minutes.
        
        Args:
            max_minutes: Maximum interview duration in minutes
        """
        if max_minutes <= 0:
            raise ValueError("Interview duration must be positive")
            
        self.interview_max_duration = max_minutes
        
        if self.debug_mode:
            print(f"Interview duration set to {max_minutes} minutes")
    
    def start_interview(self) -> str:
        """
        Start the interview process.
        
        Returns:
            The first interview question
        """
        if not self.pageant_info or not self.contestant_info:
            raise ValueError("Both pageant profile and contestant profile must be loaded before starting an interview.")
        
        if not self.conversation_manager:
            raise ValueError("Conversation manager must be set before starting an interview.")
        
        if self.debug_mode:
            print("Starting interview...")
            print(f"Pageant info: {self.pageant_info}")
            print(f"Contestant info: {self.contestant_info}")
        
        # Generate unique interview ID if not already set
        if not self.interview_id:
            self.interview_id = str(uuid.uuid4())
            
        # Record start time
        self.interview_start_time = time.time()
        
        self.interview_in_progress = True
        self.interview_complete = False
        
        first_question = self.conversation_manager.start_interview()
        
        if self.debug_mode:
            print(f"First question: {first_question}")
            print(f"Interview started at: {datetime.datetime.fromtimestamp(self.interview_start_time).strftime('%Y-%m-%d %H:%M:%S')}")
            if self.interview_max_duration:
                print(f"Time limit: {self.interview_max_duration} minutes")
            
        return first_question
    
    def check_time_limit(self) -> Tuple[bool, int]:
        """
        Check if the interview has exceeded its time limit.
        
        Returns:
            Tuple of (time_exceeded, remaining_seconds)
        """
        if not self.interview_in_progress or not self.interview_max_duration or not self.interview_start_time:
            return False, None
            
        elapsed_seconds = time.time() - self.interview_start_time
        elapsed_minutes = elapsed_seconds / 60
        
        remaining_seconds = max(0, (self.interview_max_duration * 60) - elapsed_seconds)
        
        if elapsed_minutes >= self.interview_max_duration:
            return True, 0
        else:
            return False, int(remaining_seconds)
    
    def process_contestant_response(self, response: str) -> Dict[str, Any]:
        """
        Process the contestant's response and get the next question.
        
        Args:
            response: The contestant's response
                
        Returns:
            Dictionary with next question, interview status, and remaining time
        """
        if not self.interview_in_progress:
            raise ValueError("Interview is not in progress.")
    
        if self.debug_mode:
            print(f"Processing contestant response: {response[:50]}...")
        
        # Initial check if we've exceeded the time limit
        time_exceeded, remaining_seconds = self.check_time_limit()
        if time_exceeded:
            self.interview_in_progress = False
            self.interview_complete = True
            self.interview_end_time = time.time()
            self.interview_duration = self.interview_end_time - self.interview_start_time
            
            # Generate a time-exceeded conclusion
            conclusion = self._generate_time_exceeded_conclusion()
            
            # Get interview summary
            self.interview_summary = self.conversation_manager.get_interview_summary()
            
            # Save the report automatically
            self.save_interview_report()
            
            if self.debug_mode:
                print("Interview completed due to time limit (initial check)")
                print(f"Duration: {self.interview_duration/60:.1f} minutes")
                
            return {
                "next_question": conclusion,
                "is_complete": True,
                "remaining_seconds": 0,
                "time_limit_exceeded": True
            }
            
        # Process the response normally
        conversation_result = self.conversation_manager.process_contestant_response(response)
        
        # Extract next question and completion status
        next_question = conversation_result.get('next_question')
        is_complete = conversation_result.get('is_complete', False)
        
        # Second time check - in case we exceeded the time limit during processing
        time_exceeded, remaining_seconds = self.check_time_limit()
        
        if time_exceeded:
            # Time ran out during processing
            self.interview_in_progress = False
            self.interview_complete = True
            self.interview_end_time = time.time()
            self.interview_duration = self.interview_end_time - self.interview_start_time
            
            # Generate a time-exceeded conclusion
            conclusion = self._generate_time_exceeded_conclusion()
            
            # Get interview summary
            self.interview_summary = self.conversation_manager.get_interview_summary()
            
            # Save the report automatically
            self.save_interview_report()
            
            if self.debug_mode:
                print("Interview completed due to time limit (second check)")
                print(f"Duration: {self.interview_duration/60:.1f} minutes")
                
            return {
                "next_question": conclusion,
                "is_complete": True,
                "remaining_seconds": 0,
                "time_limit_exceeded": True
            }
        
        # Normal completion check
        if is_complete:
            self.interview_in_progress = False
            self.interview_complete = True
            self.interview_end_time = time.time()
            self.interview_duration = self.interview_end_time - self.interview_start_time
            self.interview_summary = self.conversation_manager.get_interview_summary()
            
            # Save the report automatically
            self.save_interview_report()
            
            if self.debug_mode:
                print("Interview complete (normal completion)")
                print(f"Duration: {self.interview_duration/60:.1f} minutes")
                print(f"Overall score: {self.interview_summary.get('overall_score', 0):.1f}")
        else:
            if self.debug_mode:
                print(f"Next question: {next_question}")
                if self.interview_max_duration:
                    print(f"Remaining time: {remaining_seconds//60} minutes, {remaining_seconds%60} seconds")
        
        return {
            "next_question": next_question,
            "is_complete": is_complete,
            "remaining_seconds": remaining_seconds if self.interview_max_duration else None,
            "time_limit_exceeded": False
        }
    
    def _generate_time_exceeded_conclusion(self) -> str:
        """
        Generate a conclusion message when the interview time is exceeded.
        
        Returns:
            Conclusion message
        """
        contestant_name = self.contestant_info.get('name', 'there')
        pageant_name = self.pageant_info.get('name', 'this pageant')
        
        return (
            f"I see we've reached the end of our allocated time for this interview, {contestant_name}. "
            f"Thank you for sharing your experiences and insights for {pageant_name}. "
            f"Although we couldn't get through all our questions, I've gathered valuable information about your background and talents. "
            f"Our panel will review your interview and get back to you soon regarding next steps. "
            f"Do you have any brief final thoughts before we conclude?"
        )
    
    def get_interview_summary(self) -> Dict[str, Any]:
        """
        Get the interview summary.
        
        Returns:
            Interview summary information
        """
        if not self.interview_complete:
            raise ValueError("Interview is not complete.")
        
        # Add timing information to the summary
        if self.interview_summary and self.interview_start_time and self.interview_end_time:
            self.interview_summary['interview_start_time'] = self.interview_start_time
            self.interview_summary['interview_end_time'] = self.interview_end_time
            self.interview_summary['interview_duration_seconds'] = self.interview_duration
            self.interview_summary['interview_duration_minutes'] = self.interview_duration / 60
            
        return self.interview_summary
    
    def save_interview_report(self) -> str:
        """
        Save the interview report to file.
        
        Returns:
            Path to the saved report file
        """
        if not self.interview_complete or not self.interview_summary:
            raise ValueError("Interview is not complete.")
            
        # Ensure we have an interview ID
        if not self.interview_id:
            self.interview_id = str(uuid.uuid4())
            
        # Create reports directory if it doesn't exist
        os.makedirs('data/reports', exist_ok=True)
            
        # Create a filename with date and contestant name
        contestant_name = self.contestant_info.get('name', 'Unknown').replace(' ', '_')
        pageant_name = self.pageant_info.get('name', 'Unknown').replace(' ', '_')
        date_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # JSON report with full details
        json_filename = f"data/reports/{date_str}_{contestant_name}_{pageant_name}_{self.interview_id}.json"
        
        with open(json_filename, 'w') as f:
            json.dump(self.interview_summary, f, indent=2)
            
        # CSV summary for easy tracking
        self._update_summary_csv()
        
        if self.debug_mode:
            print(f"Interview report saved to {json_filename}")
            print(f"Summary updated in reports_summary.csv")
            
        return json_filename
    
    def _update_summary_csv(self) -> None:
        """Update the CSV summary file with this interview"""
        csv_file = "data/reports/pageant_reports_summary.csv"
        file_exists = os.path.isfile(csv_file)
        
        summary = self.interview_summary
        
        # Format data for CSV
        row = {
            'interview_id': self.interview_id,
            'date': datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d'),
            'time': datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S'),
            'contestant_name': summary.get('contestant_name', 'Unknown'),
            'pageant_name': summary.get('pageant_name', 'Unknown'),
            'overall_score': summary.get('overall_score', 0),
            'presentation_score': summary.get('presentation_score', 0),
            'content_score': summary.get('content_score', 0),
            'confidence_score': summary.get('confidence_score', 0),
            'relevance_score': summary.get('relevance_score', 0),
            'authenticity_score': summary.get('authenticity_score', 0),
            'duration_minutes': self.interview_duration / 60 if self.interview_duration else 0,
            'strengths_count': len(summary.get('strengths', [])),
            'improvements_count': len(summary.get('areas_for_improvement', [])),
            'notes_count': len(summary.get('notes', []))
        }
        
        # Write to CSV
        with open(csv_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            
            # Write header if file doesn't exist
            if not file_exists:
                writer.writeheader()
                
            writer.writerow(row)