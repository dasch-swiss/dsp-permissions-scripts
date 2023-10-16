# DSP Permissions Scripts

A collection of scripts to handle permissions in DSP.


## Local setup to run the scripts in this repository

Set up the poetry virtual environment:

- Install poetry with `curl -sSL https://install.python-poetry.org | python3 -`
  (for Windows, see [https://python-poetry.org/docs/](https://python-poetry.org/docs/))
- Execute `poetry install`, which will:
    - create a virtual environment (if there isn't already one)
    - install all dependencies from `poetry.lock`
- Set the virtual environment's Python interpreter as default interpreter in your IDE,
  so that your IDE uses the correct Python version and the correct dependencies.


## The DSP permissions system

There are 3 permissions systems:

- **AP**: Administrative Permissions
    - define what users of a certain group can do on project level (e.g. create resources, modify groups, etc.)
- **OAP**: Object Access Permissions
    - define permissions of objects (resources and values)
    - OAPs grant rights to certain user groups.
    - The `<permissions>` tags in the XML of DSP-TOOLS define OAPs.
- **DOAP**: Default Object Access Permissions
    - configured on a per-project basis
    - defines what should happen if a resource/property/value is created without OAP.
    - If a new project without DOAPs is created, there is a default DOAP configuration.
      (Until now it isn't possible to specify DOAPs when creating a project.)

The permissions system of DSP is documented
[here](https://docs.dasch.swiss/2023.10.01/DSP-API/05-internals/design/api-admin/administration/).

The `/admin/permissions` endpoint of DSP-API is documented
[here](https://docs.dasch.swiss/2023.10.01/DSP-API/03-endpoints/api-admin/permissions/).


### APs: Administrative Permissions

A user group can have one or more of the following permissions:
# is allowed to create resources inside the project
`ProjectResourceCreateAllPermission`
# is allowed to create resources of certain classes inside the project
`ProjectResourceCreateRestrictedPermission`
# is allowed to do anything on project level
`ProjectAdminAllPermission`
# is allowed to modify group info and group membership on all groups belonging to the project
`ProjectAdminGroupAllPermission`
# is allowed to modify group info and group membership on certain groups belonging to the project
`ProjectAdminGroupRestrictedPermission`
# is allowed to change the permissions on all objects belonging to the project
`ProjectAdminRightsAllPermission`


### OAPs: Object Access Permissions

OAPs grant **rights** to certain **user groups**.

OAPs are attached to either a resource or a value (value of a property),
but not to a property.

#### Rights

A group can have exactly one of these rights:

- (no right): If no permission is defined for a certain group of users, these users cannot view any resources/values.
- `RV` _restricted view permission_: Same as `V`,
  but if it is applied to an image, the image is shown with a reduced resolution or with a watermark overlay.
- `V` _view permission_: The user can view a resource or a value, but cannot modify it.
- `M` _modify permission_: The user can modify the element, but cannot mark it as deleted.
  The original resource or value will be preserved.
- `D` _delete permission_: The user is allowed to mark an element as deleted.
  The original resource or value will be preserved.
- `CR` _change right permission_: The user can change the permission of a resource or value.
  The user is also allowed to permanently delete (erase) a resource.

Every right of this row includes all previous rights.

#### User Groups

The user doesn't hold the permissions directly,
but belongs to an arbitrary number of groups which hold the permissions.
There are **built-in groups** and **project specific groups**:

- **Built-in groups**: Every user is automatically in at least one of the following built-in groups:
    - `UnknownUser`: The user is not known to DSP (not logged in).
    - `KnownUser`: The user is logged in, but not a member of the project the data element belongs to.
    - `ProjectMember`: The user belongs to the same project as the data element.
    - `ProjectAdmin`: The user is project administrator in the project the data element belongs to.
    - `Creator`: The user is the owner of the element (created the element).
    - `SystemAdmin`: The user is a system administrator.
- **Project specific groups**:
    - projects can define their own groups

### DOAPs: Default Object Access Permissions

DOAPs are always project-related, but more specifically, they are:

- Either group-related: I belong to a group and create a resource, which OAPs does the resource get?
- Or ontology-related:
    - class-related: resources of some classes are public, while resources of other classes are restricted
    - property-related: some properties are public, while other properties are restricted
    - or a combination of class/property-related

Group-related and class-related DOAPs cannot be combined, but there is a precedence rule.

#### Precedence rule

If a user creates a resource, DSP checks the following places for DOAPs:

- First: User belongs to group `ProjectAdmin`: take DOAPs of `ProjectAdmin`
- Then: The class of the resource-to-be-created has DOAPs: take DOAPs of the class
- ...
- Last: User belongs to group `ProjectMember`: take DOAPs of `ProjectMember`

[See the docs](https://docs.dasch.swiss/2023.03.01/DSP-API/05-internals/design/api-admin/administration/#permission-precedence-rules)
for more details.


## Typical use cases

If permissions need to be changed, it is usually because of one of the following reasons:

- Use case 1: The project is unhappy with their default DOAPs.
  They want other permissions when creating a resource via the APP.
- Use case 2: It's already too late, the project has created resources,
  and now they want to change the permissions of these resources.
    - The wrong OAPs of existing resources must be adapted.
    - The DOAPs must be adapted, so that new resources get the correct OAPs.

If we modify DOAPs, we usually have to modify them for the groups `ProjectMember` and `ProjectAdmin`,
because these are the two groups that always exist.


## Changing DOAPs

### Understanding scopes

A scope is a mapping of groups to rights granted to that group.

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
