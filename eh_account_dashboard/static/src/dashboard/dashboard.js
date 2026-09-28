/** @odoo-module **/

/**
 * Owl client action for the ERP Heritage financial dashboard.
 *
 * This component owns the live, reactive view of the dashboard. It is
 * registered against the action tag `eh_account_dashboard.board`, which
 * the model method `eh.account.dashboard.open_for_current_user` returns.
 *
 * Lifecycle:
 *
 *   onWillStart -> resolve the dashboard record id (from action context
 *                  or by calling open_for_current_user via JSON-RPC) and
 *                  load the first snapshot.
 *   onMounted   -> kick off the auto-refresh interval (60s) and hold the
 *                  handle for cleanup on unmount.
 *   onWillUnmount -> clear the interval to avoid stale ticks after the
 *                  user navigates away.
 *
 * State shape:
 *   - snapshot: the latest payload from `get_dashboard_snapshot`. Null
 *     on first render before the RPC resolves.
 *   - loading:  true while a snapshot RPC is in flight.
 *   - error:    error message string if the last RPC failed.
 *
 * Drill-downs use the existing model action methods (action_drilldown_*)
 * via env.services.action.doActionButton, so the navigation behaviour
 * stays identical to the legacy form view.
 */

import { Component, onError, onMounted, onWillStart, onWillUnmount, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

import { Sparkline } from "./sparkline";
import { KpiTile } from "./kpi_tile";

const REFRESH_INTERVAL_MS = 60_000;

export class EhDashboard extends Component {
    static template = "eh_account_dashboard.Dashboard";
    static components = { Sparkline, KpiTile };
    static props = {
        action: { type: Object, optional: true },
        actionId: { type: [Number, Boolean], optional: true },
        className: { type: String, optional: true },
        globalState: { type: Object, optional: true },
        updateActionState: { type: Function, optional: true },
        "*": { optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");

        this.state = useState({
            snapshot: null,
            loading: true,
            error: null,
            recordId: null,
        });

        this._intervalHandle = null;

        onWillStart(async () => {
            await this._resolveRecordId();
            await this._loadSnapshot();
        });

        onMounted(() => {
            this._intervalHandle = window.setInterval(
                () => this._loadSnapshot({ silent: true }),
                REFRESH_INTERVAL_MS,
            );
        });

        onWillUnmount(() => {
            if (this._intervalHandle) {
                window.clearInterval(this._intervalHandle);
                this._intervalHandle = null;
            }
        });

        // Error boundary: instead of letting an unexpected render
        // exception bubble to the global UncaughtPromiseError handler
        // (which presents a stack trace dialog), catch it locally and
        // surface a readable message inline. The original error is
        // attached to the cause for the browser console.
        onError((error) => {
            const cause = error?.cause || error;
            const message =
                cause?.data?.message
                || cause?.message
                || (typeof cause === "string" ? cause : "")
                || "The dashboard hit an unexpected error.";
            // eslint-disable-next-line no-console
            console.error("[eh_account_dashboard] render error:", error);
            this.state.error = message;
            this.state.loading = false;
        });
    }

    /**
     * Resolve the dashboard record id we should drive the snapshot
     * against. The action context may carry one (set by the server-side
     * action helper); otherwise we ask the model to find or create the
     * per-user record.
     */
    async _resolveRecordId() {
        const ctxId = this.props.action?.context?.eh_dashboard_id;
        if (ctxId) {
            this.state.recordId = ctxId;
            return;
        }
        const action = await this.orm.call(
            "eh.account.dashboard",
            "open_for_current_user",
            [],
        );
        const ctx = action?.context || {};
        if (ctx.eh_dashboard_id) {
            this.state.recordId = ctx.eh_dashboard_id;
        }
    }

    /**
     * Pull a fresh snapshot. `silent` skips the loading spinner so the
     * 60s auto-refresh does not flash the UI.
     */
    async _loadSnapshot({ silent = false } = {}) {
        if (!this.state.recordId) {
            this.state.error = _t("No dashboard record available.");
            this.state.loading = false;
            return;
        }
        if (!silent) {
            this.state.loading = true;
        }
        try {
            const snapshot = await this.orm.call(
                "eh.account.dashboard",
                "get_dashboard_snapshot",
                [[this.state.recordId]],
            );
            this.state.snapshot = snapshot;
            this.state.error = null;
        } catch (err) {
            this.state.error = err?.message?.message || _t("Failed to load dashboard.");
        } finally {
            this.state.loading = false;
        }
    }

    onClickRefresh() {
        this._loadSnapshot();
    }

    /**
     * Always-array accessor for the sparkline. The snapshot may be
     * null on first render, may be missing the cash_trend key on
     * future server changes, or may carry it as null on tenants with
     * no cash journals; the Sparkline expects an Array, so we
     * normalise here once instead of leaning on QWeb expression
     * truthiness in the template.
     */
    get cashTrend() {
        const series = this.state.snapshot?.cash_trend;
        return Array.isArray(series) ? series : [];
    }

    get revenueTrend() {
        const series = this.state.snapshot?.revenue_trend;
        return Array.isArray(series) ? series : [];
    }

    get expenseTrend() {
        const series = this.state.snapshot?.expense_trend;
        return Array.isArray(series) ? series : [];
    }

    /**
     * Lookup a delta block from the snapshot. Returns an object with
     * .delta and .pct (formatted) suitable for KpiTile props, or an
     * empty object when no delta is available so the spread silently
     * omits the props.
     */
    deltaProps(key, { higherIsBetter = true } = {}) {
        const block = this.state.snapshot?.deltas?.[key];
        if (!block) return {};
        return {
            delta: block.delta,
            deltaPct: block.pct,
            deltaLabel: this.formatMoney(block.delta),
            higherIsBetter,
        };
    }

    async onChangePeriod(ev) {
        const mode = ev.target.value;
        await this._writePeriod({ mode });
    }

    async onTogglePosted(ev) {
        await this._writePeriod({
            mode: this.state.snapshot?.period?.mode,
            posted_only: ev.target.checked,
        });
    }

    async _writePeriod({ mode, date_from = null, date_to = null, posted_only }) {
        if (!this.state.recordId) return;
        const args = [
            [this.state.recordId],
            mode || "mtd",
            date_from || false,
            date_to || false,
            posted_only !== undefined
                ? posted_only
                : !!this.state.snapshot?.period?.posted_only,
        ];
        try {
            const snapshot = await this.orm.call(
                "eh.account.dashboard",
                "update_period",
                args,
            );
            this.state.snapshot = snapshot;
            this.state.error = null;
        } catch (err) {
            this.notification.add(
                err?.message?.message || _t("Could not update period."),
                { type: "danger" },
            );
        }
    }

    async onClickDrilldown(methodName) {
        if (!this.state.recordId || !methodName) return;
        try {
            const action = await this.orm.call(
                "eh.account.dashboard",
                methodName,
                [[this.state.recordId]],
            );
            if (!action) {
                this.notification.add(
                    _t("This drill-down is not available: the related module is not installed."),
                    { type: "warning" },
                );
                return;
            }
            await this.action.doAction(action);
        } catch (err) {
            const detail = err?.data?.message
                || err?.data?.name
                || err?.message?.message
                || err?.message
                || _t("Drill-down failed.");
            this.notification.add(detail, { type: "danger" });
        }
    }

    /**
     * Format a monetary value using the snapshot currency. Avoids a
     * dependency on Odoo's monetary widget so the component renders
     * identically with or without a focused locale.
     */
    formatMoney(value) {
        const snap = this.state.snapshot;
        if (!snap) return "";
        const currency = snap.currency || {};
        const decimals = Number.isInteger(currency.decimal_places)
            ? currency.decimal_places
            : 2;
        const num = Number(value || 0).toLocaleString(undefined, {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals,
        });
        const symbol = currency.symbol || "";
        if (currency.position === "before") {
            return `${symbol}${num}`;
        }
        return `${num} ${symbol}`.trim();
    }

    formatInt(value) {
        return Number(value || 0).toLocaleString();
    }

    /**
     * Map a P&L net to a status class so the tile colour reflects sign.
     */
    netStatus(value) {
        if (!value) return "eh_dash_status_neutral";
        return value >= 0 ? "eh_dash_status_ok" : "eh_dash_status_danger";
    }

    /**
     * Aggregate the controls block into one badge so the alerts strip
     * can render without each per-control number visible. Returns null
     * if the snapshot is not loaded yet.
     */
    get controlsBadgeClass() {
        const total = this.state.snapshot?.controls?.total || 0;
        if (!total) return "eh_dash_status_ok";
        return total > 5 ? "eh_dash_status_danger" : "eh_dash_status_warn";
    }
}

registry.category("actions").add("eh_account_dashboard.board", EhDashboard);
