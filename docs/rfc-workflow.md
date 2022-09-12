# RFC: uiqmako centered workflow

## Context

Current uiqmako workflow relies heavily in the idea
that the only reliable template version to work on is
the template version stored on the ERP.
User edits are considered just a transitional, temporary and blocking
operation done by one user on a template version existing on an given ERP.

The actual process of updating a template is a longer one
that involves several people and revisions.
Just at the end of the process the result is uploaded to the production ERP.

While the current view could have some sense in a desktop application,
where the shared repository is the ERP and the user downloads and locks
the resource until its done and it is uploaded or released,
uiqmako is a shared server itself and has wide view on what the users are doing.

Owning the workflow means that the current shared working version of a template
is the one stored in uiqmako.
This could simplify and flexibilize the workflow enabling more powerful features.

For example, now:

- Several users cannot perform successive edits without uploading it to an ERP in between
- The template cannot be uploaded if it has been modified directly on the ERP
- All the edits between the import and the export are considered a single edit,
  and are removed after exporting, only exported versions are saved into version control

## Considered use cases

- Modifying a template existing in Production ERP
- Developing a brand new template
- Modifying a production template using ERP features not yet in production but in preproduction environments
- Multiple users taking part on the development of a template (IT, tech team, legal, designer...)
- Rollback development to a previous stage
- Restoring production status after an failed update
- Continuous monitoring of the effects of the changes on rendered cases.

## Principles for the new workflow

- uiqmako template status is the current development status of each template
  - several modifications might take place without uploading it to the ERP
- uiqmako template status is version controlled (using git, versions history on db... whatever)
  - you might rollback to an old version (not necessarily the user)
- You might import/export the template from/to any ERP
- You might render the template on any ERP, on demand
- Once you modify a template, the cases are automatically rendered in the uiqmako server
- Differences on case renderings, are notified to the user so she can review and aprove them
- Those automated renders use the same ERP (offline and non-mutating data) to ensure a fair diff
- On demand renders, may let use a different ERP

## Considerations

- Overwritting local or remote changes by importing/exporting
  - Import: Local changes have version control and can be recovered
  - Export: Remote changes could be saved previously into the version control for safety
  - On those cases: warn the user but let her do

- Exporting to production is delicated
  - Maybe limited to priviledged profiles

- Id coherence Exporting/Importing to/from different ERP's
  - Simpler: relay just in semantic ids, forbiding exporting if the id does not exist on the target
  - More permisive: Export non existing semantic ids by creating them
  - More permisive: Export existing erp id's by also matching name and model, but not creating

- Automated rendering and multiple ERP -> Moving target
  - should be avoided by setting up a single render ERP. It could be done:
    - for each case (the requirement but maybe hard to setup, or not if we are choosing semantic ids from a given erp)
    - for all templates (easier to implemnt but not flexible)
    - for all cases of the same template (middle ground)

- On demand rendering could be done against any other ERP provided that:
  - Case's object is semantically idded and exists in that ERP
  - Also ERP id's. Might fail but, on demand renders have no side effect

- Take over the control over the format of the template
  - The internal representation of a template could be markdown, or
    complemented with a skeleton, or having marks or being structured...

