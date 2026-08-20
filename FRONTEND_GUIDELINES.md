# Frontend

Stack

- Next.js 16
- React 19
- TypeScript
- TailwindCSS
- shadcn/ui
- Framer Motion

---

Mobile First.

Todo componente precisa funcionar perfeitamente em:

320px

375px

430px

768px

1024px

1280px

1536px

---

Utilizar:

Server Components quando possível.

Client Components apenas quando necessário.

---

Toda imagem renderizada (fotos, thumbnails, ilustrações) usa `next/image`,
nunca `<img>` — otimização automática de tamanho/formato e lazy loading por
padrão. Hoje o produto não tem nenhuma imagem de conteúdo (só ícones SVG via
lucide-react e os ícones do manifest PWA), mas a regra vale a partir da
primeira imagem que entrar.

Componente pesado que não é necessário no primeiro paint (modal, drawer,
widget flutuante) usa `next/dynamic` com `ssr: false` — ver
`components/layout/authenticated-shell.tsx` (`AssistantWidget`,
`LevelUpCelebration`) para o padrão.

---

Nunca utilizar CSS puro.

Todo estilo deve ser feito utilizando Tailwind.

---

Sempre utilizar:

React Hook Form

Zod

TanStack Query

Zustand

Axios

---

Todos os componentes devem ser reutilizáveis.
