#!/usr/bin/env python3

# Copyright © 2020-2024, Meheret Tesfaye Batu <meherett.batu@gmail.com>
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit

from abc import (
    ABC, abstractmethod
)
from typing import (
    Union, Optional
)

from ..mnemonics import IMnemonic


class ISeed(ABC):

    _name: str
    _seed: str

    def __init__(self, seed: str, **kwargs) -> None:
        """
        Initialize an object with a seed value.

        :param seed: The seed value used for initialization.
        :type seed: str

        :return: No return
        :rtype: NoneType
        """

        self._seed = seed

    @classmethod
    def name(cls) -> str:
        pass

    def seed(self) -> str:
        """
        Retrieves the seed associated with the current instance.

        :return: The seed as a string.
        :rtype: str
        """

        return self._seed

    @classmethod
    @abstractmethod
    def from_mnemonic(cls, mnemonic: Union[str, IMnemonic]) -> str:
        pass
