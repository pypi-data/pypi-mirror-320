from bloomerp.utils.router import route
from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, StreamingHttpResponse
from bloomerp.utils.llm import BloomerpOpenAI, BloomerpLangChain
from bloomerp.models import ApplicationField, DocumentTemplate, AIConversation
from django.contrib.auth.decorators import login_required
from django.conf import settings
import json
from django.core.cache import cache
from bloomerp.langchain_tools import BLOOMAI_TOOLS
import uuid
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST


@require_POST
@login_required
@route('llm_executor')
def llm_executor(request:HttpRequest) -> HttpResponse:
    '''
    Component to execute LLM queries.
    '''
    LLM_QUERY_TYPES = ['sql', 'document_template', 'tiny_mce_content', 'bloom_ai','code']
    

    # Get the json data from the request
    json_data : dict = json.loads(request.body)

    query_type = json_data.get('query_type', None)
    query = json_data.get('query', None)
    conversation_id = json_data.get('conversation_id', None)

    # Some preprocessing
    if not query_type:
        return HttpResponse('No llm query type provided')
    
    # Check if the query type is valid
    if query_type not in LLM_QUERY_TYPES:
        return HttpResponse('Invalid llm query type, must be one of: ' + ', '.join(LLM_QUERY_TYPES))
    
    # Check if the query is provided
    openai_key = settings.BLOOMERP_SETTINGS.get('OPENAI_API_KEY', None)
    if not openai_key:
        return HttpResponse('OpenAI key not found in settings')
    
    # Init the OpenAI class
    openai = BloomerpOpenAI(openai_key)

    # Check if the key is valid
    if not openai.is_valid_key():
        return HttpResponse('Invalid OpenAI key')
    
    # Parse uuid
    try:
        id = uuid.UUID(conversation_id)
    except:
        return HttpResponse('Invalid conversation id')

    # Get or create the AIConversation object
    ai_conversation_object, CREATED = AIConversation.objects.get_or_create(
            id=id,
            defaults={
                'conversation_type': query_type,
                'user' : request.user
            }            
        )

    # Get the conversation history
    if CREATED:
        conversation_history = []
    else:
        conversation_history = ai_conversation_object.conversation_history
    
    # Init the BloomerpLangChain executor
    executor = BloomerpLangChain(
        api_key=openai_key, 
        conversation_history=conversation_history
    )   

    return StreamingHttpResponse(
            stream_response(
                executor=executor,
                ai_conversation_object=ai_conversation_object,
                query=query,
                query_type=query_type,
                user=request.user,
                json_data=json_data
            ), 
            content_type='text/html')

def stream_response(
        executor:BloomerpLangChain,
        ai_conversation_object:AIConversation,
        query:str,
        user:User,
        query_type:str = 'bloom_ai',
        json_data:dict = None
    ):
    if query_type == 'bloom_ai':
        for item in executor.invoke_bloom_ai(
            query, 
            BLOOMAI_TOOLS, 
            user=user
            ):
            yield item

    elif query_type == 'sql':
        db_tables_and_columns = ApplicationField.get_db_tables_and_columns()
        for item in executor.invoke_sql_query(query, db_tables_and_columns):
            yield item

    elif query_type == 'document_template':
        # Get template id from args
        template_id = json_data['args'].get('template_id', None)

        if not template_id:
            return HttpResponse('Template id not provided')
        
        # Get the document template
        template = DocumentTemplate.objects.get(pk=template_id)
        variables = template.get_variables()

        for item in executor.invoke_document_template(
            query,
            variables
            ):
            yield item

    elif query_type == 'tiny_mce_content':
        for item in executor.invoke_tiny_mce_content(query):
            yield item

    elif query_type == 'code':
        for item in executor.invoke_code(query):
            yield item

    # Get the conversation history
    conversation_history = executor.serialize_conversation_history()

    # Save the conversation history to the object
    ai_conversation_object.conversation_history = conversation_history

    # Autoname the conversation object
    if not ai_conversation_object.auto_named and ai_conversation_object.number_of_messages > 5:
        ai_conversation_object.title = executor.auto_name()
        ai_conversation_object.auto_named = True

    ai_conversation_object.save()
        
    
    

