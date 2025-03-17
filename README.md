# Gokapi Automatic Cleaner

Simple script to retrieve all files from Gokapi via API, filter files with older than todays "EpixreAt" Meta Fields and removes them.

Files stay in the database even tho they already "expired", if the user didn't select the "Expire" checkbox on the interface.

## Usage

Simply provide API-Key (with privileges to read and delete) and url:

```bash
python gokapiautomaticcleaner/gokapiautomaticcleaner.py 123abc -u "https://share.example.de/api"
```
