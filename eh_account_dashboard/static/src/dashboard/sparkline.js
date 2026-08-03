/** @odoo-module **/

/**
 * Inline SVG sparkline for the cash trend.
 *
 * Drawn as a single polyline with min/max guides. Avoids Chart.js so
 * the asset bundle stays small and the dashboard renders even on
 * Odoo deployments that strip optional libraries from the web.assets
 * bundle. The component is purely presentational: it expects the data
 * series ready to plot, and renders nothing if the series is empty
 * or has fewer than two points (a single-point line would not convey
 * trend).
 *
 * Layout: the SVG fills 100% of its container width and a fixed pixel
 * height. Padding is applied inside the viewBox so the line never
 * touches the edges. The latest value is rendered as a small dot at
 * the right end with a label.
 */

import { Component } from "@odoo/owl";

const HEIGHT = 90;
const VIEW_WIDTH = 600;
const PAD_X = 8;
const PAD_Y = 12;

export class Sparkline extends Component {
    static template = "eh_account_dashboard.Sparkline";
    static props = {
        // `series` is treated as optional with an empty-array default
        // so the parent can pass `state.snapshot.cash_trend` even on
        // the very first render, before the snapshot RPC has resolved
        // or on a tenant that has no cash journals (server returns []).
        series: {
            type: Array,
            element: { type: Object, shape: { date: String, value: Number } },
            optional: true,
        },
        formatLabel: { type: Function, optional: true },
        accentClass: { type: String, optional: true },
    };
    static defaultProps = {
        accentClass: "eh_dash_spark_default",
        series: [],
    };
    get plottable() {
        return Array.isArray(this.props.series) && this.props.series.length >= 2;
    }

    get height() {
        return HEIGHT;
    }

    get viewBox() {
        return `0 0 ${VIEW_WIDTH} ${HEIGHT}`;
    }

    /**
     * Map data to SVG-space coordinates. Returns:
     *   - polyline points string
     *   - last-point coordinate {x, y}
     *   - min/max values for the range guide
     * Returns null when not plottable.
     */
    get geometry() {
        if (!this.plottable) return null;
        const series = this.props.series;
        const values = series.map((p) => p.value);
        const min = Math.min(...values);
        const max = Math.max(...values);
        // Avoid division-by-zero for a flat series; render a horizontal
        // line at the vertical centre so the user still sees the value.
        const range = max - min || 1;
        const stepX = (VIEW_WIDTH - 2 * PAD_X) / (series.length - 1);
        const usableY = HEIGHT - 2 * PAD_Y;
        const points = series.map((p, i) => {
            const x = PAD_X + i * stepX;
            const y = HEIGHT - PAD_Y - ((p.value - min) / range) * usableY;
            return [x, y];
        });
        const last = points[points.length - 1];
        return {
            polyline: points.map(([x, y]) => `${x},${y}`).join(" "),
            last: { x: last[0], y: last[1] },
            min,
            max,
            firstValue: series[0].value,
            lastValue: series[series.length - 1].value,
        };
    }

    /**
     * Direction class: green when the latest value is at or above the
     * first, amber when slightly below, red when materially below.
     * Threshold is intentionally generous because cash position varies
     * day to day; a 1% dip should not flash red.
     */
    get accentClass() {
        const g = this.geometry;
        if (!g) return this.props.accentClass;
        const delta = g.lastValue - g.firstValue;
        if (delta >= 0) return "eh_dash_spark_up";
        const ratio = Math.abs(delta) / (Math.abs(g.firstValue) || 1);
        if (ratio < 0.05) return "eh_dash_spark_flat";
        return "eh_dash_spark_down";
    }

    formatValue(value) {
        if (this.props.formatLabel) {
            return this.props.formatLabel(value);
        }
        return Number(value || 0).toLocaleString();
    }
}
