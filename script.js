// Import the data from the external file
import { salesData } from './sales-data.js';

document.addEventListener('DOMContentLoaded', function() {
    const data = salesData.heatmap_data;
    const analysis = salesData.analysis;

    // Populate analysis cards
    document.getElementById('best-day').textContent = analysis.best_day;
    document.getElementById('peak-hour').textContent = analysis.peak_hour;
    document.getElementById('worst-day').textContent = analysis.worst_day;
    document.getElementById('total-sales').textContent = `$${analysis.total_sales.toFixed(2)}`;
    document.getElementById('total-transactions').textContent = analysis.total_transactions;
    document.getElementById('avg-transaction').textContent = `$${analysis.avg_transaction_value.toFixed(2)}`;

    // --- Chart Setup ---
    const container = document.getElementById('heatmap-container');
    const tooltip = d3.select("#tooltip");
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const hours = Array.from({ length: 24 }, (_, i) => i);

    function drawHeatmap() {
        // Clear previous SVG content to allow for redrawing
        d3.select("#heatmap").selectAll("*").remove();
        // console.clear();

        // Define margins and calculate dimensions based on container's current width
        let marginright = 20, marginleft = 60;
        let margintop = 50, marginbot = 30;
        if (container.clientWidth < 600) marginright = 5, marginleft = 30, margintop = 30, marginbot = 10;
        const margin = { top: margintop, right: marginright, bottom: marginbot, left: marginleft};
        let width = container.clientWidth - margin.left - margin.right;
        // console.log("Container Width: "+container.clientWidth);
        // console.log("Width Pre Calc: "+width)
        if (width < 250) width = 250;

        const gridSize = Math.floor(width / hours.length);
        const height = gridSize * days.length;
        width = gridSize * hours.length;
        // console.log("Width Post Calc: "+width)
        // console.log("Height Post Calc: "+height)

        const svg = d3.select("#heatmap")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", `translate(${margin.left}, ${margin.top})`);

        // Create Day labels (Y-axis)
        svg.selectAll(".dayLabel")
            .data(days)
            .enter()
            .append("text")
            .text(d => d)
            .attr("x", 0)
            .attr("y", (d, i) => i * gridSize)
            .style("text-anchor", "end")
            .attr("transform", `translate(-6, ${gridSize / 1.5})`)
            .style("font-size", `${Math.max(8, gridSize / 2.5)}px`)
            .style("fill", "#4b5563");

        // Create Hour labels (X-axis)
        svg.selectAll(".timeLabel")
            .data(hours)
            .enter()
            .append("text")
            .text(d => `${d}h`)
            .attr("x", (d, i) => i * gridSize)
            .attr("y", 0)
            .style("text-anchor", "middle")
            .attr("transform", `translate(${gridSize / 2}, -6)`)
            .style("font-size", `${Math.max(8, gridSize / 3)}px`)
            .style("fill", "#4b5563")
            .style("display", (d, i) => {
                if (gridSize < 14) return (i % 4 === 0) ? "block" : "none";
                if (gridSize < 20) return (i % 2 === 0) ? "block" : "none";
                return "block";
            });

        // Build color scale
        const maxSales = d3.max(data, d => d.sales);
        const colorScale = d3.scaleQuantile()
            .domain([0, maxSales])
            // .range(['#d1fae5', '#6ee7b7', '#10b981', '#047857']);
            // .range(['#e0f2f1', '#b2dfdb', '#4db6ac', '#00897b', '#004d40']);    //green shades
            .range(['#e3f2fd', '#90caf9', '#42a5f5', '#1e88e5', '#0d47a1']);    //blue shades
            // .range(['#ffebee', '#ef9a9a', '#e57373', '#ef5350', '#b71c1c']);    //red shades
            // .range(['#fffde7', '#fff59d', '#ffca28', '#ff8f00', '#e65100']);    //yellow shades

        // Tooltip event handlers
        const mouseover = function(event, d) {
            tooltip.style("opacity", 1);
            d3.select(this).style("stroke", "black").style("stroke-width", 2);
        }
        const mousemove = function(event, d) {
            tooltip
                .html(`<strong>${days[d.day]} at ${d.hour}:00</strong><br>Sales: $${d.sales.toFixed(2)}`)
                .style("left", (event.pageX + 20) + "px")
                .style("top", (event.pageY - 20) + "px");
        }
        const mouseleave = function(event, d) {
            tooltip.style("opacity", 0);
            d3.select(this).style("stroke", "#e5e7eb");
        }

        // Create heatmap rectangles
        svg.selectAll()
            .data(data, d => `${d.day}:${d.hour}`)
            .enter()
            .append("rect")
            .attr("x", d => d.hour * gridSize)
            .attr("y", d => d.day * gridSize)
            .attr("rx", Math.max(1, gridSize / 8))
            .attr("ry", Math.max(1, gridSize / 8))
            .attr("width", gridSize - 1)
            .attr("height", gridSize - 1)
            .style("fill", d => d.sales > 0 ? colorScale(d.sales) : "#f3f4f6")
            .style("stroke-width", 1)
            .style("stroke", "#e5e7eb")
            .on("mouseover", mouseover)
            .on("mousemove", mousemove)
            .on("mouseleave", mouseleave);
    }

    // Initial draw
    drawHeatmap();

    // Redraw on resize
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(drawHeatmap, 250);
    });
});