Vendor Bill Approval

Configurable multi-level approval for Odoo 19 vendor bills and vendor credit notes.

Configuration

Open Accounting > Configuration > Settings > Vendor Bill Approval.

Enable Vendor Bill Approval.

Add the approval levels in the required order.

Select one or more approvers for each level. Any selected user can approve that level.

Mark a level as optional when the approver of the preceding level must decide whether it is required.

The configured users and the number of levels are not hard-coded. Configuration is company-specific.

Workflow

Submit a draft vendor bill for approval.

Approve, optionally request the next optional approval, or reject with a mandatory reason.

The most recently completed approval can be undone by its approver or an Accounting Manager.

A vendor bill can only be posted after final approval.

Submitted and approved bills are protected against accounting changes until the approval is reset.

The source interface is English. Belgian Dutch translations are included in i18n/nl_BE.po.

Approvals dashboard

Approvers automatically receive the Vendor Bill Approver group. In the
Approvals application, the first dashboard card shows only the vendor bills
currently awaiting the logged-in user's approval. Approvers do not need access
to Accounting or Purchase.