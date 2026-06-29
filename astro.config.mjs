// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);

export default defineConfig({
  site: 'https://interiorchick.nl',
  trailingSlash: 'always',
  compressHTML: true,
  integrations: [mdx()],
});
