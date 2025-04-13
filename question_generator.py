import random
import re
from typing import Dict, List, Any

# Hypothetical LlamaIndex imports
from llama_index import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.retrievers import VectorIndexRetriever

class LlamaEnhancedQuestionGenerator:
    """
    Enhanced Question Generator using LlamaIndex for semantic question retrieval
    """
    
    def __init__(self, question_bank_path: str = 'data/question_bank'):
        """
        Initialize the question generator with a LlamaIndex vector store
        
        :param question_bank_path: Path to directory containing question bank documents
        """
        self.question_bank_path = question_bank_path
        self.index = None
        self.query_engine = None
        
        # Initialize the index
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """
        Load existing index or create a new one from the question bank
        """
        try:
            # Try to load existing storage context
            storage_context = StorageContext.from_defaults(persist_dir=self.question_bank_path)
            self.index = load_index_from_storage(storage_context)
        except:
            # If no existing index, create a new one
            documents = SimpleDirectoryReader(self.question_bank_path).load_data()
            self.index = VectorStoreIndex.from_documents(documents)
            
            # Persist the index for future use
            self.index.storage_context.persist(persist_dir=self.question_bank_path)
        
        # Create query engine
        self.query_engine = self.index.as_query_engine(
            retriever=VectorIndexRetriever(self.index, similarity_top_k=5)
        )
    
    def generate_semantic_questions(self, 
                                    contestant_info: Dict[str, Any], 
                                    pageant_info: Dict[str, Any], 
                                    num_questions: int = 5) -> List[Dict[str, str]]:
        """
        Generate semantically relevant questions using LlamaIndex
        
        :param contestant_info: Information about the contestant
        :param pageant_info: Information about the pageant
        :param num_questions: Number of questions to generate
        :return: List of generated questions
        """
        # Construct a detailed query context
        query_context = self._construct_query_context(contestant_info, pageant_info)
        
        # Generate semantic questions
        semantic_questions = []
        for _ in range(num_questions):
            try:
                # Query the index with the context
                response = self.query_engine.query(query_context)
                
                # Extract and process the generated question
                question = self._process_generated_question(response.response)
                
                if question:
                    semantic_questions.append({
                        'type': 'semantic',
                        'question': question
                    })
            except Exception as e:
                print(f"Error generating semantic question: {e}")
        
        return semantic_questions
    
    def _construct_query_context(self, 
                                 contestant_info: Dict[str, Any], 
                                 pageant_info: Dict[str, Any]) -> str:
        """
        Construct a detailed context for semantic question generation
        
        :param contestant_info: Information about the contestant
        :param pageant_info: Information about the pageant
        :return: Detailed context string
        """
        context_parts = []
        
        # Add contestant details
        context_parts.append(f"Contestant Name: {contestant_info.get('name', 'Unknown')}")
        
        # Add skills and experiences
        if 'skills' in contestant_info:
            context_parts.append(f"Skills: {', '.join(contestant_info['skills'])}")
        
        if 'experiences' in contestant_info:
            exp_summary = '; '.join([
                f"{exp.get('activity', 'Experience')} with {exp.get('organization', 'Unknown')}" 
                for exp in contestant_info['experiences']
            ])
            context_parts.append(f"Experiences: {exp_summary}")
        
        # Add pageant details
        context_parts.append(f"Pageant Name: {pageant_info.get('name', 'Unknown')}")
        
        if 'values' in pageant_info:
            context_parts.append(f"Pageant Values: {', '.join(pageant_info['values'])}")
        
        if 'current_issue' in pageant_info:
            context_parts.append(f"Current Focus: {pageant_info['current_issue']}")
        
        # Construct full context
        return "Generate an insightful interview question considering the following context: " + \
               " ".join(context_parts)
    
    def _process_generated_question(self, raw_question: str) -> str:
        """
        Process and clean the generated question
        
        :param raw_question: Raw generated question
        :return: Cleaned and formatted question
        """
        # Remove any leading/trailing whitespace
        question = raw_question.strip()
        
        # Ensure it ends with a question mark
        if not question.endswith('?'):
            question += '?'
        
        # Capitalize the first letter
        question = question[0].upper() + question[1:]
        
        # Basic filtering to ensure question quality
        if len(question) < 10 or len(question) > 200:
            return None
        
        return question
    
    def generate_interview_script(self, 
                                  contestant_info: Dict[str, Any], 
                                  pageant_info: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Generate a comprehensive interview script combining traditional and semantic questions
        
        :param contestant_info: Information about the contestant
        :param pageant_info: Information about the pageant
        :return: List of interview questions
        """
        # Start with traditional question generation
        traditional_generator = QuestionGenerator()
        script = traditional_generator.generate_interview_script(contestant_info, pageant_info)
        
        # Generate additional semantic questions
        semantic_questions = self.generate_semantic_questions(contestant_info, pageant_info)
        
        # Merge and randomize questions
        script.extend(semantic_questions)
        random.shuffle(script)
        
        return script
    
    def generate_follow_up_question(self, 
                                    question_type: str, 
                                    question: str, 
                                    response: str) -> str:
        """
        Generate a follow-up question using semantic retrieval
        
        :param question_type: Type of the original question
        :param question: Original question
        :param response: Contestant's response
        :return: Generated follow-up question
        """
        # Construct query context
        query_context = f"Generate a follow-up question based on this context: " \
                        f"Original Question Type: {question_type}\n" \
                        f"Original Question: {question}\n" \
                        f"Contestant Response: {response}"
        
        try:
            # Query the index for a follow-up question
            response = self.query_engine.query(query_context)
            
            # Process the generated follow-up
            follow_up = self._process_generated_question(response.response)
            
            return follow_up if follow_up else "Could you tell me more about that?"
        
        except Exception as e:
            print(f"Error generating follow-up question: {e}")
            return "Could you elaborate on that?"

