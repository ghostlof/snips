#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions
from hermes_python.ontology import *
import io
import serial

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

class SnipsConfigParser(ConfigParser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, ConfigParser.Error) as e:
        return dict()

def subscribe_intent_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper(hermes, intentMessage, conf)


def action_wrapper(hermes, intentMessage, conf):
    import serial
    from serial import Serial
    import time
    from time import sleep

    # serial init.
    self = serial.Serial()
    self.baudrate = 9600
    self.port = '/dev/ttyUSB0'
    self.bytesize = 8
    self.parity = 'N' 
    self.stopbits = 1
    self.xonxoff = True
    self.timeout = 1
    self.open()


    command = 'TI\r\n'
    self.write(bytes(command, 'utf8'))
    time.sleep(0.2)
    repbytes = self.readline().decode('utf-8')
    if repbytes[0:4] == 'TI S' or repbytes[0:4] == 'TI D': 
        pass # it break just if you are in this break
    else : # if the conditions are false : send the command again
        command = 'ZI\r\n'
        self.write(bytes(command, 'utf8'))
        time.sleep(0.2)
        repbytes = self.readline().decode('utf-8')
        # waiting valueIme before write it
        while repbytes[0:3] =='':
            time.sleep(0.2) 
            repbytes = self.readline().decode('utf-8')


    # Entrez la phrase à prononcer pour valider l'action
    result_sentence = 'La balance a bien été tarée'
    current_session_id = intentMessage.session_id
    hermes.publish_end_session(current_session_id, result_sentence)

if __name__ == "__main__":
    mqtt_opts = MqttOptions()
    with Hermes(mqtt_options=mqtt_opts) as h:
        h.subscribe_intent("ghostlof:Tare", subscribe_intent_callback) \
         .start()
