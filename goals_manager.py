"""
Goals manager using JSON file storage.
"""
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from pathlib import Path

class GoalsManager:
    """Manage user goals with JSON file persistence."""
    
    def __init__(self, data_dir: str = "data/goals"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_user_file(self, user_id: str) -> Path:
        """Get the JSON file path for a user."""
        return self.data_dir / f"{user_id}.json"
    
    def _load_goals(self, user_id: str) -> List[Dict[str, Any]]:
        """Load goals from JSON file."""
        file_path = self._get_user_file(user_id)
        
        if not file_path.exists():
            return []
        
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    
    def _save_goals(self, user_id: str, goals: List[Dict[str, Any]]) -> None:
        """Save goals to JSON file."""
        file_path = self._get_user_file(user_id)
        
        with open(file_path, 'w') as f:
            json.dump(goals, f, indent=2, default=str)
    
    def list_goals(self, user_id: str) -> List[Dict[str, Any]]:
        """List all goals for a user."""
        return self._load_goals(user_id)
    
    def create_goal(self, user_id: str, goal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new goal."""
        goals = self._load_goals(user_id)
        
        # Create new goal with generated ID and preserve all fields
        new_goal = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'name': goal_data['name'],
            'target_amount': goal_data['target_amount'],
            'current_amount': goal_data.get('current_amount', 0),
            'target_date': goal_data['target_date'],
            'category': goal_data.get('category'),
            'description': goal_data.get('description'),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'is_active': True
        }
        
        # Preserve any additional fields (like AI estimation data)
        for key, value in goal_data.items():
            if key not in new_goal and value is not None:
                new_goal[key] = value
        
        goals.append(new_goal)
        self._save_goals(user_id, goals)
        
        return new_goal
    
    def get_goal(self, user_id: str, goal_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific goal by ID."""
        goals = self._load_goals(user_id)
        
        for goal in goals:
            if goal['id'] == goal_id:
                return goal
        
        return None
    
    def update_goal(self, user_id: str, goal_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a goal."""
        goals = self._load_goals(user_id)
        
        for i, goal in enumerate(goals):
            if goal['id'] == goal_id:
                # Update all fields, not just basic ones
                for key, value in updates.items():
                    if value is not None:
                        goal[key] = value
                
                goal['updated_at'] = datetime.utcnow().isoformat()
                goals[i] = goal
                self._save_goals(user_id, goals)
                return goal
        
        return None
    
    def delete_goal(self, user_id: str, goal_id: str) -> bool:
        """Delete a goal."""
        goals = self._load_goals(user_id)
        original_count = len(goals)
        
        goals = [g for g in goals if g['id'] != goal_id]
        
        if len(goals) < original_count:
            self._save_goals(user_id, goals)
            return True
        
        return False
    
    def calculate_goal_progress(self, goal: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate progress metrics for a goal."""
        target_amount = goal['target_amount']
        current_amount = goal['current_amount']
        target_date = datetime.fromisoformat(goal['target_date'].replace('Z', '+00:00'))
        
        # Calculate progress
        progress_percentage = (current_amount / target_amount * 100) if target_amount > 0 else 0
        
        # Calculate days remaining
        days_remaining = (target_date - datetime.utcnow()).days
        months_remaining = max(days_remaining / 30, 1)  # At least 1 month
        
        # Calculate monthly required
        amount_remaining = target_amount - current_amount
        monthly_required = amount_remaining / months_remaining if months_remaining > 0 else amount_remaining
        
        # Check if on track (simplified)
        expected_progress = (1 - (days_remaining / 365)) * 100  # Assuming 1 year goals
        on_track = progress_percentage >= expected_progress * 0.8  # 80% of expected
        
        return {
            'goal_id': goal['id'],
            'name': goal['name'],
            'target_amount': target_amount,
            'current_amount': current_amount,
            'target_date': goal['target_date'],
            'progress_percentage': round(progress_percentage, 2),
            'monthly_required': round(monthly_required, 2),
            'days_remaining': days_remaining,
            'on_track': on_track
        }

# Create singleton instance
goals_manager = GoalsManager() 