// Domain + database entity types. These mirror the SQLite schema planned for
// Phase 2 so services/UI can be wired to a real DB without changing shapes.

// ---- Shared UI states -------------------------------------------------------
export type LoadState = "idle" | "loading" | "ready" | "empty" | "error";

export type ChatMessageState =
  | "sending"
  | "typing"
  | "generating"
  | "completed"
  | "error"
  | "stopped";

// ---- Auth / User ------------------------------------------------------------
export type AuthMethod = "google" | "demo";

export interface User {
  id: string;
  name: string;
  email: string;
  avatarUrl?: string;
  method: AuthMethod;
  createdAt: string; // ISO
}

// ---- Chat -------------------------------------------------------------------
export type MessageRole = "user" | "assistant" | "system";

export interface Message {
  id: string;
  conversationId: string;
  role: MessageRole;
  content: string;
  state: ChatMessageState;
  createdAt: string; // ISO
}

export interface Conversation {
  id: string;
  title: string;
  modelId: string;
  lastMessage: string;
  pinned: boolean;
  messageCount: number;
  updatedAt: string; // ISO
  createdAt: string; // ISO
}

// ---- Models -----------------------------------------------------------------
export type ModelDownloadStatus =
  | "not_installed"
  | "downloading"
  | "installed"
  | "error";

export interface AIModel {
  id: string;
  name: string;
  tagline: string;
  description: string;
  version: string;
  sizeMb: number;
  minRamGb: number;
  license: string;
  developer: string;
  price: number; // 0 = free
  capabilities: string[];
  featured: boolean;
}

export interface InstalledModel {
  modelId: string;
  status: ModelDownloadStatus;
  progress: number; // 0..1
  installedAt?: string; // ISO
}

// ---- RAG / Documents --------------------------------------------------------
export type DocumentStatus = "uploading" | "processing" | "ready" | "error";

export interface DocumentFile {
  id: string;
  name: string;
  type: "pdf" | "txt" | "md" | "docx";
  sizeKb: number;
  status: DocumentStatus;
  chunkCount: number;
  createdAt: string; // ISO
}

export interface DocumentChunk {
  id: string;
  documentId: string;
  index: number;
  content: string;
}

// ---- Credits ----------------------------------------------------------------
export type TransactionType = "purchase" | "reward_ad" | "usage" | "bonus";

export interface CreditTransaction {
  id: string;
  type: TransactionType;
  amount: number; // +earned / -spent
  label: string;
  createdAt: string; // ISO
}

export interface CreditWallet {
  balance: number;
  lifetimeEarned: number;
  lifetimeSpent: number;
}

// ---- Feedback / Bug report --------------------------------------------------
export type FeedbackType = "general" | "feature" | "praise" | "complaint";
export type BugCategory = "crash" | "ui" | "performance" | "data" | "other";

export interface FeedbackPayload {
  type: FeedbackType;
  message: string;
}

export interface BugReportPayload {
  category: BugCategory;
  description: string;
  screenshotUri?: string;
}

export interface SubmitResult {
  ok: boolean;
  reference: string;
}
