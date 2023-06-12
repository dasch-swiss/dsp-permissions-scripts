# DSP Permissions Scripts

A collection of scripts to handle permissions in DSP.

## The DSP permissions system

There are 3 permissions systems:

- AP: administrative permissions
- OAP: object access permissions
    - permissions of objects (resources and values)
    - There are user groups who hold certain rights.
    - The `<permissions>` tags in the XML of DSP-TOOLS define OAPs.
- DOAP: default object access permissions
    - configured on a per-project basis
    - defines what should happen if a resource/property/value without OAP is created
    - If a new project without DOAPs is created, there is a default DOAP configuration. (Until now it isn't possible to specify DOAPs when creating a project.)

DOAPs are always project-related, but more specifically, they are:

- either group-related: I belong to a group and create a resource, which OAPs does the resource get?
- or class-related: resources of some classes are public, resources of other classes are restricted.

Group-related and class-related DOAPs cannot be combined, but there is a precedence rule,
[documented here](https://docs.dasch.swiss/2023.03.01/DSP-API/05-internals/design/api-admin/administration/#permission-precedence-rules):

If a user creates a resource, DSP checks the following places for DOAPs:

- First: User belongs to group `ProjectAdmin`: take DOAPs of `ProjectAdmin`
- Then: The class of the resource-to-be-created has DOAPs: take DOAPs of the class
- ...
- Last: User belongs to group `ProjectMember`: take DOAPs of `ProjectMember`

## Typical use cases

If the backend team is asked to change permissions, it is usually because of one of the following reasons:

- Use case 1: The project is unhappy with their default DOAPs. They want other permissions when creating a resource via the APP.
- Use case 2: It's already too late, the project has created resources, and now they want to change the permissions of these resources.
    - The wrong OAPs of existing resources must be adapted.
    - The DOAPs must be adapted, so that new resources get the correct OAPs.

If we modify DOAPs, we usually have to modify them for the groups `ProjectMember` and `ProjectAdmin`, because these are the two groups that always exist.

## Changing DOAPs

### Understanding scopes

Example result of `inspect_permissions()`:

```json
{
  "target": {
    "project": "http://rdfh.ch/projects/y-Hi8o-rTRubFrXDQlhqdw",
    "group": "http://www.knora.org/ontology/knora-admin#ProjectAdmin",
    "resource_class": null,
    "property": null
  },
  "scope": [
    {
      "info": "http://www.knora.org/ontology/knora-admin#ProjectAdmin",
      "name": "CR"
    },
    {
      "info": "http://www.knora.org/ontology/knora-admin#ProjectMember",
      "name": "M"
    }
  ],
  "iri": "http://rdfh.ch/permissions/0846/SWssbbAHQCmL5WShpWOI6g"
},
{
  "target": {
    "project": "http://rdfh.ch/projects/y-Hi8o-rTRubFrXDQlhqdw",
    "group": "http://www.knora.org/ontology/knora-admin#ProjectMember",
    "resource_class": null,
    "property": null
  },
  "scope": [
    {
      "info": "http://www.knora.org/ontology/knora-admin#ProjectAdmin",
      "name": "CR"
    },
    {
      "info": "http://www.knora.org/ontology/knora-admin#ProjectMember",
      "name": "M"
    }
  ],
  "iri": "http://rdfh.ch/permissions/0846/c2jUyfUHQ3mZtXyOGtMv4Q"
}
```

Explanation:

- If a `ProjectAdmin` creates a resource, the resource gets the permissions `CR:ProjectAdmin|M:ProjectMember`.
- If a `ProjectMember` creates a resource, the resource gets the permissions `CR:ProjectAdmin|M:ProjectMember`.
