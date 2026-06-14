"""Social Intelligence System — Learning social behavior from AGORA.

Treats AGORA as a social environment, not just a chat API.
Observes posts, replies, conversation flows, people, relationships,
and reactions to build social understanding.

Components:
- SocialObservationMemory: Observes social interactions
- RelationshipMemory: Tracks relationships between people
- ReputationMemory: Tracks reputation and trust scores
- SocialNormMemory: Learns implicit rules and norms
- ConversationEpisodeMemory: Records conversation episodes
- SocialSkillMemory: Stores successful social patterns

Safety: All external actions go through PolicyEngine.
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.social.intelligence")


# ═══════════════════════════════════════════════════════════════
# Data Models
# ═══════════════════════════════════════════════════════════════

@dataclass
class SocialObservation:
    """A single social observation from AGORA."""
    observation_id: str = ""
    timestamp_ms: int = 0
    observation_type: str = "general"  # post, reply, reaction, conversation, pattern
    post_id: int = 0
    author_name: str = ""
    author_id: int = 0
    content: str = ""
    context: str = ""  # What was happening around this observation
    participants: list[str] = field(default_factory=list)
    sentiment: float = 0.0  # -1.0 (negative) to 1.0 (positive)
    topics: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id, "timestamp_ms": self.timestamp_ms,
            "observation_type": self.observation_type, "post_id": self.post_id,
            "author_name": self.author_name, "author_id": self.author_id,
            "content": self.content[:300], "context": self.context[:200],
            "participants": self.participants, "sentiment": self.sentiment,
            "topics": self.topics, "tags": self.tags,
        }


@dataclass
class Relationship:
    """Relationship between two people."""
    person_a: str = ""
    person_b: str = ""
    relationship_type: str = "acquaintance"  # friend, colleague, acquaintance, rival, mentor
    closeness: float = 0.5  # 0.0 (distant) to 1.0 (close)
    interaction_count: int = 0
    last_interaction_ms: int = 0
    topics_together: list[str] = field(default_factory=list)
    sentiment_history: list[float] = field(default_factory=list)
    notes: str = ""

    @property
    def average_sentiment(self) -> float:
        return sum(self.sentiment_history) / len(self.sentiment_history) if self.sentiment_history else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "person_a": self.person_a, "person_b": self.person_b,
            "relationship_type": self.relationship_type, "closeness": self.closeness,
            "interaction_count": self.interaction_count,
            "last_interaction_ms": self.last_interaction_ms,
            "topics_together": self.topics_together[-10:],
            "average_sentiment": self.average_sentiment,
            "notes": self.notes[:200],
        }


@dataclass
class Reputation:
    """Reputation score for a person in the social network."""
    person_name: str = ""
    person_id: int = 0
    helpfulness: float = 0.5     # 0.0 to 1.0
    reliability: float = 0.5     # 0.0 to 1.0
    friendliness: float = 0.5    # 0.0 to 1.0
    expertise: float = 0.5       # 0.0 to 1.0
    activity_level: float = 0.5  # 0.0 (inactive) to 1.0 (very active)
    post_count: int = 0
    reply_count: int = 0
    mentioned_count: int = 0
    last_active_ms: int = 0

    @property
    def overall_score(self) -> float:
        return (self.helpfulness + self.reliability + self.friendliness + self.expertise) / 4

    def to_dict(self) -> dict[str, Any]:
        return {
            "person_name": self.person_name, "person_id": self.person_id,
            "helpfulness": self.helpfulness, "reliability": self.reliability,
            "friendliness": self.friendliness, "expertise": self.expertise,
            "activity_level": self.activity_level, "post_count": self.post_count,
            "reply_count": self.reply_count, "overall_score": self.overall_score,
        }


@dataclass
class SocialNorm:
    """A learned social norm or rule."""
    norm_id: str = ""
    description: str = ""
    norm_type: str = "general"  # greeting, distance, expression, taboo, timing
    context: str = ""  # When this norm applies
    confidence: float = 0.7
    examples: list[str] = field(default_factory=list)
    counter_examples: list[str] = field(default_factory=list)
    source_observations: list[str] = field(default_factory=list)
    active: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "norm_id": self.norm_id, "description": self.description,
            "norm_type": self.norm_type, "context": self.context,
            "confidence": self.confidence, "examples": self.examples[:3],
            "counter_examples": self.counter_examples[:3], "active": self.active,
        }


@dataclass
class ConversationEpisode:
    """A recorded conversation episode."""
    episode_id: str = ""
    timestamp_ms: int = 0
    participants: list[str] = field(default_factory=list)
    purpose: str = ""  # greeting, consultation, discussion, apology, small_talk, arbitration
    context: str = ""
    my_role: str = ""  # participant, observer, mediator
    key_points: list[str] = field(default_factory=list)
    emotion_detected: str = ""  # The emotional tone of the conversation
    outcome: str = ""  # positive, negative, neutral, unresolved
    lessons: list[str] = field(default_factory=list)
    related_posts: list[int] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "episode_id": self.episode_id, "timestamp_ms": self.timestamp_ms,
            "participants": self.participants, "purpose": self.purpose,
            "context": self.context[:200], "my_role": self.my_role,
            "key_points": self.key_points[:5], "emotion_detected": self.emotion_detected,
            "outcome": self.outcome, "lessons": self.lessons[:3],
            "related_posts": self.related_posts[-10:], "tags": self.tags,
        }


@dataclass
class SocialSkill:
    """A reusable social interaction pattern."""
    skill_id: str = ""
    name: str = ""
    skill_type: str = "general"  # greeting, consultation, discussion, apology, small_talk, arbitration, distance
    description: str = ""
    activation_conditions: str = ""
    template_approach: str = ""  # The general approach/template
    example_phrases: list[str] = field(default_factory=list)
    things_to_avoid: list[str] = field(default_factory=list)
    success_count: int = 0
    failure_count: int = 0
    last_used_ms: int = 0
    source_episodes: list[str] = field(default_factory=list)
    active: bool = True

    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill_id": self.skill_id, "name": self.name,
            "skill_type": self.skill_type, "description": self.description,
            "activation_conditions": self.activation_conditions,
            "template_approach": self.template_approach[:300],
            "example_phrases": self.example_phrases[:5],
            "things_to_avoid": self.things_to_avoid[:5],
            "success_count": self.success_count, "failure_count": self.failure_count,
            "success_rate": self.success_rate, "active": self.active,
        }


# ═══════════════════════════════════════════════════════════════
# Social Intelligence System
# ═══════════════════════════════════════════════════════════════

class SocialIntelligenceSystem:
    """Integrated social intelligence for AEGIS.

    Learns from AGORA interactions:
    - Observes social dynamics
    - Tracks relationships and reputation
    - Learns social norms
    - Records conversation episodes
    - Builds reusable social skills

    Usage:
        sis = SocialIntelligenceSystem(llm=llm, agora=agora_service)
        sis.observe_recent_posts()
        context = sis.get_reply_context(author_name="Kohaku", message="...")
        skill = sis.find_social_skill("apology")
    """

    def __init__(
        self,
        llm: Any = None,
        agora_service: Any = None,
        person_memory: Any = None,
        data_dir: str = "data/social",
    ) -> None:
        self._llm = llm
        self._agora = agora_service
        self._person_memory = person_memory
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)

        self._observations: list[SocialObservation] = []
        self._relationships: dict[str, Relationship] = {}  # "a|b" → Relationship
        self._reputations: dict[str, Reputation] = {}  # person_name → Reputation
        self._norms: dict[str, SocialNorm] = {}
        self._episodes: list[ConversationEpisode] = []
        self._skills: dict[str, SocialSkill] = {}

        self._load()

    def _load(self) -> None:
        """Load all social data from disk."""
        self._load_jsonl("observations.jsonl", self._observations, SocialObservation)
        self._load_relationships()
        self._load_reputations()
        self._load_norms()
        self._load_jsonl("conversation_episodes.jsonl", self._episodes, ConversationEpisode)
        self._load_skills()
        logger.info("Social intelligence loaded: %d obs, %d relationships, %d norms, %d episodes, %d skills",
                     len(self._observations), len(self._relationships), len(self._norms),
                     len(self._episodes), len(self._skills))

    def _load_jsonl(self, filename: str, target_list: list, cls: Any) -> None:
        path = self._data_dir / filename
        if not path.exists():
            return
        try:
            for line in path.read_text(encoding="utf-8").strip().split("\n"):
                if line.strip():
                    target_list.append(cls(**json.loads(line)))
        except Exception as e:
            logger.warning("Failed to load %s: %s", filename, e)

    def _load_relationships(self) -> None:
        path = self._data_dir / "relationships.jsonl"
        if not path.exists():
            return
        try:
            for line in path.read_text(encoding="utf-8").strip().split("\n"):
                if line.strip():
                    r = Relationship(**json.loads(line))
                    key = f"{r.person_a}|{r.person_b}"
                    self._relationships[key] = r
        except Exception:
            pass

    def _load_reputations(self) -> None:
        path = self._data_dir / "reputations.jsonl"
        if not path.exists():
            return
        try:
            for line in path.read_text(encoding="utf-8").strip().split("\n"):
                if line.strip():
                    rep = Reputation(**json.loads(line))
                    self._reputations[rep.person_name] = rep
        except Exception:
            pass

    def _load_norms(self) -> None:
        path = self._data_dir / "social_norms.jsonl"
        if not path.exists():
            return
        try:
            for line in path.read_text(encoding="utf-8").strip().split("\n"):
                if line.strip():
                    norm = SocialNorm(**json.loads(line))
                    self._norms[norm.norm_id] = norm
        except Exception:
            pass

    def _load_skills(self) -> None:
        path = self._data_dir / "social_skills.jsonl"
        if not path.exists():
            return
        try:
            for line in path.read_text(encoding="utf-8").strip().split("\n"):
                if line.strip():
                    skill = SocialSkill(**json.loads(line))
                    self._skills[skill.skill_id] = skill
        except Exception:
            pass

    def _append_jsonl(self, filename: str, data: dict[str, Any]) -> None:
        path = self._data_dir / filename
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

    # ── Observation ──────────────────────────────────────────────

    def observe_recent_posts(self, limit: int = 20) -> list[SocialObservation]:
        """Observe recent AGORA posts and extract social intelligence."""
        if not self._agora:
            return []

        observations: list[SocialObservation] = []
        try:
            posts = self._agora.read_posts(limit=limit)
            if not hasattr(posts, "posts"):
                return []

            for post in posts.posts:
                obs = SocialObservation(
                    observation_id=f"sobs_{os.urandom(4).hex()}",
                    timestamp_ms=int(time.time() * 1000),
                    observation_type="reply" if post.reply_to else "post",
                    post_id=post.id,
                    author_name=post.author.name,
                    author_id=post.author.id,
                    content=post.body[:300],
                    participants=[post.author.name] + [m.name for m in post.mentions],
                )

                # Analyze sentiment with LLM if available
                if self._llm and len(post.body) > 5:
                    obs.sentiment = self._analyze_sentiment(post.body)

                # Extract topics
                obs.topics = self._extract_topics(post.body)

                observations.append(obs)
                self._observations.append(obs)
                self._append_jsonl("observations.jsonl", obs.to_dict())

                # Update reputation
                self._update_reputation_from_post(post)

                # Update relationships
                if post.mentions:
                    for mention in post.mentions:
                        self._update_relationship(post.author.name, mention.name, obs.sentiment)

            # Trim old observations
            if len(self._observations) > 500:
                self._observations = self._observations[-500:]

        except Exception as e:
            logger.warning("Failed to observe AGORA posts: %s", e)

        return observations

    def observe_mentions(self, limit: int = 10) -> list[SocialObservation]:
        """Observe posts that mention AEGIS."""
        if not self._agora:
            return []

        observations: list[SocialObservation] = []
        try:
            mentions = self._agora.read_mentions(limit=limit)
            if not hasattr(mentions, "posts"):
                return []

            for post in mentions.posts:
                obs = SocialObservation(
                    observation_id=f"sobs_{os.urandom(4).hex()}",
                    timestamp_ms=int(time.time() * 1000),
                    observation_type="mention",
                    post_id=post.id,
                    author_name=post.author.name,
                    author_id=post.author.id,
                    content=post.body[:300],
                    participants=[post.author.name],
                )
                if self._llm and len(post.body) > 5:
                    obs.sentiment = self._analyze_sentiment(post.body)
                obs.topics = self._extract_topics(post.body)

                observations.append(obs)
                self._observations.append(obs)
                self._append_jsonl("observations.jsonl", obs.to_dict())

        except Exception as e:
            logger.warning("Failed to observe AGORA mentions: %s", e)

        return observations

    def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of text using LLM."""
        if not self._llm:
            return 0.0
        try:
            result = self._llm.generate(
                prompt=f"Rate the sentiment of this text from -1.0 (very negative) to 1.0 (very positive). Respond with ONLY a number.\n\nText: {text[:200]}",
                system_prompt="Output only a number between -1.0 and 1.0.",
                max_tokens=10,
            )
            if result.success:
                return max(-1.0, min(1.0, float(result.content.strip())))
        except Exception:
            pass
        return 0.0

    def _extract_topics(self, text: str) -> list[str]:
        """Extract topics from text."""
        topics = []
        keywords = ["質問", "質問です", "教えて", "どう", "なぜ", "いつ", "どこ",
                     "help", "question", "how", "why", "when", "where",
                     "バグ", "エラー", "改善", "提案", "議論", "雑談"]
        text_lower = text.lower()
        for kw in keywords:
            if kw in text_lower:
                topics.append(kw)
        return topics[:5]

    # ── Relationship ─────────────────────────────────────────────

    def _update_relationship(self, person_a: str, person_b: str, sentiment: float) -> None:
        """Update relationship between two people."""
        key = f"{person_a}|{person_b}"
        alt_key = f"{person_b}|{person_a}"
        rel = self._relationships.get(key) or self._relationships.get(alt_key)

        if rel:
            rel.interaction_count += 1
            rel.last_interaction_ms = int(time.time() * 1000)
            rel.sentiment_history.append(sentiment)
            rel.sentiment_history = rel.sentiment_history[-20:]
            # Adjust closeness based on interaction frequency
            rel.closeness = min(1.0, rel.closeness + 0.01)
        else:
            rel = Relationship(
                person_a=person_a, person_b=person_b,
                interaction_count=1, closeness=0.3,
                last_interaction_ms=int(time.time() * 1000),
                sentiment_history=[sentiment],
            )
            self._relationships[key] = rel

        self._append_jsonl("relationships.jsonl", rel.to_dict())

    def get_relationship(self, person_a: str, person_b: str) -> Relationship | None:
        """Get relationship between two people."""
        key = f"{person_a}|{person_b}"
        alt_key = f"{person_b}|{person_a}"
        return self._relationships.get(key) or self._relationships.get(alt_key)

    # ── Reputation ───────────────────────────────────────────────

    def _update_reputation_from_post(self, post: Any) -> None:
        """Update reputation based on a post."""
        name = post.author.name
        rep = self._reputations.get(name)
        if not rep:
            rep = Reputation(person_name=name, person_id=post.author.id)
            self._reputations[name] = rep

        if post.reply_to:
            rep.reply_count += 1
        else:
            rep.post_count += 1
        rep.last_active_ms = int(time.time() * 1000)

        # Update activity level
        total = rep.post_count + rep.reply_count
        rep.activity_level = min(1.0, total / 50)

        self._append_jsonl("reputations.jsonl", rep.to_dict())

    def get_reputation(self, person_name: str) -> Reputation | None:
        return self._reputations.get(person_name)

    # ── Social Norms ─────────────────────────────────────────────

    def learn_norm(self, description: str, norm_type: str = "general", context: str = "", examples: list[str] | None = None) -> SocialNorm:
        """Learn a new social norm."""
        norm = SocialNorm(
            norm_id=f"norm_{os.urandom(4).hex()}",
            description=description, norm_type=norm_type,
            context=context, examples=examples or [],
        )
        self._norms[norm.norm_id] = norm
        self._append_jsonl("social_norms.jsonl", norm.to_dict())
        return norm

    def get_norms(self, norm_type: str | None = None) -> list[SocialNorm]:
        """Get social norms, optionally filtered by type."""
        norms = [n for n in self._norms.values() if n.active]
        if norm_type:
            norms = [n for n in norms if n.norm_type == norm_type]
        return sorted(norms, key=lambda n: n.confidence, reverse=True)

    # ── Conversation Episodes ────────────────────────────────────

    def record_conversation(
        self, participants: list[str], purpose: str, context: str = "",
        key_points: list[str] | None = None, emotion_detected: str = "",
        outcome: str = "neutral", lessons: list[str] | None = None,
        related_posts: list[int] | None = None, tags: list[str] | None = None,
    ) -> ConversationEpisode:
        """Record a conversation episode."""
        ep = ConversationEpisode(
            episode_id=f"conv_{os.urandom(4).hex()}",
            timestamp_ms=int(time.time() * 1000),
            participants=participants, purpose=purpose, context=context,
            key_points=key_points or [], emotion_detected=emotion_detected,
            outcome=outcome, lessons=lessons or [],
            related_posts=related_posts or [], tags=tags or [],
        )
        self._episodes.append(ep)
        self._append_jsonl("conversation_episodes.jsonl", ep.to_dict())
        return ep

    # ── Social Skills ────────────────────────────────────────────

    def add_social_skill(
        self, name: str, skill_type: str, description: str = "",
        activation_conditions: str = "", template_approach: str = "",
        example_phrases: list[str] | None = None, things_to_avoid: list[str] | None = None,
    ) -> SocialSkill:
        """Add a social skill."""
        skill = SocialSkill(
            skill_id=f"sskill_{os.urandom(4).hex()}", name=name,
            skill_type=skill_type, description=description,
            activation_conditions=activation_conditions,
            template_approach=template_approach,
            example_phrases=example_phrases or [],
            things_to_avoid=things_to_avoid or [],
        )
        self._skills[skill.skill_id] = skill
        self._append_jsonl("social_skills.jsonl", skill.to_dict())
        return skill

    def find_social_skill(self, skill_type: str, context: str = "") -> SocialSkill | None:
        """Find a social skill by type and context."""
        candidates = [s for s in self._skills.values() if s.active and s.skill_type == skill_type]
        if not candidates:
            return None
        if context:
            # Try to match context
            for s in candidates:
                if context.lower() in s.activation_conditions.lower():
                    return s
        return max(candidates, key=lambda s: s.success_rate)

    def record_skill_result(self, skill_id: str, success: bool) -> None:
        """Record social skill usage result."""
        skill = self._skills.get(skill_id)
        if skill:
            if success:
                skill.success_count += 1
            else:
                skill.failure_count += 1
            skill.last_used_ms = int(time.time() * 1000)

    # ── Reply Context ────────────────────────────────────────────

    def get_reply_context(self, author_name: str, message: str, post_id: int = 0) -> dict[str, Any]:
        """Get comprehensive context for generating a reply.

        Returns all relevant social intelligence for replying to someone.
        """
        context: dict[str, Any] = {
            "author": author_name,
            "message": message[:200],
        }

        # Person info from PersonMemory
        if self._person_memory:
            person = self._person_memory.resolve(author_name)
            if person:
                context["person"] = {
                    "role": person.role, "authority_level": person.authority_level,
                    "trust_level": person.trust_level, "relationship": person.relationship,
                    "interaction_count": person.interaction_count,
                }

        # Reputation
        rep = self._reputations.get(author_name)
        if rep:
            context["reputation"] = rep.to_dict()

        # Relationship with AEGIS
        rel = self.get_relationship(author_name, "AEGIS")
        if rel:
            context["relationship"] = rel.to_dict()

        # Recent conversations with this person
        recent_eps = [ep for ep in self._episodes if author_name in ep.participants][-3:]
        if recent_eps:
            context["recent_conversations"] = [ep.to_dict() for ep in recent_eps]

        # Applicable social norms
        context["norms"] = [n.to_dict() for n in self.get_norms()[:3]]

        # Applicable social skill
        purpose = self._detect_conversation_purpose(message)
        skill = self.find_social_skill(purpose, message)
        if skill:
            context["suggested_skill"] = skill.to_dict()

        return context

    def _detect_conversation_purpose(self, message: str) -> str:
        """Detect the purpose of a message."""
        msg_lower = message.lower()
        if any(w in msg_lower for w in ["こんにちは", "hello", "hi", "おはよう", "hey"]):
            return "greeting"
        if any(w in msg_lower for w in ["教えて", "どう", "質問", "help", "question"]):
            return "consultation"
        if any(w in msg_lower for w in ["ありがとう", "thank", "助かる"]):
            return "gratitude"
        if any(w in msg_lower for w in ["すみません", "sorry", "ごめん"]):
            return "apology"
        if any(w in msg_lower for w in ["議論", "思う", "意見", "opinion", "think"]):
            return "discussion"
        return "general"

    # ── Internal Simulation ──────────────────────────────────────

    def simulate_reply_reception(self, reply_text: str, target_author: str, context: str = "") -> dict[str, Any]:
        """Simulate how a reply would be received.

        Internal-only — does NOT send anything.
        """
        if not self._llm:
            return {"assessment": "Cannot simulate without LLM", "risk": "unknown"}

        # Get social context
        rep = self._reputations.get(target_author)
        rel = self.get_relationship(target_author, "AEGIS")
        norms = self.get_norms()[:3]

        norm_text = "\n".join(f"- {n.description}" for n in norms) if norms else "No norms learned"
        rel_text = f"closeness={rel.closeness:.1f}, sentiment={rel.average_sentiment:.1f}" if rel else "No prior relationship"

        prompt = f"""You are simulating how a reply would be received in a social chat environment.

Reply: {reply_text[:200]}
Target: {target_author}
Relationship: {rel_text}
Social norms:
{norm_text}
Context: {context[:100]}

Assess this reply. Respond with JSON:
{{"assessment": "How would this likely be received?", "risk_level": "low|medium|high", "potential_issues": ["issue1"], "improvement_suggestions": ["suggestion1"]}}"""

        try:
            result = self._llm.generate(
                prompt=prompt,
                system_prompt="Assess social replies. Output only JSON.",
                max_tokens=200,
            )
            if result.success:
                import re
                clean = result.content.strip()
                if clean.startswith("```"):
                    lines = clean.split("\n")
                    clean = "\n".join(lines[1:])
                    if clean.endswith("```"):
                        clean = clean[:-3]
                    clean = clean.strip()
                match = re.search(r'\{.*\}', clean, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
        except Exception as e:
            logger.warning("Reply simulation failed: %s", e)

        return {"assessment": "Simulation failed", "risk": "unknown"}

    # ── Context String ───────────────────────────────────────────

    def get_social_context_string(self, max_chars: int = 600) -> str:
        """Get social intelligence context for LLM prompts."""
        parts = []

        # Recent social observations
        recent_obs = self._observations[-5:]
        if recent_obs:
            lines = ["Recent AGORA activity:"]
            for obs in recent_obs:
                lines.append(f"  - {obs.author_name}: {obs.content[:60]}")
            parts.append("\n".join(lines))

        # Known people
        if self._reputations:
            lines = ["Known people:"]
            for name, rep in sorted(self._reputations.items(), key=lambda x: x[1].overall_score, reverse=True)[:5]:
                lines.append(f"  - {name}: helpful={rep.helpfulness:.1f} reliable={rep.reliability:.1f} friendly={rep.friendliness:.1f}")
            parts.append("\n".join(lines))

        # Social norms
        norms = self.get_norms()[:3]
        if norms:
            lines = ["Social norms:"]
            for n in norms:
                lines.append(f"  - {n.description}")
            parts.append("\n".join(lines))

        return "\n\n".join(parts)[:max_chars]

    # ── Stats ────────────────────────────────────────────────────

    def get_stats(self) -> dict[str, Any]:
        return {
            "observations": len(self._observations),
            "relationships": len(self._relationships),
            "reputations": len(self._reputations),
            "norms": len(self._norms),
            "episodes": len(self._episodes),
            "skills": len(self._skills),
        }
