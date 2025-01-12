

import logging
import requests
import time
from typing import Union, Dict
from config.settings import get_settings


class DocumentIntelligenceService:
    """
    A service class for interacting with Azure Document Intelligence API.
    This class provides methods to analyze documents using Azure's Document Intelligence service.
    """

    def __init__(self):
        """
        Initialize the DocumentIntelligenceService with API credentials and endpoint.
        """
        settings = get_settings()
        self.key = settings.document_intelligence.api_key
        self.endpoint = settings.document_intelligence.endpoint
        self.api_version = "2024-02-29-preview"  # Currently only available in East US, West US2, and West Europe

    def analyze(
        self,
        source: Union[str, bytes],
        is_url: bool = True,
        model_id: str = "prebuilt-layout",
    ) -> Dict:
        """
        Analyze a document using Azure Document Intelligence.
        Args:
            source (Union[str, bytes]): The document source, either a URL or base64 encoded content.
            is_url (bool): True if the source is a URL, False if it's base64 encoded content.
            model_id (str): The ID of the model to use for analysis.
        Returns:
            Dict: The analysis results.
        Raises:
            requests.HTTPError: If the API request fails.
        """
        result_id = self._submit_analysis(source, is_url, model_id)
        return self._get_analysis_results(result_id, model_id)

    def _submit_analysis(
        self, source: Union[str, bytes], is_url: bool, model_id: str
    ) -> str:
        """
        Submit a document for analysis to Azure Document Intelligence.
        Args:
            source (Union[str, bytes]): The document source, either a URL or base64 encoded content.
            is_url (bool): True if the source is a URL, False if it's base64 encoded content.
            model_id (str): The ID of the model to use for analysis.
        Returns:
            str: The result ID for the submitted analysis.
        Raises:
            ValueError: If the Operation-Location header is missing in the response.
            requests.HTTPError: If the API request fails.
        """
        url = f"{self.endpoint}/documentintelligence/documentModels/{model_id}:analyze?api-version={self.api_version}&outputContentFormat=markdown"
        headers = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": self.key,
        }
        data = {"urlSource": source} if is_url else {"base64Source": source}

        logging.info("Submitting document for analysis")
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        operation_location = response.headers.get("Operation-Location")
        if not operation_location:
            raise ValueError("Operation-Location header is missing in the response.")

        return operation_location.split("/")[-1].split("?")[0]

    def _get_analysis_results(self, result_id: str, model_id: str) -> Dict:
        """
        Retrieve the analysis results from Azure Document Intelligence.
        Args:
            result_id (str): The ID of the analysis result to retrieve.
            model_id (str): The ID of the model used for analysis.
        Returns:
            Dict: The analysis results.
        Raises:
            requests.HTTPError: If the API request fails.
        """
        url = f"{self.endpoint}/documentintelligence/documentModels/{model_id}/analyzeResults/{result_id}?api-version={self.api_version}&outputContentFormat=markdown"
        headers = {"Ocp-Apim-Subscription-Key": self.key}

        while True:
            logging.info("Waiting for analysis to complete.")
            time.sleep(2)
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if data.get("status") in ["succeeded", "failed"]:
                return data


if __name__ == "__main__":
    # Example usage of the DocumentIntelligenceService
    client = DocumentIntelligenceService()
    analysis_results = client.analyze(
        source="https://s2.q4cdn.com/299287126/files/doc_financials/2024/ar/Amazon-com-Inc-2023-Annual-Report.pdf"
    )
    print(analysis_results.keys())
    print(analysis_results["analyzeResult"].keys())
    print(analysis_results["analyzeResult"]["content"])
    print(analysis_results["analyzeResult"]["tables"])





# Customer Support Ticket Classification System
# --------------------------------------------------------------

import instructor
from pydantic import BaseModel, Field
from openai import OpenAI
from enum import Enum
from typing import List

# Sample customer support tickets
ticket1 = """
I ordered a laptop from your store last week (Order #12345), but I received a tablet instead. 
This is unacceptable! I need the laptop for work urgently. Please resolve this immediately or I'll have to dispute the charge.
"""

ticket2 = """
Hello, I'm having trouble logging into my account. I've tried resetting my password, but I'm not receiving the reset email. 
Can you please help me regain access to my account? I've been a loyal customer for years and have several pending orders.
"""

# --------------------------------------------------------------
# Regular Completion using OpenAI (with drawbacks)
# --------------------------------------------------------------

client = OpenAI()

def classify_ticket_simple(ticket_text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Classify the following customer support ticket into a category."},
            {"role": "user", "content": ticket_text}
        ]
    )
    return response.choices[0].message.content

result = classify_ticket_simple(ticket1)
print(result)

"""
Drawbacks of this approach:
1. No structured output, making it difficult to integrate into automated systems
2. No validation of the output, potentially leading to inconsistent categorizations
3. Limited information extracted, missing important details for prioritization
4. No confidence score, making it hard to flag uncertain classifications for human review
"""


# --------------------------------------------------------------
# Step 1: Get clear on your objectives
# --------------------------------------------------------------

"""
Objective: Develop an AI-powered ticket classification system that:
- Accurately categorizes customer support tickets
- Assesses the urgency and sentiment of each ticket
- Extracts key information for quick resolution
- Provides confidence scores to flag uncertain cases for human review
Business impact:
- Reduce average response time by routing tickets to the right department
- Improve customer satisfaction by prioritizing urgent and negative sentiment tickets
- Increase efficiency by providing agents with key information upfront
- Optimize workforce allocation by automating routine classifications
"""

# --------------------------------------------------------------
# Step 2: Patch your LLM with instructor
# --------------------------------------------------------------

# Instructor makes it easy to get structured data like JSON from LLMs
client = instructor.patch(OpenAI())

# --------------------------------------------------------------
# Step 3: Define Pydantic data models
# --------------------------------------------------------------

"""
This code defines a structured data model for classifying customer support tickets using Pydantic and Python's Enum class. 
It specifies categories, urgency levels, customer sentiments, and other relevant information as predefined options or constrained fields. 
This structure ensures data consistency, enables automatic validation, and facilitates easy integration with AI models and other parts of a support ticket system.
"""

class TicketCategory(str, Enum):
    ORDER_ISSUE = "order_issue"
    ACCOUNT_ACCESS = "account_access"
    PRODUCT_INQUIRY = "product_inquiry"
    TECHNICAL_SUPPORT = "technical_support"
    BILLING = "billing"
    OTHER = "other"

class CustomerSentiment(str, Enum):
    ANGRY = "angry"
    FRUSTRATED = "frustrated"
    NEUTRAL = "neutral"
    SATISFIED = "satisfied"

class TicketUrgency(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TicketClassification(BaseModel):
    category: TicketCategory
    urgency: TicketUrgency
    sentiment: CustomerSentiment
    confidence: float = Field(ge=0, le=1, description="Confidence score for the classification")
    key_information: List[str] = Field(description="List of key points extracted from the ticket")
    suggested_action: str = Field(description="Brief suggestion for handling the ticket")
    
    
ticket_classification = TicketClassification(
    category=TicketCategory.ORDER_ISSUE,
    urgency=TicketUrgency.HIGH,
    sentiment=CustomerSentiment.ANGRY,
    confidence=0.9,
    key_information=["Order #12345", "Received tablet instead of laptop"],
    suggested_action="Contact customer to arrange laptop delivery"
)

# --------------------------------------------------------------
# Step 4: Bring everything together in a single function
# --------------------------------------------------------------

def classify_ticket(ticket_text: str) -> TicketClassification:
    response = client.chat.completions.create(
        model="gpt-4o",
        response_model=TicketClassification,
        temperature=0,
        max_retries=3,
        messages=[
            {
                "role": "system",
                "content": "Analyze the following customer support ticket and extract the requested information."
            },
            {"role": "user", "content": ticket_text}
        ]
    )
    return response

result1 = classify_ticket(ticket1)
result2 = classify_ticket(ticket2)

print(result1.model_dump_json(indent=2))
print(result2.model_dump_json(indent=2))


# --------------------------------------------------------------
# Step 5: Optimize your prompts and experiment
# --------------------------------------------------------------
# To optimize:
# 1. Refine the system message to provide more context about your business
# 2. Experiment with different models (e.g., gpt-3.5-turbo vs gpt-4)
# 3. Fine-tune the model on your specific ticket data if available
# 4. Adjust the TicketClassification model based on business needs

SYSTEM_PROMPT = """
You are an AI assistant for a large e-commerce platform's customer support team. 
Your role is to analyze incoming customer support tickets and provide structured information to help our team respond quickly and effectively.
Business Context:
- We handle thousands of tickets daily across various categories (orders, accounts, products, technical issues, billing).
- Quick and accurate classification is crucial for customer satisfaction and operational efficiency.
- We prioritize based on urgency and customer sentiment.
Your tasks:
1. Categorize the ticket into the most appropriate category.
2. Assess the urgency of the issue (low, medium, high, critical).
3. Determine the customer's sentiment.
4. Extract key information that would be helpful for our support team.
5. Suggest an initial action for handling the ticket.
6. Provide a confidence score for your classification.
Remember:
- Be objective and base your analysis solely on the information provided in the ticket.
- If you're unsure about any aspect, reflect that in your confidence score.
- For 'key_information', extract specific details like order numbers, product names, or account issues.
- The 'suggested_action' should be a brief, actionable step for our support team.
Analyze the following customer support ticket and provide the requested information in the specified format.
"""

def classify_ticket(ticket_text: str) -> TicketClassification:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        response_model=TicketClassification,
        temperature=0,
        max_retries=3,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {"role": "user", "content": ticket_text}
        ]
    )
    return response

result1 = classify_ticket(ticket1)
result2 = classify_ticket(ticket2)

print(result1.model_dump_json(indent=2))
print(result2.model_dump_json(indent=2))












