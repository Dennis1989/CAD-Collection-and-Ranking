# Mephisto CAD Collection and Ranking

This project contains a *Counterfactually Augmented Data* (CAD) collection and ranking workflow using the [Mephisto](https://mephisto.ai) framework. The architecture was developed in context of the **Not one bit sexist: a competitive game against sexist language** project, funded by Meta. 

## Debug the Project

We recommend using VSCode. Then you can simply `open in Container`.
Otherwise you can manually:

* go into the `.devcontainer` directory
* start the containers with `sudo docker-compose up -d`
* "install" our blueprint(s) by linking them to the mephisto dir running `ln -s /workspace/blueprints/* /mephisto/mephisto/abstractions/blueprints/`.

To run mephisto execute `python run_task.py`. Run configs are provided for VSCode.

## Deploy the Project


First you need AWS Access Keys to deploy to MTurk or MTurkSandbox.
These can be created on the
[AWS Console](https://us-east-1.console.aws.amazon.com/iamv2/home#/security_credentials):

![AWS Console Screenshot](./docs/aws-console-screenshot.png)

Executing `docker-compose up -d` starts the mephisto and database container.
The mephisto container only idles now. This is because the task start is not
fully automated yet.

* start the containers with `sudo docker-compose up -d`
* attach to a shell inside the mephisto container using `sudo docker exec -it <container name> /bin/bash`
* when running the container for the first time: register provider credentials that you created on the with
  ```mephisto register mturk_sandbox name=... access_key_id=... secret_access_key=...```
* run project with `python run_task.py conf=deploy` (use `conf=deploy_test` to deploy to sandbox).
  You can also override individual config parameters by appending for example:

```
mephisto.task.task_name="..."
or
mephisto.blueprint.db_password="..."
```

* to leave the container without ending the task press `<Ctrl-p> <Ctrl-q>`
* the logs can be found in `outputs/...`

<span style="color:red"> ***! Important !*** </span>
For deployment to work properly the machine has to be reachable under the hostname and port provided in `hydra_configs/conf/deploy.yaml` under `architect`.


## Access MongoDB Database

After starting the compose file the database is accessible using the connection string
`mongodb://root:better_password@127.0.0.1:27017/?replicaSet=replicaset&directConnection=true`.

## Run with Mock Backend

If you just want to work on the frontend and don't need mephisto running, you can use our mock mephisto hook.
You can change the behavior of the backend and inputs for the frontend.

* To build the project with this hook use
  * either `yarn run mock`
  * or `yarn run mock:watch` to rebuild on every file change
* To serve the webapp use `yarn run mock:serve`.

## Configuration

Mephisto uses the [hydra](https://hydra.cc) config framework for configuration.
The config files are in `hydra_configs/conf`. The config files have the following import structure:

![Import Structure](./docs/config-structure.png)

The config files contain comments that describe the parameters. The
documentation for the mephisto parameters can be found at [here](https://mephisto.ai/docs/reference/architects/)
or using the
[mephisto-wut](https://mephisto.ai/docs/guides/tutorials/first_task/#21-discovering-options-with-mephisto-wut) cli.
The parameters for our own blueprint for example can be show by running `mephisto wut blueprint=ranking_task`.

A special parameter is the `onboarding_qualification` parameter. This specifies the name of the configuration used
to **block** workers that do not pass the onboarding.
Note that even after changing this name, workers that got blocked with an old onboarding qualification will still be blocked.
Setting this parameter also has the effect of enabling the onboarding!

Parameters can also be overridden when executing the run script. For example:

```
python static_test_script.py mephisto.architect.port=1234
```

Will launch the server on port 1234 instead of the one specified in the config.


### Task Names

The task_name config parameter is not the most intuitive to use.
The mephisto developers recommend some
[best practices](https://mephisto.ai/docs/guides/tutorials/workflows/#proper-use-of-task_name)
for setting the task_name.
What is important when deploying to MTurk is to know that MTurk groups HITs. To ensure that when every time you execute the run script the HITs end up in a new group it is advisable to change the task name on every run.

## Reviewing Tasks

To review tasks you can use:

```
python ./examine_results.py
```

## Wiping Mephisto Data

In general you probably should not do this but from experience Mephisto sometimes gets stuck in a weird state configuration and the easiest way to resolve that
is to just wipe its database.

You can wipe the database by deleting the contents in `./data` and the logs by deleting the contents in `./outputs`. However don't delete the folders itself
as they have to exist to be mountable by the docker-compose. To wipe everything you could for example use:

```
rm -r ./outputs/* ./data/*
```