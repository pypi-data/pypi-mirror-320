from yta_general_utils.math.graphic.graphic_axis import GraphicAxis
from yta_general_utils.math.graphic.node import Node
from yta_general_utils.math.graphic.pair_of_nodes import PairOfNodes
from yta_general_utils.programming.parameter_validator import NumberValidator, PythonValidator

import matplotlib.pyplot as plt


class Graphic:
    """
    Class that represent a Graphic in which we will
    place Nodes and apply rate functions between
    those nodes to calculate the corresponding y
    values.
    """
    x_axis: GraphicAxis = None
    """
    The x axis which contains the min and max x 
    valid values.
    """
    y_axis: GraphicAxis = None
    """
    The y axis which contains the min and max y
    valid values.
    """
    _nodes: list[Node] = None
    """
    The list of nodes defined in the graphic to
    build it. These nodes are interconnected with
    a rate function.
    """

    @property
    def nodes(self):
        """
        Get the nodes ordered by the x position.
        """
        return sorted(self._nodes, key = lambda node: node.position[0])
    
    @property
    def min_x(self):
        return min(self.nodes, key = lambda node: node.x)
    
    @property
    def max_x(self):
        return max(self.nodes, key = lambda node: node.x)
    
    @property
    def min_y(self):
        return min(self.nodes, key = lambda node: node.y)
    
    @property
    def max_y(self):
        return max(self.nodes, key = lambda node: node.y)
    
    @property
    def pairs_of_nodes(self) -> list[PairOfNodes]:
        """
        Get pairs of nodes ordered by the x position. There
        is, at least, one pair of nodes that will be, if no
        more nodes added, the first and the last one.
        """
        return [
            PairOfNodes(self.nodes[index], self.nodes[index + 1])
            for index, _ in enumerate(self.nodes[1:])
        ]

    def __init__(self, x_axis: GraphicAxis, y_axis: GraphicAxis):
        if not PythonValidator.is_instance(x_axis, GraphicAxis) or not PythonValidator.is_instance(y_axis, GraphicAxis):
            raise Exception('The "x_axis" and "y_axis" parameter must be instances of GraphicAxis class.')

        # TODO: Maybe make it possible to be instantiated with a
        # list of nodes
        
        self.x_axis = x_axis
        self.y_axis = y_axis
        self._nodes = []

    def get_node(self, x: float):
        return next((node for node in self.nodes if node.x == x), None)

    def add_node(self, x: float, y: float):
        """
        Add a new node to the graphic if its position is
        inside the x and y axis ranges and if there is not
        another node in that position.

        This method returns the instance so you can chain
        more than one 'add_node' method call.
        """
        if x < self.x_axis.min or x > self.x_axis.max:
            raise Exception(f'The provided "x" is not in the [{self.x_axis.min}, {self.x_axis.max}] range.')
        
        if y < self.y_axis.min or y > self.x_axis.max:
            raise Exception(f'The provided "y" is not in the [{self.y_axis.min}, {self.y_axis.max}] range.')
        
        if self.get_node(x) is not None:
            raise Exception('There is another node in the provided "x" position.')

        self._nodes.append(Node(x, y))

        return self

    def _get_pair_of_node_from_x(self, x: float):
        """
        Obtain the pair of nodes in which the provided 'x'
        is contained.
        """
        return next((pair_of_node for pair_of_node in self.pairs_of_nodes if x <= pair_of_node.max_x), None)

    def get_y_from_not_normalized_x(self, x: float):
        """
        Return the 'y' value (not normalized) corresponding
        to the provided not normalized 'x' of the graphic.
        """
        if not NumberValidator.is_number_between(x, self.min_x, self.max_x):
            raise Exception(f'The "x" parameter is out of the graphic bounds, it must be between [{self.min_x}, {self.max_x}].')
        
        return self._get_pair_of_node_from_x(x).get_y_from_not_normalized_x(x).value
    
    def plot(self):
        # Limit and draw axis
        plt.xlim(self.x_axis.min, self.x_axis.max)
        plt.ylim(self.y_axis.min, self.y_axis.max)
        plt.axhline(0, color = 'black', linewidth = 1)
        plt.axvline(0, color = 'black', linewidth = 1)

        plt.grid(True)

        # Draw nodes
        x_vals = [node.x for node in self.nodes]
        y_vals = [node.y for node in self.nodes]
        plt.scatter(x_vals, y_vals, color = 'red', s = 100)

        # Draw points between nodes
        xs = []
        ys = []
        for pair_of_node in self.pairs_of_nodes:
            positions = pair_of_node.get_n_xy_values_to_plot(100)
            t_xs, t_ys = zip(*positions)
            xs += t_xs
            ys += t_ys
       
        plt.scatter(xs, ys, color = 'blue', s = 5)
        
        plt.title('')
        plt.xlabel('X axis')
        plt.ylabel('Y axis')
        
        plt.show()