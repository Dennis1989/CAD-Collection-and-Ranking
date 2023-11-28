from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.examine_utils import run_examine_or_review, print_results
from mephisto.data_model.worker import Worker
from mephisto.data_model.unit import Unit
from mephisto.tools.data_browser import DataBrowser
import mephisto.abstractions.blueprints.ranking_task.db as mongoDB
from mongoengine import *

db = None

BONUS_PER_FIRST_PLACE = 0.10

def main():
    # setup mongo db
    DATABBASE_URL = "mongodb://root:better_password@mongo:27017"
    connect(host=DATABBASE_URL)

    # setup mephisto db
    global db
    db = LocalMephistoDB()
    data_browser = DataBrowser(db=db)

    task_name = input("Input task name: ")

    tasks = db.find_tasks(task_name=task_name)
    assert len(tasks) >= 1, f"No task found under name {task_name}"

    units = data_browser.get_units_for_task_name(task_name)

    accepted_units = [u for u in units if u.get_status() == "accepted"]

    # look into mongo DB to determine all units that did not get a bonus yet
    unbonused_units = list(filter(lambda u: mongoDB.Unit.objects(unitId=u.db_id).first().paidBonus != True, accepted_units))

    # dict where keys are worker_ids and values is bonus
    bonuses = {}

    for u in unbonused_units:
        count = mongoDB.get_num_first_place_unit(u.db_id)
        worker_id = u.worker_id
        total_bonus = count * BONUS_PER_FIRST_PLACE

        if worker_id in bonuses:
            bonuses[worker_id] += total_bonus
        else:
            bonuses[worker_id] = total_bonus

    # check if there are any bonuses to be paid
    if sum(bonuses.values()) == 0:
        print("Found no bonuses to be paid!")
        print(f"Found in total:")
        print(f"\tunits: {len(units)}")
        print(f"\taccepted units: {len(accepted_units)}")
        print(f"\tUnits that have not been bonused yet: {len(unbonused_units)} (this includes ranking units which currently don't get a bonus)")
        return

    # print a confirmation screen
    print()
    print(f"Found {len(accepted_units)} accepted unit out of a total of {len(units)} units.")
    print("Computed the following bonuses:")

    print("Worker\t\t\t| Bonus")
    print("--------------------------------")
    for worker in bonuses:
        print(f"{worker}\t\t\t| {bonuses[worker]}$")
    print("--------------------------------")
    print(f"TOTAL:\t\t\t| {sum(bonuses.values())}$")
    print()

    # prompt to confirm
    options = ['a', 'p']
    print("Attention! Pressing 'p' costs money!")
    choice = input("Does this look ok? (a)bort / (p)ay: ")
    while not (choice in options):
        choice = input("Please press either 'p' to pay or 'a' to abort: ")

    if choice == 'a':
        print("Aborting!")
        return

    # go through units again
    for u in unbonused_units:
        count = mongoDB.get_num_first_place_unit(u.db_id)
        worker = u.get_assigned_agent().get_worker()
        total_bonus = count * BONUS_PER_FIRST_PLACE
        if total_bonus > 0:
            unit_record = mongoDB.Unit.objects(unitId=u.db_id).first()

            bonus_message = "\n".join([
                "Thanks for participating in the NotOneBitSexist project!",
                "",
                f'Your sentence: "{unit_record.outputCad.cad}"',
                f"was ranked the least sexist by {count} other people!",
                "Keep up the good work!",
                "",
            ])

            worker.bonus_worker(total_bonus, bonus_message, u)

            print(f"Awarded worker {worker.db_id} with {total_bonus}$ for unit {u.db_id} which got ranked first {count} times.")
            unit_record.paidBonus = True
            unit_record.save()

if __name__ == "__main__":
    main()
