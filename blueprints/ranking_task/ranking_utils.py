def get_scores(elements, ordering):
    """
    Given a set of elements and an ordering of these elements, compute the 'scores' of the elements according to the ordering.
    All element are assumed to be unique.

    Example: elements: [A, B, C] and ranking [B, C, A] will yield [2, 0, 1].

    @param elements Base list of elements.
    @param ordering Ordering of the elements.
    """
    assert len(elements) == len(ordering), "Can't determine the permutation of two orderings of different size"
    assert set(elements) == set(ordering), "Elements and ordering do not contain the same elements"

    return [ordering.index(elem) for elem in elements]

def aggregate_rankings(orderings):
    """
    Given a list of orderings of some base set, aggregate this into a single ordering.
    The resulting ordering can contain **ties**.
    Therefore we encode the result as a list of sets of the elements.

    @param orderings List of orderings.
    """
    # some sanity checks
    assert len(orderings) > 0, "Can't aggregate 0 orderings."
    elements = set(orderings[0])
    # we assume that all orderings are over the same base set
    assert len(set([len(ordering) for ordering in orderings])) == 1, "Can't aggregate orderings of different size."
    assert all([set(ordering) == elements for ordering in orderings]), "Can't aggregate orderings with different elements."

    return aggregate_rankings_avg_score(orderings)

def aggregate_rankings_avg_score(orderings):
    """
    Given a list of orderings of some base set, compute and average the scores. Then build the ranking according to these scores.

    @param orderings List of orderings. They are assumed to contain the same elements and have the same length.
    """

    base_ordering = orderings[0]
    # compute scores of elements
    scores = [get_scores(base_ordering, ordering) for ordering in orderings]

    # sum scores; don't bother to normalize because we are only interested '<' relation between scores
    sum_scores = [sum(elem_scores) for elem_scores in zip(*scores)]

    # create dictionary which keys are scores and values are sets of elements with that score
    # init
    score_dict = {score: set() for score in sum_scores}
    # add elements
    for (elem, score) in zip(base_ordering, sum_scores):
        score_dict[score].add(elem)

    # sort base ordering by summed scores and return
    return [elems for (score, elems) in sorted(score_dict.items(), key=lambda x: x[0], reverse=False)]

def aggregate_rankings_top_count(orderings):
    """
    Given a list of orderings of some base set, order the elements by the number of times they got ranked best.

    @param orderings List of orderings. They are assumed to contain the same elements and have the same length.
    """
    elements = orderings[0]

    # count the number of times every element ranked best
    top_counts = {elem: 0 for elem in elements}
    for ordering in orderings:
        top_counts[ordering[0]] += 1

    # create dictionary which keys are top-counts and values are sets of elements with that top count
    score_dict = {score: set() for score in top_counts.values()}
    for (elem, top_count) in top_counts.items():
        score_dict[top_count].add(elem)

    # return sorted list
    return [elems for (top_count, elems) in sorted(score_dict.items(), key=lambda x: x[0], reverse=True)]

def get_ordering_agreement(reference, ordering):
    """
    Given a reference ordering **with ties** compute an agreement score of 'ordering' which is an order **without ties**.

    @param reference A list of sets that encodes an ordering with ties.
    @param ordering A list of elements that encodes an ordering without ties.

    @return Agreement score. Higher is better.
    """

    # sanity check
    # check if reference and ordering are over the same base set of elements
    assert set(ordering) == set.union(*reference), "Can't compute agreement of orderings of different elements."
    return get_ordering_agreement_inversion_count(reference, ordering)

def get_ordering_agreement_inversion_count(reference, ordering):
    """
    Compute the number of inversion between reference and ordering.
    An inversion is a pair a,b such that a<b (or a>b) according to reference and a>b (resp. a<b) according to ordering.
    Notice that this definition is symmetric and that for every inversion a,b are not ties according to any ranking.
    """
    inversions = 0
    for (score_a_ordering, a) in enumerate(ordering):
        for (score_b_ordering, b) in enumerate(ordering):
            if (a != b):
                # determine scores according to reference
                score_a_reference = -1
                score_b_reference = -1
                for (idx, s) in enumerate(reference):
                    if a in s:
                        score_a_reference = idx
                for (idx, s) in enumerate(reference):
                    if b in s:
                        score_b_reference = idx

                # comp score deltas
                delta_ordering = score_a_ordering - score_b_ordering
                delta_reference = score_a_reference - score_b_reference

                # determine if it is an inversion
                if delta_reference == 0:
                    pass
                elif delta_ordering * delta_reference > 0: # delta_ordering != 0 because a!=b
                    # same sign => no inversion
                    pass
                else:
                    # otherwise => inversion
                    inversions += 1

    return -inversions

def order_rankings_by_agreement(rankings):
    """
    Given a list of rankings, return a list where they are ordered by agreement score. The resulting order can have ties.

    @param rankings List of rankings.
    @return List of lists of input rankings.
    """
    # first aggregate the rankings
    aggregate = aggregate_rankings(rankings)

    # create a dict where the keys are agreement scores and values are sets with of rankings with this score
    score_dict = {}
    for ranking in rankings:
        score = get_ordering_agreement(aggregate, ranking)
        if score in score_dict:
            if not (ranking in score_dict[score]):
                score_dict[score].append(ranking)
        else:
            score_dict[score] = [ranking]

    # return sorted list
    return [ranking_list for (score, ranking_list) in sorted(score_dict.items(), key=lambda x: x[0], reverse=True)]

def get_most_agreeable_rankings(rankings):
    """
    Given a list of rankings, return a list of rankings that have the highest agreement.

    @param rankings List of rankings
    @return Set of rankins that have the highest agreement score to the aggregate ranking.
    """
    return order_rankings_by_agreement(rankings)[0]