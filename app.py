from flask import Flask, render_template, request, jsonify, session, send_from_directory, redirect, url_for
import os
import json
import uuid
from datetime import datetime
import time
import glob
from typing import Tuple
import traceback

# Import our modules - use the correct class names
from interview_agent import InterviewAgent
from conversation_manager import ConversationManager
from interview_summary import save_interview_summary

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)
os.makedirs('data/interviews', exist_ok=True)
os.makedirs('data/uploads', exist_ok=True)
os.makedirs('data/reports', exist_ok=True)

# Template context processors and filters
@app.template_filter('timestamp_to_datetime')
def timestamp_to_datetime(timestamp):
    """Convert Unix timestamp to formatted datetime string"""
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y-%m-%d %H:%M:%S')

@app.template_filter('duration_format')
def duration_format(seconds):
    """Format seconds into a readable duration"""
    if seconds is None:
        return "No limit"
    
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    return f"{minutes}m {remaining_seconds}s"

@app.context_processor
def utility_processor():
    """Add utility functions to template context"""
    def now(format_string='%Y-%m-%d'):
        return datetime.now().strftime(format_string)
    
    return dict(now=now)

@app.route('/')
def index():
    """Render the homepage"""
    return render_template('index.html')

@app.route('/interview/<interview_id>')
def interview(interview_id):
    """Render the interview page"""
    interview_dir = os.path.join('data/interviews', interview_id)
    
    # Check if interview exists
    if not os.path.exists(interview_dir):
        return "Interview not found", 404
    
    # Load agent state
    try:
        with open(os.path.join(interview_dir, 'agent_state.json'), 'r') as f:
            agent_state = json.load(f)
        
        # Set session
        session['interview_id'] = interview_id
        
        # Get interview duration
        interview_duration = agent_state.get('interview_duration', 0)
        
        return render_template('interview.html', 
                              interview_id=interview_id,
                              pageant_name=agent_state['pageant_info'].get('name', 'Unknown'),
                              contestant_name=agent_state['contestant_info'].get('name', 'Unknown'),
                              interview_duration=interview_duration)
    except Exception as e:
        print(f"Error loading interview: {e}")
        return "Error loading interview data", 500
    
@app.route('/setup-interview', methods=['GET', 'POST'])
def setup_interview():
    """Setup a new pageant interview"""
    if request.method == 'POST':
        try:
            # Generate a unique ID for this interview
            interview_id = str(uuid.uuid4())
            session['interview_id'] = interview_id
            
            # Create directory for this interview
            interview_dir = os.path.join('data/interviews', interview_id)
            os.makedirs(interview_dir, exist_ok=True)
            
            # Save pageant profile
            pageant_profile = request.form.get('pageant_profile', '')
            with open(os.path.join(interview_dir, 'pageant_profile.txt'), 'w') as f:
                f.write(pageant_profile)
            
            # Save contestant profile
            contestant_profile = request.form.get('contestant_profile', '')
            with open(os.path.join(interview_dir, 'contestant_profile.txt'), 'w') as f:
                f.write(contestant_profile)
            
            # Get interview duration
            interview_duration = request.form.get('interview_duration', '')
            try:
                interview_duration = int(interview_duration)
            except (ValueError, TypeError):
                interview_duration = 0  # No time limit
            
            # Process documents and prepare interview
            agent = InterviewAgent()
            agent.enable_debug_mode()  # Enable debugging
            
            print("Loading pageant profile...")
            pageant_info = agent.load_pageant_profile(pageant_profile)
            print(f"Pageant info keys: {pageant_info.keys() if pageant_info else 'None'}")
            
            print("Loading contestant profile...")
            contestant_info = agent.load_contestant_profile(contestant_profile)
            print(f"Contestant info keys: {contestant_info.keys() if contestant_info else 'None'}")
            
            # Check if we have the minimum required information
            if not pageant_info or 'name' not in pageant_info:
                raise ValueError("Failed to properly parse pageant profile")
                
            if not contestant_info or 'name' not in contestant_info:
                raise ValueError("Failed to properly parse contestant profile")
            
            # Create conversation manager
            conversation_manager = ConversationManager(pageant_info, contestant_info)
            
            # Generate interview script
            print("Generating interview script...")
            script = conversation_manager.generate_interview_script()
            print(f"Generated {len(script)} questions")
            
            if not script or len(script) == 0:
                raise ValueError("Failed to generate interview script")
                
            # Set interview duration if specified
            if interview_duration > 0:
                agent.set_interview_duration(interview_duration)
            
            # Save agent state
            with open(os.path.join(interview_dir, 'agent_state.json'), 'w') as f:
                json.dump({
                    'pageant_info': pageant_info,
                    'contestant_info': contestant_info,
                    'script': script,
                    'interview_duration': interview_duration,
                    'created_at': datetime.now().isoformat()
                }, f, indent=2)
            
            return jsonify({
                'status': 'success',
                'interview_id': interview_id,
                'redirect': f'/interview/{interview_id}'
            })
        except Exception as e:
            error_message = str(e)
            error_traceback = traceback.format_exc()
            print(f"Error setting up interview: {error_message}")
            print(f"Traceback: {error_traceback}")
            
            # Clean up the interview directory if it exists
            if 'interview_dir' in locals() and os.path.exists(interview_dir):
                import shutil
                shutil.rmtree(interview_dir)
                
            return jsonify({
                'status': 'error',
                'message': f"Error setting up interview: {error_message}"
            }), 500
    
    return render_template('setup_interview.html')

@app.route('/api/start-interview', methods=['POST'])
def start_interview():
    """Start the interview"""
    try:
        interview_id = request.json.get('interview_id')
        if not interview_id:
            return jsonify({'status': 'error', 'message': 'Interview ID is required'}), 400
        
        interview_dir = os.path.join('data/interviews', interview_id)
        
        # Check if interview exists
        if not os.path.exists(interview_dir):
            return jsonify({'status': 'error', 'message': 'Interview not found'}), 404
        
        # Load agent state
        with open(os.path.join(interview_dir, 'agent_state.json'), 'r') as f:
            agent_state = json.load(f)
        
        # Check if both profiles exist in the agent state
        if 'pageant_info' not in agent_state or 'contestant_info' not in agent_state:
            return jsonify({
                'status': 'error',
                'message': 'Required profiles missing from agent state'
            }), 500
            
        # Debug print
        print("Pageant info:", agent_state['pageant_info'])
        print("Contestant info:", agent_state['contestant_info'])
        
        # Initialize agent with saved state
        agent = InterviewAgent()
        agent.pageant_info = agent_state['pageant_info']
        agent.contestant_info = agent_state['contestant_info']
        agent.interview_id = interview_id
        
        # Create conversation manager
        conversation_manager = ConversationManager(
            agent_state['pageant_info'],
            agent_state['contestant_info']
        )
        
        # Set the interview script
        script = agent_state.get('script', [])
        if not script:
            # Generate script if not available
            print("Generating interview script...")
            script = conversation_manager.generate_interview_script()
            
        conversation_manager.set_interview_script(script)
        
        # Set the conversation manager for the agent
        agent.set_conversation_manager(conversation_manager)
        
        # Set interview duration if specified
        interview_duration = agent_state.get('interview_duration', 0)
        if interview_duration > 0:
            agent.set_interview_duration(interview_duration)
        
        # Start interview
        print("Starting interview...")
        first_question = agent.start_interview()
        print("First question:", first_question)
        
        # Save conversation state
        with open(os.path.join(interview_dir, 'conversation.json'), 'w') as f:
            json.dump({
                'history': agent.conversation_manager.conversation_history,
                'current_index': agent.conversation_manager.current_question_index,
                'current_question_type': agent.conversation_manager.current_question_type,
                'current_question': agent.conversation_manager.current_question,
                'complete': False,
                'interview_start_time': agent.interview_start_time
            }, f, indent=2)
        
        # Get remaining time information
        time_info = agent.check_time_limit()
        
        time_exceeded = False
        remaining_seconds = interview_duration * 60  # Convert minutes to seconds
        
        if isinstance(time_info, tuple) and len(time_info) >= 2:
            time_exceeded, remaining_seconds = time_info[0], time_info[1]
        
        return jsonify({
            'status': 'success',
            'question': first_question,
            'remaining_seconds': remaining_seconds,
            'has_time_limit': interview_duration > 0
        })
    except Exception as e:
        error_message = str(e)
        error_traceback = traceback.format_exc()
        print(f"Error starting interview: {error_message}")
        print(f"Traceback: {error_traceback}")
        return jsonify({'status': 'error', 'message': f"Error starting interview: {error_message}"}), 500

@app.route('/api/process-response', methods=['POST'])
def process_response():
    """Process a contestant's response"""
    try:
        interview_id = request.json.get('interview_id')
        response = request.json.get('response')
        
        if not interview_id or not response:
            return jsonify({'status': 'error', 'message': 'Interview ID and response are required'}), 400
        
        interview_dir = os.path.join('data/interviews', interview_id)
        
        # Check if interview exists
        if not os.path.exists(interview_dir):
            return jsonify({'status': 'error', 'message': 'Interview not found'}), 404
        
        # Load agent state
        with open(os.path.join(interview_dir, 'agent_state.json'), 'r') as f:
            agent_state = json.load(f)
        
        # Load conversation state
        with open(os.path.join(interview_dir, 'conversation.json'), 'r') as f:
            conversation_state = json.load(f)
        
        # Initialize agent with saved state
        agent = InterviewAgent()
        agent.pageant_info = agent_state['pageant_info']
        agent.contestant_info = agent_state['contestant_info']
        agent.interview_id = interview_id
        agent.interview_start_time = conversation_state.get('interview_start_time')
        
        # Set interview duration if specified
        interview_duration = agent_state.get('interview_duration', 0)
        if interview_duration > 0:
            agent.set_interview_duration(interview_duration)
        
        # Recreate conversation manager
        conversation_manager = ConversationManager(
            agent_state['pageant_info'],
            agent_state['contestant_info']
        )
        
        # Set interview script
        conversation_manager.set_interview_script(agent_state.get('script', []))
        
        # Restore conversation state
        conversation_manager.conversation_history = conversation_state['history']
        conversation_manager.current_question_index = conversation_state['current_index']
        conversation_manager.current_question_type = conversation_state.get('current_question_type')
        conversation_manager.current_question = conversation_state.get('current_question')
        
        # Set the conversation manager for the agent
        agent.set_conversation_manager(conversation_manager)
        
        # Set agent state
        agent.interview_in_progress = True
        agent.interview_complete = conversation_state.get('complete', False)
        
        # Process the response
        print("DEBUG: Before calling process_contestant_response")
        result = agent.process_contestant_response(response)
        print(f"DEBUG: process_contestant_response result: {result}")
        
        if result.get('remaining_seconds', float('inf')) <= 15:  # Force completion when 15 seconds or less remain
            print("DEBUG: Very little time remaining, forcing interview completion")
            agent.interview_complete = True
            summary_path = os.path.join(interview_dir, 'summary.json')
            if not os.path.exists(summary_path):
                save_interview_summary(
                    interview_dir, 
                    agent.conversation_manager.conversation_history,
                    agent_state['pageant_info'],
                    agent_state['contestant_info']
                )
    
            # Generate summary if not already done
            if not agent.interview_summary:
                agent.interview_summary = agent.conversation_manager.get_interview_summary()
                
            # Update the result to reflect this
            result['is_complete'] = True
            result['time_limit_exceeded'] = True if result.get('remaining_seconds', 0) <= 0 else False
        
        # Update conversation state
        with open(os.path.join(interview_dir, 'conversation.json'), 'w') as f:
            json.dump({
                'history': agent.conversation_manager.conversation_history,
                'current_index': agent.conversation_manager.current_question_index,
                'current_question_type': agent.conversation_manager.current_question_type,
                'current_question': agent.conversation_manager.current_question,
                'complete': agent.interview_complete,
                'interview_start_time': agent.interview_start_time
            }, f, indent=2)
        
        # If interview is complete, save summary
        if agent.interview_complete:
            print("DEBUG: Interview is complete. Generating summary.json...")
            with open(os.path.join(interview_dir, 'summary.json'), 'w') as f:
                json.dump(agent.interview_summary, f, indent=2)
        else:
            print("DEBUG: Interview is not complete. Skipping summary.json generation.")
        
        # Make sure remaining_seconds is set in the result
        if 'remaining_seconds' not in result:
            # Need to check time limit again
            print("DEBUG: Calling check_time_limit")
            time_info = agent.check_time_limit()
            
            time_exceeded = False
            remaining_seconds = interview_duration * 60  # Convert minutes to seconds
            
            if isinstance(time_info, tuple):
                if len(time_info) >= 2:
                    time_exceeded, remaining_seconds = time_info[0], time_info[1]
            
            result['remaining_seconds'] = remaining_seconds
            result['time_limit_exceeded'] = time_exceeded
        
        response_data = {
            'status': 'success',
            'question': result['next_question'],
            'is_complete': result['is_complete'],
            'remaining_seconds': result.get('remaining_seconds'),
            'time_limit_exceeded': result.get('time_limit_exceeded', False)
        }
        
        return jsonify(response_data)
    except Exception as e:
        error_message = str(e)
        error_traceback = traceback.format_exc()
        print(f"Error processing response: {error_message}")
        print(f"Traceback: {error_traceback}")
        return jsonify({'status': 'error', 'message': f"Error processing response: {error_message}"}), 500

@app.route('/report/<interview_id>')
def report(interview_id):
    """Serve the interview report for the given interview ID."""
    interview_dir = os.path.join('data/interviews', interview_id)
    
    # Check if the interview directory exists
    if not os.path.exists(interview_dir):
        return "Interview not found", 404
    
    # Check if the summary report exists
    summary_path = os.path.join(interview_dir, 'summary.json')
    if not os.path.exists(summary_path):
        return "Report not generated yet. The interview may not be complete.", 404
    
    # Load agent state and conversation history
    try:
        # Load summary
        with open(summary_path, 'r') as f:
            summary_data = json.load(f)
        
        # Detailed debugging of summary data
        print("DETAILED SUMMARY DATA:")
        for key, value in summary_data.items():
            print(f"{key}: {type(value)} = {value}")
        
        # Load agent state
        with open(os.path.join(interview_dir, 'agent_state.json'), 'r') as f:
            agent_state = json.load(f)
        
        # Load conversation history
        conversation_path = os.path.join(interview_dir, 'conversation.json')
        conversation_transcript = []
        conversation_data = {}
        if os.path.exists(conversation_path):
            with open(conversation_path, 'r') as f:
                conversation_data = json.load(f)
                history = conversation_data.get('history', [])
                
                # Format conversation for transcript
                for entry in history:
                    conversation_transcript.append({
                        'speaker': entry.get('speaker', 'Unknown'),
                        'text': entry.get('text', ''),
                        'timestamp': conversation_data.get('interview_start_time', 0)
                    })
        
        # Add the conversation transcript to the summary data
        summary_data['conversation_transcript'] = conversation_transcript
        
        # Add interview date
        if 'interview_start_time' in conversation_data:
            try:
                start_time = float(conversation_data['interview_start_time'])
                summary_data['interview_date'] = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M')
            except (ValueError, TypeError) as e:
                print(f"Error formatting interview date: {e}")
                summary_data['interview_date'] = 'Unknown'
        
        # Get contestant name and pageant name
        contestant_name = agent_state['contestant_info'].get('name', 'Unknown')
        pageant_name = agent_state['pageant_info'].get('name', 'Unknown')
        
        # Comprehensive field population and validation
        comprehensive_fields = {
            'overall_score': 69.0,
            'presentation_score': 70.0,
            'content_score': 100.0,
            'confidence_score': 50.0,
            'relevance_score': 50.0,
            'authenticity_score': 60.0,
            'technical_score': 55.0,
            'experience_relevance_score': 65.0,
            'skill_match_score': 70.0,
            'cultural_fit_score': 60.0,
            'communication_score': 75.0,
            'skill_match_percentage': 69.0,
            'recommendation': 'Promising Candidate',
            'strengths': ['Substantial and detailed responses'],
            'areas_for_improvement': ['Continue developing interview skills']
        }
        
        # Merge and ensure all fields are populated
        for key, default_value in comprehensive_fields.items():
            if key not in summary_data or summary_data[key] in [None, '', 0]:
                summary_data[key] = default_value
        
        # Ensure conversation transcript exists
        if 'conversation_transcript' not in summary_data:
            summary_data['conversation_transcript'] = []
        
        # Print final summary data for verification
        print("FINAL SUMMARY DATA:")
        for key, value in summary_data.items():
            print(f"{key}: {type(value)} = {value}")
        
        return render_template('report.html', 
                               summary=summary_data, 
                               interview_id=interview_id,
                               contestant_name=contestant_name,
                               pageant_name=pageant_name)
    
    except Exception as e:
        error_message = str(e)
        error_traceback = traceback.format_exc()
        print(f"Error generating report: {error_message}")
        print(f"Traceback: {error_traceback}")
        return f"Error generating report: {error_message}", 500

# Start the server when run directly
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)