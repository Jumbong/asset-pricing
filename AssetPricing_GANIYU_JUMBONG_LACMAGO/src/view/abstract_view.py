from abc import ABC, abstractmethod

class AbstractView(ABC):
    """Abstract class for views."""

    @abstractmethod
    def display(self):
        """Display the view."""
        pass

    @abstractmethod
    def choose(self):
        """Make choice."""
        pass

