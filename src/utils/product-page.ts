import { mainNavigation } from '../data/navigation';
import { footerCategoryLinks, footerColumnHeadings } from '../data/footer';

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

const footerCategoryMeta: Record<
  keyof typeof footerCategoryLinks,
  { label: string; href: string }
> = {
  melders: footerColumnHeadings.melders,
  slaapkamer: footerColumnHeadings.slaapkamer,
  keuken: footerColumnHeadings.keuken,
  terras: footerColumnHeadings.terras,
  veiligheid: footerColumnHeadings.veiligheid,
};

export function getProductBreadcrumbTrail(slug: string): BreadcrumbItem[] | null {
  for (const navItem of mainNavigation) {
    if (!navItem.children) continue;
    for (const child of navItem.children) {
      const childSlug = child.href.replace(/^\/|\/$/g, '');
      if (childSlug === slug) {
        return [
          { label: 'Home', href: '/' },
          { label: navItem.label.toLowerCase(), href: navItem.href },
          { label: child.label.toLowerCase() },
        ];
      }
    }
  }

  for (const [key, links] of Object.entries(footerCategoryLinks) as [
    keyof typeof footerCategoryLinks,
    { label: string; href: string }[],
  ][]) {
    const meta = footerCategoryMeta[key];
    for (const link of links) {
      const linkSlug = link.href.replace(/^\/|\/$/g, '');
      if (linkSlug === slug) {
        return [
          { label: 'Home', href: '/' },
          { label: meta.label.toLowerCase(), href: meta.href },
          { label: link.label.toLowerCase() },
        ];
      }
    }
  }

  return null;
}

export function buildBreadcrumbHtml(trail: BreadcrumbItem[]): string {
  const items = trail
    .map((item, index) => {
      const position = index + 1;
      if (item.href) {
        const homeClass = index === 0 ? ' breadcrumb-home' : '';
        const name = index === 0 ? 'Home' : item.label;
        return `<li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
    <a class="${homeClass.trim()}" itemprop="item" href="${item.href}"><span itemprop="name">${name}</span></a>
    <meta itemprop="position" content="${position}"/>
  </li>`;
      }
      return `<li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
    <span itemprop="name">${item.label}</span>
    <meta itemprop="position" content="${position}"/>
  </li>`;
    })
    .join('\n  ');

  return `<div class="elementor-element elementor-element-14f208b7 elementor-align-left elementor-widget elementor-widget-breadcrumbs">
<div class="elementor-widget-container">
<ol class="zbmp-breadcrumb" itemscope itemtype="https://schema.org/BreadcrumbList">
  ${items}
</ol>
</div>
</div>`;
}

const HERO_COLUMN_MARKER =
  'elementor-element-2368d765" data-e-type="column" data-element_type="column" data-id="2368d765">\n<div class="elementor-widget-wrap elementor-element-populated">';

export function prepareProductHtml(html: string, slug: string): string {
  let content = html.trim();

  if (!content.includes('class="elementor elementor-56"')) {
    content = `<div class="elementor elementor-56">${content}</div>`;
  }

  const trail = getProductBreadcrumbTrail(slug);
  if (trail && !content.includes('zbmp-breadcrumb')) {
    const breadcrumbHtml = buildBreadcrumbHtml(trail);
    if (content.includes(HERO_COLUMN_MARKER)) {
      content = content.replace(
        HERO_COLUMN_MARKER,
        `${HERO_COLUMN_MARKER}\n\n${breadcrumbHtml}\n`
      );
    }
  }

  content = content.replace(
    /href="#top%2010" target="_blank"/g,
    'href="#top%2010"'
  );

  return content;
}
