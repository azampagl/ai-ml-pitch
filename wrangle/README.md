# Wrangle #

The source code used to gather, clean, and organize the raw pitching data from brooksbaseball.net

## File Structure ##

Each foler will contain a README with details about the folder contents.

* **scrape/**

  The source code used to scrape brooksbaseball.net.

* **filter.py**

  Converts the file structure after downloading from brooksbaseball.net from a date-based structure to a pitcher-based structure.

  e.g.

  From:

      in-directory/
        2008/
          03-01/
            game01.html
            game02.html
            ...
          03-02/
            game01.html
            game02.html
            ...
        2009/
          ...
        ...

  To: (folder names are pitcher IDs)

      out-directory/
        0239482/
          game01.html
          game02.html
          ...
        0239482/
          game01.html
          game02.html
          ...
        ...

* **compress.py**

  Converts the file structure after filtering from a pitcher-based structure to individual csv files for each pitcher. This final form can be easily read into a panda's DataFrame.

  e.g.

  From: (folder names are pitcher IDs)

      in-directory/
        0239482/
          game01.html
          game02.html
          ...
        0239482/
          game01.html
          game02.html
          ...
        ...

  To:

      out-directory/
        0239482.csv
        0239482.csv
        ...
