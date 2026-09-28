/** @odoo-module **/

import { onMounted, onPatched } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";
import { user } from "@web/core/user";
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";

patch(KanbanRenderer.prototype, {
    setup() {
        super.setup(...arguments);
        this.waOrm = useService("orm");
        this.waAction = useService("action");
        onMounted(() => this._waAddVendorBillCard());
        onPatched(() => this._waAddVendorBillCard());
    },

    async _waAddVendorBillCard() {
        const kanban = document.querySelector(".o_action_manager .o_kanban_renderer");
        if (
            this.props.list.resModel !== "approval.category"
            || !kanban
            || kanban.querySelector(".o_wa_vendor_bill_card")
            || this._waVendorBillCardLoading
        ) {
            return;
        }

        this._waVendorBillCardLoading = true;

        const card = document.createElement("div");
        card.className = "o_kanban_record o_wa_vendor_bill_card";

        const iconContainer = document.createElement("div");
        iconContainer.className = "o_wa_vendor_bill_icon";

        const nativeIcons = kanban.querySelectorAll(
            ".o_kanban_record:not(.o_wa_vendor_bill_card) img"
        );
        const nativeIcon = nativeIcons[nativeIcons.length - 1];
        if (nativeIcon) {
            const icon = nativeIcon.cloneNode(true);
            icon.removeAttribute("id");
            iconContainer.append(icon);
        }

        const content = document.createElement("div");
        content.className = "o_wa_vendor_bill_content";

        const title = document.createElement("strong");
        title.textContent = _t("Vendor Bills");

        const button = document.createElement("button");
        button.type = "button";
        button.className = "btn btn-primary";
        button.textContent = _t("To Review");
        button.addEventListener("click", () => this.waAction.doAction(
            "wa_vendor_bill_approval.action_vendor_bill_approval_inbox"
        ));

        content.append(title, button);
        card.append(iconContainer, content);
        kanban.prepend(card);

        try {
            const count = await this.waOrm.searchCount(
                "vendor.bill.approval.line",
                [
                    ["state", "=", "pending"],
                    ["approver_ids", "in", [user.userId]],
                ]
            );
            if (count) {
                button.textContent = _t("To Review (%s)", count);
            }
        } catch {
            // De tegel blijft beschikbaar wanneer de teller niet geladen kan worden.
        } finally {
            this._waVendorBillCardLoading = false;
        }
    },
});