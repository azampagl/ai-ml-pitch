"""
Scrapes brooksbaseball and stores the raw html files to disk.

The style guide follows the strict python PEP 8 guidelines.
@see http://www.python.org/dev/peps/pep-0008/

@author Aaron Zampaglione <azampaglione@g.harvard.edu>
@author Fil Piasevoli <fpiasevoli@g.harvard.edu>
@author Lyla Fadden <lylafadden@g.harvard.edu>

@requires Python >=2.7
@copyright 2014
"""
import os

from datetime import date, timedelta
from dateutil.rrule import rrule, DAILY
from urllib import urlencode
from urlparse import parse_qs, urlparse

from scrapy import Request, Spider

from brooksbaseball.items import GameItem

class RootSpider(Spider):
    # Name of the scraper.
    name = "brooksbaseball"

    # The allowed domains to crawl.
    allowed_domains = ["brooksbaseball.net"]

    # The timeout between requests.
    download_delay = 0.5

    # The base url.
    base_url = "http://www.brooksbaseball.net/pfxVB/"

    # The location to save the scraped html files.
    store_path = "data/"

    # Define a start and end date for crawling.
    #  Baseball seasons starts in March!
    start_date = date(2008, 3, 1)
    end_date = date(2014, 12, 01)

    def __init__(self, *args, **kwargs):
        """
        Initialize the scraper.
        """

        super(RootSpider, self).__init__(*args, **kwargs)

        self.start_urls = []

        # The start urls are every single date from the start to the end dates
        #  defined above.
        for dt in rrule(DAILY, dtstart=self.start_date, until=self.end_date):
            url = self.base_url + "pfx.php/?league=mlb&"
            # The site does not like 0 padded dates.
            url += "&year=" + str(int(dt.year))
            url += "&month=" + str(int(dt.month))
            url += "&day=" + str(int(dt.day))
            self.start_urls.append(url)

    def parse(self, response):
        """
        Parses the first level, which is a drop down box
        of all the games for that day.
        """

        # Find the games selection drop down box.
        xpath = '//select[@name="game"]/option'

        # For each option (game), generate a
        #  new request with game details.
        for sel in response.xpath(xpath):
            url = response.url

            params = parse_qs(
                urlparse(url).query,
                keep_blank_values=True)

            game = sel.xpath('@value').extract()[0]

            url = response.url
            url += "&prevDate=" + \
                str(int(params['month'][0])) + \
                str(int(params['day'][0]))
            url += "&prevGame=" + game
            url += "&game=" + game

            # Generate a new request which is specific to a game
            #  on a particular day.
            req = Request(url, callback=self.parse_game)

            yield req

    def parse_game(self, response):
        """
        Parses the second level, which has a dropdown box of all
        the pitchers for that game.
        """

        # Find the pitcher selection drop down box.
        xpath = '//select[@name="pitchSel"]/option'

        # For each option, generate a new request
        #  which will give the details for a particular
        #  pitcher is a particular game.
        for sel in response.xpath(xpath):
            url = response.url

            url += "&pitchSel=" + sel.xpath('@value').extract()[0]

            req = Request(url, callback=self.parse_pitcher)

            yield req

    def parse_pitcher(self, response):
        """
        Parses the third level, which is the pitcher details page
        for a particular game. It contains a link to a raw
        HTML page that contains all the stats.
        """

        params = parse_qs(
            urlparse(response.url).query,
                keep_blank_values=True)

        data = {}
        data['year'] = params['year'][0]
        data['month'] = params['month'][0]
        data['day'] = params['day'][0]
        data['pitcher_id'] = params['pitchSel'][0]
        data['game_id'] = params['game'][0]

        # Find the raw html table link.
        xpath = '//a[text()="Get Expanded Tabled Data"]'

        # Generate the url to open the raw html table page.
        sel = response.xpath(xpath)[0]

        link = urlparse(sel.xpath('@href').extract()[0])
        params = parse_qs(link.query, keep_blank_values=True)

        for key, value in params.items():
            params[key] = value[0]
        # Override the rows/column size just in case.
        params['h_size'] = 3000
        params['v_size'] = 3000

        url = self.base_url + link.path + "?" + urlencode(params)

        req = Request(url, callback=self.parse_pitcher_stats, meta={'data': data})

        yield req

    def parse_pitcher_stats(self, response):
        """
        Parses the final page of the operation - a raw html page
        with one table containing all the stats for one pitcher during
        a particular game. This html page will be directly downloaded to disk
        for post processing.

        The files will be structured as follows:

        root/
          2008/
            03-01/
              game01.html
              game02.html
              ...
            ...
          ...
        """

        data = response.meta['data']

        # Create a top level year directory that will contain
        #  sub-directories for every day containing at least
        #  one game during the year.
        path = self.store_path
        path += "/" + data['year']

        if not os.path.exists(path):
            os.makedirs(path)

        path += "/" + data['month'].zfill(2) + "-" + data['day'].zfill(2)

        if not os.path.exists(path):
            os.makedirs(path)

        # Make sure the game id and the pitcher id are in the file name.
        filename = path + "/" + \
            data['game_id'][:-1] + \
            "-pid_" + data['pitcher_id'] + ".html"

        with open(filename, 'wb') as f:
            f.write(response.body)
