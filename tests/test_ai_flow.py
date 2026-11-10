import unittest,tempfile
from unittest.mock import patch
from types import SimpleNamespace
from pydantic_ai.models.function import FunctionModel
from pydantic_ai.messages import ModelResponse, ToolCallPart, ToolReturnPart
from pydantic_ai.usage import RequestUsage
from app.db import Database
from app.seed import entries
from app.ai.engine import AIEngine, AIProcessingPaused
from app.models import Incoming

class AIFlow(unittest.TestCase):
    def test_paused_ai_never_calls_provider(self):
        with patch('pydantic_ai.providers.openai.OpenAIProvider') as provider:
            with self.assertRaises(AIProcessingPaused):
                AIEngine(SimpleNamespace(ai_enabled=False),None).decide(Incoming('p','x@example.invalid','Test','Test','<p>'),[])
            provider.assert_not_called()
    def test_real_agent_orchestration_with_fake_model(self):
        def classify(messages, info):
            return ModelResponse([ToolCallPart(info.output_tools[0].name,{'section':'paddle-boards','needs_human':False,'reason':'Maatvraag'})],usage=RequestUsage(input_tokens=10,output_tokens=4))
        def draft(messages, info):
            read=any(isinstance(part,ToolReturnPart) and part.tool_name=='get_section' for message in messages for part in message.parts)
            if not read:return ModelResponse([ToolCallPart('get_section',{'section':'paddle-boards'})],usage=RequestUsage(input_tokens=10,output_tokens=4))
            return ModelResponse([ToolCallPart(info.output_tools[0].name,{'text':'Voor dit gewicht past de 11 voet maat.','sufficient':True,'needs_human':False,'reason':'Gewicht past bij de kennisbank','sources':['paddle-boards-1'],'proposed_action':'','issue':None})],usage=RequestUsage(input_tokens=10,output_tokens=4))
        with tempfile.TemporaryDirectory() as tmp:
            db=Database('sqlite:///'+tmp+'/a.sqlite');db.init();db.seed(entries())
            config=SimpleNamespace(openai_api_key='not-a-real-key',classifier_model='openai:small',agent_model='openai:large')
            def model(name,**kw):return FunctionModel(classify if name=='small' else draft)
            with patch('pydantic_ai.models.openai.OpenAIResponsesModel',model):
                result=AIEngine(config,db).decide(Incoming('x','a@example.invalid','Board','90 kg','<x>'),[])
            self.assertEqual(result.state,'review');self.assertEqual(result.sources,['paddle-boards-1@1'])
            self.assertEqual(result.input_tokens,30);self.assertEqual(result.output_tokens,12)
if __name__=='__main__':unittest.main()
