"""
🌌 SarlakBot v3.0 - Onboarding State Management
State definitions for the cosmic onboarding journey
"""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass


class OnboardingState(Enum):
    """Onboarding conversation states"""
    
    # Initial states
    INTRO = "intro"
    MEMBERSHIP_CHECK = "membership_check"
    
    # Data collection states
    COLLECTING_NAME = "collecting_name"
    COLLECTING_NICKNAME = "collecting_nickname"
    SELECTING_TRACK = "selecting_track"
    SELECTING_GRADE_BAND = "selecting_grade_band"
    SELECTING_GRADE_YEAR = "selecting_grade_year"
    COLLECTING_PHONE = "collecting_phone"
    
    # Final states
    WELCOME = "welcome"
    COMPLETED = "completed"
    
    # Error states
    ERROR = "error"


@dataclass
class OnboardingData:
    """Onboarding data structure"""
    
    # User identification
    user_id: int
    username: Optional[str] = None
    real_name: Optional[str] = None
    nickname: Optional[str] = None
    nickname_changes_left: int = 3
    
    # Academic information
    study_track: Optional[str] = None
    grade_band: Optional[str] = None
    grade_year: Optional[str] = None
    
    # Contact information
    phone: Optional[str] = None
    
    # Status flags
    is_channel_member: bool = False
    onboarding_completed: bool = False
    
    # Timestamps
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'real_name': self.real_name,
            'nickname': self.nickname,
            'nickname_changes_left': self.nickname_changes_left,
            'study_track': self.study_track,
            'grade_band': self.grade_band,
            'grade_year': self.grade_year,
            'phone': self.phone,
            'is_channel_member': self.is_channel_member,
            'onboarding_completed': self.onboarding_completed,
            'started_at': self.started_at,
            'completed_at': self.completed_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OnboardingData':
        """Create from dictionary"""
        return cls(
            user_id=data.get('user_id'),
            username=data.get('username'),
            real_name=data.get('real_name'),
            nickname=data.get('nickname'),
            nickname_changes_left=data.get('nickname_changes_left', 3),
            study_track=data.get('study_track'),
            grade_band=data.get('grade_band'),
            grade_year=data.get('grade_year'),
            phone=data.get('phone'),
            is_channel_member=data.get('is_channel_member', False),
            onboarding_completed=data.get('onboarding_completed', False),
            started_at=data.get('started_at'),
            completed_at=data.get('completed_at')
        )


class OnboardingFlow:
    """Onboarding flow state machine"""
    
    def __init__(self):
        self.current_state = OnboardingState.INTRO
        self.data = None
        self.error_count = 0
        self.max_errors = 3
    
    def set_data(self, data: OnboardingData) -> None:
        """Set onboarding data"""
        self.data = data
    
    def get_data(self) -> Optional[OnboardingData]:
        """Get onboarding data"""
        return self.data
    
    def next_state(self) -> OnboardingState:
        """Get next state in the flow"""
        state_map = {
            OnboardingState.INTRO: OnboardingState.MEMBERSHIP_CHECK,
            OnboardingState.MEMBERSHIP_CHECK: OnboardingState.COLLECTING_NAME,
            OnboardingState.COLLECTING_NAME: OnboardingState.COLLECTING_NICKNAME,
            OnboardingState.COLLECTING_NICKNAME: OnboardingState.SELECTING_TRACK,
            OnboardingState.SELECTING_TRACK: OnboardingState.SELECTING_GRADE_BAND,
            OnboardingState.SELECTING_GRADE_BAND: OnboardingState.SELECTING_GRADE_YEAR,
            OnboardingState.SELECTING_GRADE_YEAR: OnboardingState.COLLECTING_PHONE,
            OnboardingState.COLLECTING_PHONE: OnboardingState.WELCOME,
            OnboardingState.WELCOME: OnboardingState.COMPLETED,
        }
        
        return state_map.get(self.current_state, OnboardingState.ERROR)
    
    def set_state(self, state: OnboardingState) -> None:
        """Set current state"""
        self.current_state = state
    
    def is_completed(self) -> bool:
        """Check if onboarding is completed"""
        return self.current_state == OnboardingState.COMPLETED
    
    def has_error(self) -> bool:
        """Check if in error state"""
        return self.current_state == OnboardingState.ERROR
    
    def increment_error(self) -> None:
        """Increment error count"""
        self.error_count += 1
        if self.error_count >= self.max_errors:
            self.current_state = OnboardingState.ERROR
    
    def reset_error(self) -> None:
        """Reset error count"""
        self.error_count = 0
    
    def get_progress(self) -> float:
        """Get onboarding progress (0.0 to 1.0)"""
        state_order = [
            OnboardingState.INTRO,
            OnboardingState.MEMBERSHIP_CHECK,
            OnboardingState.COLLECTING_NAME,
            OnboardingState.COLLECTING_NICKNAME,
            OnboardingState.SELECTING_TRACK,
            OnboardingState.SELECTING_GRADE_BAND,
            OnboardingState.SELECTING_GRADE_YEAR,
            OnboardingState.COLLECTING_PHONE,
            OnboardingState.WELCOME,
            OnboardingState.COMPLETED
        ]
        
        try:
            current_index = state_order.index(self.current_state)
            return (current_index + 1) / len(state_order)
        except ValueError:
            return 0.0




