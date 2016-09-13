import aiomas
import numpy as np
from .agent import Agent
from itertools import product
from functools import partial


class World(Agent):
    pass


class GridWorld(World):
    """a 2d grid world"""
    state_vars = ['grid']

    _wrap_mask = np.array([
        True, True, True,
        True, False, True,
        True, True, True])

    def init(self, state, wraps=False):
        self.height, self.width = self.state.grid.shape
        self.wraps = wraps

    @aiomas.expose
    def set_position(self, value, position):
        """set the value of a position in the grid.
        this can be, for example, an agent address."""
        x, y = position
        self.state.grid[x, y] = value

    def move_position(self, from_pos, to_pos, reset_val=0):
        return partial(self._move_position,
                       from_pos, to_pos, reset_val=reset_val)

    def _move_position(self, from_pos, to_pos, state, reset_val=0):
        """'moves' a value from one position to another"""
        tx, ty = to_pos
        fx, fy = from_pos
        state.grid[tx, ty] = state.grid[from_pos]
        state.grid[fx, fy] = reset_val
        return state

    @aiomas.expose
    def neighbors(self, position):
        """returns the neighbors around the position,
        i.e. the values of the surrounding cells"""
        x, y = position
        if self.wraps:
            return np.pad(self.state.grid, 1, mode='wrap')[
                max(0, x):x+3,
                max(0, y):y+3].ravel()[self._wrap_mask]
        else:
            xs = [x]
            ys = [y]
            if x > 0:
                xs.append(x-1)
            if x < self.width-1:
                xs.append(x+1)
            if y > 0:
                ys.append(y-1)
            if y < self.height-1:
                ys.append(y+1)

            return self.state.grid[
                list(zip(*product(xs, ys)))
            ].ravel()[1:]

    @aiomas.expose
    def vacancies(self, empty_val=0):
        return np.vstack(np.where(self.state.grid == empty_val)).T


class VoxelWorld(World):
    """a 3d grid world"""
    state_vars = ['grid']

    _wrap_mask = np.array([
        [True, True, True,
         True, True, True,
         True, True, True],
        [True, True, True,
         True, False, True,
         True, True, True],
        [True, True, True,
         True, True, True,
         True, True, True]])

    def init(self, state, wraps=False):
        self.height, self.width, self.depth = self.state.grid.shape
        self.wraps = wraps

    @aiomas.expose
    def set_position(self, value, position):
        """set the value of a position in the grid.
        this can be, for example, an agent address."""
        x, y, z = position
        self.state.grid[x, y, z] = value

    def move_position(self, from_pos, to_pos, reset_val=0):
        return partial(self._move_position,
                       from_pos, to_pos, reset_val=reset_val)

    def _move_position(self, from_pos, to_pos, state, reset_val=0):
        """'moves' a value from one position to another"""
        tx, ty, tz = to_pos
        fx, fy, fz = from_pos
        state.grid[tx, ty, tz] = state.grid[from_pos]
        state.grid[fx, fy, fz] = reset_val
        return state

    @aiomas.expose
    def neighbors(self, position):
        """returns the neighbors around the position,
        i.e. the values of the surrounding cells"""
        x, y, z = position
        if self.wraps:
            return np.pad(self.state.grid, 1, mode='wrap')[
                max(0, x):x+3,
                max(0, y):y+3,
                max(0, z):z+3].ravel()[self._wrap_mask]
        else:
            xs = [x]
            ys = [y]
            zs = [z]
            if x > 0:
                xs.append(x-1)
            if x < self.width-1:
                xs.append(x+1)
            if y > 0:
                ys.append(y-1)
            if y < self.height-1:
                ys.append(y+1)
            if z > 0:
                zs.append(z-1)
            if z < self.depth-1:
                zs.append(z+1)

            return self.state.grid[
                list(zip(*product(xs, ys, zs)))
            ].ravel()[1:]

    @aiomas.expose
    def vacancies(self, empty_val=0):
        return np.vstack(np.where(self.state.grid == empty_val)).T
