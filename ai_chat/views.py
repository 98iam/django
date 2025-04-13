import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import ChatSession, ChatMessage
from .services import GeminiService

@login_required
def chat_sidebar(request, session_id=None):
    """
    Render the chat sidebar partial template.
    This is used for AJAX loading of the sidebar.
    If session_id is provided, render the chat interface for that session.
    Otherwise, get the most recent session or create a new one.
    """
    if session_id:
        # Render chat interface for specific session
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    else:
        # Get the most recent session or create a new one
        sessions = ChatSession.objects.filter(user=request.user).order_by('-updated_at')
        if sessions.exists():
            session = sessions.first()
        else:
            # Create a new session
            session = ChatSession.objects.create(user=request.user)

    # Get messages for the session
    messages = ChatMessage.objects.filter(session=session)

    # Render chat interface
    return render(request, 'ai_chat/sidebar_chat.html', {
        'session': session,
        'messages': messages
    })

@login_required
def chat_session(request, session_id=None):
    """
    Get or create a chat session and return its messages.
    """
    if session_id:
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    else:
        # Create a new session
        session = ChatSession.objects.create(user=request.user)

    messages = ChatMessage.objects.filter(session=session)
    sessions = ChatSession.objects.filter(user=request.user)

    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'session_id': session.id
        })

    # Regular request - render the full page
    return render(request, 'ai_chat/chat.html', {
        'session': session,
        'messages': messages,
        'sessions': sessions
    })

@login_required
@require_POST
@csrf_exempt
def send_message(request):
    """
    Process a new message from the user and get a response from the AI.
    """
    try:
        data = json.loads(request.body)
        message_text = data.get('message')
        session_id = data.get('session_id')

        if not message_text or not session_id:
            return JsonResponse({'error': 'Message and session ID are required'}, status=400)

        # Get the session
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)

        # Save the user message
        user_message = ChatMessage.objects.create(
            session=session,
            role='user',
            content=message_text
        )

        # Get all messages in this session to maintain context
        messages = ChatMessage.objects.filter(session=session)
        message_list = [{'role': msg.role, 'content': msg.content} for msg in messages]

        # Get response from Gemini
        try:
            gemini_service = GeminiService()
            # Pass the user to filter products by this user's account
            ai_response = gemini_service.generate_response(message_list, user=request.user)

            # Save the AI response
            assistant_message = ChatMessage.objects.create(
                session=session,
                role='assistant',
                content=ai_response
            )

            # Update session timestamp
            session.save()

            return JsonResponse({
                'success': True,
                'user_message': {
                    'id': user_message.id,
                    'content': user_message.content,
                    'timestamp': user_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                },
                'ai_message': {
                    'id': assistant_message.id,
                    'content': assistant_message.content,
                    'timestamp': assistant_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_POST
@csrf_exempt
def delete_session(request, session_id):
    """
    Delete a chat session.
    """
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    session.delete()

    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    # Regular form submission
    return redirect('chat_session')

@login_required
@require_POST
@csrf_exempt
def update_title(request, session_id):
    """
    Update the title of a chat session.
    """
    try:
        data = json.loads(request.body)
        new_title = data.get('title')

        if not new_title:
            return JsonResponse({'error': 'Title is required'}, status=400)

        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        session.title = new_title
        session.save()

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
