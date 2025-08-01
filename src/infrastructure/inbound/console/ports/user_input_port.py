from abc import ABC, abstractmethod
from argparse import Namespace

class UserInputPort(ABC):
    @abstractmethod
    def get_user_input(self) -> Namespace:
        pass