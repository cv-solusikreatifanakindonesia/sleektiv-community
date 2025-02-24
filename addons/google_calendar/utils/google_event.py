# -*- coding: utf-8 -*-
# Part of Sleektiv. See LICENSE file for full copyright and licensing details.
import json
import logging
import re
from collections import abc
from typing import Iterator, Mapping

from sleektiv.tools import email_normalize
from sleektiv.tools.misc import ReadonlyDict

_logger = logging.getLogger(__name__)


class GoogleEvent(abc.Set):
    """This helper class holds the values of a Google event.
    Inspired by Sleektiv recordset, one instance can be a single Google event or a
    (immutable) set of Google events.
    All usual set operations are supported (union, intersection, etc).

    A list of all attributes can be found in the API documentation.
    https://developers.google.com/calendar/v3/reference/events#resource

    :param iterable: iterable of GoogleCalendar instances or iterable of dictionnaries

    """

    def __init__(self, iterable=()):
        _events = {}
        for item in iterable:
            if isinstance(item, self.__class__):
                _events[item.id] = item._events[item.id]
            elif isinstance(item, Mapping):
                _events[item.get('id')] = item
            else:
                raise ValueError("Only %s or iterable of dict are supported" % self.__class__.__name__)
        self._events = ReadonlyDict(_events)

    def __iter__(self) ->  Iterator['GoogleEvent']:
        return iter(GoogleEvent([vals]) for vals in self._events.values())

    def __contains__(self, google_event):
        return google_event.id in self._events

    def __len__(self):
        return len(self._events)

    def __bool__(self):
        return bool(self._events)

    def __getattr__(self, name):
        # ensure_one
        try:
            event, = self._events.keys()
        except ValueError:
            raise ValueError("Expected singleton: %s" % self)
        event_id = list(self._events.keys())[0]
        value = self._events[event_id].get(name)
        json.dumps(value)
        return value

    def __repr__(self):
        return '%s%s' % (self.__class__.__name__, self.ids)

    @property
    def ids(self):
        return tuple(e.id for e in self)

    @property
    def rrule(self):
        if self.recurrence and any('RRULE' in item for item in self.recurrence):
            return next(item for item in self.recurrence if 'RRULE' in item)

    def sleektiv_id(self, env):
        self.sleektiv_ids(env)  # load ids
        return self._sleektiv_id

    def _meta_sleektiv_id(self, dbname):
        """Returns the Sleektiv id stored in the Google Event metadata.
        This id might not actually exists in the database.
        """
        properties = self.extendedProperties and (self.extendedProperties.get('shared', {}) or self.extendedProperties.get('private', {})) or {}
        o_id = properties.get('%s_sleektiv_id' % dbname)
        if o_id:
            return int(o_id)

    def sleektiv_ids(self, env):
        ids = tuple(e._sleektiv_id for e in self if e._sleektiv_id)
        if len(ids) == len(self):
            return ids
        model = self._get_model(env)
        found = self._load_sleektiv_ids_from_db(env, model)
        unsure = self - found
        if unsure:
            unsure._load_sleektiv_ids_from_metadata(env, model)

        return tuple(e._sleektiv_id for e in self)

    def _load_sleektiv_ids_from_metadata(self, env, model):
        unsure_sleektiv_ids = tuple(e._meta_sleektiv_id(env.cr.dbname) for e in self)
        sleektiv_events = model.browse(_id for _id in unsure_sleektiv_ids if _id)

        # Extended properties are copied when splitting a recurrence Google side.
        # Hence, we may have two Google recurrences linked to the same Sleektiv id.
        # Therefore, we only consider Sleektiv records without google id when trying
        # to match events.
        o_ids = sleektiv_events.exists().filtered(lambda e: not e.google_id).ids
        for e in self:
            sleektiv_id = e._meta_sleektiv_id(env.cr.dbname)
            if sleektiv_id in o_ids:
                e._events[e.id]['_sleektiv_id'] = sleektiv_id

    def _load_sleektiv_ids_from_db(self, env, model):
        sleektiv_events = model.with_context(active_test=False)._from_google_ids(self.ids)
        mapping = {e.google_id: e.id for e in sleektiv_events}  # {google_id: sleektiv_id}
        existing_google_ids = sleektiv_events.mapped('google_id')
        for e in self:
            sleektiv_id = mapping.get(e.id)
            if sleektiv_id:
                e._events[e.id]['_sleektiv_id'] = sleektiv_id
        return self.filter(lambda e: e.id in existing_google_ids)


    def owner(self, env):
        # Owner/organizer could be desynchronised between Google and Sleektiv.
        # Let userA, userB be two new users (never synced to Google before).
        # UserA creates an event in Sleektiv (they are the owner) but userB syncs first.
        # There is no way to insert the event into userA's calendar since we don't have
        # any authentication access. The event is therefore inserted into userB's calendar
        # (they are the organizer in Google). The "real" owner (in Sleektiv) is stored as an
        # extended property. There is currently no support to "transfert" ownership when
        # userA syncs their calendar the first time.
        real_owner_id = self.extendedProperties and self.extendedProperties.get('shared', {}).get('%s_owner_id' % env.cr.dbname)
        try:
            # If we create an event without user_id, the event properties will be 'false'
            # and python will interpret this a a NoneType, that's why we have the 'except TypeError'
            real_owner_id = int(real_owner_id)
        except (ValueError, TypeError):
            real_owner_id = False
        real_owner = real_owner_id and env['res.users'].browse(real_owner_id) or env['res.users']
        if real_owner_id and real_owner.exists():
            return real_owner
        elif self.organizer and self.organizer.get('self'):
            return env.user
        elif self.organizer and self.organizer.get('email'):
            # In Google: 1 email = 1 user; but in Sleektiv several users might have the same email :/
            org_email = email_normalize(self.organizer.get('email'))
            return env['res.users'].search([('email_normalized', '=', org_email)], limit=1)
        else:
            return env['res.users']

    def filter(self, func) -> 'GoogleEvent':
        return GoogleEvent(e for e in self if func(e))

    def clear_type_ambiguity(self, env):
        ambiguous_events = self.filter(GoogleEvent._is_type_ambiguous)
        recurrences = ambiguous_events._load_sleektiv_ids_from_db(env, env['calendar.recurrence'])
        for recurrence in recurrences:
            self._events[recurrence.id]['recurrence'] = True
        for event in ambiguous_events - recurrences:
            self._events[event.id]['recurrence'] = False

    def is_recurrence(self):
        if self._is_type_ambiguous():
            _logger.warning("Ambiguous event type: cannot accurately tell whether a cancelled event is a recurrence or not")
        return bool(self.recurrence)

    def is_recurrent(self):
        return bool(self.recurringEventId or self.is_recurrence())

    def is_cancelled(self):
        return self.status == 'cancelled'

    def is_recurrence_follower(self):
        return bool(not self.originalStartTime or self.originalStartTime == self.start)

    def full_recurring_event_id(self):
        """
            Give the complete identifier with elements
            in `id` and `recurringEventId`.
            :return: concatenation of the id created by the recurrence
                    and the id created by the modification of a specific event
            :rtype: string if recurrent event and correct ids, `None` otherwise
        """
        # Regex expressions to match elements (according to the google support [not documented]):
        # - ID: [a-zA-Z0-9]+
        # - RANGE: R[0-9]+T[0-9]+
        # - TIMESTAMP: [0-9]+T[0-9]+Z
        # With:
        # - id: 'ID_TIMESTAMP'
        # - recurringEventID: 'ID_RANGE'
        # Find: 'ID_RANGE_TIMESTAMP'
        if not self.is_recurrent():
            return None
        # Check if ids are the same
        id_value = re.match(r'(\w+_)', self.id)
        recurringEventId_value = re.match(r'(\w+_)', self.recurringEventId)
        if not id_value or not recurringEventId_value or id_value.group(1) != recurringEventId_value.group(1):
            return None
        rec_pattern = re.search(r'(\w+_R\d+(?:T\d+)?(?:Z)?)', self.recurringEventId)
        if not rec_pattern:
            return None
        id_range = rec_pattern.group()

        ts_pattern = re.search(r'(\d{8}(?:T\d+Z?)?)$', self.id)
        if not ts_pattern:
            return None
        timestamp = ts_pattern.group()

        return f"{id_range}_{timestamp}"

    def cancelled(self):
        return self.filter(lambda e: e.status == 'cancelled')

    def exists(self, env) -> 'GoogleEvent':
        recurrences = self.filter(GoogleEvent.is_recurrence)
        events = self - recurrences
        recurrences.sleektiv_ids(env)
        events.sleektiv_ids(env)

        return self.filter(lambda e: e._sleektiv_id)

    def _is_type_ambiguous(self):
        """For cancelled events/recurrences, Google only send the id and
        the cancelled status. There is no way to know if it was a recurrence
        or simple event."""
        return self.is_cancelled() and 'recurrence' not in self._events[self.id]

    def _get_model(self, env):
        if all(e.is_recurrence() for e in self):
            return env['calendar.recurrence']
        if all(not e.is_recurrence() for e in self):
            return env['calendar.event']
        raise TypeError("Mixing Google events and Google recurrences")

    def get_meeting_url(self):
        if not self.conferenceData:
            return False
        video_meeting = list(filter(lambda entryPoints: entryPoints.get('entryPointType') == 'video', self.conferenceData.get('entryPoints', [])))
        return video_meeting[0].get('uri') if video_meeting else False

    def is_available(self):
        return self.transparency == 'transparent'

    def get_sleektiv_event(self, env):
        if self._get_model(env)._name == 'calendar.event':
            return env['calendar.event'].browse(self.sleektiv_id(self.env))
        else:
            return env['calendar.recurrence'].browse(self.sleektiv_id(self.env)).base_event_id
