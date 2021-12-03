# PRO Class calculator
This project reads AXWare results from an SCCA Solo club, and calculates event results and season standings from the first three runs for every driver (Nationals-style scoring).

## Using this project
Edit `BASE_URL` in `parser.py` to include your club's website, and then run
```
python3 pro.py
```
Make sure you have the required libraries installed first (`pandas` and `lxml`).

## Project structure
- `<year>/` - raw results downloaded from an AXWare class result page
- `pax/` - directory for PAX multipliers downloaded from solotime.info
- `results/` - directory where event and season results are saved
- `parser.py` Python script to download, read and filter event results
- `pax.py` Python script to download/read PAX multipliers and compute fastest times for each driver and event
- `pro.py` Main script that gets event results, writes CSVs, and computes season standings

## Requirements
- An internet connection
- Python 3.7 or newer
- `pandas` and `lxml` python libraries installed

## Acknowledgements
Written by Dan Ebling

This project is not affiliated or associated with SCCA or solotime.info/Solo Performance Specialties/RTP Graphics.
