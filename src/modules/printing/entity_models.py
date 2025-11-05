from enum import IntEnum, StrEnum
from typing import Literal

from pydantic import Field

from src.api.logging_ import logger
from src.config_schema import Printer
from src.pydantic_base import BaseSchema


class PrintingOptions(BaseSchema):
    copies: str | None = Field(default=None)
    "Count of copies"
    page_ranges: str | None = Field(default=None, alias="page-ranges")
    "Which page ranges to print"
    sides: Literal["one-sided", "two-sided-long-edge"] | None = Field(default=None)
    "One-sided or double-sided printing"
    number_up: Literal["1", "2", "4", "6", "9", "16"] | None = Field(default=None, alias="number-up")
    "Count of pages on a list"


class JobStateEnum(IntEnum):
    """
    Figure 3 shows the normal Job state transitions.  Normally, a Job
    progresses from left to right.  Other state transitions are unlikely
    but are not forbidden.  Not shown are the transitions to the
    'canceled' state from the 'pending', 'pending-held', and
    'processing-stopped' states.

                                                        +----> canceled
                                                        /
        +----> pending  -------> processing ---------+------> completed
        |         ^                   ^               \
    --->+         |                   |                +----> aborted
        |         v                   v               /
        +----> pending-held    processing-stopped ---+

                        Figure 3: IPP Job Life Cycle

    Jobs reach one of the three terminal states -- 'completed',
    'canceled', or 'aborted' -- after the Jobs have completed all
    activity, including stacking output media, and all Job Status
    attributes have reached their final values for the Job.

    +--------+----------------------------------------------------------+
    | Values | Symbolic Name and Description                            |
    +--------+----------------------------------------------------------+
    | '3'    | 'pending': The Job is a candidate to start processing    |
    |        | but is not yet processing.                               |
    +--------+----------------------------------------------------------+
    | '4'    | 'pending-held': The Job is not a candidate for           |
    |        | processing for any number of reasons but will return to  |
    |        | the 'pending' state as soon as the reasons are no longer |
    |        | present.  The Job's "job-state-reasons" attribute MUST   |
    |        | indicate why the Job is no longer a candidate for        |
    |        | processing.                                              |
    +--------+----------------------------------------------------------+
    | '5'    | 'processing': One or more of the following: (1) the Job  |
    |        | is using, or is attempting to use, one or more purely    |
    |        | software processes that are analyzing, creating, or      |
    |        | interpreting a PDL, etc.; (2) the Job is using, or is    |
    |        | attempting to use, one or more hardware devices that are |
    |        | interpreting a PDL; making marks on a medium; and/or     |
    |        | performing finishing, such as stapling, etc.; (3) the    |
    |        | Printer has made the Job ready for printing, but the     |
    |        | Output Device is not yet printing it, either because the |
    |        | Job hasn't reached the Output Device or because the Job  |
    |        | is queued in the Output Device or some other spooler,    |
    |        | waiting for the Output Device to print it.  When the Job |
    |        | is in the 'processing' state, the entire Job state       |
    |        | includes the detailed status represented in the          |
    |        | Printer's "printer-state", "printer-state-reasons", and  |
    |        | "printer-state-message" attributes.  Implementations MAY |
    |        | include additional values in the Job's "job-state-       |
    |        | reasons" attribute to indicate the progress of the Job,  |
    |        | such as adding the 'job-printing' value to indicate when |
    |        | the Output Device is actually making marks on paper      |
    |        | and/or the 'processing-to-stop-point' value to indicate  |
    |        | that the Printer is in the process of canceling or       |
    |        | aborting the Job.                                        |
    +--------+----------------------------------------------------------+
    | '6'    | 'processing-stopped': The Job has stopped while          |
    |        | processing for any number of reasons and will return to  |
    |        | the 'processing' state as soon as the reasons are no     |
    |        | longer present.  The Job's "job-state-reasons" attribute |
    |        | MAY indicate why the Job has stopped processing.  For    |
    |        | example, if the Output Device is stopped, the 'printer-  |
    |        | stopped' value MAY be included in the Job's "job-state-  |
    |        | reasons" attribute.  Note: When an Output Device is      |
    |        | stopped, the device usually indicates its condition in   |
    |        | human-readable form locally at the device.  A Client can |
    |        | obtain more complete device status remotely by querying  |
    |        | the Printer's "printer-state", "printer-state-reasons",  |
    |        | and "printer-state-message" attributes.                  |
    +--------+----------------------------------------------------------+
    | '7'    | 'canceled':  The Job has been canceled by a Cancel-Job   |
    |        | operation, and the Printer has completed canceling the   |
    |        | Job.  All Job Status attributes have reached their final |
    |        | values for the Job.  While the Printer is canceling the  |
    |        | Job, the Job remains in its current state, but the Job's |
    |        | "job-state-reasons" attribute SHOULD contain the         |
    |        | 'processing-to-stop-point' value and one of the          |
    |        | 'canceled-by-user', 'canceled-by-operator', or           |
    |        | 'canceled-at-device' values.  When the Job moves to the  |
    |        | 'canceled' state, the 'processing-to-stop-point' value,  |
    |        | if present, MUST be removed, but 'canceled-by-xxx', if   |
    |        | present, MUST remain.                                    |
    +--------+----------------------------------------------------------+
    | '8'    | 'aborted': The Job has been aborted by the system,       |
    |        | usually while the Job was in the 'processing' or         |
    |        | 'processing-stopped' state, and the Printer has          |
    |        | completed aborting the Job; all Job Status attributes    |
    |        | have reached their final values for the Job.  While the  |
    |        | Printer is aborting the Job, the Job remains in its      |
    |        | current state, but the Job's "job-state-reasons"         |
    |        | attribute SHOULD contain the 'processing-to-stop-point'  |
    |        | and 'aborted-by-system' values.  When the Job moves to   |
    |        | the 'aborted' state, the 'processing-to-stop-point'      |
    |        | value, if present, MUST be removed, but the 'aborted-by- |
    |        | system' value, if present, MUST remain.                  |
    +--------+----------------------------------------------------------+
    | '9'    | 'completed': The Job has completed successfully or with  |
    |        | warnings or errors after processing, all of the Job      |
    |        | Media Sheets have been successfully stacked in the       |
    |        | appropriate output bin(s), and all Job Status attributes |
    |        | have reached their final values for the Job.  The Job's  |
    |        | "job-state-reasons" attribute SHOULD contain one of the  |
    |        | 'completed-successfully', 'completed-with-warnings', or  |
    |        | 'completed-with-errors' values.                          |
    +--------+----------------------------------------------------------+

                        Table 15: "job-state" Enum Values
    """

    pending = 3
    pending_held = 4
    processing = 5
    processing_stopped = 6
    canceled = 7
    aborted = 8
    completed = 9


class JobStateReasonEnum(StrEnum):
    """
    https://www.rfc-editor.org/rfc/rfc8011.html#section-5.3.8


    The following standard 'keyword' values are defined.  For ease of
    understanding, the values are presented in the order in which the
    reasons are likely to occur (if implemented):

    o  'none': There are no reasons for the Job's current state.  This
        state reason is semantically equivalent to "job-state-reasons"
        without any value and MUST be used when there is no other value,
        since the '1setOf' attribute syntax requires at least one value.

    o  'job-incoming': Either (1) the Printer has accepted the Create-Job
        operation and is expecting additional Send-Document and/or
        Send-URI operations or (2) the Printer is retrieving/accepting
        Document data as a result of a Print-Job, Print-URI,
        Send-Document, or Send-URI operation.

    o  'job-data-insufficient': The Create-Job operation has been
        accepted by the Printer, but the Printer is expecting additional
        Document data before it can move the Job into the 'processing'
        state.  If a Printer starts processing before it has received all
        data, the Printer removes the 'job-data-insufficient' reason, but
        the 'job-incoming' reason remains.  If a Printer starts processing
        after it has received all data, the Printer removes the
        'job-data-insufficient' reason and the 'job-incoming' reason at
        the same time.

    o  'document-access-error': After accepting a Print-URI or Send-URI
        request, the Printer could not access one or more Documents passed
        by reference.  This reason is intended to cover any file access
        problem, including 'file does not exist' and 'access denied'
        because of an access control problem.  The Printer MAY also
        indicate the Document access error using the
        "job-document-access-errors" Job Status attribute (see
        Section 5.3.11).  The Printer can (1) abort the Job and move the
        Job to the 'aborted' Job state or (2) print all Documents that are
        accessible and move the Job to the 'completed' Job state with the
        'completed-with-errors' value in the Job's "job-state-reasons"
        attribute.  This value SHOULD be supported if the Print-URI or
        Send-URI operations are supported.

    o  'submission-interrupted': The Job was not completely submitted for
        some unforeseen reason, such as (1) the Printer has crashed before
        the Job was closed by the Client, (2) the Printer or the Document
        transfer method has crashed in some non-recoverable way before the
        Document data was entirely transferred to the Printer, or (3) the
        Client crashed or failed to close the Job before the time-out
        period.  See Section 5.4.31.

    o  'job-outgoing': The Printer is transmitting the Job to the Output
        Device.

    o  'job-hold-until-specified': The value of the Job's
        "job-hold-until" attribute was specified with a time period that
        is still in the future.  The Job MUST NOT be a candidate for
        processing until this reason is removed and there are no other
        reasons to hold the Job.  This value SHOULD be supported if the
        "job-hold-until" Job Template attribute is supported.

    o  'resources-are-not-ready': At least one of the resources needed by
        the Job, such as media, fonts, resource objects, etc., is not
        ready on any of the physical Output Devices for which the Job is a
        candidate.  This condition MAY be detected when the Job is
        accepted, or subsequently while the Job is pending or processing,
        depending on implementation.  The Job can remain in its current
        state or be moved to the 'pending-held' state, depending on
        implementation and/or Job scheduling policy.

    o  'printer-stopped-partly': The value of the Printer's
        "printer-state-reasons" attribute contains the value
        'stopped-partly'.

    o  'printer-stopped': The value of the Printer's "printer-state"
        attribute is 'stopped'.

    o  'job-interpreting': The Job is in the 'processing' state, but,
        more specifically, the Printer is interpreting the Document data.

    o  'job-queued': The Job is in the 'processing' state, but, more
        specifically, the Printer has queued the Document data.

    o  'job-transforming': The Job is in the 'processing' state, but,
        more specifically, the Printer is interpreting Document data and
        producing another electronic representation.

    o  'job-queued-for-marker': The Job is in any of the 'pending-held',
        'pending', or 'processing' states, but, more specifically, the
        Printer has completed enough processing of the Document to be able
        to start marking, and the Job is waiting for the marker.  Systems
        that require human intervention to release Jobs using the
        Release-Job operation put the Job into the 'pending-held' Job
        state.  Systems that automatically select a Job to use the marker
        put the Job into the 'pending' Job state or keep the Job in the
        'processing' Job state while waiting for the marker, depending on
        implementation.  All implementations put the Job into the
        'processing' state when marking does begin.

    o  'job-printing': The Output Device is marking media.  This value is
        useful for Printers that spend a great deal of time processing
        (1) when no marking is happening and they want to show that
        marking is now happening or (2) when the Job is in the process of
        being canceled or aborted while the Job remains in the
        'processing' state, but the marking has not yet stopped so that
        Impression or sheet counts are still increasing for the Job.

    o  'job-canceled-by-user': The Job was canceled by the owner of the
        Job using the Cancel-Job request, i.e., by a user whose
        authenticated identity is the same as the value of the originating
        user that created the Job, or by some other authorized End User,
        such as a member of the Job owner's security group.  This value
        SHOULD be supported.

    o  'job-canceled-by-operator': The Job was canceled by the Operator
        using the Cancel-Job request, i.e., by a user who has been
        authenticated as having Operator privileges (whether local or
        remote).  If the security policy is to allow anyone to cancel
        anyone's Job, then this value can be used when the Job is canceled
        by other than the owner of the Job.  For such a security policy,
        in effect, everyone is an Operator as far as canceling Jobs with
        IPP is concerned.  This value SHOULD be supported if the
        implementation permits canceling by other than the owner of
        the Job.

    o  'job-canceled-at-device': The Job was canceled by an unidentified
        local user, i.e., a user at a console at the device.  This value
        SHOULD be supported if the implementation supports canceling Jobs
        at the console.

    o  'aborted-by-system': The Job (1) is in the process of being
        aborted, (2) has been aborted by the system and placed in the
        'aborted' state, or (3) has been aborted by the system and placed
        in the 'pending-held' state, so that a user or Operator can
        manually try the Job again.  This value SHOULD be supported.

    o  'unsupported-compression': The Job was aborted by the system
        because the Printer determined, while attempting to decompress the
        Document data, that the compression algorithm is actually not
        among those supported by the Printer.  This value MUST be
        supported, since "compression" is a REQUIRED operation attribute.

    o  'compression-error': The Job was aborted by the system because the
        Printer encountered an error in the Document data while
        decompressing it.  If the Printer posts this reason, the Document
        data has already passed any tests that would have led to the
        'unsupported-compression' "job-state-reasons" value.

    o  'unsupported-document-format': The Job was aborted by the system
        because the Document data's "document-format" attribute is not
        among those supported by the Printer.  If the Client specifies
        "document-format" as 'application/octet-stream', the Printer MAY
        abort the Job and post this reason even though the
        "document-format" value is among the values of the Printer's
        "document-format-supported" Printer attribute but not among the
        auto-sensed Document formats.  This value MUST be supported, since
        "document-format" is a REQUIRED operation attribute.

    o  'document-format-error': The Job was aborted by the system because
        the Printer encountered an error in the Document data while
        processing it.  If the Printer posts this reason, the Document
        data has already passed any tests that would have led to the
        'unsupported-document-format' "job-state-reasons" value.

    o  'processing-to-stop-point': The requester has issued a Cancel-Job
        operation or the Printer has aborted the Job, but the Printer is
        still performing some actions on the Job until a specified stop
        point occurs or Job termination/cleanup is completed.

        If the implementation requires some measurable time to cancel the
        Job in the 'processing' or 'processing-stopped' Job state, the
        Printer MUST use this value to indicate that the Printer is still
        performing some actions on the Job while the Job remains in the
        'processing' or 'processing-stopped' state.  Once at the stop
        point, the Printer moves the Job from the 'processing' state to
        the 'canceled' or 'aborted' Job state.

    o  'service-off-line': The Printer is offline and accepting no Jobs.
        All 'pending' Jobs are put into the 'pending-held' state.  This
        situation could be true if the service's or Document transform's
        input is impaired or broken.

    o  'job-completed-successfully': The Job completed successfully.
        This value SHOULD be supported.

    o  'job-completed-with-warnings': The Job completed with warnings.
        This value SHOULD be supported if the implementation detects
        warnings.

    o  'job-completed-with-errors': The Job completed with errors (and
        possibly warnings too).  This value SHOULD be supported if the
        implementation detects errors.

    o  'job-restartable': This Job is retained (see Section 5.3.7.2) and
        is currently able to be restarted using the Restart-Job (see
        Section 4.3.7) or Resubmit-Job [PWG5100.11] operation.  If
        'job-restartable' is a value of the Job's "job-state-reasons"
        attribute, then the Printer MUST accept a Restart-Job operation
        for that Job.  This value SHOULD be supported if the Restart-Job
        operation is supported.

    o  'queued-in-device': The Job has been forwarded to a device or
        print system that is unable to send back status.  The Printer sets
        the Job's "job-state" attribute to 'completed' and adds the
        'queued-in-device' value to the Job's "job-state-reasons"
        attribute to indicate that the Printer has no additional
        information about the Job and never will have any better
        information.  See Section 5.3.7.1.
    """

    none = "none"
    job_printing = "job-printing"
    job_completed_successfully = "job-completed-successfully"


class PrinterStateReasonEnum(StrEnum):
    """
    https://github.com/istopwg/pwg-books/blob/master/ippguide/printers.md#printer-status-attributes

    The "printer-state-reasons" attribute is a list of keyword strings that provide details about the Printer's state:

    'none': Everything is super, nothing to report.
    'media-needed': The Printer needs paper loaded.
    'toner-low': The Printer is low on toner.
    'toner-empty': The Printer is out of toner.
    'marker-supply-low': The Printer is low on ink.
    'marker-supply-empty': The Printer is out of ink.

    The string may also have a severity suffix ("-error", "-warning", or "-report") to tell the Clients whether the reason affects the printing of a job.
    """

    none = "none"
    "Everything is super, nothing to report."
    cups_waiting_for_job_completed = "cups-waiting-for-job-completed"
    "CUPS is waiting for the job to complete."
    media_needed = "media-needed"
    "The Printer needs paper loaded."
    toner_low = "toner-low"
    "The Printer is low on toner."
    toner_empty = "toner-empty"
    "The Printer is out of toner."
    media_empty = "media-empty"
    "The Printer is out of paper."
    marker_supply_low = "marker-supply-low"
    "The Printer is low on ink."
    marker_supply_empty = "marker-supply-empty"
    "The Printer is out of ink."
    input_tray_missing = "input-tray-missing"
    "The input tray is missing."

    @classmethod
    def from_str(cls, value: str) -> tuple["PrinterStateReasonEnum", Literal["error", "warning", "report"] | None]:
        if value.endswith("-error"):
            return cls(value.removesuffix("-error")), "error"
        elif value.endswith("-warning"):
            return cls(value.removesuffix("-warning")), "warning"
        elif value.endswith("-report"):
            return cls(value.removesuffix("-report")), "report"
        else:
            return cls(value), None


class JobAttributes(BaseSchema):
    """
    References:
    - https://www.rfc-editor.org/rfc/rfc8011.html
    - https://github.com/istopwg/pwg-books/blob/master/ippguide/printers.md
    - https://www.iana.org/assignments/ipp-registrations/ipp-registrations.xml
    """

    job_state: JobStateEnum
    """The current state of a job

    ```python
    if job_attributes.job_state == JobStateEnum.pending:
        throbber = "⏳"
    elif job_attributes.job_state == JobStateEnum.pending_held:
        throbber = "⏳"
    elif job_attributes.job_state == JobStateEnum.processing:
        throbber = "⤹⤿⤻⤺"[iteration % 4]
    elif job_attributes.job_state == JobStateEnum.processing_stopped:
        throbber = "⏸"
    elif job_attributes.job_state == JobStateEnum.canceled:
        throbber = "❌"
    elif job_attributes.job_state == JobStateEnum.aborted:
        throbber = "❌"
    elif job_attributes.job_state == JobStateEnum.completed:
        throbber = "✅"
    else:
        assert_never(job_attributes.job_state)
    ```
    """
    job_state_reasons: JobStateReasonEnum | str
    "Reasons for the job state"
    job_state_message: str | None
    "Human readable message for the job state"

    printer_state_reasons: (
        list[
            tuple[
                PrinterStateReasonEnum | str,
                Literal["error", "warning", "report", None],
            ]
        ]
        | None
    )
    "The current state of printer"
    printer_state_message: str | None
    "Human readable message for the printer state, use for error messages"

    @classmethod
    def parse_job_state_reasons(cls, value: str) -> JobStateReasonEnum | str:
        try:
            return JobStateReasonEnum(value)
        except ValueError:
            logger.warning(f"Unknown job state: {value}")
            return value

    @classmethod
    def parse_printer_state(
        cls, value: list[str]
    ) -> list[tuple[PrinterStateReasonEnum | str, Literal["error", "warning", "report", None]]]:
        _result = []
        for v in value:
            if isinstance(v, str):
                try:
                    reason, severity = PrinterStateReasonEnum.from_str(v)
                    _result.append((reason, severity))
                except ValueError:
                    logger.warning(f"Unknown printer state: {v}")
                    _result.append((v, None))
            else:
                logger.warning(f"Unknown printer state: {v}")
                _result.append(v)
        return _result


class PrinterStatus(BaseSchema):
    printer: Printer
    offline: bool
    paper_percentage: int | None
    toner_percentage: int | None


class PreparePrintingResponse(BaseSchema):
    filename: str
    pages: int
