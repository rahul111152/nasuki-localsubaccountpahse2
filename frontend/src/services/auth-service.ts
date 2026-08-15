// AuthService — mock authentication for Phase 1.
// Phase 2 will replace the bodies with real Google OAuth; signatures stay stable.

import { storage } from "@/src/utils/storage";
import { STORAGE_KEYS } from "@/src/constants/config";
import { mockUser } from "@/src/constants/mock-data";
import { AuthMethod, User } from "@/src/types";
import { delay, nowIso } from "@/src/utils/misc";

const makeUser = (method: AuthMethod): User => ({
  ...mockUser,
  method,
  name: method === "google" ? "Google User" : mockUser.name,
  email: method === "google" ? "you@gmail.com" : mockUser.email,
  createdAt: nowIso(),
});

export const AuthService = {
  async getCurrentUser(): Promise<User | null> {
    const raw = await storage.getItem<string>(STORAGE_KEYS.authUser, "");
    if (!raw) return null;
    try {
      return JSON.parse(raw) as User;
    } catch {
      return null;
    }
  },

  async signInWithGoogle(): Promise<User> {
    // Phase 1 placeholder — no real OAuth.
    await delay(900);
    const user = makeUser("google");
    await storage.setItem(STORAGE_KEYS.authUser, JSON.stringify(user));
    return user;
  },

  async signInWithDemo(): Promise<User> {
    await delay(500);
    const user = makeUser("demo");
    await storage.setItem(STORAGE_KEYS.authUser, JSON.stringify(user));
    return user;
  },

  async signOut(): Promise<void> {
    await delay(200);
    await storage.removeItem(STORAGE_KEYS.authUser);
  },
};
