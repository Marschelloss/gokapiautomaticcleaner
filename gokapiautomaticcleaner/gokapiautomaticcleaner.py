import sys, argparse, logging
import requests
from datetime import datetime

log = logging.getLogger(__name__)

def main():
  # set up argument parser
  parser = argparse.ArgumentParser(description='Gokapi Cleaner Tool')
  parser.add_argument('apikey', help='Required API Key')
  parser.add_argument("-u", "--url", default="http://localhost/api", help="Optional: URL to be used for api calls - Default: http://localhost/api")
  parser.add_argument("-t", "--testrun", action="store_true", default=False, help='Optional: Don\' delete file, just do a test run.')
  parser.add_argument("-v", "--verbose", action="store_true", help="Increases output verbosity")
  args = parser.parse_args()

  # set up logger
  log.setLevel(logging.INFO if not args.verbose else logging.DEBUG)
  log_screen_handler = logging.StreamHandler(stream=sys.stdout)
  log.addHandler(log_screen_handler)
  log.propagate = False
  
  # add colored logs if colorama is availabe
  try:
    import colorama, copy

    LOG_COLORS = {
      logging.DEBUG: colorama.Fore.GREEN,
      logging.INFO: colorama.Fore.BLUE,
      logging.WARNING: colorama.Fore.YELLOW,
      logging.ERROR: colorama.Fore.RED,
      logging.CRITICAL: colorama.Back.RED
    }

    class ColorFormatter(logging.Formatter):
      def format(self, record, *args, **kwargs):
        # if the corresponding logger has children, they may receive modified
        # record, so we want to keep it intact
        new_record = copy.copy(record)
        if new_record.levelno in LOG_COLORS:
          new_record.levelname = "{color_begin}{level}{color_end}".format(
              level=new_record.levelname,
              color_begin=LOG_COLORS[new_record.levelno],
              color_end=colorama.Style.RESET_ALL,
          )
        return super(ColorFormatter, self).format(new_record, *args, **kwargs)

    log_screen_handler.setFormatter(ColorFormatter(fmt='%(asctime)s %(levelname)-8s %(message)s', 
      datefmt="{color_begin}[%H:%M:%S]{color_end}".format(
        color_begin=colorama.Style.DIM,
        color_end=colorama.Style.RESET_ALL
      )))
  except ModuleNotFoundError as identifier:
    pass
  
  log.debug(f"Script called with the following arguments: {vars(args)}")

  # --- Main Work
  log.info("-- Start searching for files ...")
  head = {'accept': 'application/json', 'apikey': args.apikey}
  log.debug("Used headers: %s" % head)
  url = args.url + "/files/list"
  log.debug("Used url: %s" % url)

  resp = requests.get(args.url + "/files/list", headers=head)
  if resp.status_code != 200:
      log.error("Response not 200! Exit...")
      sys.exit(0)
  files = resp.json()

  # Empty list of file ids to be deleted
  trash = []
  # Current timestamp to compare files to
  timestamp = int(datetime.now().timestamp())
  log.debug("Using current timestamp: %s" % timestamp)

  for file in files:
      # -- File Structure
      # {'Id': 'XtMMqOuRbLGaPCA', 'Name': '2024-10-28 Fa.Köstler+Klier 4.AR gepr.pdf', 'Size': '7.7 MB', 'HotlinkId': '', 'ContentType': 'application/pdf', 'ExpireAt': 1746874563, 'SizeBytes': 8040329, 'ExpireAtString': '2025-05-10 12:56', 'DownloadsRemaining': -2, 'DownloadCount': 3, 'UnlimitedDownloads': True, 'UnlimitedTime': False, 'RequiresClientSideDecryption': False, 'IsEncrypted': False, 'IsPasswordProtected': False, 'IsSavedOnLocalStorage': True}
      if file['ExpireAt'] < timestamp:
          log.debug("Found file '%s' which expires at %s // %s" % (file['Name'], file['ExpireAtString'], file['ExpireAt']))
          trash.append(file)
  log.info("-- Searched through all files.")
  log.info("-- Found %s files to be removed." % len(trash))

  # --- Delete files
  if len(trash) != 0:
      log.info("-- Starting removal of files ...")
      for t in trash:
          log.debug("Removing file '%s' with id %s" % (t['Name'], t['Id']))
          if not args.testrun:
              head = {'accept': 'application/json', 'apikey': args.apikey, 'id': t['Id']}
              url = args.url + "/files/delete"
              resp = requests.delete(url, headers=head)
              if resp.status_code != 200:
                  log.error("Removal of file '' did not work! Abort ...")
                  sys.exit(0)
          else:
              log.info("No command executed.")
      log.info("-- All files cleared. Exiting ...")
  else:
      log.info("-- No files to remove found. Exiting ...")


# ---
if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    log.critical('Interrupted by user')
    try:
      sys.exit(0)
    except SystemExit:
      os._exit(0)
