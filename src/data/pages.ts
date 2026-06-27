import slugs from './slugs.json';
import productImages from './product-images.json';
import { mainNavigation } from './navigation';
import { footerCategoryLinks } from './footer';
import { topTenCards, latestReviews } from './homepage';

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

export const allSiteSlugs: string[] = slugs;

const pages: Record<string, PageData> = {};

export function getPage(slug: string): PageData | undefined {
  return pages[slug];
}

const productImageMap: Record<string, string> = {};

for (const card of [...topTenCards, ...latestReviews]) {
  const slug = card.href.replace(/^\/|\/$/g, '');
  productImageMap[slug] = card.image;
}

for (const [slug, image] of Object.entries(productImages)) {
  if (typeof image === 'string' && image.startsWith('/images/')) {
    productImageMap[slug] = image;
  }
}

type FooterCategoryKey = keyof typeof footerCategoryLinks;

export function getCategoryItems(slug: string) {
  const navItem = mainNavigation.find((item) => item.href === `/${slug}/`);
  const footerLinks = footerCategoryLinks[slug as FooterCategoryKey];
  const links =
    navItem?.children ??
    footerLinks?.map((link) => ({ label: link.label, href: link.href })) ??
    [];

  return links.map((child) => {
    const productSlug = child.href.replace(/^\/|\/$/g, '');
    return {
      title: child.label,
      href: child.href,
      image: productImageMap[productSlug] ?? '/images/2023/06/digitale-wekker.jpeg',
      alt: child.label,
    };
  });
}
