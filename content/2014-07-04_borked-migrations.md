Title: South Migrations
Date: 2014-07-04 18:00
Modified: 2014-07-07
Tags: mozilla, foss, opw, south, git, database, django, playdoh
Slug: borked-migrations
Author: Maja Z. Frydrychowicz
Summary: As

If you're collaborating on a [Django] project that uses South for database migrations

Version control (migration files) in conflict with local database. 

Let's call the actors Sparkles and Rainbows. Sparkles and Rainbows are both contributing to the same project and so they each regularly push or pull from the same "upstream" git repository. However, they each use their own local database for development. Git does not track database changes but it does track South migration files. Here is our scenario.

1. Sparkles pushes Migration Files 1, 2, 3 to upstream and applies these migrations to their local db in that order. 
2. Rainbows pulls Migration Files 1, 2, 3 from upstream and applies them to their local db in that order.
>All is well so far. The trouble is about to start.
3. Sparkles reverses Migration 3 in their local database (backward migration to Migration 2) and pushes a delete of the Migration 3 file to upstream.
4. Rainbows pulls from upstream: Migration 3 no longer exists in the repository __but it must also be reversed in the local db__! Alas, Rainbows does not do the backward migration. :(
5. Life goes on and Sparkles now adds Migration Files 4 and 5, applies the migrations locally and pushes the files to upsteam. 
6. Rainbows happily pulls Migrations Files 4 and 5 and applies them to their local db. 
>Notice that Sparkles' migration history is now 1-2-4-5 but Rainbows' migration history is 1-2-3-4-5 even though 3 is nolonger part of the repo! 

At some point Rainbows will encounter Django or South errors, depending on the nature of the migrations, because the database doesn't match the expected schema. No worries, though, it's git, it's South: you can go back in time and fix things, but how? 

I was recently in Rainbows' position. I finally noticed that something was wrong with my database when south started refusing to apply the latest migration from upstream, telling me "Sorry! I can't drop table TaskArea, it doesn't exist!" 

    tasks:0011_auto__del_taskarea__del_field_task_area__add_field_taskkeyword_name
    FATAL ERROR - The following SQL query failed: DROP TABLE tasks_taskarea CASCADE;
    The error was: (1051, "Unknown table 'tasks_taskarea'")
    >snip
    KeyError: "The model 'taskarea' from the app 'tasks' is not available in this migration."

In my instance of this story, Migration 3 and Migration 5 both drop the TaskArea table; I was trying to apply Migration 5 now, and south was grumbling in response because I had never reversed Migration 3. 

Let's take a look at my migration history:
```mysql
select migration from south_migrationhistory where app_name="tasks";
```

Here's what I get. The lines of interest are `0009`, `0010_auth__del` and `0010_auto__chg`; I'm trying to apply migration `0011` but I can't, because it's the same migration as `0010_auto__del`, which should be reversed. 
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

I want to migrate backwards until `0009`, but I can't do that directly because the migration file for `0010_auto__del` is not in the repo anymore (just like Migration 3 in the story of Sparkles and Rainbows) so south doesn't know what to do. __FIXME__ However, that migration does exist in a previous commit, so let's go back in time.



Migrations destructive

What is south? Can it be used with non-Django
One and Done, Django, Pladoh (watch video about Playdoh)

