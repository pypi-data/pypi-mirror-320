# Copyright 2022 Sony Semiconductor Israel, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
from enum import Enum
from functools import partial
from typing import List, Optional
from copy import deepcopy

import numpy as np

from model_compression_toolkit.core import FrameworkInfo
from model_compression_toolkit.core.common import Graph, BaseNode
from model_compression_toolkit.constants import BITS_TO_BYTES, FLOAT_BITWIDTH
from model_compression_toolkit.core.common.framework_implementation import FrameworkImplementation
from model_compression_toolkit.core.common.graph.edge import EDGE_SINK_INDEX
from model_compression_toolkit.core.common.graph.virtual_activation_weights_node import VirtualActivationWeightsNode, \
    VirtualSplitWeightsNode, VirtualSplitActivationNode
from model_compression_toolkit.core.common.graph.memory_graph.memory_graph import MemoryGraph
from model_compression_toolkit.core.common.graph.memory_graph.compute_graph_max_cut import compute_graph_max_cut, Cut
from model_compression_toolkit.logger import Logger


def weights_size_utilization(mp_cfg: List[int],
                             graph: Graph,
                             fw_info: FrameworkInfo,
                             fw_impl: FrameworkImplementation) -> np.ndarray:
    """
    Computes a resource utilization vector with the respective weights' memory size for the given weight configurable node,
    according to the given mixed-precision configuration.
    If an empty configuration is given, then computes resource utilization vector for non-configurable nodes.

    Args:
        mp_cfg: A mixed-precision configuration (list of candidates index for each configurable node)
        graph: Graph object.
        fw_info: FrameworkInfo object about the specific framework (e.g., attributes of different layers' weights to quantize).
        fw_impl: FrameworkImplementation object with specific framework methods implementation (not used in this method).

    Returns: A vector of node's weights memory sizes.
    Note that the vector is not necessarily of the same length as the given config.

    """
    weights_memory = []
    mp_nodes = graph.get_configurable_sorted_nodes_names(fw_info)
    weights_mp_nodes = [n.name for n in graph.get_sorted_weights_configurable_nodes(fw_info)]

    if len(mp_cfg) == 0:
        # Computing non-configurable nodes resource utilization
        # TODO: when enabling multiple attribute quantization by default (currently,
        #  only kernel quantization is enabled) we should include other attributes memory in the sum of all
        #  weights memory (when quantized to their default 8-bit, non-configurable).
        #  When implementing this, we should just go over all attributes in the node instead of counting only kernels.
        for n in graph.nodes:
            kernel_attr = fw_info.get_kernel_op_attributes(n.type)[0]
            if kernel_attr is None:
                continue
            non_configurable_node = n.name not in weights_mp_nodes \
                                    and not n.reuse \
                                    and n.is_all_weights_candidates_equal(kernel_attr)

            if non_configurable_node:
                node_nbits = (n.candidates_quantization_cfg[0].weights_quantization_cfg
                              .get_attr_config(kernel_attr).weights_n_bits)
                node_weights_memory_in_bytes = _compute_node_weights_memory(n, node_nbits, fw_info)
                weights_memory.append(node_weights_memory_in_bytes)
    else:
        # Go over configurable all nodes that should be taken into consideration when computing the weights
        # resource utilization.
        for n in graph.get_sorted_weights_configurable_nodes(fw_info):
            # Only nodes with kernel op can be considered configurable
            kernel_attr = fw_info.get_kernel_op_attributes(n.type)[0]
            node_idx = mp_nodes.index(n.name)
            node_qc = n.candidates_quantization_cfg[mp_cfg[node_idx]]
            node_nbits = node_qc.weights_quantization_cfg.get_attr_config(kernel_attr).weights_n_bits

            node_weights_memory_in_bytes = _compute_node_weights_memory(n, node_nbits, fw_info)

            weights_memory.append(node_weights_memory_in_bytes)

    return np.array(weights_memory)


def calc_graph_cuts(graph: Graph) -> List[Cut]:
    """
    Calculate graph activation cuts.
    Args:
        graph: A graph object to calculate activation cuts on.

    Returns:
        A list of activation cuts.

    """
    memory_graph = MemoryGraph(deepcopy(graph))
    _, _, cuts = compute_graph_max_cut(memory_graph)

    if cuts is None:
        Logger.critical("Failed to calculate activation memory cuts for graph.")  # pragma: no cover
    # filter empty cuts and cuts that contain only nodes with activation quantization disabled.
    filtered_cuts = []
    for cut in cuts:
        cut_has_no_act_quant_nodes = any(
            [graph.find_node_by_name(e.node_name)[0].has_activation_quantization_enabled_candidate()
             for e in cut.mem_elements.elements])
        if len(cut.mem_elements.elements) > 0 and cut_has_no_act_quant_nodes:
            filtered_cuts.append(cut)
    return filtered_cuts


def activation_maxcut_size_utilization(mp_cfg: List[int],
                                       graph: Graph,
                                       fw_info: FrameworkInfo,
                                       fw_impl: FrameworkImplementation,
                                       cuts: Optional[List[Cut]] = None) -> np.ndarray:
    """
    Computes a resource utilization vector with the respective output memory max-cut size for activation
    nodes, according to the given mixed-precision configuration.

    Args:
        mp_cfg: A mixed-precision configuration (list of candidates index for each configurable node)
        graph: Graph object.
        fw_info: FrameworkInfo object about the specific framework (e.g., attributes of different layers' weights to quantize)
            (not used in this method).
        fw_impl: FrameworkImplementation object with specific framework methods implementation(not used in this method).
        cuts: a list of graph cuts (optional. if not provided calculated locally).
    TODO maxcut: refactor - need to remove the cuts so all metric functions signatures are the same.

    Returns: A vector of node's cut memory sizes.
    Note that the vector is not necessarily of the same length as the given config.

    """
    if len(mp_cfg) == 0:
        # Computing non-configurable nodes resource utilization for max-cut is included in the calculation of the
        # configurable nodes.
        return np.array([])

    activation_cut_memory = []
    mp_nodes = graph.get_configurable_sorted_nodes_names(fw_info)
    # Go over all nodes that should be taken into consideration when computing the weights memory utilization.
    nodes_act_nbits = {}
    for n in graph.get_sorted_activation_configurable_nodes():
        node_idx = mp_nodes.index(n.name)
        node_qc = n.candidates_quantization_cfg[mp_cfg[node_idx]]
        node_nbits = node_qc.activation_quantization_cfg.activation_n_bits
        nodes_act_nbits[n.name] = node_nbits

    if cuts is None:
        cuts = calc_graph_cuts(graph)

    for i, cut in enumerate(cuts):
        mem_elements = [m.node_name for m in cut.mem_elements.elements]
        mem = 0
        for op_name in mem_elements:
            n = graph.find_node_by_name(op_name)[0]
            if n.is_activation_quantization_enabled():
                base_nbits = n.candidates_quantization_cfg[0].activation_quantization_cfg.activation_n_bits
                mem += _compute_node_activation_memory(n, nodes_act_nbits.get(op_name, base_nbits))

        activation_cut_memory.append(mem)

    return np.array(activation_cut_memory)


# TODO maxcut: add test for this function and remove no cover
def activation_output_size_utilization(mp_cfg: List[int],
                                       graph: Graph,
                                       fw_info: FrameworkInfo,
                                       fw_impl: FrameworkImplementation) -> np.ndarray:  # pragma: no cover
    """
    Computes a resource utilization vector with the respective output memory size for each activation configurable node,
    according to the given mixed-precision configuration.
    If an empty configuration is given, then computes resource utilization vector for non-configurable nodes.

    Args:
        mp_cfg: A mixed-precision configuration (list of candidates index for each configurable node)
        graph: Graph object.
        fw_info: FrameworkInfo object about the specific framework (e.g., attributes of different layers' weights to quantize)
            (not used in this method).
        fw_impl: FrameworkImplementation object with specific framework methods implementation(not used in this method).

    Returns: A vector of node's activation memory sizes.
    Note that the vector is not necessarily of the same length as the given config.

    """
    activation_memory = []
    mp_nodes = graph.get_configurable_sorted_nodes_names(fw_info)
    activation_mp_nodes = [n.name for n in graph.get_sorted_activation_configurable_nodes()]

    if len(mp_cfg) == 0:
        # Computing non-configurable nodes resource utilization
        for n in graph.nodes:
            non_configurable_node = n.name not in activation_mp_nodes \
                                    and n.has_activation_quantization_enabled_candidate() \
                                    and n.is_all_activation_candidates_equal()

            if non_configurable_node:
                node_nbits = n.candidates_quantization_cfg[0].activation_quantization_cfg.activation_n_bits
                node_activation_memory_in_bytes = _compute_node_activation_memory(n, node_nbits)
                activation_memory.append(node_activation_memory_in_bytes)
    else:
        # Go over all nodes that should be taken into consideration when computing the weights memory utilization.
        for n in graph.get_sorted_activation_configurable_nodes():
            node_idx = mp_nodes.index(n.name)
            node_qc = n.candidates_quantization_cfg[mp_cfg[node_idx]]
            node_nbits = node_qc.activation_quantization_cfg.activation_n_bits

            node_activation_memory_in_bytes = _compute_node_activation_memory(n, node_nbits)

            activation_memory.append(node_activation_memory_in_bytes)

    return np.array(activation_memory)


def total_weights_activation_utilization(mp_cfg: List[int],
                                         graph: Graph,
                                         fw_info: FrameworkInfo,
                                         fw_impl: FrameworkImplementation) -> np.ndarray:
    """
    Computes resource utilization tensor with the respective weights size and output memory size for each activation configurable node,
    according to the given mixed-precision configuration.
    If an empty configuration is given, then computes resource utilization vector for non-configurable nodes.

    Args:
        mp_cfg: A mixed-precision configuration (list of candidates index for each configurable node)
        graph: Graph object.
        fw_info: FrameworkInfo object about the specific framework (e.g., attributes of different layers' weights to quantize)
            (not used in this method).
        fw_impl: FrameworkImplementation object with specific framework methods implementation(not used in this method).

    Returns: A 2D tensor of nodes' weights memory sizes and activation output memory size.
    Note that the vector is not necessarily of the same length as the given config.

    """
    weights_activation_memory = []
    weights_mp_nodes = [n.name for n in graph.get_sorted_weights_configurable_nodes(fw_info)]
    activation_mp_nodes = [n.name for n in graph.get_sorted_activation_configurable_nodes()]

    if len(mp_cfg) == 0:
        # Computing non-configurable nodes utilization
        for n in graph.nodes:

            non_configurable = False
            node_weights_memory_in_bytes, node_activation_memory_in_bytes = 0, 0

            # Non-configurable Weights
            # TODO: currently considering only kernel attributes in weights memory utilization.
            #  When enabling multi-attribute quantization we need to modify this method to count all attributes.
            kernel_attr = fw_info.get_kernel_op_attributes(n.type)[0]
            if kernel_attr is not None:
                is_non_configurable_weights = n.name not in weights_mp_nodes and \
                                              n.is_all_weights_candidates_equal(kernel_attr) and \
                                              not n.reuse

                if is_non_configurable_weights:
                    node_nbits = (n.candidates_quantization_cfg[0].weights_quantization_cfg
                                  .get_attr_config(kernel_attr).weights_n_bits)
                    node_weights_memory_in_bytes = _compute_node_weights_memory(n, node_nbits, fw_info)
                    non_configurable = True

            # Non-configurable Activation
            is_non_configurable_activation = n.name not in activation_mp_nodes and \
                                             n.has_activation_quantization_enabled_candidate() and \
                                             n.is_all_activation_candidates_equal()

            if is_non_configurable_activation:
                node_nbits = n.candidates_quantization_cfg[0].activation_quantization_cfg.activation_n_bits
                node_activation_memory_in_bytes = _compute_node_activation_memory(n, node_nbits)
                non_configurable = True

            if non_configurable:
                weights_activation_memory.append(
                    np.array([node_weights_memory_in_bytes, node_activation_memory_in_bytes]))
    else:
        # Go over all nodes that should be taken into consideration when computing the weights or
        # activation memory utilization (all configurable nodes).
        for node_idx, n in enumerate(graph.get_configurable_sorted_nodes(fw_info)):
            # TODO: currently considering only kernel attributes in weights memory utilization. When enabling multi-attribute
            #  quantization we need to modify this method to count all attributes.

            node_qc = n.candidates_quantization_cfg[mp_cfg[node_idx]]

            # Compute node's weights memory (if no weights to quantize then set to 0)
            node_weights_memory_in_bytes = 0
            kernel_attr = fw_info.get_kernel_op_attributes(n.type)[0]
            if kernel_attr is not None:
                if n.is_weights_quantization_enabled(kernel_attr) and not n.is_all_weights_candidates_equal(kernel_attr):
                    node_weights_nbits = node_qc.weights_quantization_cfg.get_attr_config(kernel_attr).weights_n_bits
                    node_weights_memory_in_bytes = _compute_node_weights_memory(n, node_weights_nbits, fw_info)

            # Compute node's activation memory (if node's activation are not being quantized then set to 0)
            node_activation_nbits = node_qc.activation_quantization_cfg.activation_n_bits
            node_activation_memory_in_bytes = 0
            if n.is_activation_quantization_enabled() and not n.is_all_activation_candidates_equal():
                node_activation_memory_in_bytes = _compute_node_activation_memory(n, node_activation_nbits)

            weights_activation_memory.append(np.array([node_weights_memory_in_bytes, node_activation_memory_in_bytes]))

    return np.array(weights_activation_memory)


def bops_utilization(mp_cfg: List[int],
                     graph: Graph,
                     fw_info: FrameworkInfo,
                     fw_impl: FrameworkImplementation,
                     set_constraints: bool = True) -> np.ndarray:
    """
    Computes a resource utilization vector with the respective bit-operations (BOPS) count for each configurable node,
    according to the given mixed-precision configuration of a virtual graph with composed nodes.

    Args:
        mp_cfg: A mixed-precision configuration (list of candidates index for each configurable node)
        graph: Graph object.
        fw_info: FrameworkInfo object about the specific framework (e.g., attributes of different layers' weights to quantize).
        fw_impl: FrameworkImplementation object with specific framework methods implementation.
        set_constraints: A flag for utilizing the method for resource utilization computation of a
            given config not for LP formalization purposes.

    Returns: A vector of node's BOPS count.
    Note that the vector is not necessarily of the same length as the given config.

    """

    if not set_constraints:
        return _bops_utilization(mp_cfg,
                                 graph,
                                 fw_info,
                                 fw_impl)

    # BOPs utilization method considers non-configurable nodes, therefore, it doesn't need separate implementation
    # for non-configurable nodes for setting a constraint (no need for separate implementation for len(mp_cfg) = 0).

    virtual_bops_nodes = [n for n in graph.get_topo_sorted_nodes() if isinstance(n, VirtualActivationWeightsNode)]

    mp_nodes = graph.get_configurable_sorted_nodes_names(fw_info)
    bops = [n.get_bops_count(fw_impl, fw_info, candidate_idx=_get_node_cfg_idx(n, mp_cfg, mp_nodes)) for n in virtual_bops_nodes]

    return np.array(bops)


def _bops_utilization(mp_cfg: List[int],
                      graph: Graph,
                      fw_info: FrameworkInfo,
                      fw_impl: FrameworkImplementation) -> np.ndarray:
    """
    Computes a resource utilization vector with the respective bit-operations (BOPS) count for each configurable node,
    according to the given mixed-precision configuration of an original graph.

    Args:
        mp_cfg: A mixed-precision configuration (list of candidates index for each configurable node)
        graph: Graph object.
        fw_info: FrameworkInfo object about the specific framework (e.g., attributes of different layers' weights to quantize).
        fw_impl: FrameworkImplementation object with specific framework methods implementation.

    Returns: A vector of node's BOPS count.

    """

    mp_nodes = graph.get_configurable_sorted_nodes_names(fw_info)

    # Go over all nodes that should be taken into consideration when computing the BOPS utilization.
    bops = []
    for n in graph.get_topo_sorted_nodes():
        if n.has_kernel_weight_to_quantize(fw_info) and not n.has_positional_weights:
            # If node doesn't have weights then its MAC count is 0, and we shouldn't consider it in the BOPS count.
            incoming_edges = graph.incoming_edges(n, sort_by_attr=EDGE_SINK_INDEX)
            if len(incoming_edges) != 1:
                Logger.critical(f"Unable to compute BOPS metric for node {n.name} due to multiple inputs.")  # pragma: no cover
            input_activation_node = incoming_edges[0].source_node
            if len(graph.out_edges(input_activation_node)) > 1:
                # In the case where the activation node has multiple outgoing edges
                # we don't consider this edge in the BOPS utilization calculation
                continue

            input_activation_node_cfg = input_activation_node.candidates_quantization_cfg[_get_node_cfg_idx(input_activation_node, mp_cfg, mp_nodes)]

            node_mac = fw_impl.get_node_mac_operations(n, fw_info)

            node_qc = n.candidates_quantization_cfg[_get_node_cfg_idx(n, mp_cfg, mp_nodes)]
            kenrel_node_qc = node_qc.weights_quantization_cfg.get_attr_config(fw_info.get_kernel_op_attributes(n.type)[0])
            node_weights_nbits = kenrel_node_qc.weights_n_bits if \
                kenrel_node_qc.enable_weights_quantization else FLOAT_BITWIDTH
            input_activation_nbits = input_activation_node_cfg.activation_quantization_cfg.activation_n_bits if \
                input_activation_node_cfg.activation_quantization_cfg.enable_activation_quantization else FLOAT_BITWIDTH

            node_bops = node_weights_nbits * input_activation_nbits * node_mac
            bops.append(node_bops)

    return np.array(bops)


def _get_node_cfg_idx(node: BaseNode, mp_cfg: List[int], sorted_configurable_nodes_names: List[str]) -> int:
    """
    Returns the index of a node's quantization configuration candidate according to the given
    mixed-precision configuration. If the node is not configurable, then it must have a single configuration,
    therefore, the index 0 is returned.

    Args:
        node: A node to get its candidate configuration index.
        mp_cfg: A mixed-precision configuration (list of candidates index for each configurable node)
        sorted_configurable_nodes_names: A list of configurable nodes names.

    Returns: An index (integer) of a node's quantization configuration candidate.
    """

    if node.name in sorted_configurable_nodes_names:
        node_idx = sorted_configurable_nodes_names.index(node.name)
        return mp_cfg[node_idx]
    else:
        assert len(node.candidates_quantization_cfg) > 0, \
            "Any node should have at least one candidate configuration."
        return 0


def _get_origin_weights_node(n: BaseNode) -> BaseNode:
    """
    In case we run a resource utilization computation on a virtual graph,
    this method is used to retrieve the original node out of a virtual weights node,

    Args:
        n: A possibly virtual node.

    Returns: A node from the original (non-virtual) graph which the given node represents.

    """

    if isinstance(n, VirtualActivationWeightsNode):
        return n.original_weights_node
    if isinstance(n, VirtualSplitWeightsNode):
        return n.origin_node

    return n


def _get_origin_activation_node(n: BaseNode) -> BaseNode:
    """
    In case we run a resource utilization computation on a virtual graph,
    this method is used to retrieve the original node out of a virtual activation node,

    Args:
        n: A possibly virtual node.

    Returns: A node from the original (non-virtual) graph which the given node represents.

    """

    if isinstance(n, VirtualActivationWeightsNode):
        return n.original_activation_node
    if isinstance(n, VirtualSplitActivationNode):
        return n.origin_node

    return n


def _compute_node_weights_memory(n: BaseNode, node_nbits: int, fw_info: FrameworkInfo) -> float:
    """
    Computes the weights' memory of the given node.

    Args:
        n: A node to compute its weights' memory.
        node_nbits: A bit-width in which the node's weights should be quantized.
        fw_info: FrameworkInfo object about the specific framework.

    Returns: The total memory of the node's weights when quantized to the given bit-width.

    """

    origin_node = _get_origin_weights_node(n)

    node_num_weights_params = 0
    for attr in fw_info.get_kernel_op_attributes(origin_node.type):
        if attr is not None:
            node_num_weights_params += origin_node.get_weights_by_keys(attr).flatten().shape[0]

    return node_num_weights_params * node_nbits / BITS_TO_BYTES


def _compute_node_activation_memory(n: BaseNode, node_nbits: int) -> float:
    """
    Computes the activation tensor memory of the given node.

    Args:
        n: A node to compute its activation tensor memory.
        node_nbits: A bit-width in which the node's weights should be quantized.

    Returns: The total memory of the node's activation tensor when quantized to the given bit-width.

    """

    origin_node = _get_origin_activation_node(n)
    node_output_size = origin_node.get_total_output_params()

    return node_output_size * node_nbits / BITS_TO_BYTES


class MpRuMetric(Enum):
    """
    Defines resource utilization computation functions that can be used to compute bops_utilization for a given target
    for a given mp config. The enum values can be used to call a function on a set of arguments.

     WEIGHTS_SIZE - applies the weights_size_utilization function

     ACTIVATION_MAXCUT_SIZE - applies the activation_maxcut_size_utilization function.

     ACTIVATION_OUTPUT_SIZE - applies the activation_output_size_utilization function

     TOTAL_WEIGHTS_ACTIVATION_SIZE - applies the total_weights_activation_utilization function

     BOPS_COUNT - applies the bops_utilization function

    """

    WEIGHTS_SIZE = partial(weights_size_utilization)
    ACTIVATION_MAXCUT_SIZE = partial(activation_maxcut_size_utilization)
    ACTIVATION_OUTPUT_SIZE = partial(activation_output_size_utilization)
    TOTAL_WEIGHTS_ACTIVATION_SIZE = partial(total_weights_activation_utilization)
    BOPS_COUNT = partial(bops_utilization)

    def __call__(self, *args):
        return self.value(*args)
