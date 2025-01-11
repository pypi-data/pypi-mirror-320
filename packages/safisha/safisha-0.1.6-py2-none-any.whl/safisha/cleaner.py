# safisha/cleaner.py
from __future__ import print_function  # Ensure Python 3-style print in Python 2.7
import os
import shutil

class Safisha:
    def __init__(self):
        self.home_dir = os.path.expanduser("~")  # Pata folda ya nyumbani

    def safisha_downloads(self):
        """Safisha folda ya Downloads."""
        downloads_path = os.path.join(self.home_dir, "Downloads")
        self._safisha_directory(downloads_path)

    def safisha_desktop(self):
        """Safisha folda ya Desktop."""
        desktop_path = os.path.join(self.home_dir, "Desktop")
        self._safisha_directory(desktop_path)

    def safisha_cache(self):
        """Safisha folda ya Cache."""
        cache_path = os.path.join(self.home_dir, "Library", "Caches")
        self._safisha_directory(cache_path)

    def safisha_zote(self):
        """Safisha folda zote zinazotumika."""
        self.safisha_downloads()
        self.safisha_desktop()
        self.safisha_cache()

    def _safisha_directory(self, directory):
        """Msaada wa kusafisha folda."""
        if not os.path.exists(directory):
            print("Folda {} haipo.".format(directory))
            return

        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
                    print("Imeondolewa faili: {}".format(item_path))
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    print("Imeondolewa folda: {}".format(item_path))
            except Exception as e:
                print("Imeshindwa kuondoa {}. Sababu: {}".format(item_path, str(e)))