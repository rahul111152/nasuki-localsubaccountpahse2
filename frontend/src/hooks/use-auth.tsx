// Mock auth context. Phase 2 swaps AuthService internals for real Google OAuth.

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import { AuthService, OnboardingService } from "@/src/services";
import { User } from "@/src/types";

type AuthContextValue = {
  user: User | null;
  initializing: boolean;
  onboardingComplete: boolean;
  signInWithGoogle: () => Promise<void>;
  signInWithDemo: () => Promise<void>;
  signOut: () => Promise<void>;
  completeOnboarding: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null);
  const [initializing, setInitializing] = useState(true);
  const [onboardingComplete, setOnboardingComplete] = useState(false);

  useEffect(() => {
    (async () => {
      const [current, ob] = await Promise.all([
        AuthService.getCurrentUser(),
        OnboardingService.isComplete(),
      ]);
      setUser(current);
      setOnboardingComplete(ob);
      setInitializing(false);
    })();
  }, []);

  const signInWithGoogle = useCallback(async () => {
    setUser(await AuthService.signInWithGoogle());
  }, []);

  const signInWithDemo = useCallback(async () => {
    setUser(await AuthService.signInWithDemo());
  }, []);

  const signOut = useCallback(async () => {
    await AuthService.signOut();
    setUser(null);
  }, []);

  const completeOnboarding = useCallback(async () => {
    await OnboardingService.complete();
    setOnboardingComplete(true);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      initializing,
      onboardingComplete,
      signInWithGoogle,
      signInWithDemo,
      signOut,
      completeOnboarding,
    }),
    [
      user,
      initializing,
      onboardingComplete,
      signInWithGoogle,
      signInWithDemo,
      signOut,
      completeOnboarding,
    ],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextValue => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
};
