import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from app.db import Database
from app.poller import poll_once

class MailboxBaselineTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.db=Database('sqlite:///'+self.tmp.name+'/db.sqlite')
        self.db.init()
    def tearDown(self):self.tmp.cleanup()
    def test_baseline_is_fixed_across_restarts(self):
        self.assertEqual(self.db.mailbox_baseline('box:1:',[b'2',b'9']),(9,True))
        self.assertEqual(self.db.mailbox_baseline('box:1:',[b'2',b'9',b'10']),(9,False))
    def test_empty_mailbox_accepts_first_new_uid(self):
        self.assertEqual(self.db.mailbox_baseline('box:1:',[]),(0,True))
        self.assertEqual(self.db.mailbox_baseline('box:1:',[b'1']),(0,False))
    def test_uidvalidity_change_sets_new_boundary(self):
        self.db.mailbox_baseline('box:1:',[b'7'])
        self.assertEqual(self.db.mailbox_baseline('box:2:',[b'20']),(20,True))
    def test_poll_initializes_without_reading_message_bodies(self):
        config=SimpleNamespace(app_mode='live',poll_batch_size=25,email_username='owner@example.invalid')
        with patch('app.poller.HostingerMail') as client:
            mail=client.return_value.__enter__.return_value
            mail.prefix='box:1:';mail.identifiers.return_value=[b'1',b'2']
            result=poll_once(self.db,config)
            mail.get_message.assert_not_called()
        self.assertTrue(result['initialized'])
        self.assertEqual(result['existing_skipped'],2)

if __name__=='__main__':unittest.main()
