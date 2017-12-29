# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon
import xbmcgui
import json
import requests

addon = xbmcaddon.Addon()


def trigger_event():
    """Make a POST web request to IFTTT"""

    # Set access variables
    key = addon.getSetting('key')
    event = addon.getSetting('event')
    value_1 = addon.getSetting('value_1')
    value_2 = addon.getSetting('value_2')
    value_3 = addon.getSetting('value_3')

    url = 'https://maker.ifttt.com/trigger/' + \
        str(event) + '/with/key/' + str(key)

    # Put optional values in JSON format
    payload = json.dumps(
        {"value1": str(value_1), "value2": str(value_2), "value3": str(value_3)})

    # Do the request
    r = requests.post(url, data=payload)

    # Capture the response and store the json in a dictionary
    result = r.text

    try:
        # Test if result is valid JSON
        result = json.loads(result)
        message = str(result['errors'][0]['message'])
    except ValueError, e:
        # If the result is not JSON we expect a string
        message = result

    heading = addon.getAddonInfo('name')
    icon = addon.getAddonInfo('icon')
    dialog = xbmcgui.Dialog()

    return xbmcgui.Dialog().notification(heading, message, icon)

trigger_event()
