import unittest
from mongoengine import *
import mephisto.abstractions.blueprints.ranking_task.db as db

DATABBASE_URL = "mongodb://root:better_password@mongo:27017"

class TestAssignmentGeneration(unittest.TestCase):
    def setUp(self):
        connect(host=DATABBASE_URL, db="tmp")
        get_connection().drop_database("tmp")

    def tearDown(self):
        get_connection().drop_database("tmp")
        disconnect()

    def test_basicGenCadAssignment(self):
        #initData = {
        #    "sentence 1": ["s1c1", "s1c2"],
        #    "sentence 2": ["s2c1"],
        #    "sentence 3": []
        #}
        initData = [
            {"original": "sentence 1", "original_id": "id1", "cads": [{"cad": "s1c1", "type": "test"}, {"cad": "s1c2", "type": "test"}]},
            {"original": "sentence 2", "original_id": "id2", "cads": [{"cad": "s2c1", "type": "test"}]},
            {"original": "sentence 3", "original_id": "id3", "cads": []}
        ]
        db.populate_db(initData)
        assignments = db.create_cad_assignments(2)

        # check that only for sentence 2,3 we generated assignments
        self.assertEqual(len(assignments), 2)

        ## check that we request the proper amount of cads
        self.assertEqual(assignments[0]['reqNumCads'], 1)
        self.assertEqual(assignments[1]['reqNumCads'], 2)

        # check that we don't get a second round of cad assignments
        second_assignments = db.create_cad_assignments(2)
        self.assertEqual(len(second_assignments), 0)

    def test_basicRankingAssignment(self):
        #initData = {
        #    "sentence 1": ["s1c1", "s1c2", "s1c3"],
        #    "sentence 2": ["s2c1", "s2c2"],
        #    "sentence 3": ["s3c1"],
        #    "sentence 4": []
        #}
        initData = [
            {"original": "sentence 1", "original_id": "id1",  "cads": [{"cad": "s1c1", "type": "test"}, {"cad": "s1c2", "type": "test"}, {"cad": "s1c3", "type": "test"}]},
            {"original": "sentence 2", "original_id": "id2",  "cads": [{"cad": "s2c1", "type": "test"}, {"cad": "s2c2", "type": "test"}]},
            {"original": "sentence 3", "original_id": "id3",  "cads": [{"cad": "s3c1", "type": "test"}]},
            {"original": "sentence 4", "original_id": "id3", "cads": []}
        ]
        db.populate_db(initData)
        assignments = db.create_ranking_assignments(2, 2)

        # check that min number of elements is satisfied
        self.assertEqual(len(assignments), 2)

        # check number of requested rankings
        for a in assignments:
            # NOTE: right now max_num is not directly set to reqNumRankings
            self.assertEqual(a['reqNumRankings'], 1)

        second_assignments = db.create_ranking_assignments(2,2)

        # check that we got a second round of ranking assignments
        # check that min number of elements is satisfied
        self.assertEqual(len(second_assignments), 2)

        # check number of requested rankings
        for a in second_assignments:
            # NOTE: right now max_num is not directly set to reqNumRankings
            self.assertEqual(a['reqNumRankings'], 1)

        # check that we don't get third assignments
        third_assignments = db.create_ranking_assignments(2,2)
        self.assertEqual(len(third_assignments), 0)

    def test_pipeline_cmpReqCads(self):
        sentences = [
            db.Sentence(sentence="Sentence 1").save(),
            db.Sentence(sentence="Sentence 1").save(),
        ]
        assignments = [
            db.CADAssignment(original=sentences[0], reqNumCads = 1).save(),
            db.CADAssignment(original=sentences[0], reqNumCads = 2).save(),
            db.CADAssignment(original=sentences[1], reqNumCads = 3).save(),
        ]

        pipeline = db.pipeline_cmp_req_cads()
        res = list(db.Sentence.objects().aggregate(pipeline))

        # check that no sentence got removed
        self.assertEqual(len(res), 2)

        # check values
        self.assertEqual(res[0]['totalReqNumCads'], 3)
        self.assertEqual(res[1]['totalReqNumCads'], 3)

    def test_pipeline_cmpl_cads(self):
        sentence = db.Sentence(sentence="original sentence").save()
        cads = [
            db.CAD(cad="cad 1", original=sentence).save(),
            db.CAD(cad="cad 2", original=sentence).save(),
            db.CAD(cad="cad 3", original=sentence).save()
        ]
        units = [
            db.CADUnit(workerId="a", agentId="a", outputCad=cads[0]).save(),
            db.CADUnit(workerId="a", agentId="a", outputCad=cads[0]).save(),
            db.CADUnit(workerId="a", agentId="a", outputCad=cads[1]).save(),
            db.CADUnit(workerId="a", agentId="a", outputCad=cads[2]).save()
        ]
        db.CADAssignment(units=units, original=sentence, reqNumCads=10).save()

        pipeline = db.pipeline_cmp_cmpl_cads()
        res = list(db.Sentence.objects().aggregate(pipeline))

        self.assertEqual(len(res), 1) # only one sentence
        self.assertEqual(res[0]['totalNumComplUnits'], 4)

    def test_pipeline_cmp_duplicates(self):
        sentences = [
            db.Sentence(sentence="sentence 1").save(),
            db.Sentence(sentence="sentence 2").save(),
            db.Sentence(sentence="sentence 3").save()
        ]
        cads = [[
            db.CAD(cad="cad 1", original=sentences[0]).save(),
            db.CAD(cad="cad 2", original=sentences[0]).save(),
            db.CAD(cad="cad 3", original=sentences[0]).save(),
        ],[
            db.CAD(cad="cad 1", original=sentences[1]).save(),
            db.CAD(cad="cad 2", original=sentences[1]).save(),
            db.CAD(cad="cad 3", original=sentences[1]).save(),
        ]]
        units = [[
            db.CADUnit(workerId="a", agentId="a", outputCad=cads[0][0]).save(),
            db.CADUnit(workerId="a", agentId="a", outputCad=cads[0][0]).save(),
            db.CADUnit(workerId="a", agentId="a", outputCad=cads[0][0]).save(),
            db.CADUnit(workerId="a", agentId="a", outputCad=cads[0][1]).save(),
            db.CADUnit(workerId="a", agentId="a", outputCad=cads[0][2]).save(),
            db.CADUnit(workerId="a", agentId="a", outputCad=cads[0][2]).save(),
            ],[
            db.CADUnit(workerId="a", agentId="a", outputCad=cads[1][0]).save(),
            db.CADUnit(workerId="a", agentId="a", outputCad=cads[1][1]).save(),
            db.CADUnit(workerId="a", agentId="a", outputCad=cads[1][2]).save(),
            ]
        ]
        assignments = [
            db.CADAssignment(units=units[0], original=sentences[0], reqNumCads=10).save(),
            db.CADAssignment(units=units[1], original=sentences[1], reqNumCads=10).save(),
        ]

        pipeline = db.pipeline_cmp_duplicates()
        res = list(db.Sentence.objects().aggregate(pipeline))

        self.assertEqual(len(res), 3)
        self.assertEqual(res[0]['totalNumDuplicates'], 3)
        self.assertEqual(res[1]['totalNumDuplicates'], 0)
        self.assertEqual(res[2]['totalNumDuplicates'], 0)

    def test_pipeline_cmp_duplicates_with_preexisting(self):
        sentence = db.Sentence(sentence="sentence 1").save()
        cads = [
            # one preexisting cad
            db.CAD(cad="cad 1", original=sentence).save(),
            # one duplicate submission
            db.CAD(cad="cad 2", original=sentence).save(),
        ]
        units = [
            db.CADUnit(workerId="a", agentId="a", outputCad=cads[1]).save(),
            db.CADUnit(workerId="b", agentId="b", outputCad=cads[1]).save(),
        ]
        assignments = [
            db.CADAssignment(units=units, original=sentence, reqNumCads=2).save(),
        ]
        pipeline = db.pipeline_cmp_duplicates()
        res = list(db.Sentence.objects().aggregate(pipeline))

        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['totalNumDuplicates'], 1)

    def test_pipeline_cmp_total_cads(self):
        sentence = db.Sentence(sentence="sentence").save()
        cad = db.CAD(cad="cad", original=sentence).save(),

        pipeline = db.pipeline_cmp_total_num_cads()
        res = list(db.Sentence.objects().aggregate(pipeline))

        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['totalNumCads'], 1)

    def test_new_assignment_on_duplicate_submission(self):
        """
        Test that when a duplicate cad is submitted, a new cad
        assignment is generated.
        """
        sentence = db.Sentence(sentence="sentence 1").save()
        first_cad = db.CAD(cad="cad", original=sentence).save()
        first_unit = db.CADUnit(workerId="a", agentId="a", outputCad=first_cad).save()
        first_assignment = db.CADAssignment(units=[first_unit], original=sentence, reqNumCads=3).save()

        # check that no new assignments get generated
        second_assignments = db.create_cad_assignments(3)
        self.assertEqual(len(second_assignments), 0)

        # submit duplicate cad
        second_unit = db.CADUnit(workerId="a", agentId="a", outputCad=first_cad).save()
        # submit another normal cad
        second_cad = db.CAD(cad="cad 2", original=sentence).save()
        third_unit = db.CADUnit(workerId="a", agentId="a", outputCad=second_cad).save()
        first_assignment.units += [second_unit, third_unit]
        first_assignment.save()

        third_assignments = db.create_cad_assignments(3)
        self.assertEqual(len(third_assignments), 1)
        self.assertEqual(third_assignments[0]['reqNumCads'], 1)


    def test_new_assignment_on_duplicate_submission_with_preexisting(self):
        """
        Test that when a duplicate cad is submitted, a new cad
        assignment is generated with 2 preexisting cads.
        Encountered this case during testing of whole app.
        """
        sentence = db.Sentence(sentence="sentence 1").save()
        first_cad = db.CAD(cad="cad 1", original=sentence).save()
        second_cad = db.CAD(cad="cad 2", original=sentence).save()
        first_assignment = db.CADAssignment(units=[], original=sentence, reqNumCads=2).save()

        # check that no new assignments get generated
        second_assignments = db.create_cad_assignments(4)
        self.assertEqual(len(second_assignments), 0)

        # submit duplicate cad
        third_cad = db.CAD(cad="cad 3", original=sentence).save()
        second_unit = db.CADUnit(workerId="a", agentId="a", outputCad=third_cad).save()
        third_unit = db.CADUnit(workerId="a", agentId="a", outputCad=third_cad).save()
        first_assignment.units += [second_unit, third_unit]
        first_assignment.save()

        third_assignments = db.create_cad_assignments(4)
        self.assertEqual(len(third_assignments), 1)
        self.assertEqual(third_assignments[0]['reqNumCads'], 1)

    def test_new_assignment_when_submitting_preexisting_cad(self):
        sentence = db.Sentence(sentence="sentence 1").save()
        first_cad = db.CAD(cad="cad 1", original=sentence).save()
        second_cad = db.CAD(cad="cad 2", original=sentence).save()
        first_assignment = db.CADAssignment(units=[], original=sentence, reqNumCads=2).save()

        # check that no new assignments get generated
        second_assignments = db.create_cad_assignments(4)
        self.assertEqual(len(second_assignments), 0)

        # now submit a cad that was in the preexisting set of cads
        first_unit = db.CADUnit(workerId="a", agentId="a", outputCad=first_cad).save()
        first_assignment.units += [first_unit]
        first_assignment.save()

        third_assignments = db.create_cad_assignments(4)
        self.assertEqual(len(third_assignments), 1)
        self.assertEqual(third_assignments[0]['reqNumCads'], 1)

    def test_register_cad_unit(self):
        sentence = db.Sentence(sentence="sentence 1").save()
        assignment = db.CADAssignment(units=[], original=sentence, reqNumCads=1).save()

        db.register_new_unit(assignment.id, "worker_1", "agent_1", "unit_1")
        assignment.reload()

        self.assertEqual(len(assignment.units), 1)
        unit = assignment.units[0]
        # can't exactly verify timestamp so we only check for not null
        self.assertIsNotNone(unit.startTime)
        # end time timestamp is used to determine if unit is already finished; important to check for null here
        self.assertIsNone(unit.endTime)

    def test_register_ranking_unit(self):
        sentence = db.Sentence(sentence="sentence 1").save()
        cad1 = db.CAD(cad="cad1", original=sentence).save()
        cad2 = db.CAD(cad="cad2", original=sentence).save()

        assignment = db.RankingAssignment(units=[], original=sentence, cads = [cad1, cad2], reqNumRankings=1).save()

        db.register_new_unit(assignment.id, "worker_1", "agent_1", "unit_1")
        assignment.reload()

        self.assertEqual(len(assignment.units), 1)
        unit = assignment.units[0]
        # can't exactly verify timestamp so we only check for not null
        self.assertIsNotNone(unit.startTime)
        # end time timestamp is used to determine if unit is already finished; important to check for null here
        self.assertIsNone(unit.endTime)

    def test_register_and_submit_cad_unit(self):
        sentence = db.Sentence(sentence="sentence 1").save()
        assignment = db.CADAssignment(units=[], original=sentence, reqNumCads=1).save()

        db.register_new_unit(assignment.id, "worker_1", "agent_1", "unit_1")
        db.submit_cad("agent_1", "cad_1")

        assignment.reload()
        self.assertEqual(len(assignment.units), 1)
        unit = assignment.units[0]
        self.assertEqual(unit.outputCad.cad, "cad_1")

    def test_register_and_submit_duplicate_cad(self):
        sentence = db.Sentence(sentence="sentence 1").save()
        assignment = db.CADAssignment(units=[], original=sentence, reqNumCads=2).save()

        db.register_new_unit(assignment.id, "worker_1", "agent_1", "unit_1")
        db.register_new_unit(assignment.id, "worker_2", "agent_2", "unit_2")
        db.submit_cad("agent_1", "cad_1")
        db.submit_cad("agent_2", "cad_1")

        assignment.reload()
        self.assertEqual(len(assignment.units), 2)
        output1 = assignment.units[0].outputCad
        output2 = assignment.units[1].outputCad
        self.assertEqual(output1, output2)

    def test_register_and_submit_skip_explanation(self):
        sentence = db.Sentence(sentence="sentence 1").save()
        assignment = db.CADAssignment(units=[], original=sentence, reqNumCads=2).save()

        # search for new assignments
        first_assignment_query = db.create_cad_assignments(2)
        # should be 0 because we manually created assignment
        self.assertEqual(len(first_assignment_query ), 0)

        db.register_new_unit(assignment.id, "worker_1", "agent_1", "unit_1")
        db.register_new_unit(assignment.id, "worker_2", "agent_2", "unit_2")
        db.submit_cad("agent_1", "cad_1")
        db.submit_skip_explanation("agent_2", "explanation_1")

        assignment.reload()
        self.assertEqual(len(assignment.units), 2)

        # test cmpl units pipeline
        cmpl_pipeline = db.pipeline_cmp_cmpl_cads()
        cmpl_res = list(db.Sentence.objects().aggregate(cmpl_pipeline))
        self.assertEqual(len(cmpl_res), 1) # only one sentence
        self.assertEqual(cmpl_res[0]['totalNumComplUnits'], 2)

        # test total num cads pipeline
        total_pipeline = db.pipeline_cmp_total_num_cads()
        total_res = list(db.Sentence.objects().aggregate(total_pipeline))
        # one sentence
        self.assertEqual(len(total_res), 1)
        # two units submitted
        self.assertEqual(total_res[0]['totalNumCads'], 1)

        # now search for assignments again
        second_assignment_query = db.create_cad_assignments(2)
        # should be 1 because we manually created assignment
        self.assertEqual(len(second_assignment_query), 1)
        # only one additional cad because only one worker skipped
        self.assertEqual(second_assignment_query[0]['reqNumCads'], 1)


    def test_register_and_submit_ranking_unit(self):
        sentence = db.Sentence(sentence="sentence 1").save()
        cad1 = db.CAD(cad="cad1", original=sentence).save()
        cad2 = db.CAD(cad="cad2", original=sentence).save()

        assignment = db.RankingAssignment(units=[], original=sentence, cads = [cad1, cad2], reqNumRankings=1).save()

        db.register_new_unit(assignment.id, "worker_1", "agent_1", "unit_1")
        db.submit_permutation("agent_1", [1,0])
        assignment.reload()

        ranking = assignment.units[0].outputRanking
        self.assertEqual(ranking.cads, [cad2, cad1])

    def test_worker_stats_and_history(self):
        # build a more complicated worker history
        sentence1 = db.Sentence(sentence="sentence 1").save()
        cad1 = db.CAD(cad="preexisting cad 1", original=sentence1).save()
        cad2 = db.CAD(cad="preexisting cad 2", original=sentence1).save()
        sentence2 = db.Sentence(sentence="sentence 2").save()

        assignment_dicts = db.create_cad_assignments(3)
        assignment_ids = [a["_id"] for a in assignment_dicts]
        assignment_records = [db.Assignment.objects(id=id).first() for id in assignment_ids]
        self.assertEqual(len(assignment_records), 2)
        self.assertEqual(assignment_records[0].reqNumCads, 1)
        self.assertEqual(assignment_records[1].reqNumCads, 3)

        # worker one submits cads for both sentences
        db.register_new_unit(assignment_ids[0], "worker_1", "agent_1", "unit_1")
        db.submit_cad("agent_1", "cad 1 from worker 1")
        db.register_new_unit(assignment_ids[1], "worker_1", "agent_2", "unit_2")
        db.submit_cad("agent_2", "cad 2 from worker 1")
        # worker two submits another cad
        db.register_new_unit(assignment_ids[1], "worker_2", "agent_3", "unit_3")
        db.submit_cad("agent_3", "cad 1 from worker 2")

        # now query for ranking units
        ranking_assignment_dicts = db.create_ranking_assignments(3, 1)
        # only first sentence has enough cads
        self.assertEqual(len(ranking_assignment_dicts), 1)

        # worker two ranks worker ones cad as best
        db.register_new_unit(ranking_assignment_dicts[0]["_id"], "worker_2", "agent_4", "unit_4")
        # this assumes that the cads in the ranking assignments are sorted by insertion date.
        db.submit_permutation("agent_4", [1, 0, 2])

        self.assertEqual(db.get_num_cads("worker_1"), 2)
        self.assertEqual(db.get_num_completed("worker_1"), 2)
        self.assertEqual(db.get_num_first_place("worker_1"), 1)
        self.assertEqual(db.get_num_incomplete("worker_1"), 0)
        self.assertEqual(db.get_num_rankings("worker_1"), 0)

        self.assertEqual(db.get_num_cads("worker_2"), 1)
        self.assertEqual(db.get_num_completed("worker_2"), 2)
        self.assertEqual(db.get_num_first_place("worker_2"), 0)
        self.assertEqual(db.get_num_incomplete("worker_2"), 0)
        self.assertEqual(db.get_num_rankings("worker_2"), 1)

        self.assertEqual(db.get_num_first_place_unit("unit_1"), 1)
        self.assertEqual(db.get_num_first_place_unit("unit_2"), 0)
        self.assertEqual(db.get_num_first_place_unit("unit_3"), 0)

        # do some sanity checks on history
        history1 = db.get_worker_history("worker_1")
        self.assertEqual(len(history1), 2)
        self.assertEqual(history1[0]["num_first_place"], 1)
        self.assertEqual(history1[1]["num_first_place"], 0)

        history2 = db.get_worker_history("worker_2")
        self.assertEqual(len(history2), 2)
        self.assertEqual(history2[0]["num_first_place"], 0)
        # second unit is ranking unit => no num first place

    def test_num_first_place(self):
        # build a more complicated worker history
        sentence1 = db.Sentence(sentence="sentence 1").save()

        assignment_dicts = db.create_cad_assignments(3)
        assignment_ids = [a["_id"] for a in assignment_dicts]
        assignment_records = [db.Assignment.objects(id=id).first() for id in assignment_ids]
        self.assertEqual(len(assignment_records), 1)
        self.assertEqual(assignment_records[0].reqNumCads, 3)

        # worker one submits all cads
        db.register_new_unit(assignment_ids[0], "worker_1", "agent_1", "unit_1")
        db.register_new_unit(assignment_ids[0], "worker_1", "agent_2", "unit_2")
        db.register_new_unit(assignment_ids[0], "worker_1", "agent_3", "unit_3")
        db.submit_cad("agent_1", "cad 1 from worker 1")
        db.submit_cad("agent_2", "cad 2 from worker 1")
        db.submit_cad("agent_3", "cad 3 from worker 1")

        # now query for ranking units
        ranking_assignment_dicts = db.create_ranking_assignments(3, 1)
        self.assertEqual(len(ranking_assignment_dicts), 1)
        db.register_new_unit(ranking_assignment_dicts[0]["_id"], "worker_1", "agent_4", "unit_4")
        # this assumes that the cads in the ranking assignments are sorted by insertion date.
        db.submit_permutation("agent_4", [1, 0, 2])

        # check db queries
        self.assertEqual(db.get_num_first_place_unit("unit_1"), 0)
        self.assertEqual(db.get_num_first_place_unit("unit_2"), 0)
        self.assertEqual(db.get_num_first_place_unit("unit_3"), 1)
        # should raise exception for ranking unit
        #self.failUnlessRaises(db.get_num_first_place_unit("unit_4"))
        with self.assertRaises(Exception):
            db.get_num_first_place_unit("unit_4")
        self.assertEqual(db.get_num_first_place("worker_1"), 1)

        history = db.get_worker_history("worker_1")

        self.assertEqual(len(history), 4)
        self.assertEqual(history[0]['num_first_place'], 0)
        self.assertEqual(history[1]['num_first_place'], 0)
        self.assertEqual(history[2]['num_first_place'], 1)
        self.assertFalse('num_first_place' in history[3])

