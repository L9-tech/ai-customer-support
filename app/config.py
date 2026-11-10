from pathlib import Path
from typing import Literal
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env', override=False)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra='ignore')
    app_mode: Literal['demo', 'live'] = 'demo'
    database_url: str = ''
    demo_database_path: str = str(ROOT / 'data' / 'demo.sqlite3')
    openai_api_key: str = ''
    classifier_model: str = 'openai:gpt-6-luna'
    agent_model: str = 'openai:gpt-6.1-sol'
    imap_host: str = 'imap.hostinger.com'
    imap_port: int = 993
    imap_folder: str = 'INBOX'
    imap_sent_folder: str = 'Sent'
    smtp_host: str = 'smtp.hostinger.com'
    smtp_port: int = 465
    email_username: str = ''
    email_password: str = ''
    poll_interval_seconds: int = Field(default=60, ge=10)
    poll_batch_size: int = Field(default=25, ge=1, le=100)
    dashboard_username: str = 'admin'
    dashboard_password: str = ''
    enable_sending: bool = False
    max_message_bytes: int = 1_000_000

    @model_validator(mode='after')
    def validate_live(self):
        if self.app_mode == 'live':
            required = ['database_url', 'openai_api_key', 'email_username', 'email_password', 'dashboard_password']
            missing = [name for name in required if not getattr(self, name).strip()]
            if missing:
                raise ValueError('Ontbrekende live instellingen: ' + ', '.join(missing))
            if not self.database_url.startswith(('postgresql://', 'postgres://')):
                raise ValueError('Live modus vereist PostgreSQL DATABASE_URL')
            if len(self.dashboard_password) < 16:
                raise ValueError('Gebruik voor live een dashboardwachtwoord van minstens 16 tekens')
        return self

    @property
    def effective_password(self):
        return self.dashboard_password or 'demo-local'

    @property
    def db_url(self):
        return self.database_url if self.app_mode == 'live' else 'sqlite:///' + self.demo_database_path

settings = Settings()
