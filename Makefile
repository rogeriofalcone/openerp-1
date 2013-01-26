###############################################################################
# Update the a git repository with official Openobject branches from launchpad
###############################################################################

###
# Variables
#

REMOTE = origin
BRANCHES = "openerp-web/" "openobject-addons/" "openobject-addons/extra-" "openobject-client/" "openobject-client-web/" "openobject-server/"

.SILENT: help update-master save-changes $(BRANCHES) update-all update-5.0 update-6.0 update-6.1 update-7.0

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
	echo "You can supply REMOTE=foobar argument to change the used remote. The default is origin"

update-master:
	git fetch $(REMOTE)
	git checkout master
	git pull --ff-only $(REMOTE) master

save-changes:
	echo "Saving changes in master branch..."
	git checkout master
	git add marks/*$(VERSION).bzr marks/*$(VERSION).git logs/*$(VERSION).bzr logs/*$(VERSION).git
	git commit -m "[IMP] Updated $(VERSION) branches"

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

###
# Versions update
#

update-all:
	$(MAKE) -s update-5.0
	$(MAKE) -s update-6.0
	$(MAKE) -s update-6.1
	$(MAKE) -s update-7.0

update-5.0: VERSION = 5.0
update-5.0: update-master "openobject-addons/" "openobject-addons/extra-" "openobject-client/" "openobject-client-web/" "openobject-server/" save-changes

update-6.0: VERSION = 6.0
update-6.0: update-master "openobject-addons/" "openobject-addons/extra-" "openobject-client/" "openobject-client-web/" "openobject-server/" save-changes

update-6.1: VERSION = 6.1
update-6.1: update-master "openerp-web/" "openobject-addons/" "openobject-client/" "openobject-server/" save-changes

update-7.0: VERSION = 7.0
update-7.0: update-master "openerp-web/" "openobject-addons/" "openobject-server/" save-changes

