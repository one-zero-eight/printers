# encoding: utf-8
# module cups
# from /home/dante/PycharmProjects/printers/.venv/lib64/python3.12/site-packages/cups.cpython-312-x86_64-linux-gnu.so
# by generator 1.147
# no doc
# no imports

# Variables with simple values

CUPS_DEST_FLAGS_CANCELED = 64
CUPS_DEST_FLAGS_CONNECTING = 32
CUPS_DEST_FLAGS_ERROR = 8
CUPS_DEST_FLAGS_MORE = 2
CUPS_DEST_FLAGS_NONE = 0
CUPS_DEST_FLAGS_REMOVED = 4
CUPS_DEST_FLAGS_RESOLVING = 16
CUPS_DEST_FLAGS_UNCONNECTED = 1

CUPS_FORMAT_AUTO = 'application/octet-stream'
CUPS_FORMAT_COMMAND = 'application/vnd.cups-command'
CUPS_FORMAT_PDF = 'application/pdf'
CUPS_FORMAT_POSTSCRIPT = 'application/postscript'
CUPS_FORMAT_RAW = 'application/vnd.cups-raw'
CUPS_FORMAT_TEXT = 'text/plain'

CUPS_PRINTER_AUTHENTICATED = 4194304
CUPS_PRINTER_BIND = 1024
CUPS_PRINTER_BW = 4
CUPS_PRINTER_CLASS = 1
CUPS_PRINTER_COLLATE = 128
CUPS_PRINTER_COLOR = 8
CUPS_PRINTER_COMMANDS = 8388608
CUPS_PRINTER_COPIES = 64
CUPS_PRINTER_COVER = 512
CUPS_PRINTER_DEFAULT = 131072
CUPS_PRINTER_DELETE = 1048576
CUPS_PRINTER_DISCOVERED = 16777216
CUPS_PRINTER_DUPLEX = 16
CUPS_PRINTER_FAX = 262144
CUPS_PRINTER_IMPLICIT = 65536
CUPS_PRINTER_LARGE = 16384
CUPS_PRINTER_LOCAL = 0
CUPS_PRINTER_MEDIUM = 8192

CUPS_PRINTER_NOT_SHARED = 2097152

CUPS_PRINTER_OPTIONS = 458748
CUPS_PRINTER_PUNCH = 256
CUPS_PRINTER_REJECTING = 524288
CUPS_PRINTER_REMOTE = 2
CUPS_PRINTER_SMALL = 4096
CUPS_PRINTER_SORT = 2048
CUPS_PRINTER_STAPLE = 32
CUPS_PRINTER_VARIABLE = 32768

CUPS_SERVER_DEBUG_LOGGING = '_debug_logging'

CUPS_SERVER_REMOTE_ADMIN = '_remote_admin'
CUPS_SERVER_REMOTE_ANY = '_remote_any'
CUPS_SERVER_REMOTE_PRINTERS = '_remote_printers'

CUPS_SERVER_SHARE_PRINTERS = '_share_printers'

CUPS_SERVER_USER_CANCEL_ANY = '_user_cancel_any'

HTTP_AUTHORIZATION_CANCELED = 1000

HTTP_BAD_GATEWAY = 502
HTTP_BAD_REQUEST = 400

HTTP_ENCRYPT_ALWAYS = 3

HTTP_ENCRYPT_IF_REQUESTED = 0

HTTP_ENCRYPT_NEVER = 1
HTTP_ENCRYPT_REQUIRED = 2

HTTP_ERROR = -1
HTTP_FORBIDDEN = 403

HTTP_GATEWAY_TIMEOUT = 504

HTTP_NOT_FOUND = 404
HTTP_NOT_IMPLEMENTED = 501
HTTP_NOT_MODIFIED = 304
HTTP_NOT_SUPPORTED = 505

HTTP_OK = 200

HTTP_PKI_ERROR = 1001

HTTP_REQUEST_TIMEOUT = 408

HTTP_SERVER_ERROR = 500

HTTP_SERVICE_UNAVAILABLE = 503

HTTP_STATUS_BAD_GATEWAY = 502
HTTP_STATUS_BAD_REQUEST = 400

HTTP_STATUS_CUPS_AUTHORIZATION_CANCELED = 1000

HTTP_STATUS_CUPS_PKI_ERROR = 1001

HTTP_STATUS_ERROR = -1
HTTP_STATUS_FORBIDDEN = 403

HTTP_STATUS_GATEWAY_TIMEOUT = 504

HTTP_STATUS_NOT_FOUND = 404
HTTP_STATUS_NOT_IMPLEMENTED = 501
HTTP_STATUS_NOT_MODIFIED = 304
HTTP_STATUS_NOT_SUPPORTED = 505

HTTP_STATUS_OK = 200

HTTP_STATUS_REQUEST_TIMEOUT = 408

HTTP_STATUS_SERVER_ERROR = 500

HTTP_STATUS_SERVICE_UNAVAILABLE = 503

HTTP_STATUS_UNAUTHORIZED = 401

HTTP_STATUS_UPGRADE_REQUIRED = 426

HTTP_UNAUTHORIZED = 401

HTTP_UPGRADE_REQUIRED = 426

IPP_ATTRIBUTE = 2
IPP_ATTRIBUTES = 1035

IPP_ATTRIBUTES_NOT_SETTABLE = 1043

IPP_AUTHENTICATION_CANCELED = 4096

IPP_BAD_REQUEST = 1024

IPP_CHARSET = 1037

IPP_COMPRESSION_ERROR = 1040

IPP_COMPRESSION_NOT_SUPPORTED = 1039

IPP_CONFLICT = 1038

IPP_CREATE_JOB_SUBSCRIPTION = 23

IPP_CREATE_PRINTER_SUBSCRIPTION = 22

IPP_DATA = 3

IPP_DEVICE_ERROR = 1284

IPP_DOCUMENT_ACCESS_ERROR = 1042

IPP_DOCUMENT_FORMAT = 1034

IPP_DOCUMENT_FORMAT_ERROR = 1041

IPP_ERROR = -1

IPP_ERROR_JOB_CANCELED = 1288

IPP_FINISHINGS_BALE = 12
IPP_FINISHINGS_BIND = 7

IPP_FINISHINGS_BIND_BOTTOM = 53
IPP_FINISHINGS_BIND_LEFT = 50
IPP_FINISHINGS_BIND_RIGHT = 52
IPP_FINISHINGS_BIND_TOP = 51

IPP_FINISHINGS_BOOKLET_MAKER = 13

IPP_FINISHINGS_COVER = 6

IPP_FINISHINGS_EDGE_STITCH = 9

IPP_FINISHINGS_EDGE_STITCH_BOTTOM = 27
IPP_FINISHINGS_EDGE_STITCH_LEFT = 24
IPP_FINISHINGS_EDGE_STITCH_RIGHT = 26
IPP_FINISHINGS_EDGE_STITCH_TOP = 25

IPP_FINISHINGS_FOLD = 10

IPP_FINISHINGS_JOB_OFFSET = 14

IPP_FINISHINGS_NONE = 3
IPP_FINISHINGS_PUNCH = 5

IPP_FINISHINGS_SADDLE_STITCH = 8

IPP_FINISHINGS_STAPLE = 4

IPP_FINISHINGS_STAPLE_BOTTOM_LEFT = 21
IPP_FINISHINGS_STAPLE_BOTTOM_RIGHT = 23

IPP_FINISHINGS_STAPLE_DUAL_BOTTOM = 31
IPP_FINISHINGS_STAPLE_DUAL_LEFT = 28
IPP_FINISHINGS_STAPLE_DUAL_RIGHT = 30
IPP_FINISHINGS_STAPLE_DUAL_TOP = 29

IPP_FINISHINGS_STAPLE_TOP_LEFT = 20
IPP_FINISHINGS_STAPLE_TOP_RIGHT = 22

IPP_FINISHINGS_TRIM = 11

IPP_FORBIDDEN = 1025
IPP_GONE = 1031
IPP_HEADER = 1
IPP_IDLE = 0

IPP_IGNORED_ALL_NOTIFICATIONS = 1046
IPP_IGNORED_ALL_SUBSCRIPTIONS = 1044

IPP_INTERNAL_ERROR = 1280

IPP_JOB_ABORTED = 8
IPP_JOB_CANCELED = 7
IPP_JOB_COMPLETED = 9
IPP_JOB_HELD = 4
IPP_JOB_PENDING = 3
IPP_JOB_PROCESSING = 5
IPP_JOB_STOPPED = 6

IPP_LANDSCAPE = 4

IPP_MAX_NAME = 256

IPP_MULTIPLE_JOBS_NOT_SUPPORTED = 1289

IPP_NOT_ACCEPTING = 1286
IPP_NOT_AUTHENTICATED = 1026
IPP_NOT_AUTHORIZED = 1027
IPP_NOT_FOUND = 1030
IPP_NOT_POSSIBLE = 1028

IPP_OK = 0

IPP_OK_BUT_CANCEL_SUBSCRIPTION = 6

IPP_OK_CONFLICT = 2

IPP_OK_EVENTS_COMPLETE = 7

IPP_OK_IGNORED_NOTIFICATIONS = 4
IPP_OK_IGNORED_SUBSCRIPTIONS = 3

IPP_OK_SUBST = 1

IPP_OK_TOO_MANY_EVENTS = 5

IPP_OPERATION_NOT_SUPPORTED = 1281

IPP_OP_ACTIVATE_PRINTER = 40

IPP_OP_CANCEL_CURRENT_JOB = 45

IPP_OP_CANCEL_JOB = 8
IPP_OP_CANCEL_JOBS = 56

IPP_OP_CANCEL_MY_JOBS = 57

IPP_OP_CANCEL_SUBSCRIPTION = 27

IPP_OP_CLOSE_JOB = 59

IPP_OP_CREATE_JOB = 5

IPP_OP_CREATE_JOB_SUBSCRIPTIONS = 23

IPP_OP_CREATE_PRINTER_SUBSCRIPTIONS = 22

IPP_OP_CUPS_ACCEPT_JOBS = 16392

IPP_OP_CUPS_ADD_MODIFY_CLASS = 16390
IPP_OP_CUPS_ADD_MODIFY_PRINTER = 16387

IPP_OP_CUPS_AUTHENTICATE_JOB = 16398

IPP_OP_CUPS_DELETE_CLASS = 16391
IPP_OP_CUPS_DELETE_PRINTER = 16388

IPP_OP_CUPS_GET_CLASSES = 16389
IPP_OP_CUPS_GET_DEFAULT = 16385
IPP_OP_CUPS_GET_DOCUMENT = 16423
IPP_OP_CUPS_GET_PPD = 16399
IPP_OP_CUPS_GET_PPDS = 16396
IPP_OP_CUPS_GET_PRINTERS = 16386

IPP_OP_CUPS_MOVE_JOB = 16397

IPP_OP_CUPS_REJECT_JOBS = 16393

IPP_OP_CUPS_SET_DEFAULT = 16394

IPP_OP_DEACTIVATE_PRINTER = 39

IPP_OP_DISABLE_PRINTER = 35

IPP_OP_ENABLE_PRINTER = 34

IPP_OP_GET_JOBS = 10

IPP_OP_GET_JOB_ATTRIBUTES = 9

IPP_OP_GET_NOTIFICATIONS = 28

IPP_OP_GET_PRINTER_ATTRIBUTES = 11

IPP_OP_GET_PRINTER_SUPPORTED_VALUES = 21

IPP_OP_GET_PRINT_SUPPORT_FILES = 33

IPP_OP_GET_RESOURCES = 32

IPP_OP_GET_RESOURCE_ATTRIBUTES = 30
IPP_OP_GET_RESOURCE_DATA = 31

IPP_OP_GET_SUBSCRIPTIONS = 25

IPP_OP_HOLD_JOB = 12

IPP_OP_HOLD_NEW_JOBS = 37

IPP_OP_IDENTIFY_PRINTER = 60

IPP_OP_PAUSE_PRINTER = 16

IPP_OP_PAUSE_PRINTER_AFTER_CURRENT_JOB = 36

IPP_OP_PRINT_JOB = 2
IPP_OP_PRINT_URI = 3

IPP_OP_PROMOTE_JOB = 48

IPP_OP_PURGE_JOBS = 18

IPP_OP_RELEASE_HELD_NEW_JOBS = 38

IPP_OP_RELEASE_JOB = 13

IPP_OP_RENEW_SUBSCRIPTION = 26

IPP_OP_REPROCESS_JOB = 44

IPP_OP_RESTART_JOB = 14
IPP_OP_RESTART_PRINTER = 41

IPP_OP_RESUBMIT_JOB = 58

IPP_OP_RESUME_JOB = 47
IPP_OP_RESUME_PRINTER = 17

IPP_OP_SCHEDULE_JOB_AFTER = 49

IPP_OP_SEND_DOCUMENT = 6

IPP_OP_SEND_HARDCOPY_DOCUMENT = 62

IPP_OP_SEND_NOTIFICATIONS = 29
IPP_OP_SEND_URI = 7

IPP_OP_SET_JOB_ATTRIBUTES = 20

IPP_OP_SET_PRINTER_ATTRIBUTES = 19

IPP_OP_SHUTDOWN_PRINTER = 42

IPP_OP_STARTUP_PRINTER = 43

IPP_OP_SUSPEND_CURRENT_JOB = 46

IPP_OP_VALIDATE_DOCUMENT = 61
IPP_OP_VALIDATE_JOB = 4

IPP_ORIENT_LANDSCAPE = 4
IPP_ORIENT_PORTRAIT = 3

IPP_ORIENT_REVERSE_LANDSCAPE = 5
IPP_ORIENT_REVERSE_PORTRAIT = 6

IPP_PKI_ERROR = 4097

IPP_PORTRAIT = 3

IPP_PRINTER_BUSY = 1287
IPP_PRINTER_IDLE = 3

IPP_PRINTER_IS_DEACTIVATED = 1290

IPP_PRINTER_PROCESSING = 4
IPP_PRINTER_STOPPED = 5

IPP_PRINT_SUPPORT_FILE_NOT_FOUND = 1047

IPP_QUALITY_DRAFT = 3
IPP_QUALITY_HIGH = 5
IPP_QUALITY_NORMAL = 4

IPP_REDIRECTION_OTHER_SITE = 512

IPP_REQUEST_ENTITY = 1032
IPP_REQUEST_VALUE = 1033

IPP_RES_PER_CM = 4
IPP_RES_PER_INCH = 3

IPP_REVERSE_LANDSCAPE = 5
IPP_REVERSE_PORTRAIT = 6

IPP_SERVICE_UNAVAILABLE = 1282

IPP_STATE_ATTRIBUTE = 2
IPP_STATE_DATA = 3
IPP_STATE_ERROR = -1
IPP_STATE_HEADER = 1
IPP_STATE_IDLE = 0

IPP_STATUS_ERROR_ATTRIBUTES_NOT_SETTABLE = 1043

IPP_STATUS_ERROR_ATTRIBUTES_OR_VALUES = 1035

IPP_STATUS_ERROR_BAD_REQUEST = 1024

IPP_STATUS_ERROR_BUSY = 1287
IPP_STATUS_ERROR_CHARSET = 1037

IPP_STATUS_ERROR_COMPRESSION_ERROR = 1040

IPP_STATUS_ERROR_COMPRESSION_NOT_SUPPORTED = 1039

IPP_STATUS_ERROR_CONFLICTING = 1038

IPP_STATUS_ERROR_CUPS_AUTHENTICATION_CANCELED = 4096

IPP_STATUS_ERROR_CUPS_PKI = 4097

IPP_STATUS_ERROR_CUPS_UPGRADE_REQUIRED = 4098

IPP_STATUS_ERROR_DEVICE = 1284

IPP_STATUS_ERROR_DOCUMENT_ACCESS = 1042

IPP_STATUS_ERROR_DOCUMENT_FORMAT_ERROR = 1041

IPP_STATUS_ERROR_DOCUMENT_FORMAT_NOT_SUPPORTED = 1034

IPP_STATUS_ERROR_FORBIDDEN = 1025
IPP_STATUS_ERROR_GONE = 1031

IPP_STATUS_ERROR_IGNORED_ALL_NOTIFICATIONS = 1046
IPP_STATUS_ERROR_IGNORED_ALL_SUBSCRIPTIONS = 1044

IPP_STATUS_ERROR_INTERNAL = 1280

IPP_STATUS_ERROR_JOB_CANCELED = 1288

IPP_STATUS_ERROR_MULTIPLE_JOBS_NOT_SUPPORTED = 1289

IPP_STATUS_ERROR_NOT_ACCEPTING_JOBS = 1286

IPP_STATUS_ERROR_NOT_AUTHENTICATED = 1026
IPP_STATUS_ERROR_NOT_AUTHORIZED = 1027
IPP_STATUS_ERROR_NOT_FOUND = 1030
IPP_STATUS_ERROR_NOT_POSSIBLE = 1028

IPP_STATUS_ERROR_OPERATION_NOT_SUPPORTED = 1281

IPP_STATUS_ERROR_PRINTER_IS_DEACTIVATED = 1290

IPP_STATUS_ERROR_PRINT_SUPPORT_FILE_NOT_FOUND = 1047

IPP_STATUS_ERROR_REQUEST_ENTITY = 1032
IPP_STATUS_ERROR_REQUEST_VALUE = 1033

IPP_STATUS_ERROR_SERVICE_UNAVAILABLE = 1282

IPP_STATUS_ERROR_TEMPORARY = 1285
IPP_STATUS_ERROR_TIMEOUT = 1029

IPP_STATUS_ERROR_TOO_MANY_SUBSCRIPTIONS = 1045

IPP_STATUS_ERROR_URI_SCHEME = 1036

IPP_STATUS_ERROR_VERSION_NOT_SUPPORTED = 1283

IPP_STATUS_OK = 0

IPP_STATUS_OK_BUT_CANCEL_SUBSCRIPTION = 6

IPP_STATUS_OK_CONFLICTING = 2

IPP_STATUS_OK_EVENTS_COMPLETE = 7

IPP_STATUS_OK_IGNORED_NOTIFICATIONS = 4

IPP_STATUS_OK_IGNORED_OR_SUBSTITUTED = 1

IPP_STATUS_OK_IGNORED_SUBSCRIPTIONS = 3

IPP_STATUS_OK_TOO_MANY_EVENTS = 5

IPP_STATUS_REDIRECTION_OTHER_SITE = 512

IPP_TAG_BOOLEAN = 34
IPP_TAG_CHARSET = 71
IPP_TAG_ENUM = 35
IPP_TAG_INTEGER = 33
IPP_TAG_JOB = 2
IPP_TAG_KEYWORD = 68
IPP_TAG_LANGUAGE = 72
IPP_TAG_MIMETYPE = 73
IPP_TAG_NAME = 66
IPP_TAG_OPERATION = 1
IPP_TAG_PRINTER = 4
IPP_TAG_RANGE = 51
IPP_TAG_STRING = 48
IPP_TAG_TEXT = 65
IPP_TAG_URI = 69
IPP_TAG_ZERO = 0

IPP_TEMPORARY_ERROR = 1285

IPP_TIMEOUT = 1029

IPP_TOO_MANY_SUBSCRIPTIONS = 1045

IPP_UPGRADE_REQUIRED = 4098

IPP_URI_SCHEME = 1036

IPP_VERSION_NOT_SUPPORTED = 1283

PPD_CONFORM_RELAXED = 0
PPD_CONFORM_STRICT = 1

PPD_ORDER_ANY = 0
PPD_ORDER_DOCUMENT = 1
PPD_ORDER_EXIT = 2
PPD_ORDER_JCL = 3
PPD_ORDER_PAGE = 4
PPD_ORDER_PROLOG = 5

PPD_UI_BOOLEAN = 0
PPD_UI_PICKMANY = 2
PPD_UI_PICKONE = 1

# functions

def connectDest(dest, cb, flags=0, msec=-1, user_data=None): # real signature unknown; restored from __doc__
    """
    connectDest(dest,cb,flags=0,msec=-1,user_data=None) -> (conn, resource)

    @type dest: Dest object
    @param dest: destination to connect to
    @type cb: callable
    @param cb: callback function, given user_data, dest flags, and dest.
    Should return 1 to continue enumeration and 0 to cancel.
    @type flags: integer
    @param flags: enumeration flags
    @type msec: integer
    @param msec: timeout, or -1 for no timeout
    @type user_data: object
    @param user_data: user data to pass to callback function
    @return: a 2-tuple of the Connection object and the HTTP resource.
    """
    pass

def enumDests(cb, flags=0, msec=-1, type=0, mask=0, user_data=None): # real signature unknown; restored from __doc__
    """
    enumDests(cb,flags=0,msec=-1,type=0,mask=0,user_data=None) -> None

    @type cb: callable
    @param cb: callback function, given user_data, dest flags, and dest.
    Should return 1 to continue enumeration and 0 to cancel.
    @type flags: integer
    @param flags: enumeration flags
    @type msec: integer
    @param msec: timeout, or -1 for no timeout
    @type type: integer
    @param type: bitmask of printer types to return
    @type mask: integer
    @param mask: bitmask of type bits to examine
    @type user_data: object
    @param user_data: user data to pass to callback function
    """
    pass

def getEncryption(): # real signature unknown; restored from __doc__
    """
    getEncryption() -> integer

    Get encryption policy.
    @see: L{setEncryption}
    """
    return 0

def getPort(): # real signature unknown; restored from __doc__
    """
    getPort() -> integer

    @return: IPP port to connect to.
    """
    return 0

def getServer(): # real signature unknown; restored from __doc__
    """
    getServer() -> string

    @return: server to connect to.
    """
    return ""

def getUser(): # real signature unknown; restored from __doc__
    """
    getUser() -> string

    @return: user to connect as.
    """
    return ""

def ippErrorString(statuscode): # real signature unknown; restored from __doc__
    """
    ippErrorString(statuscode) -> name

    @type statuscode: integer
    @param statuscode: IPP Request status code
    @return: a string describing the status code
    """
    pass

def ippOpString(op): # real signature unknown; restored from __doc__
    """
    ippOpString(op) -> name

    @type op: integer
    @param op: IPP Request operation
    @return: a string representing the operation name
    """
    pass

def modelSort(s1, s2): # real signature unknown; restored from __doc__
    """
    modelSort(s1,s2) -> integer

    Sort two model strings.

    @type s1: string
    @param s1: first string
    @type s2: string
    @param s2: second string
    @return: strcmp-style comparison result
    """
    return 0

def ppdSetConformance(level): # real signature unknown; restored from __doc__
    """
    ppdSetConformance(level) -> None

    Set PPD conformance level.

    @type level: integer
    @param level: PPD_CONFORM_RELAXED or PPD_CONFORM_STRICT
    """
    pass

def require(version): # real signature unknown; restored from __doc__
    """
    require(version) -> None

    Require pycups version.

    @type version: string
    @param version: minimum pycups version required
    @raise RuntimeError: requirement not met
    """
    pass

def setEncryption(policy): # real signature unknown; restored from __doc__
    """
    setEncryption(policy) -> None

    Set encryption policy.

    @type policy: integer
    @param policy: L{HTTP_ENCRYPT_ALWAYS}, L{HTTP_ENCRYPT_IF_REQUESTED},
    L{HTTP_ENCRYPT_NEVER}, or L{HTTP_ENCRYPT_REQUIRED}
    """
    pass

def setPasswordCB(fn): # real signature unknown; restored from __doc__
    """
    setPasswordCB(fn) -> None

    Set password callback function.  This Python function will be called
    when a password is required.  It must take one string parameter
    (the password prompt) and it must return a string (the password), or
    None to abort the operation.

    @type fn: callable object
    @param fn: callback function
    """
    pass

def setPasswordCB2(fn, context=None): # real signature unknown; restored from __doc__
    """
    setPasswordCB2(fn, context=None) -> None

    Set password callback function.  This Python function will be called
    when a password is required.  It must take parameters of type string
    (the password prompt), instance (the cups.Connection), string (the
    HTTP method), string (the HTTP resource) and, optionally, the user-
    supplied context.  It must return a string (the password), or None
    to abort the operation.

    @type fn: callable object, or None for default handler
    @param fn: callback function
    """
    pass

def setPort(port): # real signature unknown; restored from __doc__
    """
    setPort(port) -> None

    Set IPP port to connect to.

    @type port: integer
    @param port: IPP port
    """
    pass

def setServer(server): # real signature unknown; restored from __doc__
    """
    setServer(server) -> None

    Set server to connect to.

    @type server: string
    @param server: server hostname
    """
    pass

def setUser(user): # real signature unknown; restored from __doc__
    """
    setUser(user) -> None

    Set user to connect as.

    @type user: string
    @param user: username
    """
    pass

# classes

class Attribute(object):
    """
    PPD attribute
    =============

      A PPD attribute.

    @type name: string
    @ivar name: attribute name
    @type spec: string
    @ivar spec: specifier string (if any)
    @type text: string
    @ivar text: human-readable text (if any)
    @type value: string
    @ivar value: attribute value
    """
    def __init__(self, *args, **kwargs): # real signature unknown
        pass

    @staticmethod # known case of __new__
    def __new__(*args, **kwargs): # real signature unknown
        """ Create and return a new object.  See help(type) for accurate signature. """
        pass

    def __repr__(self, *args, **kwargs): # real signature unknown
        """ Return repr(self). """
        pass

    name = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """name"""

    spec = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """spec"""

    text = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """text"""

    value = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """value"""



class Connection(object):
    """
    CUPS connection
    ===============

      A connection to the CUPS server.  Before it is created the
      connection server and username should be set using
      L{cups.setServer} and L{cups.setUser}; otherwise the defaults will
      be used.  When a Connection object is instantiated it results in a
      call to the libcups function httpConnectEncrypt().

      The constructor takes optional arguments host, port, and encryption,
      which default to the values of L{cups.getServer}(),
      L{cups.getPort}(), and L{cups.getEncryption}().
    """
    def acceptJobs(self, name): # real signature unknown; restored from __doc__
        """
        acceptJobs(name) -> None

        Cause printer to accept jobs.
        @type name: string
        @param name: queue name
        @raise IPPError: IPP problem
        """
        pass

    def addPrinter(self, name): # real signature unknown; restored from __doc__
        """
        addPrinter(name) -> None

        Add or adjust a print queue.  Several parameters can select which
        PPD to use (filename, ppdname, and ppd) but only one may be
        given.

        @type filename: string
        @keyword filename: local filename of PPD file
        @type ppdname: string
        @keyword ppdname: filename from L{getPPDs}
        @type info: string
        @keyword info: human-readable information about the printer
        @type location: string
        @keyword location: human-readable printer location
        @type device: string
        @keyword device: device URI string
        @type ppd: L{cups.PPD} instance
        @keyword ppd: PPD object
        @raise IPPError: IPP problem
        """
        pass

    def addPrinterOptionDefault(self, name, option, value): # real signature unknown; restored from __doc__
        """
        addPrinterOptionDefault(name, option, value) -> None

        Set a network default option.  Jobs submitted to the named queue
        will have the job option added if it is not already present in the
        job.  This works with CUPS servers of at least version 1.2.

        @type name: string
        @param name: queue name
        @type option: string
        @param option: option name, for example 'job-priority'
        @type value: string
        @param value: option value as a string
        @raise IPPError: IPP problem
        """
        pass

    def addPrinterToClass(self, name, p_class): # real signature unknown; restored from __doc__
        """
        addPrinterToClass(name, class) -> None

        Add a printer to a class.  If the class does not yet exist,
        it is created.

        @type name: string
        @param name: queue name
        @type class: string
        @param class: class name
        @raise IPPError: IPP problem
        """
        pass

    def adminExportSamba(self, name, samba_server, samba_username, samba_password): # real signature unknown; restored from __doc__
        """
        adminExportSamba(name, samba_server, samba_username,
                         samba_password) -> None

        Export a printer to Samba.

        @type name: string
        @param name: queue name
        @type samba_server: string
        @param samba_server: samba server
        @type samba_username: string
        @param samba_username: samba username
        @type samba_password: string
        @param samba_password: samba password
        @raise IPPError: IPP problem
        """
        pass

    def adminGetServerSettings(self): # real signature unknown; restored from __doc__
        """
        adminGetServerSettings() -> dict

        Get server settings.

        @return: dict representing server settings; keywords include
        L{CUPS_SERVER_DEBUG_LOGGING}, L{CUPS_SERVER_REMOTE_ADMIN},
        L{CUPS_SERVER_REMOTE_PRINTERS}, L{CUPS_SERVER_SHARE_PRINTERS},
        L{CUPS_SERVER_USER_CANCEL_ANY}
        @see: L{adminSetServerSettings}
        @raise IPPError: IPP problem
        """
        return {}

    def adminSetServerSettings(self, settings): # real signature unknown; restored from __doc__
        """
        adminSetServerSettings(settings) -> None

        Set server settings.

        @type settings: dict
        @param settings: dict of server settings
        @see: L{adminGetServerSettings}
        @raise IPPError: IPP problem
        """
        pass

    def authenticateJob(self, jobid, auth_info=None): # real signature unknown; restored from __doc__
        """
        authenticateJob(jobid, auth_info=None) -> None

        @type jobid: integer
        @param jobid: job ID to authenticate
        @type auth_info: optional string list
        @param auth_info: authentication details
        @raise IPPError: IPP problem
        """
        pass

    def cancelAllJobs(self, name=None, uri=None, my_jobs=False, purge_jobs=True): # real signature unknown; restored from __doc__
        """
        cancelAllJobs(name=None, uri=None, my_jobs=False, purge_jobs=True) -> None

        @type name: string
        @param name: queue name
        @type uri: string
        @param uri: printer URI
        @type my_jobs: boolean
        @param my_jobs: whether to restrict operation to jobs owned by
        the current CUPS user (as set by L{cups.setUser}).
        @type purge_jobs: boolean
        @param purge_jobs: whether to remove data and control files
        @raise IPPError: IPP problem
        """
        pass

    def cancelJob(self, jobid, purge_job=False): # real signature unknown; restored from __doc__
        """
        cancelJob(jobid, purge_job=False) -> None

        @type jobid: integer
        @param jobid: job ID to cancel
        @type purge_job: boolean
        @param purge_job: whether to remove data and control files
        @raise IPPError: IPP problem
        """
        pass

    def cancelSubscription(self, id): # real signature unknown; restored from __doc__
        """
        cancelSubscription(id) -> None

        Cancel a subscription.

        @type id: integer
        @param id: subscription ID
        @raise IPPError: IPP problem
        """
        pass

    def createJob(self, printer, title, options): # real signature unknown; restored from __doc__
        """
        createJob(printer, title, options) -> integer

        Create an empty job for streaming.

        @type printer: string
        @param printer: queue name
        @type title: string
        @param title: title of the print job
        @type options: dict
        @param options: dict of options
        @return: job ID
        @raise IPPError: IPP problem
        """
        return 0

    def createSubscription(self, uri, events=[], job_id=-1, recipient_uri, *args, **kwargs): # real signature unknown; NOTE: unreliably restored from __doc__
        """
        createSubscription(uri, events=[], job_id=-1, recipient_uri=,
                           lease_duration=-1, time_interval=-1,
                           user_data=) -> integer

        Create a subscription.

        @type uri: string
        @param uri: URI for object
        @type events: string list
        @keyword events: events to receive notifications for
        @type job_id: integer
        @keyword job_id: job ID to receive notifications for
        @type recipient_uri: string
        @keyword recipient_uri: URI for notifications recipient
        @type lease_duration: integer
        @keyword lease_duration: lease duration in seconds
        @type time_interval: integer
        @keyword time_interval: time interval
        @type user_data: string
        @keyword user_data: user data to receive with notifications
        @return: subscription ID
        @raise IPPError: IPP problem
        """
        pass

    def deleteClass(self, p_class): # real signature unknown; restored from __doc__
        """
        deleteClass(class) -> None

        Delete a class.

        @type class: string
        @param class: class name
        @raise IPPError: IPP problem
        """
        pass

    def deletePrinter(self, name): # real signature unknown; restored from __doc__
        """
        deletePrinter(name) -> None

        Delete a printer.

        @type name: string
        @param name: queue name
        @raise IPPError: IPP problem
        """
        pass

    def deletePrinterFromClass(self, name, p_class): # real signature unknown; restored from __doc__
        """
        deletePrinterFromClass(name, class) -> None

        Remove a printer from a class.  If the class would be left empty,
        it is removed.

        @type name: string
        @param name: queue name
        @type class: string
        @param class: class name
        @raise IPPError: IPP problem
        """
        pass

    def deletePrinterOptionDefault(self, name, option): # real signature unknown; restored from __doc__
        """
        deletePrinterOptionDefault(name, option) -> None

        Removes a network default option.  See L{addPrinterOptionDefault}.

        @type name: string
        @param name: queue name
        @type option: string
        @param option: option name, for example 'job-priority'
        @raise IPPError: IPP problem
        """
        pass

    def disablePrinter(self, name): # real signature unknown; restored from __doc__
        """
        disablePrinter(name) -> None

        Disable printer.  This prevents the printer from processing its
        job queue.

        @type name: string
        @param name: queue name
        @type reason: string
        @keyword reason: optional human-readable reason for disabling the
        printer
        @raise IPPError: IPP problem
        """
        pass

    def enablePrinter(self, name): # real signature unknown; restored from __doc__
        """
        enablePrinter(name) -> None

        Enable printer.  This allows the printer to process its job queue.

        @type name: string
        @param name: queue name
        @raise IPPError: IPP problem
        """
        pass

    def finishDocument(self, printer): # real signature unknown; restored from __doc__
        """
        finishDocument(printer) -> integer

        Finish sending a document.

        @type printer: string
        @param printer: queue name
        @return: HTTP status
        @raise IPPError: IPP problem
        """
        return 0

    def getClasses(self): # real signature unknown; restored from __doc__
        """
        getClasses() -> dict

        @return: a dict, indexed by name, of objects representing
        classes.  Each class object is either a string, in which case it
        is for the remote class; or a list, in which case it is a list of
        queue names.
        @raise IPPError: IPP problem
        """
        return {}

    def getDefault(self): # real signature unknown; restored from __doc__
        """
        getDefault() -> string or None

        Get the system default printer.

        @return: default printer name or None
        """
        return ""

    def getDests(self): # real signature unknown; restored from __doc__
        """
        getDests() -> dict

        @return: a dict representing available destinations.  Each
        dictionary key is a pair of (queue, instance) strings, and the
        dictionary value is a L{cups.Dest} object.  In addition to the
        available destinations, a special dictionary key (None,None) is
        provided for looking up the default destination; this destination
        will also be available under its own key.
        @raise IPPError: IPP problem
        """
        return {}

    def getDevices(self, limit=0, exclude_schemes=None, include_schemes=None): # real signature unknown; restored from __doc__
        """
        getDevices(limit=0, exclude_schemes=None, include_schemes=None) -> dict

        @type limit: integer
        @param limit: maximum number of devices to return
        @type exclude_schemes: string list
        @param exclude_schemes: URI schemes to exclude
        @type include_schemes: string list
        @param include_schemes: URI schemes to include
        @return: a dict, indexed by device URI, of dicts representing
        devices, indexed by attribute.
        @raise IPPError: IPP problem
        """
        return {}

    def getDocument(self, printer_uri, job_id, document_number): # real signature unknown; restored from __doc__
        """
        getDocument(printer_uri, job_id, document_number) -> dict

        Fetches the job document and stores it in a temporary file.

        @type printer_uri: string
        @param printer_uri: the printer-uri for the printer
        @type job_id: integer
        @param job_id: the job ID
        @type document_number: integer
        @param document_number: the document number to retrieve
        @return: a dict with the following keys:  'file' (string), temporary filename holding the job document;  'document-format' (string), its MIME type.  There may also be a  'document-name' key, in which case this is for the document name.
        @raise RuntimeError: Not supported in libcups until 1.4
        @raise IPPError: IPP problem
        """
        return {}

    def getFile(self, resource, filename=None, fd=-1, file=None): # real signature unknown; restored from __doc__
        """
        getFile(resource, filename=None, fd=-1, file=None) -> None

        Fetch a CUPS server resource to a local file.

        This is for obtaining CUPS server configuration files and
        log files.

        @type resource: string
        @param resource: resource name
        @type filename: string
        @param filename: name of local file for storage
        @type fd: int
        @param fd: file descriptor of local file
        @type file: file
        @param file: Python file object for local file
        @raise HTTPError: HTTP problem
        """
        pass

    def getJobAttributes(self, jobid, requested_attributes=None): # real signature unknown; restored from __doc__
        """
        getJobAttributes(jobid, requested_attributes=None) -> dict

        Fetch job attributes.
        @type jobid: integer
        @param jobid: job ID
        @type requested_attributes: string list
        @param requested_attributes: list of requested attribute names
        @return: a dict representing job attributes.
        @raise IPPError: IPP problem
        """
        return {}

    def getJobs(self, which_jobs='not-completed', my_jobs=False, limit=-1, first_job_id=-1, requested_attributes=None): # real signature unknown; restored from __doc__
        """
        getJobs(which_jobs='not-completed', my_jobs=False, limit=-1, first_job_id=-1, requested_attributes=None) -> dict
        Fetch a list of jobs.
        @type which_jobs: string
        @param which_jobs: which jobs to fetch; possible values:
        'completed', 'not-completed', 'all'
        @type my_jobs: boolean
        @param my_jobs: whether to restrict the returned jobs to those
        owned by the current CUPS user (as set by L{cups.setUser}).
        @return: a dict, indexed by job ID, of dicts representing job
        attributes.
        @type limit: integer
        @param limit: maximum number of jobs to return
        @type first_job_id: integer
        @param first_job_id: lowest job ID to return
        @type requested_attributes: string list
        @param requested_attributes: list of requested attribute names
        @raise IPPError: IPP problem
        """
        return {}

    def getNotifications(self, subscription_ids): # real signature unknown; restored from __doc__
        """
        getNotifications(subscription_ids) -> list

        Get notifications for subscribed events.

        @type subscription_ids: integer list
        @param subscription_ids: list of subscription IDs to receive
        notifications for
        @return: list of dicts, each representing an event
        @raise IPPError: IPP problem
        """
        return []

    def getPPD(self, name): # real signature unknown; restored from __doc__
        """
        getPPD(name) -> string

        Fetch a printer's PPD.

        @type name: string
        @param name: queue name
        @return: temporary PPD file name
        @raise IPPError: IPP problem
        """
        return ""

    def getPPD3(self, name, modtime=None, filename=None): # real signature unknown; restored from __doc__
        """
        getPPD3(name[, modtime, filename]) -> (status,modtime,filename)

        Fetch a printer's PPD if it is newer.

        @type name: string
        @param name: queue name
        @type modtime: float
        @param modtime: modification time of existing file
        @type filename: string
        @param filename: filename of existing file
        @return: tuple of HTTP status, modification time, and filename
        """
        pass

    def getPPDs(self, limit=0, exclude_schemes=None, include_schemes=None, ppd_natural_language=None, ppd_device_id=None, ppd_make=None, ppd_make_and_model=None, ppd_model_number=-1, ppd_product=None, ppd_psversion=None, ppd_type=None): # real signature unknown; restored from __doc__
        """
        getPPDs(limit=0, exclude_schemes=None, include_schemes=None,
        ppd_natural_language=None, ppd_device_id=None, ppd_make=None,
        ppd_make_and_model=None, ppd_model_number=-1, ppd_product=None,
        ppd_psversion=None, ppd_type=None) -> dict

        @type limit: integer
        @param limit: maximum number of PPDs to return
        @type exclude_schemes: string list
        @param exclude_schemes: list of PPD schemes to exclude
        @type include_schemes: string list
        @param include_schemes: list of PPD schemes to include
        @type ppd_natural_language: string
        @param ppd_natural_language: required language
        @type ppd_device_id: string
        @param ppd_device_id: IEEE 1284 Device ID to match against
        @type ppd_make: string
        @param ppd_make: required printer manufacturer
        @type ppd_make_and_model: string
        @param ppd_make_and_model: required make and model
        @type ppd_model_number: integer
        @param ppd_model_number: model number required (from cupsModelNumber
        in PPD file)
        @type ppd_product: string
        @param ppd_product: required PostScript product string (Product)
        @type ppd_psversion: string
        @param ppd_psversion: required PostScript version (PSVersion)
        @type ppd_type: string
        @param ppd_type: required type of PPD. Valid values are fax; pdf;
        postscript; raster; unknown.
        @return: a dict, indexed by PPD name, of dicts representing
        PPDs, indexed by attribute.
        @raise IPPError: IPP problem
        """
        return {}

    def getPPDs2(self, limit=0, exclude_schemes=None, include_schemes=None, ppd_natural_language=None, ppd_device_id=None, ppd_make=None, ppd_make_and_model=None, ppd_model_number=-1, ppd_product=None, ppd_psversion=None, ppd_type=None): # real signature unknown; restored from __doc__
        """
        getPPDs2(limit=0, exclude_schemes=None, include_schemes=None,
        ppd_natural_language=None, ppd_device_id=None, ppd_make=None,
        ppd_make_and_model=None, ppd_model_number=-1, ppd_product=None,
        ppd_psversion=None, ppd_type=None) -> dict

        @type limit: integer
        @param limit: maximum number of PPDs to return
        @type exclude_schemes: string list
        @param exclude_schemes: list of PPD schemes to exclude
        @type include_schemes: string list
        @param include_schemes: list of PPD schemes to include
        @type ppd_natural_language: string
        @param ppd_natural_language: required language
        @type ppd_device_id: string
        @param ppd_device_id: IEEE 1284 Device ID to match against
        @type ppd_make: string
        @param ppd_make: required printer manufacturer
        @type ppd_make_and_model: string
        @param ppd_make_and_model: required make and model
        @type ppd_model_number: integer
        @param ppd_model_number: model number required (from cupsModelNumber
        in PPD file)
        @type ppd_product: string
        @param ppd_product: required PostScript product string (Product)
        @type ppd_psversion: string
        @param ppd_psversion: required PostScript version (PSVersion)
        @type ppd_type: string
        @param ppd_type: required type of PPD. Valid values are fax; pdf;
        postscript; raster; unknown.
        @return: a dict, indexed by PPD name, of dicts representing
        PPDs, indexed by attribute.  All attribute values are lists.
        @raise IPPError: IPP problem
        """
        return {}

    def getPrinterAttributes(self, name=None, uri=None, requested_attributes=None): # real signature unknown; restored from __doc__
        """
        getPrinterAttributes(name=None, uri=None, requested_attributes=None) -> dict
        Fetch the attributes for a printer, specified either by name or by
        uri but not both.

        @type name: string
        @param name: queue name
        @type uri: string
        @param uri: queue URI
        @type requested_attributes: string list
        @param requested_attributes: list of requested attribute names
        @return: a dict, indexed by attribute, of printer attributes
        for the specified printer.

        Attributes:
          - 'job-sheets-supported': list of strings
          - 'job-sheets-default': tuple of strings (start, end)
          - 'printer-error-policy-supported': if present, list of strings
          - 'printer-error-policy': if present, string
          - 'printer-op-policy-supported': if present, list of strings
          - 'printer-op-policy': if present, string

        There are other attributes; the exact list of attributes returned
        will depend on the IPP server.
        @raise IPPError: IPP problem
        """
        return {}

    def getPrinters(self): # real signature unknown; restored from __doc__
        """
        getPrinters() -> dict

        @return: a dict, indexed by name, of dicts representing
        queues, indexed by attribute.
        @raise IPPError: IPP problem
        """
        return {}

    def getServerPPD(self, ppd_name): # real signature unknown; restored from __doc__
        """
        getServerPPD(ppd_name) -> string

        Fetches the named PPD and stores it in a temporary file.

        @type ppd_name: string
        @param ppd_name: the ppd-name of a PPD
        @return: temporary filename holding the PPD
        @raise RuntimeError: Not supported in libcups until 1.3
        @raise IPPError: IPP problem
        """
        return ""

    def getSubscriptions(self, uri): # real signature unknown; restored from __doc__
        """
        getSubscriptions(uri) -> integer list

        Get subscriptions.

        @type uri: string
        @param uri: URI for object
        @type my_subscriptions: boolean
        @keyword my_subscriptions: only return subscriptions belonging to
        the current user (default False)
        @type job_id: integer
        @keyword job_id: only return subscriptions relating to this job
        @return: list of subscriptions
        @raise IPPError: IPP problem
        """
        return 0

    def moveJob(self, printer_uri=None, job_id=-1, job_printer_uri): # real signature unknown; restored from __doc__
        """
        moveJob(printer_uri=None, job_id=-1, job_printer_uri) -> None

        Move a job specified by printer_uri and jobid (only one need be given)
        to the printer specified by job_printer_uri.

        @type job_id: integer
        @param job_id: job ID to move
        @type printer_uri: string
        @param printer_uri: printer to move job(s) from
        @type job_printer_uri: string
        @param job_printer_uri: printer to move job(s) to
        @raise IPPError: IPP problem
        """
        pass

    def printFile(self, printer, filename, title, options): # real signature unknown; restored from __doc__
        """
        printFile(printer, filename, title, options) -> integer

        Print a file.

        @type printer: string
        @param printer: queue name
        @type filename: string
        @param filename: local file path to the document
        @type title: string
        @param title: title of the print job
        @type options: dict
        @param options: dict of options
        @return: job ID
        @raise IPPError: IPP problem
        """
        return 0

    def printFiles(self, printer, filenames, title, options): # real signature unknown; restored from __doc__
        """
        printFiles(printer, filenames, title, options) -> integer

        Print a list of files.

        @type printer: string
        @param printer: queue name
        @type filenames: list
        @param filenames: list of local file paths to the documents
        @type title: string
        @param title: title of the print job
        @type options: dict
        @param options: dict of options
        @return: job ID
        @raise IPPError: IPP problem
        """
        return 0

    def printTestPage(self, name): # real signature unknown; restored from __doc__
        """
        printTestPage(name) -> job ID

        Print a test page.

        @type name: string
        @param name: queue name
        @type file: string
        @keyword file: input file (default is CUPS test page)
        @type title: string
        @keyword title: job title (default 'Test Page')
        @type format: string
        @keyword format: document format (default 'application/postscript')
        @type user: string
        @keyword user: user to submit the job as
        @raise IPPError: IPP problem
        """
        pass

    def putFile(self, resource, filename=None, fd=-1, file=None): # real signature unknown; restored from __doc__
        """
        putFile(resource, filename=None, fd=-1, file=None) -> None

        This is for uploading new configuration files for the CUPS
        server.  Note: L{adminSetServerSettings} is a way of
        adjusting server settings without needing to parse the
        configuration file.
        @type resource: string
        @param resource: resource name
        @type filename: string
        @param filename: name of local file to upload
        @type fd: int
        @param fd: file descriptor of local file
        @type file: file
        @param file: Python file object for local file
        @raise HTTPError: HTTP problem
        """
        pass

    def rejectJobs(self, name): # real signature unknown; restored from __doc__
        """
        rejectJobs(name)

        Cause printer to reject jobs.

        @type name: string
        @param name: queue name
        @type reason: string
        @keyword reason: optional human-readable reason for rejecting jobs
        @raise IPPError: IPP problem
        """
        pass

    def renewSubscription(self, id, lease_duration=-1): # real signature unknown; restored from __doc__
        """
        renewSubscription(id, lease_duration=-1) -> None

        Renew a subscription.

        @type id: integer
        @param id: subscription ID
        @type lease_duration: integer
        @param lease_duration: lease duration in seconds
        @raise IPPError: IPP problem
        """
        pass

    def restartJob(self, job_id, job_hold_until=None): # real signature unknown; restored from __doc__
        """
        restartJob(job_id, job_hold_until=None) -> None

        Restart a job.

        @type job_id: integer
        @param job_id: job ID to restart
        @type job_hold_until: string
        @param job_hold_until: new job-hold-until value for job
        @raise IPPError: IPP problem
        """
        pass

    def setDefault(self, name): # real signature unknown; restored from __doc__
        """
        setDefault(name) -> None

        Set the system default printer.  Note that this can be over-ridden
        on a per-user basis using the lpoptions command.

        @type name: string
        @param name: queue name
        @raise IPPError: IPP problem
        """
        pass

    def setJobHoldUntil(self, jobid, job_hold_until): # real signature unknown; restored from __doc__
        """
        setJobHoldUntil(jobid, job_hold_until) -> None

        Specifies when a job should be printed.
        @type jobid: integer
        @param jobid: job ID to adjust
        @type job_hold_until: string
        @param job_hold_until: when to print the job; examples: 'hold',
        'immediate', 'restart', resume'
        @raise IPPError: IPP problem
        """
        pass

    def setPrinterDevice(self, name, device_uri): # real signature unknown; restored from __doc__
        """
        setPrinterDevice(name, device_uri) -> None

        Set the device URI for a printer.

        @type name: string
        @param name: queue name
        @type device_uri: string
        @param device_uri: device URI
        @raise IPPError: IPP problem
        """
        pass

    def setPrinterErrorPolicy(self, name, policy): # real signature unknown; restored from __doc__
        """
        setPrinterErrorPolicy(name, policy) -> None

        Set the printer's error policy.

        @type name: string
        @param name: queue name
        @type policy: string
        @param policy: policy name; supported policy names can be found
        by using the L{getPrinterAttributes} function and looking for the
        'printer-error-policy-supported' attribute
        @raise IPPError: IPP problem
        """
        pass

    def setPrinterInfo(self, name, info): # real signature unknown; restored from __doc__
        """
        setPrinterInfo(name, info) -> None

        Set the human-readable information about a printer.

        @type name: string
        @param name: queue name
        @type info: string
        @param info: human-readable information about the printer
        @raise IPPError: IPP problem
        """
        pass

    def setPrinterJobSheets(self, name, start, end): # real signature unknown; restored from __doc__
        """
        setPrinterJobSheets(name, start, end) -> None

        Specifies job sheets for a printer.

        @type name: string
        @param name: queue name
        @type start: string
        @param start: name of a sheet to print before each job
        @type end: string
        @param end: name of a sheet to print after each job
        @raise IPPError: IPP problem
        """
        pass

    def setPrinterLocation(self, name, location): # real signature unknown; restored from __doc__
        """
        setPrinterLocation(name, location) -> None

        Set the human-readable printer location

        @type name: string
        @param name: queue name
        @type location: string
        @param location: human-readable printer location
        @raise IPPError: IPP problem
        """
        pass

    def setPrinterOpPolicy(self, name, policy): # real signature unknown; restored from __doc__
        """
        setPrinterOpPolicy(name, policy) -> None

        Set the printer's operation policy.

        @type name: string
        @param name: queue name
        @type policy: string
        @param policy: policy name; supported policy names can be found
        by using the L{getPrinterAttributes} function and looking for the
        'printer-op-policy-supported' attribute
        @raise IPPError: IPP problem
        """
        pass

    def setPrinterShared(self, name, shared): # real signature unknown; restored from __doc__
        """
        setPrinterShared(name, shared) -> None

        Set whether a printer is shared with other people.  This works
        with CUPS servers of at least version 1.2, by setting the
        printer-is-shared printer attribute.

        @type name: string
        @param name: queue name
        @type shared: boolean
        @param shared: whether printer should be shared
        @raise IPPError: IPP problem
        """
        pass

    def setPrinterUsersAllowed(self, name, allowed): # real signature unknown; restored from __doc__
        """
        setPrinterUsersAllowed(name, allowed) -> None

        Set the list of users allowed to use a printer.  This works
        with CUPS server of at least version 1.2, by setting the
        requesting-user-name-allowed printer attribute.

        @type name: string
        @param name: queue name
        @type allowed: string list
        @param allowed: list of allowed users; ['all']
        means there will be no user-name restriction.
        @raise IPPError: IPP problem
        """
        pass

    def setPrinterUsersDenied(self, name, denied): # real signature unknown; restored from __doc__
        """
        setPrinterUsersDenied(name, denied) -> None

        Set the list of users denied the use of a printer.  This works
        with CUPS servers of at least version 1.2, by setting the
        requesting-user-name-denied printer attribute.

        @type name: string
        @param name: queue name
        @type denied: string list
        @param denied: list of denied users; ['none']
        means there will be no user-name restriction.
        @raise IPPError: IPP problem
        """
        pass

    def startDocument(self, printer, job_id, doc_name, format, last_document): # real signature unknown; restored from __doc__
        """
        startDocument(printer, job_id, doc_name, format, last_document) -> integer

        Add a document to a job created with createJob.

        @type printer: string
        @param printer: queue name
        @type job_id: integer
        @param job_id: job ID to create document
        @type doc_name: string
        @param doc_name: name of the document
        @type format: string
        @param format: MIME type
        @type last_document: integer
        @param last_document: 1 for last document of job, 0 otherwise
        @return: HTTP status
        @raise IPPError: IPP problem
        """
        return 0

    def writeRequestData(self, buffer, length): # real signature unknown; restored from __doc__
        """
        writeRequestData(buffer, length) -> integer

        Write data after an IPP request.

        @type buffer: string
        @param buffer: bytes to write
        @type length: integer
        @param length: number of bytes to write
        @return: HTTP status
        @raise IPPError: IPP problem
        """
        return 0

    def __init__(self, *args, **kwargs): # real signature unknown
        pass

    @staticmethod # known case of __new__
    def __new__(*args, **kwargs): # real signature unknown
        """ Create and return a new object.  See help(type) for accurate signature. """
        pass

    def __repr__(self, *args, **kwargs): # real signature unknown
        """ Return repr(self). """
        pass


class Constraint(object):
    """
    PPD constraint
    ==============

      A PPD constraint.

    @type option1: string
    @ivar option1: first option keyword
    @type choice1: string
    @ivar choice1: first option choice
    @type option2: string
    @ivar option2: second option keyword
    @type choice2: string
    @ivar choice2: secondoption choice
    """
    def __init__(self, *args, **kwargs): # real signature unknown
        pass

    @staticmethod # known case of __new__
    def __new__(*args, **kwargs): # real signature unknown
        """ Create and return a new object.  See help(type) for accurate signature. """
        pass

    choice1 = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """choice1"""

    choice2 = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """choice2"""

    option1 = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """option1"""

    option2 = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """option2"""



class Dest(object):
    """
    CUPS destination
    ================

      A destination print queue, as returned by L{Connection.getDests}.

    @type name: string
    @ivar name: destination queue name
    @type instance: string
    @ivar instance: destination instance name
    @type is_default: boolean
    @ivar is_default: whether this is the default destination
    @type options: dict
    @ivar options: string:string dict of default options for this
    destination, indexed by option name
    """
    def __init__(self, *args, **kwargs): # real signature unknown
        pass

    @staticmethod # known case of __new__
    def __new__(*args, **kwargs): # real signature unknown
        """ Create and return a new object.  See help(type) for accurate signature. """
        pass

    def __repr__(self, *args, **kwargs): # real signature unknown
        """ Return repr(self). """
        pass

    instance = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """instance"""

    is_default = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """is_default"""

    name = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """name"""

    options = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """options"""



class Group(object):
    """
    PPD option group
    ================

      A PPD option group.

    @type text: string
    @ivar text: user-presentable group name
    @type name: string
    @ivar name: unique group name
    @type options: L{Option} list
    @ivar options: list of options in the group
    @type subgroups: L{Group} list
    @ivar subgroups: list of subgroups in the group
    """
    def __init__(self, *args, **kwargs): # real signature unknown
        pass

    @staticmethod # known case of __new__
    def __new__(*args, **kwargs): # real signature unknown
        """ Create and return a new object.  See help(type) for accurate signature. """
        pass

    def __repr__(self, *args, **kwargs): # real signature unknown
        """ Return repr(self). """
        pass

    name = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """name"""

    options = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """options"""

    subgroups = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """subgroups"""

    text = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """text"""



class HTTPError(Exception):
    """
    This exception is raised when an HTTP problem has occurred.  It
    provides an integer HTTP status code.

    Use it like this::
      try:
        ...
      except cups.HTTPError as (status):
        print 'HTTP status is %d' % status
    """
    def __init__(self, *args, **kwargs): # real signature unknown
        pass

    __weakref__ = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """list of weak references to the object"""



class IPPAttribute(object):
    """
    IPP Attribute
    =============
      An IPP attribute.

    @type group_tag: int
    @ivar group_tag: IPP group tag
    @type value_tag: int
    @ivar value_tag: IPP value tag
    @type values: list
    @ivar value: list of values
    """
    def __init__(self, *args, **kwargs): # real signature unknown
        pass

    @staticmethod # known case of __new__
    def __new__(*args, **kwargs): # real signature unknown
        """ Create and return a new object.  See help(type) for accurate signature. """
        pass

    def __repr__(self, *args, **kwargs): # real signature unknown
        """ Return repr(self). """
        pass

    group_tag = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """IPP group tag"""

    name = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """IPP attribute name"""

    values = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """List of values"""

    value_tag = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """IPP value tag"""



class IPPError(Exception):
    """
    This exception is raised when an IPP error has occurred.  It
    provides an integer IPP status code, and a human-readable string
    describing the error.

    Use it like this::
      try:
        ...
      except cups.IPPError as (status, description):
        print 'IPP status is %d' % status
        print 'Meaning:', description
    """
    def __init__(self, *args, **kwargs): # real signature unknown
        pass

    __weakref__ = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """list of weak references to the object"""



class IPPRequest(object):
    """
    IPP Request
    ===========
      An IPP request.  The constructor takes an optional argument of the
    operation code.
    """
    def add(self, attr): # real signature unknown; restored from __doc__
        """
        add(attr) -> IPPAttribute

        @type attr: IPPAttribute
        @param attr: Attribute to add to the request
        @return: IPP request attribute
        """
        return IPPAttribute

    def addSeparator(self): # real signature unknown; restored from __doc__
        """
        addSeparator() -> IPPAttribute

        @return: IPP request attribute
        """
        return IPPAttribute

    def readIO(self, read_fn, blocking=True): # real signature unknown; restored from __doc__
        """
        readIO(read_fn, blocking=True) -> IPP state

        @type read_fn: Callable function
        @param read_fn: A callback, taking a single integer argument for
        'size', for reading IPP data
        @type blocking: Boolean
        @param blocking: whether to continue reading until a complete
        request is read
        @return: IPP state value
        """
        pass

    def writeIO(self, write_fn, blocking=True): # real signature unknown; restored from __doc__
        """
        writeIO(write_fn, blocking=True) -> IPP state

        @type write_fn: Callable function
        @param write_fn: A callback, taking a bytes object, for writing
        IPP data
        @type blocking: Boolean
        @param blocking: whether to continue reading until a complete
        request is written
        @return: IPP state value
        """
        pass

    def __init__(self, *args, **kwargs): # real signature unknown
        pass

    @staticmethod # known case of __new__
    def __new__(*args, **kwargs): # real signature unknown
        """ Create and return a new object.  See help(type) for accurate signature. """
        pass

    attributes = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """IPP request attributes"""

    operation = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """IPP request operation"""

    state = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """IPP request transfer state"""

    statuscode = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """IPP response status code"""



class Option(object):
    """
    PPD option
    ==========
      A PPD option.

    @type conflicted: boolean
    @ivar conflicted: whether this option is in conflict
    @type keyword: string
    @ivar keyword: the option keyword e.g. Duplex
    @type defchoice: string
    @ivar defchoice: the default option choice
    @type text: string
    @ivar text: the user-presentable option name e.g. Double-sided printing
    @type ui: integer
    @ivar ui: the option type; one of L{PPD_UI_BOOLEAN},
    L{PPD_UI_PICKONE}, L{PPD_UI_PICKMANY}
    @type choices: list
    @ivar choices: list of the option's choices
    """
    def __init__(self, *args, **kwargs): # real signature unknown
        pass

    @staticmethod # known case of __new__
    def __new__(*args, **kwargs): # real signature unknown
        """ Create and return a new object.  See help(type) for accurate signature. """
        pass

    def __repr__(self, *args, **kwargs): # real signature unknown
        """ Return repr(self). """
        pass

    choices = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """choices"""

    conflicted = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """Whether this option is in conflict"""

    defchoice = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """defchoice"""

    keyword = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """keyword"""

    text = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """text"""

    ui = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """ui"""



class PPD(object):
    """
    PPD file
    ========
      A PPD file.

    @type constraints: L{Constraint} list
    @ivar constraints: list of constraints
    @type attributes: L{Attribute} list
    @ivar attributes: list of attributes
    @type optionGroups: L{Group} list
    @ivar optionGroups: list of PPD option groups
    """
    def conflicts(self): # real signature unknown; restored from __doc__
        """
        conflicts() -> integer

        @return: number of conflicts.
        """
        return 0

    def emit(self, file, section): # real signature unknown; restored from __doc__
        """
        emit(file, section) -> None

        Output marked options for section to a file.
        @type file: file
        @param file: file object
        @type section: integer
        @param section: section id
        """
        pass

    def emitAfterOrder(self, file, section, limit, min_order): # real signature unknown; restored from __doc__
        """
        emitAfterOrder(file, section, limit, min_order) -> None

        Output marked options for section to a file.
        @type file: file
        @param file: file object
        @type section: integer
        @param section: section id
        @type limit: integer
        @param limit: non-zero to use min_order
        @type min_order: float
        @param min_order: minimum order dependency
        """
        pass

    def emitFd(self, fd, section): # real signature unknown; restored from __doc__
        """
        emitFd(fd, section) -> None

        Output marked options for section to a file descriptor.
        @type fd: integer
        @param fd: file descriptor
        @type section: integer
        @param section: section id
        """
        pass

    def emitJCL(self, file, job_id, user, title): # real signature unknown; restored from __doc__
        """
        emitJCL(file, job_id, user, title) -> None

        Emit code for JCL options to a file.
        @type file: file object
        @param file: file
        @type job_id: integer
        @param job_id: job id
        @type user: string
        @param user: user name on job
        @type title: string
        @param title: title of job
        """
        pass

    def emitJCLEnd(self, file): # real signature unknown; restored from __doc__
        """
        emitJCLEnd(file) -> None

        Emit JCLEnd code to a file.
        @type file: file object
        @param file: file
        """
        pass

    def emitString(self, section, min_order): # real signature unknown; restored from __doc__
        """
        emitString(section, min_order) -> string

        Return a string with the marked options for section, with at least min_order order dependency.
        @type section: integer
        @param section: section id
        @type min_order: float
        @param min_order: minimum order dependency
        @return: string containing emitted postscript
        """
        return ""

    def findAttr(self, name): # real signature unknown; restored from __doc__
        """
        findAttr(name)

        @type name: string
        @param name: attribute name
        @type spec: string
        @keyword spec: specifier string (optional)
        @rtype: L{Attribute} or None
        @return: matching attribute, or None if not found.
        """
        pass

    def findNextAttr(self, name): # real signature unknown; restored from __doc__
        """
        findNextAttr(name)

        @type name: string
        @param name: attribute name
        @type spec: string
        @keyword spec: specifier string (optional)
        @rtype: L{Attribute} or None
        @return: next matching attribute, or None if not found.
        """
        pass

    def findOption(self, name): # real signature unknown; restored from __doc__
        """
        findOption(name)

        @type name: string
        @param name: option keyword
        @rtype: L{Option} or None
        @return: named option, or None if not found.
        """
        pass

    def localize(self): # real signature unknown; restored from __doc__
        """
        localize() -> None

        Localize PPD to the current locale.
        """
        pass

    def localizeIPPReason(self, reason, scheme): # real signature unknown; restored from __doc__
        """
        localizeIPPReason(reason, scheme) -> string or None

        Localize IPP reason to the current locale.
        """
        return ""

    def localizeMarkerName(self, name): # real signature unknown; restored from __doc__
        """
        localizeMarkerName(name) -> string or None

        Localize marker name to the current locale.
        """
        return ""

    def markDefaults(self): # real signature unknown; restored from __doc__
        """
        markDefaults() -> None

        Set (mark) all options to their default choices.
        """
        pass

    def markOption(self, option, choice): # real signature unknown; restored from __doc__
        """
        markOption(option, choice) -> integer

        Set an option to a particular choice.

        @type option: string
        @param option: option keyword
        @type choice: string
        @param choice: option choice
        @return: number of conflicts
        """
        return 0

    def nondefaultsMarked(self): # real signature unknown; restored from __doc__
        """
        nondefaultsMarked() -> boolean

        Returns true if any non-default option choices are marked.
        """
        return False

    def writeFd(self, fd): # real signature unknown; restored from __doc__
        """
        writeFd(fd) -> None

        Write PPD file, with marked choices as defaults, to file
        descriptor.

        @type fd: integer
        @param fd: open file descriptor
        """
        pass

    def __init__(self, *args, **kwargs): # real signature unknown
        pass

    @staticmethod # known case of __new__
    def __new__(*args, **kwargs): # real signature unknown
        """ Create and return a new object.  See help(type) for accurate signature. """
        pass

    attributes = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """List of attributes"""

    constraints = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """List of constraints"""

    optionGroups = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default
    """List of PPD option groups"""



# variables with complex values

__loader__ = None # (!) real value is '<_frozen_importlib_external.ExtensionFileLoader object at 0x7fe9026674a0>'

__spec__ = None # (!) real value is "ModuleSpec(name='cups', loader=<_frozen_importlib_external.ExtensionFileLoader object at 0x7fe9026674a0>, origin='/home/dante/PycharmProjects/printers/.venv/lib64/python3.12/site-packages/cups.cpython-312-x86_64-linux-gnu.so')"
