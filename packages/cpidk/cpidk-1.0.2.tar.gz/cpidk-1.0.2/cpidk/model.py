from typing import Optional, List

from pydantic import BaseModel, Field

class DocumentStatus(BaseModel):
    code: str = Field(alias="kod")
    value: str = Field(alias="wartosc")

class DocumentStatusReason(BaseModel):
    document_status: DocumentStatus = Field(alias="stanDokumentu")
    reason: List[str] = Field(alias="powodZmianyStanu")

class DocumentType(BaseModel):
    code: str = Field(alias="kod")
    value: str = Field(alias="wartosc")

class CategoryPermissions(BaseModel):
    category: str = Field(alias="kategoria")
    expiration_date: Optional[str] = Field(alias="dataWaznosci")

class IssuingAuthority(BaseModel):
    code: str = Field(alias="kod")
    value: str = Field(alias="wartosc")

class LicenseDocument(BaseModel):
    type: DocumentType = Field(alias="typDokumentu")
    serial_number: str = Field(alias="seriaNumerBlankietuDruku")
    issuing_authority: IssuingAuthority = Field(alias="organWydajacyDokument")
    expiration_date: Optional[str] = Field(alias="dataWaznosci")
    status: DocumentStatusReason = Field(alias="stanDokumentu")
    category_permissions: List[CategoryPermissions] = Field(alias="daneUprawnieniaKategorii")

class Statement(BaseModel):
    description: str = Field(alias="opis")

class Document(BaseModel):
    document: LicenseDocument = Field(alias="dokumentPotwierdzajacyUprawnienia")
    statements: List[Statement] = Field(alias="komunikaty")


class Error(BaseModel):
    code: str
    message: str
    value: Optional[str]

class ErrorResponse(BaseModel):
    errors: List[Error]