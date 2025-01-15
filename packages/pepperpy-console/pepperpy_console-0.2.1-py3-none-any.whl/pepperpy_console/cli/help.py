"""Help system for CLI applications."""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class HelpTopic:
    """Help topic definition.

    Attributes:
        name (str): Topic name
        content (str): Topic content
        category (Optional[str]): Topic category

    """

    name: str
    content: str
    category: str | None = None


@dataclass
class HelpCategory:
    """Category of related help topics.

    Attributes:
        name (str): Category name
        description (str): Category description
        topics (List[HelpTopic]): Topics in the category

    """

    name: str
    description: str = ""
    topics: list[HelpTopic] = field(default_factory=list)

    def add_topic(self, topic: HelpTopic) -> None:
        """Add a topic to the category.

        Args:
            topic: Topic to add

        """
        topic.category = self.name
        self.topics.append(topic)


class HelpManager:
    """Manager for help topics and categories.

    Attributes:
        topics (Dict[str, HelpTopic]): Registered topics
        categories (Dict[str, HelpCategory]): Help categories

    """

    def __init__(self) -> None:
        """Initialize the help manager."""
        self.topics: dict[str, HelpTopic] = {}
        self.categories: dict[str, HelpCategory] = {}

    def register_topic(self, topic: HelpTopic) -> None:
        """Register a help topic.

        Args:
            topic: Topic to register

        """
        self.topics[topic.name] = topic
        if topic.category and topic.category not in self.categories:
            self.categories[topic.category] = HelpCategory(name=topic.category)
            self.categories[topic.category].add_topic(topic)

    def register_category(self, category: HelpCategory) -> None:
        """Register a help category.

        Args:
            category: Category to register

        """
        self.categories[category.name] = category
        for topic in category.topics:
            self.topics[topic.name] = topic

    def get_topic(self, name: str) -> HelpTopic | None:
        """Get a help topic by name.

        Args:
            name: Topic name

        Returns:
            Optional[HelpTopic]: Topic if found

        """
        return self.topics.get(name)

    def get_category(self, name: str) -> HelpCategory | None:
        """Get a help category by name.

        Args:
            name: Category name

        Returns:
            Optional[HelpCategory]: Category if found

        """
        return self.categories.get(name)

    def list_topics(self) -> list[HelpTopic]:
        """List all registered help topics.

        Returns:
            List[HelpTopic]: List of topics

        """
        return list(self.topics.values())

    def list_categories(self) -> list[HelpCategory]:
        """List all help categories.

        Returns:
            List[HelpCategory]: List of categories

        """
        return list(self.categories.values())
