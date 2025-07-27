"""
Vertex AI client for the Finance AI Agent.
"""
import json
import logging
import os
from typing import Dict, Any, Optional
from google.cloud import aiplatform
from google.auth import default
from config import config

logger = logging.getLogger(__name__)

class VertexAIClient:
    """Client for interacting with Vertex AI."""
    
    def __init__(self):
        """Initialize the Vertex AI client."""
        self.project_id = config.VERTEX_AI_PROJECT_ID
        self.location = config.VERTEX_AI_LOCATION
        self.model_name = config.VERTEX_AI_MODEL
        
        # Check if project_id looks like a file path (service account key)
        if self.project_id.endswith('.json'):
            # Extract project ID from service account file
            import json
            try:
                with open(self.project_id, 'r') as f:
                    sa_data = json.load(f)
                    self.project_id = sa_data.get('project_id', self.project_id)
                    print(f"🔧 Extracted project ID from service account: {self.project_id}")
            except Exception as e:
                print(f"❌ Error reading service account file: {e}")
                raise ValueError("Invalid service account file or project ID")
        
        # Set Google Application Credentials if not set
        if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS') and config.VERTEX_AI_PROJECT_ID.endswith('.json'):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config.VERTEX_AI_PROJECT_ID
            print(f"🔧 Set GOOGLE_APPLICATION_CREDENTIALS to: {config.VERTEX_AI_PROJECT_ID}")
        
        # Initialize Vertex AI
        aiplatform.init(
            project=self.project_id,
            location=self.location
        )
        
        # Get the model - try different approaches
        try:
            # For Vertex AI, we need to use the full model path
            if not self.model_name.startswith('projects/'):
                # Convert model name to Vertex AI format
                vertex_model_name = f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/{self.model_name}"
                print(f"🔧 Using Vertex AI model: {vertex_model_name}")
            else:
                vertex_model_name = self.model_name
            
            # Try the newer GenerativeModel approach
            self.model = aiplatform.GenerativeModel(vertex_model_name)
        except AttributeError:
            try:
                # Try the older approach with model endpoint
                from google.cloud.aiplatform_v1 import ModelServiceClient
                self.model = aiplatform.Model(vertex_model_name)
            except Exception as e:
                print(f"❌ Error initializing Vertex AI model: {e}")
                raise
        
    async def generate_content(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate content using Vertex AI.
        
        Args:
            prompt: The input prompt
            **kwargs: Additional parameters for generation
            
        Returns:
            Dictionary containing the response
        """
        try:
            # Set default parameters
            generation_config = {
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.8),
                "top_k": kwargs.get("top_k", 40),
                "max_output_tokens": kwargs.get("max_output_tokens", 2048),
            }
            
            # Generate content
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return {
                "text": response.text,
                "candidates": response.candidates,
                "usage_metadata": response.usage_metadata
            }
            
        except Exception as e:
            logger.error(f"Error generating content with Vertex AI: {str(e)}")
            raise
    
    async def get_celebrity_data(self, celebrity_name: str) -> Dict[str, Any]:
        """
        Get celebrity financial data using Vertex AI.
        
        Args:
            celebrity_name: Name of the celebrity
            
        Returns:
            Dictionary containing celebrity financial data
        """
        prompt = f"""
        Get current financial data for {celebrity_name}. Return ONLY a JSON object with these exact fields:
        {{
            "name": "{celebrity_name}",
            "net_worth": <number in USD>,
            "monthly_income": <number in USD>,
            "investments": <number in USD>,
            "real_estate": <number in USD>,
            "primary_income_sources": ["source1", "source2"],
            "data_source": "Forbes/Wikipedia/etc",
            "last_updated": "2024"
        }}
        
        Rules:
        - Use latest available data (2024-2025)
        - Convert all amounts to USD
        - Be accurate and realistic
        - For Shah Rukh Khan: net worth ~$600M, monthly income ~$2M
        - For Jeff Bezos: net worth ~$170B, monthly income ~$50M
        - For Elon Musk: net worth ~$230B, monthly income ~$100M
        - Return ONLY the JSON, no explanations
        """
        
        try:
            response = await self.generate_content(prompt, temperature=0.3)
            response_text = response["text"].strip()
            
            # Extract JSON from response (handle markdown formatting)
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1]
            
            # Parse JSON
            celebrity_data = json.loads(response_text)
            
            # Validate required fields
            required_fields = ["name", "net_worth", "monthly_income", "investments", "real_estate", "primary_income_sources", "data_source", "last_updated"]
            for field in required_fields:
                if field not in celebrity_data:
                    raise ValueError(f"Missing required field: {field}")
            
            return celebrity_data
            
        except Exception as e:
            logger.error(f"Error getting celebrity data for {celebrity_name}: {str(e)}")
            # Return fallback data
            return {
                "name": celebrity_name,
                "net_worth": 1000000000,  # 1 billion USD
                "monthly_income": 5000000,  # 5 million USD
                "investments": 500000000,  # 500 million USD
                "real_estate": 200000000,  # 200 million USD
                "primary_income_sources": ["Entertainment", "Business"],
                "data_source": "Estimated",
                "last_updated": "2024"
            }

# Create a singleton instance
vertex_ai_client = VertexAIClient() 