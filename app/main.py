from contextlib import asynccontextmanager
import secrets
from pathlib import Path
from email.utils import make_msgid
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
from app.config import settings
from app.db import Database
from app.seed import entries
from app.demo import load_demo
from app.poller import poll_once
from app.hostinger import HostingerMail

class Edit(BaseModel):
    text: str=Field(min_length=1,max_length=12000)
    version: int
class Approval(BaseModel):
    version: int
class EntryUpdate(BaseModel):
    title: str=Field(min_length=1,max_length=200)
    content: str=Field(min_length=1,max_length=20000)
    revision: int

def create_app(config=settings, database=None):
    db=database or Database(config.db_url)
    @asynccontextmanager
    async def lifespan(app):
        db.init();db.seed(entries());yield
    app=FastAPI(title='Oumar Customer Support',lifespan=lifespan)
    auth=HTTPBasic(auto_error=False)
    def require(request:Request,credentials:HTTPBasicCredentials|None=Depends(auth)):
        valid=credentials is not None and secrets.compare_digest(credentials.username.encode(),config.dashboard_username.encode()) and secrets.compare_digest(credentials.password.encode(),config.effective_password.encode())
        if not valid:raise HTTPException(401,'Inloggen vereist',headers={'WWW-Authenticate':'Basic'})
        if request.method not in ('GET','HEAD','OPTIONS') and request.headers.get('X-Support-Action')!='dashboard':raise HTTPException(403,'Actieheader ontbreekt')
    @app.middleware('http')
    async def headers(request,call_next):
        response=await call_next(request)
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Referrer-Policy']='no-referrer'
        response.headers['Cache-Control']='no-store'
        response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'"
        return response
    @app.get('/health')
    def health():return {'status':'ok'}
    @app.get('/api/status',dependencies=[Depends(require)])
    def status():
        return {'mode':config.app_mode,'sending':config.enable_sending and config.app_mode=='live','counts':db.all('SELECT state,COUNT(*) AS count FROM tickets GROUP BY state'),'usage':db.one('SELECT COALESCE(SUM(input_tokens),0) AS input_tokens,COALESCE(SUM(output_tokens),0) AS output_tokens FROM events')}
    @app.get('/api/tickets',dependencies=[Depends(require)])
    def tickets():return db.all('SELECT * FROM tickets ORDER BY updated_at DESC LIMIT 200')
    @app.get('/api/tickets/{id}',dependencies=[Depends(require)])
    def ticket(id:str):
        row=db.ticket(id)
        if not row:raise HTTPException(404,'Ticket niet gevonden')
        return {'ticket':row,'messages':db.messages(id),'audit':db.all('SELECT * FROM audit WHERE ticket_id=? ORDER BY created_at',(id,))}
    @app.get('/api/events',dependencies=[Depends(require)])
    def events():return db.all('SELECT * FROM events ORDER BY updated_at DESC LIMIT 200')
    @app.get('/api/knowledge',dependencies=[Depends(require)])
    def knowledge():return db.knowledge()
    @app.put('/api/knowledge/{id}',dependencies=[Depends(require)])
    def update_knowledge(id:str,data:EntryUpdate):
        row=db.update_entry(id,data.title,data.content,data.revision)
        if not row:raise HTTPException(409,'Kennisbank gewijzigd; vernieuw eerst')
        db.audit(None,'knowledge_update',id+' revision '+str(row['revision']));return row
    @app.put('/api/tickets/{id}/draft',dependencies=[Depends(require)])
    def edit(id:str,data:Edit):
        row=db.edit(id,data.text,data.version)
        if not row:raise HTTPException(409,'Ticket gewijzigd of niet bewerkbaar; vernieuw eerst')
        db.audit(id,'draft_edited','Door ingelogde medewerker');return row
    @app.post('/api/tickets/{id}/send',dependencies=[Depends(require)])
    def send(id:str,data:Approval):
        if config.app_mode!='live' or not config.enable_sending:raise HTTPException(403,'Verzenden staat uit')
        ticket=db.claim_send(id,data.version)
        if not ticket:raise HTTPException(409,'Concept gewijzigd, leeg of al verstuurd')
        outid=make_msgid(domain=config.email_username.split('@')[-1])
        db.audit(id,'send_started',outid)
        try:
            warning=HostingerMail(config).send_reply(db.latest(ticket),ticket['draft'],outid)
            db.sent(ticket,outid,warning,config.email_username)
        except Exception:
            db.delivery_unknown(id);db.audit(id,'delivery_unknown',outid)
            raise HTTPException(502,'Verzendresultaat onzeker. Controleer je mailbox; niet automatisch opnieuw proberen.')
        db.audit(id,'sent',outid);return {'status':'sent','warning':warning}
    @app.post('/api/demo',dependencies=[Depends(require)])
    def demo():
        if config.app_mode!='demo':raise HTTPException(403,'Demo alleen in demomodus')
        return {'results':load_demo(db)}
    @app.post('/api/poll',dependencies=[Depends(require)])
    def poll():
        try:return poll_once(db,config)
        except Exception as error:raise HTTPException(502,'Mailboxcontrole mislukt: '+type(error).__name__)
    frontend=Path(__file__).resolve().parents[1]/'dashboard'/'dist'
    if (frontend/'assets').exists():app.mount('/assets',StaticFiles(directory=frontend/'assets'),name='assets')
    @app.get('/')
    def home():
        if not (frontend/'index.html').exists():raise HTTPException(503,'Bouw eerst het dashboard')
        return FileResponse(frontend/'index.html')
    return app
app=create_app()
