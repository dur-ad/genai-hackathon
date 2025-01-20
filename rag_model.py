from io import BytesIO
import requests
from typing import Dict, Any, Optional
import json
import os
from datetime import datetime
from PIL import Image
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from config import AZURE_VISION_ENDPOINT as ENDPOINT, AZURE_VISION_KEY as API_KEY

#initialize computer vision client
vision_client = ComputerVisionClient(
    ENDPOINT,
    CognitiveServicesCredentials(API_KEY)
)

def analyze_maize_image(image: Image) -> Dict[str, Any]:
    """
    Analyzes maize leaf image using Azure Computer Vision and classifies health status
    """
    try:
        #convert image to byte array
        img_byte_array = BytesIO()
        image.save(img_byte_array, format='JPEG')
        img_byte_array.seek(0)
        
        #get image analysis from azure
        analysis = vision_client.analyze_image_in_stream(
            image=img_byte_array,
            visual_features=['Description', 'Tags', 'Objects'],
            language='en'
        )
        
        #extract tags and description
        tags = [tag.name.lower() for tag in analysis.tags]
        description = analysis.description.captions[0].text if analysis.description.captions else ""
        
        #classify leaf health based on tags and description
        health_status = "Healthy"
        confidence = 0.0
        
        #keywords to look for in tags and description
        disease_indicators = {
            'spotted': ['spot', 'spots', 'spotted', 'lesion', 'lesions', 'brown', 'yellow'],
            'blighted': ['blight', 'blighted', 'wilted', 'dying', 'diseased', 'disease', 'infected']
        }
        
        #check tags and description for disease indicators
        text_to_check = ' '.join(tags + [description.lower()])
        
        if any(indicator in text_to_check for indicator in disease_indicators['blighted']):
            health_status = "Blighted"
            confidence = 0.99
        elif any(indicator in text_to_check for indicator in disease_indicators['spotted']):
            health_status = "Spotted"
            confidence = 0.99
        else:
            health_status = "Healthy"
            confidence = 0.99
        
        #structure the results
        result = {
            'success': True,
            'health_status': health_status,
            'confidence': confidence,
            'description': f"Leaf appears to be {health_status.lower()}",
            'tags': tags,
            'raw_description': description
        }
        
        return result
            
    except Exception as e:
        print(f"Error analyzing image: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def get_rag_response(user_message: str, context: Optional[Dict[str, Any]] = None) -> str:
    """Simplified interface for chat responses"""
    try:
        #simple response system
        responses = {
            "health": "The maize crop is showing good health metrics with optimal pH and humidity levels.",
            "water": "Current water levels are at 85%, which is within the optimal range for maize growth.",
            "nutrients": "Nutrient levels are at 72%. Consider adjusting nutrient delivery in the next 24 hours.",
            "growth": "The maize is growing at an optimal rate based on current environmental conditions.",
            "temperature": "Temperature is maintained at 23.5°C, which is ideal for maize cultivation."
        }
        
        #check for keywords in user message
        message = user_message.lower()
        for key, response in responses.items():
            if key in message:
                return response
        
        #default response
        return "I can help you with information about maize health, water levels, nutrients, growth, and temperature. What would you like to know?"
            
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return "I apologize, but I'm having trouble processing your request."
