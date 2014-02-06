# OpenERP

This repository is updated daily.

## Official branches imported from launchpad
* 5.0 Series
    * openobject-server/5.0
    * openobject-addons/5.0
    * openobject-addons/extra-5.0
    * openobject-client-web/5.0
    * openobject-client/5.0
* 6.0 Series
    * openobject-server/6.0
    * openobject-addons/6.0
    * openobject-addons/extra-6.0
    * openobject-client-web/6.0
    * openobject-client/6.0
* 6.1 Series
    * openobject-server/6.1
    * openobject-addons/6.1
    * openerp-web/6.1
    * openobject-client/6.1
* 7.0 Series
    * openobject-server/7.0
    * openobject-addons/7.0
    * openerp-web/7.0
* OCB 6.1 Series
    * ocb-server/6.1
    * ocb-addons/6.1
    * ocb-web/6.1
* OCB 7.0 Series
    * ocb-server/7.0
    * ocb-addons/7.0
    * ocb-web/7.0

## Demo branches, with a Makefile for simple environment initialization
* demo/5.0
* demo/6.0
* demo/6.1
* demo/7.0
* demo-ocb/6.1
* demo-ocb/7.0

## Quick creation and update of a new project's repo

### Creation

To start a new project, you can import official branches from this repository as subtrees of your project repo.
You must have at least one commit on your repo for the `git merge -s ours` commands work as expected, this is why we add an empty `.gitignore` file in this example.

```bash
git init new_project
cd new_project
touch .gitignore
git add .gitignore
git commit -m "[INIT] Initialize new project"
git remote add -f openerp https://github.com/syleam/openerp.git
git merge -s ours --no-commit openerp/openobject-server/<VERSION>
git read-tree --prefix=server -u openerp/openobject-server/<VERSION>
git commit -m "[ADD] Add server <VERSION>"
git merge -s ours --no-commit openerp/openobject-addons/<VERSION>
git read-tree --prefix=addons -u openerp/openobject-addons/<VERSION>
git commit -m "[ADD] Add addons <VERSION>"
git merge -s ours --no-commit openerp/openerp-web/<VERSION>
git read-tree --prefix=web -u openerp/openerp-web/<VERSION>
git commit -m "[ADD] Add web addons <VERSION>"
```
### Update

Git allows you to update the branches with a simple merge.

```bash
git merge -Xsubtree=server openerp/openobject-server/<VERSION>
git merge -Xsubtree=addons openerp/openobject-addons/<VERSION>
git merge -Xsubtree=web openerp/openerp-web/<VERSION>
```
