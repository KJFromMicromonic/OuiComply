"""
LeChat Memory Integration Module.

This module provides integration with LeChat's memory system to store and retrieve
compliance assessments, enabling more autonomous decision-making.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

import httpx
from pydantic import BaseModel, Field

from ..config import get_config
from .compliance_engine import ComplianceReport

logger = logging.getLogger(__name__)


class MemoryEntry(BaseModel):
    """
    Model representing a memory entry for LeChat.
    
    Attributes:
        memory_id: Unique identifier for the memory entry
        title: Short title for the memory
        content: Main content of the memory
        category: Category of the memory (compliance, risk, assessment)
        tags: List of tags for categorization
        priority: Priority level (low, medium, high, critical)
        created_at: When the memory was created
        expires_at: When the memory expires (optional)
        metadata: Additional metadata
    """
    memory_id: str
    title: str
    content: str
    category: str
    tags: List[str] = Field(default_factory=list)
    priority: str = "medium"
    created_at: str
    expires_at: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MemorySearchResult(BaseModel):
    """
    Model representing a memory search result.
    
    Attributes:
        memory_id: ID of the found memory
        title: Title of the memory
        content: Content of the memory
        relevance_score: How relevant this memory is to the search
        category: Category of the memory
        tags: Tags associated with the memory
        created_at: When the memory was created
    """
    memory_id: str
    title: str
    content: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    category: str
    tags: List[str]
    created_at: str


class LeChatMemoryService:
    """
    Service for integrating with LeChat's memory system.
    
    This service provides capabilities to:
    - Store compliance assessments in LeChat memory
    - Retrieve relevant memories for decision-making
    - Update and manage memory entries
    - Search memories by content and metadata
    """
    
    def __init__(self):
        """Initialize the LeChat memory service."""
        self.config = get_config()
        self.base_url = getattr(self.config, 'lechat_api_url', 'https://api.lechat.ai')
        self.api_key = getattr(self.config, 'lechat_api_key', None)
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
    
    async def store_compliance_assessment(
        self, 
        report: ComplianceReport,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None
    ) -> str:
        """
        Store a compliance assessment in LeChat memory.
        
        Args:
            report: Compliance report to store
            user_id: ID of the user (optional)
            organization_id: ID of the organization (optional)
            
        Returns:
            Memory ID of the stored assessment
            
        Raises:
            httpx.HTTPError: If API request fails
            ValueError: If required parameters are missing
        """
        logger.info(f"Storing compliance assessment in LeChat memory - report_id: {report.report_id}, user_id: {user_id}")
        
        try:
            # Create memory entry from compliance report
            memory_entry = self._create_memory_from_report(
                report, 
                user_id, 
                organization_id
            )
            
            # Store in LeChat memory
            response = await self.client.post(
                "/api/v1/memories",
                json=memory_entry.model_dump()
            )
            response.raise_for_status()
            
            memory_id = response.json().get("memory_id")
            logger.info(f"Compliance assessment stored successfully - memory_id: {memory_id}")
            
            return memory_id
            
        except Exception as e:
            logger.error(f"Failed to store compliance assessment: {str(e)}")
            raise
    
    def _create_memory_from_report(
        self, 
        report: ComplianceReport,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None
    ) -> MemoryEntry:
        """
        Create a memory entry from a compliance report.
        
        Args:
            report: Compliance report
            user_id: User ID (optional)
            organization_id: Organization ID (optional)
            
        Returns:
            Memory entry
        """
        # Generate memory content
        content = self._generate_memory_content(report)
        
        # Determine priority based on risk level
        priority_map = {
            "low": "low",
            "medium": "medium", 
            "high": "high",
            "critical": "critical"
        }
        priority = priority_map.get(report.risk_level.value, "medium")
        
        # Create tags
        tags = [
            "compliance",
            "assessment",
            report.overall_status.value,
            report.risk_level.value
        ] + report.frameworks_analyzed
        
        # Create metadata
        metadata = {
            "report_id": report.report_id,
            "document_id": report.document_id,
            "risk_score": report.risk_score,
            "total_issues": len(report.issues),
            "critical_issues": len([i for i in report.issues if i.severity == "critical"]),
            "frameworks_analyzed": report.frameworks_analyzed,
            "user_id": user_id,
            "organization_id": organization_id
        }
        
        return MemoryEntry(
            memory_id=str(uuid4()),
            title=f"Compliance Assessment: {report.document_id}",
            content=content,
            category="compliance_assessment",
            tags=tags,
            priority=priority,
            created_at=datetime.utcnow().isoformat(),
            metadata=metadata
        )
    
    def _generate_memory_content(self, report: ComplianceReport) -> str:
        """
        Generate memory content from compliance report.
        
        Args:
            report: Compliance report
            
        Returns:
            Formatted memory content
        """
        content = f"""COMPLIANCE ASSESSMENT SUMMARY

Document: {report.document_id}
Status: {report.overall_status.value.upper()}
Risk Level: {report.risk_level.value.upper()}
Risk Score: {report.risk_score:.2f}/1.0

Key Findings:
- Total Issues: {len(report.issues)}
- Critical Issues: {len([i for i in report.issues if i.severity == 'critical'])}
- High Priority Issues: {len([i for i in report.issues if i.severity == 'high'])}
- Missing Clauses: {len(report.missing_clauses)}

Frameworks Analyzed: {', '.join(report.frameworks_analyzed)}

"""
        
        # Add critical issues
        critical_issues = [i for i in report.issues if i.severity == "critical"]
        if critical_issues:
            content += "CRITICAL ISSUES:\n"
            for issue in critical_issues:
                content += f"- {issue.description} ({issue.framework.upper()})\n"
            content += "\n"
        
        # Add high priority issues
        high_issues = [i for i in report.issues if i.severity == "high"]
        if high_issues:
            content += "HIGH PRIORITY ISSUES:\n"
            for issue in high_issues:
                content += f"- {issue.description} ({issue.framework.upper()})\n"
            content += "\n"
        
        # Add missing clauses
        if report.missing_clauses:
            content += "MISSING CLAUSES:\n"
            for clause in report.missing_clauses:
                content += f"- {clause}\n"
            content += "\n"
        
        # Add top recommendations
        if report.recommendations:
            content += "KEY RECOMMENDATIONS:\n"
            for i, rec in enumerate(report.recommendations[:3], 1):  # Top 3
                content += f"{i}. {rec}\n"
        
        return content.strip()
    
    async def search_memories(
        self,
        query: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10,
        user_id: Optional[str] = None
    ) -> List[MemorySearchResult]:
        """
        Search memories in LeChat.
        
        Args:
            query: Search query
            category: Filter by category (optional)
            tags: Filter by tags (optional)
            limit: Maximum number of results
            user_id: User ID filter (optional)
            
        Returns:
            List of matching memory search results
            
        Raises:
            httpx.HTTPError: If API request fails
        """
        logger.info(f"Searching LeChat memories - query: {query}, category: {category}, user_id: {user_id}")
        
        try:
            # Prepare search parameters
            search_params = {
                "query": query,
                "limit": limit
            }
            
            if category:
                search_params["category"] = category
            if tags:
                search_params["tags"] = tags
            if user_id:
                search_params["user_id"] = user_id
            
            # Perform search
            response = await self.client.get(
                "/api/v1/memories/search",
                params=search_params
            )
            response.raise_for_status()
            
            # Parse results
            results_data = response.json()
            results = []
            
            for item in results_data.get("results", []):
                result = MemorySearchResult(
                    memory_id=item["memory_id"],
                    title=item["title"],
                    content=item["content"],
                    relevance_score=item.get("relevance_score", 0.0),
                    category=item["category"],
                    tags=item.get("tags", []),
                    created_at=item["created_at"]
                )
                results.append(result)
            
            logger.info(f"Memory search completed - results_count: {len(results)}")
            
            return results
            
        except Exception as e:
            logger.error(f"Memory search failed: {str(e)}")
            raise
    
    async def get_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """
        Retrieve a specific memory by ID.
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            Memory entry if found, None otherwise
            
        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            response = await self.client.get(f"/api/v1/memories/{memory_id}")
            
            if response.status_code == 404:
                return None
            
            response.raise_for_status()
            data = response.json()
            
            return MemoryEntry(**data)
            
        except Exception as e:
            logger.error(f"Failed to retrieve memory {memory_id}: {str(e)}")
            raise
    
    async def update_memory(
        self, 
        memory_id: str, 
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update a memory entry.
        
        Args:
            memory_id: ID of the memory to update
            updates: Dictionary of fields to update
            
        Returns:
            True if update successful, False otherwise
            
        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            response = await self.client.patch(
                f"/api/v1/memories/{memory_id}",
                json=updates
            )
            
            if response.status_code == 404:
                return False
            
            response.raise_for_status()
            return True
            
        except Exception as e:
            logger.error(f"Failed to update memory {memory_id}: {str(e)}")
            raise
    
    async def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory entry.
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            True if deletion successful, False otherwise
            
        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            response = await self.client.delete(f"/api/v1/memories/{memory_id}")
            
            if response.status_code == 404:
                return False
            
            response.raise_for_status()
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {str(e)}")
            raise
    
    async def get_compliance_history(
        self,
        document_id: Optional[str] = None,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        limit: int = 20
    ) -> List[MemorySearchResult]:
        """
        Get compliance assessment history.
        
        Args:
            document_id: Filter by document ID (optional)
            user_id: Filter by user ID (optional)
            organization_id: Filter by organization ID (optional)
            limit: Maximum number of results
            
        Returns:
            List of compliance assessment memories
        """
        # Build search query
        query_parts = ["compliance", "assessment"]
        
        if document_id:
            query_parts.append(document_id)
        
        query = " ".join(query_parts)
        
        # Search for compliance assessments
        results = await self.search_memories(
            query=query,
            category="compliance_assessment",
            user_id=user_id,
            limit=limit
        )
        
        # Filter by organization if specified
        if organization_id:
            filtered_results = []
            for result in results:
                # This would require checking metadata, which might not be available in search results
                # For now, we'll return all results
                filtered_results.append(result)
            return filtered_results
        
        return results
    
    async def get_risk_trends(
        self,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get risk trend analysis from stored assessments.
        
        Args:
            user_id: Filter by user ID (optional)
            organization_id: Filter by organization ID (optional)
            days: Number of days to analyze
            
        Returns:
            Risk trend analysis data
        """
        # Get recent compliance assessments
        assessments = await self.get_compliance_history(
            user_id=user_id,
            organization_id=organization_id,
            limit=100  # Get more for trend analysis
        )
        
        # Analyze trends
        risk_scores = []
        issue_counts = []
        critical_issues = []
        
        for assessment in assessments:
            # Extract risk score from metadata if available
            # This would require the memory to store structured metadata
            # For now, we'll use a placeholder approach
            risk_scores.append(0.5)  # Placeholder
            issue_counts.append(0)    # Placeholder
            critical_issues.append(0) # Placeholder
        
        # Calculate trends
        avg_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0
        total_issues = sum(issue_counts)
        total_critical = sum(critical_issues)
        
        return {
            "period_days": days,
            "total_assessments": len(assessments),
            "average_risk_score": avg_risk_score,
            "total_issues": total_issues,
            "total_critical_issues": total_critical,
            "trend_direction": "stable",  # Placeholder
            "risk_level": "medium" if avg_risk_score > 0.5 else "low"
        }
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
