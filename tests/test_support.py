import tempfile, unittest, json
from pathlib import Path
from dataclasses import replace
from unittest.mock import patch
from types import SimpleNamespace
from fastapi.testclient import TestClient
from app.db import Database
from app.models import Incoming, Decision, ProductIssue
from app.hostinger import parse_message, HostingerMail
from app.pipeline import handle_message
from app.demo import load_demo
from app.ai.engine import DemoEngine
from app.ai.rules import proposal
from app.config import Settings
from app.main import create_app
from app.seed import entries

class SupportTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.db=Database('sqlite:///'+self.tmp.name+'/test.sqlite');self.db.init();self.db.seed(entries());self.engine=DemoEngine(self.db)
        self.msg=Incoming('m1','customer@example.invalid','Paddle board','Welke maat board?','<m1@example.invalid>')
    def tearDown(self):self.tmp.cleanup()
    def test_demo_runs_and_is_idempotent(self):
        result=load_demo(self.db);self.assertEqual(result.count('review'),2);self.assertEqual(result.count('escalated'),4)
        self.assertEqual(load_demo(self.db),['duplicate']*6)
        self.assertEqual(len(self.db.all('SELECT * FROM tickets')),6)
    def test_auto_message_skipped(self):
        self.assertEqual(handle_message(self.db,self.engine,replace(self.msg,automatic=True)),'skipped');self.assertEqual(self.db.all('SELECT * FROM tickets'),[])
    def test_self_mail_skipped(self):self.assertEqual(handle_message(self.db,self.engine,self.msg,self.msg.sender),'skipped')
    def test_attachment_escalates_without_model(self):
        class Never:
            def decide(self,*a):raise AssertionError('Model must not run')
        self.assertEqual(handle_message(self.db,Never(),replace(self.msg,attachments=True)),'escalated')
    def test_empty_body_escalates(self):self.assertEqual(handle_message(self.db,self.engine,replace(self.msg,body='')),'escalated')
    def test_reference_links_same_sender(self):
        handle_message(self.db,self.engine,self.msg)
        handle_message(self.db,self.engine,replace(self.msg,key='m2',message_id='<m2@x>',references=[self.msg.message_id]))
        self.assertEqual(len(self.db.all('SELECT * FROM tickets')),1)
    def test_reference_cannot_join_other_customer(self):
        handle_message(self.db,self.engine,self.msg)
        handle_message(self.db,self.engine,replace(self.msg,key='m2',sender='other@example.invalid',references=[self.msg.message_id]))
        self.assertEqual(len(self.db.all('SELECT * FROM tickets')),2)
    def test_escalation_stays_with_human(self):
        handle_message(self.db,self.engine,replace(self.msg,attachments=True))
        result=handle_message(self.db,self.engine,replace(self.msg,key='m2',references=[self.msg.message_id]))
        self.assertEqual(result,'escalated')
    def test_stale_edit_and_send_blocked(self):
        handle_message(self.db,self.engine,self.msg);ticket=self.db.all('SELECT * FROM tickets')[0]
        self.assertIsNotNone(self.db.edit(ticket['id'],'changed',ticket['version']))
        self.assertIsNone(self.db.claim_send(ticket['id'],ticket['version']))
        t=self.db.ticket(ticket['id']);self.assertIsNotNone(self.db.claim_send(t['id'],t['version']));self.assertIsNone(self.db.claim_send(t['id'],t['version']))
    def test_delivery_unknown_not_retried(self):
        handle_message(self.db,self.engine,self.msg);t=self.db.all('SELECT * FROM tickets')[0];self.db.delivery_unknown(t['id']);self.assertIsNone(self.db.claim_send(t['id'],t['version']))
    def test_failure_logged_without_secret(self):
        class Broken:
            def decide(self,*a):raise ValueError('secret-placeholder')
        self.assertEqual(handle_message(self.db,Broken(),self.msg),'failed')
        self.assertNotIn('secret-placeholder',str(self.db.all('SELECT * FROM events')))
    def test_model_failure_can_recover_after_configuration_fix(self):
        class Broken:
            def decide(self,*a):raise RuntimeError('provider unavailable')
        self.assertEqual(handle_message(self.db,Broken(),self.msg),'failed')
        self.assertEqual(self.db.all('SELECT * FROM tickets')[0]['state'],'failed')
        self.assertEqual(handle_message(self.db,self.engine,self.msg),'review')
        self.assertEqual(len(self.db.all('SELECT * FROM messages')),1)
    def test_exhausted_retry_requires_current_version_and_failed_ticket(self):
        class Broken:
            def decide(self,*a):raise RuntimeError('provider unavailable')
        for _ in range(3):handle_message(self.db,Broken(),self.msg)
        self.assertEqual(handle_message(self.db,self.engine,self.msg),'duplicate')
        ticket=self.db.all('SELECT * FROM tickets')[0]
        self.assertIsNone(self.db.retry(ticket['id'],ticket['version']-1))
        self.assertIsNotNone(self.db.retry(ticket['id'],ticket['version']))
        self.assertEqual(handle_message(self.db,self.engine,self.msg),'review')
        current=self.db.ticket(ticket['id'])
        self.assertIsNone(self.db.retry(ticket['id'],current['version']))
    def test_parser_mime_html_and_headers(self):
        raw=b'From: Test <test@example.invalid>\r\nSubject: Hello\r\nMessage-ID: <a@x>\r\nReferences: <z@x>\r\nContent-Type: text/html; charset=utf-8\r\n\r\n<p>Hello</p><script>bad()</script>'
        m=parse_message(raw,'k');self.assertEqual(m.sender,'test@example.invalid');self.assertIn('Hello',m.body);self.assertNotIn('bad',m.body);self.assertEqual(m.references,['<z@x>'])
    def test_empty_search_is_safe(self):
        client=HostingerMail(None);client.mail=SimpleNamespace(uid=lambda *a:('OK',[None]));self.assertEqual(client.identifiers(),[])
    def test_search_failure_raises(self):
        client=HostingerMail(None);client.mail=SimpleNamespace(uid=lambda *a:('NO',[]))
        with self.assertRaises(RuntimeError):client.identifiers()
    def test_fetch_uses_peek(self):
        calls=[]
        def uid(*args):
            calls.append(args)
            if 'SIZE' in args[-1]:return 'OK',[b'1 (RFC822.SIZE 90)']
            return 'OK',[(b'1',b'From: a@example.invalid\r\n\r\nHello')]
        client=HostingerMail(SimpleNamespace(max_message_bytes=1000));client.mail=SimpleNamespace(uid=uid);client.prefix='account:INBOX:12:'
        m=client.get_message(b'1');self.assertEqual(calls[-1][-1],'(BODY.PEEK[])');self.assertEqual(m.key,'account:INBOX:12:1')
    def test_kb_edit_survives_seed(self):
        e=self.db.knowledge()[0];self.db.update_entry(e['id'],'New','New text',e['revision']);self.db.seed(entries());self.assertEqual(self.db.one('SELECT title FROM knowledge_base WHERE id=?',(e['id'],))['title'],'New')
    def test_rule_boundaries(self):
        for days,expected in [(30,'replace_board'),(31,'repair_kit')]:self.assertEqual(proposal(ProductIssue(product='board',problem='air_loss',order='x',valve_checked=True,delivery_days=days)),expected)
        self.assertEqual(proposal(ProductIssue(product='shelf',problem='panels',order='x',parts=['a','a','b'])),'replacement_panels')
        self.assertEqual(proposal(ProductIssue(product='board',problem='accessory')),'ask_details')
    def test_api_auth_csrf_demo_and_send_disabled(self):
        config=Settings(app_mode='demo',dashboard_password='test-only-password',demo_database_path=self.tmp.name+'/api.sqlite')
        with TestClient(create_app(config,self.db)) as c:
            self.assertEqual(c.get('/api/tickets').status_code,401)
            c.auth=('admin','test-only-password');self.assertEqual(c.post('/api/demo').status_code,403)
            c.headers['X-Support-Action']='dashboard';self.assertEqual(c.post('/api/demo').status_code,200)
            tickets=c.get('/api/tickets').json();self.assertEqual(len(tickets),6)
            self.assertEqual(c.post('/api/tickets/'+tickets[0]['id']+'/send',json={'version':tickets[0]['version']}).status_code,403)
    def test_live_requires_config(self):
        with self.assertRaises(ValueError):Settings(app_mode='live',database_url='',openai_api_key='',email_username='',email_password='',dashboard_password='')

if __name__=='__main__':unittest.main()
