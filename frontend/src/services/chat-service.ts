// ChatService — mock chat. Phase 2 wires this to the local LLM (Gemma) + SQLite.

import { mockConversations, mockMessages } from "@/src/constants/mock-data";
import { Conversation, Message } from "@/src/types";
import { delay, nowIso, uid } from "@/src/utils/misc";

let conversations: Conversation[] = [...mockConversations];
const messages: Record<string, Message[]> = JSON.parse(
  JSON.stringify(mockMessages),
);

const CANNED = [
  "Great question! Here's a clear breakdown you can use right away.",
  "Sure — let me walk you through it step by step so it sticks.",
  "Here's a concise answer, plus a tip most people miss.",
  "Absolutely. I'd approach it like this, keeping things simple.",
];

export const ChatService = {
  async listConversations(): Promise<Conversation[]> {
    await delay(400);
    return [...conversations].sort(
      (a, b) =>
        Number(b.pinned) - Number(a.pinned) ||
        +new Date(b.updatedAt) - +new Date(a.updatedAt),
    );
  },

  async getMessages(conversationId: string): Promise<Message[]> {
    await delay(300);
    return messages[conversationId] ?? [];
  },

  async createConversation(modelId: string): Promise<Conversation> {
    await delay(200);
    const convo: Conversation = {
      id: uid("cnv"),
      title: "New chat",
      modelId,
      lastMessage: "",
      pinned: false,
      messageCount: 0,
      updatedAt: nowIso(),
      createdAt: nowIso(),
    };
    conversations = [convo, ...conversations];
    messages[convo.id] = [];
    return convo;
  },

  // Mock streaming: returns the user + assistant messages the UI should render.
  async sendMessage(
    conversationId: string,
    content: string,
  ): Promise<{ user: Message; assistant: Message }> {
    const user: Message = {
      id: uid("m"),
      conversationId,
      role: "user",
      content,
      state: "completed",
      createdAt: nowIso(),
    };
    const reply = CANNED[Math.floor(Math.random() * CANNED.length)];
    const assistant: Message = {
      id: uid("m"),
      conversationId,
      role: "assistant",
      content: `${reply}\n\nYou asked: "${content.slice(0, 80)}"`,
      state: "generating",
      createdAt: nowIso(),
    };
    const list = messages[conversationId] ?? [];
    messages[conversationId] = [...list, user, assistant];
    return { user, assistant };
  },

  async stopGeneration(_conversationId: string): Promise<void> {
    await delay(100);
  },

  async regenerateMessage(
    conversationId: string,
  ): Promise<Message> {
    await delay(400);
    const reply = CANNED[Math.floor(Math.random() * CANNED.length)];
    return {
      id: uid("m"),
      conversationId,
      role: "assistant",
      content: reply,
      state: "generating",
      createdAt: nowIso(),
    };
  },

  async renameConversation(id: string, title: string): Promise<void> {
    await delay(150);
    conversations = conversations.map((c) =>
      c.id === id ? { ...c, title } : c,
    );
  },

  async togglePin(id: string): Promise<void> {
    await delay(120);
    conversations = conversations.map((c) =>
      c.id === id ? { ...c, pinned: !c.pinned } : c,
    );
  },

  async deleteConversation(id: string): Promise<void> {
    await delay(150);
    conversations = conversations.filter((c) => c.id !== id);
    delete messages[id];
  },
};
