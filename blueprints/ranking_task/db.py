from mongoengine import *
from mongoengine.connection import _get_db
from mephisto.abstractions.blueprints.ranking_task.game_stage import GameStage
import datetime

from mephisto.utils.logger_core import (
    get_logger,
)
logger = get_logger(name=__name__)


### Task Data ###
class Sentence(Document):
    sentence = StringField()
    externalId = StringField()
    meta = { 'collection': 'sentence' }

class CAD(Document):
    cad      = StringField()
    original = ReferenceField(Sentence)
    type = StringField()
    meta = { 'collection': 'cad', 'indexes': ['original']}

class Ranking(Document):
    cads = ListField(ReferenceField(CAD))

class SkipExplanation(Document):
    explanation = StringField()
    original = ReferenceField(Sentence)

class Worker(Document):
    workerId             = StringField(required = True)
    gender               = StringField(required = True)
    age                  = StringField(required = True)
    occupation           = StringField(required = True)
    education            = StringField(required = True)
    birthCountry         = StringField(required = True)
    youthCountry         = StringField(required = True)
    currentCountry       = StringField(required = True)
    ethnicity            = StringField(required = True)
    religion             = StringField(required = True)
    politicalAffiliation = StringField(required = True)
    englishFluency       = StringField(required = True)
    sexismFaced          = StringField(required = True)

### Units ###
class Unit(Document):
    startTime = DateTimeField()
    endTime   = DateTimeField()
    workerId = StringField(required=True)
    agentId  = StringField(required=True)
    unitId = StringField()
    paidBonus = BooleanField()
    meta = {'collection': 'unit', 'allow_inheritance': True, 'indexes': ['agentId']}

class RankingUnit(Unit):
    outputRanking = ReferenceField(Ranking)

class CADUnit(Unit):
    outputCad = ReferenceField(CAD)
    outputExplanation = ReferenceField(SkipExplanation)

### Assignments ###
class Assignment(Document):
    units = ListField(ReferenceField(Unit))
    meta = {'collection': 'assignment', 'allow_inheritance': True}

class RankingAssignment(Assignment):
    original = ReferenceField(Sentence, required = True) # not strictly necessary, but makes querying easier.
    cads = ListField(ReferenceField(CAD), required = True)
    # this is the requested number of rankings. note that this differs from
    # the length of units. When workers have not started the unit list is
    # still empty, and if some abort this might get larger tahn req_num_rankings
    reqNumRankings = IntField(required=True)
    meta = {'indexes': ['original']}

class CADAssignment(Assignment):
    original = ReferenceField(Sentence, required = True)
    reqNumCads = IntField(required=True)
    meta = {'indexes': ['original']}

### Feedback ###
class Feedback(Document):
    workerId = StringField()
    unit = ReferenceField(Unit)
    feedback = StringField()

# unused
class GameAssignment(Assignment):
    gameStage = EnumField(GameStage)
    original  = ReferenceField(Sentence, required = True)
    cads      = ListField(ReferenceField(CAD))

def create_ranking_assignments(min_cads, max_units):
    '''
    Query the database for sentences whose cads don't have rankings yet.
    Then group these cads and filter out groups that are smaller than min_cads.
    Then create RankingAssignment entries and return these.
    '''
    # this is run on: Sentences
    pipeline = [
        # first filter out originals that already have units
        {
            "$lookup": {
                "from": Assignment._get_collection().name,
                "pipeline": [
                    {"$match": {"_cls": RankingAssignment._class_name}}, # join only with ranking assignments
                    {"$project": {"_id": True, 'reqNumRankings': True}}], # keep id and reqNumRankings
                "localField": "_id",
                "foreignField": "original",
                "as": "assignments"
            }
        },
        {"$addFields": {"totalReqNumRankings": {"$sum": "$assignments.reqNumRankings"}}},
        {"$unset": "assignments"},
        {"$match": {"totalReqNumRankings": {"$lt": max_units}}}, # check if we should request new rankings
        # remove added fields
        {"$unset": "totalReqNumRankings"},

        # now filter out originals with to few cads
        {
            "$lookup": {
                "from": CAD._get_collection().name,
                "localField": "_id",
                "foreignField": "original",
                "as": "cads"
            }
        },
        {"$match": { "$expr" :{"$gte": [{"$size": "$cads"}, min_cads]}}}, # check if there exist enough cads for the original
        {"$project":
            {
                "_id": False,
                "cads": {
                    "$map": {
                        "input": "$cads",
                        "in": "$$this._id",
                    }
                },
                "original": "$_id",
            }
        },
        { "$set": {"_cls": RankingAssignment._class_name}}, # manually set class information for ORM
        { "$addFields": {"reqNumRankings": 1}} # hard code num rankings for now TODO: change
    ]

    mongo = get_connection()
    new_assignments = None
    with mongo.start_session() as session:
        with session.start_transaction():
            try:
                sentence_collection = Sentence._get_collection()
                assignment_collection = Assignment._get_collection()

                new_assignments = list(sentence_collection.aggregate(pipeline, session=session))

                if new_assignments:
                    assignment_collection.insert_many(new_assignments, session=session)

            except Exception as e:
                session.abort_transaction()
                raise e

    return new_assignments

"""
This pipeline should be run on the SENTENCE collection
and adds a field 'totalReqNumCads' to every sentence
that is the sum of all 'reqNumCads' fields of Assignments that
for this sentence.
"""
def pipeline_cmp_req_cads():
    return [
        # Step 1: compute the number of requested cads
        # join sentence with all assignments that reference it
        # this adds a list 'assignments' that contains the a list of all assignments
        {"$lookup": {
            "from": Assignment._get_collection().name,
            "pipeline": [
                {"$match": {"_cls": CADAssignment._class_name}}, # join only with cad assignments
                {"$project": {"_id": True, 'reqNumCads': True}}], # keep id and req_num_cads
            "localField": "_id",
            "foreignField": "original",
            "as": "assignments"
        }},
        # now we sum up the requested numbers
        {"$addFields": {"totalReqNumCads": {"$sum": "$assignments.reqNumCads"}}},
        # and remove the intermediary assignment field
        {"$unset": "assignments"},
    ]

"""
This pipeline should be run on the SENTENCE collection
and adds a field 'totalNumComplUnits' to every sentence
that holds the number of completed cad units that
have this sentence as original.
"""
def pipeline_cmp_cmpl_cads():
    return [
        # Step 2: compute the number of completed CAD units
        # lookup CADAssignments lookup CADUnits lookup CAD
        # this adds a field 'totalNumComplUnits' that contains a list with all cad-units we already completed by assignment
        {"$lookup": {
            "from": Assignment._get_collection().name,
            "pipeline": [
                {"$match": {"_cls": CADAssignment._class_name}},
                {"$unwind": "$units"},
                {"$lookup":{
                    "from": Unit._get_collection().name,
                    # we need an inner lookup to join the Units with their result objects
                    "pipeline": [
                        {"$match": {"_cls": CADUnit._class_name}},
                        # lookup cad results
                        {"$lookup": {
                            "from": CAD._get_collection().name,
                            "localField":"outputCad",
                            "foreignField": "_id",
                            "as": "result_cads"
                        }},
                        # lookup explanation results
                        {"$lookup": {
                            "from": SkipExplanation._get_collection().name,
                            "localField":"outputExplanation",
                            "foreignField": "_id",
                            "as": "result_explanations"
                        }},
                        {"$match": {"$expr": {"$or": [{"$gt": [{"$size": "$result_cads"}, 0]}, {"$gt": [{"$size": "$result_explanations"}, 0]}]}}}], # only take units that have at least one cad

                    "localField": "units",
                    "foreignField": "_id",
                    "as": "unit"
                }},
                {"$match": {"$expr": {"$gt": [{"$size": "$unit"}, 0]}}} # only take assignments that have at least one unit
            ],
            "localField": "_id",
            "foreignField": "original",
            "as": "units"
        }},
        # we are just interrested in the size of this array
        {"$addFields": {"totalNumComplUnits": {"$size": "$units"}}},
        # and remove intermediary field
        {"$unset": "units"}
    ]

"""
This pipeline should be run on the SENTENCE collection
and adds a field 'totalNumDuplicates' to every sentence
that holds the number of units that point to a cad
for this sentence that already has an associated unit.

For example in this case:

┌─────────────────┐
│original sentence│
└───────▲─────────┘
        │
┌───────┴────────┐
│a counterexample│
└────▲─────────▲─┘
     │         │
┌────┴───┐ ┌───┴───────┐
│one unit│ │second unit│
└────────┘ └───────────┘

the totalNumDuplicates would be 1
"""
def pipeline_cmp_duplicates():
    return [
        # Step 3: compute the number of duplicate cads
        {"$lookup": {
            "from": CAD._get_collection().name,
            "pipeline": [
                {"$lookup": {
                    "from": Unit._get_collection().name,
                    "pipeline": [{"$match": {"_cls": CADUnit._class_name}}], # match only with cad units
                    "localField": "_id",
                    "foreignField": "outputCad",
                    "as": "author_units"
                }},
                {"$addFields": {"num_additional_submits": {"$subtract": [{"$size": "$author_units"}, 1]}}},
                {"$match": {"$expr": {"$gt": ["$num_additional_submits", 0]}}} # only duplicates
            ],
            "localField": "_id",
            "foreignField": "original",
            "as": "duplicate_cads"
        }},
        {"$addFields": {"totalNumDuplicates": {"$sum": "$duplicate_cads.num_additional_submits"}}},
        {"$unset": "duplicate_cads"},
    ]

"""
This pipeline should be run on the SENTENCE collection
and adds a field 'totalNumCads' to every sentence
that holds the number of ALL cads for this sentence.
"""
def pipeline_cmp_total_num_cads():
    return [
    # Step 4: compute the total number of CADs that we have for the sentence.
    # join sentence with all cads that reference it
    # this adds a list 'cads' that contain all cad objects for this sentence
    {"$lookup": {
        "from": CAD._get_collection().name,
        "localField": "_id",
        "foreignField": "original",
        "as": "cads"
    }},
    # same as before
    {"$addFields": {"totalNumCads": {"$size": "$cads"}}},
    {"$unset": "cads"}
]


def create_cad_assignments(max_cads):
    '''
    Query the database for sentences that don't have enough (`max_cads`) cads yet.
    Create new CADAssignment entries with according reqNumCads and return them.
    '''
    # this is run on sentences collection
    pipeline = pipeline_cmp_req_cads() + pipeline_cmp_cmpl_cads() + pipeline_cmp_total_num_cads() + [
        # add a field that contains a number of how many cads we still want to generate
        # this is calculated as: max_cads - (totalReqNumCads + (totalNumCads - totalNumComplUnits)))
        #                                     ---------------   ----------------------------------
        #                                   already requested      number of preexisting cads
        {"$addFields" : {
            "numMissingCads": {"$subtract": [max_cads, {"$add": ["$totalReqNumCads", {"$subtract": ["$totalNumCads", "$totalNumComplUnits"]}]}]}
        }},
        # now remove aux fields
        {"$unset": "totalReqNumCads"},
        {"$unset": "totalNumCads"},
        {"$unset": "totalNumComplUnits"},

        # now we filter all cads that still need assignments
        {"$match": {"numMissingCads": {"$gt":  0}}},

        # finally we prepare the new documents
        # rename _id -> original
        {"$set": {"original": "$_id"}},
        {"$unset": "_id"},
        # rename numMissingCads -> reqNumCads
        {"$set": {"reqNumCads": "$numMissingCads"}},
        {"$unset": "numMissingCads"},

        # remove sentence val
        {"$unset": "sentence"},
        # remove external id
        {"$unset": "externalId"},
        # manually set class information for ORM
        { "$set": {"_cls": CADAssignment._class_name}}
    ]

    mongo = get_connection()
    new_assignments = None
    with mongo.start_session() as session:
        with session.start_transaction():
            try:
                sentence_collection = Sentence._get_collection()
                assignment_collection = Assignment._get_collection()

                new_assignments = list(sentence_collection.aggregate(pipeline, session=session))

                if new_assignments:
                    assignment_collection.insert_many(new_assignments, session=session)


            except Exception as e:
                session.abort_transaction()
                raise e

    return new_assignments

def populate_db(sentences_list, num_sentences=-1, num_cads=-1):
    """
    Read sentences from the dict and populate the database with them.
    Dict should have sentences as keys and all corresponding counterfactuals as values.
    :param num_sentences Maximum number of sentences to read. Read all sentences if this is <0
    """
    sentences_added = 0
    for current_entry in sentences_list:
        if num_sentences - sentences_added == 0:
            # added max number of sentences => break
            # compare for equality so that this never gets triggered for num_sentences<0
            break
        else:
            # add sentence
            sentence_ref = Sentence(sentence=current_entry["original"], externalId=current_entry['original_id']).save()
            cads_added = 0
            for cad_item in current_entry['cads']:
                if num_cads - cads_added == 0:
                    # added max number of cads => break
                    # compare for equality so that this never gets triggered for num_sentences<0
                    break
                CAD(cad=cad_item['cad'], original=sentence_ref, type=cad_item['type']).save()
                cads_added += 1
            sentences_added += 1

def clear_db():
    """
    Drop all collections in the database.
    """
    mongo = get_connection()
    mongo.drop_database('test')

def get_num_cads(worker_id):
    """
    Get the number of cads a given worker has submitted.
    """
    return CADUnit.objects(workerId=worker_id, outputCad__ne=None).count()

def get_num_first_place(worker_id):
    """
    Get the number of times a cad from a given worker has been ranked as the least sexist.
    """
    # get workers cads
    cmpl_cad_units = CADUnit.objects(workerId=worker_id, outputCad__ne=None)
    # count how many rankings have the first cad in cad_ids
    return sum([get_num_first_place_unit(u.unitId) for u in cmpl_cad_units])

def get_num_first_place_unit(unit_id):
    """
    Get the number of times a cad from a given unit has been ranked as the least sexist.

    @param unit_id: This is the *MEPHISTO* unit id!
    """
    # get unit record
    unit = CADUnit.objects(unitId=str(unit_id)).first()

    assert unit != None, "Called with invalid unit_id"

    cad_id = unit.outputCad
    related_rankings = Ranking.objects(cads__contains=cad_id)
    first_place_count = 0
    for r in related_rankings:
        if cad_id == r.cads[-1]:
            first_place_count += 1
    return first_place_count

def get_num_rankings(worker_id):
    """
    Get the number of rankings a given worker has submitted.
    """
    return RankingUnit.objects(workerId=worker_id, outputRanking__ne=None).count()

def get_num_served(worker_id):
    """
    Get the number of units served to a worker.
    """
    return Unit.objects(workerId=worker_id).count()

def get_num_completed(worker_id):
    """
    Get the number of units completed by a worker.
    """
    return Unit.objects(workerId=worker_id, endTime__ne=None).count() - CADUnit.objects(workerId=worker_id, outputExplanation__exists=True).count()

def get_num_incomplete(worker_id):
    """
    For a given worker, get the number of served but not completed units.
    """
    return Unit.objects(workerId=worker_id, endTime=None).count()

def get_total_time(worker_id):
    """
    For a given worker get the total worked time.
    """
    completed_units = Unit.objects(workerId=worker_id, endTime__ne=None)
    return sum([u.endTime - u.startTime for u in completed_units], datetime.timedelta())

def get_worker_history(worker_id):
    # only completed units for now
    units = Unit.objects(workerId=worker_id, endTime__ne=None).order_by('endTime')

    def serialize_unit(unit):
        end_time = unit.endTime.strftime('%a %d %b %Y, %I:%M%p')
        if isinstance(unit, CADUnit):
            # count how often this cad was ranked first
            num_first_place = get_num_first_place_unit(unit.unitId)
            return {
                "finished_time": end_time,
                "stage": GameStage.CAD,
                "num_first_place": num_first_place,
                "original": unit.outputCad.original.sentence,
                "cad": unit.outputCad.cad
            }
        elif isinstance(unit, RankingUnit):
            return {
                "finished_time": end_time,
                "stage": GameStage.RANKING,
                "output_ranking": [entry.cad for entry in unit.outputRanking.cads]
            }
        else:
            raise "Dashboard not implemented for other units"

    # ignore skipped units for now
    units = [u for u in units if (not hasattr(u, 'outputExplanation') or u.outputExplanation == None)]

    return [serialize_unit(u) for u in units]

def all_requested_cads_generated():
    """
    This method checks if all cads that have been requested are generated.
    This is usefull to check if the generator can stop.
    """
    for assignment in CADAssignment.objects():
        completed_units = list(filter(lambda u : u.endTime != None, assignment.units))
        if len(completed_units) < assignment.reqNumCads:
            return False
    return True

def register_new_unit(assignment_id, worker_id, agent_id, unit_id):
    """
    Creates a new unit in the MongoDB for the given assignment.
    Unit type is inferred from assignment. Unit is added to the assignments
    unit list and the initial timestamp is set.
    """
    # get the assignment record in our db
    assignment_record = Assignment.objects(id=assignment_id).first()
    start_time = datetime.datetime.utcnow

    unit_record = None
    if isinstance(assignment_record, RankingAssignment):
        unit_record = RankingUnit(workerId=str(worker_id), agentId=str(agent_id), startTime=start_time, unitId=str(unit_id), paidBonus=False)
    elif isinstance(assignment_record, CADAssignment):
        unit_record = CADUnit(workerId=str(worker_id), agentId=str(agent_id), startTime=start_time, unitId=str(unit_id), paidBonus=False)
    else:
        raise "Unknown assignment type!"
    unit_record.save()
    # add new unit record to assignment
    assignment_record.units += [unit_record]
    assignment_record.save()

def submit_cad(agent_id, cad):
    """
    Creates a new cad object if submitted cad is not yet in DB, sets metadata,
    and registers cad output with unit.
    Does check for duplicates and creates references accordingly.
    Does not check if this operation 'makes sense', i.e.
    if this agent already has a submission.
    """
    # get records
    unit_record = CADUnit.objects(agentId=agent_id).first()
    assignment_record = CADAssignment.objects(units__contains=unit_record).first()
    original = assignment_record.original

    # save metadata
    unit_record.endTime = datetime.datetime.utcnow

    # check if cad was submitted by someone else
    other_submitted_cads = CAD.objects(original=original)

    # function to compare two cads for (semi)-equality
    def check_equal(a, b):
        return a.lower() == b.lower()

    is_duplicate = False
    duplicate_cad_record = None
    for o in other_submitted_cads:
        if check_equal(cad, o.cad):
            is_duplicate = True
            duplicate_cad_record = o
            break

    if is_duplicate:
        logger.info("Got duplicate cad submission!")
        # set a reference to the first submission of this cad
        unit_record.outputCad = duplicate_cad_record
    else:
        # create new cad unit
        cad_record = CAD(original=original, cad=cad, type="manual_mephisto").save()
        unit_record.outputCad = cad_record

    unit_record.save()

def submit_skip_explanation(agent_id, explanation):
    """
    Creates a new skip explanation object, sets metadata,
    and registers cad output with unit.
    Does check for duplicates and creates references accordingly.
    Does not check if this operation 'makes sense', i.e.
    if this agent already has a submission.
    """
    # get records
    unit_record = CADUnit.objects(agentId=agent_id).first()
    assignment_record = CADAssignment.objects(units__contains=unit_record).first()
    original = assignment_record.original

    # save metadata
    unit_record.endTime = datetime.datetime.utcnow

    # create new explanation record
    explanation_record = SkipExplanation(original=original, explanation=explanation).save()
    unit_record.outputExplanation = explanation_record

    unit_record.save()

def submit_permutation(agent_id, permutation):
    """
    Creates a new ranking object for the given permutation.
    Sets metadata of unit and links output ranking.
    Does check if permutation is valid and converts it to list of references.
    Does not parse string encoded permutations or checks if agent already
    has submission.
    """
    # get records
    unit_record = RankingUnit.objects(agentId=agent_id).first()
    assignment_record = RankingAssignment.objects(units__contains=unit_record).first()

    # save metadata
    unit_record.endTime = datetime.datetime.utcnow

    # verify permutation
    num_of_cads = len(assignment_record.cads)
    if len(permutation) != num_of_cads:
        logger.error("Received permutation with more elements than original number of cads!")
    for i in range(num_of_cads):
        if not i in permutation:
            logger.error(f"Received permutation that does not contain {i}!")

    permutated_cads = [assignment_record.cads[i] for i in permutation]
    ranking_record = Ranking(cads = permutated_cads).save()
    unit_record.outputRanking = ranking_record

    unit_record.save()

def submit_worker_demographics(worker_id, demographics):
    Worker(
        workerId             = worker_id,
        gender               = demographics['gender'],
        age                  = demographics['age'],
        occupation           = demographics['occupation'],
        education            = demographics['education'],
        birthCountry         = demographics['birthCountry'],
        youthCountry         = demographics['youthCountry'],
        currentCountry       = demographics['currentCountry'],
        ethnicity            = demographics['ethnicity'],
        religion             = demographics['religion'],
        politicalAffiliation = demographics['politicalAffiliation'],
        englishFluency       = demographics['englishFluency'],
        sexismFaced          = demographics['sexismFaced'],
    ).save()
    logger.info(f"Submitted demographics for worker {worker_id}!")

def submit_feedback(worker_id, unit, feedback):
    Feedback(
        workerId = worker_id,
        unit = unit,
        feedback = feedback,
    ).save()
    logger.info(f"Submitted feedback from worker {worker_id}!")

def ranking_done(original_id):
    """
    Given an id returns if all requested rankings for the cads relating to the given original have been submitted.

    @param original_id Mongo DB id of the original sentence.
    """
    ranking_assignments = RankingAssignment.objects(original=original_id)
    for assignment in ranking_assignments:
        completed_units = [u for u in assignment.units if u.outputRanking != None]
        if len(completed_units) < assignment.reqNumRankings:
            return False
    return True
