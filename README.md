# Sheet to triples

Experiment for simple translation from spreadsheets (for collaborative data editing) to triples (for use in shared meaning platform). The aim was to produce a quick tool to help explore a few questions in advance of attempting a more complete solutions:

* Implement enough of the process flow to try out on real projects
* Sanity check the complexity of a transform interface
* Test practicality of transform editing by non-technical colleagues
* Find points of friction going from flat editing to graph data items

For more rigorous approaches along similar lines, see [TARQL](#tarql) and [RML](#rml).


## Why

Building a Visual Meaning zoomable map involves a lot of listening, note taking, diagramming, art production, and quite often assembling of information in spreadsheets. What we'd like to include in the final result is semantically sensible entities and relationships that can be explored in conjunction with the artwork.

Current practice - of manually doing yet another translation from the notes or spreadsheet into form fields for a few different specific schemas is slow, prone to errors, and makes later edit in response to feedback onerous.

One option is creating a flexible editing interface that matches the final data model. Prior art on this is not encouraging - graph and schema authoring tools are not known for being user friendly.

What if instead we collect and edit the information the same way, and write a custom transform for different kinds of data that lets us reshape the flat structure into predicates and objects that relate into the rest of the constructed model.


## Implementation

What the code in this repo actually does!

In order to install all required Python packages, run the following command :

```
pip install -r requirements.txt
```

### Command

The tool can be used as such:

    $ python3 -m sheet_to_triples --model Model.json --book Markers.xlsx \
      --model-out New.json --verbose t_one t_two

Here the command takes inputs `Model.json` and `Markers.xlsx` then applies two named transforms `t_one` and `t_two` and produces an updated output `New.json` model.

For expediency, this is closely matched to immediate Visual Meaning needs. For instance an existing model is given as a JSON file containing a 'triples' key with specific content, rather than a standard format. The transforms are simplistic custom format using Python data syntax.

See help for more arguments usage:

    $ python3 -m sheet_to_triples --help

Because seeing a model in Turtle format turned out to be useful, can get that by just not supplying a transform:

    $ python3 -m sheet_to_triples --model eco_five.json --verbose

Would be nice to just have an 'identity' transform, but the lack of clarity between appending to the model vs replacing it complicates what the command output should do.

The tool looks for transform files inside the directory path specified by the `TRANSFORMS_DIR` environment variable. If unset, this will default to a folder called `transforms` inside the current working directory.

### Transform shape

The initial idea for the transform format was to just have data as triples, and use a little custom string interpolation using Python format strings for all logic. In use, this expanded to include means to bind variables and queries.

The top level attributes of a transform are:

* `name`

  Taken from the filename rather than in the file.
* `sheet: str`

  Name of the sheet/tab to look for the related data in a workbook.
* `data: Union[List[Tuple[str, ...]], List[Dict[str, str]]]`

  Alternative to providing `sheet` just give an inline list for rows.
* `lets: Dict[str, str_template]`

  Bind variables which will be set for each row.

* `conds: Dict[str, Tuple(str_template, str_template, str_template)]`

  Variables that are the result of some conditional. The first item in the tuple is the condition, evaluated with `Cell` methods such as `exists`. The second item is the value if True, and the third item is the value if False.

* `query: Dict[str, str_query]`

  Bind result of query to be run for each row.
* `triples: List[Tuple[str_template, str_template, str_template]]`

  Output triples to create and be added to model.
* `non_unique: List[str_predicate, ...]`

  Normally triples are assumed unique for the first two items in each triple (subject predicate). If multiple triples have the same subject-predicate pairing, the oldest triple will be dropped and replaced with the newest one. By adding a predicate to `non_unique` it is treated as non-unique, and only duplicates of the full `(subject, predicate, object)` triple will be dropped.
* `allow_empty_subject: bool`

  By default, an exception is raised if any triple does not have a subject. If this flag is set to `True` instead that triple is just omitted from the output.
* `skip_empty_rows: bool`

  By default the first empty row found in a sheet is treated as the EOF and row parsing will halt if one is encountered. If this flag is set to `True` then empty rows will be skipped over instead and the entire sheet will be parsed.
* `sheet_encoding: str_encoding`

  For tabular input data that does not include the text encoding as part of the format, for instance CSV, the name of the Python encoding to decode the content using. By default 'utf-8' is used, and an exception is thrown for invalid content.
* (provisional) `melt_cols: List[str]`

  If supplied, process triples not only for each row, but for each row/column pair by multiplying the columns given in this value. Including `melt_cols` will cause an additional column to be added to every row called `_has_melt`, which is a boolean value indicating whether this row contains melted values or not. If `_has_melt` is True, two further columns will be added, `_melt_colname` and `_melt_value`, which contain the column-value pairings for this row for each column in `melt_cols`.


## Findings

What are the answers to our questions from the start.

### Real use

Actually using the translations on projects lead to a number of changes to the transform format and command line parameters over time. We also shipped finished maps, with content from external contributors, while integrating with data input through the exiting editing interface.

People use cell colours to mean things and communicate during editing, or put parenthetical statements behind the cell values. The translation still works, but may not be as intended.

Getting geopoints off the map and into the spreadsheet is painful. This is known, but to fix we must discard manual layout in general, record the position of entities in the map, and automatically position new entities by their direct relations.

### Transform complexity

The transforms created are all pretty simple, though not exactly self-describing. Including a SPARQL query to do relation linking is not ideal, alternatives would be possible.

There's a core tension between using fields that carry a lot of information (like markdown text) versus using very granular, simple values, with many more relationships. Splitting at the transform stage is hard - it makes sense to encourage more columns, even sparse ones, at the spreadsheet stage.

Some things would be nice but were not essential, like having a means to map a set of cell values to some other arbitrary result values.

The transform language cannot actually be authored by untrusted sources without sandboxing, it's possible to escape via format strings, and I doubt SPARQL in RDFlib is safe either. This is fine, it's in declarative form for other reasons.

### Transform editing

Just using Python literal syntax (as can be understood by `ast.literal_eval()`) made it easy for me, though probably no one else. Lint via `flake8` offers reasonable validation.

Adapting existing rules was possible with minimal explanation of the syntax, though there are still many runtime errors that can escape. The transform code chooses to make missing subjects or predicates a transform-time error, but missing objects acceptable and cause no triple to be generated. It is easy to typo the value of a query, and not obvious from the transform result when a spreadsheet cell should be edited to match existing data.

Debuggability is key, but difficult to implement well, particularly when the result is missing or mismatched data rather than an exception.


### Frictions

What specifically came up as problems to keep in mind for the future.

#### Generating IRIs is still hard

To reference or give properties to a thing in RDF, you must create a unique identifier for it in your namespace (or use an existing one). There is surprisingly little practical advice about how to do this well. The problem also awkwardly straddles authorship, curation, and transform spaces.

In general, one row in a spreadsheet results in one new entity, and one field from the row is a name or other sensible identifier-ish sort of value, but may not be unique, and can change during editing. Just using row number, or generated unique id, has obvious issues when the input sheet will be edited over time but must continue to relate to the graph produced.

As implemented, one or more fields can be used by the transform to create the IRI (with some optional sluggification to hopefully make it less ugly). Editing problems are not yet tackled, the new values are thrown away each run, but could be handled by retaining the old id and relating with a same-as type property to preserve as an alias.

#### SPARQL ain't great

SQL is not the best part of relational databases, and by emulating the syntax for SPARQL you get cognitively complex statements for even quite simple graph operations.

The initial plan was not to do queries at all, just do path resolution, but turned out queries (or at least predicate support) made sense to add. Most parts of the transform can be simpler, but mapping an existing copy of the graph is handy particularly to let the spreadsheet authors use labels rather than IRIs to create relationships.

#### Stringly typed holes

The input graph data comes in JSON as strings, and the translation steps use Python format strings. The most common use of types in RDF looks like what you get trying to stuff Java into an XML shaped hole.

The main upshot of this awkwardness is that while we care what is an identifier and what is a literal, that's nearly the complete toolset we have to work with, and even to get that there's a lot of inferring from the content of values. If a string starts with something that might be a namespace prefix or a scheme, we'll cast it to Identifier? Is all a bit ick.

During one transform step, a value might be cast back and forth from string needlessly, just because the basic unit of composition in the transform is string interpolation.

Using mini-languages as cell and triple values is reasonable and pragmatic, but having them all as string values means treating them mostly as opaque. For geopoints specifically, it made sense to add an explicit bit of handling in Python to validate and reshape, but it would be nice to just take that from the predicate rather than making it something each transform has to care about.

#### Add or replace?

The core use case for these projects was augmenting an existing set of triples with some new data from table rows, and then updating when the table rows changed.

As the transforms a designed to be run as a repeatable process, that leaves the interesting question of where does the responsibility for removing any old data from the last transform lie?

The bad answer at present is some things are just coded to be stripped after loading the existing model. A better one would be you could write a transform to remove items as well as add them, or should be explicit about keeping all the other triples.

Final nice option could be to track (perhaps automatically, with git) the provenance of added data, and use that to inform how new data is integrated.

#### Result stability

There are a lot of different triple serialisation formats. There's academic work on creating canonical graphs, considering blank nodes and various other complications. There's surprisingly little information about just writing your triples out in a consistent order.

Turtle is nice because it's actually towards human readable in ways the earlier formats fail horribly at, but the RDFlib serialisation is perplexingly ordered. Did you guess classes first, then subjects by most referenced? The fix is probably to write a new plugin that subclasses and just does by subject then predicate lexically.

Also ended up writing some horrible code to tweak output order - due to poor IRI design earlier, not having finished another authoring feature, and lists in RDF being a bother.


## Unimplemented

There are some obvious features that are not yet worth implementing.

Downloading the spreadsheet is an unnecessary step. Using the Google Sheets api or Microsoft Graph is an obvious next step. Requires tackling authentication, but enables use in other contexts as well.

Triggering a data load from button in the platform, rather than needing to run locally, would put the power of update into the right hands. Could even just run periodically as a sync.

We don't make much use of common schemas or vocabularies yet. That should adapt with time, at least picking up some Dublin Core, and perhaps a whole base ontology.

The library to do the translations is in the same repo as the translations being authored, simply as a convenience while experimenting. It would make sense to split them.


## Alternatives

Rather than use this code, what can we do instead?

### TARQL

Tool to convert CSV to RDF with SQARQL transform syntax.

Main issue is many forms of basic logic are painful to express, and authoring relies on database query language knowledge. There is no obvious way to populate values based on a query from an existing graph. Producing SPARQL output for a meta-transform for variations by a few properties, or just binding of extra variables from the command line tool, also seems tricky.

There is a Python implementation - by a company we like - that would be pretty easy to adopt and extend.


### RML

A draft specification of a generic mapping to the RDF data model, building on the R2RML recommendation for mapping from relational data.

The transform is written in the syntax of the output (a graph) with logic bound to specific namespaces. From XSLT, this is likely a good design choice, though does tend to mean verbose syntax, and challenges with extensibility when the limits of the core operators are hit.

The team have a bunch of interesting publications, and some tooling - mostly in Java.


### YARRRML

With RML but into a YAML syntax, and under the same umbrella.


### Don't do that then

Is encouraging editing of flat formats in order to generate graph data even sensible?

The general assumption is that end users will interface through to graphs only by custom built interfaces that provide context specific views, or that graphs will be built by experts out of limited cues provided in data in other formats.


## References

* Tarql: SPARQL for Tables

  https://tarql.github.io/
* Python implementation of TARQL, based on RDFLib.

  https://github.com/semanticarts/pytarql
* R2RML: RDB to RDF Mapping Language

  W3C Recommendation 27 September 2012

  https://www.w3.org/TR/r2rml/
* RDF Mapping Language (RML)

  Unofficial Draft 15 July 2020

  https://rml.io/specs/rml/
* YARRRML

  Unofficial Draft 27 August 2020

  https://rml.io/yarrrml/spec/
* SPARQL 1.1 Query Results CSV and TSV Formats

  W3C Recommendation 21 March 2013

  https://www.w3.org/TR/sparql11-results-csv-tsv/
* RDF 1.1 Turtle

  Terse RDF Triple Language

  W3C Recommendation 25 February 2014

  https://www.w3.org/TR/turtle/
* RDFlib - pure Python package for working with RDF

  https://rdflib.readthedocs.io/
* Quit Store (Quads in Git)

  https://github.com/AKSW/QuitStore
* Stringly Typed

  https://wiki.c2.com/?StringlyTyped
* Google Sheets API v4

  https://developers.google.com/sheets/api
* Excel workbooks and charts API overview

  https://docs.microsoft.com/en-us/graph/excel-concept-overview
* XSL Transformations (XSLT)

  Version 1.0 _(the good bit)_

  https://www.w3.org/TR/1999/REC-xslt-19991116
* Wikidata

  https://www.wikidata.org/
