# HalalFit frontend

Next.js TypeScript frontend exported for web and Capacitor Android.

## API configuration

```env
NEXT_PUBLIC_API_URL=https://backend.fastapicloud.dev/api
```

## Development

```powershell
pnpm install
pnpm dev
```

## Build and Android sync

```powershell
pnpm build
npx cap sync android
npx cap open android
```

The app includes mobile bottom navigation, a mobile menu, OTP registration/password reset/email change, profile editing, About and Contact pages.
