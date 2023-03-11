# Tank-Datenbank to Drivenote

The `tank_datenbank_to_drivenote.py` script will convert
a [Tank-Datenbank](https://play.google.com/store/apps/details?id=at.harnisch.android.fueldb)
XML export to a CSV file which can be imported
by [Drivenote](https://play.google.com/store/apps/details?id=de.drivenote.android).

Install the required Python packages (preferably in a virtual environment):

```
$ pip install -r requirements.txt
```

Run the script:

```
$ python tank_datenbank_to_drivenote.py -i Tank-Datenbank.xml
```
