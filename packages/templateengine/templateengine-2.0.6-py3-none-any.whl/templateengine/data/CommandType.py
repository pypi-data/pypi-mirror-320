from enum import Enum

class CommandType(Enum):
    Unknown = 0
    CreateComponentSkeleton = 1
    ParseDescription = 2
    LearnPatterns = 3
    CreateComponent = 4
    UpdateComponent = 5
    # ...