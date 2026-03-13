"""
Profile Recommender - Smart profile recommendation logic
Analyzes system hardware and user experience to recommend optimal profile
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RecommendationResult:
    """Profile recommendation result"""
    recommended_profile: str
    confidence: float  # 0.0 to 1.0
    reason: str
    alternative_profiles: list[str]  # Other profiles the user might consider
    warnings: list[str]  # Any warnings about the recommendation


class ProfileRecommender:
    """
    Smart profile recommendation engine.

    Uses system information and user experience level to recommend
    the most appropriate optimization profile.

    Philosophy: Safety-first. Default to SAFE unless there's a clear
    reason to recommend a higher-risk profile.
    """

    # Profile definitions with requirements
    PROFILES = {
        "SAFE": {
            "min_system_tier": 1,
            "min_ram_gb": 4,
            "requires_desktop": False,
            "requires_gaming_gpu": False,
            "risk_level": "LOW",
            "expected_gain": "2-5%",
            "description": "For everyday use and stability. Recommended for beginners."
        },
        "COMPETITIVE": {
            "min_system_tier": 3,
            "min_ram_gb": 8,
            "requires_desktop": False,  # Gaming laptops welcome
            "requires_gaming_gpu": True,
            "risk_level": "MEDIUM",
            "expected_gain": "5-10%",
            "description": "Balanced for performance and responsiveness. Recommended for most gamers."
        },
        "EXTREME": {
            "min_system_tier": 4,
            "min_ram_gb": 16,
            "requires_desktop": True,  # Desktops only (better cooling)
            "requires_gaming_gpu": True,
            "risk_level": "HIGH",
            "expected_gain": "10-15%",
            "description": "Maximum power for top-tier gaming. Advanced users only."
        }
    }

    # User experience levels
    EXPERIENCE_LEVELS = {
        "beginner": {
            "max_safe_risk": "LOW",
            "description": "New to Windows optimization. Prioritizes safety and stability."
        },
        "intermediate": {
            "max_safe_risk": "MEDIUM",
            "description": "Some Windows knowledge. Comfortable with minor trade-offs."
        },
        "advanced": {
            "max_safe_risk": "HIGH",
            "description": "Expert Windows user. Can troubleshoot issues."
        }
    }

    def __init__(self):
        """Initialize profile recommender"""
        self.recommendation_history: list[Dict[str, Any]] = []

    def recommend(
        self,
        system_info: Dict[str, Any],
        user_experience: str = "beginner",
        user_goal: Optional[str] = None
    ) -> RecommendationResult:
        """
        Recommend a profile based on system and user.

        Args:
            system_info: System information dictionary (from SystemDetector)
                - cpu_tier: 1-5 (1=low-end, 5=high-end)
                - gpu_tier: 1-5
                - ram_gb: Total RAM in GB
                - is_laptop: True if laptop
                - is_gaming_gpu: True if has dedicated gaming GPU
                - os_version: "10" or "11"
            user_experience: "beginner", "intermediate", or "advanced"
            user_goal: Optional user goal ("gaming", "productivity", etc.)

        Returns:
            RecommendationResult with recommended profile and reasoning
        """
        # Validate inputs
        if user_experience not in self.EXPERIENCE_LEVELS:
            logger.warning(f"Invalid experience level: {user_experience}. Defaulting to beginner.")
            user_experience = "beginner"

        # Calculate system tier (overall system capability)
        system_tier = self._calculate_system_tier(system_info)

        # Get user's max safe risk level
        max_safe_risk = self.EXPERIENCE_LEVELS[user_experience]["max_safe_risk"]

        # Determine recommended profile
        recommended_profile = self._determine_profile(
            system_tier,
            max_safe_risk,
            system_info,
            user_goal
        )

        # Calculate confidence and generate reasoning
        confidence, reason, warnings = self._generate_recommendation_reasoning(
            recommended_profile,
            system_tier,
            max_safe_risk,
            system_info,
            user_experience,
            user_goal
        )

        # Determine alternative profiles
        alternative_profiles = self._get_alternatives(
            recommended_profile,
            system_tier,
            max_safe_risk
        )

        result = RecommendationResult(
            recommended_profile=recommended_profile,
            confidence=confidence,
            reason=reason,
            alternative_profiles=alternative_profiles,
            warnings=warnings
        )

        # Log recommendation
        logger.info(
            f"Profile recommendation: {recommended_profile} "
            f"(confidence: {confidence:.2f}, experience: {user_experience}, "
            f"system_tier: {system_tier})"
        )

        # Save to history
        self.recommendation_history.append({
            "profile": recommended_profile,
            "confidence": confidence,
            "system_tier": system_tier,
            "user_experience": user_experience,
            "user_goal": user_goal
        })

        return result

    def _calculate_system_tier(self, system_info: Dict[str, Any]) -> int:
        """
        Calculate overall system tier (1-5).

        Uses weakest link approach: system is only as good as its
        weakest component.
        """
        cpu_tier = system_info.get("cpu_tier", 2)
        gpu_tier = system_info.get("gpu_tier", 2)
        ram_gb = system_info.get("ram_gb", 8)

        # RAM tier calculation
        if ram_gb < 8:
            ram_tier = 1
        elif ram_gb < 16:
            ram_tier = 2
        elif ram_gb < 32:
            ram_tier = 3
        else:
            ram_tier = 4

        # System tier = minimum of CPU, GPU, RAM tiers
        # This ensures we don't recommend profiles that bottleneck on weak components
        system_tier = min(cpu_tier, gpu_tier, ram_tier)

        # Reduce tier for laptops (thermal constraints)
        if system_info.get("is_laptop", False):
            system_tier = max(1, system_tier - 1)

        logger.debug(
            f"System tier calculation: CPU={cpu_tier}, GPU={gpu_tier}, "
            f"RAM={ram_tier}, Laptop={system_info.get('is_laptop', False)} "
            f"→ System={system_tier}"
        )

        return system_tier

    def _determine_profile(
        self,
        system_tier: int,
        max_safe_risk: str,
        system_info: Dict[str, Any],
        user_goal: Optional[str]
    ) -> str:
        """
        Determine which profile to recommend.

        Philosophy: Conservative recommendations. Only recommend higher-risk
        profiles when there's clear evidence the user can benefit from them.
        """
        # Default to SAFE (safety-first)
        recommended = "SAFE"

        # Risk level mapping
        risk_hierarchy = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
        max_risk_value = risk_hierarchy[max_safe_risk]

        # Can we recommend COMPETITIVE?
        # Requirements:
        # - System tier 3+ (decent hardware)
        # - Gaming GPU present
        # - User accepts MEDIUM risk
        if (
            self.PROFILES["COMPETITIVE"]["min_system_tier"] <= system_tier
            and system_info.get("is_gaming_gpu", False)
            and max_risk_value >= risk_hierarchy["MEDIUM"]
        ):
            recommended = "COMPETITIVE"

        # Can we recommend EXTREME?
        # Requirements:
        # - System tier 4+ (high-end hardware)
        # - Desktop only (better cooling, no thermal throttling)
        # - Gaming GPU present
        # - User accepts HIGH risk
        # - User explicitly wants maximum performance OR is advanced
        if (
            self.PROFILES["EXTREME"]["min_system_tier"] <= system_tier
            and not system_info.get("is_laptop", True)  # Must be desktop
            and system_info.get("is_gaming_gpu", False)
            and max_risk_value >= risk_hierarchy["HIGH"]
            and (user_goal == "maximum_performance" or max_safe_risk == "HIGH")
        ):
            recommended = "EXTREME"

        logger.debug(
            f"Profile determination: system_tier={system_tier}, "
            f"max_safe_risk={max_safe_risk}, recommended={recommended}"
        )

        return recommended

    def _generate_recommendation_reasoning(
        self,
        profile: str,
        system_tier: int,
        max_safe_risk: str,
        system_info: Dict[str, Any],
        user_experience: str,
        user_goal: Optional[str]
    ) -> tuple[float, str, list[str]]:
        """
        Generate confidence score, reasoning, and warnings for recommendation.
        """
        confidence = 0.5  # Start at neutral
        reasons = []
        warnings = []

        # Base confidence on user experience matching profile risk
        risk_match = {
            "beginner": "SAFE",
            "intermediate": "COMPETITIVE",
            "advanced": "EXTREME"
        }

        if risk_match[user_experience] == profile:
            confidence += 0.3
            reasons.append(f"Matches your {user_experience} experience level")
        elif user_experience == "beginner" and profile == "SAFE":
            confidence += 0.2
            reasons.append("Safe choice for beginners")

        # System capability factors
        if profile == "SAFE":
            confidence += 0.2
            reasons.append("Recommended for stability and daily use")

        elif profile == "COMPETITIVE":
            if system_tier >= 3:
                confidence += 0.2
                reasons.append("Your system hardware is suitable for gaming optimizations")

            if system_info.get("is_gaming_gpu"):
                confidence += 0.1
                reasons.append("Dedicated GPU detected")

            if system_info.get("is_laptop"):
                warnings.append(
                    "Laptop detected: Monitor temperatures during extended gaming sessions. "
                    "COMPETITIVE profile may increase heat output."
                )

        elif profile == "EXTREME":
            if system_tier >= 4:
                confidence += 0.1
                reasons.append("High-end system detected")

            if not system_info.get("is_laptop", True):
                confidence += 0.1
                reasons.append("Desktop form factor allows aggressive optimizations")

            warnings.extend([
                "⚠️ EXTREME profile is for advanced users only",
                "May cause system instability on some configurations",
                "Requires Windows troubleshooting knowledge",
                "Always create a full backup before applying"
            ])

        # User goal considerations
        if user_goal == "gaming":
            if profile in ["COMPETITIVE", "EXTREME"]:
                confidence += 0.1
                reasons.append("Optimized for gaming performance")

        elif user_goal == "stability":
            if profile == "SAFE":
                confidence += 0.1
                reasons.append("Prioritizes system stability")

        # Cap confidence at 1.0
        confidence = min(1.0, confidence)

        # Build reason string
        reason = f"Recommended: {self.PROFILES[profile]['description']}\n"
        if reasons:
            reason += "\n".join(f"• {r}" for r in reasons)

        return confidence, reason, warnings

    def _get_alternatives(
        self,
        recommended: str,
        system_tier: int,
        max_safe_risk: str
    ) -> list[str]:
        """
        Get alternative profiles the user might consider.
        """
        alternatives = []

        # Always include SAFE as alternative (unless it's the recommendation)
        if recommended != "SAFE":
            alternatives.append("SAFE")

        # Include COMPETITIVE if system supports it
        if (
            recommended != "COMPETITIVE"
            and system_tier >= 3
            and max_safe_risk in ["MEDIUM", "HIGH"]
        ):
            alternatives.append("COMPETITIVE")

        # Include EXTREME only for high-end systems with advanced users
        if (
            recommended != "EXTREME"
            and system_tier >= 4
            and max_safe_risk == "HIGH"
        ):
            alternatives.append("EXTREME")

        return alternatives

    def get_profile_requirements(self, profile_name: str) -> Dict[str, Any]:
        """
        Get requirements and information for a specific profile.

        Args:
            profile_name: "SAFE", "COMPETITIVE", or "EXTREME"

        Returns:
            Dictionary with profile requirements and info
        """
        if profile_name not in self.PROFILES:
            raise ValueError(f"Unknown profile: {profile_name}")

        return self.PROFILES[profile_name].copy()

    def can_use_profile(
        self,
        profile_name: str,
        system_info: Dict[str, Any],
        user_experience: str
    ) -> tuple[bool, list[str]]:
        """
        Check if a user can use a specific profile.

        Args:
            profile_name: Profile to check
            system_info: System information
            user_experience: User's experience level

        Returns:
            (can_use, reasons) tuple
        """
        if profile_name not in self.PROFILES:
            return False, ["Unknown profile"]

        profile = self.PROFILES[profile_name]
        reasons = []

        # Check system tier
        system_tier = self._calculate_system_tier(system_info)
        if system_tier < profile["min_system_tier"]:
            reasons.append(
                f"System tier {system_tier} below minimum {profile['min_system_tier']}"
            )

        # Check RAM
        ram_gb = system_info.get("ram_gb", 0)
        if ram_gb < profile["min_ram_gb"]:
            reasons.append(
                f"RAM ({ram_gb}GB) below minimum ({profile['min_ram_gb']}GB)"
            )

        # Check if desktop required
        if profile["requires_desktop"] and system_info.get("is_laptop", True):
            reasons.append("Profile requires desktop (not laptop)")

        # Check if gaming GPU required
        if profile["requires_gaming_gpu"] and not system_info.get("is_gaming_gpu", False):
            reasons.append("Profile requires dedicated gaming GPU")

        # Check user experience vs risk level
        max_safe_risk = self.EXPERIENCE_LEVELS[user_experience]["max_safe_risk"]
        risk_hierarchy = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}

        if risk_hierarchy[max_safe_risk] < risk_hierarchy[profile["risk_level"]]:
            reasons.append(
                f"Profile risk ({profile['risk_level']}) exceeds your "
                f"experience level ({user_experience})"
            )

        can_use = len(reasons) == 0
        return can_use, reasons


# Singleton instance
_recommender_instance: Optional[ProfileRecommender] = None


def get_recommender() -> ProfileRecommender:
    """Get singleton recommender instance"""
    global _recommender_instance
    if _recommender_instance is None:
        _recommender_instance = ProfileRecommender()
    return _recommender_instance
