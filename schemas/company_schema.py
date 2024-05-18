from pydantic import BaseModel, Field


class CompanyBase(BaseModel):
    """
    Base model for company data, specifying the common attributes shared across different company models.

    Attributes:
    - name (str): The name of the company.
    - AFM (str): The AFM (tax identification number) of the company.
    """
    name: str = Field(..., description="The name of the company")
    AFM: str = Field(..., description="The AFM of the company")


class Company(CompanyBase):
    """
    Full model for a company, extending the base model with additional details.

    Attributes:
    - id (int): The unique identifier for the company.
    """
    id: int = Field(..., description="The unique identifier for the company")

    class Config:
        from_attributes = True
