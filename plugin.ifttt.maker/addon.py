# -*- coding: utf-8 -*-

import sys
from urllib import urlencode
from urlparse import parse_qsl
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import json
import requests

addon = xbmcaddon.Addon()
icon = addon.getAddonInfo('icon')

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

triggers = [{'name': addon.getSetting('trigger1_name'),
             'event':  addon.getSetting('trigger1_event'),
             'value1': addon.getSetting('trigger1_value_1'),
             'value2': addon.getSetting('trigger1_value_2'),
             'value3': addon.getSetting('trigger1_value_3,'),
             'thumb': icon},
            {'name': addon.getSetting('trigger2_name'),
             'event': addon.getSetting('trigger2_event'),
             'value1': addon.getSetting('trigger2_value_1'),
             'value2': addon.getSetting('trigger2_value_2'),
             'value3': addon.getSetting('trigger2_value_3,'),
             'thumb': icon},
            {'name': addon.getSetting('trigger3_name'),
             'event': addon.getSetting('trigger3_event'),
             'value1': addon.getSetting('trigger3_value_1'),
             'value2': addon.getSetting('trigger3_value_2'),
             'value3': addon.getSetting('trigger3_value_3,'),
             'thumb': icon}
            ]


def trigger_event(event, value1, value2, value3):
    """Make a POST web request to IFTTT"""

    # Get key set in settings to acces IFTTT
    key = addon.getSetting('key')

    url = 'https://maker.ifttt.com/trigger/' + \
        str(event) + '/with/key/' + str(key)

    # Put optional values in JSON format
    payload = {'value1': value1, 'value2': value2, 'value3': value3}

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

    # Build notification variables
    heading = addon.getAddonInfo('name')
    icon = addon.getAddonInfo('icon')
    dialog = xbmcgui.Dialog()

    # Return notification
    return xbmcgui.Dialog().notification(heading, message, icon)


def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively
    from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: str
    """
    return '{0}?{1}'.format(_url, urlencode(kwargs))


def get_triggers():
    """
    Retrieve the list of triggers and do some parsing if needed
    TODO: consider using generators functions instead of returning lists.
    https://wiki.python.org/moin/Generators
    """
    # TODO: filter out nonetypes?
    for trigger in triggers:
        for i in trigger:
            xbmc.log(msg='The value of %s is %s and a %s' % (i, trigger[i], type(trigger[i])),
                         level=xbmc.LOGNOTICE)
    return triggers


def list_triggers():
    """
    Create the list of triggerable triggers in the Kodi interface.
    """
    # Get the list of triggers.
    triggers = get_triggers()
    # Iterate through triggers.
    for trigger in triggers:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=trigger['name'])
        # Set graphics for the list item.
        list_item.setArt({'thumb': trigger['thumb'], 'icon': trigger[
                         'thumb']})
        # Create an URL for a plugin recursive call.
        # Example: plugin://plugin.ifttt.maker/?action=trigger&id=event1
        url = get_url(action='trigger',
                      event=trigger['event'],
                      value1=trigger['value1'],
                      value2=trigger['value2'],
                      value3=trigger['value3']
                      )
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

    # Add a link to the settings
    list_item = xbmcgui.ListItem(label='Settings')
    # Set additional info for the list item.
    list_item.setArt({'thumb': trigger['thumb'], 'icon': trigger[
                     'thumb']})
    # Create a URL for a plugin recursive call.
    # Example: plugin://plugin.ifttt.maker/?action=trigger&id=event1
    url = 'self.Addon.openSettings()'
    # Add the list item to a virtual Kodi folder.
    # is_folder = False means that this item won't open any sub-list.
    is_folder = False
    # Add our item to the Kodi virtual folder listing.
    xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

    # Add a sort method for the virtual folder items (alphabetically, ignore
    # articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def play_video(path):
    """
    Play a video by the provided path.
    :param path: Fully-qualified video URL
    :type path: str
    """
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=path)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def router(paramstring):
    xbmc.log(msg='Starting Plug-in, Python version is: %s' % (sys.version),
             level=xbmc.LOGNOTICE)
    """
    Router function that calls other functions
    depending on the provided paramstring
    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'trigger':
            # Write to the log what variables are passed on
            xbmc.log(msg='Triggering Event: %s with value1 %s, value2 %s and value3 %s' % (params['event'], params['value1'], params['value2'], params['value3']), level=xbmc.LOGNOTICE)
            # Call the trigger event
            trigger_event(params['event'], params['value1'],
                          params['value2'], params['value3'])
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_triggers()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call
    # paramstring
    router(sys.argv[2][1:])
