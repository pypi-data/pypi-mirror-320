import AutoRPE.UtilsRPE.Getter as Getter
import AutoRPE.UtilsRPE.VariablePrecision as VariablePrecision
from AutoRPE.UtilsRPE.Error import VariableNotFound
import networkx as nx


def create_nodes(variables: list['Variable'], graph:nx.Graph):
    """
    Creates nodes in the graph for each variable in the given list.

    Parameters:
        variables (list): A list of variables to create nodes for.
        graph (networkx.Graph): The graph in which nodes will be created.

    Raises:
        KeyError: If a variable's `hash_id` is not found in the graph.
        AttributeError: If the `procedure.level` attribute is missing for a variable.
    """
    for v in variables:
        try:
            graph[v.hash_id]
        except KeyError:
            dim = v.dimension if v.dimension is not None else 0
            try:
                weight = v.procedure.level
            except AttributeError:
                weight = 100
            graph.add_node(v.hash_id,
                           dimension=dim,
                           name=v.name,
                           routine=v.procedure.name,
                           module=v.procedure.module.name,
                           intent=str(v.intent),
                           level=weight,
                           is_used=v.is_used,
                           is_banned=v.is_banned,
                           cluster_id=v.cluster_id,
                           external=str(v.is_used_in_external),
                           type=v.type)


def create_edges(argument: 'Variable', dummy: 'Variable', graph: nx.Graph):
    """
    Creates an edge in the graph between two variables based on their relationship.

    Parameters:
        argument (Variable): The first variable.
        dummy (Variable): The second variable.
        graph (networkx.Graph): The graph in which the edge will be created.
    """
    v1, v2 = argument, dummy
    dim = v1.dimension if v1.dimension is not None else 0
    try:
        weight = v1.procedure.level
    except AttributeError:
        weight = 100
    graph.add_edge(v1.hash_id, v2.hash_id,
                   routine=str(v2.procedure.name),
                   kind=str(v2.intent),
                   weight=1 + weight
                   )


def track_dependencies(vault: 'Vault', graph: nx.Graph, var_type: str):
    """
    Tracks dependencies between variables in the vault and updates the graph with nodes and edges.

    Parameters:
        vault (Vault): The vault containing variables and subprogram calls.
        graph (networkx.Graph): The graph to update with dependency information.
        var_type (str): The type of variables to track.

    Returns:
        None

    Raises:
        VariableNotFound: If a variable is not found in the vault while processing pointer assignments.
    """
    total = len(vault.modules)

    for subprogram_call in vault.dictionary_of_calls.values():
        for call in subprogram_call:
            # Get arguments, that have intent out/inout and are real
            if call.subprogram.has_mixed_interface:
                continue
            node = [[a.variable, d] for d, a in zip(call.dummy_arguments, call.arguments)
                    if d.intent in ['out', 'inout'] and d.type in var_type]
            # From the argument, get the variable that is bound
            for arg, dummy_var in node:
                # Create nodes
                create_nodes([arg, dummy_var], graph)
                # Add edges
                create_edges(arg, dummy_var, graph)

    for module_index, module in enumerate(vault.modules.values()):
        print("\rTracking dependencies %i/%i  %20s" % (module_index + 1, total, module.name), end="")
        for line_info in module.line_info:
            # Returns all var_type variables find in line and corresponding dummy argument
            # TODO: Added the  try/except
            try:
                node = Getter.get_pointer_assignment(line_info.unconditional_line, vault, line_info.block, var_type)
            except VariableNotFound as err:
                print(err)
                node = None
            if node:
                # From the argument, get the variable that is bound
                for ptr, target in node:
                    # Create nodes
                    create_nodes([ptr, target], graph)
                    # Add edges
                    create_edges(ptr, target, graph)


def create_graph(vault: 'Vault', graph_name: str, var_type: str):
    """
    Creates a directed graph to represent dependencies, then converts it to an undirected graph.

    Parameters:
        vault (Vault): The vault containing variables and subprogram calls.
        graph_name (str): The name to save the graph to (optional).
        var_type (str): The type of variables to track in the graph.

    Returns:
        networkx.Graph: The undirected graph representing dependencies.

    Raises:
        FileNotFoundError: If saving the graph to disk fails due to an invalid path.
    """
    # Creates a graph to be filled
    graph = nx.DiGraph()

    # Track dependencies
    track_dependencies(vault, graph, var_type)

    # Change graph to undirected
    graph = graph.to_undirected()

    # If a name has been specified, save the graph to disk
    if graph_name:
        nx.write_graphml(graph, graph_name + '.graphml')
    return graph


def propagate_dependencies(vault: 'Vault', graph_name: str=None, var_type: dict=VariablePrecision.real_id):
    """
    Propagates dependencies by creating a graph and storing dependency information into the vault.

    Parameters:
        vault (Vault): The vault containing variables.
        graph_name (str, optional): The name of the graph file to save (defaults to None).
        var_type (dict, optional): The type of variables to track in the graph (defaults to `VariablePrecision.real_id`).

    Returns:
        None

    Raises:
        FileNotFoundError: If saving the graph to disk fails due to an invalid path.
    """
    # Create graph
    graph = create_graph(vault, graph_name, var_type)
    # Get variables in clusters
    variables_in_graph = [v for v in vault.variables if v.hash_id in graph.nodes]
    # Stores info about these dependencies into the vault
    for v in variables_in_graph:
        v.same_as = list(nx.node_connected_component(graph, v.hash_id))
