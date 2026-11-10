from app.models import Decision

def handle_message(db, engine, message, own_address=''):
    if not db.claim(message.key):return 'duplicate'
    ticket=None
    try:
        if message.automatic or message.sender.casefold()==own_address.casefold() or '@' not in message.sender:
            db.finish(message.key,'skipped',error='Automatisch bericht, eigen afzender of ongeldig adres');return 'skipped'
        ticket=db.ingest(message)
        current=db.ticket(ticket)
        if current['state'] in ('sending','delivery_unknown'):
            db.finish(message.key,'held',ticket,error='Lopende verzending moet eerst worden gecontroleerd');return 'held'
        if message.attachments or current['state']=='escalated':
            result=Decision(category=current['category'] or 'other',state='escalated',reason='Bijlage of gesprek dat al bij een medewerker ligt')
        elif not message.body.strip():
            result=Decision(category='other',state='escalated',reason='Geen leesbare berichttekst')
        else:
            history=[{'direction':m['direction'],'body':m['body'][:12000]} for m in db.messages(ticket)][-8:]
            result=engine.decide(message,history)
        db.decide(ticket,message.key,result);db.finish(message.key,'processed',ticket,result)
        db.audit(ticket,'decision',result.reason)
        return result.state
    except Exception as error:
        # Error types are useful for diagnosis without retaining credentials or raw provider responses.
        db.finish(message.key,'failed',ticket,error=type(error).__name__)
        if ticket:
            db.decide(ticket,message.key,Decision(category='other',state='escalated',reason='Verwerking mislukt; zie gebeurtenis'))
        return 'failed'
