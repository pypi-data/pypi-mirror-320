class ConflictError(Exception):
    """Custom exception for handling duplicate entries."""

    def __init__(self, message="Duplicate entry detected"):
        
        super().__init__(message)

class NotFoundError(Exception):
    """Custom exception for handling cases where an entity or resource is not found."""

    def __init__(self, message="oops, Resource not found!!"):
        super().__init__(message)

class ValidationError(Exception):
    """Raised for validation errors."""
    
    def __init__(self, message="Invalid Request!!"):
        super().__init__(message)
        
class DatabaseError(Exception):
    """Raised for database operation errors."""
    
    def __init__(self, message="Database error!!"):
        super().__init__(message)