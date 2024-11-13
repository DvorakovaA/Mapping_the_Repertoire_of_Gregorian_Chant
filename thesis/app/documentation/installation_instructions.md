### Installation instructions for local run of ChantMapper app

To prepare the application for the local run, you need the following:
- Have the files downloaded to run the application.
- Make sure Python (ideally version 3.11.6) is installed. If not, then follow the instructions on the official language page to install it.
- Install its libraries according to the file app_requirements.txt, which available in the app folder. (At the command line, run `pip install -r path/to/app_requirements.txt`.)

Once all the dependencies have been successfully installed, all you need to do in the command line in the
`app/Gregorian_chant_repertoire` folder is to run the `python manage.py runserver` command.
The tool can then be found via a web browser at `http://127.0.0.1:8000/`.
