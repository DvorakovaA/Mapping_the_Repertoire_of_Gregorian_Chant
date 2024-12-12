## ChantMapper development documentation

This project is a web application for musicologists - gregorianists developed using the Django framework. The installation process for local use is outlined in the file `installation_instructions.md` otherwise it can be reached at https://dominant-highly-bluejay.ngrok-free.app/map_repertoire/. 

The software can be divided into two fundamental units: the backend and the frontend. The specific functions and interactions of these units within the tool are illustrated in the following diagram. 

![app_schema](pics\app_schema.png "Schema of ")

The term backend is used to describe the component of an application that operates in the background. This component is responsible for handling data and database management tasks that are too computationally demanding for the frontend to process, as well as any operations that have a reference implementation in Python.
In this context, its function is to identify and represent the relevant community repertoire.

In contrast, the frontend is responsible for providing the user interface.
Through this interface, queries are submitted and the corresponding results are displayed by the backend. In this tool, the frontend is responsible for displaying the query form and for constructing the table of results as well as handling the results maps. Communication with the user is conducted via a web browser. When the web application is executed locally, the home page is accessible at the default URL of Django: http://127.0.0.1:8000/.

The application is programmed in the Django framework (https://www.djangoproject.com/) in Python. The backend uses a number of Python libraries. The frontend is designed using the Django template system, but uses the javascript framework Bootstrap (https://getbootstrap.com/) for the visual appearance of the page and the leaflet (https://leafletjs.com/) library for the map functionality.


### Data and its storage

We use the SQLite database technology for data storage.(https://www.sqlite.org/). It is a lightweight and standalone database engine that is simple to use.
We have a predefined database designed for the backend. A significant drawback of SQLite is its low performance.
However, since our use case is not that data flow intensive, 
we did not find it necessary to change the default solution provided by Django.

Main data source, besides data from users, are CSV data files in data directory. We distinguish between given (original CSV files from DACT scrape of Cantus Index) and generated files (derived from given files to make database load easier via `scripts\new_csv.py` script). From them we take specific columns to fill in app database as shown in following database schema. 

![db_schema](pics\db_schema.png "Schema of database")

The prescriptions of the individual tables from the referenced schema are located within the models.py file. Each table is a class of the type Model and the individual columns of the table are its attributes. In addition to the individual fields and their data types, the classes also describe the behaviour to be adopted in the event of a missing value (in the case of a field that permits the input of a null value).

The transfer of data from the corresponding CVS files into the database is accomplished through the execution of the `scripts\load_csv.py` script. This script employs the Pandas library (https://pandas.pydata.org/) to load and save the files via models into the database (`db\db.sqlite3`). We do not use all columns from source files, just those corresponding to presented schema are required.


### Backend

As mentioned above, the term backend means the part of the application that is responsible for data management (database) and calculations. We decided to create this part of the software using Python. 
We chose it because it has available and easy-to-use reference implementations of all the methods we want to use, and also because it is the most widely used programming language in the digital humanities community.

The backend is based on the Django web framework in Python. It allows us to write web applications quickly and with a focus on the application itself, while taking care of the~uniform (tedious) parts of web development, for which it provides us with an accessible abstraction. 

Each Djnago project is composed of parts called app (applications). These are individual self-contained pieces of software where each provides its own functionality. 
They can be easily moved between different projects due to the modularity of Django. In our case, we have only one app in the `Gregorian\_chant\_repertoire project: Map\_repertoire`. 
Its involvement in the project is specified in the `settings.py` and `urls.py` files of the project.

Another web development task where Django is involved as great help is processing of forms.
In `forms.py` class for each form type in app is specified (e. g. `UploadDatasetForm`) with requierements for fields, introduced options for selection fields (e.g. which column from which database table), set options names etc. Then in frontend creation and handling of forms is done just by creating class instance and all handeling is covered as specified in python class definition.


#### Computations provided by backend
The computational part of the backend consists of functions in four files:
- `communities.py`
    - its main function is `get_communites` 
    - for given parameters comming form users request such as officia, feasts and community detection method gets data from database and provides communities, edges and significance level 
    - community detection methods implemeted are:
        - Topic modeling - 2, 5, 10 and 20 topics (models trained on 250 sources from Cantus Index, LDA implementation from `scikit-learn` library)
        - Louvain algorithm - with resolution 1.0 (implementation from `networkx` library)
        - CAT based principle - we consider comminuty those sources, whose chants are equal sets

- `map_construct.py`
    - its main function is `get_map_data`
    - based on the found communities it prepares with querying the database a data structure (dictionary) for Javascript functions creating maps

- `table_construct.py`
    - its main function is `get_table_data`
    - for the found communities it constructs the content of the result table (with database queriying) and returns it as a dictionary suitable for Django template language to parse in frontend

- `datasets.py`
    - functions for uploading and deleting user datasets - mainly `add_dataset_record`, `delete_dataset` and `integrate_chants`
    - functions for geography data updates handling


### Communication of main components
The call flow of the functions described in previous section and the subsequent communication between the backend and the frontend is written in the django `views.py` file. In it we find eight important functions, each of which serves one of the seven pages in the application: `index`, `tool`, `datasets`, `geography` and `help`, `register`, `login`, `contact`.

Passing data from backend to frontend templates can be done via two ways - setting `request.session` variable (dictionary) passed in request redirect or render or via `context` dictionary passed in render. Both can be easily parsed in coresponding HTML files thanks to Django template language. Both ways are used in our app.

Functions in `views` take a web request and returns a web response - in this case, the content of the page to display, e.g. `return render(request, "map\_repertoire/tool.html", context)` to display the tool page, where `render` causes the load of a new page from the selected HTML file. The `context` variable in the return function call is a dictionary that is used to pass data between the backend and frontend.


### Frontend
The frontend is the part of the program responsible for the user part of the application - collecting user requests and displaying answer, e. g. the results of the community search. The backend provides the data for display in a suitable form. Communication between these two parts is done through functions in `views.py`.

The flow of a request from a user (submitting a valid form) looks like this: 
- The data from the form (`forms.InputForm`) through which the user specifies his request is collected in `views.tool`

- The backend creates `sig_level`, `map_data` and `tab_data` based on the data and puts them into the `context` dictionary.

- A new load of `tool.html` (`return render(...)`) is triggered.

    - Using the Django template language, iteration through `tab_data` will occur, filling the results table with the appropriate content. 

    - The `map_data` dictionary is passed to the javascript part of the frontend code and is used by function `getMaps` from `static.create_map`.

    - The resulting maps are merged with the corresponding `<div>` elements on the `tool` page.


The forms for uploading and deleting datasets as well as for updating geographic data work equivalently. Almost all of them also have mechanisms in them to check the validity of the input and conveniently provide feedback on it (via `context` or `request.session`).


#### Pages

In addition to the tool page with form and results, the frontend provides a home page with basic information and a map of all known provenance tools (`index`), which is accessed from the backend via `context` and calls `map_data_all` and then, after obtained data dictionary is passed, `getMapOfAllSources` is called - again from `static.create_map.js`. 

The frontend also provides a help page (`help`), a `datasets` page that provides an interface for maintaining user datasets and `geography` that provides form for updating geography data. Beside it there are `register` and `login` pages for user accounts usage.

The basic skeleton of all provided pages resides within `app` in the `templates/Map_repertoire` folder. All of them extend the  `base.html` file from the `templates` folder, which contains common parts of the pages and descriptions of the behavior of CSS elements.

#### Maps
To create maps in the `getMapOfAllSources` and `getMaps` functions, the application uses the   `leaflet` library of the Javascript language (version 1.9.4). This is a basic library for creating interactive maps. The `leaflet` library files are stored locally in the `static/leaflet` folder in the application.

For non-circular map point shapes (triangle and square) we use the `Leaflet.SvgShapeMarkers` extension (https://github.com/rowanwins/Leaflet.SvgShapeMarkers.git). 
However, at a more advanced stage of development, we found that if there are a large number of vertices (and therefore edges) on the map, and there can be up to around two hundred vertices and up to forty thousand edges, the interactivity of the map slows down significantly. (The ability to display all edges, not just those within communities, is important when examining, for example, the uniqueness of communities.) We have therefore decided to move to Canvas technology for display. The `leaflet` library supports this option (edges and circular points worked), but suitable support had to be added to the extension used for other vertex shapes. The extension code is written after the original SVG code in the `static/leaflet-svg-shape-markers.js` file.

#### Design
To elevate the visual appearance of the application above the basic HTML design, we chose the CSS framework `bootstrap` (version 5.3). It is an easy and accessible variant that provides a page design enhancement that should not complicate the work of any future programmer. The code for the framework (CSS and JavaScript files) is again stored locally, in the `static/bootstrap` folder.


### Dependencies
The running of the application and its functionality depends on several other programs. You must have Python installed to run it. Version 3.11.6 was used during development, so the application is not guaranteed to run with other (especially) lower versions. In addition, you need to install `Django` (version 5.0), `pandas` (version 2.1.2), `networkx` (version 3.3), `matplotlib` (version 3.8.2), `scipy` (version 1.12.0), `numpy` (version 1.26.1) and `scikit-learn` (version 1.4.2). For local run follow the instructions in `installation_instructions.md` to install everything you need. We provide standard `app_requirements.txt` file.