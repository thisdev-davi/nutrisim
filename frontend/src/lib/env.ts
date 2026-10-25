export const env = {
  api: {
    url: (process.env.NEXT_PUBLIC_BACK_END_API || "http://localhost:8000").replace(/\/$/, ""),
  },
} as const;
