Title: Database Migrations ("You know nothing, Version Control.")
Date: 2014-07-04 18:00
Modified: 2014-07-25
Tags: mozilla, foss, opw, south, git, database, django
Slug: borked-migrations
Author: Maja Frydrychowicz
Summary: How to rewrite database migration history in a Django project with South and git.

[playdoh]: https://github.com/mozilla/playdoh
[south]: http://south.aeracode.org/

This is the story of how I rediscovered what version control doesn't do for you. Sure, I understand that git doesn't track what's in my project's local database, but to understand is one thing and to _feel in your heart forever_ is another. In short, learning from mistakes and accidents is the greatest!

So, I've been working on a Django project and as the project acquires new features, the database schema changes here and there. Changing the database from one schema to another and possibly moving data between tables is called a _migration_. To manage database migrations, we use [South][south], which is sort of integrated into the project's `manage.py` script. (This is because we're really using [playdoh][playdoh], Mozilla's augmented, specially-configured flavour of Django.)

South is lovely. Whenever you change the model definitions in your Django project, you ask South to generate Python code that defines the corresponding schema migration, which you can customize as needed. We'll call this Python code a _migration file_. To actually update your database with the schema migration, you feed the migration file to `manage.py migrate`.

These migration files are safely stored in your git repository, so your project has a history of database changes _that you can replay backward and forward_. For example, let's say you're working in a different repository branch on a new feature for which you've changed the database schema a bit. Whenever you switch to the feature branch __you must remember__ to apply your new database migration (migrate forward). Whenever you switch back to master __you must remember__ to migrate backward to the database schema expected by the code in master. __Git doesn't know which migration your database should be at.__ Sometimes I'm distracted and I forget. :(

As always, it gets more interesting when you have project collaborators because they might push changes to migration files and __you must pay attention and remember__ to actually apply these migrations in the right order. We will examine one such scenario in detail.

# Adventures with Overlooked Database Migrations

Let's call the actors Sparkles and Rainbows. Sparkles and Rainbows are both contributing to the same project and so they each regularly push or pull from the same "upstream" git repository. However, they each use their own local database for development. As far as the database goes, git is only tracking South migration files. Here is our scenario.

1. Sparkles pushes Migration Files 1, 2, 3 to upstream and applies these migrations to their local db in that order. 
2. Rainbows pulls Migration Files 1, 2, 3 from upstream and applies them to their local db in that order.
>All is well so far. The trouble is about to start.
3. Sparkles reverses Migration 3 in their local database (backward migration to Migration 2) and pushes a delete of the Migration 3 file to upstream.
4. Rainbows pulls from upstream: the Migration 3 file no longer exists at `HEAD` __but it must also be reversed in the local db__! Alas, Rainbows does not perform the backward migration. :(
5. Life goes on and Sparkles now adds Migration Files 4 and 5, applies the migrations locally and pushes the files to upstream. 
6. Rainbows happily pulls Migrations Files 4 and 5 and applies them to their local db. 
>Notice that Sparkles' migration history is now 1-2-4-5 but Rainbows' migration history is 1-2-3-4-5, but 3 is nolonger part of the up-to-date project! 

At some point Rainbows will encounter Django or South errors, depending on the nature of the migrations, because the database doesn't match the expected schema. No worries, though, it's git, it's South: you can go back in time and fix things.

I was recently in Rainbows' position. I finally noticed that something was wrong with my database when South started refusing to apply the latest migration from upstream, telling me "Sorry! I can't drop table TaskArea, it doesn't exist!" 

    tasks:0011_auto__del_taskarea__del_field_task_area__add_field_taskkeyword_name
    FATAL ERROR - The following SQL query failed: DROP TABLE tasks_taskarea CASCADE;
    The error was: (1051, "Unknown table 'tasks_taskarea'")
    >snip
    KeyError: "The model 'taskarea' from the app 'tasks' is not available in
    this migration."

In my instance of the Sparkles-Rainbows story, Migration 3 and Migration 5 both drop the TaskArea table; I'm trying to apply Migration 5, and South  grumbles in response because I had never reversed Migration 3. As far as South knows, there's no such thing as a TaskArea table. 

Let's take a look at my migration history, which is conveniently stored in the database itself:
```mysql
select migration from south_migrationhistory where app_name="tasks";
```

The output is shown below. The lines of interest are `0010_auth__del` and `0010_auto__chg`; I'm trying to apply migration `0011` but I can't, because it's the same migration as `0010_auto__del`, which should have been reversed a few commits ago. 
```
+------------------------------------------------------------------------------+
|  migration                                                                   |
+------------------------------------------------------------------------------+
|  0001_initial                                                                |
|  0002_auto__add_feedback                                                     |
|  0003_auto__del_field_task_allow_multiple_finishes                           |
|  0004_auto__add_field_task_is_draft                                          |
|  0005_auto__del_field_feedback_task__del_field_feedback_user__add_field_feed |
|  0006_auto__add_field_task_creator__add_field_taskarea_creator               |
|  0007_auto__add_taskkeyword__add_tasktype__add_taskteam__add_taskproject__ad |
|  0008_task_data                                                              |
|  0009_auto__chg_field_task_team                                              |
|  0010_auto__del_taskarea__del_field_task_area__add_field_taskkeyword_name    |
|  0010_auto__chg_field_taskattempt_user__chg_field_task_creator__chg_field_ta |
+------------------------------------------------------------------------------+
```

I want to migrate backwards until `0009`, but I can't do that directly because the migration file for `0010_auto__del` is not part of `HEAD` anymore, just like Migration 3 in the story of Sparkles and Rainbows, so South doesn't know what to do. However, that migration does exist in a previous commit, so let's go back in time.

I figure out which commit added the migration I need to reverse:

```sh
# Display commit log along with names of files affected by each commit. 
# Once in less, I searched for '0010_auto__del' to get to the right commit.
git log --name-status | less
```

With that key information, the following sequence of commands tidies everything up:

```sh
# Switch to the commit that added migration 0010_auto__del
git checkout e67fe32c
# Migrate backward to a happy migration; I chose 0008 to be safe. 
# ./manage.py migrate [appname] [migration]
./manage.py migrate oneanddone.tasks 0008
git checkout master
# Sync the database and migrate all the way forward using the most 
# up-to-date migrations.
./manage.py syncdb && ./manage.py migrate
```
