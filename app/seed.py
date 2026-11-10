from pathlib import Path

def entries():
    rows=[]
    for file in sorted((Path(__file__).resolve().parents[1]/'knowledge_base').glob('*.md')):
        for index,chunk in enumerate(file.read_text().split('\n## ')[1:]):
            title,_,body=chunk.partition('\n')
            rows.append({'id':file.stem+'-'+str(index+1),'section':file.stem,'title':title.strip(),'content':body.strip()})
    return rows

if __name__=='__main__':
    from app.config import settings
    from app.db import Database
    db=Database(settings.db_url);db.init();db.seed(entries());print('Kennisbank geladen. Bestaande wijzigingen zijn behouden.')
