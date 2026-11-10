import logging
import time
from app.config import settings
from app.db import Database
from app.hostinger import HostingerMail
from app.ai.engine import AIEngine
from app.pipeline import handle_message

def poll_once(db=None, config=None):
    config=config or settings;db=db or Database(config.db_url)
    if config.app_mode!='live':return {'mode':'demo','processed':0}
    count=0;failures=0
    with HostingerMail(config) as mail:
        identifiers=mail.identifiers()
        boundary,initialized=db.mailbox_baseline(mail.prefix,identifiers)
        if initialized:
            db.audit(None,'mailbox_initialized','Bestaande berichten overgeslagen; vanaf nu nieuwe mail verwerken')
            return {'mode':'live','processed':0,'failed':0,'initialized':True,'existing_skipped':len(identifiers)}
        for uid in identifiers:
            if int(uid)<=boundary:continue
            key=mail.key(uid)
            if db.handled(key):continue
            if count>=config.poll_batch_size:break
            count+=1
            try:
                message=mail.get_message(uid)
                if handle_message(db,AIEngine(config,db),message,config.email_username)=='failed':failures+=1
            except Exception as error:
                failures+=1
                if db.claim(key):db.finish(key,'failed',error=type(error).__name__)
    return {'mode':'live','processed':count,'failed':failures}

def main():
    logging.basicConfig(level=logging.INFO)
    if settings.app_mode!='live':raise SystemExit('Poller start alleen met APP_MODE=live. Gebruik de demoknop voor offline testen.')
    db=Database(settings.db_url);db.init()
    while True:
        try:logging.info('poll %s',poll_once(db))
        except Exception as error:logging.error('poll failed: %s',type(error).__name__)
        time.sleep(settings.poll_interval_seconds)
if __name__=='__main__':main()
