Title: Jsonb
Date: 2017-12-14 12:20
Category: PostgreSQL

<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>

[//]: <> (# Jsonb outline:- definition- usage- benchmarks- future work)
		
In this article I was going to explain why and when jsonb is better than 3NF, clarify the differences between json and jsonb.
		
# Definition
At first glance, jsonb looks like a usual json except for some differences in guts:

<script type="text/javascript">
      google.charts.load('current', {'packages':['table']});
      google.charts.setOnLoadCallback(drawTable);

      function drawTable() {
        var data = new google.visualization.DataTable();
        data.addColumn('string', 'Comment');
        data.addColumn('string', 'Example');
        data.addColumn('string', 'Json');
        data.addColumn('string', 'Jsonb');
        
        // TODO: find out how to show spaces!!!
        data.addRows([
          ['unique keys', 'select \'{"0":0, "1":1,"0":2}\'::json;','{"0":0, "1":1, "0":2}', '{"1":1, "0":2}'],
          ['no identation',  'select \'{"0":0, "1":1,        "0":2}\'::json;',  '{"0":0, "1":1,        "0":2}', '{"1":1, "0":2}']
        ]);
		
        var table = new google.visualization.Table(document.getElementById('definition_table'));

        table.draw(data, {showRowNumber: true, width: '100%', height: '100%'});
      }
</script>
<div id="definition_table"></div>


But don't be fooled by this table. Jsonb is much more complex then json.

# Usage
Long story short, I will suggest using jsonb in a case when your tables are too sparse. The following chapter will explain this.

## Project
I would like to start explanations with description of the project I used to work with.

Let's imagine that we have a beautiful project with data in [3NF][3NF], everything works fine and fast. Let's look at our beautiful table of users:

<script type="text/javascript">
      google.charts.load('current', {'packages':['table']});
      google.charts.setOnLoadCallback(drawTable);

      function drawTable() {
        var data = new google.visualization.DataTable();
        data.addColumn('string', 'Name');
        data.addColumn('number', 'Salary');
        data.addColumn('boolean', 'Full Time Employee');
        data.addRows([
          ['Mike',  {v: 10000, f: '$10,000'}, true],
          ['Jim',   {v:8000,   f: '$8,000'},  false],
          ['Alice', {v: 12500, f: '$12,500'}, true],
          ['Bob',   {v: 7000,  f: '$7,000'},  true],
        ]);

        var table = new google.visualization.Table(document.getElementById('usage_table'));

        table.draw(data, {showRowNumber: true, width: '100%', height: '100%'});
      }
</script>

<div id="usage_table"></div>

And suddenly our customer wants to add more features:

- wife's salary (should be null if a user doesn't have one)
- kids salary (should be null if a user doesn't have one)
- apartment size, squared matters (should also be null if a user doesn't have one)
- if a user is an admin - add fields like "when it became an admin" 
- if a user is an elf - add the id of his tree
- etc

So, we will have a really sparse table and here starts data science (something like information retrieval). Not the offline one - customer wants hot data and concurrent. As far as we good at googling, we find python library that perfectly fits our (customer's) demands ([pandas][pd]). After we've installed it (via [installation guide][pd_tutor]) we can see that CPU usage raised dramatically. That happens because we need to rebuild the whole table each time into feature list. One of the possible solutions is to store it in database:

<script type="text/javascript">
      google.charts.load('current', {'packages':['table']});
      google.charts.setOnLoadCallback(drawTable);

      function drawTable() {
        var data = new google.visualization.DataTable();
        data.addColumn('string', 'Name');
        data.addColumn('number', 'Salary');
        data.addColumn('boolean', 'Full Time Employee');
        data.addColumn('number', 'wife\'s salary');
        data.addColumn('number', 'kids salary');
        data.addColumn('number', 'apartment size');
        data.addColumn('string', 'etc');
        data.addRows([
          ['Mike',  {v: 10000, f: '$10,000'}, true, {v: 1000, f: '$1,000'}, {v: 15000, f: '$10,000'}, 42, '...'],
          ['Jim',   {v:8000,   f: '$8,000'},  false, {v: 8000, f: '$8,000'}, null, 100, '...'],
          ['Alice', {v: 12500, f: '$12,500'}, true, null, {v: 10000, f: '$10,000'}, 78, '...'],
          ['Bob',   {v: 7000,  f: '$7,000'},  true, null, null, null, '...'],
        ]);

        var table = new google.visualization.Table(document.getElementById('usage_table_2'));

        table.draw(data, {showRowNumber: true, width: '100%', height: '100%'});
      }
</script>

<div id="usage_table_2"></div> 

This approach has some significant drawbacks. One of them is a huge amount of fields(columns) and redundant information in tables: just imagine what happens if Make, for example, and Alice have 3 children each? All the fields our customer wanted to add will be repeated for each child:

<script type="text/javascript">
      google.charts.load('current', {'packages':['table']});
      google.charts.setOnLoadCallback(drawTable);

      function drawTable() {
        var data = new google.visualization.DataTable();
        data.addColumn('string', 'Name');
        data.addColumn('number', 'Salary');
        data.addColumn('boolean', 'Full Time Employee');
        data.addColumn('number', 'wife\'s salary');
        data.addColumn('number', 'kids salary');
        data.addColumn('number', 'apartment size');
        data.addColumn('string', 'etc');
        data.addRows([
          ['Mike',  {v: 10000, f: '$10,000'}, true, {v: 1000, f: '$1,000'}, {v: 15000, f: '$15,000'}, 42, '...'],
          ['Mike',  {v: 10000, f: '$10,000'}, true, {v: 1000, f: '$1,000'}, {v: 5000, f: '$5,000'}, 42, '...'],
          ['Mike',  {v: 10000, f: '$10,000'}, true, {v: 1000, f: '$1,000'}, {v: 23000, f: '$23,000'}, 42, '...'],
          ['Jim',   {v:8000,   f: '$8,000'},  false, {v: 8000, f: '$8,000'}, null, 100, '...'],
          ['Alice', {v: 12500, f: '$12,500'}, true, null, {v: 1000, f: '$1,000'}, 78, '...'],
          ['Alice', {v: 12500, f: '$12,500'}, true, null, {v: 4000, f: '$4,000'}, 78, '...'],
          ['Alice', {v: 12500, f: '$12,500'}, true, null, {v: 100000, f: '$100,000'}, 78, '...'],
          ['Bob',   {v: 7000,  f: '$7,000'},  true, null, null, null, '...'],
        ]);

        var table = new google.visualization.Table(document.getElementById('usage_table_3'));

        table.draw(data, {showRowNumber: true, width: '100%', height: '100%'});
      }
</script>

<div id="usage_table_3"></div>

As a result, our pretty 4 by 4 table became a 100500 by 100500 monster! 

This is where json comes. We can put all those fields (especially about kids) into json:

<script type="text/javascript">
      google.charts.load('current', {'packages':['table']});
      google.charts.setOnLoadCallback(drawTable);

      function drawTable() {
        var data = new google.visualization.DataTable();
        data.addColumn('string', 'Name');
        data.addColumn('number', 'Salary');
        data.addColumn('boolean', 'Full Time Employee');
        data.addColumn('string', 'extra fields');
        data.addRows([
          ['Mike',  {v: 10000, f: '$10,000'}, true, "{'wife\'s salary':$15,000, 'kids salary':[$1,000, $5,000, $23,000], 'apartment size':42, 'etc':'...'}"],
          ['Jim',   {v:8000,   f: '$8,000'},  false, "{'wife\'s salary':$8,000, 'apartment size':100, 'etc':'...'}"],
          ['Alice', {v: 12500, f: '$12,500'}, true, "{'wife\'s salary':$15,000, 'kids salary':[$1,000, $4,000, $100,000], 'apartment size':78, 'etc':'...'}"],
          ['Bob',   {v: 7000,  f: '$7,000'},  true, "{'etc':'...'}"],
        ]);

        var table = new google.visualization.Table(document.getElementById('usage_table_4'));

        table.draw(data, {showRowNumber: true, width: '100%', height: '100%'});
      }
</script>

<div id="usage_table_4"></div>

So, we have 5 by 4 table now.

# Benchmarks:
## without jsonb at all
The key concept of this point is to check how much space and time can jsonb save if the data in the database is hardly structured.

## json vs jsonb
Let's assume that we all agree that json and jsonb are both useful. But what is better(faster)? This question will be answered in the following benchmark. [Here][pyGen] you can find a python script I used to generate tests. Actually, all of the benchmark tests look like 
```sql
select testold('{}'::json)::json;
```
or
```sql
select testnew('{}'::jsonb);
```
Where *"testnew"* is used to test jsonb and *"testold"* is used to test json so that we can clearly define what were the results of jsonb and json.

<script type="text/javascript">
     var data;
     var chart;

      // Load the Visualization API and the piechart package.
      google.charts.load('current', {'packages':['corechart']});

      // Set a callback to run when the Google Visualization API is loaded.
      google.charts.setOnLoadCallback(drawChart);

      // Callback that creates and populates a data table,
      // instantiates the pie chart, passes in the data and
      // draws it.
      function drawChart() {
        data = new google.visualization.DataTable();
        data.addColumn('number', 'json size');
        data.addColumn('number', 'latency_old, s');
        data.addColumn('number', 'latency_new, s');
        data.addRows([
          [1,		7.208,		2.77],
          [1001,	53.411,		9.285],
          [2001,	103.929,	16.214],
          [3001,	157.989,	25.814],
          [4001,	204.865,	31.78],
          [5001,	259.243,	40.423],
          [6001,	309.912,	49.886],
          [7001,	359.798,	53.999],
          [8001,	414.597,	63.592],
          [9001,	481.893,	74.574],
          [10001,	520.906,	80.629],
          [11001,	573.934,	87.01],
          [12001,	630.937,	94.384],
          [13001,	686.475,	103.035],
          [14001,	744.054,	113.548],
          [15001,	798.305,	116.316],
          [16001,	861.136,	126.024],
          [17001,	916.432,	148.425],
          [18001,	979.769,	151.548],
          [19001,	1050.776,	161.134],
          [20001,	1084.992,	169.715],
          [21001,	1149.904,	181.003],
          [22001,	1189.699,	185.644],
          [23001,	1237.404,	192.815],
          [24001,	1298.407,	199.408],
          [25001,	1348.316,	209.455],
          [26001,	1431.793,	221.336],
          [27001,	1474.972,	219.977],
          [28001,	1510.263,	225.925],
          [29001,	1574.153,	241.067]
        ]);

        // Set chart options
        var options = {
        	title:'Differences in latency',
        	curveType: 'function',
        	legend: { position: 'right' }
            };

        // Instantiate and draw our chart, passing in some options.
        var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
        // google.visualization.events.addListener(chart, 'select', selectHandler);
        chart.draw(data, options);
      }

      function selectHandler() {
        var selectedItem = chart.getSelection()[0];
        var value = data.getValue(selectedItem.row, 0);
        alert('The user selected ' + value);
      }

</script>
    
<div id="chart_div" style="width:400; height:700"></div>


# Future work:

[//]: <> (src)
[pyGen]: https://github.com/ankarion/jsonb_plperl/blob/master/sql/bench/gen_tests.py
[jsonb_plperl]: https://github.com/ankarion/jsonb_plperl

[//]: <> (img)


[//]: <> (articles)
[3NF]: https://en.wikipedia.org/wiki/Third_normal_form
[pd]: https://pandas.pydata.org/
[pd_tutor]: 
