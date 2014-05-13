###############################################################################
# Update the a git repository with official Openobject branches from launchpad
###############################################################################

###
# Variables
#

REMOTE = origin
BRANCHES = "openerp-web/" "openobject-addons/" "openobject-addons/extra-" "openobject-client/" "openobject-client-web/" "openobject-server/" "ocb-server/" "ocb-addons/" "ocb-web/"

.SILENT: help update-master save-changes $(BRANCHES) update-all update-5.0 update-6.0 update-6.1 update-7.0 update-trunk update-demo-5.0 update-demo-6.0 update-demo-6.1 update-demo-7.0 update-demo-trunk

###
# Base commands
#

help:
	echo "Available commands :"
	echo "  update-all"
	echo "  update-5.0"
	echo "  update-6.0"
	echo "  update-6.1"
	echo "  update-7.0"
	echo "  update-trunk"
	echo "  update-demo-5.0"
	echo "  update-demo-6.0"
	echo "  update-demo-6.1"
	echo "  update-demo-7.0"
	echo "  update-demo-trunk"
	echo "You can supply REMOTE=foobar argument to change the used remote. The default is origin"

update-master:
	git fetch $(REMOTE)
	git checkout master
	git pull --ff-only $(REMOTE) master

save-changes:
	echo "Saving changes in master branch..."
	git checkout master
	git add marks/*$(VERSION).bzr marks/*$(VERSION).git logs/*$(VERSION).bzr logs/*$(VERSION).git
	-git commit -m "[IMP] Updated $(VERSION) branches"

###
# Branches update
#

$(BRANCHES): BRANCH = $(subst ",,$@)$(VERSION)
$(BRANCHES): BRANCH_FILE = $(subst /,-,$(BRANCH))
$(BRANCHES):
	echo "Updating $(BRANCH)..."
	-git branch -f -t $(BRANCH) $(REMOTE)/$(BRANCH)
	-bzr fast-export --marks=marks/$(BRANCH_FILE).bzr --git-branch=$(BRANCH) lp:$(BRANCH) 2> logs/$(BRANCH_FILE).bzr \
	    | git fast-import --import-marks-if-exists=marks/$(BRANCH_FILE).git --export-marks=marks/$(BRANCH_FILE).git > logs/$(BRANCH_FILE).git 2>&1

demo-old:
	git checkout demo/$(VERSION)
	git pull --ff-only $(REMOTE) demo/$(VERSION)
	git merge -Xsubtree=server openobject-server/$(VERSION)
	git merge -Xsubtree=addons openobject-addons/$(VERSION)
	git merge -Xsubtree=addons-extra openobject-addons/extra-$(VERSION)
	git merge -Xsubtree=web openobject-client-web/$(VERSION)
	git checkout master

demo:
	git checkout demo/$(VERSION)
	git pull --ff-only $(REMOTE) demo/$(VERSION)
	git merge -Xsubtree=server openobject-server/$(VERSION)
	git merge -Xsubtree=addons openobject-addons/$(VERSION)
	git merge -Xsubtree=web openerp-web/$(VERSION)
	git checkout master

demo-ocb:
	git checkout demo-ocb/$(VERSION)
	git pull --ff-only $(REMOTE) demo-ocb/$(VERSION)
	git merge -Xsubtree=server ocb-server/$(VERSION)
	git merge -Xsubtree=addons ocb-addons/$(VERSION)
	git merge -Xsubtree=web ocb-web/$(VERSION)
	git checkout master

###
# Versions update
#

update-all:
	$(MAKE) -s update-5.0
	$(MAKE) -s update-6.0
	$(MAKE) -s update-6.1
	$(MAKE) -s update-7.0
	$(MAKE) -s update-trunk
	$(MAKE) -s update-demo-5.0
	$(MAKE) -s update-demo-6.0
	$(MAKE) -s update-demo-6.1
	$(MAKE) -s update-demo-7.0
	$(MAKE) -s update-demo-trunk

update-5.0: VERSION = 5.0
update-5.0: update-master "openobject-addons/" "openobject-addons/extra-" "openobject-client/" "openobject-client-web/" "openobject-server/" save-changes

update-6.0: VERSION = 6.0
update-6.0: update-master "openobject-addons/" "openobject-addons/extra-" "openobject-client/" "openobject-client-web/" "openobject-server/" save-changes

update-6.1: VERSION = 6.1
update-6.1: update-master "openerp-web/" "openobject-addons/" "openobject-client/" "openobject-server/" "ocb-server/" "ocb-addons/" "ocb-web/" save-changes

update-7.0: VERSION = 7.0
update-7.0: update-master "openerp-web/" "openobject-addons/" "openobject-server/" "ocb-server/" "ocb-addons/" "ocb-web/" save-changes

update-trunk: VERSION = trunk
update-trunk: update-master "openerp-web/" "openobject-addons/" "openobject-addons/extra-" "openobject-client/" "openobject-client-web/" "openobject-server/" save-changes

update-demo-5.0: VERSION = 5.0
update-demo-5.0: demo-old

update-demo-6.0: VERSION = 6.0
update-demo-6.0: demo-old

update-demo-6.1: VERSION = 6.1
update-demo-6.1: demo demo-ocb

update-demo-7.0: VERSION = 7.0
update-demo-7.0: demo demo-ocb

update-demo-trunk: VERSION = trunk
update-demo-trunk: demo

