# HalalFit Next.js frontend

## Development

```bash
cp .env.local.example .env.local
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_URL` to the FastAPI URL, including `/api`.

## Android / Google Play

The frontend uses static export and Capacitor.

```bash
npm run build
# Android project is already included
npm run android:sync
npm run android:open
```

In Android Studio, create a signed Android App Bundle (`.aab`) for Play Console. Add the production FastAPI URL to `.env.local` before building. Camera permission is required for barcode/QR scanning and label images.
