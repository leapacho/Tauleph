import logging
from enum import Enum, auto
from time import sleep
from typing import Union

class ErrorCategory(Enum):
    SERVER_ERROR = auto()
    RATE_LIMIT = auto()
    AUTHENTICATION = auto()
    VALIDATION = auto()
    UNKNOWN = auto()

class GoogleAPIExceptionHandler:
    #Configure logging.
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        filename='groq_api_errors.log')
    logger = logging.getLogger('groq_api')

    def __init__(self, err, graph, config, initial_messages=None):
        self.error_details = err.response
        self.graph = graph
        self.initial_messages = initial_messages
        self.config = config
        self.contact_message = "Contact Discord user 'limonero.' if this issue is recurring."

        #Extract error information once.
        self.error = self.error_details.get("error", {}) if isinstance(self.error_details, dict) else {}
        self.error_status = self.error.get("status", "")
        self.error_message = self.error.get("message", "No error message provided.")

    def categorize_error(self) -> ErrorCategory:
        """
        Categorize the error type to determine handling strategy.
        """
        if self.error_details is None or not isinstance(self.error_details, dict):
            return ErrorCategory.UNKNOWN

        #Server errors.
        if self.error_status in ["INTERNAL", "UNAVAILABLE", ]:
            return ErrorCategory.SERVER_ERROR
        
        #Rate limit errors.
        if self.error_status in ["RESOURCE_EXHAUSTED"]:
            return ErrorCategory.RATE_LIMIT
        
        #Authentication errors.
        if self.error_status in ["PERMISSION_DENIED", "FAILED_PRECONDITION"]:
            return ErrorCategory.AUTHENTICATION
        
        #Validation errors.
        if self.error_status in ["INVALID_ARGUMENT"]:
            return ErrorCategory.VALIDATION
        
        return ErrorCategory.UNKNOWN
    
    def handle_api_exception(self) -> str:
        """
        Main handler that processes API excepitions based on their category.
        """

        if self.error_details is None:
            return f"An API error occurred, but no response was associated with it. {self.contact_message}"
        
        if not (isinstance(self.error_details, dict) and 'error' in self.error_details):
            return f"An unexpected API error fromat was recieved. {self.contact_message}"
        
        error_category = self.categorize_error()

        #Handle based on category.
        if error_category == ErrorCategory.SERVER_ERROR:
            self.logger.info(f"Attempting retry for server error: {self.error_status}")
            retry_response = self.retry(max_retries=3)
            if not retry_response:
                return f"Failed after 3 retries. Error message: {self.error_message}\nType: {self.error_status}"
            return retry_response
        
        elif error_category == ErrorCategory.RATE_LIMIT:
            self.logger.warning(f"Rate limit encountered: {self.error_message}")
            retry_response = self.retry(max_retries=5, base_delay=5)
            if not retry_response:
                return f"Rate limit exceeded after 5 failed retries. Please try again later or use a different model. {self.contact_message}"
            return retry_response
        
        elif error_category == ErrorCategory.VALIDATION:
            self.logger.error(f"Validation error: {self.error_message}")
            return f"Invalid request: {self.error_message} Please try again. {self.contact_message}"
        
        #Unknown errors.
        self.logger.error(f"Unknown error: {self.error_message}\nType: {self.error_status}")
        return f"{self.error_message}\nType: {self.error_status}\n\n{self.contact_message}"
    
    def retry(self, max_retries: int, base_delay: float = 2) -> Union[str, bool]:
        """
        Retry mechanism with configurable base delay.
        """
        for attempt in range(1, max_retries + 1):
            delay = base_delay * attempt
            self.logger.info(f"Retry attempt {attempt}/{max_retries}, waiting {delay} seconds.")
            sleep(delay)

            try:
                from LLMManaging.graph_manager import process_input
                result = process_input(self.graph, self.config, self.initial_messages)
                self.logger.info(f"Retry {attempt} succesful")
                return result
            except Exception as e:
                self.logger.warning(f"Retry attempt failed: {str(e)}")
                continue

        self.logger.error(f"All {max_retries} retry attempts failed.")
        return False