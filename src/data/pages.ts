export interface PageData {
  slug: string;
  title: string;
  description: string;
  featuredImage: string;
  content: string;
  type: 'article' | 'product' | 'category' | 'page' | 'blog';
  url: string;
  items?: { label: string; href: string }[];
}

import slugs from './slugs.json';
import { mainNavigation } from './navigation';

export const allSiteSlugs: string[] = slugs;

const pages: Record<string, PageData> = {};

export function getPage(slug: string): PageData | undefined {
  return pages[slug];
}

export function getCategoryItems(slug: string) {
  const navItem = mainNavigation.find((item) => item.href === `/${slug}/`);
  if (!navItem?.children) return [];
  return navItem.children.map((child) => ({
    title: child.label,
    href: child.href,
    image: '/images/2023/06/digitale-wekker.jpeg',
    alt: child.label,
  }));
}
