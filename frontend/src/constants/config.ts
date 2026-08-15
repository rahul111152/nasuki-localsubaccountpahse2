// App-wide constants (routes, storage keys, config).

export const APP = {
  name: "NASUKI",
  tagline: "YOUR LOCAL AI",
  version: "1.0",
} as const;

export const STORAGE_KEYS = {
  onboardingComplete: "nasuki.onboarding.complete",
  authUser: "nasuki.auth.user",
  themeMode: "nasuki.theme.mode",
} as const;

// 1 credit = 20 messages (from Figma Home card).
export const CREDITS = {
  messagesPerCredit: 20,
  rewardPerAd: 5,
  starting: 100,
} as const;
