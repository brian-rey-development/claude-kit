export type Run = { text: string; fg: string | null; bg: string | null }
export type Art = { width: number; rows: readonly (readonly Run[])[] }
export type Card = { tagline: string; caption: string; sizes: readonly Art[] }
