"""Instantiates the global :class:`~.InputState.InputState` object."""

__all__ = ['inputState']

# This file had to be separated from MessengerGlobal to resolve a
# circular include dependency with DirectObject.

from toontown.controls import InputState

#: The global :class:`~.InputState.InputState` object.
inputState = InputState.InputState()
