from pydantic import BaseModel, Field


class CompanyBase(BaseModel):
    """
    Base model for company data, specifying the common attributes shared across different company models.
    This model includes essential details such as the company's name, tax identification number (AFM), contact details, and location.

    Attributes:
    - name (str): The name of the company.
    - AFM (str): The tax identification number of the company, unique for each company.
    - email (str): Official email address of the company.
    - telephone (str): Contact telephone number of the company.
    - city (str): City where the company is located, indicating the primary place of business operations.
    """
    name: str = Field(..., description="The name of the company")
    AFM: str = Field(..., description="The AFM of the company")
    email: str = Field(..., description="Email address of the company")
    telephone: str = Field(..., description="Telephone number of the company")
    city: str = Field(..., description="City where the company is located")


class Company(CompanyBase):
    """
    Full model for a company, extending the base model with additional details.

    Attributes:
    - id (int): The unique identifier for the company.
    """
    id: int = Field(..., description="The unique identifier for the company")

    class Config:
        from_attributes = True
