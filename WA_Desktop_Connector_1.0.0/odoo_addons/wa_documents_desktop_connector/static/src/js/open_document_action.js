/** @odoo-module **/

import { registry } from "@web/core/registry";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";

function selectedId(action) {
    const ids = action?.context?.active_ids || [];
    if (ids.length === 1) return Number(ids[0]);
    const selectors = [
        ".o_kanban_record.o_record_selected[data-id]", ".o_kanban_record.o_selected[data-id]",
        "tr.o_data_row.o_selected_row[data-id]", "tr.o_data_row.table-active[data-id]",
        "input.o_list_record_selector:checked"
    ];
    for (const selector of selectors) {
        const nodes = [...document.querySelectorAll(selector)];
        for (const node of nodes) {
            const holder = node.closest("[data-id]") || node;
            const value = holder.dataset.id || holder.getAttribute("data-res-id");
            if (value && /^\d+$/.test(value)) return Number(value);
        }
    }
    return null;
}

export async function openDesktop(env, id) {
    const result = await env.services.orm.call(
        "documents.document",
        "action_wa_prepare_desktop_open",
        [[id]]
    );
    if (!result?.url) {
        throw new Error("No desktop URL returned.");
    }
    window.location.href = result.url;
}

registry.category("actions").add("wa_documents_desktop_connector.open", async (env, action) => {
    const id = selectedId(action);
    if (!id) {
        env.services.notification.add(_t("Select exactly one file."), {type:"warning"});
        return;
    }

    env.services.dialog.add(ConfirmationDialog, {
        title: _t("Open document"),
        body: _t("How do you want to open this document?"),
        confirmLabel: _t("Open in desktop app"),
        cancelLabel: _t("Open in Odoo"),
        confirm: () => openDesktop(env, id),
        cancel: () => {},
    });
});
