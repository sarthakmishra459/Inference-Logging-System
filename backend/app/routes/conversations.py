from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.repositories.conversations import ConversationRepository
from app.repositories.messages import MessageRepository
from app.routes.deps import get_conversation_repository, get_message_repository
from app.schemas.conversation import Conversation, Message

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=list[Conversation])
async def list_conversations(
    repository: Annotated[ConversationRepository, Depends(get_conversation_repository)],
) -> list[dict]:
    return await repository.list()


@router.get("/{conversation_id}", response_model=Conversation)
async def get_conversation(
    conversation_id: str,
    repository: Annotated[ConversationRepository, Depends(get_conversation_repository)],
) -> dict:
    conversation = await repository.get(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.get("/{conversation_id}/messages", response_model=list[Message])
async def list_messages(
    conversation_id: str,
    conversations: Annotated[ConversationRepository, Depends(get_conversation_repository)],
    messages: Annotated[MessageRepository, Depends(get_message_repository)],
) -> list[dict]:
    conversation = await conversations.get(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return await messages.list_for_conversation(conversation_id)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    repository: Annotated[ConversationRepository, Depends(get_conversation_repository)],
) -> None:
    deleted = await repository.delete(conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
