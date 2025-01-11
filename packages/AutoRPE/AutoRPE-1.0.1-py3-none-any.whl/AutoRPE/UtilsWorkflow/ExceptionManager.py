""""Different ways of handling exception"""


def divide_and_force(analyzed_job: 'Job', binary_tree: 'BinaryTree'):
    """
    Handles exceptions by dividing and forcing variables for analyzed jobs.

    Parameters:
        analyzed_job (Job): The job being analyzed.
        binary_tree (BinaryTree): The binary tree managing the job states.

    Returns:
        None
    """
    # Move the father to suspend queue
    # print("Exception found!", analyzed_job.kind_of_exception())
    binary_tree.move_to_suspended(analyzed_job)

    child_1, child_2 = analyzed_job.child
    hash_1, hash_2 = child_1.hash, child_2.hash
    # The analysis variables of one child are the forced variables of the other one
    child_1.forced_ids.extend(id for id in child_2.id_reduced_precision if id not in child_1.forced_ids)
    child_2.forced_ids.extend(id for id in child_1.id_reduced_precision if id not in child_2.forced_ids)

    # Avoid loops making them fail
    if child_1.hash == hash_1 or child_2.hash == hash_2:
        binary_tree.move_to_failed(analyzed_job)
    else:
        for ch in analyzed_job.child:
            binary_tree.move_to_pending(ch)
            # Disinherit all child's descendants
            for job in ch.descendants():
                job.parent = None
            ch.child = []
    # Save disinherited jobs
    disinherited = [j for j in binary_tree.all() if j.parent is None and j.level != 0]
    for job in disinherited:
        binary_tree[job.status].remove(job)
        if job not in binary_tree.disinherited:
            binary_tree.disinherited.append(job)


def resolve_exception(analyzed_job: 'Job', binary_tree: 'BinaryTree'):
    """
    Resolves exceptions during job analysis.

    Parameters:
        analyzed_job (Job): The job that encountered an exception.
        binary_tree (BinaryTree): The binary tree managing job states.

    Returns:
        None
    """
    # more than 2 children, we are in the loop of children_fail_test
    if len(analyzed_job.child) > 2:
        children_submit_batch(analyzed_job, binary_tree)

    # Variables are good separately but bad together (and they cannot be divided further)
    elif len(analyzed_job.id_reduced_precision) == 2:
        binary_tree.move_to_failed(analyzed_job)
    else:
        print("Job failed while kids were ok, reanalyzing")
        analyzed_job.print_info_job("suspended")

        # Exception handling
        # Compute dictionary of descendants with their red. prec. variables
        child_analysis_set_dict = {}
        analyzed_job.find_child_set(child_analysis_set_dict)

        # Number of descendants is small
        if len(child_analysis_set_dict) <= 10 \
                and (not analyzed_job.child[0].child
                     or not analyzed_job.child[1].child)\
                and not analyzed_job.has_cluster():
            # One of the child that failed together, has never been divided: divide, and try to find the bad var
            divide_and_force(analyzed_job, binary_tree)
            return
        else:
            # Compute the cost of banning one of the children
            success_child, failed_child = choose_child(analyzed_job)
            # Amount of banned variables is too high, try to keep the good jobs
            if len(failed_child.id_reduced_precision) > 10 and not analyzed_job.reshuffle:
                children_fail_test(analyzed_job, binary_tree)
            # Affordable, ban just one child
            else:
                binary_tree.move_to_failed(failed_child)
                binary_tree.move_to_success(analyzed_job)
            return


def choose_child(analyzed_job: 'Job'):
    """
    Selects the child job for further analysis based on variable restrictions.

    Parameters:
        analyzed_job (Job): The parent job with children to analyze.

    Returns:
        tuple: The selected success_child and failed_child.
    """
    # Choose one of the children
    if len(analyzed_job.child[0].banned_variables) == len(analyzed_job.child[1].banned_variables):
        # Same number of banned variables, then ban the smalled analysis set, or promote child 0 if the len is the same
        if len(analyzed_job.child[0].id_reduced_precision) >= len(analyzed_job.child[0].id_reduced_precision):
            success_child = analyzed_job.child[0]
            failed_child = analyzed_job.child[1]
        else:
            success_child = analyzed_job.child[1]
            failed_child = analyzed_job.child[2]
    elif len(analyzed_job.child[0].banned_variables) > len(analyzed_job.child[1].banned_variables):
        # Ban the child with the greatest number of banned variables
        success_child = analyzed_job.child[1]
        failed_child = analyzed_job.child[0]
    else:
        success_child = analyzed_job.child[0]
        failed_child = analyzed_job.child[1]
    return success_child, failed_child


def children_fail_test(analyzed_job: 'Job', binary_tree: 'BinaryTree'):
    """
    Handles failure of children jobs by separating them into batches.

    Parameters:
        analyzed_job (Job): The job being analyzed.
        binary_tree (BinaryTree): The binary tree managing the job states.

    Returns:
        None
    """
    # Separate the descendants in batches if they haven't yet
    analyzed_job.create_children_batch()
    binary_tree.move_to_suspended(analyzed_job)
    children_submit_batch(analyzed_job, binary_tree)


def children_submit_batch(analyzed_job: 'Job', binary_tree: 'BinaryTree'):
    """
    Submits a batch of children jobs for analysis.

    Parameters:
        analyzed_job (Job): The job whose children are being submitted.
        binary_tree (BinaryTree): The binary tree managing job states.

    Returns:
        None
    """

    # Update children with new batch
    analyzed_job.child = analyzed_job.child_batch_list[analyzed_job.batch_counter]

    # Submit intended batch of children
    for ch in analyzed_job.child:
        if ch not in binary_tree.all():
            binary_tree.move_to_pending(ch)

    # Increment batch counter
    analyzed_job.batch_counter += 1






