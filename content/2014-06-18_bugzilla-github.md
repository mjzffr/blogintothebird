Title: Project Management at Mozilla
Date: 2014-06-10 22:41
Tags: mozilla, foss
Slug: bugzilla-github
Author: Maja Z. Frydrychowicz
Summary: How One and Done uses Github pull requests and bugs in Bugzilla.

One of the most interesting aspects of my OPW internship is learning how contributions and planning are managed in Mozilla projects. Mozilla is known for giant projects like Firefox, but it also has lots of supporting tools and websites. All projects, big and small, are managed using Bugzilla and possibly a mix of other tools, depending on the project team. My observations are based mostly on one project that I've become familiar with: [One and Done](https://github.com/mozilla/oneanddone).

# Bugzilla

[Bugzilla](https://bugzilla.mozilla.org/) is used to describe "bugs" and track their status. A "bug" in Bugzilla in not necessarily a problem that needs to be fixed: it can be feature planned by the core project team, a suggestion from a community member, a representation of a project milestone or even a request for new office furniture for a team member. ;)

Ideally, all the discussion about a bug takes place publicly in its Comments section on Bugzilla so that everyone can see how the bug is evolving. (Not all discussion is public: bugs that relate to a security vulnerability can only be viewed by authorized users.)

If the bug represents a new feature, people might use the Comments section to narrow down or adjust requirements, request clarification or feedback, etc. 

* [Example 1: Profile button](https://bugzilla.mozilla.org/show_bug.cgi?id=1020981)  
* [Example 2: Front page header text](https://bugzilla.mozilla.org/show_bug.cgi?id=1005082)

Bugzilla is also where developers submit solutions for [code review](https://developer.mozilla.org/en-US/docs/Mozilla/Developer_guide/How_to_Submit_a_Patch#Getting_the_patch_reviewed). 

# Bugzilla with Github

Like many other Mozilla projects, One and Done has its repository hosted on Github. When a developer makes a pull request on Github, that PR should refer to the Bugzilla bug ID and it should be [attached to the bug](http://globau.wordpress.com/2013/10/21/github-pull-requests-and-bugzilla/) in Bugzilla with a request for review. ([Example 3: Completed Tasks PR](https://github.com/mozilla/oneanddone/pull/124).) Detailed discussion and feedback about the code takes place in the pull request on Github, but a summary thereof is always included in Bugzilla, often by the reviewer. Github Issues are not used at all since Bugzilla bugs fulfill their role. 

----

Since there are so many tools available to describe and communicate about project progress, it's easy to have project information spread around in many different places, where it may be overlooked or become out-of-date. In the case of One and Done, although there is a project wiki, a Github repo and a Kanban board, all the key project data is in Bugzilla or linked-to from there. As a contributor to the project, there's really only one place I need to look for definitive information, and that's Bugzilla. 
