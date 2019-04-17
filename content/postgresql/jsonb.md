Title: Jsonb
Date: 2017-12-14 12:20
Category: PostgreSQL

<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>

[//]: <> (# Jsonb outline:- definition- usage- benchmarks- future work)

In this article, I want to introduce you a type "jsonb". It is not new, but it is frequently used type in PostgreSQL.

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

<center><div id="entities">
<table width=80%>
<tr>
<td><b>users:</b><div id="normalization_table_1"></div></td>
<td></td>
<td><b>kids:</b><div id="normalization_table_2"></div></td>
</tr>
</table></div></center>

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


[//]: <> (src)
[pyGen]: https://github.com/ankarion/jsonb_plperl/blob/master/sql/bench/gen_tests.py
[jsonb_plperl]: https://github.com/ankarion/jsonb_plperl

[//]: <> (img)


[//]: <> (articles)
[3NF]: https://en.wikipedia.org/wiki/Third_normal_form
[jsonb]: https://www.postgresql.org/docs/9.6/static/functions-json.html
