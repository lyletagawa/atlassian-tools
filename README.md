# atlassian-tools

Improve the Atlassian experience by automating cumbersome workflows

## Atlassian Jira

### go-jira

[go-jira](https://github.com/go-jira/jira) is a simple command line client for Atlassian's Jira service (originally from Netflix-Skunkworks) written in Go.

## Atlassian Confluence

### confluence_export_space.py

Exporting a Confluence space is beneficial:

- Maintain a local, offline copy of critical documentation
- Maintain a vendor-neutral external backup of team/company documentation

Confluence allows its users to export a single page to PDF. However, exporting multiple pages (in one operation) is prohibited without the `Export Space` permission...

In addition, the Atlassian REST API does not include an option for exporting a space (missing from the Atlassian API since Confluence 5.5).

Instead, we can use the Atlassian REST API to export a Confluence space by reconstructing the Confluence space hierarchy and exporting each individual page.

This is inefficient, but it is a workaround if your Atlassian installation does not authorize you to export a space.

### confluence_group_members.py

Listing an Atlassian group's users is beneficial:

- Determine appropriate group for use in Confluence wiki restrictions
- Determine appropriate group to @tag in a Jira issue or Confluence wiki

Atlassian users however, are not authorized to list group membership unless they have `Administrator` privileges...

```
$ curl -s -u "${user}:${pass}" "https://example.atlassian.net/rest/api/3/group/member?groupname=users" | jq -r '.errorMessages[]'
You are not authorized to perform this action. Administrator privileges are required.
```

Atlassian users however, are authorized to list users' groups. We can use the Atlassian API to enumerate each user object and reconstruct a groups' members.

This is inefficient, but it is a workaround if your Atlassian installation does not authorize you to list group membership.
