import numpy as np


class Distributor:
    """a distributor, given an agent, returns
    the node manager to send it to"""
    pass


class RoundRobin(Distributor):
    """distributes agents sequentially"""
    def __init__(self, managers):
        self.index = 0
        self.managers = managers

    def next(self, agent):
        prev = self.index
        if self.index == len(self.managers) - 1:
            self.index = 0
        else:
            self.index += 1
        return self.managers[prev]


class Grid2DPartition(Distributor):
    """partitions a 2d grid, distributing agents accordingly"""
    def __init__(self, managers, grid_shape):
        # convert to grid of positions
        xs, ys = np.indices(grid_shape)
        self.grid = np.vstack(([xs.T],[ys.T])).T

        # construct a mapping of grid positions to managers
        self.pos_to_manager = {}
        for i, subgrid in enumerate(self.partition_grid(self.grid, len(managers))):
            for chunk in subgrid:
                for pos in chunk:
                    self.pos_to_manager[tuple(pos)] = managers[i]

    def partition_grid(grid, n):
        """simple partitioning method,
        bisect the largest chunk along its longest axis"""
        parts = [grid]
        while n > 1:
            part = parts.pop(0)
            w, h = part.shape
            axis = 0 if w > h else 1
            parts += np.array_split(part, 2, axis=axis)
            n -= 1
        return parts

    def next(self, agent):
        return self.pos_to_manager[agent.state.position]
