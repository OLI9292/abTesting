(function() {

  for (var g = 0; g < graphs.length; g++) {

    $('.graph-heading').show();

    var m = [30, 30, 40, 60];
    var h = 400 - m[0] - m[2];
    var w = 600 - m[1] - m[3]; 
    var column = graphs[g]['col'];
    var div = graphs[g]['div'];
    var title = graphs[g]['title'];

    $(div).empty();

    function max(arr, attr) {
      return Math.max.apply(Math, arr.map(function(o){return o[attr];}));
    };

    var format = d3.time.format("%Y-%m-%d %H:%M:%S");

    var x = d3.time.scale().domain([format.parse(data[0]['session_start_at']), 
                                    format.parse(data.slice(-1)[0]['session_start_at'])])
                           .range([m[3], w+m[1]]);

    var y = d3.scale.linear().domain([0, max(data, column) * 1.2]).range([h, 0]);

    var control = data.filter(function(c) { return c.status === 'control'; });
    var test = data.filter(function(t) { return t.status === 'test'; });

    var line = d3.svg.line()
      .x(function(d) { return x(format.parse(d.session_start_at)); })
      .y(function(d) { return y(d[column]); });

    var line2 = d3.svg.line()
      .x(function(d) { return x(format.parse(d.session_start_at)); })
      .y(function(d) { return y(d[column]); });

    var graph = d3.select(div).append("svg:svg")
        .attr("width", w + m[1] + m[3])
        .attr("height", h + m[0] + m[2])
      .append("svg:g")
        .attr("transform", "translate(" + m[3] + "," + m[0] + ")");

    graph.append("svg:g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + h + ")");

    var yAxisLeft = d3.svg.axis().scale(y).tickSize(-w).ticks(5).orient("left")
      .tickFormat(function(d) { return d; })
      .tickPadding(10);

    graph.append("svg:g")
      .attr("class", "y axis")
      .call(yAxisLeft);

    graph.append("svg:path")
      .datum(control)
      .attr("class", "line")
      .attr("d", line)
      .attr("transform", "translate(" + (m[3] * -1) + ", 0)")
      .style("stroke", "black");

    graph.append("svg:path")
      .datum(test)
      .attr("class", "line")
      .attr("d", line2)
      .attr("transform", "translate(" + (m[3] * -1) + ", 0)")
      .style("stroke", "#6A0BC1");

    graph.append('text')
      .text(title)
      .attr("y", '-10')
      .attr("class", "graph-title");

    graph.append('text')
      .text('TEST |')
      .attr("y", '320')
      .attr("x", '500')
      .style("stroke", '#6A0BC1')
      .attr("class", "test-key");

    graph.append('text')
      .text('CONTROL |')
      .attr("y", '300')
      .attr("x", '500')
      .attr("class", "control-key");
  }
})();
