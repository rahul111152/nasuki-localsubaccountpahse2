# NASUKI — "Your Local AI"

## Original Problem Statement
Build **Phase 1** of NASUKI, a local/on-device AI chatbot app, based on the user's Figma
("nasukiChatBot" / AI-BRAINBOX style). Phase 1 is **UI foundation only**: navigation, design
system, reusable components, and Figma-based screens with **mock data / mock services**.
No AI inference, RAG, backend, AdMob, billing, real Google auth, encryption, or cloud sync.

## Figma Source of Truth
- Public prototype captured via browser: **Splash → Login → Home** (with model download states:
  idle → rainbow progress → installed ✓).
- Light, monochrome (black/white/gray) aesthetic with a salmon/coral accent (GOOGLE button).
- Rounded white cards, dark rounded-pill bottom nav with a floating active tab, hexagon "network" logo.
- Screens not present in Figma were extended in the same design language (per brief §2).

## Architecture
- **Expo Router** (file-based), React Native, **strict TypeScript** (tsc: 0 errors).
- `src/theme` — colors (light + dark tokens), typography (Space Grotesk), spacing (8pt), radius,
  shadows, `ThemeProvider`/`useTheme` (default light; dark prepared + working toggle).
- `src/types` — Phase-2-ready entities (User, Conversation, Message, AIModel, InstalledModel,
  DocumentFile, DocumentChunk, CreditTransaction, CreditWallet, etc.).
- `src/constants` — centralized mock data + config (storage keys, credit rules).
- `src/services` — Auth, Chat, Model, Document, Credit, Feedback, BugReport, Onboarding (mock impls;
  UI talks only to these abstractions).
- `src/hooks` — `useAuth` (mock auth context + onboarding), `useToast`.
- `src/components/ui` — 20+ reusable components + Logo (SVG) + custom BottomNavigation.
- Fonts: Space Grotesk (bundled ttf) + icon-font prewarm preserved.
- Keyboard: `react-native-keyboard-controller` (KeyboardProvider; chat + forms).

## User Personas
- Privacy-conscious user who wants AI that runs on-device.
- Power user managing multiple local models + document (RAG) chat.

## Core Requirements (static)
Splash, Onboarding, Login (Google + Demo placeholders), Home, Chat + Chat History, Model Store +
Model Details, RAG Documents + Details, Credits, Profile, Settings, Privacy, Feedback, Bug Report.
Reusable design system; loading/empty/error/offline states; responsive; accessible; no secrets.

## Implemented (2026-06 / Phase 1) — DONE
- [x] Design tokens + ThemeProvider (light default, dark ready + toggle in Settings)
- [x] 20+ reusable components: Button, IconButton, Card, Input, SearchBar, Header, ChatBubble,
      ModelCard, CreditBadge, Avatar, Modal, BottomSheet, Toast, LoadingIndicator, EmptyState,
      ErrorState, Divider, Badge, ProgressBar (rainbow), DownloadProgress, Logo, SettingRow,
      SectionHeader, Touchable, ScreenContainer, ThemedStatusBar, BottomNavigation.
- [x] Navigation: `(auth)` vs `(tabs)` groups; stack for details/utility screens; auth gate + splash.
- [x] Splash (Figma-exact), Onboarding carousel (Next/Back/Skip/Get Started), Login (Figma-exact).
- [x] Home (Figma-exact): credit pill, watch-ads card, unlimited-chat card, AI Models w/ live
      download states (idle → rainbow progress → installed ✓).
- [x] Chat conversation: empty/typing/generating/completed/stopped states, stop, suggestions, keyboard.
- [x] Chat History: search, pin, rename (modal), delete (sheet), new-chat FAB.
- [x] Model Store: filter chips (single-line scroller), cards, download; Model Details w/ specs.
- [x] RAG Documents: empty/upload/processing/ready states; Document Details w/ chunk preview.
- [x] Credits: balance hero, watch-ad reward, buy packs, transaction history.
- [x] Profile, Settings (toggles + dark mode), Privacy, Feedback (success/error), Bug Report (success/error).
- [x] Mock services + mock data centralized; strict TS clean; app boots & verified via screenshots.

## Backlog (future phases — NOT in Phase 1)
- P0: Real on-device model inference (Gemma), SQLite persistence, real Google OAuth.
- P1: RAG (PDF parsing, embeddings, vector search), AdMob rewards, Play Billing / RevenueCat.
- P2: Cloud sync, E2E encryption, image/video generation, developer marketplace.

## Run
`cd /app/frontend` (Metro runs via supervisor on port 3000). Preview:
https://nasuki-auth-sqlite.preview.emergentagent.com — or scan the Expo Go QR from the preview panel.

## Notes / Limitations
- All data is mock/in-memory; nothing persists server-side. Onboarding/auth persist via local storage.
- Backend (FastAPI/Mongo) is untouched and unused in Phase 1.
