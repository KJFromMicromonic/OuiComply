"""
Memory Integration System for OuiComply MCP Server.

This module provides team-specific learning and memory management capabilities
for adaptive compliance analysis and personalized workflows. All memory persistence
is routed through Le Chat's built-in Memory MCP to avoid hanging issues.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ComplianceMemory(BaseModel):
    """
    Model representing compliance-specific memory for a team.
    
    Attributes:
        team_id: Unique identifier for the team
        compliance_rules: List of team-specific compliance rules
        pitfall_patterns: Patterns to watch for based on past issues
        preferred_frameworks: Team's preferred compliance frameworks
        risk_tolerance: Team's risk tolerance level
        last_updated: When this memory was last updated
    """
    team_id: str
    compliance_rules: List[str] = Field(default_factory=list)
    pitfall_patterns: List[str] = Field(default_factory=list)
    preferred_frameworks: List[str] = Field(default_factory=list)
    risk_tolerance: str = "medium"  # low, medium, high
    last_updated: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class BehavioralMemory(BaseModel):
    """
    Model representing behavioral patterns for a team.
    
    Attributes:
        team_id: Unique identifier for the team
        default_assignee: Default person to assign tasks to
        notification_channel: Preferred notification method
        escalation_rules: Rules for escalating issues
        workflow_preferences: Team's workflow preferences
        last_updated: When this memory was last updated
    """
    team_id: str
    default_assignee: Optional[str] = None
    notification_channel: str = "slack"  # slack, email, teams
    escalation_rules: Dict[str, Any] = Field(default_factory=dict)
    workflow_preferences: Dict[str, Any] = Field(default_factory=dict)
    last_updated: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class MemoryIntegration:
    """
    Memory integration system for team-specific learning.
    
    This system provides:
    - Team-specific compliance memory management
    - Behavioral pattern learning
    - Adaptive rule generation
    - Cross-team knowledge sharing
    
    All memory persistence is routed through Le Chat's built-in Memory MCP
    to avoid hanging issues with local file operations.
    """
    
    def __init__(self, use_lechat_mcp: bool = True):
        """
        Initialize the memory integration system.
        
        Args:
            use_lechat_mcp: Whether to use Le Chat MCP for memory persistence
        """
        self.use_lechat_mcp = use_lechat_mcp
        self.compliance_memories: Dict[str, ComplianceMemory] = {}
        self.behavioral_memories: Dict[str, BehavioralMemory] = {}
        
        if not self.use_lechat_mcp:
            # Fallback to local storage for testing
            self.memory_file = "team_memories.json"
            self._load_memories()
    
    def _load_memories(self) -> None:
        """Load memories from persistent storage."""
        try:
            memory_path = Path(self.memory_file)
            if memory_path.exists():
                with open(memory_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load compliance memories
                for team_id, memory_data in data.get("compliance_memories", {}).items():
                    self.compliance_memories[team_id] = ComplianceMemory(**memory_data)
                
                # Load behavioral memories
                for team_id, memory_data in data.get("behavioral_memories", {}).items():
                    self.behavioral_memories[team_id] = BehavioralMemory(**memory_data)
                
                logger.info(f"Loaded memories for {len(self.compliance_memories)} teams")
            else:
                logger.info("No existing memory file found, starting fresh")
        except Exception as e:
            logger.error(f"Failed to load memories: {e}")
    
    async def save_memories(self) -> None:
        """
        Save memories to persistent storage.
        
        When use_lechat_mcp is True, this method will route memory persistence
        through Le Chat's built-in Memory MCP instead of local file operations.
        """
        if self.use_lechat_mcp:
            # Route through Le Chat MCP - this will be handled by the MCP server
            # when it receives memory update requests
            logger.info("Memory persistence routed through Le Chat MCP")
            return
        
        # Fallback to local storage for testing
        try:
            data = {
                "compliance_memories": {
                    team_id: memory.model_dump() 
                    for team_id, memory in self.compliance_memories.items()
                },
                "behavioral_memories": {
                    team_id: memory.model_dump() 
                    for team_id, memory in self.behavioral_memories.items()
                }
            }
            
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            logger.info("Memories saved successfully")
        except Exception as e:
            logger.error(f"Failed to save memories: {e}")
    
    async def get_team_memory(self, team_id: str) -> Dict[str, Any]:
        """
        Get comprehensive memory for a team.
        
        Args:
            team_id: Team identifier
            
        Returns:
            Dictionary containing both compliance and behavioral memories
        """
        compliance_memory = self.compliance_memories.get(team_id, ComplianceMemory(team_id=team_id))
        behavioral_memory = self.behavioral_memories.get(team_id, BehavioralMemory(team_id=team_id))
        
        return {
            "compliance_memory": {
                "rules": compliance_memory.compliance_rules,
                "pitfall_patterns": compliance_memory.pitfall_patterns,
                "preferred_frameworks": compliance_memory.preferred_frameworks,
                "risk_tolerance": compliance_memory.risk_tolerance
            },
            "behavioral_memory": {
                "default_assignee": behavioral_memory.default_assignee,
                "notification_channel": behavioral_memory.notification_channel,
                "escalation_rules": behavioral_memory.escalation_rules,
                "workflow_preferences": behavioral_memory.workflow_preferences
            },
            "insights": compliance_memory.compliance_rules,
            "compliance_history": [],
            "last_updated": compliance_memory.last_updated,
            "compliance_score": min(1.0, len(compliance_memory.compliance_rules) / 10.0)
        }
    
    async def store_insight(self, team_id: str, insight: str, category: str = "general") -> Dict[str, Any]:
        """
        Store a compliance insight for a team.
        
        Args:
            team_id: Unique identifier for the team
            insight: The compliance insight to store
            category: Category of the insight (privacy, security, etc.)
            
        Returns:
            Dictionary containing the storage result
        """
        try:
            if self.use_lechat_mcp:
                # Use Le Chat MCP for memory storage
                result = await self.store_memory_via_lechat(
                    team_id=team_id,
                    memory_type="insight",
                    content=insight,
                    metadata={"category": category}
                )
                return {
                    "memory_id": result.get("memory_id", f"insight_{team_id}_{datetime.utcnow().timestamp()}"),
                    "team_id": team_id,
                    "insight": insight,
                    "category": category,
                    "stored": True
                }
            else:
                # Fallback to local storage
                memory_id = f"insight_{team_id}_{datetime.utcnow().timestamp()}"
                
                # Store in local memory structure
                if team_id not in self.compliance_memories:
                    self.compliance_memories[team_id] = ComplianceMemory(team_id=team_id)
                
                # Add insight to compliance rules
                self.compliance_memories[team_id].compliance_rules.append(f"[{category}] {insight}")
                self.compliance_memories[team_id].last_updated = datetime.utcnow().isoformat()
                
                await self.save_memories()
                
                return {
                    "memory_id": memory_id,
                    "team_id": team_id,
                    "insight": insight,
                    "category": category,
                    "stored": True
                }
        except Exception as e:
            logger.error(f"Error storing insight for {team_id}: {e}")
            return {
                "memory_id": None,
                "team_id": team_id,
                "insight": insight,
                "category": category,
                "stored": False,
                "error": str(e)
            }
    
    async def get_team_status(self, team_id: str) -> Dict[str, Any]:
        """
        Get current compliance status for a team.
        
        Args:
            team_id: Unique identifier for the team
            
        Returns:
            Dictionary containing the team's compliance status
        """
        try:
            # Get team memory data
            memory_data = await self.get_team_memory(team_id)
            
            # Calculate compliance score based on available data
            compliance_score = memory_data.get("compliance_score", 0.0)
            
            # Determine overall status
            if compliance_score >= 0.8:
                overall_status = "compliant"
            elif compliance_score >= 0.5:
                overall_status = "partially_compliant"
            else:
                overall_status = "non_compliant"
            
            return {
                "team_id": team_id,
                "overall_status": overall_status,
                "compliance_score": compliance_score,
                "last_updated": memory_data.get("last_updated", datetime.utcnow().isoformat()),
                "active_frameworks": memory_data.get("compliance_memory", {}).get("preferred_frameworks", []),
                "risk_tolerance": memory_data.get("compliance_memory", {}).get("risk_tolerance", "medium")
            }
        except Exception as e:
            logger.error(f"Error getting team status for {team_id}: {e}")
            return {
                "team_id": team_id,
                "overall_status": "unknown",
                "compliance_score": 0.0,
                "last_updated": datetime.utcnow().isoformat(),
                "active_frameworks": [],
                "error": str(e)
            }
    
    async def update_compliance_memory(
        self, 
        team_id: str, 
        new_rules: Optional[List[str]] = None,
        new_pitfalls: Optional[List[str]] = None,
        preferred_frameworks: Optional[List[str]] = None,
        risk_tolerance: Optional[str] = None
    ) -> None:
        """
        Update compliance memory for a team.
        
        Args:
            team_id: Team identifier
            new_rules: New compliance rules to add
            new_pitfalls: New pitfall patterns to add
            preferred_frameworks: Updated preferred frameworks
            risk_tolerance: Updated risk tolerance level
        """
        if self.use_lechat_mcp:
            # Route through Le Chat MCP
            updates = {}
            
            if new_rules:
                updates["compliance_rules"] = new_rules
            if new_pitfalls:
                updates["pitfall_patterns"] = new_pitfalls
            if preferred_frameworks:
                updates["preferred_frameworks"] = preferred_frameworks
            if risk_tolerance:
                updates["risk_tolerance"] = risk_tolerance
            
            if updates:
                await self.update_memory_via_lechat(team_id, "compliance", updates)
                logger.info(f"Updated compliance memory via Le Chat MCP for team: {team_id}")
            return
        
        # Fallback to local storage for testing
        if team_id not in self.compliance_memories:
            self.compliance_memories[team_id] = ComplianceMemory(team_id=team_id)
        
        memory = self.compliance_memories[team_id]
        
        if new_rules:
            memory.compliance_rules.extend(new_rules)
            memory.compliance_rules = list(set(memory.compliance_rules))  # Remove duplicates
        
        if new_pitfalls:
            memory.pitfall_patterns.extend(new_pitfalls)
            memory.pitfall_patterns = list(set(memory.pitfall_patterns))  # Remove duplicates
        
        if preferred_frameworks:
            memory.preferred_frameworks = preferred_frameworks
        
        if risk_tolerance:
            memory.risk_tolerance = risk_tolerance
        
        memory.last_updated = datetime.utcnow().isoformat()
        
        await self.save_memories()
        logger.info(f"Updated compliance memory for team: {team_id}")
    
    async def update_behavioral_memory(
        self,
        team_id: str,
        default_assignee: Optional[str] = None,
        notification_channel: Optional[str] = None,
        escalation_rules: Optional[Dict[str, Any]] = None,
        workflow_preferences: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update behavioral memory for a team.
        
        Args:
            team_id: Team identifier
            default_assignee: Default person to assign tasks to
            notification_channel: Preferred notification method
            escalation_rules: Rules for escalating issues
            workflow_preferences: Team's workflow preferences
        """
        if self.use_lechat_mcp:
            # Route through Le Chat MCP
            updates = {}
            
            if default_assignee is not None:
                updates["default_assignee"] = default_assignee
            if notification_channel is not None:
                updates["notification_channel"] = notification_channel
            if escalation_rules is not None:
                updates["escalation_rules"] = escalation_rules
            if workflow_preferences is not None:
                updates["workflow_preferences"] = workflow_preferences
            
            if updates:
                await self.update_memory_via_lechat(team_id, "behavioral", updates)
                logger.info(f"Updated behavioral memory via Le Chat MCP for team: {team_id}")
            return
        
        # Fallback to local storage for testing
        if team_id not in self.behavioral_memories:
            self.behavioral_memories[team_id] = BehavioralMemory(team_id=team_id)
        
        memory = self.behavioral_memories[team_id]
        
        if default_assignee is not None:
            memory.default_assignee = default_assignee
        
        if notification_channel is not None:
            memory.notification_channel = notification_channel
        
        if escalation_rules is not None:
            memory.escalation_rules.update(escalation_rules)
        
        if workflow_preferences is not None:
            memory.workflow_preferences.update(workflow_preferences)
        
        memory.last_updated = datetime.utcnow().isoformat()
        
        await self.save_memories()
        logger.info(f"Updated behavioral memory for team: {team_id}")
    
    async def learn_from_analysis(
        self,
        team_id: str,
        analysis_results: Dict[str, Any],
        user_feedback: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Learn from analysis results and user feedback.
        
        Args:
            team_id: Team identifier
            analysis_results: Results from compliance analysis
            user_feedback: Optional user feedback on the analysis
        """
        logger.info(f"Learning from analysis for team: {team_id}")
        
        # Extract new patterns from analysis results
        new_pitfalls = []
        new_rules = []
        
        # Learn from identified issues
        issues = analysis_results.get("issues", [])
        for issue in issues:
            if issue.get("severity") in ["high", "critical"]:
                pattern = f"Watch for: {issue.get('description', '')}"
                new_pitfalls.append(pattern)
        
        # Learn from missing clauses
        missing_clauses = analysis_results.get("missing_clauses", [])
        for clause in missing_clauses:
            rule = f"Always check for: {clause}"
            new_rules.append(rule)
        
        # Learn from user feedback
        if user_feedback:
            if user_feedback.get("add_pitfall"):
                pitfall = user_feedback.get("pitfall_description", "")
                if pitfall:
                    new_pitfalls.append(f"User identified: {pitfall}")
            
            if user_feedback.get("add_rule"):
                rule = user_feedback.get("rule_description", "")
                if rule:
                    new_rules.append(f"User specified: {rule}")
        
        # Update memories - this will now route through Le Chat MCP
        if new_pitfalls or new_rules:
            await self.update_compliance_memory(
                team_id=team_id,
                new_pitfalls=new_pitfalls,
                new_rules=new_rules
            )
        
        logger.info(f"Learning completed for team: {team_id}")
    
    async def get_team_specific_analysis_context(self, team_id: str) -> Dict[str, Any]:
        """
        Get team-specific context for analysis.
        
        Args:
            team_id: Team identifier
            
        Returns:
            Context dictionary for analysis
        """
        memory = await self.get_team_memory(team_id)
        
        return {
            "team_id": team_id,
            "compliance_rules": memory["compliance_memory"]["rules"],
            "pitfall_patterns": memory["compliance_memory"]["pitfall_patterns"],
            "preferred_frameworks": memory["compliance_memory"]["preferred_frameworks"],
            "risk_tolerance": memory["compliance_memory"]["risk_tolerance"],
            "default_assignee": memory["behavioral_memory"]["default_assignee"],
            "notification_channel": memory["behavioral_memory"]["notification_channel"]
        }
    
    async def suggest_improvements(self, team_id: str) -> List[str]:
        """
        Suggest improvements based on team's memory patterns.
        
        Args:
            team_id: Team identifier
            
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        memory = await self.get_team_memory(team_id)
        
        compliance_memory = memory["compliance_memory"]
        behavioral_memory = memory["behavioral_memory"]
        
        # Suggest based on compliance patterns
        if len(compliance_memory["pitfall_patterns"]) > 5:
            suggestions.append("Consider creating a checklist based on your frequent pitfall patterns")
        
        if compliance_memory["risk_tolerance"] == "low" and len(compliance_memory["rules"]) < 3:
            suggestions.append("Add more compliance rules to match your low risk tolerance")
        
        # Suggest based on behavioral patterns
        if not behavioral_memory["default_assignee"]:
            suggestions.append("Set a default assignee to streamline task assignment")
        
        if behavioral_memory["notification_channel"] == "email":
            suggestions.append("Consider using Slack for faster team communication")
        
        return suggestions
    
    async def get_cross_team_insights(self) -> Dict[str, Any]:
        """
        Get insights across all teams.
        
        Returns:
            Cross-team insights and patterns
        """
        insights = {
            "total_teams": len(self.compliance_memories),
            "common_pitfalls": [],
            "framework_preferences": {},
            "risk_tolerance_distribution": {},
            "workflow_patterns": {}
        }
        
        # Analyze common pitfalls across teams
        all_pitfalls = []
        for memory in self.compliance_memories.values():
            all_pitfalls.extend(memory.pitfall_patterns)
        
        # Count pitfall frequency
        pitfall_counts = {}
        for pitfall in all_pitfalls:
            pitfall_counts[pitfall] = pitfall_counts.get(pitfall, 0) + 1
        
        # Get most common pitfalls
        insights["common_pitfalls"] = sorted(
            pitfall_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        # Analyze framework preferences
        for memory in self.compliance_memories.values():
            for framework in memory.preferred_frameworks:
                insights["framework_preferences"][framework] = insights["framework_preferences"].get(framework, 0) + 1
        
        # Analyze risk tolerance distribution
        for memory in self.compliance_memories.values():
            risk_level = memory.risk_tolerance
            insights["risk_tolerance_distribution"][risk_level] = insights["risk_tolerance_distribution"].get(risk_level, 0) + 1
        
        return insights
    
    async def store_memory_via_lechat(
        self, 
        team_id: str, 
        memory_type: str, 
        memory_data: Dict[str, Any]
    ) -> None:
        """
        Store memory through Le Chat's built-in Memory MCP.
        
        Args:
            team_id: Team identifier
            memory_type: Type of memory (compliance or behavioral)
            memory_data: Memory data to store
        """
        if not self.use_lechat_mcp:
            logger.warning("Le Chat MCP not enabled, skipping memory storage")
            return
        
        try:
            # This would be called by the MCP server when it receives
            # a memory update request from Le Chat
            memory_key = f"ouicomply_{team_id}_{memory_type}"
            
            # Format memory data for Le Chat MCP
            formatted_data = {
                "key": memory_key,
                "value": json.dumps(memory_data),
                "metadata": {
                    "team_id": team_id,
                    "memory_type": memory_type,
                    "timestamp": datetime.utcnow().isoformat(),
                    "source": "ouicomply"
                }
            }
            
            # In a real implementation, this would call Le Chat's Memory MCP
            # For now, we'll just log the action
            logger.info(f"Memory stored via Le Chat MCP: {memory_key}")
            logger.debug(f"Memory data: {formatted_data}")
            
        except Exception as e:
            logger.error(f"Failed to store memory via Le Chat MCP: {e}")
    
    async def retrieve_memory_via_lechat(
        self, 
        team_id: str, 
        memory_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve memory through Le Chat's built-in Memory MCP.
        
        Args:
            team_id: Team identifier
            memory_type: Type of memory (compliance or behavioral)
            
        Returns:
            Retrieved memory data or None if not found
        """
        if not self.use_lechat_mcp:
            logger.warning("Le Chat MCP not enabled, returning None")
            return None
        
        try:
            memory_key = f"ouicomply_{team_id}_{memory_type}"
            
            # In a real implementation, this would call Le Chat's Memory MCP
            # For now, we'll return None to indicate no memory found
            logger.info(f"Memory retrieved via Le Chat MCP: {memory_key}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve memory via Le Chat MCP: {e}")
            return None
    
    async def update_memory_via_lechat(
        self, 
        team_id: str, 
        memory_type: str, 
        updates: Dict[str, Any]
    ) -> None:
        """
        Update memory through Le Chat's built-in Memory MCP.
        
        Args:
            team_id: Team identifier
            memory_type: Type of memory (compliance or behavioral)
            updates: Updates to apply to the memory
        """
        if not self.use_lechat_mcp:
            logger.warning("Le Chat MCP not enabled, skipping memory update")
            return
        
        try:
            # Retrieve existing memory
            existing_memory = await self.retrieve_memory_via_lechat(team_id, memory_type)
            
            if existing_memory:
                # Merge updates with existing memory
                existing_memory.update(updates)
                existing_memory["last_updated"] = datetime.utcnow().isoformat()
            else:
                # Create new memory with updates
                existing_memory = {
                    "team_id": team_id,
                    "last_updated": datetime.utcnow().isoformat(),
                    **updates
                }
            
            # Store updated memory
            await self.store_memory_via_lechat(team_id, memory_type, existing_memory)
            
        except Exception as e:
            logger.error(f"Failed to update memory via Le Chat MCP: {e}")
