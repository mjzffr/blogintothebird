Title: Not Testing a Firefox Build (Generic Tasks in TaskCluster)
Date: 2016-05-02
Modified: 2016-05-02
Tags: mozilla, foss, ci, automation, taskcluster
Slug: taskcluster-generic-tasks
Author: Maja Frydrychowicz
Summary: I take advantage of generic tasks to run a mozharness script in a gecko source checkout.

A few months ago I wrote about my [tentative setup]({filename}2016-02-09_mozilla-taskcluster.md) of a TaskCluster task that was neither a build nor a test. Since then, gps has implemented ["generic" in-tree tasks](https://groups.google.com/forum/#!searchin/mozilla.dev.platform/generic$20task/mozilla.dev.platform/bNYp2HDyeqU/tg4mnGHEAwAJ) so I [adapted my initial work](https://bugzilla.mozilla.org/show_bug.cgi?id=1227367#c116) to take advantage of that.

# Triggered by file changes

All along I wanted to run some in-tree tests without having them wait around for a Firefox build or any other dependencies they don't need. So I originally implemented this task as a ["build"]({filename}2016-02-09_mozilla-taskcluster.md#scheduling_summary) so that it would get scheduled for every incoming changeset in Mozilla's repositories. 

But forget "builds", forget "tests" -- now there's a third category of tasks that we'll call "generic" and it's exactly what I need. 

In [base_jobs.yml](https://hg.mozilla.org/mozilla-central/diff/e4ea9261d5bb/testing/taskcluster/tasks/branches/base_jobs.yml) I say, "hey, here's a new task called `marionette-harness` -- run it whenever there's a change under (branch)/testing/marionette/harness". Of course, I can also just trigger the task with try syntax like `try: -p linux64_tc -j marionette-harness -u none -t none`.

When the task is triggered, a chain of events follows: 

* `marionette-harness` is defined by [harness_marionette.yml](https://hg.mozilla.org/mozilla-central/file/e4ea9261d5bb/testing/taskcluster/tasks/tests/harness_marionette.yml), which depends on [harness_test.yml](https://hg.mozilla.org/mozilla-central/file/e4ea9261d5bb/testing/taskcluster/tasks/harness_test.yml)
* [harness_test.yml](https://hg.mozilla.org/mozilla-central/file/e4ea9261d5bb/testing/taskcluster/tasks/harness_test.yml) says to run [build.sh](https://hg.mozilla.org/mozilla-central/diff/e4ea9261d5bb/testing/docker/desktop-build/bin/build.sh) with the appropriate mozilla branch and revision.
* [harness_marionette.yml](https://hg.mozilla.org/mozilla-central/file/e4ea9261d5bb/testing/taskcluster/tasks/tests/harness_marionette.yml) sets more environment variables and parameters for build.sh to use (`JOB_SCRIPT`, `MOZHARNESS_SCRIPT`, etc.)
* So build.sh checks out the source tree and executes [harness-test-linux.sh](https://hg.mozilla.org/mozilla-central/diff/e4ea9261d5bb/testing/taskcluster/scripts/tester/harness-test-linux.sh) (`JOB_SCRIPT`)...
* ...which in turn executes [marionette_harness_tests.py](https://hg.mozilla.org/mozilla-central/file/1e0b4e27bd51/testing/mozharness/scripts/marionette_harness_tests.py) (`MOZHARNESS_SCRIPT`) with the parameters passed on by build.sh

# For Tasks that Make Sense in a gecko Source Checkout

As you can see, I made the `build.sh` script in the `desktop-build` docker image execute an arbitrary in-tree `JOB_SCRIPT`, and I created `harness-test-linux.sh` to run mozharness within a gecko source checkout. 

## Why not the desktop-test image?

But we can also run arbitrary mozharness scripts thanks to the configuration in the desktop-test docker image! Yes, and all of that configuration is geared toward testing a Firefox binary, which implies downloading tools that my task either doesn't need or already has access to in the source tree. Now we have a lighter-weight option for executing tests that don't exercise Firefox.

## Why not mach?

In my lazy work-in-progress, I had originally executed the Marionette harness tests via a simple call to mach, yet now I have this crazy chain of shell scripts that leads all the way mozharness. The mach command didn't disappear -- you can run Marionette harness tests with `./mach python-test ...`. However, mozharness provides clearer control of Python dependencies, appropriate handling of return codes to report test results to Treeherder, and I can write a job-specific script and configuration.






