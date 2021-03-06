Title: Transform
Date: 2017-12-20 12:20
Category: PostgreSQL
Status: published

<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>

# Preface
Jsonb is not a new feature in PostgreSQL and you can easily find some articles by just [googling it][jsonbLMGTFY](even I have one in drafts). But while writing my jsonb article, I found out that I couldn't find a proper way of working with jsonb inside [triggers][triggers].

After googling for a few seconds I thought "Meh, I've tried. Maybe it is easier to write my own way of working with jsonb."

## My own way of working with jsonb
So, I'm happy to introduce you the "My own way of working with jsonb". The idea is to take a json as the incoming parameter(which in perl is $_[0]) and inside the function parse it into the desired object. TA-dah!

```perl
use JSON;
my $hash = decode_json($_[0]);
```

Well... In the end, it became obvious that this is not the best solution because PostgreSQL 9.5+ provides ["create transform"][transform] functionality which is supposed to work better.

# Intro
This article is dedicated to [transforms][transform] and designed in order to save you from some possible mistakes. I will show what "transform" is and how to use it on a simple artificial example, at the end of this article there is a "benchmark" section which will compare **jsonb + transform** vs **json + decode_hash** (which was described in "Preface" part)

# Definition
[Transforms][transform] are supposed to define the way PostgreSQL object can be represented in certain language. 
For example, we want to represent PostgreSQL type "hstore" as a perl type. This can be done through 4 lines of SQL code:

```sql 
CREATE TRANSFORM FOR hstore LANGUAGE pl/perl (
	FROM SQL WITH FUNCTION name_of_function_from_sql (name_of_the_argument [, ...]),
    TO SQL WITH FUNCTION name_of_function_to_sql (name_of_the_argument [, ...])
)
```

The problem is that we have to define those two functions ["name_of_function_from_sql"][hstore_plperl_from_sql] and ["name_of_function_to_sql"][hstore_plperl_to_sql]. They describe the way the object will be transformed.

It is not always the easiest solution, but the good news is that some transforms are already implemented. Jsonb can be transformed [into python][jsonb_plpython] and [into perl][jsonb_plperl] (feel free to check it out and participate in [perl][commit_fest_pe] and [python][commit_fest_py] patch discussions). 

So, the only thing you need to do is to install an extension:

```sql
create extension jsonb_plperl;
```

And show that transform should be used in the definition of the function:

```sql
TRANSFORM FOR TYPE jsonb
```

Full SQL code should look like this:

```sql
CREATE EXTENSION jsonb_plperl CASCADE;

CREATE FUNCTION blah(val jsonb) RETURNS jsonb
LANGUAGE plperl
TRANSFORM FOR TYPE jsonb
AS $$
	$val = $_[0];
	...
	return $val;
$$;
```

# Benchmarks
This is the most spectacular part of this article. We are going to find out which method is better(faster) - the old one or the "transform". 

Benchmarking process is divided into two stages: 

- the init part
- the workload part

## Init
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

## Workloads
Taking into account the init part, workloads look like:

```sql
select testold('{...}'::json)::json;
```

and

```sql
select testnew('{...}'::jsonb);
```

Where {...} - is json which contains strings associated with it's int representation. For example:

```sql
{
	"1":1,
	"2":2,
	etc
}
```

[Here][pyGen] you can find a python script I used to generate workloads. Important thing to note before running the script - you need to create a directory called "tests" inside the directory where gen_tests.py is located.

## Results

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
        data.addColumn('number', 'bad practise');
        data.addColumn('number', 'transform');
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

On this chart, you can see how bad was my first approach in comparison with transform. The higher graph values go, the more milliseconds corresponding method worked.

The "bad practice" is the first approach I've been talking about. As you can see, "transform" grows slower, which means that "transform" approach works a lot faster. This is the reason why I called "bad practice" bad.

[//]: <> (sources)
[pyGen]: https://github.com/ankarion/jsonb_plperl/blob/master/sql/bench/gen_tests.py
[jsonb_plpython]: https://github.com/postgrespro/jsonb_plpython
[jsonb_plperl]: https://github.com/ankarion/jsonb_plperl
[commit_fest_pe]: https://www.postgresql.org/message-id/flat/20171024140129.6bd01f68@anthony-24-g082ur#20171024140129.6bd01f68@anthony-24-g082ur
[commit_fest_py]: https://www.postgresql.org/message-id/flat/20171025145100.3a19933f@anthony-24-g082ur/
[hstore_plperl_to_sql]: https://github.com/postgres/postgres/blob/master/contrib/hstore_plperl/hstore_plperl.c#L101
[hstore_plperl_from_sql]: https://github.com/postgres/postgres/blob/master/contrib/hstore_plperl/hstore_plperl.c#L68

[//]: <> (images)


[//]: <> (articles)
[3NF]: https://en.wikipedia.org/wiki/Third_normal_form
[pd]: https://pandas.pydata.org/
[jsonb]: https://www.postgresql.org/docs/9.6/static/functions-json.html
[jsonbArt]: https://ankarion.github.io/blog/jsonb.html
[jsonbLMGTFY]: http://lmgtfy.com/?q=jsonb+postgresql
[triggers]: https://www.postgresql.org/docs/9.1/static/sql-createtrigger.html
[transform]: https://www.postgresql.org/docs/9.5/static/sql-createtransform.html
