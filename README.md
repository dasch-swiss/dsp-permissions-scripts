# DSP Permissions Scripts

A collection of scripts to handle permissions in DSP.

> 💡 **Note**
>
> The code and logs of accomplished projects can be found on
> [Google Drive](https://drive.google.com/drive/folders/1TRsQjId97-QbmY-nCuWEUJdgkxlRMGDH)


## Local setup to run the scripts in this repository

Set up the poetry virtual environment:

- Install poetry with `curl -sSL https://install.python-poetry.org | python3 -`
    - for Windows, see [https://python-poetry.org/docs/](https://python-poetry.org/docs/)
- Execute `poetry install`, which will:
    - create a virtual environment (if there isn't already one)
    - install all dependencies from `poetry.lock`
- Set the virtual environment's Python interpreter as default interpreter in your IDE,
  so that your IDE uses the correct Python version and the correct dependencies.


## How to use this repo

- Make a copy of `dsp_permissions_scripts/template.py` and adapt it to your needs.
- The template is the only file you should modify. All other code can be considered as consume-only library.
- If you interact with a server that needs credentials, set them in a `.env` file:

  ```bash
  # DO NOT COMMIT THIS FILE TO GIT!

  PROD_EMAIL="your.name@dasch.swiss"
  PROD_PASSWORD="pw-on-app.dasch.swiss"

  TEST_EMAIL="your-name@dasch.swiss"
  TEST_PASSWORD="pw-on-app.test.dasch.swiss"

  DEV_EMAIL="your-name@dasch.swiss"
  DEV_PASSWORD="pw-on-app.dev.dasch.swiss"
  ```

- For a first, exploratory run, comment out the parts of the template that make the modifications.
- You will get JSON files in `project_data/<shortcode>/` with the permissions retrieved from the server.
- Based on these, write your code to modify the permissions.
- Run the entire script.


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


## AP: Administrative Permissions

A user group can have one or more of the following permissions:

- `ProjectResourceCreateAllPermission`: is allowed to create resources inside the project
- `ProjectResourceCreateRestrictedPermission`: is allowed to create resources of certain classes inside the project
- `ProjectAdminAllPermission`: is allowed to do anything on project level
- `ProjectAdminGroupAllPermission`: is allowed to modify group info and group membership on all groups of the project
- `ProjectAdminGroupRestrictedPermission`: is allowed to modify group info and group membership on certain groups of the project
- `ProjectAdminRightsAllPermission`: is allowed to change the permissions on all objects belonging to the project

> 💡 **Note**
>
> [This example file](project_data/F18E_example_project/APs_original.json)
> contains 2 APs that:
>
>- grant to `knora-admin:ProjectAdmin` the rights to do anything on project level, and to create resources of any class.
>- grant to `knora-admin:ProjectMember` the rights to create resources of any class.


## OAP: Object Access Permissions

OAPs grant **rights** to certain **user groups**.
These are mapped to each other using **permission strings** (represented as **scopes** in this repo).

OAPs are attached to either a resource or a value (value of a property), but not to a property.


### 1. Rights

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


### 2. User Groups

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


### 3. Permission strings / scopes

**Permission strings** (represented as **scopes** in this repo) are used to grant **rights** to certain **user groups**.

> 💡 **Note**
>
> [This example file](project_data/F18E_example_project/OAPs_original/resource_XwwqVvWgSmuHRobQubg9uQ.json)
> contains an OAP that grants the following rights to the resource `http://rdfh.ch/0102/XwwqVvWgSmuHRobQubg9uQ`:
> 
> - Project admins have change rights.
> - The creator has deletion rights.
> - Project members have view rights.
> - All others (logged-in or logged-out users) have restricted view rights.
>
> The string representation of this scope would be:
> `CR knora-admin:ProjectAdmin|D knora-admin:Creator|M knora-admin:ProjectMember|RV knora-admin:UnknownUser,knora-admin:KnownUser`.


## DOAP: Default Object Access Permissions

DOAPs are always project-related, but more specifically, they are:

- Either group-related: I belong to a group and create a resource, which OAPs does the resource get?
- Or ontology-related:
    - class-related: resources of some classes are public, while resources of other classes are restricted
    - property-related: some properties are public, while other properties are restricted
    - or a combination of class/property-related

> 💡 **Note**
>
> [This example file](project_data/F18E_example_project/DOAPs_original.json)
> contains 2 DOAPs that encode the following information:
> 
> - If a `ProjectAdmin` creates a resource, the resource's OAP would grant
>     - change rights to `ProjectAdmin`
>     - deletion rights to `Creator` and `ProjectMember`
>     - view rights to `KnownUser` and `UnknownUser`
> - If a `ProjectMember` creates a resource, the resources OAP would grant the same permissions to the same user groups.


### Precedence rule

Group-related and class-related DOAPs cannot be combined, but there is a precedence rule.

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
