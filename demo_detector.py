import random
import time

class DemoAIDetector:
    """Demo AI detector that simulates analysis without API calls"""
    
    def __init__(self):
        """Initialize demo detector"""
        pass
    
    def detect_ai_content(self, text):
        """
        Simulate AI content detection for demo purposes
        
        Args:
            text (str): The text content to analyze
            
        Returns:
            dict: Simulated analysis results
        """
        # Simulate processing time
        time.sleep(0.5)
        
        # Generate realistic demo results based on text characteristics
        text_length = len(text)
        word_count = len(text.split())
        
        # Simulate different scenarios based on text patterns
        if any(phrase in text.lower() for phrase in [
            "in conclusion", "furthermore", "additionally", "however", "therefore",
            "it is important to note", "as we can see", "to summarize"
        ]):
            # Text with formal academic patterns - higher AI probability
            ai_probability = random.uniform(0.65, 0.85)
            reasoning = "The text exhibits formal academic patterns and structured transitions commonly found in AI-generated content. Phrases like 'in conclusion' and 'furthermore' appear in typical AI writing patterns."
        elif text_length < 100:
            # Short text - uncertain
            ai_probability = random.uniform(0.3, 0.7)
            reasoning = "Short text length makes detection challenging. Limited content available for comprehensive analysis."
        elif any(phrase in text.lower() for phrase in [
            "i think", "in my opinion", "personally", "i believe", "my experience",
            "i remember", "last week", "yesterday", "my friend"
        ]):
            # Personal experiences - lower AI probability
            ai_probability = random.uniform(0.15, 0.35)
            reasoning = "The text contains personal experiences and subjective language patterns typical of human writing. References to personal opinions and experiences suggest human authorship."
        elif word_count > 500 and text.count('.') / word_count < 0.05:
            # Long text with few periods - potentially human stream of consciousness
            ai_probability = random.uniform(0.2, 0.4)
            reasoning = "Long passages with minimal punctuation suggest stream-of-consciousness writing style more characteristic of human authors."
        else:
            # Default case
            ai_probability = random.uniform(0.4, 0.6)
            reasoning = "Mixed indicators present. The text shows some characteristics of both human and AI writing patterns, making definitive classification challenging."
        
        # Generate confidence based on text length and clarity
        if text_length > 1000:
            confidence = random.uniform(0.8, 0.95)
        elif text_length > 300:
            confidence = random.uniform(0.6, 0.8)
        else:
            confidence = random.uniform(0.4, 0.6)
        
        return {
            'ai_probability': ai_probability,
            'confidence': confidence,
            'reasoning': reasoning,
            'demo_mode': True
        }
    
    def batch_detect(self, texts):
        """
        Simulate batch detection
        
        Args:
            texts (list): List of text strings to analyze
            
        Returns:
            list: List of simulated analysis results
        """
        results = []
        for i, text in enumerate(texts):
            result = self.detect_ai_content(text)
            result['index'] = i
            results.append(result)
        return results