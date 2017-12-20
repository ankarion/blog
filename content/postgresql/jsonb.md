Title: Jsonb
Date: 2017-12-14 12:20
Category: PostgreSQL

<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>

[//]: <> (# Jsonb outline:- definition- usage- benchmarks- future work)

# Outline
	
- **definition** section contains link to official documentation and some thoughts about it.
- **usage** section - for those who was interested in usage of jsonb. It contains description of the project I used to work with and some comments on how it should be implemented.
- **benchmarks** - contains velocity comparison of jsonb and json.
		
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
          ['unique keys', 'select \'{"0":0, "1":1, "0":2}\'::json;','{"0":0, "1":1, "0":2}', '{"1":1, "0":2}'],
          ['no identation',  'select \'{"0":0, "1":1,&nbsp;&nbsp;&nbsp;&nbsp;"0":2}\'::json;',  '{"0":0, "1":1, &nbsp;&nbsp;&nbsp;&nbsp;"0":2}', '{"1":1, "0":2}']
        ]);
		
        var table = new google.visualization.Table(document.getElementById('definition_table'));

        table.draw(data, {showRowNumber: true, width: '100%', height: '100%', allowHtml: true});
      }
</script>
<div id="definition_table"></div>


But don't be fooled by this data. Jsonb is much more complex then json. [Here][jsonb] you can find full definition of jsonb.

# Usage
Long story short, I will suggest using jsonb in case when your tables are too sparse. The following chapter will explain this.

## Project
Let's imagine that we have a beautiful project with data in [3NF][3NF], everything works fine and fast. Let's look at our beautiful table of **users**:

<script type="text/javascript">
      google.charts.load('current', {'packages':['table']});
      google.charts.setOnLoadCallback(drawTable);

      function drawTable() {
        var data = new google.visualization.DataTable();
        data.addColumn('string', 'Name');
        data.addColumn('number', 'Salary');
        data.addRows([
          ['Mike',  {v: 10000, f: '$10,000'}],
          ['Jim',   {v:8000,   f: '$8,000'}],
          ['Alice', {v: 12500, f: '$12,500'}],
          ['Bob',   {v: 7000,  f: '$7,000'}],
        ]);

        var table = new google.visualization.Table(document.getElementById('usage_table'));

        table.draw(data, {showRowNumber: true, width: '30%', height: '30%'});
      }
</script>
<center>
<div id="usage_table"></div>
</center>

And suddenly our customer wants to add more features:

- wife's salary (should be null if a user doesn't have one)
- kid's salary (should be null if a user doesn't have one)
- apartment size square meters (should also be null if a user doesn't have one)
- if a user is an admin - add fields like "when it became an admin" 
- if a user is an elf - add the id of his tree
- etc

Adding all those field to the table has some significant drawbacks. One of them is a huge amount of fields(columns) and redundant information in tables: just imagine what happens if Mike, for example, and Alice have 3 children each? All the fields our customer wanted to add will be repeated for each child:

<script type="text/javascript">
      google.charts.load('current', {'packages':['table']});
      google.charts.setOnLoadCallback(drawTable);

      function drawTable() {
        var data = new google.visualization.DataTable();
        data.addColumn('string', 'Name');
        data.addColumn('number', 'Salary');
        data.addColumn('number', 'wife\'s salary');
        data.addColumn('number', 'kids salary');
        data.addColumn('number', 'apartment size');
        data.addColumn('string', 'etc');
        data.addRows([
          ['Mike',  {v: 10000, f: '$10,000'},  {v: 1000, f: '$1,000'}, {v: 15000, f: '$15,000'}, 42, '...'],
          ['Mike',  {v: 10000, f: '$10,000'},  {v: 1000, f: '$1,000'}, {v: 5000, f: '$5,000'}, 42, '...'],
          ['Mike',  {v: 10000, f: '$10,000'},  {v: 1000, f: '$1,000'}, {v: 23000, f: '$23,000'}, 42, '...'],
          ['Jim',   {v:8000,   f: '$8,000'},   {v: 8000, f: '$8,000'}, null, 100, '...'],
          ['Alice', {v: 12500, f: '$12,500'},  null, {v: 15000, f: '$15,000'}, 78, '...'],
          ['Alice', {v: 12500, f: '$12,500'},  null, {v: 4000, f: '$4,000'}, 78, '...'],
          ['Alice', {v: 12500, f: '$12,500'},  null, {v: 100000, f: '$100,000'}, 78, '...'],
          ['Bob',   {v: 7000,  f: '$7,000'},   null, null, null, '...'],
        ]);

        var table = new google.visualization.Table(document.getElementById('usage_table_3'));

        table.draw(data, {showRowNumber: true, width: '90%', height: '90%'});
      }
</script>
<center>
<div id="usage_table_3"></div>
</center>

As a result, our pretty 4 by 4 table became a 100500 by 100500 monster! We can fix it in 2 different ways: normalization or jsonb.

### Normalization
The first idea is to return data back to [3NF][3NF] in order to reduce sizes of that monster.

<script type="text/javascript">
      google.charts.load('current', {'packages':['table']});
      google.charts.setOnLoadCallback(drawTable);

      function drawTable() {
        var data1 = new google.visualization.DataTable();
        data1.addColumn('string', 'Name');
        data1.addColumn('number', 'Salary');
        data1.addColumn('number', 'Wife');
        data1.addColumn('number', 'apartment size');
        data1.addColumn('string', 'etc');
        data1.addRows([
          ['Mike',  {v: 10000, f: '$10,000'}, 3, 42, '...'],
          ['Jim',   {v:8000,   f: '$8,000'},  null, 100, '...'],
          ['Alice', {v: 12500, f: '$12,500'}, null, 78, '...'],
          ['Bob',   {v: 7000,  f: '$7,000'},  null, null, '...'],
        ]);

        var table = new google.visualization.Table(document.getElementById('normalization_table_1'));

        table.draw(data1, {showRowNumber: true, width: '100%', height: '100%'});
        
        var data2 = new google.visualization.DataTable();
        data2.addColumn('number', 'Salary');
        data2.addColumn('number', 'Parent 1');
        data2.addColumn('number', 'Parent 2');
        data2.addColumn('string', 'etc');
        data2.addRows([
          [{v: 15000, f: '$15,000'}, 1, 3, '...'],
          [{v: 5000, f: '$5,000'}, 1, null, '...'],
          [{v: 23000, f: '$23,000'}, 1, null, '...'],
          [{v: 100000, f: '$100,000'}, 3, null, '...'],
          [{v: 4000,  f: '$4,000'},  3, null, '...'],
        ]);

        var table = new google.visualization.Table(document.getElementById('normalization_table_2'));

        table.draw(data2, {showRowNumber: true, width: '100%', height: '100%'});
      }
</script>

<center><div id="entities"></div></center>
<table>
<tr>
<td><b>users:</b><div id="normalization_table_1"></div></td>
<td><b>kids:</b><div id="normalization_table_2"></div></td>
</tr>
</table>

As you can see in the example, Mike has a wife(Alice) and they have only one kid with salary $15,000, but they have 2 more kids from other marriage.

<!-- TODO: add more tables -->

We'll have about 100500 different tables with 2-3 tuples. The problem we can run into is a complexity of joins. Let's look at other solution.

### Jsonb

This is where json comes. We can put all those fields (especially about kids) into json:

<script type="text/javascript">
      google.charts.load('current', {'packages':['table']});
      google.charts.setOnLoadCallback(drawTable);

      function drawTable() {
        var data = new google.visualization.DataTable();
        data.addColumn('string', 'Name');
        data.addColumn('number', 'Salary');
        data.addColumn('string', 'extra fields');
        data.addRows([
          ['Mike',  {v: 10000, f: '$10,000'},  "{'wife\'s salary':$15,000, 'kids salary':[$1,000, $5,000, $23,000], 'apartment size':42, 'etc':'...'}"],
          ['Jim',   {v:8000,   f: '$8,000'},   "{'wife\'s salary':$8,000, 'apartment size':100, 'etc':'...'}"],
          ['Alice', {v: 12500, f: '$12,500'},  "{'wife\'s salary':$15,000, 'kids salary':[$1,000, $4,000, $100,000], 'apartment size':78, 'etc':'...'}"],
          ['Bob',   {v: 7000,  f: '$7,000'},   "{'etc':'...'}"],
        ]);

        var table = new google.visualization.Table(document.getElementById('usage_table_4'));

        table.draw(data, {showRowNumber: true, width: '100%', height: '100%'});
      }
</script>

<div id="usage_table_4"></div>

So, we have 5 by 4 table now.

# Benchmarks:
Let's assume that we all agree that json and jsonb are both useful. But what is better(faster)? This question will be answered in the following benchmark. [Here][pyGen] you can find a python script I used to generate tests. 

Benchmarking proccesss is divided into two stages: 

- the init part, which is not going to be taken into account.
- the workload part, which is going to be evaluated.

In "init" part, we initialize the functions which transforms objects into perl and then parses it back to plpgsql language:
```sql
CREATE EXTENSION jsonb_plperlu CASCADE;

CREATE FUNCTION test1(val jsonb) RETURNS jsonb
LANGUAGE plperlu
TRANSFORM FOR TYPE jsonb
AS $$
return (%_[0]);
$$;

CREATE FUNCTION test2(val text) RETURNS text
LANGUAGE plperlu
AS $$
use JSON;
my $hash = decode_json($_[0]);
return encode_json $hash;
$$;
```

The workload looks like 
```sql
select testold('{}'::json)::json;
```
or
```sql
select testnew('{}'::jsonb);
```

<script type="text/javascript">
     var data;
     var chart;

      // Load the Visualization API and the piechart package.
      google.charts.load('current', {'packages':['line']});

      // Set a callback to run when the Google Visualization API is loaded.
      google.charts.setOnLoadCallback(drawChart);

      // Callback that creates and populates a data table,
      // instantiates the pie chart, passes in the data and
      // draws it.
      function drawChart() {
        data = new google.visualization.DataTable();
        data.addColumn('number', 'json size');
        data.addColumn('number', 'latency_old');
        data.addColumn('number', 'latency_new');
        data.addRows([
          [{v:1,f:'1 object'},		{v:7.208,f:'0.007208s'}, {v:2.77,f:'0.00277s'}],
          [{v:1001,f:'1001 objects'},	{v:53.411,f:'0.053411s'}, {v:9.285,f:'0.009285s'}],
          [{v:2001,f:'2001 objects'},	{v:103.929,f:'0.103929s'}, {v:16.214,f:'0.016214s'}],
          [{v:3001,f:'3001 objects'},	{v:157.989,f:'0.157989s'}, {v:25.814,f:'0.025814s'}],
          [{v:4001,f:'4001 objects'},	{v:204.865,f:'0.204865s'}, {v:31.78,f:'0.03178s'}],
          [{v:5001,f:'5001 objects'},	{v:259.243,f:'0.259243s'}, {v:40.423,f:'0.040423s'}],
          [{v:6001,f:'6001 objects'},	{v:309.912,f:'0.309912s'}, {v:49.886,f:'0.049886s'}],
          [{v:7001,f:'7001 objects'},	{v:359.798,f:'0.359798s'}, {v:53.999,f:'0.053999s'}],
          [{v:8001,f:'8001 objects'},	{v:414.597,f:'0.414597s'}, {v:63.592,f:'0.063592s'}],
          [{v:9001,f:'9001 objects'},	{v:481.893,f:'0.481893s'}, {v:74.574,f:'0.074574s'}],
          [{v:10001,f:'10001 objects'},	{v:520.906,f:'0.520906s'}, {v:80.629,f:'0.080629s'}],
          [{v:11001,f:'11001 objects'},	{v:573.934,f:'0.573934s'}, {v:87.01,f:'0.08701s'}],
          [{v:12001,f:'12001 objects'},	{v:630.937,f:'0.630937s'}, {v:94.384,f:'0.094384s'}],
          [{v:13001,f:'13001 objects'},	{v:686.475,f:'0.686475s'}, {v:103.035,f:'0.103035s'}],
          [{v:14001,f:'14001 objects'},	{v:744.054,f:'0.744054s'}, {v:113.548,f:'0.113548s'}],
          [{v:15001,f:'15001 objects'},	{v:798.305,f:'0.798305s'}, {v:116.316,f:'0.116316s'}],
          [{v:16001,f:'16001 objects'},	{v:861.136,f:'0.861136s'}, {v:126.024,f:'0.126024s'}],
          [{v:17001,f:'17001 objects'},	{v:916.432,f:'0.916432s'}, {v:148.425,f:'0.148425s'}],
          [{v:18001,f:'18001 objects'},	{v:979.769,f:'0.979769s'}, {v:151.548,f:'0.151548s'}],
          [{v:19001,f:'19001 objects'},	{v:1050.776,f:'1.050776s'}, {v:161.134,f:'0.161134s'}],
          [{v:20001,f:'20001 objects'},	{v:1084.992,f:'1.084992s'}, {v:169.715,f:'0.169715s'}],
          [{v:21001,f:'21001 objects'},	{v:1149.904,f:'1.149904s'}, {v:181.003,f:'0.181003s'}],
          [{v:22001,f:'22001 objects'},	{v:1189.699,f:'1.189699s'}, {v:185.644,f:'0.185644s'}],
          [{v:23001,f:'23001 objects'},	{v:1237.404,f:'1.237404s'}, {v:192.815,f:'0.192815s'}],
          [{v:24001,f:'24001 objects'},	{v:1298.407,f:'1.298407s'}, {v:199.408,f:'0.199408s'}],
          [{v:25001,f:'25001 objects'},	{v:1348.316,f:'1.348316s'}, {v:209.455,f:'0.209455s'}],
          [{v:26001,f:'26001 objects'},	{v:1431.793,f:'1.431793s'}, {v:221.336,f:'0.221336s'}],
          [{v:27001,f:'27001 objects'},	{v:1474.972,f:'1.474972s'}, {v:219.977,f:'0.219977s'}],
          [{v:28001,f:'28001 objects'},	{v:1510.263,f:'1.510263s'}, {v:225.925,f:'0.225925s'}],
          [{v:29001,f:'29001 objects'},	{v:1574.153,f:'1.574153s'}, {v:241.067,f:'0.241067s'}]
        ]);

        // Set chart options
        var options = {
        	hAxis: {
		      title: 'Json size',
		      gridlines:{
		      	count: 3,
		      	color: '#CCC'
		      	}
		    },
		    vAxis: {
		      title: 'Latency, msec',
		      gridlines:{
		      	count: 3,
		      	color: '#CCC'
		      	}
		    }
            };

        // Instantiate and draw our chart, passing in some options.
        var chart = new google.charts.Line(document.getElementById('chart_div'));
        // google.visualization.events.addListener(chart, 'select', selectHandler);
        chart.draw(data, google.charts.Line.convertOptions(options));
      }

      function selectHandler() {
        var selectedItem = chart.getSelection()[0];
        var value = data.getValue(selectedItem.row, 0);
        alert('The user selected ' + value);
      }

</script>

<center>
<div id="chart_div" style="width:90%; height:700"></div>
</center>


[//]: <> (src)
[pyGen]: https://github.com/ankarion/jsonb_plperl/blob/master/sql/bench/gen_tests.py
[jsonb_plperl]: https://github.com/ankarion/jsonb_plperl

[//]: <> (img)


[//]: <> (articles)
[3NF]: https://en.wikipedia.org/wiki/Third_normal_form
[pd]: https://pandas.pydata.org/
[jsonb]: https://www.postgresql.org/docs/9.6/static/functions-json.html
[pd_tutor]: 
