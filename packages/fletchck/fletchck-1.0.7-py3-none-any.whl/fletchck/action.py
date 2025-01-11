# SPDX-License-Identifier: MIT
"""Action base and specific classes"""

from . import defaults
from logging import getLogger, DEBUG, INFO, WARNING, ERROR
from tornado.httpclient import HTTPClient
from urllib.parse import urlencode
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.utils import make_msgid, formatdate
from subprocess import run
from paho.mqtt.client import MQTTv5
from paho.mqtt.publish import single as publish
import json

import ssl

_log = getLogger('fletchck.action')
_log.setLevel(INFO)

ACTION_TYPES = {}


def loadAction(name, config):
    """Return an action object for the provided config dict"""
    ret = None
    if config['type'] in ACTION_TYPES:
        options = defaults.getOpt('options', config, dict, {})
        ret = ACTION_TYPES[config['type']](name, options)
        ret.actionType = config['type']
    else:
        _log.warning('%s: Invalid action type ignored', name)
    return ret


class BaseAction():
    """Action base class, implements the log type and interface"""

    def __init__(self, name=None, options={}):
        self.name = name
        self.options = options
        self.actionType = 'log'

    def getStrOpt(self, key, default=None):
        return defaults.getOpt(key, self.options, str, default)

    def getIntOpt(self, key, default=None):
        return defaults.getOpt(key, self.options, int, default)

    def getListOpt(self, key, default=None):
        return defaults.getOpt(key, self.options, list, default)

    def getBoolOpt(self, key, default=None):
        return defaults.getOpt(key, self.options, bool, default)

    def _notify(self, source):
        return True

    def trigger(self, source):
        count = 0
        while True:
            if self._notify(source):
                break
            count += 1
            if count >= defaults.ACTIONTRIES:
                _log.error('%s (%s): Fail after %r tries', self.name,
                           self.actionType, count)
                return False
        return True

    def flatten(self):
        """Return the action detail as a flattened dictionary"""
        return {'type': self.actionType, 'options': self.options}


class publishMsg(BaseAction):
    """Publish single message to MQTT broker"""

    def _notify(self, source):
        ret = True
        basetopic = self.getStrOpt('topic')
        if basetopic is not None:
            # todo: sanitise source name?
            topic = basetopic + '/' + source.name.replace('/', '')
            hostname = self.getStrOpt('hostname')
            port = self.getIntOpt('port', 8883)
            username = self.getStrOpt('username')
            password = self.getStrOpt('password')
            auth = None
            if username or password:
                auth = {'username': username, 'password': password}
            usetls = self.getBoolOpt('usetls', True)
            msg = json.dumps(source.msgObj())
            _log.debug('Publish msg to %r via %r : %r', topic, hostname, msg)

            ret = False
            try:
                ctx = None
                if usetls:
                    ctx = ssl.create_default_context()
                publish(topic=topic,
                        payload=msg,
                        qos=1,
                        retain=True,
                        hostname=hostname,
                        port=port,
                        auth=auth,
                        tls=ctx,
                        protocol=MQTTv5)
                ret = True
            except Exception as e:
                _log.warning('MQTT publish notify failed: %s', e)

        else:
            _log.warning('MQTT publish notify not configured')
        return ret


class sendEmail(BaseAction):
    """Send email by configured submit"""

    def _notify(self, source):
        site = self.getStrOpt('site', defaults.APPNAME)

        subject = "[%s] %s (%s) in %s state" % (
            site, source.name, source.checkType, source.getState())
        ml = []
        ml.append('%s (%s) in %s state at %s%s' %
                  (source.name, source.checkType, source.getState(),
                   source.lastFail if source.failState else source.lastPass,
                   '' if source.failState else '\n\U0001f436\U0001F44D'))
        if source.log:
            ml.append('')
            ml.append('Log:')
            ml.append('')
            for l in source.log:
                ml.append(l)
        message = '\n'.join(ml)
        username = self.getStrOpt('username')
        password = self.getStrOpt('password')
        sender = self.getStrOpt('sender')
        recipients = self.getListOpt('recipients', [])
        hostname = self.getStrOpt('hostname')
        fallback = self.getStrOpt('fallback')
        port = self.getIntOpt('port', 0)
        timeout = self.getIntOpt('timeout', defaults.SUBMITTIMEOUT)

        _log.debug('Send email to %r via %r : %r', recipients, hostname,
                   subject)

        ret = True
        if not recipients:
            _log.info('No email recipients specified - notify ignored')
            return ret

        msgid = make_msgid()
        m = MIMEText(message)
        if sender:
            m['From'] = sender
        m['Subject'] = subject
        m['Message-ID'] = msgid
        m['Date'] = formatdate(localtime=True)

        if hostname:
            ret = False
            try:
                ctx = ssl.create_default_context()
                with SMTP_SSL(host=hostname,
                              port=port,
                              timeout=timeout,
                              context=ctx) as s:
                    if username and password:
                        s.login(username, password)
                    s.send_message(m, from_addr=sender, to_addrs=recipients)
                ret = True
            except Exception as e:
                _log.warning('SMTP Email Notify failed: %s', e)
        elif fallback:
            ret = False
            try:
                cmd = [fallback, '-oi']
                if sender:
                    cmd.extend(['-r', sender])
                cmd.append('--')
                cmd.extend(recipients)
                run(cmd,
                    capture_output=True,
                    input=m.as_bytes(),
                    timeout=timeout,
                    check=True)
                _log.debug('Fallback email sent ok to: %r', recipients)
                ret = True
            except Exception as e:
                _log.warning('Fallback Email Notify failed: %s', e)
        else:
            _log.warning('Email notify not configured')
        return ret


class ckSms(BaseAction):
    """Post SMS via cloudkinnect api"""

    def trigger(self, source):
        message = '%s: %s\n%s\n%s'
        if source.failState:
            message = '\U0001f436\U0001f4ac\n%s: %s\n%s\n%s' % (
                source.name,
                source.getState(),
                source.getSummary(),
                source.lastFail,
            )
        else:
            message = '\U0001f436\U0001F44D\n%s: %s\n%s' % (
                source.name,
                source.getState(),
                source.lastPass,
            )
        sender = self.getStrOpt('sender', 'dedicated')
        recipients = [i for i in self.getListOpt('recipients', [])]
        url = self.getStrOpt('url', defaults.CKURL)
        apikey = self.getStrOpt('apikey')

        httpClient = HTTPClient()
        failCount = 0
        while recipients and failCount < defaults.ACTIONTRIES:
            recipient = ','.join(recipients).replace('+', '')
            _log.debug('Send sms to %r via %r : %r', recipient, url, message)
            postBody = urlencode({
                'originator': sender,
                'mobile_number': recipient,
                'concatenated': 'true',
                'utf': 'true',
                'text': message
            })
            try:
                response = httpClient.fetch(
                    url,
                    method='POST',
                    headers={
                        'Authorization': 'Bearer ' + apikey,
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body=postBody)
                if response.code == 200:
                    recipients = None
                else:
                    failCount += 1
                    _log.warning('SMS Notify failed: %r:%r', response.code,
                                 response.body)
            except Exception as e:
                failCount += 1
                _log.warning('SMS Notify failed: %s', e)
        return not recipients


class apiSms(BaseAction):
    """Post SMS via smscentral api"""

    def trigger(self, source):
        message = '%s: %s\n%s\n%s'
        if source.failState:
            message = message % (
                source.name,
                source.getState(),
                source.getSummary(),
                source.lastFail,
            )
        else:
            message = message % (
                source.name,
                source.getState(),
                '\U0001f436\U0001F44D',
                source.lastPass,
            )
        sender = self.getStrOpt('sender', 'dedicated')
        recipients = [i for i in self.getListOpt('recipients', [])]
        username = self.getStrOpt('username')
        password = self.getStrOpt('password')
        url = self.getStrOpt('url', defaults.SMSCENTRALURL)

        httpClient = HTTPClient()
        failCount = 0
        while recipients and failCount < defaults.ACTIONTRIES:
            recipient = recipients[0]
            _log.debug('Send sms to %r via %r : %r', recipient, url, message)
            postBody = urlencode({
                'ACTION': 'send',
                'USERNAME': username,
                'PASSWORD': password,
                'ORIGINATOR': sender,
                'RECIPIENT': recipient,
                'MESSAGE_TEXT': message
            })
            try:
                response = httpClient.fetch(
                    url,
                    method='POST',
                    headers={
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body=postBody)
                if response.body == b'0':
                    recipients.pop(0)
                else:
                    failCount += 1
                    _log.warning('SMS Notify failed: %r:%r', response.code,
                                 response.body)
            except Exception as e:
                failCount += 1
                _log.warning('SMS Notify failed: %s', e)
        return not recipients


ACTION_TYPES['email'] = sendEmail
ACTION_TYPES['sms'] = apiSms
ACTION_TYPES['cksms'] = ckSms
ACTION_TYPES['mqtt'] = publishMsg
