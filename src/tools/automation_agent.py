"""
Automation Agent for OuiComply MCP Server.

This module provides automation capabilities for Linear, Slack, and GitHub integration
to streamline compliance workflows and task management.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class LinearTask(BaseModel):
    """
    Model representing a Linear task.
    
    Attributes:
        title: Task title
        description: Task description
        priority: Task priority (1-4, where 1 is urgent)
        assignee: Person assigned to the task
        team: Team the task belongs to
        labels: List of labels for the task
        due_date: When the task is due
        external_id: External reference ID
    """
    title: str
    description: str
    priority: int = Field(ge=1, le=4, default=2)
    assignee: Optional[str] = None
    team: str
    labels: List[str] = Field(default_factory=list)
    due_date: Optional[str] = None
    external_id: Optional[str] = None


class SlackMessage(BaseModel):
    """
    Model representing a Slack message.
    
    Attributes:
        channel: Slack channel to send to
        text: Message text
        blocks: Rich message blocks (optional)
        attachments: Message attachments (optional)
        thread_ts: Thread timestamp for replies
    """
    channel: str
    text: str
    blocks: Optional[List[Dict[str, Any]]] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    thread_ts: Optional[str] = None


class GitHubIssue(BaseModel):
    """
    Model representing a GitHub issue.
    
    Attributes:
        title: Issue title
        body: Issue description
        labels: List of labels
        assignees: List of assignees
        milestone: Milestone number
        state: Issue state (open, closed)
    """
    title: str
    body: str
    labels: List[str] = Field(default_factory=list)
    assignees: List[str] = Field(default_factory=list)
    milestone: Optional[int] = None
    state: str = "open"


class AutomationResult(BaseModel):
    """
    Result of automation actions.
    
    Attributes:
        success: Whether the automation was successful
        actions_taken: List of actions that were taken
        errors: List of any errors that occurred
        external_ids: Mapping of action types to external IDs
        timestamp: When the automation was performed
    """
    success: bool
    actions_taken: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    external_ids: Dict[str, str] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class AutomationAgent:
    """
    Automation agent for prompting Le Chat to use native MCP servers.
    
    This agent provides:
    - Prompts for Linear task creation via Le Chat's Linear MCP server
    - Prompts for Slack notifications via Le Chat's Slack MCP server
    - Prompts for GitHub issue creation via Le Chat's GitHub MCP server
    - Workflow automation guidance based on compliance results
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the automation agent.
        
        Args:
            config: Configuration dictionary (not needed since we use Le Chat's MCP servers)
        """
        self.config = config or {}
        # No API keys needed - we'll prompt Le Chat to use its native MCP servers
    
    async def generate_linear_prompt(
        self, 
        task: LinearTask,
        team_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a prompt for Le Chat to create a Linear task using its MCP server.
        
        Args:
            task: Linear task to create
            team_id: Linear team ID (optional)
            
        Returns:
            Prompt for Le Chat to execute
        """
        logger.info(f"Generating Linear task prompt: {task.title}")
        
        try:
            # Generate prompt for Le Chat to use its Linear MCP server
            prompt = f"""
            Please use your Linear MCP server to create a new task with the following details:
            
            **Task Title:** {task.title}
            **Description:** {task.description}
            **Priority:** {task.priority} (1=urgent, 4=low)
            **Team:** {team_id or 'Default Team'}
            **Assignee:** {task.assignee or 'Unassigned'}
            **Labels:** {', '.join(task.labels) if task.labels else 'None'}
            **Due Date:** {task.due_date or 'No due date'}
            
            Please create this task and return the task ID and URL.
            """
            
            return {
                "success": True,
                "prompt": prompt,
                "action_type": "linear_task_creation",
                "task_details": task.model_dump()
            }
                
        except Exception as e:
            logger.error(f"Linear prompt generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_slack_prompt(self, message: SlackMessage) -> Dict[str, Any]:
        """
        Generate a prompt for Le Chat to send a Slack message using its MCP server.
        
        Args:
            message: Slack message to send
            
        Returns:
            Prompt for Le Chat to execute
        """
        logger.info(f"Generating Slack message prompt for channel: {message.channel}")
        
        try:
            # Generate prompt for Le Chat to use its Slack MCP server
            prompt = f"""
            Please use your Slack MCP server to send a message with the following details:
            
            **Channel:** {message.channel}
            **Message Text:** {message.text}
            """
            
            if message.blocks:
                prompt += f"\n**Rich Blocks:** {json.dumps(message.blocks, indent=2)}"
            
            if message.attachments:
                prompt += f"\n**Attachments:** {json.dumps(message.attachments, indent=2)}"
            
            if message.thread_ts:
                prompt += f"\n**Thread Reply to:** {message.thread_ts}"
            
            prompt += "\n\nPlease send this message and confirm delivery."
            
            return {
                "success": True,
                "prompt": prompt,
                "action_type": "slack_message",
                "message_details": message.model_dump()
            }
                    
        except Exception as e:
            logger.error(f"Slack prompt generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_github_prompt(self, issue: GitHubIssue) -> Dict[str, Any]:
        """
        Generate a prompt for Le Chat to create a GitHub issue using its MCP server.
        
        Args:
            issue: GitHub issue to create
            
        Returns:
            Prompt for Le Chat to execute
        """
        logger.info(f"Generating GitHub issue prompt: {issue.title}")
        
        try:
            # Generate prompt for Le Chat to use its GitHub MCP server
            prompt = f"""
            Please use your GitHub MCP server to create a new issue with the following details:
            
            **Title:** {issue.title}
            **Body:** {issue.body}
            **Labels:** {', '.join(issue.labels) if issue.labels else 'None'}
            **Assignees:** {', '.join(issue.assignees) if issue.assignees else 'None'}
            **State:** {issue.state}
            """
            
            if issue.milestone:
                prompt += f"\n**Milestone:** {issue.milestone}"
            
            prompt += "\n\nPlease create this issue and return the issue number and URL."
            
            return {
                "success": True,
                "prompt": prompt,
                "action_type": "github_issue_creation",
                "issue_details": issue.model_dump()
            }
                
        except Exception as e:
            logger.error(f"GitHub prompt generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_automation_prompts(
        self,
        analysis_results: Dict[str, Any],
        team_context: str,
        assignee: Optional[str] = None
    ) -> AutomationResult:
        """
        Generate prompts for Le Chat to automate compliance workflow using its MCP servers.
        
        Args:
            analysis_results: Results from compliance analysis
            team_context: Team context for personalization
            assignee: Default assignee for tasks
            
        Returns:
            Automation result with generated prompts
        """
        logger.info(f"Generating automation prompts for team: {team_context}")
        
        result = AutomationResult(success=True)
        prompts = []
        
        try:
            # Extract key information
            issues = analysis_results.get("issues", [])
            missing_clauses = analysis_results.get("missing_clauses", [])
            risk_level = analysis_results.get("risk_level", "medium")
            document_name = analysis_results.get("document_name", "Unknown Document")
            
            # Generate Linear task prompt for critical issues
            if issues:
                critical_issues = [i for i in issues if i.get("severity") == "critical"]
                if critical_issues:
                    task_title = f"URGENT: Address {len(critical_issues)} critical compliance issues in {document_name}"
                    task_description = self._generate_task_description(critical_issues, missing_clauses)
                    
                    linear_task = LinearTask(
                        title=task_title,
                        description=task_description,
                        priority=1,  # Urgent
                        assignee=assignee,
                        team=team_context,
                        labels=["compliance", "urgent", "legal"],
                        due_date=self._calculate_due_date("critical"),
                        external_id=f"compliance_{int(asyncio.get_event_loop().time())}"
                    )
                    
                    linear_prompt = await self.generate_linear_prompt(linear_task)
                    if linear_prompt["success"]:
                        prompts.append(linear_prompt)
                        result.actions_taken.append("Generated Linear task creation prompt")
                    else:
                        result.errors.append(f"Failed to generate Linear prompt: {linear_prompt.get('error')}")
            
            # Generate Slack notification prompt
            slack_message = self._generate_slack_message(analysis_results, team_context)
            slack_prompt = await self.generate_slack_prompt(slack_message)
            if slack_prompt["success"]:
                prompts.append(slack_prompt)
                result.actions_taken.append("Generated Slack notification prompt")
            else:
                result.errors.append(f"Failed to generate Slack prompt: {slack_prompt.get('error')}")
            
            # Generate GitHub issue prompt for audit trail
            github_issue = self._generate_github_issue(analysis_results, team_context)
            github_prompt = await self.generate_github_prompt(github_issue)
            if github_prompt["success"]:
                prompts.append(github_prompt)
                result.actions_taken.append("Generated GitHub issue creation prompt")
            else:
                result.errors.append(f"Failed to generate GitHub prompt: {github_prompt.get('error')}")
            
            # Store prompts in external_ids for easy access
            result.external_ids["prompts"] = prompts
            
            # Update result success based on any errors
            if result.errors:
                result.success = len(result.errors) < len(result.actions_taken)
            
            logger.info(f"Automation prompts generated - actions: {len(result.actions_taken)}, errors: {len(result.errors)}")
            return result
            
        except Exception as e:
            logger.error(f"Automation prompt generation failed: {e}")
            result.success = False
            result.errors.append(str(e))
            return result
    
    def _generate_task_description(self, issues: List[Dict[str, Any]], missing_clauses: List[str]) -> str:
        """Generate task description from issues and missing clauses."""
        description = "## Compliance Issues Found\n\n"
        
        for i, issue in enumerate(issues, 1):
            description += f"### {i}. {issue.get('description', 'Unknown issue')}\n"
            description += f"- **Severity:** {issue.get('severity', 'unknown').upper()}\n"
            description += f"- **Category:** {issue.get('category', 'unknown')}\n"
            description += f"- **Location:** {issue.get('location', 'Not specified')}\n"
            description += f"- **Recommendation:** {issue.get('recommendation', 'No recommendation')}\n\n"
        
        if missing_clauses:
            description += "## Missing Required Clauses\n\n"
            for clause in missing_clauses:
                description += f"- {clause}\n"
        
        description += "\n---\n*This task was automatically generated by OuiComply MCP Server*"
        
        return description
    
    def _generate_slack_message(self, analysis_results: Dict[str, Any], team_context: str) -> SlackMessage:
        """Generate Slack message from analysis results."""
        status = analysis_results.get("overall_status", "unknown")
        risk_level = analysis_results.get("risk_level", "unknown")
        issues_count = len(analysis_results.get("issues", []))
        document_name = analysis_results.get("document_name", "Unknown Document")
        
        # Determine channel based on team
        channel_map = {
            "procurement team": "#procurement-compliance",
            "sales team": "#sales-compliance",
            "legal team": "#legal-compliance",
            "hr team": "#hr-compliance",
            "finance team": "#finance-compliance"
        }
        
        channel = channel_map.get(team_context.lower(), "#compliance-alerts")
        
        # Create message text
        text = f"🔍 *Compliance Analysis Complete*\n\n"
        text += f"*Document:* {document_name}\n"
        text += f"*Team:* {team_context}\n"
        text += f"*Status:* {status.upper()}\n"
        text += f"*Risk Level:* {risk_level.upper()}\n"
        text += f"*Issues Found:* {issues_count}\n\n"
        
        if issues_count > 0:
            text += "⚠️ *Action Required* - Please review the Linear task for details"
        else:
            text += "✅ *No Issues Found* - Document appears compliant"
        
        # Create rich message blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🔍 Compliance Analysis Complete"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Document:*\n{document_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Team:*\n{team_context}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Status:*\n{status.upper()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Risk Level:*\n{risk_level.upper()}"
                    }
                ]
            }
        ]
        
        if issues_count > 0:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"⚠️ *{issues_count} issues found* - Check Linear for details"
                }
            })
        else:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "✅ *No issues found* - Document appears compliant"
                }
            })
        
        return SlackMessage(
            channel=channel,
            text=text,
            blocks=blocks
        )
    
    def _generate_github_issue(self, analysis_results: Dict[str, Any], team_context: str) -> GitHubIssue:
        """Generate GitHub issue from analysis results."""
        document_name = analysis_results.get("document_name", "Unknown Document")
        status = analysis_results.get("overall_status", "unknown")
        risk_level = analysis_results.get("risk_level", "unknown")
        issues = analysis_results.get("issues", [])
        missing_clauses = analysis_results.get("missing_clauses", [])
        
        title = f"Compliance Analysis: {document_name} - {status.upper()}"
        
        body = f"""# Compliance Analysis Report

**Document:** {document_name}  
**Team:** {team_context}  
**Status:** {status.upper()}  
**Risk Level:** {risk_level.upper()}  
**Analysis Date:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

## Summary

This issue tracks the compliance analysis results for {document_name}.

"""
        
        if issues:
            body += f"## Issues Found ({len(issues)})\n\n"
            for i, issue in enumerate(issues, 1):
                body += f"### {i}. {issue.get('description', 'Unknown issue')}\n"
                body += f"- **Severity:** {issue.get('severity', 'unknown').upper()}\n"
                body += f"- **Category:** {issue.get('category', 'unknown')}\n"
                body += f"- **Framework:** {issue.get('framework', 'unknown').upper()}\n"
                body += f"- **Location:** {issue.get('location', 'Not specified')}\n"
                body += f"- **Recommendation:** {issue.get('recommendation', 'No recommendation')}\n\n"
        
        if missing_clauses:
            body += f"## Missing Required Clauses ({len(missing_clauses)})\n\n"
            for clause in missing_clauses:
                body += f"- {clause}\n"
            body += "\n"
        
        body += """## Next Steps

- [ ] Review identified issues
- [ ] Address critical issues immediately
- [ ] Update document with missing clauses
- [ ] Schedule follow-up review

---
*Generated by OuiComply MCP Server v1.0.0*
"""
        
        # Determine labels based on analysis
        labels = ["compliance", "legal", "analysis"]
        if risk_level in ["high", "critical"]:
            labels.append("urgent")
        if issues:
            labels.append("issues-found")
        else:
            labels.append("compliant")
        
        return GitHubIssue(
            title=title,
            body=body,
            labels=labels
        )
    
    def _calculate_due_date(self, severity: str) -> str:
        """Calculate due date based on severity."""
        days_map = {
            "critical": 1,
            "high": 3,
            "medium": 7,
            "low": 14
        }
        
        days = days_map.get(severity, 7)
        due_date = datetime.utcnow() + timedelta(days=days)
        return due_date.isoformat()
    
    def _get_default_team_id(self) -> str:
        """Get default Linear team ID for prompt generation."""
        return self.config.get("linear_default_team_id", "Default Team")
    
    def _get_assignee_id(self, assignee: str) -> Optional[str]:
        """Get assignee name for prompt generation."""
        return assignee
    
    def _get_label_ids(self, labels: List[str]) -> List[str]:
        """Get label names for prompt generation."""
        return labels
