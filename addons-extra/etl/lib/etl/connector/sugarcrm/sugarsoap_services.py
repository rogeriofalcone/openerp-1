
from sugarsoap_services_types import *
import urlparse, types
from ZSI.TCcompound import ComplexType, Struct
from ZSI import client
import ZSI
 

# Locator
class sugarsoapLocator:
    sugarsoapPortType_address = "http://192.168.0.7/sugarcrm/soap.php"
    def getsugarsoapPortTypeAddress(self):
        return sugarsoapLocator.sugarsoapPortType_address
    def getsugarsoapPortType(self, url=None, **kw):
        return sugarsoapBindingSOAP(url or sugarsoapLocator.sugarsoapPortType_address, **kw)

# Methods
class sugarsoapBindingSOAP:
    def __init__(self, url, **kw):
        kw.setdefault("readerclass", None)
        kw.setdefault("writerclass", None)
        # no resource properties
        self.binding = client.Binding(url=url, **kw)
        # no ws-addressing

    # op: create_session
    def create_session(self, request):
        if isinstance(request, create_sessionRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/create_session", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=create_sessionResponse.typecode.ofwhat, pyclass=create_sessionResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: end_session
    def end_session(self, request):
        if isinstance(request, end_sessionRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/end_session", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=end_sessionResponse.typecode.ofwhat, pyclass=end_sessionResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: contact_by_email
    def contact_by_email(self, request):
        if isinstance(request, contact_by_emailRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/contact_by_email", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=contact_by_emailResponse.typecode.ofwhat, pyclass=contact_by_emailResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: user_list
    def user_list(self, request):
        if isinstance(request, user_listRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/user_list", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=user_listResponse.typecode.ofwhat, pyclass=user_listResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: search
    def search(self, request):
        if isinstance(request, searchRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/search", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=searchResponse.typecode.ofwhat, pyclass=searchResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response



    # op: create_contact
    def create_contact(self, request):
        if isinstance(request, create_contactRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/create_contact", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=create_contactResponse.typecode.ofwhat, pyclass=create_contactResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: create_lead
    def create_lead(self, request):
        if isinstance(request, create_leadRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/create_lead", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=create_leadResponse.typecode.ofwhat, pyclass=create_leadResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: create_account
    def create_account(self, request):
        if isinstance(request, create_accountRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/create_account", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=create_accountResponse.typecode.ofwhat, pyclass=create_accountResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: create_opportunity
    def create_opportunity(self, request):
        if isinstance(request, create_opportunityRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/create_opportunity", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=create_opportunityResponse.typecode.ofwhat, pyclass=create_opportunityResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: create_case
    def create_case(self, request):
        if isinstance(request, create_caseRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/create_case", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=create_caseResponse.typecode.ofwhat, pyclass=create_caseResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: login
    def login(self, request):       
        if isinstance(request, loginRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/login", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=loginResponse.typecode.ofwhat, pyclass=loginResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: is_loopback
    def is_loopback(self, request):
        if isinstance(request, is_loopbackRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/is_loopback", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=is_loopbackResponse.typecode.ofwhat, pyclass=is_loopbackResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: seamless_login
    def seamless_login(self, request):
        if isinstance(request, seamless_loginRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/seamless_login", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=seamless_loginResponse.typecode.ofwhat, pyclass=seamless_loginResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: get_entry_list
    def get_entry_list(self, request):       
        if isinstance(request, get_entry_listRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/get_entry_list", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=get_entry_listResponse.typecode.ofwhat, pyclass=get_entry_listResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: get_entry
    def get_entry(self, request):
        if isinstance(request, get_entryRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/get_entry", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=get_entryResponse.typecode.ofwhat, pyclass=get_entryResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: get_entries
    def get_entries(self, request):
        if isinstance(request, get_entriesRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/get_entries", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=get_entriesResponse.typecode.ofwhat, pyclass=get_entriesResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: set_entry
    def set_entry(self, request):
        if isinstance(request, set_entryRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/set_entry", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=set_entryResponse.typecode.ofwhat, pyclass=set_entryResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: set_entries
    def set_entries(self, request):
        if isinstance(request, set_entriesRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/set_entries", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=set_entriesResponse.typecode.ofwhat, pyclass=set_entriesResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: set_note_attachment


    # op: relate_note_to_module
    def relate_note_to_module(self, request):
        if isinstance(request, relate_note_to_moduleRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/relate_note_to_module", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=relate_note_to_moduleResponse.typecode.ofwhat, pyclass=relate_note_to_moduleResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: get_related_notes
    def get_related_notes(self, request):
        if isinstance(request, get_related_notesRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/get_related_notes", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=get_related_notesResponse.typecode.ofwhat, pyclass=get_related_notesResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: logout
    def logout(self, request):
        if isinstance(request, logoutRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/logout", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=logoutResponse.typecode.ofwhat, pyclass=logoutResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: get_module_fields
    def get_module_fields(self, request):
        if isinstance(request, get_module_fieldsRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/get_module_fields", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=get_module_fieldsResponse.typecode.ofwhat, pyclass=get_module_fieldsResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: get_available_modules
    def get_available_modules(self, request):
        if isinstance(request, get_available_modulesRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/get_available_modules", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=get_available_modulesResponse.typecode.ofwhat, pyclass=get_available_modulesResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: update_portal_user
    def update_portal_user(self, request):
        if isinstance(request, update_portal_userRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/update_portal_user", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=update_portal_userResponse.typecode.ofwhat, pyclass=update_portal_userResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: test
    def test(self, request):
        if isinstance(request, testRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/test", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=testResponse.typecode.ofwhat, pyclass=testResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: get_user_id
    def get_user_id(self, request):
        if isinstance(request, get_user_idRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/get_user_id", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=get_user_idResponse.typecode.ofwhat, pyclass=get_user_idResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: get_user_team_id
    def get_user_team_id(self, request):
        if isinstance(request, get_user_team_idRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/get_user_team_id", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=get_user_team_idResponse.typecode.ofwhat, pyclass=get_user_team_idResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: get_server_time
    def get_server_time(self, request):
        if isinstance(request, get_server_timeRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/get_server_time", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=get_server_timeResponse.typecode.ofwhat, pyclass=get_server_timeResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: get_gmt_time
    def get_gmt_time(self, request):
        if isinstance(request, get_gmt_timeRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/get_gmt_time", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=get_gmt_timeResponse.typecode.ofwhat, pyclass=get_gmt_timeResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response


    # op: get_relationships
    def get_relationships(self, request):
        if isinstance(request, get_relationshipsRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/get_relationships", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=get_relationshipsResponse.typecode.ofwhat, pyclass=get_relationshipsResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: set_relationship
    def set_relationship(self, request):
        if isinstance(request, set_relationshipRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/set_relationship", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=set_relationshipResponse.typecode.ofwhat, pyclass=set_relationshipResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: set_relationships
    def set_relationships(self, request):
        if isinstance(request, set_relationshipsRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/set_relationships", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=set_relationshipsResponse.typecode.ofwhat, pyclass=set_relationshipsResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response



    # op: search_by_module
    def search_by_module(self, request):
        if isinstance(request, search_by_moduleRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/search_by_module", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=search_by_moduleResponse.typecode.ofwhat, pyclass=search_by_moduleResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

    # op: get_mailmerge_document
    def get_mailmerge_document(self, request):
        if isinstance(request, get_mailmerge_documentRequest) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        kw = {}
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://192.168.0.7/sugarcrm/soap.php/get_mailmerge_document", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=get_mailmerge_documentResponse.typecode.ofwhat, pyclass=get_mailmerge_documentResponse.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response



class create_sessionRequest:
    def __init__(self):
        self._user_name = None
        self._password = None
        return
create_sessionRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","create_session"), ofwhat=[ZSI.TC.String(pname="user_name", aname="_user_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="password", aname="_password", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=create_sessionRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class create_sessionResponse:
    def __init__(self):
        self._return = None
        return
create_sessionResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","create_sessionResponse"), ofwhat=[ZSI.TC.String(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=create_sessionResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class end_sessionRequest:
    def __init__(self):
        self._user_name = None
        return
end_sessionRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","end_session"), ofwhat=[ZSI.TC.String(pname="user_name", aname="_user_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=end_sessionRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class end_sessionResponse:
    def __init__(self):
        self._return = None
        return
end_sessionResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","end_sessionResponse"), ofwhat=[ZSI.TC.String(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=end_sessionResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class contact_by_emailRequest:
    def __init__(self):
        self._user_name = None
        self._password = None
        self._email_address = None
        return
contact_by_emailRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","contact_by_email"), ofwhat=[ZSI.TC.String(pname="user_name", aname="_user_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="password", aname="_password", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="email_address", aname="_email_address", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=contact_by_emailRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class contact_by_emailResponse:
    def __init__(self):
        self._return = None
        return
contact_by_emailResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","contact_by_emailResponse"), ofwhat=[ns0.contact_detail_array_Def(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=contact_by_emailResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class user_listRequest:
    def __init__(self):
        self._user_name = None
        self._password = None
        return
user_listRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","user_list"), ofwhat=[ZSI.TC.String(pname="user_name", aname="_user_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="password", aname="_password", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=user_listRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class user_listResponse:
    def __init__(self):
        self._return = None
        return
user_listResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","user_listResponse"), ofwhat=[ns0.user_detail_array_Def(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=user_listResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class searchRequest:
    def __init__(self):
        self._user_name = None
        self._password = None
        self._name = None
        return
searchRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","search"), ofwhat=[ZSI.TC.String(pname="user_name", aname="_user_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="password", aname="_password", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="name", aname="_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=searchRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class searchResponse:
    def __init__(self):
        self._return = None
        return
searchResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","searchResponse"), ofwhat=[ns0.contact_detail_array_Def(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=searchResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class track_emailRequest:
    def __init__(self):
        self._user_name = None
        self._password = None
        self._parent_id = None
        self._contact_ids = None
        self._date_sent = None
        self._email_subject = None
        self._email_body = None
        return
track_emailRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","track_email"), ofwhat=[ZSI.TC.String(pname="user_name", aname="_user_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="password", aname="_password", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="parent_id", aname="_parent_id", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="contact_ids", aname="_contact_ids", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TCtimes.gDate(pname="date_sent", aname="_date_sent", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="email_subject", aname="_email_subject", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="email_body", aname="_email_body", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=track_emailRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class track_emailResponse:
    def __init__(self):
        self._return = None
        return
track_emailResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","track_emailResponse"), ofwhat=[ZSI.TC.String(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=track_emailResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class create_contactRequest:
    def __init__(self):
        self._user_name = None
        self._password = None
        self._first_name = None
        self._last_name = None
        self._email_address = None
        return
create_contactRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","create_contact"), ofwhat=[ZSI.TC.String(pname="user_name", aname="_user_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="password", aname="_password", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="first_name", aname="_first_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="last_name", aname="_last_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="email_address", aname="_email_address", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=create_contactRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class create_contactResponse:
    def __init__(self):
        self._return = None
        return
create_contactResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","create_contactResponse"), ofwhat=[ZSI.TC.String(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=create_contactResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class create_leadRequest:
    def __init__(self):
        self._user_name = None
        self._password = None
        self._first_name = None
        self._last_name = None
        self._email_address = None
        return
create_leadRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","create_lead"), ofwhat=[ZSI.TC.String(pname="user_name", aname="_user_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="password", aname="_password", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="first_name", aname="_first_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="last_name", aname="_last_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="email_address", aname="_email_address", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=create_leadRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class create_leadResponse:
    def __init__(self):
        self._return = None
        return
create_leadResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","create_leadResponse"), ofwhat=[ZSI.TC.String(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=create_leadResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class create_accountRequest:
    def __init__(self):
        self._user_name = None
        self._password = None
        self._name = None
        self._phone = None
        self._website = None
        return
create_accountRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","create_account"), ofwhat=[ZSI.TC.String(pname="user_name", aname="_user_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="password", aname="_password", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="name", aname="_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="phone", aname="_phone", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="website", aname="_website", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=create_accountRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class create_accountResponse:
    def __init__(self):
        self._return = None
        return
create_accountResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","create_accountResponse"), ofwhat=[ZSI.TC.String(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=create_accountResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class create_opportunityRequest:
    def __init__(self):
        self._user_name = None
        self._password = None
        self._name = None
        self._amount = None
        return
create_opportunityRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","create_opportunity"), ofwhat=[ZSI.TC.String(pname="user_name", aname="_user_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="password", aname="_password", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="name", aname="_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="amount", aname="_amount", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=create_opportunityRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class create_opportunityResponse:
    def __init__(self):
        self._return = None
        return
create_opportunityResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","create_opportunityResponse"), ofwhat=[ZSI.TC.String(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=create_opportunityResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class create_caseRequest:
    def __init__(self):
        self._user_name = None
        self._password = None
        self._name = None
        return
create_caseRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","create_case"), ofwhat=[ZSI.TC.String(pname="user_name", aname="_user_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="password", aname="_password", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="name", aname="_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=create_caseRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class create_caseResponse:
    def __init__(self):
        self._return = None
        return
create_caseResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","create_caseResponse"), ofwhat=[ZSI.TC.String(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=create_caseResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class loginRequest:
    def __init__(self):
        self._user_auth = None
        self._application_name = None
        return
loginRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","login"), ofwhat=[ns0.user_auth_Def(pname="user_auth", aname="_user_auth", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="application_name", aname="_application_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=loginRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class loginResponse:
    def __init__(self):
        self._return = None
        return
loginResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","loginResponse"), ofwhat=[ns0.set_entry_result_Def(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=loginResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class is_loopbackRequest:
    def __init__(self):
        return
is_loopbackRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","is_loopback"), ofwhat=[], pyclass=is_loopbackRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class is_loopbackResponse:
    def __init__(self):
        self._return = None
        return
is_loopbackResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","is_loopbackResponse"), ofwhat=[ZSI.TCnumbers.Iint(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=is_loopbackResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class seamless_loginRequest:
    def __init__(self):
        self._session = None
        return
seamless_loginRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","seamless_login"), ofwhat=[ZSI.TC.String(pname="session", aname="_session", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=seamless_loginRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class seamless_loginResponse:
    def __init__(self):
        self._return = None
        return
seamless_loginResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","seamless_loginResponse"), ofwhat=[ZSI.TCnumbers.Iint(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=seamless_loginResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class get_entry_listRequest:
    def __init__(self):
        self._session = None
        self._module_name = None
        self._query = None
        self._order_by = None
        self._offset = None
        self._select_fields = None
        self._max_results = None
        self._deleted = None
        return
get_entry_listRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_entry_list"), ofwhat=[ZSI.TC.String(pname="session", aname="_session", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="module_name", aname="_module_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="query", aname="_query", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="order_by", aname="_order_by", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TCnumbers.Iint(pname="offset", aname="_offset", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ns0.select_fields_Def(pname="select_fields", aname="_select_fields", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TCnumbers.Iint(pname="max_results", aname="_max_results", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TCnumbers.Iint(pname="deleted", aname="_deleted", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=get_entry_listRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class get_entry_listResponse:
    def __init__(self):
        self._return = None
        return
get_entry_listResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_entry_listResponse"), ofwhat=[ns0.get_entry_list_result_Def(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=get_entry_listResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class get_entryRequest:
    def __init__(self):
        self._session = None
        self._module_name = None
        self._id = None
        self._select_fields = None
        return
get_entryRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_entry"), ofwhat=[ZSI.TC.String(pname="session", aname="_session", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="module_name", aname="_module_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="id", aname="_id", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ns0.select_fields_Def(pname="select_fields", aname="_select_fields", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=get_entryRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class get_entryResponse:
    def __init__(self):
        self._return = None
        return
get_entryResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_entryResponse"), ofwhat=[ns0.get_entry_result_Def(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=get_entryResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class get_entriesRequest:
    def __init__(self):
        self._session = None
        self._module_name = None
        self._ids = None
        self._select_fields = None
        return
get_entriesRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_entries"), ofwhat=[ZSI.TC.String(pname="session", aname="_session", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="module_name", aname="_module_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ns0.select_fields_Def(pname="ids", aname="_ids", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ns0.select_fields_Def(pname="select_fields", aname="_select_fields", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=get_entriesRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class get_entriesResponse:
    def __init__(self):
        self._return = None
        return
get_entriesResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_entriesResponse"), ofwhat=[ns0.get_entry_result_Def(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=get_entriesResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class set_entryRequest:
    def __init__(self):
        self._session = None
        self._module_name = None
        self._name_value_list = None
        return
set_entryRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","set_entry"), ofwhat=[ZSI.TC.String(pname="session", aname="_session", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="module_name", aname="_module_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ns0.name_value_list_Def(pname="name_value_list", aname="_name_value_list", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=set_entryRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class set_entryResponse:
    def __init__(self):
        self._return = None
        return
set_entryResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","set_entryResponse"), ofwhat=[ns0.set_entry_result_Def(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=set_entryResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class set_entriesRequest:
    def __init__(self):
        self._session = None
        self._module_name = None
        self._name_value_lists = None
        return
set_entriesRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","set_entries"), ofwhat=[ZSI.TC.String(pname="session", aname="_session", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="module_name", aname="_module_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ns0.name_value_lists_Def(pname="name_value_lists", aname="_name_value_lists", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=set_entriesRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class set_entriesResponse:
    def __init__(self):
        self._return = None
        return
set_entriesResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","set_entriesResponse"), ofwhat=[ns0.set_entries_result_Def(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=set_entriesResponse, encoded="http://www.sugarcrm.com/sugarcrm")


class logoutRequest:
    def __init__(self):
        self._session = None
        return
logoutRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","logout"), ofwhat=[ZSI.TC.String(pname="session", aname="_session", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=logoutRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class logoutResponse:
    def __init__(self):
        self._return = None
        return
logoutResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","logoutResponse"), ofwhat=[ns0.error_value_Def(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=logoutResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class get_module_fieldsRequest:
    def __init__(self):
        self._session = None
        self._module_name = None
        return
get_module_fieldsRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_module_fields"), ofwhat=[ZSI.TC.String(pname="session", aname="_session", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="module_name", aname="_module_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=get_module_fieldsRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class get_module_fieldsResponse:
    def __init__(self):
        self._return = None
        return
get_module_fieldsResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_module_fieldsResponse"), ofwhat=[ns0.module_fields_Def(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=get_module_fieldsResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class get_available_modulesRequest:
    def __init__(self):
        self._session = None
        return
get_available_modulesRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_available_modules"), ofwhat=[ZSI.TC.String(pname="session", aname="_session", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=get_available_modulesRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class get_available_modulesResponse:
    def __init__(self):
        self._return = None
        return
get_available_modulesResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_available_modulesResponse"), ofwhat=[ns0.module_list_Def(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=get_available_modulesResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class update_portal_userRequest:
    def __init__(self):
        self._session = None
        self._portal_name = None
        self._name_value_list = None
        return
update_portal_userRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","update_portal_user"), ofwhat=[ZSI.TC.String(pname="session", aname="_session", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="portal_name", aname="_portal_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ns0.name_value_list_Def(pname="name_value_list", aname="_name_value_list", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=update_portal_userRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class update_portal_userResponse:
    def __init__(self):
        self._return = None
        return
update_portal_userResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","update_portal_userResponse"), ofwhat=[ns0.error_value_Def(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=update_portal_userResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class testRequest:
    def __init__(self):
        self._string = None
        return
testRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","test"), ofwhat=[ZSI.TC.String(pname="string", aname="_string", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=testRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class testResponse:
    def __init__(self):
        self._return = None
        return
testResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","testResponse"), ofwhat=[ZSI.TC.String(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=testResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class get_user_idRequest:
    def __init__(self):
        self._session = None
        return
get_user_idRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_user_id"), ofwhat=[ZSI.TC.String(pname="session", aname="_session", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=get_user_idRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class get_user_idResponse:
    def __init__(self):
        self._return = None
        return
get_user_idResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_user_idResponse"), ofwhat=[ZSI.TC.String(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=get_user_idResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class get_user_team_idRequest:
    def __init__(self):
        self._session = None
        return
get_user_team_idRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_user_team_id"), ofwhat=[ZSI.TC.String(pname="session", aname="_session", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=get_user_team_idRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class get_user_team_idResponse:
    def __init__(self):
        self._return = None
        return
get_user_team_idResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_user_team_idResponse"), ofwhat=[ZSI.TC.String(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=get_user_team_idResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class get_server_timeRequest:
    def __init__(self):
        return
get_server_timeRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_server_time"), ofwhat=[], pyclass=get_server_timeRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class get_server_timeResponse:
    def __init__(self):
        self._return = None
        return
get_server_timeResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_server_timeResponse"), ofwhat=[ZSI.TC.String(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=get_server_timeResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class get_gmt_timeRequest:
    def __init__(self):
        return
get_gmt_timeRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_gmt_time"), ofwhat=[], pyclass=get_gmt_timeRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class get_gmt_timeResponse:
    def __init__(self):
        self._return = None
        return
get_gmt_timeResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_gmt_timeResponse"), ofwhat=[ZSI.TC.String(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=get_gmt_timeResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class get_sugar_flavorRequest:
    def __init__(self):
        return
get_sugar_flavorRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_sugar_flavor"), ofwhat=[], pyclass=get_sugar_flavorRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class get_sugar_flavorResponse:
    def __init__(self):
        self._return = None
        return
get_sugar_flavorResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_sugar_flavorResponse"), ofwhat=[ZSI.TC.String(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=get_sugar_flavorResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class get_server_versionRequest:
    def __init__(self):
        return
get_server_versionRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_server_version"), ofwhat=[], pyclass=get_server_versionRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class get_server_versionResponse:
    def __init__(self):
        self._return = None
        return
get_server_versionResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_server_versionResponse"), ofwhat=[ZSI.TC.String(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=get_server_versionResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class get_relationshipsRequest:
    def __init__(self):
        self._session = None
        self._module_name = None
        self._module_id = None
        self._related_module = None
        self._related_module_query = None
        self._deleted = None
        return
get_relationshipsRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_relationships"), ofwhat=[ZSI.TC.String(pname="session", aname="_session", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="module_name", aname="_module_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="module_id", aname="_module_id", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="related_module", aname="_related_module", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="related_module_query", aname="_related_module_query", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TCnumbers.Iint(pname="deleted", aname="_deleted", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=get_relationshipsRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class get_relationshipsResponse:
    def __init__(self):
        self._return = None
        return
get_relationshipsResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_relationshipsResponse"), ofwhat=[ns0.get_relationships_result_Def(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=get_relationshipsResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class set_relationshipRequest:
    def __init__(self):
        self._session = None
        self._set_relationship_value = None
        return
set_relationshipRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","set_relationship"), ofwhat=[ZSI.TC.String(pname="session", aname="_session", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ns0.set_relationship_value_Def(pname="set_relationship_value", aname="_set_relationship_value", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=set_relationshipRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class set_relationshipResponse:
    def __init__(self):
        self._return = None
        return
set_relationshipResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","set_relationshipResponse"), ofwhat=[ns0.error_value_Def(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=set_relationshipResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class set_relationshipsRequest:
    def __init__(self):
        self._session = None
        self._set_relationship_list = None
        return
set_relationshipsRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","set_relationships"), ofwhat=[ZSI.TC.String(pname="session", aname="_session", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ns0.set_relationship_list_Def(pname="set_relationship_list", aname="_set_relationship_list", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=set_relationshipsRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class set_relationshipsResponse:
    def __init__(self):
        self._return = None
        return
set_relationshipsResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","set_relationshipsResponse"), ofwhat=[ns0.set_relationship_list_result_Def(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=set_relationshipsResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class set_document_revisionRequest:
    def __init__(self):
        self._session = None
        self._note = None
        return
set_document_revisionRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","set_document_revision"), ofwhat=[ZSI.TC.String(pname="session", aname="_session", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ns0.document_revision_Def(pname="note", aname="_note", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=set_document_revisionRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class set_document_revisionResponse:
    def __init__(self):
        self._return = None
        return
set_document_revisionResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","set_document_revisionResponse"), ofwhat=[ns0.set_entry_result_Def(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=set_document_revisionResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class search_by_moduleRequest:
    def __init__(self):
        self._user_name = None
        self._password = None
        self._search_string = None
        self._modules = None
        self._offset = None
        self._max_results = None
        return
search_by_moduleRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","search_by_module"), ofwhat=[ZSI.TC.String(pname="user_name", aname="_user_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="password", aname="_password", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="search_string", aname="_search_string", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ns0.select_fields_Def(pname="modules", aname="_modules", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TCnumbers.Iint(pname="offset", aname="_offset", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TCnumbers.Iint(pname="max_results", aname="_max_results", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=search_by_moduleRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class search_by_moduleResponse:
    def __init__(self):
        self._return = None
        return
search_by_moduleResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","search_by_moduleResponse"), ofwhat=[ns0.get_entry_list_result_Def(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=search_by_moduleResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class get_mailmerge_documentRequest:
    def __init__(self):
        self._session = None
        self._file_name = None
        self._fields = None
        return
get_mailmerge_documentRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_mailmerge_document"), ofwhat=[ZSI.TC.String(pname="session", aname="_session", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="file_name", aname="_file_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ns0.select_fields_Def(pname="fields", aname="_fields", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=get_mailmerge_documentRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class get_mailmerge_documentResponse:
    def __init__(self):
        self._return = None
        return
get_mailmerge_documentResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_mailmerge_documentResponse"), ofwhat=[ns0.get_sync_result_encoded_Def(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=get_mailmerge_documentResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class get_document_revisionRequest:
    def __init__(self):
        self._session = None
        self._i = None
        return
get_document_revisionRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_document_revision"), ofwhat=[ZSI.TC.String(pname="session", aname="_session", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="i", aname="_i", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=get_document_revisionRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class get_document_revisionResponse:
    def __init__(self):
        self._return = None
        return
get_document_revisionResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_document_revisionResponse"), ofwhat=[ns0.return_document_revision_Def(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=get_document_revisionResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class set_campaign_mergeRequest:
    def __init__(self):
        self._session = None
        self._targets = None
        self._campaign_id = None
        return
set_campaign_mergeRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","set_campaign_merge"), ofwhat=[ZSI.TC.String(pname="session", aname="_session", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ns0.select_fields_Def(pname="targets", aname="_targets", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="campaign_id", aname="_campaign_id", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=set_campaign_mergeRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class set_campaign_mergeResponse:
    def __init__(self):
        self._return = None
        return
set_campaign_mergeResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","set_campaign_mergeResponse"), ofwhat=[ns0.error_value_Def(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=set_campaign_mergeResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class sync_get_modified_relationshipsRequest:
    def __init__(self):
        self._session = None
        self._module_name = None
        self._related_module = None
        self._from_date = None
        self._to_date = None
        self._offset = None
        self._max_results = None
        self._deleted = None
        self._module_id = None
        self._select_fields = None
        self._ids = None
        self._relationship_name = None
        self._deletion_date = None
        self._php_serialize = None
        return
sync_get_modified_relationshipsRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","sync_get_modified_relationships"), ofwhat=[ZSI.TC.String(pname="session", aname="_session", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="module_name", aname="_module_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="related_module", aname="_related_module", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="from_date", aname="_from_date", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="to_date", aname="_to_date", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TCnumbers.Iint(pname="offset", aname="_offset", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TCnumbers.Iint(pname="max_results", aname="_max_results", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TCnumbers.Iint(pname="deleted", aname="_deleted", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="module_id", aname="_module_id", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ns0.select_fields_Def(pname="select_fields", aname="_select_fields", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ns0.select_fields_Def(pname="ids", aname="_ids", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="relationship_name", aname="_relationship_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="deletion_date", aname="_deletion_date", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TCnumbers.Iint(pname="php_serialize", aname="_php_serialize", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=sync_get_modified_relationshipsRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class sync_get_modified_relationshipsResponse:
    def __init__(self):
        self._return = None
        return
sync_get_modified_relationshipsResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","sync_get_modified_relationshipsResponse"), ofwhat=[ns0.get_entry_list_result_encoded_Def(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=sync_get_modified_relationshipsResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class get_modified_entriesRequest:
    def __init__(self):
        self._session = None
        self._module_name = None
        self._ids = None
        self._select_fields = None
        return
get_modified_entriesRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_modified_entries"), ofwhat=[ZSI.TC.String(pname="session", aname="_session", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="module_name", aname="_module_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ns0.select_fields_Def(pname="ids", aname="_ids", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ns0.select_fields_Def(pname="select_fields", aname="_select_fields", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=get_modified_entriesRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class get_modified_entriesResponse:
    def __init__(self):
        self._return = None
        return
get_modified_entriesResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_modified_entriesResponse"), ofwhat=[ns0.get_sync_result_encoded_Def(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=get_modified_entriesResponse, encoded="http://www.sugarcrm.com/sugarcrm")

class get_attendee_listRequest:
    def __init__(self):
        self._session = None
        self._module_name = None
        self._id = None
        return
get_attendee_listRequest.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_attendee_list"), ofwhat=[ZSI.TC.String(pname="session", aname="_session", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="module_name", aname="_module_name", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="id", aname="_id", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=get_attendee_listRequest, encoded="http://www.sugarcrm.com/sugarcrm")

class get_attendee_listResponse:
    def __init__(self):
        self._return = None
        return
get_attendee_listResponse.typecode = Struct(pname=("http://www.sugarcrm.com/sugarcrm","get_attendee_listResponse"), ofwhat=[ns0.get_sync_result_encoded_Def(pname="return", aname="_return", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=get_attendee_listResponse, encoded="http://www.sugarcrm.com/sugarcrm")


class LoginError(Exception): pass
