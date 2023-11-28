import mephisto.abstractions.blueprints.ranking_task.ranking_utils as ru
import unittest

class TestRankingUtils(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_scores_example(self):
        base = ["A", "B", "C"]
        ordering = ["B", "C", "A"]

        scores = ru.get_scores(base, ordering)
        self.assertEqual(scores, [2, 0, 1])

    def test_aggregate_orderings_avg_score_basic(self):
        orderings = [
            ["A", "B", "C"],
            ["A", "C", "B"],
            ["A", "C", "B"],
        ]

        aggregate = ru.aggregate_rankings_avg_score(orderings)
        self.assertEqual(aggregate, [set(["A"]), set(["C"]), set(["B"])])

    def test_aggregate_orderings_avg_score_tie(self):
        orderings = [
            ["A", "B", "C"],
            ["A", "C", "B"],
        ]

        aggregate = ru.aggregate_rankings_avg_score(orderings)
        self.assertEqual(aggregate, [set(["A"]), set(["C","B"])])

    def test_aggregate_orderings_top_count_basic(self):
        orderings = [
            ["A", "B", "C"],
            ["A", "B", "C"],
            ["B", "C", "A"],
        ]

        aggregate = ru.aggregate_rankings_top_count(orderings)
        self.assertEqual(aggregate, [set(["A"]), set(["B"]), set(["C"])])

    def test_aggregate_orderings_top_count_tie(self):
        orderings = [
            ["A", "B", "C"],
            ["A", "C", "B"],
            ["A", "C", "B"],
        ]

        aggregate = ru.aggregate_rankings_top_count(orderings)
        self.assertEqual(aggregate, [set(["A"]), set(["C","B"])])

    def test_get_ordering_agreement_inversion_count_basic(self):
        reference = [set(["A"]), set(["B"]), set(["C"])]
        ordering = ["A", "C", "B"]

        inversion_count = ru.get_ordering_agreement_inversion_count(reference, ordering)
        self.assertEqual(inversion_count, -2)

    def test_get_ordering_agreement_inversion_count_with_ties(self):
        reference = [set(["A", "B"]), set(["C"])]
        ordering = ["A", "C", "B"]

        inversion_count = ru.get_ordering_agreement_inversion_count(reference, ordering)
        self.assertEqual(inversion_count, -2)

    def test_get_ordering_agreement_inversion_count_with_ties2(self):
        reference = [set(["A"]), set(["B", "C"])]
        ordering = ["A", "C", "B"]

        inversion_count = ru.get_ordering_agreement_inversion_count(reference, ordering)
        self.assertEqual(inversion_count, 0)

    def test_order_rankings_by_agreement_basic(self):
        rankings = [
            ["A", "B", "C"],
            ["A", "C", "B"],
            ["A", "C", "B"],
        ]

        ranking_of_rankings = ru.order_rankings_by_agreement(rankings)
        best = ru.get_most_agreeable_rankings(rankings)

        self.assertEqual(ranking_of_rankings, [[["A", "C", "B"]], [["A", "B", "C"]]])
        self.assertEqual(best, [["A", "C", "B"]])

    def test_order_rankings_by_agreement_tie(self):
        rankings = [
            ["A", "B", "C"],
            ["A", "C", "B"]
        ]

        ranking_of_rankings = ru.order_rankings_by_agreement(rankings)
        # sort all elements of ^ because they are supposed to sets
        ranking_of_rankings = [sorted(e) for e in ranking_of_rankings]

        best = ru.get_most_agreeable_rankings(rankings)

        self.assertEqual(ranking_of_rankings, [sorted([["A", "C", "B"], ["A", "B", "C"]])])
        self.assertEqual(sorted(best), sorted([["A", "C", "B"], ["A", "B", "C"]]))