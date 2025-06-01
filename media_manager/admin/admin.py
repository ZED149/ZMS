

# Author: Salman Ahmad a.k.a ZED
# Created at: 4:43pm GMT +5:00, 30 May 2025 Friday


from enum import Enum
from ..message_generator import MessageGenerator
from ..classes import MailHandling
from ..classes import Logging


class E_Channel(Enum):
    email = 1
    whatsapp = 2


class Admin:
    """
    Contains methods that are required for an admin class to perform administrative tasks
    """

    # utility functions

    # perform_assertions
    def __perform_assertions(self, a_name, a_email, a_password):
        # a_name
        assert type(a_name) == str, "a_name needs to be a string."
        assert a_name != '' or None, "Admin name cannot be none."

        # a_email
        assert type(a_email) == str, "a_email needs to be a string."
        assert a_email != '' or None, "Admin email needs to be a valid email."

        # a_password
        assert type(a_password) == str, "a_password needs to be a string."
        assert a_password != '' or None, "Admin password cannot be none."

    # data members
    # private

    __a_name = None         # Name of the Admin
    __a_email = None        # Email of the Admin
    __a_password = None     # Password for the account

    # constructor
    def __init__(self, a_name, a_email, a_password):
        # performing asserts on parameters
        self.__perform_assertions(a_name, a_email, a_password)

        # assigning values
        self.__a_name = a_name
        self.__a_email = a_email
        self.__a_password = a_password

    # notify_admin
    def notify_admin(self, verbose: bool, channel: E_Channel, excep: Exception, logger: Logging) -> None:
        """
        Notifies the admin through the channel provided.

        Args:
            :channel: Channel can either be an Email or Whatsapp.

        Returns:
            None
        """
        if verbose:
            logger.write('-------------------------Notify Admin, notify_admin()-------------------------\n')
        # performing assertions on parameters
        assert type(channel) == E_Channel, "channel must be an E_Channel."
        assert type(verbose) == bool, "verbosity must be a boolean."
        assert type(logger) == Logging, "logger must be a Logging instance."
        
        # checking mode of channel
        if channel == E_Channel.email:
            if verbose:
                logger.write(f"Notifying admin ({self.__a_name}) through email ({self.__a_email}).\n")
                logger.write("Generating message\n")
            message = MessageGenerator.error_in_zms(a_name=self.__a_name, error=excep)
            if verbose:
                logger.write("Message generation successful\n")
                logger.write("Sending email\n")
            se = MailHandling()
            se.send_email(message=message, receiver_email='salmanahmad111499@gmail.com',
                          verbose=True, logger=logger, sender_email=self.__a_email,
                          sender_password=self.__a_password, sender_name=self.__a_name,
                          email_subject='[ZMS] Error During Execution')
            if verbose:
                logger.write('-------------------------notify_admin(), DONE-------------------------\n')
        elif channel == E_Channel.whatsapp:
            print("Notifying through whatsapp.")
            # needs to be implemented.