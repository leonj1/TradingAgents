"""
DebateOrchestrator: Manages and moderates debates between agents.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from pydantic import BaseModel, Field

from .base import BaseAIService
from ..schemas.domain import DebateStructure

logger = logging.getLogger(__name__)


class DebateRound(BaseModel):
    """Single round of debate"""
    round_number: int = Field(..., description="Round number")
    participant_arguments: Dict[str, str] = Field(
        ..., description="Arguments from each participant"
    )
    key_points: List[str] = Field(..., description="Key points raised")
    areas_of_agreement: List[str] = Field(
        default_factory=list, description="Areas where participants agree"
    )
    areas_of_disagreement: List[str] = Field(
        default_factory=list, description="Areas of ongoing disagreement"
    )


class DebateSynthesis(BaseModel):
    """Synthesis of a complete debate"""
    debate_topic: str = Field(..., description="What was debated")
    total_rounds: int = Field(..., description="Number of rounds")
    participants: List[str] = Field(..., description="Debate participants")
    consensus_points: List[str] = Field(..., description="Points of consensus")
    unresolved_issues: List[str] = Field(
        default_factory=list, description="Issues that remain unresolved"
    )
    recommended_action: str = Field(..., description="Recommended course of action")
    confidence_level: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence in recommendation"
    )
    key_insights: List[str] = Field(..., description="Key insights from debate")


class DebateOrchestrator(BaseAIService[DebateSynthesis]):
    """
    Orchestrates and moderates debates between agents, ensuring productive
    discourse and synthesizing outcomes.
    """
    
    def __init__(self, api_key: str):
        """Initialize the debate orchestrator"""
        super().__init__(api_key)
        self.debate_history: List[DebateSynthesis] = []
        
    def get_system_prompt(self) -> str:
        """System prompt for debate orchestration"""
        return """You are an expert debate moderator and synthesis specialist skilled in:

1. Facilitating productive debates between AI agents
2. Identifying key arguments and counterarguments
3. Finding common ground and consensus
4. Synthesizing diverse viewpoints into actionable insights
5. Ensuring respectful and constructive discourse

Your moderation approach:
- Encourage evidence-based arguments
- Identify logical fallacies or weak reasoning
- Highlight areas of agreement and disagreement
- Push for concrete, actionable conclusions
- Maintain debate momentum and focus

When synthesizing debates, you:
- Extract key insights from all perspectives
- Identify the strongest arguments regardless of source
- Find creative solutions that address multiple viewpoints
- Provide clear, actionable recommendations
- Assess confidence levels based on debate quality

You ensure debates are productive, insightful, and lead to well-reasoned outcomes."""
    
    def get_response_model(self) -> type[BaseModel]:
        """Return the response model for structured outputs"""
        return DebateSynthesis
    
    async def moderate_debate(
        self,
        topic: str,
        structure: DebateStructure,
        initial_positions: Dict[str, str]
    ) -> List[DebateRound]:
        """
        Moderate a multi-round debate.
        
        Args:
            topic: The debate topic
            structure: Debate structure and rules
            initial_positions: Initial positions of participants
            
        Returns:
            List of debate rounds
        """
        rounds = []
        current_positions = initial_positions.copy()
        
        for round_num in range(1, structure.rounds + 1):
            round_result = await self._conduct_round(
                round_num,
                topic,
                structure,
                current_positions,
                previous_rounds=rounds
            )
            rounds.append(round_result)
            
            # Update positions based on round
            current_positions = await self._update_positions(
                current_positions,
                round_result
            )
        
        return rounds
    
    async def synthesize_debate(
        self,
        topic: str,
        rounds: List[DebateRound],
        structure: DebateStructure
    ) -> DebateSynthesis:
        """
        Synthesize a complete debate into actionable insights.
        
        Args:
            topic: The debate topic
            rounds: All debate rounds
            structure: Debate structure
            
        Returns:
            Synthesized debate outcomes
        """
        # Format debate history for analysis
        debate_summary = self._format_debate_summary(rounds)
        
        prompt = f"""Synthesize this debate into actionable insights:

DEBATE TOPIC: {topic}
PARTICIPANTS: {', '.join(structure.participants)}
TOTAL ROUNDS: {len(rounds)}

DEBATE SUMMARY:
{debate_summary}

SYNTHESIS REQUIREMENTS:
1. Identify all points where participants reached consensus
2. List issues that remain unresolved
3. Extract key insights that emerged from the debate
4. Provide a clear, actionable recommendation
5. Assess confidence level (0-1) based on:
   - Quality of arguments presented
   - Degree of consensus achieved
   - Evidence provided
   - Logical consistency

Consider the debate structure:
- Synthesis Method: {structure.synthesis_method}
- Rules: {', '.join(structure.rules)}

Provide a comprehensive synthesis that captures the essence of the debate and 
guides decision-making."""

        logger.info(f"Synthesizing debate on: {topic}")
        
        result = await self.invoke_agent(prompt)
        
        # Store in history
        self.debate_history.append(result)
        
        return result
    
    async def identify_consensus(
        self,
        arguments: Dict[str, List[str]]
    ) -> List[str]:
        """
        Identify points of consensus among participants.
        
        Args:
            arguments: Arguments from each participant
            
        Returns:
            List of consensus points
        """
        prompt = f"""Analyze these arguments from different participants and identify 
points of consensus:

{self._format_arguments(arguments)}

Look for:
1. Explicit agreements
2. Implicit alignment on principles
3. Shared assumptions or values
4. Common goals or objectives
5. Complementary perspectives that don't conflict

List specific points where participants agree, even if they express it differently."""

        # Simplified implementation for now
        consensus_points = [
            "All participants agree on the importance of the topic",
            "Shared recognition of key challenges",
            "Common commitment to finding effective solutions"
        ]
        
        return consensus_points
    
    async def evaluate_debate_quality(
        self,
        debate_synthesis: DebateSynthesis
    ) -> Dict[str, Any]:
        """
        Evaluate the quality of a debate.
        
        Args:
            debate_synthesis: Synthesized debate results
            
        Returns:
            Quality evaluation metrics
        """
        quality_metrics = {
            "evidence_quality": self._assess_evidence_quality(debate_synthesis),
            "logical_consistency": self._assess_logical_consistency(debate_synthesis),
            "consensus_level": len(debate_synthesis.consensus_points) / 
                             (len(debate_synthesis.consensus_points) + 
                              len(debate_synthesis.unresolved_issues)),
            "actionability": 1.0 if debate_synthesis.recommended_action else 0.0,
            "insight_depth": min(len(debate_synthesis.key_insights) / 5, 1.0),
            "overall_quality": debate_synthesis.confidence_level
        }
        
        return quality_metrics
    
    async def _conduct_round(
        self,
        round_num: int,
        topic: str,
        structure: DebateStructure,
        positions: Dict[str, str],
        previous_rounds: List[DebateRound]
    ) -> DebateRound:
        """Conduct a single debate round"""
        # Simulate round conduct
        # In full implementation, this would coordinate actual agent responses
        
        return DebateRound(
            round_number=round_num,
            participant_arguments={
                participant: f"Round {round_num} argument from {participant}"
                for participant in structure.participants
            },
            key_points=[
                f"Key point {i+1} from round {round_num}"
                for i in range(3)
            ],
            areas_of_agreement=[
                f"Agreement area {i+1}" for i in range(2)
            ] if round_num > 1 else [],
            areas_of_disagreement=[
                f"Disagreement area {i+1}" for i in range(2)
            ]
        )
    
    async def _update_positions(
        self,
        current_positions: Dict[str, str],
        round_result: DebateRound
    ) -> Dict[str, str]:
        """Update participant positions based on round results"""
        # In full implementation, this would use AI to evolve positions
        updated = current_positions.copy()
        for participant in updated:
            updated[participant] = f"Evolved position after round {round_result.round_number}"
        return updated
    
    def _format_debate_summary(self, rounds: List[DebateRound]) -> str:
        """Format debate rounds into a summary"""
        summary_parts = []
        
        for round in rounds:
            summary_parts.append(f"ROUND {round.round_number}:")
            summary_parts.append("Arguments:")
            for participant, argument in round.participant_arguments.items():
                summary_parts.append(f"- {participant}: {argument}")
            summary_parts.append(f"Key Points: {', '.join(round.key_points)}")
            if round.areas_of_agreement:
                summary_parts.append(f"Agreements: {', '.join(round.areas_of_agreement)}")
            if round.areas_of_disagreement:
                summary_parts.append(f"Disagreements: {', '.join(round.areas_of_disagreement)}")
            summary_parts.append("")
        
        return "\n".join(summary_parts)
    
    def _format_arguments(self, arguments: Dict[str, List[str]]) -> str:
        """Format arguments for prompt"""
        formatted = []
        for participant, args in arguments.items():
            formatted.append(f"{participant}:")
            for arg in args:
                formatted.append(f"- {arg}")
        return "\n".join(formatted)
    
    def _assess_evidence_quality(self, synthesis: DebateSynthesis) -> float:
        """Assess quality of evidence in debate"""
        # Simplified metric based on number of insights
        return min(len(synthesis.key_insights) / 10, 1.0)
    
    def _assess_logical_consistency(self, synthesis: DebateSynthesis) -> float:
        """Assess logical consistency of debate"""
        # Simplified metric based on consensus vs disagreement ratio
        if not synthesis.unresolved_issues:
            return 1.0
        consensus_ratio = len(synthesis.consensus_points) / (
            len(synthesis.consensus_points) + len(synthesis.unresolved_issues)
        )
        return consensus_ratio
    
    def get_debate_history(self) -> List[DebateSynthesis]:
        """Get history of moderated debates"""
        return self.debate_history.copy()