from pydantic import BaseModel


# This is a base schema shared by both input (OptionCreate) and output (OptionOut) schemas.
class OptionBase(BaseModel):
    text: str
    is_correct: bool
    question_id: int
    

# This schema is used when creating a new option.
# Since it doesn't add or modify anything, we just use pass
# FastAPI will use this when a user sends a POST request to create an option
class OptionCreate(OptionBase):
    # if no changes is required in incoming data just write pass
    pass


# This schema is used when returning an Option from the database (i.e., response)
# It extends OptionBase by adding id, because when options are stored in the DB, they have a unique identifier (id).
class OptionOut(OptionBase):
    id: int
    class Config:
        # Tells Pydantic: Object received is ORM convert it to JSON
        from_attributes = True
