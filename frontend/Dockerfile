# syntax=docker/dockerfile:1

# =============================================================================
# Stage 1 — deps: instala as dependências a partir do lockfile, isolado do
# código-fonte para maximizar o reaproveitamento de cache do Docker.
# =============================================================================
FROM node:24-alpine AS deps

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci


# =============================================================================
# Stage 2 — builder: compila o build de produção do Next.js (output
# "standalone", configurado em next.config.ts).
# =============================================================================
FROM node:24-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Variáveis NEXT_PUBLIC_* são inlinadas no bundle do cliente em build-time —
# por isso precisam existir como build arg, e não apenas como env var de
# runtime do container final.
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ENV NEXT_TELEMETRY_DISABLED=1

RUN npm run build


# =============================================================================
# Stage 3 — runner: imagem final enxuta, apenas com o output "standalone"
# (server.js autocontido + node_modules mínimo), rodando como usuário
# não-root.
# =============================================================================
FROM node:24-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0

RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

CMD ["node", "server.js"]
