Title: First Experiment with TaskCluster
Date: 2016-02-09
Modified: 2016-02-16
Tags: mozilla, foss, ci, taskcluster
Slug: taskcluster-learning
Author: Maja Frydrychowicz
Summary: Adding a new task to TaskCluster continuous integration system.

[^1]: This is accomplished in part thanks to [mozilla-taskcluster](http://blog.gregarndt.com/taskcluster/2015/08/05/demystifying-in-tree-scheduling/), a service that links Mozilla's hg repo to TaskCluster and creates each decision task. More at [TaskCluster at Mozilla](http://docs.taskcluster.net/introduction/getting-started/#taskcluster-at-mozilla)
[^2]: Run tasks on any platform thanks to [generic worker](http://docs.taskcluster.net/workers/generic-worker/)
[^3]: To look at a `graph.json` artifact, go to [Treeherder](http://treeherder.mozilla.org/), click a green 'D' job, then Job details > Inspect Task, where you should find a list of artifacts.
[^4]: It's not _really_ true that build tasks don't depend on anything. Any task that uses a task-image depends on the task that creates the image. I'm sorry for saying 'task' five times in every sentence, by the way.
[^5]: ...as opposed to a [generic worker](http://docs.taskcluster.net/workers/generic-worker/).
[^6]: `{{#task_id_for_image}}` is an example of a predefined variable that we can use in our TC yaml files. Where do they come from? How do they get populated? I don't know.


[TaskCluster](http://docs.taskcluster.net/) is a new-ish continuous integration system made at Mozilla. It manages the scheduling and execution of tasks based on a graph of their dependencies. It's a general CI tool, and could be used for any kind of job, not just Mozilla things. 

However, the example I describe here refers to a Mozilla-centric use case of TaskCluster[^1]: tasks are run per check-in on the branches of Mozilla's Mercurial repository and then results are posted to [Treeherder](https://github.com/mozilla/treeherder). For now, the tasks can be configured to run in Docker images (Linux), but other platforms are in the works[^2]. 

So, I want to schedule a task! I need to add a new task to the task graph that's created for each revision submitted to hg.mozilla.org. (This is part of my work on deploying a suite of [tests for the Marionette Python test runner](https://bugzilla.mozilla.org/show_bug.cgi?id=1227367), i.e. testing the test harness itself.) 

The rest of this post describes what I learned while making [this work-in-progress](https://hg.mozilla.org/try/rev/6b7479c4aa30).

# There are builds and there are tests

mozilla-taskcluster operates based on the info under [`testing/taskcluster/tasks`](https://dxr.mozilla.org/mozilla-central/source/testing/taskcluster/tasks) in Mozilla's source tree, where there are yaml files that describe tasks. Specific tasks can inherit common configuration options from base yaml files. 

The yaml files are organized into two main categories of tasks: builds and tests. This is just a convention in mozilla-taskcluster about how to group task configurations; TC itself doesn't actually know or care whether a task is a build or a test.

The task I'm creating doesn't quite fit into either category: it runs harness tests that just exercise the Python runner code in [marionette_client](http://marionette-client.readthedocs.org), so I only need a source checkout, not a Firefox build. I'd like these tests to run quickly without having to wait around for a build. Another example of such a task is the recently-created [ESLint task](https://hg.mozilla.org/mozilla-central/rev/4b34c9d1a31a).

# Scheduling a task

Just adding a yaml file that describes your new task under `testing/taskcluster/tasks` isn't enough to get it scheduled: you must also add it to the list of tasks in [`base_jobs.yml`](https://dxr.mozilla.org/mozilla-central/source/testing/taskcluster/tasks/branches/base_jobs.yml), and define an identifier for your task in [`base_job_flags.yml`](https://dxr.mozilla.org/mozilla-central/source/testing/taskcluster/tasks/branches/base_job_flags.yml). This identifier is used in `base_jobs.yml`, and also by people who want to run your task when pushing to [try](https://wiki.mozilla.org/ReleaseEngineering/TryServer).

How does scheduling work? First a [decision task](http://docs.taskcluster.net/introduction/getting-started/#decision-tasks-and-task-graphs) generates a _task graph_, which describes all the tasks and their relationships. More precisely, it looks at `base_jobs.yml` and other yaml files in `testing/taskcluster/tasks` and spits out a json artifact, `graph.json`[^3]. Then, `graph.json` gets sent to TC's [`createTask`](http://docs.taskcluster.net/queue/api-docs/#createTask) endpoint, which takes care of the actual scheduling.  

In the excerpt below, you can see a task definition with a `requires` field and you can recognize a lot of fields that are in common with the 'task' section of the yaml files under `testing/taskcluster/tasks/`.

    :::javascript
    {
    "tasks": [
        {
          "requires": [
            // id of a build task that this task depends on
            "fZ42HVdDQ-KFFycr9PxptA"  
          ], 
          "task": {
            "taskId": "c2VD_eCgQyeUDVOjsmQZSg"
            "extra": {
              "treeherder": {
                  "groupName": "Reftest", 
                  "groupSymbol": "tc-R", 
              }, 
            }, 
            "metadata": {
              "description": "Reftest test run 1", 
              "name": "[TC] Reftest", 
            //...
      ]
    }

For now at least, a major assumption in the task-graph creation process seems to be that _test_ tasks can depend on _build_ tasks and _build_ tasks don't really[^4] depend on anything. So:

* If you want your tasks to run for every push to a Mozilla hg branch, add it to the list of __builds__ in `base_jobs.yml`. 
* If you want your task to run after certain build tasks succeed, add it to the list of __tests__ in `base_jobs.yml` and specify which build tasks it depends on.
* Other than the above, I don't see any way to specify a dependency between task A and task B in `testing/taskcluster/tasks`.

So, I added `marionette-harness` under `builds`. Recall, my task isn't a build task, but it doesn't depend on a build, so it's not a test, so I'll treat it like a build.

    :::yaml
    # in base_job_flags.yml
    builds:
      # ...
      - marionette-harness

    # in base_jobs.yml
    builds:
      # ...
      marionette-harness:
        platforms:
          - Linux64
        types:
          opt:
            task: tasks/tests/harness_marionette.yml

This will allow me to trigger my task with the following try syntax: `try: -b o -p marionette-harness`. Cool.

# Make your task do stuff
Now I have to add some stuff to `tasks/tests/harness_marionette.yml`. Many of my choices here are based on the work done for the [ESLint task](https://hg.mozilla.org/mozilla-central/rev/4b34c9d1a31a). I created a base task called `harness_test.yml` by mostly copying bits and pieces from the basic build task, `build.yml` and making a few small changes. The actual task, `harness_marionette.yml` inherits from `harness_test.yml` and defines specifics like Treeherder symbols and the command to run.

## The command
The heart of the task is in `task.payload.command`. You could chain a bunch of shell commands together directly in this field of the yaml file, but it's better not to. Instead, it's common to call a TaskCluster-friendly shell script that's available in your task's environment. For example, the [`desktop-test`](https://dxr.mozilla.org/mozilla-central/source/testing/docker/desktop-test) docker image has a script called `test.sh` through which you can call the [mozharness](https://wiki.mozilla.org/ReleaseEngineering/Mozharness) script for your tests. There's a similar `build.sh` script on `desktop-build`. Both of these scripts depend on environment variables set elsewhere in your task definition, or in the Docker image used by your task. The environment might also provide utilities like [tc-vcs](http://tc-vcs.readthedocs.org/en/latest/), which is used for checking out source code.

    :::yaml
    # in harness_marionette.yml
    payload:
      command:
        + bash
        + -cx
        + >
            tc-vcs checkout ./gecko {{base_repository}} {{head_repository}} {{head_rev}} {{head_ref}} &&
            cd gecko &&
            ./mach marionette-harness-test

My task's `payload.command` should be moved into a custom shell script, but for now it just chains together the source checkout and a call to [mach](https://developer.mozilla.org/en-US/docs/Mozilla/Developer_guide/mach). It's not terrible of me to use mach in this case because I expect my task to work in a build environment, but most tests would likely call mozharness.

# Configuring the task's environment

Where should the task run? What resources should it have access to? This was probably the hardest piece for me to figure out.

## docker-worker

My task will run in a docker image using a [docker-worker](http://docs.taskcluster.net/workers/docker-worker/)[^5]. The image, called `desktop-build`, is defined in-tree under [`testing/docker`](https://dxr.mozilla.org/mozilla-central/source/testing/docker/desktop-build). There are many other images defined there, but I only considered `desktop-build` versus `desktop-test`. I opted for `desktop-build` because `desktop-test` seems to contain mozharness-related stuff that I don't need for now.
  
    :::yaml
    # harness_test.yml
    image:
       type: 'task-image'
       path: 'public/image.tar'
       taskId: '{{#task_id_for_image}}desktop-build{{/task_id_for_image}}'

The image is stored as an artifact of another TC task, which makes it a 'task-image'. Which artifact? The default is `public/image.tar`. Which task do I find the image in? The magic incantation `'{{#task_id_for_image}}desktop-build{{/task_id_for_image}}'` somehow[^6] obtains the correct ID, and if I look at a particular run of my task, the above snippet does indeed get populated with an actual `taskId`. 

    :::javascript
    "image": {
      "path": "public/image.tar",
      // Mystery task that makes a desktop-build image for us. Thanks, mystery task!
      "taskId": "aqt_YdmkTvugYB5b-OvvJw", 
      "type": "task-image"
    }

Snooping around in the handy [Task Inspector](https://tools.taskcluster.net/task-inspector/), I found that the magical mystery task is defined in [image.yml](https://dxr.mozilla.org/mozilla-central/source/testing/taskcluster/tasks/image.yml) and runs [`build_image.sh`](https://dxr.mozilla.org/mozilla-central/source/testing/docker/image_builder/bin/build_image.sh). Fun. It's also quite convenient to [define and test your own custom image](http://docs.taskcluster.net/presentations/TC-102/#/images-00).

## Other details that I mostly ignored

    :::yaml
    # in harness_test.yml
    scopes:
      # Nearly all of our build tasks use tc-vcs
      - 'docker-worker:cache:level-{{level}}-{{project}}-tc-vcs'
    cache:
       # The taskcluster-vcs tooling stores the large clone caches in this
       # directory and will reuse them for new requests this saves about 20s~
       # and is the most generic cache possible.
       level-{{level}}-{{project}}-tc-vcs: '/home/worker/.tc-vcs'

* _Routes_ allow your task to be looked up in the task index. This isn't necessary in my case so I just omitted routes altogether.
* _Scopes_ are permissions for your tasks, and I just copied the scope that is used for checking out source code.
* _workerType_ is a configuration for managing the workers that run tasks. To me, this was a choice between `b2gtest` and `b2gbuild`, which aren't specific to b2g anyway. `b2gtest` is more lightweight, I hear, which suits my harness-test task fine.
* I had to include a few dummy values under `extra` in `harness_test.yml`, like `build_name`, just because they are expected in _build_ tasks. I don't use these values for anything, but my task fails to run if I don't include them.

# Yay for trial and error
* If you have syntax errors in your yaml, the Decision task will fail. If this happens during a try push, look under Job Details > Inspect Task to fine useful error messages.
* Iterating on your task is pretty easy. Aside from pushing to try, you can [run tasks locally using vagrant](http://docs.taskcluster.net/presentations/TC-101/#/run-locally-environment) and you can build a task graph locally as well with `mach taskcluster-graph`. 

# Resources 
Blog posts from other TaskCluster users at Mozilla:

* [https://ehsanakhgari.org/blog/2015-09-29/my-experience-adding-new-build-type-taskcluster](https://ehsanakhgari.org/blog/2015-09-29/my-experience-adding-new-build-type-taskcluster)
* [https://elvis314.wordpress.com/2015/11/09/adventures-in-task-cluster-running-tests-locally/](https://elvis314.wordpress.com/2015/11/09/adventures-in-task-cluster-running-tests-locally/)
* [https://elvis314.wordpress.com/2015/11/11/adventures-in-task-cluster-running-a-custom-docker-image/](https://elvis314.wordpress.com/2015/11/11/adventures-in-task-cluster-running-a-custom-docker-image/)

There is lots of great documentation at [docs.taskcluster.net](https://docs.taskcluster.net), but these sections were especially useful to me:

* [createTask API](http://docs.taskcluster.net/queue/api-docs/#createTask)
* [Workers](http://docs.taskcluster.net/workers/)

# Acknowledgements
Thanks to [dustin](http://code.v.igoro.us/), pmoore and others for corrections and feedback.






