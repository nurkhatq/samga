"""
Pydantic схемы для валидации данных
"""

# Common
from app.schemas.common import (
    ErrorResponse,
    SuccessResponse,
    PaginationParams,
    PaginatedResponse,
)

# User
from app.schemas.user import (
    UserLogin,
    TokenResponse,
    RefreshTokenRequest,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    CurrentUserResponse,
)

# Major
from app.schemas.major import (
    MajorCreate,
    MajorUpdate,
    MajorResponse,
    MajorListResponse,
    MajorWithSubjectsResponse,
)

# Subject
from app.schemas.subject import (
    SubjectCreate,
    SubjectUpdate,
    SubjectResponse,
    SubjectListResponse,
    SubjectStatsResponse,
)

# Question
from app.schemas.question import (
    QuestionOptionBase,
    QuestionOptionCreate,
    QuestionOptionResponse,
    QuestionOptionWithCorrect,
    QuestionCreate,
    QuestionResponse,
    QuestionWithCorrectResponse,
    QuestionListResponse,
    QuestionImportResult,
)

# Exam
from app.schemas.exam import (
    PracticeStartRequest,
    ExamStartRequest,
    ExamStartResponse,
    GetQuestionsRequest,
    GetQuestionsResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    ExamStatusResponse,
    ExamSubmitRequest,
    ExamResultResponse,
    ExamResultWithQuestionsResponse,
    UserStatisticsResponse,
)

# Proctoring
from app.schemas.proctoring import (
    ProctoringEventCreate,
    ProctoringEventResponse,
    ProctoringEventBatchCreate,
    ProctoringEventBatchResponse,
    ProctoringStatisticsResponse,
)

__all__ = [
    # Common
    "ErrorResponse",
    "SuccessResponse",
    "PaginationParams",
    "PaginatedResponse",
    
    # User
    "UserLogin",
    "TokenResponse",
    "RefreshTokenRequest",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserListResponse",
    "CurrentUserResponse",
    
    # Major
    "MajorCreate",
    "MajorUpdate",
    "MajorResponse",
    "MajorListResponse",
    "MajorWithSubjectsResponse",
    
    # Subject
    "SubjectCreate",
    "SubjectUpdate",
    "SubjectResponse",
    "SubjectListResponse",
    "SubjectStatsResponse",
    
    # Question
    "QuestionOptionBase",
    "QuestionOptionCreate",
    "QuestionOptionResponse",
    "QuestionOptionWithCorrect",
    "QuestionCreate",
    "QuestionResponse",
    "QuestionWithCorrectResponse",
    "QuestionListResponse",
    "QuestionImportResult",
    
    # Exam
    "PracticeStartRequest",
    "ExamStartRequest",
    "ExamStartResponse",
    "GetQuestionsRequest",
    "GetQuestionsResponse",
    "SubmitAnswerRequest",
    "SubmitAnswerResponse",
    "ExamStatusResponse",
    "ExamSubmitRequest",
    "ExamResultResponse",
    "ExamResultWithQuestionsResponse",
    "UserStatisticsResponse",
    
    # Proctoring
    "ProctoringEventCreate",
    "ProctoringEventResponse",
    "ProctoringEventBatchCreate",
    "ProctoringEventBatchResponse",
    "ProctoringStatisticsResponse",
]
