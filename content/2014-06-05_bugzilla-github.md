Title: Project Management at Mozilla
Date: 2014-06-05 20:41
Modified: 2014-06-18 
Tags: mozilla, foss
Slug: bugzilla-github
Author: Maja Z. Frydrychowicz
Summary: How One and Done uses Github pull requests and bugs in Bugzilla.

One of the most interesting aspects of my [OPW](https://wiki.gnome.org/OutreachProgramForWomen) internship is learning how contributions and planning are managed in Mozilla projects. So huge! So many contributors! Ahhh! Mozilla is known for giant projects like Firefox, but it also builds lots of supporting tools and websites. All projects, big and small, are managed using Bugzilla and often a mix of other tools, depending on the project team. My observations are based mostly on one project that I've become familiar with: [One and Done](https://github.com/mozilla/oneanddone). Warning: I'm going to say "Bugzilla" a lot.

# Bugzilla
[Bugzilla](https://bugzilla.mozilla.org/) is used to describe "bugs" and track their status. A "bug" in Bugzilla in not necessarily a problem that needs to be fixed: it can be feature planned by the core project team, a suggestion from a community member, a representation of a project milestone or even a request for new office furniture for a team member. Seriously.

Ideally, all the discussion about a bug takes place publicly in its Comments section on Bugzilla so that everyone can see how the bug is evolving and anyone can join in. (Not all discussion is public: bugs that relate to a security vulnerability can only be viewed by authorized users.)

If the bug represents a new feature, people might use the Comments section to narrow down or adjust requirements, request clarification or feedback, etc. 

* [Example 1: Profile button bug](https://bugzilla.mozilla.org/show_bug.cgi?id=1020981)  
* [Example 2: Front page header text bug](https://bugzilla.mozilla.org/show_bug.cgi?id=1005082)

Bugzilla is also where developers submit solutions for [code review](https://developer.mozilla.org/en-US/docs/Mozilla/Developer_guide/How_to_Submit_a_Patch#Getting_the_patch_reviewed). 

# Bugzilla with Github
Like many other Mozilla projects, One and Done has its repository hosted on Github. Github Issues are not used at all since Bugzilla bugs fulfill their role. When a developer makes a pull request on Github, that PR should refer a Bugzilla bug ID and it should be [attached to the bug](http://globau.wordpress.com/2013/10/21/github-pull-requests-and-bugzilla/) in Bugzilla with a request for review. ([Example 3: Completed Tasks PR](https://github.com/mozilla/oneanddone/pull/124).) One can also add a brief summary of the PR in the bug comments. Detailed discussion and feedback about the code takes place in the pull request on Github, but a summary thereof is always included in Bugzilla, often by the reviewer. 

# One Source of Information
Since there are so many tools available to describe and communicate about project progress, it's a common problem to have project information spread around in many different places, where it may be overlooked or become out-of-date. 

In the case of One and Done, although there is a [project wiki](https://wiki.mozilla.org/QA/OneandDone), a [Github repo](https://github.com/mozilla/oneanddone), a [Kanban board](https://mozilla.kanbanery.com/projects/45827/board/?key=fe86e00cb6c613df344772a58b72bd92a0f38995) and brief discussion over IRC and email,  all the key project data is in Bugzilla or linked-to from there. As a contributor to the project, there's really only one place I need to look for definitive information, and that's Bugzilla. Bugzilla, Bugzilla, Bugzilla.
