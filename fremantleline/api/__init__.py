# -*- coding: utf-8 -*-
#
# Fremantle Line: Transperth trains live departure information
# Copyright (c) 2009-2013 Matt Austin
#
# Fremantle Line is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Fremantle Line is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/

from __future__ import absolute_import, unicode_literals
from datetime import datetime
from fremantleline.api.useragent import URLOpener
from urllib import urlencode
import lxml.html


class Operator(object):
    """Operating company.

    """

    name = 'Transperth Trains'
    uri = 'http://www.transperth.wa.gov.au/TimetablesMaps/LiveTrainTimes.aspx'

    def __repr__(self):
        return '<{class_name}: {name}>'.format(
            class_name=self.__class__.__name__, name=self.name)

    def get_stations(self):
        """Returns list of Station instances for this operator."""
        if not getattr(self, '_stations', False):
            stations = []
            url_opener = URLOpener()
            response = url_opener.open(self.uri)
            html = lxml.html.parse(response).getroot()
            options = html.xpath('.//*[@id="EntryForm"]//select/option')
            for option in options:
                name = unicode(option.attrib['value'])
                stations += [Station(name=name, operator=self)]
            self._stations = stations
        return self._stations


class Station(object):
    """Train station.

    """

    def __init__(self, operator, name):
        self.operator = operator
        self.name = name

    def __repr__(self):
        return '<{class_name}: {name}>'.format(
            class_name=self.__class__.__name__, name=self.name)

    def get_departures(self):
        """Returns Departure instances, using information processed from
        the stations departure board html."""
        departures = []
        html = self._get_html()
        rows = html.xpath(
            '//*[@id="dnn_ctr1608_ModuleContent"]//table//table/tr')[1:-1]
        for row in rows:
            cols = row.xpath('td')
            line = cols[0].xpath('img')[0].attrib['title']
            time = datetime.strptime(cols[1].text_content().strip(),
                                     '%H:%M').time()
            destination = cols[2].text_content().strip()
            description = cols[3].text_content().strip()
            status = cols[5].text_content().strip()
            departure = Departure(station=self,
                                  line=line,
                                  time=time,
                                  destination=destination,
                                  description=description,
                                  status=status)
            departures += [departure]
        return departures

    def _get_html(self):
        """Returns html from the station's departure board web page."""
        url_opener = URLOpener()
        data = urlencode({'stationname': self.name})
        response = url_opener.open('{base_url}?{data}'.format(
            base_url=self.operator.uri, data=data))
        html = lxml.html.parse(response).getroot()
        return html


class Departure(object):
    """Departure information.

    """

    def __init__(self, station, line=None, time=None, destination=None,
                 description=None, status=None):
        self.station = station
        self.line = line
        self.time = time
        self.destination = destination
        self.description = description
        self.status = status

    def __repr__(self):
        return '<{class_name}: {time} {destination} {status}>'.format(
            class_name=self.__class__.__name__, time=self.time,
            destination=self.destination, status=self.status)


transperth = Operator()
