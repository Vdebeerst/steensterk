/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { DocumentsKanbanRecord } from "@documents/views/kanban/documents_kanban_model";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { openDesktop } from "./open_document_action";

function hasFileExtension(record) {
    const name = record.data.name || record.data.display_name || "";
    return record.data.type === "binary" && /\.[^./\\]+$/.test(name);
}

patch(DocumentsKanbanRecord.prototype, {
    async onClickPreview(ev) {
        if (!hasFileExtension(this)) {
            return super.onClickPreview(...arguments);
        }

        ev.stopPropagation();
        ev.preventDefault();

        this.model.env.services.dialog.add(ConfirmationDialog, {
            title: _t("Open document"),
            body: _t("How do you want to open this document?"),
            confirmLabel: _t("Open in desktop app"),
            cancelLabel: _t("Open in Odoo"),
            confirm: () => openDesktop(this.model.env, this.data.id),
            cancel: () => super.onClickPreview(...arguments),
        });
    },
});
