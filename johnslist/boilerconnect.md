* Week 1 - Django 1.9 Migration
Many projects using Python have fast update cycles compared to other projects built on C or other languages.  This is because the Python language updates fairly and software developers rewrite their code to make use of the latest and greatest features.

Django is one of these projects, having a major release every few months.  It is very important for us to keep updated with the most recent version of Django not only for updates to the core code, but also to ensure the array of plugins and addons we make use of continue to work as third party devs update.

Migration to Django 1.9 involved a few significant changes to our settings file to make sure it remained valid and also removal of deprecated functions from our codebase.
** Tasks Completed - *commit id*
- migrate project, forms, settings, models all to Django 1.9 - *0a44849*
- link resources locally (bootstrap, external images, etc.) - *cd37644* 
- add `client_organization` attribute to Job - *bc2c652*


* Week 2 - Open Source Contributions + Client Organization field
This week I added a few more notification messages to the system.  Specifically, after a Job is created and submitted to an organization, all members of that organization receive a notification they can click on to take them to the JobRequest of interest.

I also learned how to make a pull request on Github:  The notifications-hq plugin we use only accepts individual users as recipients when sending a message.  However, Django ships with a user group model.  I searched through the notifications-hq code for the line where the message is actually sent and modified the function to also accept Groups.  If the function receives a Group type as recipient, it will iterate through all the Group's members and send a message to each.  Then I submitted a pull request to the notifications-hq Github project, wrote some tests at the request of the maintainer, and finally my commit was made public about 2 days later.

We added a `client_organization` field to the Job model so that any Purdue Group receiving a request would see something like `Lafayette City Farms` as the job submitter instead of community partner's user name.
** Tasks Completed - *commit id*
- send notification on JobCreation, redirect user to user_dash after login, remove deprecated functions - *8385cc0*
- add client_organization field to populate.py, cleanup dashboard headers - *58dea3f*

* Week 4 - Job Creation Working
The guided job creation page is finally working.  We've had it almost finished for a while now, but couldn't figure out how to save the selected organizations to the model, since they were being displayed in a custom form.  In the end, we added a hidden "organizations" field to model form on the page, then scripted the form submit button to copy the selected Organization primary keys from our custom html input box immediately before POST.
** Tasks Completed - *commit id*
- display forms errors use base.html - *d9f8147*
- redirect to user dash after account creation - *ae7dcc4*
- patch organization_create form icon upoad - *0c998f5*
- serious html formatting cleanup (aka, de-Dimitrification) - *bd16ec1*
- make job_creation inherit from base.html, make submission and processing work - *d693ced*

* Week 5 - Move to Django Built In Field
One of the features we want available on the organization settings page is for the user to set when their organization is available for work.  The change to models.py was simple enough, with just the addition of a Boolean field.  However, when the field is rendered, it only shows two nondescript radio buttons labeled "True" and "False".  To change the text on these buttons, I tried a hack with custom html similar to what I did for organization selection in Job creation.  However, the solution turned out to be much simpler.  It turns out that BooleanField accepts an argument `choices` that lets you specify the text context for each button, right from models.py.
** Tasks Completed - *commit id*
- add navigation to job creation - *128ba23*
- do proper input validation of org settings in forms.py instead of view - *14b63ae*
- complete job_creation. form submits, orgs are saved, and job is created - *c7a3ccb*
* Week 6 - Explanatory Popup Dialogs
Since our group has been developing this site for almost two years, the site structure and purpose of all pages is perfectly clear to us.  However, new users to our site might be confused to the intent and displayed information of each page.

To solve this, I added dialog boxes which pop up the first time a user visits a page that he/she hasn't seen before.  After the popup is displayed, a record is saved in UserProfile that the page has been visited and the popup doesn't show again.

Beta testing later this semester should give us an idea how effective these popups are.
** Tasks Completed - *commit id*
- add popup dialogs to explain page purpose - *16a483d*
- fix community partner permissions bug in populate.py - *4e98bf1*
* Week 7 -  
** Tasks Completed - *commit id*
- remove noise/logos/notifications from settings pages, fix quick pulldown - *b267ca5*
* Week 8 -  
** Tasks Completed - *commit id*
- make organization search in job_creation portable - *9bcd0b4*
- split all long source lines into multiple lines for readability - ae3812b*

* Week 9 - Modelforms vs Manual Form Handling
For the past few semesters we have been using a mixture of Modelforms and separate form fields with some extra glue in the view when we needed to further customize the appearance of a field.  For example, in Job creation all the attributes (`deliverable`, `description`, `budget`, etc.) are handled by a Modelform with the exception of `organization`, which is a OneToMany relation.  Normally, django will render this field as a `<select>` element with all organizations in the database listed.  Since we needed to organizations to be searchable and have categories, this default didn't work for us, so we wrote a custom form from scratch which provided these things.  

This introduces several new problems when saving and recalling `organization` from the database.  First, we are no longer making use of django's built in mechanisms for prepopulating form data.  We have to pass `organization` as a list of organization names, then use Javascript to select these items in the form field after page load.  Second, we have to handle all the logic that comes with creating and deleting these OneToMany relation.  This wasn't such a huge deal in `job_creation`, where the only possible action is creating new relations. However, when I began writing the `job_edit` page, I realized I would have to compare what was submitted in the form with what was in the database, add the new relations, delete missing ones, and take no action on relations that were already there.

** Tasks Completed
- split org create and edit into two forms - *d86c2ec*

* Week 10 - 
** Tasks Completed
- remove need  for confirm message, use djangos built in messaging - *12f12d5*
- reduce comments code size by about 80% - *58482c0*
- use static modals to display instructions, instead of alert boxes - *23d6bbf*
- dont show other job requests after job confirmation - *fe91160*
- fix comment refresh bug - *f1d17c5*


Talk about beta testing and popups for explanation

* Week 11 - 
** Tasks Completed
- try out split views - *split views branch*
- update example fields on job creation - *61e6ba5*

Talk about why split views do, why they didnt work well, what was solution

* Week 12 - 
** Tasks Completed
- make use of sniplates for form reuseability - *6d59bac*
- keep selected_orgs after error on job_creation/settings - *2585fc4*

talk about sniplates and form resuability

* Week 14 - Beta Testing 2

